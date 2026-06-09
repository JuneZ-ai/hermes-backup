# Lark-CLI Feishu Doc Export Workflow

> Use `lark-cli drive +export` to export Feishu docx/doc/sheet/slides as markdown or other formats.
> Falls back to the docs_ai API when `feishu_doc_read` is unavailable (no Feishu comment context).

## Prerequisites

- `lark-cli` installed and authenticated with user OAuth (not bot token)
- User identity must have **read permission** on the target document
- The doc token is the last path segment of the Feishu URL: `https://my.feishu.cn/docx/F4Pzd71i2osBaXx2PaocWFQunde` → token = `F4Pzd71i2osBaXx2PaocWFQunde`

## Export Command

```bash
# Dry run to verify permissions first
lark-cli drive +export --token <TOKEN> --doc-type docx --file-extension markdown --dry-run

# Actual export (saves to current directory)
lark-cli drive +export --token <TOKEN> --doc-type docx --file-extension markdown
```

### Flags

| Flag | Required | Values |
|:-----|:---------|:-------|
| `--token` | ✅ | Document token from URL |
| `--doc-type` | ✅ | `doc` \| `docx` \| `sheet` \| `bitable` \| `slides` |
| `--file-extension` | ✅ | `markdown` \| `docx` \| `pdf` \| `xlsx` \| `csv` \| `base` (bitable only) |
| `--output-dir` | ❌ | Default: current directory. ⚠️ **Must be a relative path** (absolute paths rejected) |
| `--file-name` | ❌ | Custom output filename (optional) |
| `--dry-run` | ❌ | Print API call without executing |
| `--overwrite` | ❌ | Overwrite existing output file |

### Pitfalls

| Issue | Fix |
|:------|:----|
| **"unsafe output path"** | `--output-dir` only accepts relative paths. `cd` to target directory first |
| **Export fails after auth** | Re-authenticate: `lark-cli config bind --source hermes --identity user-default` |
| **Export succeeds but file empty** | Check actual content. Try `--file-extension docx` instead of markdown |

## Integration with obsidian-ingestion-pipeline

When processing a Feishu doc link in the knowledge ingestion pipeline:

1. **Extract token** from URL: `https://my.feishu.cn/docx/{TOKEN}`
2. **Export to md**: `cd /tmp && lark-cli drive +export --token {TOKEN} --doc-type docx --file-extension markdown`
3. **Read content**: `read_file` on the exported markdown file
4. **Classify & process**: Follow standard pipeline (classify → extract → enrich notes → update total outline)
5. **Archive raw source**: Save original markdown to `_raw_sources/articles/<title>.md`

> ⚠️ The `feishu_doc_read` tool only works inside a Feishu comment context. For general Feishu document access, use `lark-cli drive +export`.
