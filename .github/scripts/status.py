"""Live progress dashboard: STATUS.md on the `status` branch (open it on GitHub to watch).

status.py queue                         (reads $MATRIX) mark these exams queued
status.py set <dir> <state> [bytes]     state: rendering | done | failed
status.py pct <dir> <percent>           progress while rendering
Many jobs push at once, so each update retries with a fresh pull.
"""
import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = os.environ.get("GITHUB_REPOSITORY", "")
RUN = f"https://github.com/{REPO}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"
ICON = {"queued": "⏳ queued", "rendering": "🎬 rendering", "done": "✅ done", "failed": "❌ failed"}


def sh(*a, cwd=None, check=True):
    return subprocess.run(a, cwd=cwd, check=check, capture_output=True, text=True)


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def render_md(rows):
    jobs = {j["dir"]: j for j in json.load(open(Path(os.environ.get("GITHUB_WORKSPACE", ".")) / "exams.json", encoding="utf-8"))} \
        if (Path(os.environ.get("GITHUB_WORKSPACE", ".")) / "exams.json").exists() else {}
    done = sum(1 for r in rows.values() if r["state"] == "done")
    lines = [f"# Render progress\n\n**{done} / {len(rows)} done** · updated {now()} · "
             f"[videos](https://github.com/{REPO}/releases/tag/videos) · [runs](https://github.com/{REPO}/actions)\n",
             "| # | Exam | State | Progress | Started | Finished | Size | Run |", "|---|---|---|---|---|---|---|---|"]
    for d, r in sorted(rows.items()):
        j = jobs.get(d, {})
        size = f"{int(r['bytes']) / 2**20:.0f} MB" if r.get("bytes") else ""
        pct = f"{r.get('pct', 0):.0f}%" if r["state"] == "rendering" else ("100%" if r["state"] == "done" else "")
        name = f"{j.get('company', '')} · {j.get('post', '')} · {j.get('date', '')}" if j else d
        lines.append(f"| {d[:2]} | {name} | {ICON.get(r['state'], r['state'])} | {pct} | {r.get('started', '')} | "
                     f"{r.get('finished', '')} | {size} | [log]({r.get('run', RUN)}) |")
    return "\n".join(lines) + "\n"


def update(fn):
    url = f"https://x-access-token:{os.environ['GH_TOKEN']}@github.com/{REPO}.git"
    for attempt in range(25):
        with tempfile.TemporaryDirectory() as t:
            r = sh("git", "clone", "-q", "--depth", "1", "--branch", "status", url, t, check=False)
            if r.returncode != 0:  # first time: make an empty orphan branch
                sh("git", "init", "-q", t)
                sh("git", "checkout", "-q", "--orphan", "status", cwd=t)
                sh("git", "remote", "add", "origin", url, cwd=t)
            sh("git", "config", "user.name", "render-bot", cwd=t)
            sh("git", "config", "user.email", "render-bot@users.noreply.github.com", cwd=t)
            p = Path(t) / "status.json"
            rows = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
            fn(rows)
            p.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
            (Path(t) / "STATUS.md").write_text(render_md(rows), encoding="utf-8")
            sh("git", "add", "-A", cwd=t)
            if sh("git", "diff", "--cached", "--quiet", cwd=t, check=False).returncode == 0:
                return
            sh("git", "commit", "-q", "-m", "status", cwd=t)
            if sh("git", "push", "-q", "origin", "status", cwd=t, check=False).returncode == 0:
                return
        time.sleep(2 + attempt)
    print("could not update the dashboard (it does not stop the render)")


def main():
    cmd = sys.argv[1]
    if cmd == "queue":
        m = json.loads(os.environ.get("MATRIX", "[]"))
        update(lambda rows: rows.update({j["dir"]: {"state": "queued", "run": RUN} for j in m}))
    elif cmd == "set":
        d, state = sys.argv[2], sys.argv[3]

        def f(rows):
            r = rows.setdefault(d, {})
            r.update(state=state, run=RUN)
            if state == "rendering":
                r.update(started=now(), finished="", pct=0)
            if state in ("done", "failed"):
                r["finished"] = now()
            if len(sys.argv) > 4:
                r["bytes"] = sys.argv[4]
        update(f)
    elif cmd == "pct":
        d, pct = sys.argv[2], float(sys.argv[3])
        update(lambda rows: rows.setdefault(d, {"state": "rendering"}).update(pct=pct))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # the dashboard must never fail a render
        print("dashboard update skipped:", e)
