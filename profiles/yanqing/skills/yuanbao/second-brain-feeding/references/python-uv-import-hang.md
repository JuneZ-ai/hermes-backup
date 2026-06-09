# Python UV Import Hang (Hermes Agent WSL)

## Symptom
`python3 -c "import ebooklib"` hangs indefinitely (times out at 10s+).
`python3 --version` returns `Python 3.11.15` normally.
`echo "alive"` works fine in the same terminal.

## Root Cause
The `python3` on PATH points to:
```
/usr/local/lib/hermes-agent/venv/bin/python3
  → python (symlink)
  → /root/.local/share/uv/python/cpython-3.11.15-linux-x86_64-gnu/bin/python3.11
```

This is a **Hermes Agent managed Python via uv** that hangs on `import` of any non-builtin module. Even `import sys` times out after the pip install, though a fresh interpreter works briefly. The hang is likely a site.py startup issue or a pipe/stdin deadlock in the uv isolation layer.

## Verified Working Alternative

```
/usr/bin/python3.14
```

This is the **system Debian Python 3.14** installed at the OS level. It works fine with `--break-system-packages`:

```bash
/usr/bin/python3.14 -m pip install --break-system-packages ebooklib mobi
/usr/bin/python3.14 -c "import ebooklib; print('ok')"  # works
```

## Fix Applied

- Script shebang: `#!/usr/bin/env python3.14`
- CLI wrapper: `ebook2md` at `/home/hermes/.local/bin/ebook2md` invokes `/usr/bin/python3.14` directly
- Memory entry recorded for future sessions

## Detection

```bash
which python3   # /usr/local/lib/hermes-agent/venv/bin/python3
file $(which python3)  # symbolic link to python
# VS
ls /usr/bin/python3*  # reveals /usr/bin/python3.14 is available
```
