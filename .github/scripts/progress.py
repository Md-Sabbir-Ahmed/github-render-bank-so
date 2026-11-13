"""Reads the renderer's output (piped in), prints it, and posts % to the dashboard about every 5 minutes."""
import re
import subprocess
import sys
import time

d = sys.argv[1]
last = 0.0
for line in sys.stdin:
    sys.stdout.write(line)
    sys.stdout.flush()
    m = re.search(r"(?:Streaming|Capturing) frame (\d+)/(\d+)", line)
    if m and time.time() - last > 300:
        last = time.time()
        pct = int(m.group(1)) * 100 / int(m.group(2))
        subprocess.run([sys.executable, ".github/scripts/status.py", "pct", d, f"{pct:.1f}"], cwd="../..", check=False)
