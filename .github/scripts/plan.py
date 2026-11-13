"""Pick the exams to render → writes `matrix` and `count` to $GITHUB_OUTPUT.
usage: plan.py "all" | "1,2,5" | "1-10"   [skip_done true|false]"""
import json
import os
import subprocess
import sys

sel, skip = sys.argv[1].strip().lower(), (sys.argv[2] if len(sys.argv) > 2 else "true") == "true"
jobs = json.load(open("exams.json", encoding="utf-8"))
if sel not in ("", "all"):
    want = set()
    for part in sel.replace(" ", "").split(","):
        if "-" in part:
            a, b = part.split("-")
            want |= set(range(int(a), int(b) + 1))
        elif part:
            want.add(int(part))
    jobs = [j for j in jobs if j["n"] in want]
if skip:
    out = subprocess.run(["gh", "release", "view", "videos", "--json", "assets", "-q", ".assets[].name"],
                         capture_output=True, text=True)
    have = set(out.stdout.split())
    jobs = [j for j in jobs if j["asset"] not in have]
matrix = [{"dir": j["dir"], "asset": j["asset"], "n": j["n"]} for j in jobs]
with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
    f.write(f"matrix={json.dumps(matrix)}\ncount={len(matrix)}\n")
print(f"{len(matrix)} exams to render:", ", ".join(j["dir"] for j in matrix))
