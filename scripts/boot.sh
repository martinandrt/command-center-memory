#!/bin/bash
# Session boot: the state of the world in one command. Called by /alive.
# Prints: the number and name of the session (claims it), who is running alongside, the last 10 lines of the activity log,
# overdue / upcoming commitments, git state and the paths of the required reading (BRAIN.md, LINEAGE.md).
# It does not print the files themselves: Claude reads them with the Read tool.
#
# Usage: bash scripts/boot.sh
# A new file in the boot = add a line to BOOT_FILES (the only place where it is defined).

CC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BOOT_FILES=(
  "memory/BRAIN.md"
  "memory/LINEAGE.md"
)

cd "$CC" || { echo "boot.sh: folder $CC not found" >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "boot.sh: python3 is missing (3.8+ required)" >&2; exit 1; }

section() { printf '\n===== %s =====\n' "$1"; }

section "Your session"
claim=$(python3 scripts/session-claim.py 2>&1)
num=$(printf '%s\n' "$claim" | awk 'NR==1{print $1}')
if [[ "$num" =~ ^[0-9]+$ ]]; then
  printf '%s\n' "$claim"
  echo "This number is yours for the whole session: it goes into commits, the staging folder and /end-session."
  handoff="memory/.staging/$num/HANDOFF.md"
  mkdir -p "memory/.staging/$num"
  if [[ ! -f "$handoff" ]]; then
    cat > "$handoff" <<EOF
# Handoff for session $num (created $(date '+%Y-%m-%d %H:%M'))

Running notes for LINEAGE. /checkpoint fills it in, /end-session builds the entry from this file.
Not committed.

## What is being worked on

## Decisions

## Learned

## Handoff (open items, running processes, data)
EOF
  fi
  echo "Handoff: $CC/$handoff"
else
  echo "session-claim.py failed:"
  printf '%s\n' "$claim"
fi

section "Activity (last 10)"
if [[ -s memory/activity.log ]]; then tail -n 10 memory/activity.log; else echo "(empty so far)"; fi

section "Commitments"
due=$(python3 scripts/due-commitments.py --summary 2>&1)
if [[ -n "$due" ]]; then printf '%s\n' "$due"; else echo "nothing is burning"; fi

section "Git"
if git rev-parse --git-dir >/dev/null 2>&1; then
  n=$(git status --short | wc -l | tr -d ' ')
  echo "Uncommitted changes: $n"
  echo "Last commit: $(git log -1 --format='%h %s (%cr)' 2>/dev/null || echo 'none')"
else
  echo "This folder is not a git repo (run git init, otherwise memory is not saved anywhere)."
fi

section "Memory status"
[[ -f memory/MEMORY.md ]] || python3 scripts/memory-index.py >/dev/null 2>&1
unfilled=$(grep -c "\[FILL IN" memory/BRAIN.md 2>/dev/null || true)
sessions=$(grep -c '^## SESSION [0-9]' memory/LINEAGE.md 2>/dev/null || true)
echo "BRAIN.md: unfilled placeholders: ${unfilled:-0}"
echo "LINEAGE.md: sessions in body: ${sessions:-0}"
if [[ "${unfilled:-0}" -gt 0 ]]; then
  echo "-> BRAIN.md is not filled in yet. Offer a short interview (5 questions) and fill it in yourself from the answers."
fi
if [[ "${sessions:-0}" -eq 0 ]]; then
  echo "-> First session: there is no handoff from before, that is fine."
fi

section "REQUIRED READING: read with the Read tool, whole, no limit/offset, all in one go"
for f in "${BOOT_FILES[@]}"; do
  if [[ -f "$f" ]]; then echo "$CC/$f  ($(wc -c <"$f" | tr -d ' ') B)"; else echo "$CC/$f  (file missing!)"; fi
done
echo
echo "Done. Now: read the files above, then give a short status (see /alive)."
