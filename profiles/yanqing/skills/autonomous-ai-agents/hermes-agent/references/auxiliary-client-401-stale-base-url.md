# Title Generator / Auxiliary Client 401 from Stale OPENAI_BASE_URL

**Symptom:** Gateway startup log shows:
```
WARNING agent.auxiliary_client: OPENAI_BASE_URL is set (https://dashscope.aliyuncs.com/compatible-mode/v1) but model.provider is 'stepfun'. Auxiliary clients may route to the wrong endpoint.
WARNING agent.title_generator: Title generation failed: Error code: 401 - {'error': {'message': 'Incorrect API key provided', 'type': 'invalid_api_key'}}
```
The bot connects to Feishu successfully but auxiliary features (title generation, session titling) fail with 401.

**Root cause:** `~/.hermes/.env` contains a stale `OPENAI_BASE_URL` pointing at a different provider than the one configured in `config.yaml`. The auxiliary client reads `OPENAI_BASE_URL` and `OPENAI_API_KEY` directly from `.env`, ignoring `config.yaml`'s `model.base_url` / `api_key_env`. When the env var points at DashScope (or TokenHub, or any old provider) but the key in `.env` belongs to a different provider, auth fails with 401.

This is distinct from the main model 401 (covered in the dot-env-consistency section). The main model uses `api_key_env: DEEPSEEK_API_KEY` and reads from `.env` correctly; the **auxiliary client** uses `OPENAI_API_KEY`/`OPENAI_BASE_URL` and is poisoned by stale values.

**Diagnosis:**
```bash
grep "OPENAI_BASE_URL" ~/.hermes/.env
grep "OPENAI_API_KEY" ~/.hermes/.env
grep "WARNING agent.auxiliary_client" ~/.hermes/logs/agent.log* | tail -5
```

**Fix:**
```bash
# Remove the stale override so auxiliary falls back to the configured provider
sed -i '/^OPENAI_BASE_URL=/d' ~/.hermes/.env
# If OPENAI_API_KEY is a leftover from a different provider, remove it too
sed -i '/^OPENAI_API_KEY=/d' ~/.hermes/.env
```
Then restart the gateway.

**Why this happens:** When switching providers (e.g. OpenAI → DeepSeek → StepFun, or adding DashScope for a specific task), `OPENAI_BASE_URL` is set for the new provider but never cleaned up when the provider changes again. The auxiliary client has no provider-selection logic — it trusts `OPENAI_BASE_URL` blindly.

**Prevention:** After any provider switch via `hermes model` or manual config edit, audit `.env` for stale `OPENAI_BASE_URL` and `OPENAI_API_KEY` entries. They should either be removed or match the current provider.
