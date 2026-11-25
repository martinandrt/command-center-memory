"""Render a terminal-style GIF from a real (shortened) Claude Code session transcript."""
import os
import subprocess
import sys
import textwrap
from PIL import Image, ImageDraw, ImageFont

OUT_GIF = sys.argv[1]
WORK = sys.argv[2]
os.makedirs(WORK, exist_ok=True)

S = 2  # render scale (retina-crisp text), downscaled at the end by ffmpeg
W, H = 900 * S, 560 * S
PAD = 22 * S
CHROME = 34 * S
FONT = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 14 * S)
FONT_B = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 14 * S, index=1)
LH = int(20 * S)
CW = FONT.getlength("M")
COLS = int((W - 2 * PAD) // CW)
ROWS = int((H - CHROME - 2 * PAD) // LH)

BG = (24, 26, 31)
CHROME_BG = (36, 39, 46)
FG = (215, 218, 224)
DIM = (125, 133, 148)
HEAD = (102, 178, 196)
USER = (236, 238, 242)
PROMPT = (126, 200, 130)
CLAUDE = (217, 119, 87)
PILL_BG = (217, 119, 87)
PILL_FG = (24, 26, 31)

frames = []  # (image, duration_ms)
buf = []     # list of (segments) where segment = (text, color, bold)
caption = ""


def wrap(text, indent, first_prefix=""):
    width = COLS - indent
    lines = textwrap.wrap(text, width=width) or [""]
    return lines


def render(cursor_line=None):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, CHROME], fill=CHROME_BG)
    for i, c in enumerate([(237, 106, 94), (245, 191, 79), (98, 197, 84)]):
        cx = PAD + i * 20 * S
        d.ellipse([cx, CHROME / 2 - 6 * S, cx + 12 * S, CHROME / 2 + 6 * S], fill=c)
    title = "command-center-memory"
    tw = FONT.getlength(title)
    d.text(((W - tw) / 2, CHROME / 2 - 9 * S), title, font=FONT, fill=DIM)
    if caption:
        cw = FONT_B.getlength(caption) + 24 * S
        x1 = W - PAD - cw
        d.rounded_rectangle([x1, 7 * S, W - PAD, CHROME - 7 * S], radius=10 * S, fill=PILL_BG)
        d.text((x1 + 12 * S, CHROME / 2 - 9 * S), caption, font=FONT_B, fill=PILL_FG)
    view = buf[-ROWS:]
    y = CHROME + PAD
    for segs in view:
        x = PAD
        for text, color, bold in segs:
            f = FONT_B if bold else FONT
            d.text((x, y), text, font=f, fill=color)
            x += f.getlength(text)
        y += LH
    if cursor_line is not None:
        segs = view[-1] if view else []
        x = PAD + sum((FONT_B if b else FONT).getlength(t) for t, _, b in segs)
        yy = CHROME + PAD + (len(view) - 1) * LH
        d.rectangle([x + 1 * S, yy + 2 * S, x + CW - 1 * S, yy + LH - 3 * S], fill=FG)
    return img


def frame(ms, cursor=False):
    frames.append((render(0 if cursor else None), ms))


def blank(ms=0):
    buf.append([("", FG, False)])
    if ms:
        frame(ms)


def type_cmd(prompt, prompt_color, text, color=USER, per=2, ms=40):
    buf.append([(prompt, prompt_color, True)])
    frame(350, cursor=True)
    lines = wrap(text, len(prompt))
    for li, line in enumerate(lines):
        if li > 0:
            buf.append([(" " * len(prompt), FG, False)])
        base = list(buf[-1])
        for i in range(0, len(line) + 1, per):
            buf[-1] = base + [(line[:i], color, False)]
            frame(ms, cursor=True)
        buf[-1] = base + [(line, color, False)]
    frame(450)


def out(text, color=FG, ms=55, indent=2, bold=False):
    for line in wrap(text, indent):
        buf.append([(" " * indent + line, color, bold)])
        frame(ms)


def claude(paragraphs, ms=110, hold=1600):
    first = True
    for p in paragraphs:
        color = FG
        if isinstance(p, tuple):
            p, color = p
        lines = wrap(p, 2)
        for i, line in enumerate(lines):
            if first:
                buf.append([("● ", CLAUDE, True), (line, color, False)])
                first = False
            else:
                buf.append([("  " + line, color, False)])
            frame(ms)
    frame(hold)


def clear():
    del buf[:]


# ---------------- Day 1 ----------------
caption = "Day 1"
frame(600)
type_cmd("$ ", PROMPT, "claude", per=1, ms=70)
blank()
type_cmd("> ", CLAUDE, "/alive", per=1, ms=70)
out("===== Your session =====", HEAD)
out("1  Potter", FG, bold=True)
out("(nobody else is running)", DIM)
out("===== Memory status =====", HEAD)
out("BRAIN.md: unfilled placeholders: 6", DIM)
out("-> First session: there is no handoff from before, that is fine.", DIM)
blank(200)
claude([
    "Session 1, Potter. First session: no previous handoff to continue from.",
    "BRAIN.md still has 6 unfilled placeholders. I can fill them in from a short interview (5 questions), or we can leave it for later. What are we working on?",
], hold=1800)
blank()
type_cmd("> ", CLAUDE, "Skip the interview, just note my name: I'm Sam, a freelance designer. Draft a 3-sentence reminder to my client Acme about the unpaid invoice of 1,200 EUR.")
blank()
claude([
    "The draft is below, not sent. Your name and role are in memory/BRAIN.md.",
    ("  ... If the payment has already gone out, please disregard this message.", DIM),
    ("  Best regards,", DIM),
    ("  Sam", DIM),
], hold=1400)
blank()
type_cmd("> ", CLAUDE, "No. Never sign as 'Best regards'. Always sign just 'Sam'. Also: I promised Acme the final logo files by Friday 27 November.")
blank()
claude([
    "Both are saved: the signature rule is in memory/feedback/sign-just-sam.md, and the logo files for Acme are in memory/commitments.md with the deadline 2026-11-27.",
], hold=1800)
blank()
type_cmd("> ", CLAUDE, "/end-session", per=1, ms=70)
blank()
claude([
    "Session 1 — Potter is closed. Everything is committed locally; nothing was pushed.",
    "Commitment still open: final logo files to Acme by 2026-11-27. The next session start will flag it.",
], hold=2400)

# ---------------- Day 2 ----------------
clear()
caption = "Day 2 · new session"
frame(900)
type_cmd("$ ", PROMPT, "claude", per=1, ms=70)
blank()
type_cmd("> ", CLAUDE, "/alive", per=1, ms=70)
out("===== Your session =====", HEAD)
out("2  Egret", FG, bold=True)
out("===== Activity (last 10) =====", HEAD)
out("2026-11-25 16:56  Session 1 — Potter: name into BRAIN, payment reminder draft for Acme, signature rule, commitment logo files to Acme", DIM)
out("===== Commitments =====", HEAD)
out("SUMMARY: within 3 days 1", FG)
out("SOON (in 2 days): Deliver the final logo files, to whom: Acme (client) [2026-11-27]", FG)
blank(250)
claude([
    "Session 2, Egret, picking up after Potter.",
    "Commitments: the final logo files for Acme are due 2026-11-27.",
    "Open from last time: the Acme payment reminder (1,200 EUR) exists only in session 1's chat. I don't know whether you sent it.",
    "What are we working on?",
], ms=140, hold=5000)

# ---------------- write ----------------
lst = os.path.join(WORK, "list.txt")
with open(lst, "w") as f:
    for i, (img, ms) in enumerate(frames):
        p = os.path.join(WORK, "f%04d.png" % i)
        img.save(p)
        f.write("file '%s'\nduration %.3f\n" % (p, ms / 1000.0))
    f.write("file '%s'\n" % os.path.join(WORK, "f%04d.png" % (len(frames) - 1)))
pal = os.path.join(WORK, "pal.png")
vf = "scale=%d:-1:flags=lanczos" % (W // S)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                "-vf", vf + ",palettegen=max_colors=64:stats_mode=full", pal], check=True)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", pal,
                "-lavfi", vf + "[x];[x][1:v]paletteuse=dither=none", "-r", "25", OUT_GIF], check=True)
print("frames", len(frames), "duration %.1fs" % (sum(ms for _, ms in frames) / 1000.0), "size %.0f kB" % (os.path.getsize(OUT_GIF) / 1024))
