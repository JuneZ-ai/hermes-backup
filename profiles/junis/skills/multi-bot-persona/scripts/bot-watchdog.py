#!/usr/bin/env python3
"""三Bot网关巡检脚本 — 每30分钟检查，死掉自动重启"""
import json, os, subprocess, sys, time
from pathlib import Path

HERMES = "/usr/local/bin/hermes"
PROFILES_DIR = Path.home() / ".hermes" / "profiles"
PROFILES = [
    ("saodiseng",  "扫地僧"),
    ("yanqing",    "燕青"),
    ("huanglaoxie","黄老邪"),
    ("luban",      "鲁班"),
]

def check_and_restart(profile_name, display_name):
    state_file = PROFILES_DIR / profile_name / "gateway_state.json"
    lock_file = PROFILES_DIR / profile_name / "gateway.lock"
    pid_file = PROFILES_DIR / profile_name / "gateway.pid"

    pid = None
    if state_file.exists():
        try:
            data = json.loads(state_file.read_text())
            pid = data.get("pid")
        except (json.JSONDecodeError, KeyError):
            pass

    alive = False
    if pid:
        try:
            subprocess.run(["ps", "-p", str(pid), "-o", "pid", "--no-headers"],
                         capture_output=True, timeout=5)
            alive = True
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            pass

    if alive:
        return f"+ {display_name} (PID={pid}) 正常运行"

    # 进程死了 -> 清理旧锁 + 重启
    for f in [lock_file, pid_file]:
        if f.exists():
            f.unlink()
    state_file.write_text("{}")

    log_path = Path.home() / "bot-watchdog" / f"{profile_name}-restart.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        proc = subprocess.Popen(
            [HERMES, "-p", profile_name, "gateway", "run", "--replace"],
            cwd=str(PROFILES_DIR / profile_name),
            stdout=open(log_path, "w"),
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        time.sleep(3)
        if proc.poll() is None:
            return f"~ {display_name} 已重启 (new PID={proc.pid})"
        else:
            return f"- {display_name} 重启失败 (exit_code={proc.returncode})，详情见 {log_path}"
    except Exception as e:
        return f"- {display_name} 启动异常: {e}"

def main():
    results = []
    for name, display in PROFILES:
        try:
            result = check_and_restart(name, display)
        except Exception as e:
            result = f"- {display} 巡检异常: {e}"
        results.append(result)
        print(result)

    ok_count = sum(1 for r in results if r.startswith("+"))
    print(f"\n健康度: {ok_count}/{len(results)}")
    if ok_count < len(results):
        print("异常，请检查")

if __name__ == "__main__":
    main()
