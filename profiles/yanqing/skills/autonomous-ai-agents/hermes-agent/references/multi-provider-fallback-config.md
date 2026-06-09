# Multi-Provider Fallback Config Template

**Use when:** A profile needs a primary model with a fallback provider for resilience.

## Known-Good Pattern (verified across 4 profiles)

```yaml
model:
  default: <primary-model-name>
  provider: <primary-provider-name>
  base_url: https://api.<primary>.com   # omit for deepseek (uses default)
providers:
  <primary-provider>:
    api_key_env: <PRIMARY>_API_KEY
    base_url: https://api.<primary>.com
    models:
    - <primary-model-name>
    - <primary-model-variant>          # optional: list all available models
  stepfun:
    api_key_env: STEPFUN_API_KEY
    base_url: https://api.stepfun.com/v1
    models:
    - step-3.5-flash
fallback_providers:
- provider: stepfun
  models:
  - step-3.5-flash
  activation:
    mode: sequential
    min_priority: 1
```

## Profile Inventory (as of 2026-05-31)

| Profile | Primary | Fallback |
|---------|---------|----------|
| junis | deepseek-v4-flash | step-3.5-flash |
| yanqing | step-3.7-flash | (none — single provider) |
| huanglaoxie | deepseek-v4-flash | step-3.5-flash |
| saodiseng | deepseek-v4-flash | step-3.5-flash |

## Pitfalls

1. **STEPFUN_API_KEY must exist in the profile's `.env`** — providers section references it but does NOT inherit from root `.env`.
2. **activation block is required for fallback to engage** — without `mode: sequential` + `min_priority: 1`, fallback may not trigger on primary failure.
3. **yanqing uses stepfun as primary** — no fallback configured; if stepfun is down, the bot goes dark. Consider adding deepseek fallback if resilience is needed.
