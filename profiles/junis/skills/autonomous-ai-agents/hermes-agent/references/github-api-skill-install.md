# GitHub API Skill Installation (git clone fallback)

When `git clone` fails (WSL network issues, timeouts, firewall), use the GitHub API to download individual skill files.

## Prerequisites

No auth needed for public repos. Rate limit: 60 requests/hr unauthenticated.

## One-liner: Download a single SKILL.md from any repo

```bash
# From a known repo path
curl -sL -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/{owner}/{repo}/contents/{path}/SKILL.md" \
| python3 -c "
import sys,json,base64
d=json.load(sys.stdin)
with open('/dev/stdout','wb') as f:
    f.write(base64.b64decode(d['content']))
" > ~/.hermes/skills/{category}/{skill-name}/SKILL.md
```

## Full multi-file workflow

```bash
# 1. List repo contents
curl -sL "https://api.github.com/repos/{owner}/{repo}/contents" \
| python3 -c "import sys,json; [print(x['name']) for x in json.load(sys.stdin)]"

# 2. List sub-directory (e.g., references/)
curl -sL "https://api.github.com/repos/{owner}/{repo}/contents/references" \
| python3 -c "import sys,json; [print(x['name']) for x in json.load(sys.stdin)]"

# 3. Download each file
for file in SKILL.md references/foo.md scripts/bar.sh; do
  curl -sL -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/{owner}/{repo}/contents/$file" \
  | python3 -c "
import sys,json,base64
d=json.load(sys.stdin)
with open('/dev/stdout','wb').write(base64.b64decode(d['content']))
" > ~/.hermes/skills/{category}/{skill-name}/$file
done
```

## Binary file handling

For images (.png, .jpg, .gif) or other binary files, the API returns base64 content the same way — decode and write as bytes:
```python
import sys, json, base64
d = json.load(sys.stdin)
with open('output.png', 'wb') as f:
    f.write(base64.b64decode(d['content']))
```

## Troubleshooting

| Error | Likely cause | Fix |
|-------|-------------|-----|
| `KeyError: 'content'` | File doesn't exist or path wrong | Check the repo's directory structure first |
| `'message': 'Not Found'` | 404 — wrong owner/repo/path | Verify the URL; repos may require auth |
| `UnicodeDecodeError` | File contains non-UTF-8 chars | Use `open(f,'wb')` instead of `open(f,'w',encoding='utf-8')` |
| Empty output | Rate limited or network blocked | Wait 1 minute; try with a `-H "Authorization: token $GITHUB_TOKEN"` header |
