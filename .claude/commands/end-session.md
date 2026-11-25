---
description: Close the session. Assess what is worth writing down, save lessons to memory/, write the handoff into LINEAGE, regenerate the index and commit.
---

# /end-session: close the session

Goal: after the session, the contribution and the handoff are written down and nothing is left hanging. Write **only what has value**.

You have the number, name and ID of the session from boot (`python3 scripts/session-claim.py --show`). Do not invent new ones. Your own staging is `memory/.staging/<number>/`; do not read foreign staging folders.

## 1. Assess

| Question | Yes | No |
|---|---|---|
| Was something substantial worked on? | LINEAGE (step 5) | no LINEAGE |
| Did you learn a new procedure or trap? | `knowledge/` (step 4) | skip |
| Did the user correct you or confirm an unexpected approach? | `feedback/` (step 4) | skip |
| Did the state of work in progress change? | `projects/` (step 4) | skip |

**An empty session** (a greeting, nothing substantial): do only step 2 and step 8 ("session without a record"). The closing in step 8 is **never skipped**, otherwise the session hangs in the registry for 18 hours as a running neighbour.

## 2. Mechanics (always)

```bash
python3 scripts/activity-append.py "Session <N> — <Name>: what was done (one sentence)"
```

## 3. Commitments

```bash
python3 scripts/due-commitments.py --all-open
```

For each one decide: `done` (note by what and when in the notes, move to the Archive), `dropped` (reason), a new deadline, or it stays `open` (what it hangs on). What cannot be decided from the context of the session, leave and mention in the summary. Do not close a foreign commitment (written by another session) by guessing. Add new promises from this session that are not in the table yet.

## 4. Lessons (at most 5)

For each finding, in this order:

1. **Proposal**: one sentence of the core (not the topic of the session).
2. **Check against what is already written**: `grep -ril "<keywords>" memory/`.
   - already written the same way: write nothing,
   - an existing file covers the topic and the finding adds to it: extend it,
   - it contradicts what is written: fix the existing text in place, do not add a new version next to the old one,
   - nothing fits: a new file.
3. **Where**: `feedback/` (corrections from the user: rule, why, how to apply), `knowledge/` (how a thing works), `projects/` (state of work). Model and writing rules: `memory/README_MEMORY.md`.
4. **Frontmatter** (`name`, `description`, `type`, `status`, `last_edited`) and a link `[[slug]]` to a related file.

One experience is an observation, not a rule: write it as "seen 1x, date". If something keeps repeating (the same complaint a second time), a script or a check step solves it, not another sentence in the rules; propose that to the user in the summary.

## 5. LINEAGE (only a substantial session)

**First** update `memory/.staging/<number>/HANDOFF.md` from the current conversation, including everything since the last `/checkpoint` (if no checkpoint ever ran, the file is only the empty outline from boot). Only then build the entry from it into the file `memory/.staging/<number>/LINEAGE-entry.md`:

```text
## SESSION <N> — <Name>

**Date:** YYYY-MM-DD

### What was done
- ...

### Key decisions
- ...

### Learned
- ...

### Handoff
- open technical items (path:line, what remains), state of tests and deployment, data being handed over
- What I'm unsure about: ...
- What you might miss: ... (nothing = omit the line)
```

The "Handoff" **must not contain** an agenda for the next session ("consider", "I recommend", "worth doing"), open items copied from earlier, or an evaluation of your own performance. Only state and data.

Insert the entry and do the rollover with one command (LINEAGE keeps the 3 newest, everything is complete in `memory/archive/sessions/`):

```bash
python3 scripts/lineage-rollover.py --add memory/.staging/<number>/LINEAGE-entry.md
```

## 6. Index

```bash
python3 scripts/memory-index.py
```

If it warns about a missing `description`, add it.

## 7. Commit

```bash
git status --short                                  # what changed
git add <only your files, by name>                  # memory/…, LINEAGE.md, archive/sessions/…, activity.log, possibly project files
git commit -m "Session <N> — <Name>: <description>" -- <the same paths>   # pathspec commit: only these paths go in
```

- A pathspec commit (`git commit -- <paths>`) leaves out everything else that may be in the index. Do not unstage or restore files you did not touch: they may be another window's work.
- This does not give full isolation between windows: a shared file such as `commitments.md` can carry the other window's edits. Keep both windows in the same folder (separate worktrees would number sessions on their own).

- **Never `git add -A`, `git add .` or `git add memory/`**: a second window with work in progress may be running alongside, and it would be carried into your commit.
- `git push`: ask first, unless BRAIN §4 explicitly allows it. Never push to a remote that is public or that the user does not own. Otherwise the commit stays local, and say so in the summary.
- After the commit, send your own staging folder to the Trash: `bash scripts/to-trash.sh memory/.staging/<number>`.

## 8. Summary and closing (always, even for an empty session)

Close the record in the registry. Only now, not earlier:

```bash
python3 scripts/session-claim.py --close <number>
```

After closing, do not run a bare `session-claim.py` without `--id`: within a few minutes it would claim a new number.

Summary for the user, **max 6 lines**, skip the points without content:
- Session N — Name (or "session without a record"),
- what was written and where (for each finding: new / extended in X / fixed in X / already there),
- commitments that could not be decided,
- what remained uncommitted or unpushed and why,
- handoff: one sentence, where to continue.

## Rules

- No ballast: a short session with one decision = a short entry.
- Deleting only into the Trash (`scripts/to-trash.sh`), never permanently.
- Never read `.env`; no keys, passwords or copies of foreign e-mails belong in memory or in a commit.
