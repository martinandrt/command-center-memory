#!/bin/bash
# Test of the whole cycle in a temporary copy: boot -> handoff -> end of session -> second boot.
# Changes nothing in your folder. Usage: bash scripts/selftest.sh
# Output: PASS/FAIL lines and a summary at the end; exit 0 only if everything passed.
# The copy holds only skeleton files (never .env*); on success it goes to the Trash, on failure it stays for inspection.

# never inherit a repo location from the caller: the test must only ever touch its own temp repo
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_OBJECT_DIRECTORY
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
set -euo pipefail   # strict during setup; relaxed before the checks (grep -q in pipes would trip pipefail)

# Copy only what the test needs to the destination $1, never secrets or runtime files.
# Tracked files (git ls-files) when SRC is a git repo with commits, otherwise an explicit set of skeleton paths.
copy_skeleton() {
  local dest="$1" list f
  [ -n "$dest" ] && [ -d "$dest" ] || { echo "selftest: bad destination" >&2; return 1; }
  list="$(mktemp "${TMPDIR:-/tmp}/cc-selftest-list.XXXXXX")" || return 1
  if ( cd "$SRC" && git rev-parse -q --verify HEAD >/dev/null 2>&1 ) \
     && ( cd "$SRC" && git ls-files -z -- . > "$list" 2>/dev/null ) && [ -s "$list" ]; then
    :
  else
    ( cd "$SRC" && find CLAUDE.md LICENSE .gitignore .claude/commands memory scripts -type f -print0 2>/dev/null ) > "$list" || true
  fi
  while IFS= read -r -d '' f; do
    case "$f" in
      .env|.env.*|*/.env|*/.env.*|*.pem|*.key|*__pycache__*|*.pyc|*.tmp|*.lock) continue ;;
      memory/.staging/*|memory/.index/*|memory/sessions-running.jsonl|memory/activity.log) continue ;;
      memory/archive/sessions/[0-9]*.md) continue ;;
    esac
    [ -f "$SRC/$f" ] || continue
    mkdir -p "$dest/$(dirname "$f")"
    cp -p "$SRC/$f" "$dest/$f"
  done < "$list"
  rm -f "$list"
  [ -f "$dest/scripts/boot.sh" ] && [ -f "$dest/memory/BRAIN.md" ] || { echo "selftest: the copy is incomplete" >&2; return 1; }
}

T="$(mktemp -d "${TMPDIR:-/tmp}/cc-selftest.XXXXXX")" || { echo "selftest: mktemp failed" >&2; exit 1; }
[ -n "$T" ] && [ -d "$T" ] || { echo "selftest: no temporary directory" >&2; exit 1; }
echo "Temporary copy: $T"
copy_skeleton "$T"
cd "$T" || exit 1
[ "$(pwd -P)" != "$(cd "$SRC" && pwd -P)" ] || { echo "selftest: refusing to run inside the source repo" >&2; exit 1; }
# Known state for the first-run test: BRAIN must hold a placeholder (a filled-in repo has none)
grep -q "\[FILL IN" memory/BRAIN.md || printf '\n- [FILL IN: selftest placeholder]\n' >> memory/BRAIN.md
# LINEAGE without any real entries (only the intro up to the first "## SESSION <number>")
python3 - <<'PY'
import re, pathlib
p = pathlib.Path("memory/LINEAGE.md")
t = p.read_text(encoding="utf-8")
m = re.search(r"^## SESSION \d+ — ", t, re.M)
if m:
    p.write_text(t[:m.start()].rstrip() + "\n", encoding="utf-8")
PY
git init -q . 2>/dev/null || true
git config user.email selftest@example.invalid
git config user.name selftest
git add -A >/dev/null 2>&1 && git commit -qm "selftest: initial state" >/dev/null 2>&1 || true
set +e +o pipefail

FAIL=0
ok()  { echo "PASS: $1"; }
bad() { echo "FAIL: $1"; FAIL=$((FAIL+1)); }
chk() { if eval "$2"; then ok "$1"; else bad "$1"; fi; }
write_session() {  # $1 number, $2 name: an entry into LINEAGE via rollover
  mkdir -p "memory/.staging/$1"
  cat > "memory/.staging/$1/LINEAGE-entry.md" <<REC
## SESSION $1 — $2

**Date:** $(date +%Y-%m-%d)

### What was done
- Trial session $1.

### Handoff
- Nothing open.
REC
  python3 scripts/lineage-rollover.py --add "memory/.staging/$1/LINEAGE-entry.md"
}

echo; echo "--- 1. boot (session 1)"
export CLAUDE_CODE_SESSION_ID="selftest-a"
OUT1=$(bash scripts/boot.sh 2>&1); echo "$OUT1" | sed -n '1,14p'
chk "boot claimed number 1" 'echo "$OUT1" | grep -qE "^1  [^ ]"'
chk "boot created the handoff" '[ -f memory/.staging/1/HANDOFF.md ]'
chk "boot reports required reading BRAIN and LINEAGE" 'echo "$OUT1" | grep -q "BRAIN.md" && echo "$OUT1" | grep -q "LINEAGE.md"'
chk "boot reports an unfilled BRAIN" 'echo "$OUT1" | grep -q "unfilled placeholders: [1-9]"'
chk "repeated boot of the same session gives no new number" 'bash scripts/boot.sh 2>&1 | grep -qE "^1  [^ ]"'

echo; echo "--- 2. simulated work and /end-session"
python3 scripts/session-claim.py --topic "trial topic" >/dev/null
echo "- Trial decision" >> memory/.staging/1/HANDOFF.md
NAME=$(python3 scripts/session-claim.py | awk 'NR==1{print $2}')
write_session 1 "$NAME"
chk "LINEAGE contains session 1" 'grep -q "^## SESSION 1 — " memory/LINEAGE.md'
chk "archive contains session 1" 'ls memory/archive/sessions/001-*.md >/dev/null 2>&1'
python3 scripts/activity-append.py "Session 1 — $NAME: selftest" >/dev/null
python3 scripts/memory-index.py
chk "index contains the sample lesson" 'grep -q "verify-before-done" memory/MEMORY.md'
python3 scripts/session-claim.py --close 1
chk "session 1 closed in the registry" 'python3 scripts/session-claim.py --show | grep -q "Nobody is running"'

echo; echo "--- 3. commitment due today"
TODAY=$(date +%Y-%m-%d)
python3 - "$TODAY" <<'PY'
import sys, pathlib
p = pathlib.Path("memory/commitments.md")
t = p.read_text(encoding="utf-8")
row = "| Test Person | **Trial commitment for today** | %s | open | 1 | selftest |\n" % sys.argv[1]
i = t.index("\n## Archive")
p.write_text(t[:i].rstrip("\n") + "\n" + row + t[i:], encoding="utf-8")
PY

echo; echo "--- 4. second boot (session 2)"
export CLAUDE_CODE_SESSION_ID="selftest-b"
OUT2=$(bash scripts/boot.sh 2>&1); echo "$OUT2" | sed -n '1,22p'
chk "second boot has number 2" 'echo "$OUT2" | grep -qE "^2  [^ ]"'
chk "second boot shows 1 session from before in LINEAGE" 'echo "$OUT2" | grep -q "sessions in body: 1"'
chk "second boot sees the entry in the activity log" 'echo "$OUT2" | grep -q "Session 1 — $NAME: selftest"'
chk "boot reports the commitment due today" 'echo "$OUT2" | grep -q "DUE (TODAY): Trial commitment for today"'
chk "boot reports SUMMARY" 'echo "$OUT2" | grep -q "^SUMMARY: today 1"'
chk "LINEAGE for reading contains the handoff of session 1" 'grep -q "^## SESSION 1 — " memory/LINEAGE.md'

echo; echo "--- 5. two windows at once (two starts in parallel)"
( CLAUDE_CODE_SESSION_ID=par-1 python3 scripts/session-claim.py > par1.txt ) &
( CLAUDE_CODE_SESSION_ID=par-2 python3 scripts/session-claim.py > par2.txt ) &
wait
A=$(awk 'NR==1{print $1}' par1.txt); B=$(awk 'NR==1{print $1}' par2.txt)
chk "the two windows got different numbers ($A and $B)" '[ -n "$A" ] && [ -n "$B" ] && [ "$A" != "$B" ]'

echo; echo "--- 6. rollover: only the 3 newest in LINEAGE"
for n in 3 4 5; do write_session $n "Trial$n" >/dev/null; done
chk "3 sessions remained in LINEAGE" '[ "$(grep -c "^## SESSION [0-9]" memory/LINEAGE.md)" = "3" ]'
chk "all 4 sessions are in the archive" '[ "$(ls memory/archive/sessions/0*.md | wc -l | tr -d " ")" = "4" ]'
chk "archive INDEX has 4 rows" '[ "$(grep -c "^| \[" memory/archive/sessions/INDEX.md)" = "4" ]'
python3 scripts/lineage-rollover.py | grep -q "INDEX unchanged" && ok "rollover is idempotent" || bad "rollover is idempotent"

echo; echo "--- 7. parallel writers lose nothing (activity log, rollover)"
for i in 1 2 3 4 5 6 7 8 9 10 11 12; do python3 scripts/activity-append.py "parallel-line-$i" >/dev/null 2>&1 & done
wait
chk "12 parallel activity lines are all there" '[ "$(grep -c "parallel-line-" memory/activity.log)" = "12" ]'
for n in 6 7 8; do write_session $n "Par$n" >/dev/null 2>&1 & done
wait
chk "3 parallel rollovers: all in the archive" '[ "$(ls memory/archive/sessions/0*.md | wc -l | tr -d " ")" = "7" ]'
chk "3 parallel rollovers: INDEX has 7 rows" '[ "$(grep -c "^| \[" memory/archive/sessions/INDEX.md)" = "7" ]'
chk "3 parallel rollovers: LINEAGE keeps the 3 newest" '[ "$(grep -c "^## SESSION [0-9]" memory/LINEAGE.md)" = "3" ]'
chk "no temp files left behind" '[ -z "$(find memory -name "*.tmp" 2>/dev/null)" ]'

echo; echo "--- 8. to-trash fallback: same name in the same second does not overwrite"
H="$T/home"; STUB="$T/stub"; mkdir -p "$H" "$STUB" "$T/d1" "$T/d2"
for c in mkdir mv basename mktemp; do ln -sf "$(command -v $c)" "$STUB/$c"; done   # a PATH without the `trash` command
echo one > "$T/d1/same.txt"; echo two > "$T/d2/same.txt"
HOME="$H" PATH="$STUB" "$BASH" scripts/to-trash.sh "$T/d1/same.txt" "$T/d2/same.txt" >/dev/null
chk "both same-named files are in the Trash" '[ "$(find "$H/.Trash" -type f -name same.txt | wc -l | tr -d " ")" = "2" ]'
chk "both contents survived" '[ "$(cat $(find "$H/.Trash" -type f -name same.txt) | sort | tr -d "\n")" = "onetwo" ]'
chk "the originals are gone" '[ ! -e "$T/d1/same.txt" ] && [ ! -e "$T/d2/same.txt" ]'

echo; echo "--- 9. commitments: invalid date, escaped pipe, short row"
python3 - "$TODAY" <<'PY'
import sys, pathlib
p = pathlib.Path("memory/commitments.md")
t = p.read_text(encoding="utf-8")
rows = ("| Alice | **Invalid date item** | 2026-02-30 | open | 1 | x |\n"
        "| Bob | **Pipe \\| item** | %s | open | 1 | x |\n"
        "| Carol | **Short row** | 2026-01-01 |\n"
        "| Dan | **Old but valid item** | 2020-01-01 | open | 1 | x |\n" % sys.argv[1])
i = t.index("\n## Archive")
p.write_text(t[:i].rstrip("\n") + "\n" + rows + t[i:], encoding="utf-8")
PY
OUT3=$(python3 scripts/due-commitments.py --summary 2>&1); RC3=$?
OUT4=$(python3 scripts/due-commitments.py --all-open 2>&1); RC4=$?
chk "no traceback, exit 0 (boot and --all-open)" '[ $RC3 = 0 ] && [ $RC4 = 0 ] && ! echo "$OUT3$OUT4" | grep -q Traceback'
chk "invalid date is reported per row" 'echo "$OUT3" | grep -q "invalid date in row: Invalid date item"'
chk "the other rows are still reported" 'echo "$OUT3" | grep -q "Old but valid item"'
chk "escaped pipe stays in one cell, row not dropped" 'echo "$OUT3" | grep -q "DUE (TODAY): Pipe | item"'
chk "a row with the wrong column count gives a warning" 'echo "$OUT3" | grep -q "WARNING: table row has 3 columns"'

echo; echo "--- 10. selftest on a filled-in repo (BRAIN without placeholders)"
if [ -n "${SELFTEST_NESTED:-}" ]; then
  echo "(skipped in the nested run)"
else
  F="$(mktemp -d "${TMPDIR:-/tmp}/cc-selftest-filled.XXXXXX")"
  if [ -n "$F" ] && [ -d "$F" ] && ( copy_skeleton "$F" ); then
    python3 - "$F/memory/BRAIN.md" <<'PY'
import re, sys, pathlib
p = pathlib.Path(sys.argv[1])
p.write_text(re.sub(r"\[FILL IN[^\]]*\]", "filled in", p.read_text(encoding="utf-8")), encoding="utf-8")
PY
    chk "the test copy has no placeholders left" '! grep -q "\[FILL IN" "$F/memory/BRAIN.md"'
    ( cd "$F" && SELFTEST_NESTED=1 bash scripts/selftest.sh ) > "$F.out" 2>&1
    chk "selftest passes on the filled-in copy" 'tail -n 1 "$F.out" | grep -q "SELFTEST: everything passed"'
    [ "$FAIL" -eq 0 ] || tail -n 15 "$F.out"
  else
    bad "could not prepare the filled-in copy"
  fi
fi

echo; echo "--- 11. cleanup"
if [ "$FAIL" -eq 0 ]; then
  [ -z "${F:-}" ] || bash "$SRC/scripts/to-trash.sh" "$F" "$F.out" >/dev/null 2>&1 || true
  cd "$SRC" && bash scripts/to-trash.sh "$T" >/dev/null 2>&1 && echo "The temporary copy went to the Trash." || echo "The temporary copy stays in $T (move it to the Trash: bash scripts/to-trash.sh \"$T\")"
else
  echo "The temporary copy stays in $T for inspection (then: bash scripts/to-trash.sh \"$T\")"
fi
echo
if [ "$FAIL" -eq 0 ]; then echo "SELFTEST: everything passed"; exit 0; else echo "SELFTEST: $FAIL failures"; exit 1; fi
