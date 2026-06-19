<!--
Reusable prompt skeleton for refining ONE failing question. Generic — no SAT content here.
The orchestrator fills {INJECT:...} at runtime (see references/workflow.md → "Refine").
Runs only on questions a verifier failed; the corrected item goes straight back to verify.
-->
# Prompt: refine a failing question

One question failed one or more verification rules. Fix it with the **lightest change**
that turns every failed rule green. Do not rewrite parts that already pass, and do not
change the difficulty.

## The failing item

{INJECT:ITEM}

## Rules it failed (IDs + the reviewer's reasons)

{INJECT:FAILED_RULES}

These are the only problems you must solve. The reviewer's reason for each one tells you
what specifically is wrong.

## Subskill design (fix in line with this)

{INJECT:SUBSKILL_CORE}

## Difficulty (keep the item at this level)

{INJECT:DIFFICULTY}

## All verification rules (so your fix doesn't break a passing one)

{INJECT:VERIFICATION_RULES}

## How to fix

- Change only what's needed to clear the failed rules — but make the change *coherent*. If
  the correct answer itself changes, update the explanation to match, and for Math update
  the ` ```spec ` block so its keyed option is the new unique solution.
- Keep every currently-passing rule passing; re-check your edit against the full rule list
  above before finishing.
- Any new or rewritten content must stay original per `references/distinctness.md` — don't
  fix a problem by drifting toward the reference items.
- If the item is too compromised to patch (e.g. the passage itself is the failure), rebuild
  it from the subskill design rather than forcing a patch.

## Output

Output the single corrected item only, in the same standard item format as the input — the
same `## Item N` number, the `**Stem:**` / `**A.**`–`**D.**` / `**Correct:**` /
`**Explanation:**` labels, plus `**Passage:**` for Reading & Writing or the ` ```spec `
block for Math. No commentary. It goes straight back through verification.
