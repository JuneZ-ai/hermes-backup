# Main Model 401 — Provider-Revoked API Key

**Symptom:** Gateway logs show repeated 401 errors from the **main model provider** (not auxiliary):

```
❌ Non-retryable client error (HTTP 401). Aborting.
   📝 Error: HTTP 401: Authentication Fails, Your api key: ****ired is invalid
   📋 Details: {'message': 'Authentication Fails, ...', 'type': 'authentication_error', 'param': None, 'code': 'invalid_request_error'}
```

The bot may connect to Feishu successfully but **all model calls fail** — the user sees no replies.

**Distinction from other 401 patterns:**

| Pattern | Error signature | Root cause | Fix |
|---------|----------------|------------|-----|
| Auxiliary 401 (stale base URL) | `agent.auxiliary_client` + `agent.title_generator` warnings | `OPENAI_BASE_URL` points at wrong provider | Remove stale `OPENAI_BASE_URL` from `.env` |
| Placeholder key | `OPENAI_API_KEY=***` (literal asterisks) | `.env` never got a real key | Replace with actual key |
| Key mismatch across profiles | Different key values in main vs profile `.env` | Inconsistent rotation | Sync all `.env` files |
| **Provider-revoked key** | `Authentication Fails, Your api key: ****ired is invalid` | **Provider side revoked/expired the key** | Generate new key at provider dashboard |

**Diagnosis:**

```bash
# 1. Confirm it's the main model (not auxiliary)
grep "Non-retryable client error (HTTP 401)" ~/.hermes/logs/errors.log | tail -5

# 2. Check key consistency across .env files
for p in ~/.hermes ~/.hermes/profiles/*/; do
  echo "$p:"; grep "DEEPSEEK_API_KEY\|OPENAI_API_KEY" "$p.env" 2>/dev/null | head -1
done

# 3. If keys are consistent AND error says "invalid" (not "missing"), it's provider-side revocation
#    The key prefix/suffix will match across files but the provider rejects it
```

**Fix — two-step diagnostic:**

**Step 1: Verify the key is actually valid at the provider**
```bash
python3 -c "
import urllib.request, json
with open('$HOME/.hermes/.env') as f:
    key = [l.split('=',1)[1].strip() for l in f if l.startswith('DEEPSEEK_API_KEY=')][0]
req = urllib.request.Request('https://api.deepseek.com/v1/chat/completions',
  data=json.dumps({'model':'deepseek-chat','messages':[{'role':'user','content':'hi'}]}).encode(),
  headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'})
with urllib.request.urlopen(req, timeout=10) as r: print(f'Key valid: {r.status}')
"
```
- If this returns 200 → key is valid, problem is in Hermes config/auth cache
- If this returns 401 → provider has revoked the key, proceed to Step 2

**Step 2a: If key is valid but gateway still 401s — clear credential_pool**
```bash
python3 -c "
import json
p = '$HOME/.hermes/auth.json'
d = json.load(open(p))
if 'credential_pool' in d:
    d['credential_pool'] = {}
    json.dump(d, open(p, 'w'), indent=2)
    print('credential_pool cleared')
"
systemctl --user restart hermes-gateway
```

**Step 2b: If key is invalid at the provider — rotate key**
- Log in to provider dashboard (e.g., `platform.deepseek.com`)
- Generate new API key
- Update **all** `.env` files: `~/.hermes/.env` + `~/.hermes/profiles/<name>/.env` for each profile
- Clear credential_pool (Step 2a) — the old revoked entry persists in auth.json and will override the new .env value
- Restart gateway

**Why credential_pool matters:** Hermes loads credentials from `auth.json` → `credential_pool` at gateway startup, taking priority over `.env`. Even after updating `.env` with a valid key, a stale revoked entry in credential_pool will cause persistent 401s. Always clear both when rotating keys.

**Prevention:** Key rotation checklist = update `.env` + clear `credential_pool` + restart gateway. Monitor `errors.log` for `Authentication Fails`.
