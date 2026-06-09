# API Key Truncated in .env — Diagnosis Checklist

## Symptom
Auxiliary vision client (or any API call) fails with 401 / key-related error even though DASHSCOPE_API_KEY is present in .env.

## Root Cause
The API key value was stored truncated in .env — manual copy-paste, shell-escaped insertion, or editor silently cutting a long value.

## Verification
A valid DashScope key is 30–40+ characters. A value like sk-03e...551d with only 13 characters is definitely truncated.

## Why This Happens
- Dashboard copy-paste: console truncates key in UI; must click "Show full key" before copying.
- Terminal echo: long env-var values get wrapped with backslash continuation if pasted without care.
- Credential pool stale override: auth.json credential_pool can cache old revoked key that overrides .env.

## Fix
1. Open DashScope console: https://dashscope.console.aliyun.com/
2. Reveal full API key (click "Show" / eye icon)
3. Update .env with the complete value
4. Clear credential pool: hermes auth reset dashscope
5. Restart session

## Pitfall: credential_pool overrides .env
If auth.json has a cached key in credential_pool, it overrides .env. After any key rotation, run hermes auth reset <provider> to clear cache.
