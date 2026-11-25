#!/usr/bin/env python3
"""Commitments from memory/commitments.md.

    python3 scripts/due-commitments.py              # boot: overdue / today (DUE), within 3 days (SOON), no date
    python3 scripts/due-commitments.py --summary    # the same, with a "SUMMARY: ..." line on top
    python3 scripts/due-commitments.py --all-open   # closing: all open ones
    python3 scripts/due-commitments.py --today 2026-12-01   # simulate the date (test)

No output = nothing is burning.

Reads ONLY the table in the section "## Current commitments" (ends at the next "## " heading).
Columns: To whom | What | Deadline | Status | Session | Notes. Only the statuses open and in-progress count.
A commitment without a date would never remind anyone by itself, so the script reports it separately as NO DATE.

Standard library only, Python 3.8+.
"""
import datetime
import re
import sys
from pathlib import Path

PATH = Path(__file__).resolve().parent.parent / "memory" / "commitments.md"
SECTION = "## Current commitments"
HEADER_CELL = "to whom"  # first cell of the table header row, skipped by the parser


def split_cells(line):
    """Split a table row on unescaped pipes only; "\\|" stays inside the cell as "|"."""
    cells = [c.replace("\\|", "|").strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
    return cells


def rows(text):
    out, active = [], False
    for ln in text.splitlines():
        if ln.startswith(SECTION):
            active = True
            continue
        if active and ln.startswith("## "):
            break
        if active and ln.startswith("|"):
            cells = split_cells(ln)
            if cells[0].lower() == HEADER_CELL or set(cells[0]) <= set("-: "):
                continue
            if len(cells) != 6:  # wrong column count: warn instead of silently dropping or shifting
                print("WARNING: table row has %d columns (expected 6)%s: %s"
                      % (len(cells), ", skipped" if len(cells) < 4 else "", ln.strip()[:80]))
                if len(cells) < 4:
                    continue
            out.append(cells)
    return out


def title(what, n=60):
    m = re.match(r"\s*\*\*(.+?)\*\*", what)
    t = (m.group(1) if m else what).strip().rstrip(":.")
    return t if len(t) <= n else t[:n - 1].rstrip() + "..."


def row_date(r, today):
    """(days until the deadline, or None without a date). ValueError for an impossible date such as 2026-02-30."""
    m = re.search(r"\d{4}-\d{2}-\d{2}", r[2])
    if not m:
        return None
    return (datetime.date.fromisoformat(m.group(0)) - today).days


def days(n):
    return "%d %s" % (n, "day" if n == 1 else "days")


def main():
    argv = sys.argv[1:]
    if {"-h", "--help"} & set(argv):
        print(__doc__)
        return 0
    today = datetime.date.today()
    if "--today" in argv:
        today = datetime.date.fromisoformat(argv[argv.index("--today") + 1])
    if not PATH.exists():
        return 0
    open_rows = [r for r in rows(PATH.read_text(encoding="utf-8")) if r[3].lower() in ("open", "in-progress")]

    if "--all-open" in argv:
        if not open_rows:
            print("No open commitments.")
        else:
            print("OPEN COMMITMENTS: %d. Decide for each: done / dropped / new deadline / stays open (and why).\n" % len(open_rows))
        for r in open_rows:
            try:
                d = row_date(r, today)
            except ValueError:
                print("invalid date in row: %s [%s]\n" % (title(r[1], 60), r[2]))
                continue
            if d is not None:
                when = "%s overdue" % days(-d) if d < 0 else "TODAY" if d == 0 else "in %s" % days(d)
            else:
                when = "no date"
            print("[%s] (%s) %s\n    to whom: %s, deadline: %s\n" % (r[3], when, title(r[1], 200), r[0], r[2]))
        return 0

    due, soon, undated, invalid = [], [], [], []
    for r in open_rows:
        try:
            d = row_date(r, today)
        except ValueError:
            invalid.append(r)
            continue
        if d is None:
            undated.append(r)
            continue
        if d <= 0:
            due.append((d, r))
        elif d <= 3:
            soon.append((d, r))
    if not (due or soon or undated or invalid):
        return 0

    if "--summary" in argv:
        due_today = [r for d, r in due if d == 0]
        overdue = [d for d, r in due if d < 0]
        parts = []
        if invalid:
            parts.append("invalid date %d" % len(invalid))
        if due_today:
            parts.append("today %d (%s)" % (len(due_today), "; ".join(title(r[1], 40) for r in due_today[:3])))
        if overdue:
            parts.append("overdue %d, oldest %s" % (len(overdue), days(-min(overdue))))
        if soon:
            parts.append("within 3 days %d" % len(soon))
        if undated:
            parts.append("no date %d" % len(undated))
        print("SUMMARY: " + " | ".join(parts))
    for d, r in sorted(due, key=lambda x: x[0]):
        print("DUE (%s): %s, to whom: %s [%s]" % ("%s overdue" % days(-d) if d < 0 else "TODAY", title(r[1]), r[0], r[2]))
    for d, r in sorted(soon, key=lambda x: x[0]):
        print("SOON (in %s): %s, to whom: %s [%s]" % (days(d), title(r[1]), r[0], r[2]))
    for r in invalid:
        print("invalid date in row: %s, to whom: %s [%s]" % (title(r[1]), r[0], r[2]))
    for r in undated:
        print("NO DATE (open, nobody will remind): %s, to whom: %s" % (title(r[1]), r[0]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
