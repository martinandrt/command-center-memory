# LINEAGE — handoff sheet between sessions

> Every session reads this file right after BRAIN.md. You are part of a continuity, not an isolated instance: the newest entry below is your starting point.

## How to read

1. The writing rules below.
2. The newest entry (the first one below the line) = what the previous session did and what it left open.
3. Older sessions are kept in full in `memory/archive/sessions/` (`INDEX.md` is the overview). Read them only when you need older context.

## Writing rules

- Written at the end of a session (`/end-session`). The entry is not written into this file by hand: it is prepared in `memory/.staging/<number>/LINEAGE-entry.md` and inserted with `python3 scripts/lineage-rollover.py --add <file>`.
- **The handoff = what the NEXT session must know**, not a list of work done. Short.
- The number and name of the session are assigned by boot (`scripts/session-claim.py`), they are not invented. Every new session gets the next whole number, even if another one is running alongside.
- Retroactively inserting older numbers is forbidden. Catching up on work from past days gets the next number with a note "caught up from YYYY-MM-DD".
- The 3 newest sessions stay in the body, and each of them is also complete in the archive (handled by `scripts/lineage-rollover.py`, nothing is deleted).
- Findings of lasting value belong in `memory/feedback/` or `memory/knowledge/`, not only here.

**Entry format** (the "Handoff" section contains only):
- open technical items (`path:line` and what remains), work in progress,
- state of tests and deployment, known bugs,
- data being handed over (links, IDs),
- "What I'm unsure about": unverified claims, one sentence each,
- "What you might miss": what the next session cannot notice by itself (a running process, a temporary state).

**Does not belong in the handoff** (it is an agenda, not a handoff): "consider next time", "I recommend", "worth doing", "proactively offer", open items copied from previous sessions, evaluation of one's own performance.

Example of an entry (fictional; the example is ignored by rollover):

```text
## SESSION N — Kestrel

**Date:** 2026-01-15

### What was done
- Preparing materials for the supplier contract negotiation (a price overview for 3 years).

### Key decisions
- We compare only contracts after 2024, older ones have different terms.

### Learned
- The user wants prices excluding VAT and always in a table (written to memory/feedback/prices-without-vat.md).

### Handoff
- In progress: the price table in `memory/projects/supplier-negotiation.md`, the year 2026 is missing.
- What I'm unsure about: the shipping price for supplier B comes from an e-mail, not from the contract.
```

---
