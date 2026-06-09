#!/usr/bin/env python3
"""每日保底记录脚本：检查每日记录表，当天无记录则补充空白记录"""
import requests, os, sys, datetime, json

# 飞书凭证
APP_TOKEN = "NzuPbMtMFa0wUusVQKwc69lenib"
APP_ID = os.environ.get("FEISHU_APP_ID", "cli_aa869b8d6b3c5cc3")
APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "qSk4tz...VaHN")

def get_token():
    resp = requests.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": APP_ID, "app_secret": APP_SECRET}, timeout=10)
    data = resp.json()
    if data.get("code") != 0:
        print("TOKEN_ERROR:", json.dumps(data))
        sys.exit(1)
    return data["tenant_access_token"]

def get_today_ms():
    """UTC+8 当天0点毫秒时间戳"""
    tz = datetime.timezone(datetime.timedelta(hours=8))
    now = datetime.datetime.now(tz)
    today = datetime.datetime(now.year, now.month, now.day, tzinfo=tz)
    return int(today.timestamp() * 1000)

def get_lunar_info():
    """计算当日农历信息"""
    try:
        from lunar_python import Solar
        tz = datetime.timezone(datetime.timedelta(hours=8))
        now = datetime.datetime.now(tz)
        s = Solar.fromYmd(now.year, now.month, now.day)
        l = s.getLunar()
        lunar_str = l.getMonthInChinese() + "月" + l.getDayInChinese()
        gan_zhi = l.getYearInGanZhi() + "年 " + l.getMonthInGanZhi() + "月 " + l.getDayInGanZhi() + "日"
        yi = l.getDayYi()
        ji = l.getDayJi()
        chong = l.getDayChong()
        yi_str = "、".join(yi[:8]) if yi else "无"
        ji_str = "、".join(ji[:6]) if ji else "无"
        huangli = "宜：" + yi_str + "\n忌：" + ji_str + "\n冲：" + chong
        jieqi = s.getJieQi() or ""
        return lunar_str, gan_zhi, huangli, jieqi
    except ImportError:
        return "", "", "", ""

def main():
    token = get_token()
    today_ms = get_today_ms()
    headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json; charset=utf-8"}
    base_url = "https://open.feishu.cn/open-apis/bitable/v1/apps/" + APP_TOKEN

    results = []

    # ===== 每日记录 =====
    daily_table = "tblTLllADiUdhL6e"
    resp = requests.get(base_url + "/tables/" + daily_table + "/records?page_size=50", headers=headers, timeout=10)
    items = resp.json().get("data", {}).get("items", [])
    has_record = any(r.get("fields", {}).get("公历时间") == today_ms for r in items)

    if not has_record:
        lunar_str, gan_zhi, huangli, jieqi = get_lunar_info()
        rec = {
            "fields": {
                "公历时间": today_ms,
                "农历": lunar_str,
                "节气": jieqi,
                "干支": gan_zhi,
                "黄历宜忌": huangli,
                "记录内容": "今日无操作",
                "类型": "💼 工作"
            }
        }
        r = requests.post(base_url + "/tables/" + daily_table + "/records", headers=headers, json=rec, timeout=10)
        if r.json().get("code") == 0:
            results.append("每日记录: 已补充今日空白记录")
        else:
            results.append("每日记录失败: " + str(r.json()))
    else:
        results.append("每日记录: 今日已有记录")

    # ===== 搭建日志保底 =====
    log_table = "tbllV9WgN64Zwput"
    resp = requests.get(base_url + "/tables/" + log_table + "/records?page_size=50", headers=headers, timeout=10)
    items = resp.json().get("data", {}).get("items", [])
    has_log = any(r.get("fields", {}).get("时间") == today_ms for r in items)
    if not has_log:
        rec = {
            "fields": {
                "操作内容": "今日无知识库操作",
                "领域": "工具配置",
                "时间": today_ms,
                "状态": "✅ 已完成"
            }
        }
        r = requests.post(base_url + "/tables/" + log_table + "/records", headers=headers, json=rec, timeout=10)
        if r.json().get("code") == 0:
            results.append("搭建日志: 已补充今日无操作")
        else:
            results.append("搭建日志失败: " + str(r.json()))
    else:
        results.append("搭建日志: 今日已有记录")

    print("\n".join(results))

if __name__ == "__main__":
    main()
