# Python Package Install in WSL — `--break-system-packages` Pattern

## Symptom
`pip install <package>` fails with `error: externally-managed-environment` on WSL Debian.

## Cause
Debian/Ubuntu PEP 668 enforcement blocks `pip` to `/usr/local/lib/python3.X/dist-packages`. The system Python is externally managed.

## Fix
Use the same Python version that already works for the project (check which `python3` can `import` the required deps):

```bash
# 1. Identify working Python (often python3.14 in WSL)
which python3.14

# 2. Install with that Python, allowing user-site override
python3.14 -m pip install --break-system-packages <package>

# 3. Verify
python3.14 -c "import <package>; print('OK')"
```

## Why not `--user` alone
`--user` often silently fails if `PYTHONNOUSERSITE` is set or site-packages dir is non-standard. `--break-system-packages` with the correct Python binary is more reliable.

## Why not virtualenv
Hermes scripts and cron jobs call `python3` directly (not a venv path). A venv would need to be activated in every entry point. Using system Python with `--break-system-packages` avoids that coordination overhead.

## Known working Python versions in this environment
- `python3.14` — confirmed working, can import all installed packages
- `python3` / `python3.11` — uv-managed, import may fail for some packages
