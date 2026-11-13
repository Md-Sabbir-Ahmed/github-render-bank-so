# Combined Bank Senior Officer 2026 question-solution video: cloud render

This repo renders the Combined Bank Senior Officer (13 Nov 2026) solution video on GitHub's computers, up to 20 at a time. Your PC can be off.
Each folder in `exams/` is one finished HyperFrames video project (scenes, voice, fonts). Videos longer than 30 minutes are
split into parts of about 27 minutes (`…-part1`, `…-part2`, …); the PC joins them after download.
Folder numbers = BCS numbers.

## Render
1. Open the **Actions** tab, choose **Render videos**, then **Run workflow**.
2. Fill in the three inputs:
   - **exams:** `all` (or BCS numbers like `45,46` or `35-40`; all parts of a BCS are taken together).
   - **bitrate:** `3M`, the default.
   - **skip_done:** leave it ticked. Parts that already have an MP4 are skipped, so re-running only redoes the failed ones.
3. Close the page if you like. Each part takes about 1–3 hours, and up to 20 run in parallel.

## Watch progress
- **Dashboard:** switch to the **`status`** branch and open **STATUS.md** (queued, rendering with %, done or failed, times, size, log link).
- **Live logs:** **Actions** tab → the run → any job.

## Get the videos
**Releases → Rendered videos**: one MP4 per job, named `<job folder>.mp4`.
Download the parts of one BCS into a folder, then in the video workspace:
`python -I -X utf8 bcs/_pipeline/join_parts.py <paper-folder> <part1.mp4> <part2.mp4> …`
That decode-checks every part, joins them without re-encoding into `bcs/videos/<Bangla name>.mp4`, decode-checks the result,
rewrites the chapters with the real part lengths and writes the YouTube files.

## Notes
- **Time limit:** each job may run 6 hours; parts of ≈ 27 minutes are well under that.
- **Failed renders:** the render log is attached to the run; re-run with skip_done ticked.
- **More papers:** `python -I -X utf8 bcs/_pipeline/make_github.py <paper> …` in the video workspace, then push.
