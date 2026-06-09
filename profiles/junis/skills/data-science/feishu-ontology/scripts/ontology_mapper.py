#!/usr/bin/env python3
"""
燕青本体巡检脚本 — 异虎飞书三表 Ontology Mapper
============================================
功能：
  1. 连接飞书Bitable，获取三表最新数据
  2. 检查本体映射一致性（字段名、选项值、类型匹配）
  3. 输出变更日志 + 关系异常检测
  4. 生成当日本体快照 JSON

使用方式：
  export FEISHU_APP_ID=cli_aa869b8d6b3c5cc3
  export FEISHU_APP_SECRET=your_secret
  python3 ontology_mapper.py [--report-only]

依赖：
  curl, python3 (stdlib only — requests not required)
"""

import json
import os
import time
import subprocess
from datetime import datetime, timezone

# ===== 配置 =====
APP_TOKEN = "NzuPbMtMFa0wUusVQKwc69lenib"
TABLES = {
    "operation_log": {"id": "tbllV9WgN64Zwput", "label": "搭建日志"},
    "daily_record": {"id": "tblTLllADiUdhL6e", "label": "每日记录"},
    "favorite_item": {"id": "tblydJHMALlK3stv", "label": "收藏随想录"},
}
OUTPUT_DIR = os.path.expanduser("~/hermes-vault/ontology")

META_FIELDS = {
    "operation_log": {"对象键": "时间", "关系字段": [], "动作字段": ["操作内容"], "状态字段": ["状态"], "分类字段": ["领域"]},
    "daily_record": {"对象键": "公历时间", "关系字段": [], "动作字段": ["记录内容"], "状态字段": [], "分类字段": ["类型"]},
    "favorite_item": {"对象键": "标题", "关系字段": ["来源链接"], "动作字段": ["我的感悟"], "状态字段": ["状态"], "分类字段": ["分类", "来源类型"]},
}

CROSS_RELATIONS = [
    {"name": "daily_vs_operation", "from": "daily_record", "from_field": "公历时间",
     "to": "operation_log", "to_field": "时间", "match_type": "date"},
    {"name": "daily_vs_favorite", "from": "daily_record", "from_field": "公历时间",
     "to": "favorite_item", "to_field": "收藏日期", "match_type": "date"},
]


class FeishuBitable:
    def __init__(self):
        self.app_id = os.environ.get("FEISHU_APP_ID", "cli_aa869b8d6b3c5cc3")
        self.app_secret = os.environ.get("FEISHU_APP_SECRET", "")
        self.token = None
        self.token_expire = 0

    def _get_token(self):
        if self.token and time.time() < self.token_expire - 60:
            return self.token
        cmd = f'''curl -s -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d '{{"app_id":"{self.app_id}","app_secret":"{self.app_secret}"}}' '''
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        data = json.loads(result.stdout)
        assert data.get("code") == 0, f"Token failed: {data}"
        self.token = data["tenant_access_token"]
        self.token_expire = time.time() + data["expire"]
        return self.token

    def _request(self, path):
        token = self._get_token()
        url = f"https://open.feishu.cn/open-apis{path}"
        cmd = f'curl -s "{url}" -H "Authorization: Bearer {token}"'
        return json.loads(subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout)

    def get_table_meta(self, table_id):
        return self._request(f"/bitable/v1/apps/{APP_TOKEN}/tables/{table_id}/fields")

    def get_records(self, table_id, page_size=100):
        return self._request(f"/bitable/v1/apps/{APP_TOKEN}/tables/{table_id}/records?page_size={page_size}")


class OntologyMapper:
    def __init__(self, client):
        self.client = client
        self.meta_cache = {}
        self.record_cache = {}

    def fetch_all(self):
        for key, table in TABLES.items():
            self.meta_cache[key] = self.client.get_table_meta(table["id"])
            self.record_cache[key] = self.client.get_records(table["id"]).get("data", {}).get("items", [])
        return self

    def check_field_consistency(self):
        issues = []
        field_names = {k: [f.get("field_name", "") for f in self.meta_cache[k].get("data", {}).get("items", [])] for k in TABLES}
        for key, meta in META_FIELDS.items():
            obj_key = meta["对象键"]
            if obj_key not in field_names.get(key, []):
                issues.append({"severity": "critical", "table": key, "field": obj_key, "msg": f"对象键「{obj_key}」不存在或被重命名"})
        return issues

    def check_option_consistency(self):
        issues = []
        for key in TABLES:
            items = self.meta_cache[key].get("data", {}).get("items", [])
            for field in items:
                props = field.get("property") or {}
                options = props.get("options", [])
                if not options:
                    continue
                names = [o.get("name", "") for o in options]
                seen = {}
                for n in names:
                    norm = n.replace(" ", "")
                    if norm in seen:
                        issues.append({"severity": "medium", "table": key, "field": field.get("field_name",""),
                                       "msg": f"选项「{n}」与「{seen[norm]}」可能重复（空格差异）"})
                    seen[norm] = n
                no_icon = [n for n in names if n and not any(n.startswith(p) for p in ("✅","📋","⏳","📚","💼","🤝","💡","🏠","🌐","💻","📱","🎧","🎬","📰","🎵","📨","💬","📄","🏢","🧘","🎯","📖","🔮","🎨","⭐","🔖","🔄","🧠"))]
                if no_icon:
                    issues.append({"severity": "info", "table": key, "field": field.get("field_name",""),
                                   "msg": f"无图标的纯文本选项: {no_icon}"})
        return issues

    def detect_cross_relations(self):
        relations = {}
        for rel in CROSS_RELATIONS:
            from_records = self.record_cache.get(rel["from"], [])
            to_records = self.record_cache.get(rel["to"], [])
            matches = []
            for fr in from_records[:15]:
                f_val = fr.get("fields", {}).get(rel["from_field"])
                if not f_val:
                    continue
                f_day = int(f_val) // 86400000 if rel["match_type"] == "date" else str(f_val)[:10]
                for tr in to_records:
                    t_val = tr.get("fields", {}).get(rel["to_field"])
                    if not t_val:
                        continue
                    t_day = int(t_val) // 86400000 if rel["match_type"] == "date" else str(t_val)[:10]
                    if f_day == t_day:
                        matches.append({
                            "from": (fr.get("fields", {}).get("记录内容", str(f_val)))[:40],
                            "to": (tr.get("fields", {}).get("操作内容" if rel["to"] == "operation_log" else "标题", str(t_val)))[:40]
                        })
            relations[rel["name"]] = {"total_matches": len(matches), "sample": matches[:5]}
        return relations

    def generate_report(self):
        issues1 = self.check_field_consistency()
        issues2 = self.check_option_consistency()
        relations = self.detect_cross_relations()
        score = 100 - sum(20 for i in issues1 if i["severity"] == "critical") - sum(5 for i in issues2 if i["severity"] == "medium") - sum(2 for i in issues2 if i["severity"] == "info")
        return {
            "timestamp": datetime.now(timezone.utc).astimezone().isoformat(),
            "summary": {
                "total_tables": len(TABLES),
                "total_records": {k: len(v) for k, v in self.record_cache.items()},
                "critical_issues": len([i for i in issues1 if i["severity"] == "critical"]),
                "medium_issues": len([i for i in issues2 if i["severity"] == "medium"]),
                "info_issues": len([i for i in issues2 if i["severity"] == "info"]),
                "cross_relations_detected": {k: v["total_matches"] for k, v in relations.items()},
            },
            "field_consistency": issues1,
            "option_issues": issues2,
            "cross_relations": relations,
            "health_score": max(0, score),
        }


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    client = FeishuBitable()
    mapper = OntologyMapper(client)

    mapper.fetch_all()
    report = mapper.generate_report()

    fp = os.path.join(OUTPUT_DIR, f"ontology_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    s = report["summary"]
    print(f"✅ 本体健康度: {report['health_score']}/100")
    print(f"📦 {s['total_tables']} 张表, 共 {sum(s['total_records'].values())} 条")
    print(f"⚠️  中等问题: {s['medium_issues']} | 提示: {s['info_issues']} | 严重: {s['critical_issues']}")
    print(f"🔗 跨表关系: {s['cross_relations_detected']}")
    print(f"📁 快照: {fp}")

    for i in report.get("option_issues", []):
        print(f"  [{i['severity'][0].upper()}] {TABLES[i['table']]['label']}.{i['field']}: {i['msg']}")


if __name__ == "__main__":
    main()
