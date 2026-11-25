---
description: Start a session. Loads the context and handoff from last time, reports what is burning and says what we are continuing with.
---

# /alive: start a session

## 1. Boot (one command)

```bash
bash scripts/boot.sh
```

The output shows: the number and name of your session (it claims it by itself), who is running alongside, the last 10 lines of `memory/activity.log`, overdue and upcoming commitments, the git state and the memory state. At the end there is the **REQUIRED READING** section.

## 2. Read the required files

Read the files from the last section of the output (`memory/BRAIN.md`, `memory/LINEAGE.md`) with the Read tool, **whole, all at once, without limit/offset**. Do not skip them and do not grep them: they say how we work together and where the previous session stopped. Do **not** read `memory/MEMORY.md` at boot; it is an index for searching on demand.

Boot is needed once per session. A repeated `/alive` in the same session does not claim a number again; do not read the files again.

## 3. Session number

The first line of the output "Your session" (`N  Name`) is yours for the whole session: it belongs in commits, the staging folder and `/end-session`. Do not invent another one. If another window is running alongside you, mention it once in half a sentence.

As soon as the user gives the first substantive task, write the topic so that the neighbour can see what you are working on (it overwrites, it does not append):

```bash
python3 scripts/session-claim.py --topic "short, what I am working on"
```

## 4. Unfilled BRAIN

If boot reports "unfilled placeholders" in `BRAIN.md` greater than 0, offer the user a short interview: ask in turn about the four things in §1 (what the work is about, what to delegate, what the user decides personally, how they want answers) and about their hard limits from §4. Write the answers into `BRAIN.md` yourself, the user does not have to edit the file; replace `[YOUR NAME]` as well. Do not push: if the user does not want to, leave it for next time.

## 5. Commitments and handoff

- Take the `SUMMARY:` line from the Commitments section into the status unchanged. An empty section = nothing is burning, do not mention it.
- If the staging folder `memory/.staging/` holds a foreign `HANDOFF.md` of another session that crashed, it is the unfinished work of that session; mention it to the user, do not delete it.
- After a compact (shortening of the context), first read your own `memory/.staging/<number>/HANDOFF.md`.

## 6. Output (max 5 lines)

- Session number and name, what you are continuing with (from the newest entry in LINEAGE), and whether another window is running alongside,
- commitments: the SUMMARY line, if there is one,
- anything in the activity log or the git state that is out of the ordinary (many uncommitted changes = the previous session may not have closed),
- at the end: "What are we working on?"

## Rules

- No dump of files into the answer, do not recite BRAIN or LINEAGE. Internalise, do not copy.
- Tone: brief, equal, ready to work.
- A new file in the boot = a line in `BOOT_FILES` in `scripts/boot.sh`.
