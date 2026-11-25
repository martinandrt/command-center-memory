#!/usr/bin/env python3
"""Append one line to memory/activity.log (boot shows the last 10).

    python3 scripts/activity-append.py "Session 3 — Kestrel: what was done"

The log keeps at most 200 lines; on overflow the last 150 remain.
Standard library only, Python 3.8+.
"""
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _fileutil import Lock, atomic_write  # noqa: E402

LOG = Path(__file__).resolve().parent.parent / "memory" / "activity.log"
LOCK = LOG.parent / ".activity.lock"


def main():
    text = " ".join(sys.argv[1:]).strip().replace("\n", " ")
    if not text or text in ("-h", "--help"):
        print(__doc__)
        return 0 if text else 1
    with Lock(LOCK):  # read-modify-write under one lock: two windows cannot drop each other's line
        lines = LOG.read_text(encoding="utf-8").splitlines() if LOG.exists() else []
        lines.append("%s  %s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), text))
        if len(lines) > 200:
            lines = lines[-150:]
        atomic_write(LOG, "\n".join(lines) + "\n")
    print("activity.log: +1 line (%d total)" % len(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
