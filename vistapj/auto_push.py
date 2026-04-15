#!/usr/bin/env python3
import os
import subprocess
import sys
import time

REPO_DIR = os.path.abspath(os.path.dirname(__file__))
WATCH_PATHS = ["index.html"]
POLL_INTERVAL = 0.5
DEBOUNCE_SEC = 1.0


def run_git(*args):
    return subprocess.run(
        ["git", "-C", REPO_DIR, *args],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def get_mtime(path):
    try:
        return os.path.getmtime(path)
    except FileNotFoundError:
        return 0.0


def has_changes():
    res = run_git("status", "--porcelain")
    return res.returncode == 0 and bool(res.stdout.strip())


def auto_commit_and_push():
    run_git("add", "-A")
    if not has_changes():
        return
    msg = time.strftime("auto: update %Y-%m-%d %H:%M:%S")
    commit = run_git("commit", "-m", msg)
    if commit.returncode != 0:
        print(commit.stdout.strip())
        return
    push = run_git("push", "origin", "main")
    if push.returncode != 0:
        print(push.stdout.strip())


def main():
    watch_files = [os.path.join(REPO_DIR, p) for p in WATCH_PATHS]
    last = {p: get_mtime(p) for p in watch_files}
    pending_since = None

    print("Watching for changes:", ", ".join(WATCH_PATHS))
    try:
        while True:
            changed = False
            for p in watch_files:
                mtime = get_mtime(p)
                if mtime != last.get(p, 0.0):
                    last[p] = mtime
                    changed = True
            if changed:
                pending_since = time.time()
            if pending_since and time.time() - pending_since >= DEBOUNCE_SEC:
                auto_commit_and_push()
                pending_since = None
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("\nStopped.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
