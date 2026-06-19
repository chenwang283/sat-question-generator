<!--
GUIDELINE TEMPLATE — Math subskill. One file per subskill is the single source of truth for
BOTH generation and verification (see references/workflow.md). The orchestrator slices this
file into three pieces, so KEEP these headings exactly:
  - SUBSKILL_CORE      = the `## Core` section (identity + design)
  - DIFFICULTY         = one `### <level>` block under `## Difficulty`
  - VERIFICATION_RULES = the `## Verification rules` section
Fill in every TODO below.
When the file is complete, change `status` from PLACEHOLDER to `ready`.
-->

# Math · Algebra · Systems of two linear equations in two variables

## Core

- **section:** math
- **skill:** algebra
- **subskill:** systems-of-two-linear-equations-in-two-variables
- **status:** PLACEHOLDER — rules not yet written

### Invariant — what this subskill tests

The constant across every item: the exact skill and cognitive task, regardless of the
surface story or numbers. This is what "functionally equivalent to a College Board item"
means.

> TODO: 2–4 sentences. e.g. for *Linear equations in one variable*: "Solve, or reason about
> the solution of, a single linear equation in one variable — including no-solution and
> infinite-solution cases. The student isolates the variable or recognizes the structural
> feature that fixes the number of solutions."

### Question variables

The knobs the generator turns for variety without changing what is tested.

| Variable | Allowed range / options | Notes |
|---|---|---|
| Context / framing | TODO (abstract, or a real-world frame) | |
| Numbers / coefficients | TODO (e.g. integers in a stated range) | keep arithmetic SAT-appropriate |
| Form presented | TODO (equation / table / graph / words) | |
| What is asked | TODO (solve for x / evaluate an expression / number of solutions) | |
| Answer format | TODO (4-option multiple choice, or student-produced response) | |

### Answer & distractor design

- **Correct-answer rule:** TODO — state precisely what makes exactly one option correct.
- **Distractor error patterns:** TODO — list the specific, named student errors each wrong
  option should embody (e.g. sign error when moving a term, divide-instead-of-multiply,
  dropped distribution). Distractors must be diagnostic, not random.
- **Option distinctness:** all four options distinct; no two equal values.

### Solution spec (required for every Math item)

Every generated item carries a machine-checkable `spec` block so `check_math.py` can confirm
the key. The JSON shape is fixed in `references/output-format.md` (`given`, `ask`, `options`,
`correct`, `verify`).

> TODO: note any skill-specific spec needs (e.g. "state the domain restriction", "give units").

## Difficulty

What moves an item between levels *for this subskill*. Same skill at every level — only the
load changes. Each block is injected on its own, so write each to stand alone.

### Easy
> TODO — what makes this subskill easy (e.g. one operation, integer answer, abstract framing).

### Medium
> TODO — e.g. two or three steps, variables on both sides, light real-world translation.

### Hard
> TODO — e.g. structural insight required, multi-step translation, fractional/edge-case
> answers, or a no-/infinite-solution twist.

## Verification rules

Checked by the verifier; an item passes only if **all** pass. Each references the sections
above, so they apply as soon as Core and Difficulty are filled in. Adjust per subskill only
if needed.

| ID | Rule (passes when…) |
|---|---|
| M-1 | The item tests the Invariant above and nothing else. |
| M-2 | The item is calibrated to the requested difficulty (its `### <level>` block). |
| M-3 | Exactly one option is mathematically correct, confirmed by `check_math.py`. |
| M-4 | Every distractor maps to a named error pattern in the distractor design. |
| M-5 | Numbers and the answer are clean and SAT-appropriate per the question variables. |
| M-6 | The explanation correctly derives the keyed answer. |
| M-7 | Distinctness: not a paraphrase of any reference item (see `distinctness.md`). |
| M-8 | The item is self-contained and unambiguous — exactly one defensible answer. |
