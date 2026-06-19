<!--
GUIDELINE TEMPLATE — Reading & Writing skill. One file per skill is the single source
of truth for BOTH generation and verification (see references/workflow.md). The orchestrator
slices this file into three pieces, so KEEP these headings exactly:
  - SKILL_CORE      = the `## Core` section (identity + design, incl. the passage spec)
  - DIFFICULTY         = one `### <level>` block under `## Difficulty`
  - VERIFICATION_RULES = the `## Verification rules` section
Fill in every TODO below.
When the file is complete, change `status` from PLACEHOLDER to `ready`.
-->

# Reading & Writing · Information and Ideas · Inferences

## Core

- **subject:** reading-writing
- **topic:** information-and-ideas
- **skill:** inferences
- **status:** PLACEHOLDER — rules not yet written

### Invariant — what this skill tests

The constant across every item: the exact reading/writing demand, regardless of passage
topic. This is what "functionally equivalent to a College Board item" means.

> TODO: 2–4 sentences. e.g. for *Words in Context*: "Choose the most logical and precise word
> or phrase for a blank, based strictly on textual evidence — not on which word is most
> sophisticated."

### Passage spec

The passage is original content the generator writes. Hold it to SAT norms.

| Attribute | Setting |
|---|---|
| Length | TODO (digital SAT passages run ~25–150 words; set a tight range) |
| Subject areas | TODO (literature, history/social studies, the humanities, science) |
| Register / complexity | TODO (grade-appropriate; a readability band if you have one) |
| Special structure | TODO (e.g. a figure/table for quantitative evidence; a text pair for cross-text) |
| Sourcing | Fully original — no excerpt or close paraphrase of real text or any reference item. |

### Question variables

| Variable | Allowed range / options | Notes |
|---|---|---|
| Passage topic | TODO | vary widely across a set |
| Stem phrasing | TODO (canonical phrasings for this skill) | |
| What is asked | TODO | |
| Options | 4 single-select | |

### Answer & distractor design

- **Correct-answer rule:** TODO — exactly one option fully supported by the passage,
  defensible from the text alone with no outside knowledge.
- **Distractor traps:** TODO — name the classic traps (e.g. "true but not the central idea",
  "uses a passage word in the wrong sense", "grammatically tempting but creates a comma
  splice"). Each distractor embodies one named trap.
- **Option distinctness:** all four options meaningfully distinct.

## Difficulty

What moves an item between levels *for this skill*. Same skill at every level — only the
load changes. Each block is injected on its own, so write each to stand alone.

### Easy
> TODO — e.g. answer strongly signposted, common vocabulary, short passage.

### Medium
> TODO — e.g. requires synthesizing two sentences, moderate vocabulary, one tempting distractor.

### Hard
> TODO — e.g. abstract passage, subtle logical relationship, several close distractors,
> low-frequency vocabulary.

## Verification rules

Checked by the verifier; an item passes only if **all** pass. Each references the sections
above, so they apply as soon as Core and Difficulty are filled in. Adjust per skill only
if needed.

| ID | Rule (passes when…) |
|---|---|
| R-1 | The item tests the Invariant above and nothing else. |
| R-2 | The passage meets the passage spec (length, subject, structure, originality). |
| R-3 | The item is calibrated to the requested difficulty (its `### <level>` block). |
| R-4 | Exactly one option is defensible from the passage alone — no outside knowledge needed. |
| R-5 | Every distractor maps to a named trap in the distractor design. |
| R-6 | The stem uses a canonical phrasing for this skill. |
| R-7 | The explanation cites the textual evidence for the keyed answer. |
| R-8 | Distinctness: passage and question are original (see `distinctness.md`). |
| R-9 | The item is self-contained and unambiguous — exactly one defensible answer. |
| R-10 | Each wrong-answer explanation accurately and precisely states why that option is incorrect, consistent with its distractor trap. |
