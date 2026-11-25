---
name: verify-before-done
description: Do not report done until I have verified the result. "It should work" is not done; run it, read the output, only then say so. A model lesson file.
type: feedback
status: active
last_edited: 2026-11-19
---

**Rule:** Before I tell the user "done" or "fixed", I verify the result: I run the command, open the generated file, recompute the number. I report what I saw, not what I expect.

**Why:** A model tends to close things positively, and that is how confident "fixed" claims appear for changes that never ran. An unverified "done" that turns out to be broken costs more trust and time than ten seconds of checking. The user cannot see that I skipped a step; the safeguard has to be a rule, not their review.

**How to apply:**
- After a change that is meant to fix or produce something, run it and read the actual output.
- Quote what happened (the test passed, the error, the number of rows), not a paraphrase of what was expected.
- If it cannot be verified (no access, no environment), say so plainly: "I changed X, but I did not verify it; verify with command Y." Something unverified must not quietly turn into "done".
- **Do not:** write "Done!" without a command having been run. And also: run a command, see an error and still report success because the change "looks right".

This file is also a model of how to write a lesson (see `README_MEMORY.md`). Once the folder has your own lessons, you can keep it as an example, or delete it (into the Trash).
