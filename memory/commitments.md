---
name: commitments
description: Tracker of commitments with deadlines (who promised what to whom, by when). Boot reads it and reports commitments that are overdue or due within 3 days. Claude writes to it when the user promises something.
type: tracker
status: active
last_edited: 2026-11-19
---

# Commitments: what we promised to whom

> Goal: a promise with a deadline does not get lost between sessions. When the user says "I'll send it to Alex by Friday", Claude writes a row here right away. Boot (`scripts/boot.sh`) reads the table and reports what is burning.

## How to write

A Markdown table. Columns: **To whom | What | Deadline | Status | Session | Notes**.

- **Deadline**: always an absolute date `YYYY-MM-DD`. Rewrite "by Friday" to a concrete day. Without a date the script only flags the commitment as NO DATE.
- **Status**: `open` (waiting), `in-progress` (under way), `done` (finished), `dropped` (cancelled, reason in the notes).
- **Session**: the number of the session that wrote the commitment.
- Move `done` and `dropped` to the Archive section below the table right away, so that the active table shows only what is open.

**The row must be in the section "Current commitments".** The script reads only that section and stops at the next `## ` heading; an open commitment below the Archive will never be seen. A note outside the table (a heading and bullets) is not read either.

When to write on your own: the user promises something with a deadline, someone promises something to the user, or a checkpoint is agreed ("we'll look at it in a week").

Check: `python3 scripts/due-commitments.py` (what is burning), `--all-open` (everything open, used by `/end-session`).

## Current commitments

| To whom | What | Deadline | Status | Session | Notes |
|---------|------|----------|--------|---------|-------|
| (example) Alex Smith | **Send the materials for the offer** (price table, 3 references) | 2026-01-20 | example | 0 | The script ignores a row with the status "example"; delete it when you write the first real one. |

## Archive (done / dropped)

| To whom | What | Deadline | Status | Session | Notes |
|---------|------|----------|--------|---------|-------|
