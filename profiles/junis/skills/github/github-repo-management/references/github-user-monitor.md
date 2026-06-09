# GitHub User Repo Monitoring & Auto-Sync

Watch specific GitHub users for new/changed repos and auto-pull tracked repos locally.

## Overview

Two mechanisms working together:
1. **Snapshot comparison** — periodically fetch all public repos from target users, compare `updated_at` against stored snapshot, report diffs
2. **Optimized auto-pull** — check remote commit date via API before `git pull`, skip git network if up-to-date

## Architecture

```
~/.hermes/scripts/monitor-github-tracked.py   # main script
~/.hermes/scripts/.github-snapshot.json       # persistent state (auto-created)
~/github-tracked/<user>/<repo>/               # local clones
```

## Script Design

### Key Patterns

**Snapshot-based change detection:**
```python
# Fetch all public repos (NOT search API — /users/{user}/repos endpoint)
url = f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated"
# Compare updated_at against saved snapshot
# Three event types: NEW repo, UPDATED repo, DELETED repo
```

**Optimized git pull (avoid slowness):**
```python
# Step 1: Compare local HEAD date vs remote latest commit date
remote_date > pushed_date  →  needs pull

# Step 2: Only git pull if confirmed outdated
git pull --ff-only
```

This avoids `git pull` network calls on 99% of runs (when nothing changed), reducing script runtime from minutes to seconds.

### Pitfalls

**Token type matters.** Classic PATs (`ghp_...42 chars`) use `Bearer` auth and work with `/users/{user}/repos` endpoint. Fine-grained PATs (`github_pat_...`) need explicit repo grants. Use the `X-OAuth-Scopes` response header to check capabilities:
```python
print(resp.headers.get('X-OAuth-Scopes'))  # → 'repo, notifications'
```

**Branch detection.** Repos may use `main` or `master`. Try both:
```python
for branch in ["main", "master"]:
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{branch}"
```

**WSL git clone fails — "unexpected disconnect while reading sideband packet".**
Fix: downgrade git HTTP to HTTP/1.1:
```bash
git config --global http.version HTTP/1.1
git config --global http.postBuffer 524288000
```

**No_agent cron pattern.** For script-only watchdog delivery:
```python
# Script output gets delivered verbatim to Feishu/Telegram/etc.
# Empty stdout = silent delivery (no notification when nothing changed)
if not changes and not pull_results_with_updates:
    return  # silent exit
```

## no_agent Cron Setup

```bash
# Create the cron job
hermes cron create --schedule "every 12h" \
    --name "github-tracker-monitor" \
    --script "monitor-github-tracked.py" \
    --no-agent \
    --deliver "feishu"
```

Key: `no_agent=True` — pure script execution, no LLM cost. `deliver="feishu"` sends script stdout to Feishu home channel.

## Script Template

Place at `~/.hermes/scripts/monitor-github-tracked.py`:

```python
#!/usr/bin/env python3
"""Monitor GitHub users for repo changes, auto-pull tracked repos."""

import json, os, subprocess, sys, urllib.request
import yaml

# Config
TRACKED_DIR = os.path.expanduser("~/github-tracked")
SNAPSHOT_FILE = os.path.expanduser("~/.hermes/scripts/.github-snapshot.json")
USERS = ["alchaincyf", "AIPMAndy"]  # <-- customize
AUTO_PULL_REPOS = [
    "alchaincyf/nuwa-skill",
    # <-- add repos to auto-pull
]
VERBOSE = "--verbose" in sys.argv

def get_github_token():
    config_path = os.path.expanduser("~/.hermes/config.yaml")
    with open(config_path) as f:
        config = yaml.safe_load(f)
    return config["mcp_servers"]["github"]["env"]["GITHUB_PERSONAL_ACCESS_TOKEN"]

def fetch_user_repos(token, username):
    """Fetch ALL public repos via paginated API."""
    repos, url = [], f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated"
    while url:
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Hermes-Monitor",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            page = json.loads(resp.read())
            repos.extend({
                "name": r["name"], "full_name": r["full_name"],
                "description": (r["description"] or "")[:100],
                "updated_at": r["updated_at"], "pushed_at": r["pushed_at"],
                "html_url": r["html_url"], "language": r.get("language"),
            } for r in page)
            link = resp.headers.get("Link", "")
            url = None
            if 'rel="next"' in link:
                for part in link.split(","):
                    if 'rel="next"' in part:
                        url = part.split(";")[0].strip(" <>")
    return repos

def check_repo_needs_update(token, owner, repo, local_path):
    """API check before git pull — avoids network timeouts."""
    # Get local HEAD date
    result = subprocess.run(
        ["git", "-C", local_path, "log", "-1", "--format=%cI"],
        capture_output=True, text=True, timeout=10
    )
    local_date = result.stdout.strip()
    if not local_date:
        return True
    # Check remote
    for branch in ["main", "master"]:
        url = f"https://api.github.com/repos/{owner}/{repo}/commits/{branch}"
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Hermes-Monitor"
        })
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                remote_date = data.get("commit", {}).get("committer", {}).get("date", "")
                return remote_date > local_date
        except urllib.error.HTTPError:
            continue  # try next branch
    return True  # pull to be safe

# Main flow: snapshot comparison + auto-pull
# (Full implementation at ~/.hermes/scripts/monitor-github-tracked.py)
```
