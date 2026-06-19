---
name: sat-question-generator
description: >-
  Generate original, College-Board-distinct SAT practice questions that test the same
  skills as the official digital SAT, via a generate → verify → refine → Word-export
  pipeline. Use this whenever the user wants to create, write, generate, produce, or
  build SAT or digital-SAT / Bluebook-style practice problems, question sets, or item
  banks — for Math or Reading & Writing, by subskill and difficulty (Easy/Medium/Hard) —
  or wants to verify generated SAT items against rules, refine failing items, or turn
  uploaded College Board question PDFs into fresh, equivalent practice. Trigger even on
  terse asks like "make me 10 hard linear-equation SAT questions" or "write SAT Words in
  Context items," and whenever the user uploads official SAT question PDFs and asks for
  similar ones. Built to run in Claude Code (uses subagents).
---

# SAT question generator

Turn uploaded official SAT questions into fresh, original practice that tests the same
skill the same way — **functionally equivalent** to College Board items (same skill,
structure, difficulty) but **original** content (no copied or paraphrased passages,
scenarios, or values). Questions are generated, independently verified, refined until
they pass, and exported to a standardized Word document.

## When and where

Built for **Claude Code**, because the pipeline runs **subagents**: one generator per
difficulty, and one independent verifier per difficulty. The independence is the point —
a verifier that didn't write the questions catches what the writer rationalized. Outside
Claude Code it can run serially, without that parallelism or independence.

## The pipeline

```
3 PDFs ─► GENERATE (1/difficulty) ─► VERIFY (1/difficulty) ─► REFINE ─► (re-verify) ─► WORD DOC
                                          └──────── loop until all pass ────────┘
```

Operational detail — subagent orchestration, injection, loop conditions, on-disk
staging — lives in **`references/workflow.md`**; read it before running a job. At a
glance:

1. **Intake.** The user uploads 3 PDFs (one subskill at easy/medium/hard, 10 questions
   each) and says which is which. Echo the mapping back to confirm before generating.
2. **Generate.** One subagent per difficulty. Each reads its own reference PDF plus the
   subskill's guideline file — the shared sections, plus only its own difficulty's
   block — and writes 10 full questions in the standard format.
3. **Verify.** One independent subagent per difficulty checks all 10 against the
   subskill's verification rules; Math correctness runs through `check_math.py`. Output
   is pass/fail per question.
4. **Refine.** Any question that fails any check is corrected (lightest coherent touch)
   and sent back to verify. Loop until all pass; cap at 3 cycles and surface stragglers.
5. **Export.** Build one Word doc: three sets of 10 full questions (easy / medium /
   hard), one after another.

## Two layers: reusable prompts + per-subskill guidelines

Instructions and content are kept separate. `prompts/*.md` are **generic skeletons,
written once**, with `{INJECT:...}` slots and no SAT content of their own. The
**per-subskill guideline file** supplies the content. At runtime the orchestrator
injects the relevant guidelines into a skeleton and hands it to a subagent.

There is **one guideline file per subskill**, and it feeds *both* generation and
verification — the generator writes toward it, the verifier checks against it — so the
question rules and the verification rules can't drift apart, and each subskill is
maintained in exactly one place. Difficulty lives in that same file as three labeled
blocks; each per-difficulty subagent is injected only its own block, so the "hard"
generator never sees the "easy" definition that would drag it toward the middle.

```
references/subskill-rules/<section>/<skill>/<subskill>.md
```

## Current state: guideline files are placeholders*

The guideline files are **empty stubs** right now (structure shown in the templates
`references/subskill-rules/_TEMPLATE-*.md`). Generation quality depends entirely on
them, so **before generating for a subskill, its file must be filled in** — if it still
says `status: PLACEHOLDER`, stop and tell the user that subskill isn't ready.

## Prompt skeletons

- `prompts/generate.md` — one generation subagent (subskill × difficulty); gets the
  guideline (core + one difficulty block) and the reference PDF injected.
- `prompts/verify.md` — one verification subagent; gets the guideline and the questions.
- `prompts/refine.md` — fix one failing item against its failed rule IDs.

## Reference files

- `references/workflow.md` — the pipeline in operational detail.
- `references/distinctness.md` — same skill, original content; what the distinctness
  check fails on. **Read before generating.**
- `references/output-format.md` — the standard question-set markdown, the Math solution
  spec, the verification report, and the final Word layout. The scripts depend on these.
- `references/taxonomy.json` — canonical digital-SAT taxonomy (drives the subskill folder layout).
- `references/subskill-rules/...` — the per-subskill guideline files (source of truth).

## Scripts

- `scripts/check_math.py` — confirms each Math item has exactly one correct option
  matching the key. Run during verification.
  `python scripts/check_math.py <question-set.md>`
- `scripts/build_docx.py` — builds the final Word doc (three sets of 10).
  `python scripts/build_docx.py --out final.docx --title "..." <sets...>`

Dependencies: `sympy`, `python-docx`
(`pip install sympy python-docx --break-system-packages`). To read reference PDFs, use
the `pdf` skill.
