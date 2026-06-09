#!/usr/bin/env python3
"""扫描搭建日志，把历史所有喂料（入库/收录原文）同步到收藏随想录"""
import requests, json, re, os, sys
from datetime import datetime, timezone, timedelta

APP_ID = "cli_aa869b8d6b3c5cc3"
APP_SECRET = "qSk4tz1A15aWo5K4eFw2lbhibgMAVaHN"
BASE_TOKEN = "NzuPbMtMFa0wUusVQKwc69lenib"
COLLECT_TABLE = "tblydJHMALlK3stv"
LOG_PATH = "/mnt/c/Users/18502/Documents/Obsidian Vault/MOC地图/第二大脑搭建日志.md"
TZ = timezone(timedelta(hours=8))

SOURCE_MAP = [
    (["开源", "GitHub", "TencentDB"], "🌐 网页"),
    (["微信", "公众号"], "📱 微信文章"),
    (["播客", "Lightcone", "访谈"], "🎧 播客"),
    (["书籍", "书", "精读", "PDF", "全文"], "📚 书籍"),
    (["文章", "新闻", "发布"], "📰 新闻"),
    (["PDF", "文档", "文件"], "📄 PDF/文档"),
    (["报告", "调研", "论文", "研究"], "📰 新闻"),
]
CATEGORY_MAP = [
    (["AI", "Agent", "记忆", "开源", "模型", "技术", "工具", "FDE", "Harness", "OCR", "Python"], "💻 技术/AI"),
    (["商业", "企业", "战略", "管理", "组织", "营销", "定位", "格局"], "🏢 商业/管理"),
    (["个人成长", "纳瓦尔", "判断力", "认知", "思维"], "🎯 认知/思维"),
    (["毛", "马哲", "党史", "历史", "哲学", "人文", "社科", "文明"], "📖 人文/社科"),
    (["易", "命理", "八字", "三命", "千里", "周易", "道家", "儒"], "🔮 传统文化"),
    (["毛选", "毛泽东", "诗词", "文章"], "📖 人文/社科"),
    (["小说", "百年孤独", "文学", "一句顶一万句"], "📖 人文/社科"),
]

def get_token():
    r = requests.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": APP_ID, "app_secret": APP_SECRET}, timeout=10)
    return r.json()["tenant_access_token"]

def get_existing_titles(token):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    titles, page_token = set(), None
    while True:
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BASE_TOKEN}/tables/{COLLECT_TABLE}/records?page_size=500"
        if page_token: url += f"&page_token={page_token}"
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
        if data.get("code") != 0: break
        for item in data["data"]["items"]:
            titles.add(item.get("fields", {}).get("标题", "").strip())
        if not data["data"].get("has_more"): break
        page_token = data["data"].get("page_token")
    return titles

def add_collection(token, fields):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = requests.post(
        f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BASE_TOKEN}/tables/{COLLECT_TABLE}/records",
        headers=headers, json={"fields": fields}, timeout=10)
    return r.json()

def classify(task_name, module):
    name_lower = (task_name + " " + module).lower()
    source = "🗂 其他"
    for keywords, val in SOURCE_MAP:
        if any(kw.lower() in name_lower for kw in keywords):
            source = val; break
    category = "🗂 其他"
    for keywords, val in CATEGORY_MAP:
        if any(kw.lower() in name_lower for kw in keywords):
            category = val; break
    return source, category

def parse_log(filepath):
    if not os.path.exists(filepath):
        print(f"❌ 文件不存在: {filepath}"); return []
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    sections = re.split(r"(?=^## \d{4}-\d{2}-\d{2})", content, flags=re.MULTILINE)
    entries = []
    for section in sections:
        if not section.strip(): continue
        date_match = re.search(r"## (\d{4}-\d{2}-\d{2})", section)
        if not date_match: continue
        date_str = date_match.group(1)
        rows = re.findall(r"\|\s*\d+\s*\|\s*\*\*([^*]+)\*\*\s*（([^）]+)）\s*\|\s*([^|]+)\s*\|\s*✅", section)
        rows += re.findall(r"\|\s*\d+\s*\|\s*([^|]+?)\s*\|\s*([^|]+)\s*\|\s*✅", section)
        for row in rows:
            if len(row) == 3:
                task_name, detail, module = row[0].strip(), row[1].strip(), row[2].strip()
            elif len(row) == 2:
                task_name, module, detail = row[0].strip(), row[1].strip(), ""
            else: continue
            if any(kw in task_name + detail for kw in ["入库", "收录", "原文", "全文", "PDF", "精读笔记", "笔记入库"]):
                entries.append((date_str, task_name, detail, module))
    return entries

def main():
    token = get_token()
    existing_titles = get_existing_titles(token)
    print(f"📋 已存在 {len(existing_titles)} 条收藏记录")
    entries = parse_log(LOG_PATH)
    print(f"🔍 搭建日志中找到 {len(entries)} 条喂料记录")
    added, skipped = 0, 0
    for date_str, task_name, detail, module in entries:
        title = task_name
        if title in existing_titles: skipped += 1; continue
        y, m, d = map(int, date_str.split("-"))
        ts = int(datetime(y, m, d, 0, 0, 0, tzinfo=TZ).timestamp() * 1000)
        source, category = classify(task_name + " " + detail, module)
        link = ""
        lm = re.search(r"https?://[^\s）]+", detail)
        if lm: link = lm.group(0)
        fields = {"标题": title, "来源链接": link, "我的感悟": detail[:200] if detail else "知识库原文留存。",
                  "来源类型": source, "分类": category, "收藏日期": ts, "状态": "✅ 已归档"}
        fields = {k: v for k, v in fields.items() if v}
        result = add_collection(token, fields)
        if result.get("code") == 0:
            print(f"  ✅ {date_str} {title[:40]}"); added += 1
        else:
            print(f"  ❌ {date_str} {title[:40]} → {result.get('msg','')}")
            if result.get("code") == 1800102: skipped += 1
    print(f"\n📊 总计: 新增 {added} 条, 跳过 {skipped} 条")

if __name__ == "__main__":
    main()
