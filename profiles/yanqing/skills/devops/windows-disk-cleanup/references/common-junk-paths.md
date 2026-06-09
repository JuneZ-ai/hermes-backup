# Common Windows Junk Paths

All paths are under `/mnt/c/` (C: drive). Replace `<user>` with the actual Windows username.

## Safe to Clean (automatic)

| Path | Typical Size | Notes |
|---|---|---|
| `Users/<user>/AppData/Local/Temp` | 1–5 GB | User temp files. Some in-use files won't delete — normal. |
| `Users/<user>/AppData/Local/Google/Chrome/User Data/Default/Cache` | 100–500 MB | Chrome browser cache. |
| `Users/<user>/AppData/Local/Microsoft/Edge/User Data/Default/Cache` | 100–500 MB | Edge browser cache. |
| `Users/<user>/AppData/Local/Microsoft/Windows/INetCache` | 5–50 MB | IE/Edge legacy internet cache. |
| `Users/<user>/.cache` | 100–300 MB | User-level cache (various apps). |
| `Windows/Temp` | 50–500 MB | System temp. Many files in use — delete what you can. |
| `ProgramData/Package Cache` | 100–500 MB | MSI installer cache. May need admin rights in Windows to fully clear. |

## Needs User Confirmation

| Path | Typical Size | Notes |
|---|---|---|
| `Users/<user>/Downloads` | 5–15 GB | List top items for user to evaluate. |
| `Users/<user>/Desktop` | 5–20 GB | Often huge due to files dropped there. User needs to triage. |
| `$Recycle.Bin` | 0–30 GB | Confirm no important files before emptying. |
| `Users/<user>/AppData/Roaming/Tencent/xwechat` | 3–8 GB | WeChat main data store. Deleting loses chat history. |
| `Users/<user>/AppData/Roaming/Tencent/WeChat` | 1–3 GB | WeChat app data + cache. |
| `Users/<user>/Documents/WeChat Files` | 0.5–2 GB | WeChat received files. |
| `Users/<user>/AppData/Local/Tencent` | 0–500 MB | Other Tencent app data. |

## Do NOT Touch

| Path | Reason |
|---|---|
| `Windows/Installer` | MSI cache — removing breaks program uninstall. |
| `Windows/System32/driverstore` | Driver store — removing breaks device drivers. |
| `Windows/WinSxS` | Component store — Windows needs this; use DISM instead. |
| `Windows/SoftwareDistribution` | Windows Update — only clear if instructed (usually negligible size anyway). |

## WeChat Built-in Cleanup (recommended over direct deletion)

Path: Settings → General → Storage Space Management

- **Cache** — safe to clear, no data loss
- **Chat Records** — granular: delete by contact, by time range, or by file type (images/videos/files)
- **Other Data** — app binaries, do not touch
