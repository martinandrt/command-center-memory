---
name: readme-memory
description: Guide to the memory. Where to write what (feedback, knowledge, projects, reference, commitments), the frontmatter format and how to write entries so that the next session really uses them.
type: process
status: active
last_edited: 2026-11-19
---

# memory/ — where to write what

`MEMORY.md` is a **generated listing** (`python3 scripts/memory-index.py` reads `description` from the frontmatter). It says what is in the memory. **Where to write something is said by this file.**

The memory is a working manual for Claude, not documentation for people. The user does not have to read it or approve it; what matters is that the next session does the right thing on the first try, on the user's word.

## Where things belong

| What I should write down | Where | Test |
|---|---|---|
| The user corrected me or said how they want something | `feedback/<slug>.md` | Is it a preference or a correction of behaviour that holds next time too? |
| I learned how something works (a tool, a procedure, a system) | `knowledge/<slug>.md` | Is it about the world, not about the user's preferences? |
| State of work in progress | `projects/<name>.md` | Does it have a beginning, an end and a changing state? |
| A stable fact to look up (a contact, a number, a link, a price list) | `reference/<slug>.md` | Does it stay the same and is it only ever looked up? |
| A promise with a deadline (who promised what to whom, by when) | `commitments.md` | Does it have a date and a second party? |
| Who the user is and what drives them | `BRAIN.md` §1 and §7 | Does it hold about the person across tasks? |
| A greeting, a trifle, a one-off thing | nowhere | Would it help the next session? No = do not write it. |

**Writing rules:**
- First try to extend an existing file (`grep -ril "<topic>" memory/`). A new file only when nothing fits. Duplication is worse than a longer file.
- One fact, one place. If you need it elsewhere: a link `[[file-slug]]`, not a copy. A number in two places drifts apart within a month.
- Plain, factual language, in the language of the user, no emoji. File names in `kebab-case`, the date only in the frontmatter.
- Copies of e-mails, CVs and personal data of third parties are not written into the repo, only a link to where they are.
- A path in backticks means "this exists". A path that disappeared is written without backticks and with a note on where it is now.
- Do not edit `MEMORY.md` by hand.

## Frontmatter (every file in memory/ except BRAIN and LINEAGE)

```yaml
---
name: short-name-or-slug
description: One sentence. It is the only thing that appears in MEMORY.md and the way the file is found. Write it in the user's own words.
type: feedback        # feedback | knowledge | project | reference | tracker | process
status: active        # active | archived
last_edited: 2026-11-19
---
```

The parser is deliberately dumb: only single-line `key: value`, no nested YAML. `description` is the search surface; a vague description = a file that is never found and gets written a second time.

## How to write a lesson (feedback) so that it works

The file is not read by a person, it is read by Claude, who then acts on it. Six rules:

1. **What to do on top**, not the story of how it came about. Ideally the user's actual sentence and the exact procedure next to it.
2. **Always why.** Without a reason the next session applies the rule too narrowly or too broadly, or gets around it.
3. **What not to do, explicitly.** The model tends to do "something extra to be safe". The prohibition has to be in the file.
4. **Freshness.** A file that refers to something that no longer exists poses as truth. Before using it, check that the referenced thing still exists.
5. **Names the user uses.** The file is searched by words, not by taxonomy. Name it the way the user would say it.
6. **Conclusion on top, detail below.** If the first three lines do not say what to do, rewrite it.

Recommended skeleton (model: `feedback/verify-before-done.md`):

```text
**Rule:** <trigger → what to do>
**Why:** <reason>
**How to apply:** <concrete steps and what NOT to do>
```

**One experience is not a rule.** The first time, write it down as an observation ("seen 1x, date"); it becomes a rule only when it is confirmed a second time. Otherwise a conclusion from a single coincidence gets into memory and every session then follows it.

## What is not written by hand

| File | Who writes it |
|---|---|
| `MEMORY.md` | `scripts/memory-index.py` |
| `LINEAGE.md`, `archive/sessions/` | `/end-session` via `scripts/lineage-rollover.py` |
| `activity.log` | `scripts/activity-append.py` (called by `/end-session`) |
| `sessions-running.jsonl`, `.staging/` | `scripts/session-claim.py` and boot; not part of git |

## Maintenance

- Regenerate the index: `python3 scripts/memory-index.py` (`--check` shows whether it is out of date).
- Once a month go through `feedback/` and `knowledge/`: whatever is out of date goes to `memory/archive/` (into the Trash via `scripts/to-trash.sh`, not by permanent deletion). A memory that only grows turns into sediment.
- `archive/` holds retired material and old sessions, not lasting memory.
