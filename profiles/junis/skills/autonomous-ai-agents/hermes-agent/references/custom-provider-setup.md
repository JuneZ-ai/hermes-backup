# Custom OpenAI-Compatible Provider Setup

Add a non-built-in provider (e.g. StepFun/阶跃星辰) that's OpenAI API-compatible, alongside built-in providers, with the ability to switch between them via `/model`.

## Overview

Hermes supports 20+ built-in providers out of the box. For providers not in the built-in list (like StepFun), use the `model_catalog.providers` section to register them as switchable alternatives.

## Step-by-Step

### 1. Add API Key to `.env`

```bash
# ~/.hermes/.env
STEPFUN_API_KEY=your_key_here
```

Respect the [tool update protocol](tool-update-protocol.md): notify user before modifying `.env`.

### 2. Register Provider in `model_catalog.providers`

In `~/.hermes/config.yaml`:

```yaml
model_catalog:
  enabled: true
  providers:
    stepfun:                              # provider name for /model switching
      api_key_env: STEPFUN_API_KEY        # env var name (NOT inline key)
      base_url: https://api.stepfun.com/v1
      models:
        - step-3.5-flash                  # list available models
        - step-2-16k
        - step-1-flash
    deepseek:                             # built-in providers also work here
      api_key_env: DEEPSEEK_API_KEY
      base_url: https://api.deepseek.com
      models:
        - deepseek-chat
        - deepseek-reasoner
```

### 3. Set Active Default

The `model` section at the top of `config.yaml` controls which provider+model is used for **new sessions**:

```yaml
model:
  provider: stepfun               # matches one of model_catalog.providers keys
  name: step-3.5-flash
  api_key_env: STEPFUN_API_KEY
  api_base: https://api.stepfun.com/v1
  default: step-3.5-flash
  base_url: https://api.stepfun.com/v1
```

### 4. Switching Models

**In-session (slash command):**
```
/model stepfun/step-3.5-flash
/model deepseek/deepseek-chat
```

This changes the model for subsequent turns in the **current session**. If it doesn't appear to take effect, verify the model name matches exactly what's in `model_catalog.providers.<name>.models`.

**New session (CLI flags):**
```bash
hermes -m stepfun/step-3.5-flash
hermes -m deepseek/deepseek-chat
```

**Interactive picker:**
```bash
hermes model
```

### 5. Verify

Check which model is active:
```
/model        # shows current model
```

Or check response header — the system shows `Model: <provider>/<model>` on each reply.

## Pitfalls

- **API key in config.yaml vs .env**: Never put raw API keys in `config.yaml`. Use `api_key_env: VAR_NAME` pointing to an env var, and store the actual key in `.env`. The `.env` file is read at startup and does NOT need a gateway restart for CLI sessions, but does need a gateway restart for messaging platforms.

- **Model name mismatch**: `/model stepfun/step-3.5-flash` won't work if `step-3.5-flash` isn't listed under `model_catalog.providers.stepfun.models`. Keep the lists in sync.

- **`/model` not taking effect**: Some config changes require `/reset` (new session). `/model` itself should work mid-session, but if the user reports "还是deepseek啊", double-check the model name spelling matches exactly.

- **No fallback**: If the primary provider is down and no `fallback_providers` are configured, the session will error out. See `fallback_providers` in the config for auto-failover setup.
