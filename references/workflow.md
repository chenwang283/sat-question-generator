# Workflow: generate → verify → refine → export

Operational detail behind the pipeline summarized in SKILL.md. Read this before running
a job.

```
3 PDFs ─► GENERATE (1/difficulty) ─► VERIFY (1/difficulty) ─► REFINE ─► (re-verify) ─► WORD DOC
                                          └──────── loop until all pass ────────┘
```

The unit of work is one **(subskill × difficulty)** → **10 questions**. A normal run is
one subskill across all three difficulties — the three PDFs the user uploads.

## How prompts and guidelines assemble

Two layers (see SKILL.md): generic **prompt skeletons** in `prompts/` with `{INJECT:...}`
slots, and one **guideline file per subskill** under `references/subskill-rules/` that
holds the content. At each stage the orchestrator pulls the relevant pieces out of the
guideline file, fills the skeleton's slots, and hands the assembled prompt to a subagent.

Three pieces get pulled from a guideline file:

- **Core** — the subskill's identity header (section / skill / subskill, used to write the
  output's `set-meta` line) plus the difficulty-independent design content: the invariant
  (what the subskill tests), the question variables, the distractor design, and for Math
  the machine-checkable solution-spec requirement.
- **Difficulty** — one self-labeled block for the level being run (its name and
  definition together, e.g. a `### Hard` block). In the guideline file the difficulty
  section is three such self-contained blocks; only the relevant one is ever injected, so
  a "hard" subagent isn't anchored by the "easy" definition.
- **Verification rules** — the yes/no checks (verify and refine stages only).

## Orchestrator role — how slots get filled

The skill runs with one **orchestrator** (the main agent) plus stage **subagents**
(workers). Subagents never talk to each other; every piece of data flows through the
orchestrator. For each stage it: extracts the pieces it needs from the guideline file and
from the previous stage's staged output, fills the next prompt's `{INJECT:...}` slots,
spawns the subagent, and stages whatever comes back. It also drives the verify → refine →
re-verify loop and the final export.

This works because every staged artifact is in a fixed format (see `output-format.md`), so
the orchestrator extracts by known headings and labels — the `### <level>` block in a
guideline, `## Item N` in a set, `**Failed rules:**` in a report — not by loose reading.
Staging each stage's output to disk is what gives the orchestrator (and `check_math.py`) a
concrete file to parse. The orchestrator extracts the guideline slices once at intake and
holds them for the whole run, so verify and refine reuse them rather than re-reading.

Where each slot comes from:

| Stage | Slot | Source |
|---|---|---|
| Generate | `SUBSKILL_CORE` | guideline file — identity header + core sections, sliced by heading |
| | `DIFFICULTY` | guideline file — the one `### <level>` block |
| | `REFERENCE_PDF` | the PDF the user mapped to this difficulty at intake |
| | `COUNT` | the run setting (default 10) |
| Verify | `SUBSKILL_CORE`, `DIFFICULTY` | the same guideline slices already extracted for generation |
| | `VERIFICATION_RULES` | guideline file — the verification-rules section, sliced by heading |
| | `QUESTIONS` | path to the staged `generated/<subskill>__<difficulty>.md` |
| Refine | `ITEM` | the `## Item N` block pulled from the staged set, for each N the report marked FAIL |
| | `FAILED_RULES` | the verification report — that item's failed rule IDs + the reviewer's reason rows |
| | `SUBSKILL_CORE`, `DIFFICULTY`, `VERIFICATION_RULES` | the same guideline slices, reused |

## 0. Intake

The user uploads 3 PDFs (one subskill, at easy/medium/hard, 10 questions each) and says
in their message which PDF is which. There is no categorization step — take the mapping
from what the user said.

Before anything else, **echo the mapping back and wait for confirmation** — e.g.
"Generating 10 each for *linear-equations-in-one-variable* at easy, medium, and hard from
these three files — correct?" This catches a mislabeled upload before it becomes a batch
of wrong-subskill questions.

Then load the subskill's guideline file. **If it still says `status: PLACEHOLDER`, stop
and tell the user that subskill isn't ready** — there are no rules to generate or verify
against.

## 1. Generate — one subagent per difficulty

Spin up three subagents to run in parallel, one per difficulty. Each receives the full assembled
`prompts/generate.md`, which combines **standing** instructions baked into the skeleton
with **injected** run-specific pieces. The complete payload to each subagent is:

Standing (in the skeleton, identical every run):
- the task framing — write `{COUNT}` original SAT items for one subskill at one difficulty;
- the distinctness principle (same skill, original content), pointing to
  `references/distinctness.md`;
- the output requirement, pointing to the question-set format in
  `references/output-format.md`.

Injected (per subagent, from the orchestrator):
- `{INJECT:SUBSKILL_CORE}` ← the subskill's core design content (invariant, question
  variables, distractor design, and for Math the solution-spec requirement);
- `{INJECT:DIFFICULTY}` ← the one self-labeled difficulty block for this subagent (label
  and definition together); the other two levels are never passed;
- `{INJECT:REFERENCE_PDF}` ← the matching uploaded PDF, which the subagent reads itself —
  for structure, and as the specific items it must not duplicate;
- `{INJECT:COUNT}` ← 10.

Each subagent writes 10 full questions in the standard question-set markdown: all four
options, the correct answer, and an explanation of the correct answer; Math items also
carry the `spec` block.

Stage output to `generated/<subskill>__<difficulty>.md`.

## 2. Verify — one independent subagent per difficulty

For each difficulty, assemble `prompts/verify.md`:

- `{INJECT:SUBSKILL_CORE}` + `{INJECT:DIFFICULTY}` — so the checker knows the design and
  the difficulty target it's checking against;
- `{INJECT:VERIFICATION_RULES}` ← the yes/no checks from the guideline;
- `{INJECT:QUESTIONS}` ← the generated set.

The verifier is a **fresh subagent that did not write the questions** — that independence
is the whole point; it checks rather than defends its own work. For Math it runs
`python scripts/check_math.py <set>` and uses that result for the correctness rule rather
than eyeballing arithmetic. It outputs a pass/fail per question — one line per rule with a
reason — in the verification-report format (`output-format.md`), ending each item with a
`Failed rules:` line.

Stage reports to `verified/<subskill>__<difficulty>.md`.

A question is **done** when it passes every rule. Any failed rule routes it to refine.

## 3. Refine — failing questions only, failed rules only

For each failing question, assemble `prompts/refine.md`:

- `{INJECT:ITEM}` ← the single failing question;
- `{INJECT:FAILED_RULES}` ← the failed rule IDs plus the verifier's reasons;
- `{INJECT:SUBSKILL_CORE}` + `{INJECT:DIFFICULTY}` + `{INJECT:VERIFICATION_RULES}`.

The refiner makes the lightest change that turns the failed rules green, adjusting
dependent parts only as needed (e.g. if the key changes, fix the explanation and, for
Math, the `spec` block too). It does not touch what already passes. If an item is too
broken to patch, it rebuilds from the guideline. Output is the single corrected item.

## 4. Loop

Send refined items back through step 2. Repeat refine ↔ verify until every question
passes, capped at **3 cycles**. Anything still failing after the cap is surfaced to the
user, not shipped — don't lower the bar to force a pass.

## 5. Export

When all three sets pass, stage them to `final/<subskill>__<difficulty>.md`, then run
`scripts/build_docx.py` over those files. It strips the Math `spec` blocks and emits one
Word doc: three sets of 10 full questions (easy / medium / hard), one after another, each
a uniform block (question, options, answer, explanation). Exact layout is in
`output-format.md`.

## Orchestration notes

- **Context hygiene:** each subagent gets only its slice — one subskill, one difficulty,
  the relevant guideline pieces — never the whole job.
- **Continuity:** keep `generated/`, `verified/`, `final/` on disk so any stage can re-run
  without redoing the rest.
- **Parallelism:** the three difficulties run in parallel at both generate and verify.
- **Determinism where it counts:** Math correctness (`check_math.py`) and the Word layout
  (`build_docx.py`) go through scripts, so they're identical every run.
