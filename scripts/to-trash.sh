#!/bin/bash
# Move to the Trash instead of deleting permanently (rm). Usage: bash scripts/to-trash.sh <file-or-folder> [...]
# macOS: the `trash` command (part of the system since macOS 14, otherwise `brew install trash`); otherwise mv into ~/.Trash.
[ $# -gt 0 ] || { echo "usage: to-trash.sh <path> [...]"; exit 1; }
rc=0  # non-zero if any item failed
for f in "$@"; do
  [ -e "$f" ] || [ -L "$f" ] || { echo "does not exist: $f"; rc=1; continue; }
  if command -v trash >/dev/null 2>&1; then
    trash "$f" && echo "moved to Trash: $f" || rc=1
  else
    mkdir -p "$HOME/.Trash"
    # a unique folder per item, the original name kept inside: same-named files never collide
    d=$(mktemp -d "$HOME/.Trash/to-trash.XXXXXX") || { echo "cannot create a folder in ~/.Trash"; rc=1; continue; }
    mv "$f" "$d/$(basename "$f")" && echo "moved to Trash: $f" || rc=1
  fi
done
exit $rc
