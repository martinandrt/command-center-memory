# How the demo GIF was made

`docs/demo.gif` is a shortened replay of a real run, not a mock-up.

1. A fresh copy of this repo, one initial commit, then real Claude Code sessions in it (`claude -p`, one prompt each):
   - session 1 ("Day 1" in the GIF): `/alive`, a small task, a correction plus a promise, `/end-session`;
   - session 2 ("Day 2"): a brand-new session a few minutes later, `/alive`. Both ran on 2026-11-25; "Day" stands for a new working session.
2. The full answers are in `demo-transcript/`, one file per prompt.
3. `render-demo-gif.py` draws the terminal frames and builds the GIF with ffmpeg. The prompts are verbatim; Claude's answers are quoted from `demo-transcript/`, shortened, nothing reworded; the boot lines are `scripts/boot.sh` output from the same run. macOS only as written (Menlo font, Pillow, ffmpeg):

   ```bash
   python3 dev/render-demo-gif.py docs/demo.gif /tmp/demo-frames
   ```
