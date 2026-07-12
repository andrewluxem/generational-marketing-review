# Grader Prompt

This file defines the exact, machine-substitutable prompt template used to grade
a single review. The runtime grader prompt is produced by extracting the fenced
`text` template below and substituting three placeholders:

- `{{SCENARIO}}` — the verbatim contents of `input.md`;
- `{{ASSERTIONS}}` — the numbered list of **semantic** assertions from
  `assertions.yaml`, one line per assertion, formatted as `N. [id] description`;
- `{{REVIEW}}` — the verbatim review being graded.

Both the run harness and `scripts/validate_eval.py` extract this same fenced
block and substitute identically (via the shared helpers in `validate_eval.py`),
so the validator can regenerate the exact runtime prompt and confirm it matches
what was sent (and that the grader results are bound to the current scenario,
assertions, and output).

## Isolation and blindness

Each grader is a fresh, fully isolated model context (no global or repository
`CLAUDE.md`/`AGENTS.md`, no skills, hooks, MCP, memories, agents, prior
conversations, or tools). It receives only the scenario input, the semantic
assertions, and **one** unlabeled review. It is not told whether the review is
the baseline or the skill-enabled output, and it never sees the other review,
the other grader's results, or any expected outcome. Two independent grader runs
are performed, one per review.

Required assertions treat `uncertain` as a failure; that gating is applied
downstream by `scripts/validate_eval.py`, so the grader itself reserves
`uncertain` for cases where the review genuinely does not give enough to decide.

## Template

```text
You are an impartial evaluator of a marketing-asset review. The asset under
review is a single lifecycle email. You are grading ONE review of that email.
You do not know how the review was produced or whether it is expected to score
well or poorly. Judge only what the review text actually says. Do not reward a
review for length or format; reward it only for substantively satisfying each
assertion.

SCENARIO THE REVIEW WAS RESPONDING TO:
<scenario>
{{SCENARIO}}
</scenario>

THE REVIEW TO GRADE:
<review>
{{REVIEW}}
</review>

ASSERTIONS TO EVALUATE:
{{ASSERTIONS}}

For EVERY assertion, produce one object with these fields:
- assertion_id: the bracketed id, exactly as written
- result: "pass", "fail", or "uncertain"
- reason: one short line
- excerpt: a short verbatim quote from the review that supports your judgment,
  or null if none applies
- confidence: "high", "medium", or "low"

Use "uncertain" only when the review genuinely does not give you enough to
decide. Return exactly one result for every assertion in the list, in order, and
do not add, drop, or rename any assertion id.

Output ONLY a single JSON object and nothing else. No prose, no markdown, no code
fences. The object must have exactly this shape:
{"results": [{"assertion_id": "...", "result": "...", "reason": "...", "excerpt": "..." , "confidence": "..."}]}
```

## Recorded binding

`grader-output.json` records, for each of the `baseline` and `skill` result sets,
the raw per-assertion results and totals plus the SHA-256 of the graded output,
the input, the assertions file, and this grader-prompt file. `run-metadata.json`
records the exact runtime grader prompt and its SHA-256 for each grader run. The
validator recomputes all of these and fails if any artifact changed after
grading or if a result set is bound to a different output.
