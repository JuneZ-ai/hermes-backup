#!/usr/bin/env python3
"""
Create a Feishu document from a markdown file via Feishu Open API (docx).
Usage: python3 scripts/create-feishu-doc.py <markdown_file> [title]
"""
import requests, sys, re

FEISHU_APP_ID = "cli_aa869b8d6b3c5cc3"
FEISHU_APP_SECRET = "qSk4tz1A15aWo5K4eFw2lbhibgMAVaHN"

BT = {
    "text": 2, "heading1": 3, "heading2": 4, "heading3": 5, "heading4": 6,
    "bullet": 12, "ordered": 13, "code": 14,
}

def get_token():
    r = requests.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}, timeout=10)
    return r.json()['tenant_access_token']

def create_doc(token, title):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = requests.post("https://open.feishu.cn/open-apis/docx/v1/documents",
        headers=headers, json={"title": title}, timeout=10)
    data = r.json()
    if data.get('code') != 0:
        raise Exception(f"create_doc: {data}")
    return data['data']['document']

def add_batch(token, doc_id, parent_id, blocks):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = requests.post(
        f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{parent_id}/children",
        headers=headers, json={"children": blocks}, timeout=60)
    data = r.json()
    return data.get('code') == 0

def te(content, bold=False):
    el = {"text_run": {"content": content}}
    if bold:
        el["text_run"]["text_element_style"] = {"bold": True}
    return el

def parse_md(md_text):
    blocks = []
    lines = md_text.split('\n')
    i = 0
    in_code = False
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith('```'):
            in_code = not in_code
            if in_code:
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                in_code = False
                if code_lines:
                    blocks.append({"block_type": BT["code"],
                        "code": {"elements": [{"text_run": {"content": '\n'.join(code_lines)}}]}})
            i += 1
            continue
        if in_code:
            i += 1; continue
        s = line.strip()
        if s in ('---', '***', '___'):  # dividers not supported
            i += 1; continue
        if line.startswith('# '):
            blocks.append({"block_type": BT["heading1"], "heading1": {"elements": [te(s[2:])]}})
        elif line.startswith('## '):
            blocks.append({"block_type": BT["heading2"], "heading2": {"elements": [te(s[3:])]}})
        elif line.startswith('### '):
            blocks.append({"block_type": BT["heading3"], "heading3": {"elements": [te(s[4:])]}})
        elif line.startswith('#### '):
            blocks.append({"block_type": BT["heading4"], "heading4": {"elements": [te(s[5:])]}})
        elif s.startswith('- ') or s.startswith('* '):
            content = s[2:]
            m = re.match(r'\*\*(.+?)\*\*(.*)', content)
            els = [te(m.group(1), bold=True)] + ([te(m.group(2).strip())] if m and m.group(2).strip() else [])
            if not m:
                els = [te(content)]
            blocks.append({"block_type": BT["bullet"], "bullet": {"elements": els}})
        elif re.match(r'^\d+[.、]', s):
            content = re.sub(r'^\d+[.、]\s*', '', s)
            blocks.append({"block_type": BT["ordered"], "ordered": {"elements": [te(content)]}})
        elif s.startswith('> '):
            blocks.append({"block_type": BT["text"], "text": {"elements": [te(s[2:])]}})
        elif s.startswith('| '):
            tbl = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                tbl.append(lines[i]); i += 1
            blocks.append({"block_type": BT["code"],
                "code": {"elements": [{"text_run": {"content": '\n'.join(tbl)}}]}})
            continue
        elif s:
            parts = re.split(r'(\*\*.*?\*\*)', s)
            if len(parts) > 1:
                els = []
                for p in parts:
                    if p.startswith('**') and p.endswith('**'):
                        els.append(te(p[2:-2], bold=True))
                    elif p:
                        els.append(te(p))
                blocks.append({"block_type": BT["text"], "text": {"elements": els}})
            else:
                blocks.append({"block_type": BT["text"], "text": {"elements": [te(s)]}})
        i += 1
    return blocks

def main():
    if len(sys.argv) < 2:
        print("Usage: create-feishu-doc.py <markdown_file> [title]"); sys.exit(1)
    with open(sys.argv[1], encoding='utf-8') as f:
        md = f.read()
    title = sys.argv[2] if len(sys.argv) > 2 else "文档"
    token = get_token()
    doc = create_doc(token, title)
    doc_id = doc['document_id']
    blocks = parse_md(md)
    BATCH = 30
    success = 0
    fail = []
    for start in range(0, len(blocks), BATCH):
        batch = blocks[start:start + BATCH]
        if add_batch(token, doc_id, doc_id, batch):
            success += len(batch)
        else:
            for j, blk in enumerate(batch):
                if add_batch(token, doc_id, doc_id, [blk]):
                    success += 1
                else:
                    fail.append(start + j)
    print(f"{success}/{len(blocks)} blocks")
    if fail:
        print(f"Failed: {fail}")
    print(f"https://bytedance.feishu.cn/docx/{doc_id}")

if __name__ == "__main__":
    main()
