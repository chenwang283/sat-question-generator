# Output format

Four standardized shapes so every stage and script reads each other's output
mechanically:

1. **Question set** (markdown) — the unit generated and passed between stages.
2. **Math solution spec** (JSON) — embedded in Math items; checked by `check_math.py`.
3. **Verification report** (markdown) — the verifier's per-item pass/fail.
4. **Word layout** (.docx) — the final deliverable from `build_docx.py`.

These shapes are fixed: the orchestrator routes by their headings and labels, the scripts
parse them, and Study Spaces extracts the Word doc by structure. Don't vary them.

On disk these correspond to the staged artifacts named in `workflow.md`: the **question set**
is staged as `generated/<skill>__<difficulty>.md` (and, once it passes, copied verbatim to
`final/<skill>__<difficulty>.md`), and the **verification report** as
`verified/<skill>__<difficulty>.md`. This file defines the *shapes*; `workflow.md` defines
*where they are staged* — the two are kept separate on purpose.

## 1. Question set (markdown)

One file per `(skill × difficulty)`. A header line, a `set-meta` comment, then items
separated by a line containing only `---`. Math example:

````markdown
# <Subject> · <Topic> · <Skill> — <Difficulty>
<!-- set-meta: subject=math; topic=algebra; skill=linear-equations-in-one-variable; difficulty=easy; count=10 -->

## Item 1
**Stem:** If 3x + 5 = 20, what is the value of x?
**A.** 3
**B.** 5
**C.** 9
**D.** 25/3
**Correct:** B
**Explanation:** Subtracting 5 from both sides gives 3x = 15, so x = 5.
**Why not A:** Reaches 3x = 15 but divides by the constant 5 instead of the coefficient 3 (15 ÷ 5 = 3).
**Why not C:** Reaches 3x = 15 but subtracts the coefficient 3 twice instead of dividing (15 − 3 − 3 = 9).
**Why not D:** Adds 5 to both sides instead of subtracting, then divides by 3: (20 + 5)/3 = 25/3.
```spec
{ "given": ["3*x+5=20"], "ask": "x", "options": {"A":"3","B":"5","C":"9","D":"25/3"}, "correct": "B", "verify": "auto" }
```

---
## Item 2
...
````

Reading & Writing items include a `**Passage:**` line (an original passage) and omit the
`spec` block:

````markdown
## Item 1
**Passage:** The archivist's approach was notably ______: rather than discarding the water-damaged ledgers, she catalogued each one before deciding its fate.
**Stem:** Which choice completes the text with the most logical and precise word?
**A.** methodical
**B.** hasty
**C.** indifferent
**D.** decorative
**Correct:** A
**Explanation:** The cataloguing-before-deciding behavior signals careful order, so "methodical" fits.
**Why not B:** "Hasty" is the opposite of the careful, cataloguing-before-deciding behavior the text describes.
**Why not C:** "Indifferent" contradicts the archivist's deliberate effort to catalogue each ledger before acting.
**Why not D:** "Decorative" is unrelated to the process described; nothing in the text concerns ornamentation.
````

Rules:

- Exact bolded labels: `**Passage:**` (R&W only), `**Stem:**`, `**A.**`–`**D.**`,
  `**Correct:**` (a single letter A–D), `**Explanation:**` (explains why the correct
  answer is correct).
- After `**Explanation:**`, exactly three `**Why not X:**` lines — one for each option
  letter that is *not* the `**Correct:**` letter (so if `**Correct:**` is B, the lines are
  `**Why not A:**`, `**Why not C:**`, `**Why not D:**`). Each states, accurately and
  precisely, why that choice is wrong. The `**Explanation:**` line itself is unchanged.
- Items are separated by a lone `---`.
- Math items end with a ` ```spec ` block (after the `Why not` lines) and have no
  `**Passage:**`. R&W items have a `**Passage:**` and no `spec` block.
- `set-meta` slugs (`subject`, `topic`, `skill`) match `taxonomy.json`; `difficulty` is
  `easy` | `medium` | `hard`.

## 2. Math solution spec (JSON — Math items only)

Lets `check_math.py` confirm exactly one option is correct rather than trusting the key.

```json
{
  "given": ["3*x + 5 = 20"],
  "ask": "x",
  "options": { "A": "3", "B": "5", "C": "9", "D": "25/3" },
  "correct": "B",
  "verify": "auto"
}
```

- `given` — equations/constraints as sympy-parseable strings (`**` for powers, `*` for
  multiplication); may be empty for pure-evaluation items.
- `ask` — the symbol to solve for, or an expression to evaluate under the solution.
- `options` — each choice as a sympy-parseable value/expression.
- `correct` — the claimed correct option letter.
- `verify` — `"auto"` (script checks it) or `"manual"` (item can't be encoded — e.g. it
  depends on a figure; the script records it as unverified and the verifier reasons it by
  hand). Prefer `"auto"`.

## 3. Verification report (markdown)

One report per set. Per item: a verdict line, one row per rule, and a `**Failed rules:**`
line that the refine stage reads.

````markdown
# Verification — <Subject> · <Skill> — <Difficulty>
<!-- verify-meta: subject=math; topic=algebra; skill=linear-equations-in-one-variable; difficulty=easy; cycle=1 -->

## Item 1 — VERDICT: PASS
| Rule | Result | Reason |
|---|---|---|
| M-1 | PASS | Tests single-variable linear solve only |
| M-3 | PASS | check_math.py: B is the unique correct value |
| M-7 | PASS | Original scenario; no overlap with reference items |
**Failed rules:**

## Item 2 — VERDICT: FAIL
| Rule | Result | Reason |
|---|---|---|
| M-1 | PASS | Tests single-variable linear solve only |
| M-3 | FAIL | check_math.py: options B and D both evaluate to 5 |
**Failed rules:** M-3
````

- `## Item N — VERDICT: PASS|FAIL` per item; the verdict is FAIL if any rule failed.
- One table row per rule ID; `Result` is `PASS` or `FAIL`; `Reason` is one specific line.
- `**Failed rules:**` lists the failed IDs, comma-separated (empty when the item passes
  everything).
- Rule IDs come from the skill's verification-rules section.

## 4. Final Word layout (.docx)

The pipeline builds **one .docx per difficulty** — three docs per run (easy / medium /
hard) — by running `build_docx.py` once over each difficulty's final file. Each doc holds
that one difficulty's 10 questions; the script strips the `spec` blocks and lays them out
in a fixed shape:

- **Title** — the run name, naming the skill and difficulty (e.g. "Linear equations in one
  variable — Easy").
- A heading for the skill, then the difficulty label.
- The 10 questions one after another, each an identical block:
  - `Question <n>` (bold)
  - the passage (Reading & Writing only)
  - the stem
  - options `A.`–`D.`, one per line
  - `Answer: <letter>`
  - `Explanation: <text>`
  - `Why not <letter>: <text>` for each of the three non-correct options, in A→D order

Every item uses the same block shape and the same `Answer:` / `Explanation:` / `Why not X:`
labels, so Study Spaces can extract mechanically.
