# Workflow: generate → verify → refine → export

Operational detail behind the pipeline summarized in SKILL.md. Read this before running
a job.

```
3 PDFs ─► GENERATE (1/difficulty) ─► VERIFY (1/difficulty) ─► REFINE ─► (re-verify) ─► 3 WORD DOCS (1/difficulty)
                                          └──────── loop until all pass ────────┘
```

The unit of work is one **(skill × difficulty)** → **10 questions**. A normal run is
one skill across all three difficulties — the three PDFs the user uploads.

## How prompts and guidelines assemble

Two layers (see SKILL.md): generic **prompt skeletons** in `prompts/` with `{INJECT:...}`
slots, and one **guideline file per skill** under `references/skill-rules/` that
holds the content. At each stage the orchestrator pulls the relevant pieces out of the
guideline file, fills the skeleton's slots, and hands the assembled prompt to a subagent.

Three pieces get pulled from a guideline file, each a **fixed heading** the orchestrator
slices on (the template says to keep these headings exactly, so the slice is mechanical, not
a judgement call):

- **Core** → `{INJECT:SKILL_CORE}` — the `# <Subject> · <Topic> · <Skill>` title line plus the
  entire `## Core` section. That section carries the `subject / topic / skill` identity bullets
  (used to write the output's `set-meta` line) and the difficulty-independent design content
  under it: `### Invariant` (what the skill tests), `### Question variables`, `### Answer &
  distractor design`, and for Math the `### Solution spec` requirement.
- **Difficulty** → `{INJECT:DIFFICULTY}` — exactly one `### <level>` block (`### Easy`,
  `### Medium`, or `### Hard`) from under the `## Difficulty` heading, the one matching the
  run's difficulty. The other two blocks are never injected, so a "hard" subagent isn't
  anchored by the "easy" definition.
- **Verification rules** → `{INJECT:VERIFICATION_RULES}` — the `## Verification rules` section
  (the yes/no rule table). Verify and refine stages only.

## Orchestrator role — how slots get filled

The skill runs with one **orchestrator** (the main agent) plus per-stage **subagents**
(workers). Subagents never talk to each other; every piece of data flows through the
orchestrator. For each stage it: extracts the pieces it needs from the guideline file and
from the previous stage's staged output, fills the next prompt's `{INJECT:...}` slots,
spawns the subagent, and stages whatever comes back. It also drives the verify → refine →
re-verify loop and the final export.

This works because every staged artifact is in a fixed format (see `output-format.md`), so
the orchestrator extracts by known headings and labels — `## Core`, the matching
`### <level>` block, and `## Verification rules` in a guideline; `## Item N` in a set;
`**Failed rules:**` in a report — not by loose reading.
Staging each stage's output to disk is what gives the orchestrator (and `check_math.py`) a
concrete file to parse. The orchestrator extracts the guideline slices once at intake and
holds them for the whole run, so verify and refine reuse them rather than re-reading.

Where each slot comes from:

| Stage | Slot | Source |
|---|---|---|
| Generate | `SKILL_CORE` | guideline file — the `# …` title line + the whole `## Core` section, sliced by heading |
| | `DIFFICULTY` | guideline file — the one matching `### <level>` block under `## Difficulty` |
| | `REFERENCE_PDF` | the PDF the user mapped to this difficulty at intake |
| | `COUNT` | the run setting (default 10) |
| Verify | `SKILL_CORE`, `DIFFICULTY` | the same guideline slices already extracted for generation |
| | `VERIFICATION_RULES` | guideline file — the `## Verification rules` section, sliced by heading |
| | `QUESTIONS` | path to the staged `generated/<skill>__<difficulty>.md` |
| Refine | `ITEM` | the `## Item N` block pulled from the staged set, for each N the report marked FAIL |
| | `FAILED_RULES` | the verification report — that item's failed rule IDs + the reviewer's reason rows |
| | `SKILL_CORE`, `DIFFICULTY`, `VERIFICATION_RULES` | the same guideline slices, reused |

## 0. Intake

The user uploads 3 PDFs (one skill, at easy/medium/hard, 10 questions each) and says
in their message which PDF is which. There is no categorization step — take the mapping
from what the user said.

Before anything else, **echo the mapping back and wait for confirmation** — e.g.
"Generating 10 each for *linear-equations-in-one-variable* at easy, medium, and hard from
these three files — correct?" This catches a mislabeled upload before it becomes a batch
of wrong-skill questions.

Then load the skill's guideline file. **If it still says `status: PLACEHOLDER`, stop
and tell the user that skill isn't ready** — there are no rules to generate or verify
against.

## 1. Generate — one subagent per difficulty

Spin up three subagents to run in parallel, one per difficulty. Each receives the full assembled
`prompts/generate.md`, which combines **standing** instructions baked into the prompt skeleton
with **injected** run-specific pieces. The complete payload to each subagent is:

Standing (in the prompt skeleton, identical every run):
- the task framing — write `{COUNT}` original SAT items for one skill at one difficulty;
- the distinctness principle (same skill, original content), pointing to
  `references/distinctness.md`;
- the output requirement, pointing to the question-set format in
  `references/output-format.md`.

Injected (per subagent, from the orchestrator):
- `{INJECT:SKILL_CORE}` ← the skill's core design content (invariant, question
  variables, distractor design, and for Math the solution-spec requirement);
- `{INJECT:DIFFICULTY}` ← the one self-labeled difficulty block for this subagent (label
  and definition together); the other two levels are never passed;
- `{INJECT:REFERENCE_PDF}` ← the matching uploaded PDF, which the subagent reads itself —
  for structure, and as the specific items it must not duplicate;
- `{INJECT:COUNT}` ← 10.

Each subagent writes 10 full questions in the standard question-set markdown: all four
options, the correct answer, and an explanation of the correct answer; Math items also
carry the `spec` block.

Stage output to `generated/<skill>__<difficulty>.md`.

## 2. Verify — one independent subagent per difficulty

For each difficulty, assemble `prompts/verify.md`:

- `{INJECT:SKILL_CORE}` + `{INJECT:DIFFICULTY}` — so the checker knows the design and
  the difficulty target it's checking against;
- `{INJECT:VERIFICATION_RULES}` ← the yes/no checks from the guideline;
- `{INJECT:QUESTIONS}` ← the generated set.

The verifier is a **fresh subagent that did not write the questions** — that independence
is the whole point; it checks rather than defends its own work. For Math it runs
`python scripts/check_math.py <set>` and uses that result for the correctness rule rather
than eyeballing arithmetic. It outputs a pass/fail per question — one line per rule with a
reason — in the verification-report format (`output-format.md`), ending each item with a
`Failed rules:` line.

Stage reports to `verified/<skill>__<difficulty>.md`.

A question is **done** when it passes every rule. Any failed rule routes it to refine.

## 3. Refine — failing questions only, failed rules only

For each failing question, assemble `prompts/refine.md`:

- `{INJECT:ITEM}` ← the single failing question;
- `{INJECT:FAILED_RULES}` ← the failed rule IDs plus the verifier's reasons;
- `{INJECT:SKILL_CORE}` + `{INJECT:DIFFICULTY}` + `{INJECT:VERIFICATION_RULES}`.

The refiner makes the lightest change that turns the failed rules green, adjusting
dependent parts only as needed (e.g. if the key changes, fix the explanation and, for
Math, the `spec` block too). It does not touch what already passes. If an item is too
broken to patch, it rebuilds from the guideline. Output is the single corrected item.

**The orchestrator then writes that corrected item back into the set file**
`generated/<skill>__<difficulty>.md`, replacing the old `## Item N` block in place (matched
by item number) with the returned one. This is the step that actually applies the fix: the
set file is the single source the next verify pass and `check_math.py` read, and the one the
export ultimately ships — a corrected item held only in the orchestrator's context, and not
spliced back, would be silently dropped. Refine never appends or renumbers; it overwrites
exactly the `## Item N` it was given, so the set always has 10 items in order.

## 4. Loop

Re-verify (step 2) the **updated** set file — not the original generation and not the
corrected items in isolation. Because every refinement was spliced back in above, the file
holds the current best version of all 10, so the re-run checks exactly what will ship.
Repeat refine ↔ verify until every question passes, capped at **3 cycles**. Anything still
failing after the cap is surfaced to the user, not shipped — don't lower the bar to force a
pass.

## 5. Export

When all three sets pass, stage each one — the fully-refined `generated/<skill>__<difficulty>.md`,
with every corrected item already spliced in (step 3) — to `final/<skill>__<difficulty>.md`.
The final file is just the passing set as it now stands on disk, so the doc is built from the
corrected items, never the original failing ones. Then run `scripts/build_docx.py` **once per
difficulty** — three separate invocations, each over that one difficulty's final file —
producing **three Word docs**, one per difficulty
(easy / medium / hard), each holding that difficulty's 10 full questions. Give each call
its own `--out` path and a `--title` naming the skill and difficulty:

```
python scripts/build_docx.py --out final/<skill>-easy.docx \
    --title "<Skill label> — Easy"   final/<skill>__easy.md
# …and again for medium and hard.
```

The script strips the Math `spec` blocks and lays each item out as a uniform block
(question, options, answer, explanation). Exact layout is in `output-format.md`. Do **not**
pass all three final files in one call — that merges them into a single combined doc, which
is no longer what we want; pass exactly one difficulty's file per call.

## Orchestration notes

- **Context hygiene:** each subagent gets only its slice — one skill, one difficulty,
  the relevant guideline pieces — never the whole job.
- **Continuity:** keep `generated/`, `verified/`, `final/` on disk so any stage can re-run
  without redoing the rest.
- **Parallelism:** the three difficulties run in parallel at both generate and verify.
- **Determinism where it counts:** Math correctness (`check_math.py`) and the Word layout
  (`build_docx.py`) go through scripts, so they're identical every run.
