---
description: Save findings and state along the way without closing the session. Can be run at any time, the session keeps running.
---

# /checkpoint: save along the way (the session continues)

A long session does not wait for `/end-session`. A checkpoint saves what you have learned so far, completes the handoff and commits. It does **not close** the session (no write to LINEAGE, no closing of the number). It can be repeated.

An unwritten finding disappears when the session crashes or the context is shortened. That is why "write it down" leads here.

## 1. Assess what has happened so far

| Question | If yes |
|---|---|
| Did you learn a new procedure, or run into a trap (gotcha)? | `memory/knowledge/` |
| Did the user correct you or confirm an unexpected approach? | `memory/feedback/` |
| Did the state of work in progress change (a decision, a milestone, a blocker)? | `memory/projects/<name>.md` |
| Did the user promise something with a deadline? | `memory/commitments.md` |

**Nothing substantial since the last checkpoint: say so and finish.** No commit for the sake of tidiness.

## 2. Write

The writing rules are in `memory/README_MEMORY.md` (where, frontmatter, how to write). In short:
- First `grep -ril "<topic>" memory/`: extending an existing file is better than creating a new one.
- A new file has frontmatter (`name`, `description`, `type`, `status`, `last_edited`).
- At most 5 entries per checkpoint. Plain language, no emoji.

## 3. Complete the handoff

`memory/.staging/<number>/HANDOFF.md` (created by boot; if it is missing, create it): add what has been worked on, decided and learned since last time, and what remains open (running processes, waiting for the user). Bullets, brief, so that `/end-session` can build the entry from it without thinking. Staging is not committed.

## 4. Index and commit

```bash
python3 scripts/memory-index.py
git add <only the files you touched, by name>
git commit -m "Checkpoint — <topic>: <what was saved>" -- <the same paths>   # pathspec commit: only these paths go in
```

- **Never `git add -A` or `git add memory/`**: a second window with work in progress may be running alongside. Stage only your own files by name and commit them with `git commit -- <paths>`, so nothing else in the index is included. Do not unstage or restore files you did not touch: they may be another window's work.
- This does not give full isolation between windows: a shared file such as `commitments.md` can carry the other window's edits. Keep both windows in the same folder (separate worktrees would number sessions on their own).
- `git push`: ask first, unless BRAIN §4 explicitly allows it. Never push to a remote that is public or that the user does not own.

## 5. Topic in the registry

```bash
python3 scripts/session-claim.py --topic "what I am working on now"
```

A topic that has not been updated is, after an hour, a falsehood, not information; the neighbouring window sees it at boot.

## 6. Summary (max 3 lines)

What was written, what was committed, what remains open. The session keeps running, no agenda for next time.
