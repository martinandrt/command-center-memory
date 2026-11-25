#!/usr/bin/env python3
"""Session number and name, who is running alongside, topic, closing.

    python3 scripts/session-claim.py                   # claims a number (or returns mine); 1st line: "N  Name"
    python3 scripts/session-claim.py --topic "what I work on"   # overwrites the topic of my session
    python3 scripts/session-claim.py --show            # who is running
    python3 scripts/session-claim.py --close N         # closes the record (done by /end-session)

Why this exists: two Claude Code windows open side by side would otherwise read the same last
number from LINEAGE and both would declare themselves the next one. So the number is claimed right at boot,
in the registry `memory/sessions-running.jsonl`, under a file lock (a second start in the same second
gets a different number). The registry is not committed.

My session is recognised by CLAUDE_CODE_SESSION_ID. Without it (older versions) pass `--id N`;
a bare call without an ID would claim a new number.

Standard library only, Python 3.8+. The lock uses fcntl (macOS, Linux, WSL).
"""
import argparse
import datetime
import json
import os
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MEM = ROOT / "memory"
REG = MEM / "sessions-running.jsonl"
LOCK = MEM / ".sessions.lock"
LINEAGE = MEM / "LINEAGE.md"
ARCHIVE = MEM / "archive" / "sessions"
TIMEOUT_H = 18  # an unclosed session older than this does not count as running (safety net for crashed ones)

WORDS = """Kestrel Osprey Falcon Lynx Otter Badger Beaver Eagle Harrier Heron Stork Cormorant
Owl Stag Roebuck Fox Marten Ermine Trout Perch Pike Grayling Hobby Raven Magpie
Skylark Wagtail Woodpecker Oriole Nuthatch Lapwing Gull Egret Kingfisher Carpenter Smith Potter
Cooper Farmer Miller Wheelwright Joiner Glazier Goldsmith Baker Fisher Beekeeper Fell Boatman
Anchor Beacon Harbor Compass Spring Ford Valley Island Cape Ridge Pass Boundary
Meadow Grove Cliff Brook Heather Juniper Elm Hornbeam Maple Alder Birch Pine Spruce""".split()


class Lock(object):
    """Exclusive lock via fcntl; without fcntl (Windows) it runs without a lock and warns."""

    def __enter__(self):
        MEM.mkdir(parents=True, exist_ok=True)
        self.f = open(str(LOCK), "a+")
        try:
            import fcntl
            fcntl.flock(self.f, fcntl.LOCK_EX)
            self.fcntl = fcntl
        except ImportError:
            self.fcntl = None
            print("(warning: fcntl is missing, concurrent windows are not guarded)", file=sys.stderr)
        return self

    def __exit__(self, *a):
        if self.fcntl:
            self.fcntl.flock(self.f, self.fcntl.LOCK_UN)
        self.f.close()


def load():
    out = []
    if REG.exists():
        for ln in REG.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(ln)
                if isinstance(r, dict) and "id" in r:
                    out.append(r)
            except ValueError:
                continue
    return out


def save(recs):
    recs = recs[-200:]
    tmp = REG.with_suffix(".tmp")
    tmp.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in recs), encoding="utf-8")
    os.replace(str(tmp), str(REG))


def now():
    return datetime.datetime.now().replace(microsecond=0)


def alive(r, current):
    """Running = not closed and younger than TIMEOUT_H."""
    if r.get("end"):
        return False
    try:
        start = datetime.datetime.fromisoformat(r["start"])
    except (KeyError, ValueError):
        return False
    return (current - start) < datetime.timedelta(hours=TIMEOUT_H)


def known():
    """(numbers, names) from LINEAGE, the archive and the registry."""
    numbers, names = set(), set()
    if LINEAGE.exists():
        for m in re.finditer(r"^## SESSION (\d+) — (.+?)\s*$", LINEAGE.read_text(encoding="utf-8"), re.M):
            numbers.add(int(m.group(1)))
            names.add(m.group(2).strip().lower())
    if ARCHIVE.exists():
        for p in ARCHIVE.glob("*.md"):
            m = re.match(r"(\d+)-(.+)\.md$", p.name)
            if m:
                numbers.add(int(m.group(1)))
                names.add(m.group(2).lower())
    for r in load():
        numbers.add(int(r["id"]))
        names.add(str(r.get("name", "")).lower())
    return numbers, names


def slug(s):
    import unicodedata
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def new_name(used, number):
    taken = set(used) | set(slug(x) for x in used)
    free = [w for w in WORDS if w.lower() not in taken and slug(w) not in taken]
    if free:
        return random.choice(free)
    return "%s-%d" % (random.choice(WORDS), number)  # the supply ran out, a name with a number is still unique


def neighbours(recs, my_id, current):
    out = []
    for r in recs:
        if r["id"] != my_id and alive(r, current):
            since = r.get("start", "")[11:16]
            topic = r.get("topic") or "topic not set"
            out.append("%s %s (since %s, %s)" % (r["id"], r.get("name", ""), since, topic))
    return out


def find_mine(recs, sid, ident):
    if ident is not None:
        for r in recs:
            if r["id"] == ident:
                return r
        return None
    if sid:
        for r in reversed(recs):
            if r.get("sid") == sid:
                return r
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--topic")
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--close", type=int, metavar="N")
    ap.add_argument("--id", type=int, help="my number, when CLAUDE_CODE_SESSION_ID is not set")
    ap.add_argument("--name", help="a custom name instead of a random one")
    ap.add_argument("--sid", default=os.environ.get("CLAUDE_CODE_SESSION_ID"), help="session ID (otherwise from the environment)")
    a = ap.parse_args()
    current = now()

    if a.show:
        with Lock():
            recs = load()
        running = [r for r in recs if alive(r, current)]
        if not running:
            print("Nobody is running.")
        for r in running:
            print("%s %s (since %s) %s" % (r["id"], r.get("name", ""), r.get("start", "")[11:16], r.get("topic") or "(topic not set)"))
        return 0

    if a.close is not None:
        with Lock():
            recs = load()
            for r in recs:
                if r["id"] == a.close:
                    r["end"] = current.isoformat()
                    save(recs)
                    print("Session %s closed." % a.close)
                    return 0
        print("Session %s is not in the registry." % a.close, file=sys.stderr)
        return 1

    if a.topic is not None:
        with Lock():
            recs = load()
            r = find_mine(recs, a.sid, a.id)
            if not r:
                print("My session not found (pass --id N).", file=sys.stderr)
                return 1
            r["topic"] = a.topic.strip()
            save(recs)
            print("Topic of session %s: %s" % (r["id"], r["topic"]))
        return 0

    # claim a number, or return mine
    with Lock():
        recs = load()
        r = find_mine(recs, a.sid, a.id)
        if r is None:
            numbers, names = known()
            number = (max(numbers) if numbers else 0) + 1
            r = {"id": number, "name": a.name or new_name(names, number), "sid": a.sid or "",
                 "start": current.isoformat(), "topic": "", "end": None}
            recs.append(r)
            save(recs)
        others = neighbours(recs, r["id"], current)
    print("%s  %s" % (r["id"], r["name"]))
    if others:
        print("(running alongside: %s)" % "; ".join(others))
    else:
        print("(nobody else is running)")
    if not a.sid and a.id is None:
        print("(warning: CLAUDE_CODE_SESSION_ID is missing; remember your number and keep using --id %s)" % r["id"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
