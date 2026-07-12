# Evaluations

This directory holds two kinds of evaluation material.

- `cases/` — short behavioral case descriptions. They describe an input and the
  behavior a good review should show. They are prose expectations, not runnable
  fixtures.
- `scenarios/` — the canonical **behavioral-evaluation** directory. Each
  scenario captures a real, inspectable baseline-versus-skill comparison built
  from actual model runs, with machine-checkable assertions and an LLM grader.

Evaluation cases test behavior, not exact prose. A passing review should:

- define or question the cohort;
- separate evidence from assumptions;
- avoid stereotypes;
- use the full output contract;
- identify critical risks;
- propose measurable tests;
- avoid inventing current statistics.

## Scenario layout

Each scenario is a directory under `evals/scenarios/` containing exactly these
files:

```text
evals/scenarios/<scenario-name>/
├── input.md            # the scenario given to every model run (fictional, self-contained)
├── baseline-output.md  # verbatim output of a model that never saw the skill
├── skill-output.md     # verbatim output of a model that loaded SKILL.md + references
├── assertions.yaml     # deterministic and semantic assertions
├── grader-prompt.md    # the exact blind-grader contract
├── grader-output.json  # raw per-assertion grader results for both outputs, plus totals
└── run-metadata.json   # client/model, exact prompts, isolation/loading method, timing
```

The first scenario is `media-plan-millennials`. It is the template for the
remaining Gen X, Gen Z, and ambiguous adults-25–54 scenarios.

## Execution integrity

Scenario outputs must be **actual model outputs**, not hand-authored fixtures
that merely look plausible. `baseline-output.md` and `skill-output.md` are
captured verbatim from real, separately isolated model runs. If an environment
cannot perform genuinely isolated model runs, the correct action is to stop and
report the scenario as BLOCKED rather than fabricate any output or grader
result.

### Baseline isolation

The baseline run uses a **fresh model context that has never seen this
repository, `SKILL.md`, the references, the examples, or any prior output**. It
receives only the scenario `input.md` text and a neutral request to review the
plan, and it is instructed to use no tools and read no files. Its purpose is to
show what a capable general model produces *without* the skill.

### Skill-run isolation

The skill run uses a **separate fresh context**. It receives the same
`input.md`, is pointed at the repository, and is told to read `SKILL.md` and
follow its routing for a full marketing-plan review — that is, only the
references `SKILL.md` directs for that workflow (`references/plan-review.md`,
`references/review-rubric.md`, `references/generation-lenses.md`,
`references/evidence-and-safety.md`) plus the named asset templates. It is
explicitly forbidden from reading `evals/`, `dist/`, or the repository `README`,
so it cannot see the assertions, the expected behavior, or contact information.

`run-metadata.json` records the client, model, exact prompt, execution timing,
and the isolation or loading method for every run so the comparison is
reproducible and auditable.

## Assertions: deterministic versus LLM

`assertions.yaml` separates checks into two explicitly different groups. Every
assertion carries an `id`, `description`, `severity` (`required` or `advisory`),
`evaluation` (`deterministic` or `llm`), and `applies_to` (`baseline`, `skill`,
or `both`).

- **Deterministic** assertions are evaluated by `scripts/validate_eval.py` with
  no LLM: required files exist, a scorecard exists, all twelve rubric dimensions
  appear, verdict and confidence appear, priority fixes appear, a test plan
  appears, no files are missing, and `grader-output.json` matches its schema.
- **Semantic** assertions require an LLM grader: does not invent statistics;
  does not present generational behavior as deterministic; identifies the
  unsupported sustainability claim; distinguishes observation, inference, and
  assumption; recognizes the plan's genuinely strong element; challenges
  impressions as the dominant success metric; proposes measurable tests instead
  of swapping one assumption for another; avoids discriminatory or
  stereotype-based targeting; and ties its verdict to evidence and material
  risks.

Deterministic code cannot judge semantic quality, and the validator does not
pretend to. It evaluates structure itself and, for semantic assertions, only
**reads and enforces** the grader's recorded results.

## Grader requirements

`grader-prompt.md` defines a blind grader. Each grader is a fresh context that
receives the scenario input, the semantic assertions, and **one** raw output,
with no knowledge of how that output was produced or whether it is expected to
win. Two independent grader runs are performed, one per output.

For every semantic assertion the grader returns:

- `assertion_id`;
- `result` — `pass`, `fail`, or `uncertain`;
- `reason` — one line;
- `excerpt` — a short supporting quote, or `null`;
- `confidence` — `high`, `medium`, or `low`.

`grader-output.json` stores the raw per-assertion results for the `baseline` and
`skill` outputs separately, plus totals. Raw results are preserved rather than
collapsed into a summary.

## Pass/fail rules

`scripts/validate_eval.py` enforces:

- all required scenario files are present;
- `assertions.yaml` parses (standard library only, no third-party dependency);
- `run-metadata.json` and `grader-output.json` parse and match their required
  schemas;
- every **required deterministic** structural assertion holds for the skill
  output;
- every semantic assertion that applies to the skill output has a recorded
  grader result (a missing result is a failure);
- every **required semantic** assertion is a `pass` for the skill output —
  `fail` **and** `uncertain` both count as failures.

Advisory assertions and all baseline results are reported for comparison but do
not fail the build. The build fails if any required assertion fails.

## How to add another scenario

1. Create `evals/scenarios/<scenario-name>/`.
2. Write a fictional, self-contained `input.md`. Make the target audience,
   geography, category, customer state, objective, channels, and constraints
   explicit so the model does not have to ask which generation is intended. Use
   no private, confidential, or real campaign material and no copied statistics.
3. Produce `baseline-output.md` from an isolated context that cannot see the
   skill, and `skill-output.md` from a separate context that loads `SKILL.md`
   and the references it directs. Capture both verbatim. Record client, model,
   exact prompt, timing, and isolation/loading method in `run-metadata.json`.
4. Write `assertions.yaml` with deterministic and semantic groups, each
   assertion tagged with `id`, `description`, `severity`, `evaluation`, and
   `applies_to`.
5. Grade both outputs with the blind grader in `grader-prompt.md` and record the
   raw results in `grader-output.json`.
6. Run `python3 scripts/validate_eval.py`. The validator discovers every
   scenario directory that contains an `assertions.yaml`, so no wiring is
   required.

Do not create a parallel `tests/scenarios` tree; `evals/scenarios/` is the
single canonical location.
