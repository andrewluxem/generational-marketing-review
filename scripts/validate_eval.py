#!/usr/bin/env python3
"""Deterministic validator for behavioral evaluation scenarios.

This script performs ONLY deterministic checks and cryptographic binding:

- required scenario files exist;
- assertions.yaml parses (small standard-library parser, no third-party dep);
- run-metadata.json and grader-output.json parse and match their schemas;
- every recorded artifact SHA-256 (inputs, outputs, prompts) matches the file on
  disk, so nothing changed after grading;
- each grader result set is bound to the exact graded output, input, assertions,
  and grader prompt, and the runtime grader prompt regenerates exactly from
  grader-prompt.md (results cannot refer to a different or edited output);
- required structural assertions hold for the skill output, using canonical
  rubric-dimension identifiers from assertions.yaml (matchers are not tuned to
  any specific output);
- each grader result set covers the semantic assertions exactly once with no
  duplicate, missing, or extra ids;
- totals are recomputed from raw results rather than trusted;
- required semantic assertions are a PASS for the skill output, treating a
  missing or "uncertain" result as a failure.

It deliberately does NOT judge semantic quality; that judgment belongs to the
LLM grader and is only read and enforced here. Standard library only. Exit 0 on
success, 1 on any required failure.

The helper functions (parse_block_yaml, semantic_assertions,
format_semantic_assertions, extract_grader_template, build_grader_prompt, the
hashing and normalization helpers) are imported by the run harness so that the
runtime grader prompt and the validator's regenerated prompt are identical by
construction.
"""

from pathlib import Path
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS_DIR = ROOT / "evals" / "scenarios"

REQUIRED_FILES = [
    "input.md",
    "baseline-output.md",
    "skill-output.md",
    "assertions.yaml",
    "grader-prompt.md",
    "grader-output.json",
    "run-metadata.json",
]

# Files whose SHA-256 must be recorded in run-metadata.artifact_hashes.
HASHED_ARTIFACTS = [
    "input.md",
    "baseline-output.md",
    "skill-output.md",
    "assertions.yaml",
    "grader-prompt.md",
]

RESULT_VALUES = {"pass", "fail", "uncertain"}
CONFIDENCE_VALUES = {"high", "medium", "low"}
SEVERITY_VALUES = {"required", "advisory"}
EVALUATION_VALUES = {"deterministic", "llm"}
APPLIES_VALUES = {"baseline", "skill", "both"}

REQUIRED_METADATA_FIELDS = [
    "scenario",
    "runs.baseline.model",
    "runs.baseline.isolation_method",
    "runs.baseline.exact_prompt",
    "runs.baseline.exact_prompt_sha256",
    "runs.skill.model",
    "runs.skill.loading_method",
    "runs.skill.exact_prompt",
    "runs.skill.exact_prompt_sha256",
    "grader.model",
    "grader.method",
]

GRADER_RESULT_KEYS = ("assertion_id", "result", "reason", "excerpt", "confidence")
GRADER_SET_KEYS = (
    "output_file",
    "graded_output_sha256",
    "input_sha256",
    "assertions_sha256",
    "grader_prompt_sha256",
    "grader_model",
    "grader_client",
    "results",
    "totals",
)

# Normalization stopwords for canonical dimension matching. Dropping conjunctions
# and articles is a general, principled rule applied identically to the canonical
# names and the output text; it is not tuned to any particular output's wording.
STOPWORDS = {"and", "the", "a", "an", "of", "for", "to"}


# --------------------------------------------------------------------------- #
# Hashing helpers
# --------------------------------------------------------------------------- #
def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path):
    return sha256_bytes(Path(path).read_bytes())


# --------------------------------------------------------------------------- #
# Minimal block-YAML parser (a controlled subset, not general YAML)
# --------------------------------------------------------------------------- #
def _coerce(value):
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    return value


def _split_pair(text):
    idx = text.find(":")
    if idx == -1:
        return text.strip(), ""
    return text[:idx].strip(), _coerce(text[idx + 1:])


def parse_block_yaml(text):
    """Parse the constrained block-YAML grammar used by assertions.yaml.

    Supports top-level "key: value" scalars, top-level "key:" introducing a
    block sequence, sequence items that are scalars ("- value") or mappings
    ("- key: value" with deeper-indented "key: value" continuation lines).
    Full-line comments and blank lines are ignored. Not a general parser.
    """
    root = {}
    lines = text.splitlines()
    n = len(lines)
    i = 0
    while i < n:
        raw = lines[i]
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if indent != 0:
            i += 1
            continue
        if stripped.endswith(":"):
            key = stripped[:-1].strip()
            seq = []
            root[key] = seq
            i += 1
            while i < n:
                r2 = lines[i]
                s2 = r2.strip()
                if not s2 or s2.startswith("#"):
                    i += 1
                    continue
                ind2 = len(r2) - len(r2.lstrip(" "))
                if ind2 == 0:
                    break
                if s2.startswith("- "):
                    rem = s2[2:].strip()
                    if ":" in rem:
                        item = {}
                        k, v = _split_pair(rem)
                        item[k] = v
                        i += 1
                        while i < n:
                            r3 = lines[i]
                            s3 = r3.strip()
                            if not s3 or s3.startswith("#"):
                                i += 1
                                continue
                            ind3 = len(r3) - len(r3.lstrip(" "))
                            if ind3 <= ind2:
                                break
                            k3, v3 = _split_pair(s3)
                            item[k3] = v3
                            i += 1
                        seq.append(item)
                    else:
                        seq.append(_coerce(rem))
                        i += 1
                else:
                    i += 1
            continue
        key, value = _split_pair(stripped)
        root[key] = value
        i += 1
    return root


def load_assertions(scenario_dir):
    return parse_block_yaml((Path(scenario_dir) / "assertions.yaml").read_text("utf-8"))


def semantic_assertions(assertions):
    return [a for a in assertions.get("semantic", []) if isinstance(a, dict)]


def format_semantic_assertions(assertions):
    """Deterministic numbered list handed to the grader. Shared by harness."""
    lines = []
    for idx, a in enumerate(semantic_assertions(assertions), start=1):
        lines.append(f"{idx}. [{a.get('id')}] {a.get('description')}")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Grader prompt construction (shared by harness and validator)
# --------------------------------------------------------------------------- #
def extract_grader_template(grader_prompt_md):
    """Extract the first fenced ```text block from grader-prompt.md, verbatim."""
    marker = "```text\n"
    start = grader_prompt_md.find(marker)
    if start == -1:
        raise ValueError("grader-prompt.md has no fenced text template block")
    start += len(marker)
    end = grader_prompt_md.find("\n```", start)
    if end == -1:
        raise ValueError("grader-prompt.md template block is not closed")
    return grader_prompt_md[start:end]


def build_grader_prompt(template, scenario, assertions_text, review):
    mapping = {"SCENARIO": scenario, "ASSERTIONS": assertions_text, "REVIEW": review}
    return re.sub(
        r"\{\{(SCENARIO|ASSERTIONS|REVIEW)\}\}",
        lambda m: mapping[m.group(1)],
        template,
    )


def regenerate_grader_prompt(scenario_dir, assertions, review_text):
    grader_md = (Path(scenario_dir) / "grader-prompt.md").read_text("utf-8")
    template = extract_grader_template(grader_md)
    scenario = (Path(scenario_dir) / "input.md").read_text("utf-8")
    return build_grader_prompt(
        template, scenario, format_semantic_assertions(assertions), review_text
    )


# --------------------------------------------------------------------------- #
# Canonical dimension normalization
# --------------------------------------------------------------------------- #
def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    tokens = [t for t in text.split() if t and t not in STOPWORDS]
    return " ".join(tokens)


def dimension_present(canonical_name, normalized_output):
    needle = normalize_text(canonical_name)
    return needle in normalized_output


# --------------------------------------------------------------------------- #
# Report accumulator
# --------------------------------------------------------------------------- #
class Report:
    def __init__(self):
        self.required_failures = []
        self.advisory_warnings = []
        self.lines = []

    def ok(self, msg):
        self.lines.append(f"  PASS  {msg}")

    def fail(self, msg):
        self.lines.append(f"  FAIL  {msg}")
        self.required_failures.append(msg)

    def warn(self, msg):
        self.lines.append(f"  WARN  {msg}")
        self.advisory_warnings.append(msg)

    def note(self, msg):
        self.lines.append(f"        {msg}")


def dotted_get(obj, path):
    cur = obj
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None, False
        cur = cur[part]
    return cur, True


# --------------------------------------------------------------------------- #
# Structural checks against the skill output
# --------------------------------------------------------------------------- #
def structural_check(assertion_id, skill_text, dimensions):
    lower = skill_text.lower()
    if assertion_id == "verdict-present":
        fit_labels = ["strong fit", "promising but needs revision", "weak fit",
                      "insufficient evidence"]
        ok = ("verdict" in lower) or any(f in lower for f in fit_labels) or ("fit:" in lower)
        return ok, "verdict / fit label"
    if assertion_id == "confidence-present":
        return "confidence" in lower, "confidence"
    if assertion_id == "audience-definition-check-present":
        return ("audience-definition check" in lower
                or "audience definition check" in lower), "audience-definition check"
    if assertion_id == "scorecard-present":
        return "scorecard" in lower, "scorecard"
    if assertion_id == "twelve-dimensions-present":
        normalized = normalize_text(skill_text)
        missing = [d for d in dimensions if not dimension_present(d, normalized)]
        if missing:
            return False, "missing dimensions: " + "; ".join(missing)
        return True, f"all {len(dimensions)} canonical rubric dimensions present"
    if assertion_id == "priority-fixes-present":
        return ("priority fixes" in lower or "priority fix" in lower), "priority fixes"
    if assertion_id == "test-plan-present":
        return "test plan" in lower, "test plan"
    if assertion_id == "final-recommendation-present":
        return "final recommendation" in lower, "final recommendation"
    if assertion_id == "stereotype-flags-present":
        return "stereotype" in lower, "stereotype flags"
    if assertion_id == "evidence-register-present":
        return "evidence register" in lower, "evidence register"
    return None, "no structural check implemented"


# --------------------------------------------------------------------------- #
# Schema validators
# --------------------------------------------------------------------------- #
def validate_metadata_schema(report, meta):
    ok = True
    for path in REQUIRED_METADATA_FIELDS:
        value, found = dotted_get(meta, path)
        if not found:
            report.fail(f"run-metadata.json missing field: {path}")
            ok = False
        elif not isinstance(value, str) or not value.strip():
            report.fail(f"run-metadata.json field empty or not a string: {path}")
            ok = False
    ah = meta.get("artifact_hashes")
    if not isinstance(ah, dict):
        report.fail("run-metadata.json missing artifact_hashes object")
        ok = False
    else:
        for name in HASHED_ARTIFACTS:
            if not isinstance(ah.get(name), str) or not ah.get(name):
                report.fail(f"run-metadata.json artifact_hashes missing: {name}")
                ok = False
    if ok:
        report.ok("run-metadata.json has all required fields")
    return ok


def validate_result_entry(report, side, entry):
    ok = True
    if not isinstance(entry, dict):
        report.fail(f"grader-output.json {side} result is not an object")
        return False
    for key in GRADER_RESULT_KEYS:
        if key not in entry:
            report.fail(f"grader-output.json {side} result missing key: {key}")
            ok = False
    if entry.get("result") not in RESULT_VALUES:
        report.fail(f"grader-output.json {side} invalid result: {entry.get('result')!r}")
        ok = False
    if entry.get("confidence") not in CONFIDENCE_VALUES:
        report.fail(f"grader-output.json {side} invalid confidence: {entry.get('confidence')!r}")
        ok = False
    excerpt = entry.get("excerpt", "")
    if not (excerpt is None or isinstance(excerpt, str)):
        report.fail(f"grader-output.json {side} excerpt must be string or null")
        ok = False
    return ok


def validate_grader_schema(report, grader):
    ok = True
    if not isinstance(grader, dict):
        report.fail("grader-output.json is not an object")
        return False
    for side in ("baseline", "skill"):
        block = grader.get(side)
        if not isinstance(block, dict):
            report.fail(f"grader-output.json missing object: {side}")
            ok = False
            continue
        for key in GRADER_SET_KEYS:
            if key not in block:
                report.fail(f"grader-output.json {side} missing key: {key}")
                ok = False
        if isinstance(block.get("results"), list):
            for entry in block["results"]:
                if not validate_result_entry(report, side, entry):
                    ok = False
        else:
            report.fail(f"grader-output.json {side}.results must be a list")
            ok = False
        if not isinstance(block.get("totals"), dict):
            report.fail(f"grader-output.json {side}.totals must be an object")
            ok = False
    if "totals" not in grader:
        report.fail("grader-output.json missing top-level totals")
        ok = False
    if ok:
        report.ok("grader-output.json matches the required grader-result schema")
    return ok


# --------------------------------------------------------------------------- #
# Cryptographic binding
# --------------------------------------------------------------------------- #
def verify_hash_binding(report, scenario_dir, meta, grader, assertions):
    scenario_dir = Path(scenario_dir)
    disk = {name: sha256_file(scenario_dir / name) for name in HASHED_ARTIFACTS}

    # artifact-hashes-bound: run-metadata hashes match the files on disk.
    ah_ok = True
    ah = meta.get("artifact_hashes", {})
    for name in HASHED_ARTIFACTS:
        recorded = ah.get(name)
        if recorded != disk[name]:
            report.fail(f"[det/required] artifact-hashes-bound: {name} hash mismatch "
                        f"(recorded {str(recorded)[:12]}..., disk {disk[name][:12]}...)")
            ah_ok = False
    # exact-prompt hashes in run-metadata match the recorded prompt text.
    for run in ("baseline", "skill"):
        p, _ = dotted_get(meta, f"runs.{run}.exact_prompt")
        h, _ = dotted_get(meta, f"runs.{run}.exact_prompt_sha256")
        if isinstance(p, str) and sha256_text(p) != h:
            report.fail(f"[det/required] artifact-hashes-bound: runs.{run}.exact_prompt "
                        "hash does not match its text")
            ah_ok = False
    if ah_ok:
        report.ok("[det/required] artifact-hashes-bound: all recorded hashes match disk")

    # grader-binding-valid: each grader result set bound to the exact artifacts.
    gb_ok = True
    expected = {
        "baseline": disk["baseline-output.md"],
        "skill": disk["skill-output.md"],
    }
    for side in ("baseline", "skill"):
        block = grader.get(side, {})
        if block.get("graded_output_sha256") != expected[side]:
            report.fail(f"[det/required] grader-binding-valid: {side} results are bound to a "
                        f"different output than {side}-output.md")
            gb_ok = False
        if block.get("input_sha256") != disk["input.md"]:
            report.fail(f"[det/required] grader-binding-valid: {side} input_sha256 does not "
                        "match input.md (input changed after grading)")
            gb_ok = False
        if block.get("assertions_sha256") != disk["assertions.yaml"]:
            report.fail(f"[det/required] grader-binding-valid: {side} assertions_sha256 does not "
                        "match assertions.yaml (assertions changed after grading)")
            gb_ok = False
        if block.get("grader_prompt_sha256") != disk["grader-prompt.md"]:
            report.fail(f"[det/required] grader-binding-valid: {side} grader_prompt_sha256 does not "
                        "match grader-prompt.md (grader prompt changed after grading)")
            gb_ok = False

    # Runtime grader prompt must regenerate exactly from grader-prompt.md.
    output_text = {
        "baseline": (scenario_dir / "baseline-output.md").read_text("utf-8"),
        "skill": (scenario_dir / "skill-output.md").read_text("utf-8"),
    }
    grader_prompts, _ = dotted_get(meta, "grader.prompts")
    for side in ("baseline", "skill"):
        try:
            regenerated = regenerate_grader_prompt(scenario_dir, assertions, output_text[side])
        except Exception as exc:  # noqa: BLE001
            report.fail(f"[det/required] grader-binding-valid: cannot regenerate {side} grader "
                        f"prompt: {exc}")
            gb_ok = False
            continue
        recorded = None
        if isinstance(grader_prompts, dict) and isinstance(grader_prompts.get(side), dict):
            recorded = grader_prompts[side].get("exact_prompt")
            recorded_hash = grader_prompts[side].get("exact_prompt_sha256")
            if recorded_hash != sha256_text(recorded or ""):
                report.fail(f"[det/required] grader-binding-valid: grader.prompts.{side} hash "
                            "does not match its recorded text")
                gb_ok = False
        if recorded is None:
            report.fail(f"[det/required] grader-binding-valid: run-metadata.json missing "
                        f"grader.prompts.{side}.exact_prompt")
            gb_ok = False
        elif recorded != regenerated:
            report.fail(f"[det/required] grader-binding-valid: recorded {side} grader prompt does "
                        "not correspond to grader-prompt.md substituted with the current scenario, "
                        "assertions, and output")
            gb_ok = False
    if gb_ok:
        report.ok("[det/required] grader-binding-valid: grader results bound to the exact "
                  "output, input, assertions, and grader prompt")
    return ah_ok and gb_ok


# --------------------------------------------------------------------------- #
# Result-set integrity: duplicate / missing / extra ids, totals
# --------------------------------------------------------------------------- #
def results_by_id(report, side, block, expected_ids):
    entries = block.get("results", [])
    seen = {}
    dupes = set()
    for entry in entries:
        aid = entry.get("assertion_id") if isinstance(entry, dict) else None
        if aid in seen:
            dupes.add(aid)
        seen[aid] = entry
    ids = [e.get("assertion_id") for e in entries if isinstance(e, dict)]
    idset = set(ids)
    if dupes:
        report.fail(f"grader-output.json {side}: duplicate assertion ids: {sorted(dupes)}")
    missing = expected_ids - idset
    extra = idset - expected_ids
    if missing:
        report.fail(f"grader-output.json {side}: missing assertion results: {sorted(missing)}")
    if extra:
        report.fail(f"grader-output.json {side}: extra assertion ids: {sorted(extra)}")
    if not dupes and not missing and not extra:
        report.ok(f"grader-output.json {side}: assertion ids complete, unique, no extras")
    return seen


def verify_totals(report, side, block):
    counts = {"pass": 0, "fail": 0, "uncertain": 0}
    for entry in block.get("results", []):
        r = entry.get("result") if isinstance(entry, dict) else None
        if r in counts:
            counts[r] += 1
    counts["total"] = sum(counts[k] for k in ("pass", "fail", "uncertain"))
    stored = block.get("totals", {})
    recomputed = dict(counts)
    for key, val in recomputed.items():
        if stored.get(key) != val:
            report.fail(f"grader-output.json {side}.totals[{key}] is {stored.get(key)}, "
                        f"recomputed {val}")
            return recomputed, False
    report.ok(f"grader-output.json {side}.totals match recomputed values {recomputed}")
    return recomputed, True


# --------------------------------------------------------------------------- #
# Scenario validation
# --------------------------------------------------------------------------- #
def validate_scenario(scenario_dir):
    scenario_dir = Path(scenario_dir)
    report = Report()
    report.note(f"scenario: {scenario_dir.name}")

    missing_files = [f for f in REQUIRED_FILES if not (scenario_dir / f).is_file()]
    if missing_files:
        for f in missing_files:
            report.fail(f"[det/required] files-present: missing required file: {f}")
        return report
    report.ok("[det/required] files-present: all required scenario files present")

    try:
        assertions = load_assertions(scenario_dir)
    except Exception as exc:  # noqa: BLE001
        report.fail(f"assertions.yaml failed to parse: {exc}")
        return report

    deterministic = [a for a in assertions.get("deterministic", []) if isinstance(a, dict)]
    semantic = semantic_assertions(assertions)
    dimensions = [d for d in assertions.get("rubric_dimensions", []) if isinstance(d, str)]
    if not deterministic:
        report.fail("assertions.yaml has no deterministic assertions")
    if not semantic:
        report.fail("assertions.yaml has no semantic assertions")
    if len(dimensions) != 12:
        report.fail(f"assertions.yaml rubric_dimensions must list 12 dimensions, found {len(dimensions)}")

    # applies_to and field integrity for every assertion.
    for a in deterministic + semantic:
        for field in ("id", "description", "severity", "evaluation", "applies_to"):
            if field not in a:
                report.fail(f"assertion missing field '{field}': {a}")
        if a.get("severity") not in SEVERITY_VALUES:
            report.fail(f"assertion {a.get('id')} invalid severity: {a.get('severity')}")
        if a.get("evaluation") not in EVALUATION_VALUES:
            report.fail(f"assertion {a.get('id')} invalid evaluation: {a.get('evaluation')}")
        if a.get("applies_to") not in APPLIES_VALUES:
            report.fail(f"assertion {a.get('id')} invalid applies_to: {a.get('applies_to')}")
    if not report.required_failures:
        report.ok(f"assertions.yaml parsed: {len(deterministic)} deterministic, "
                  f"{len(semantic)} semantic, {len(dimensions)} dimensions")

    # JSON artifacts.
    try:
        meta = json.loads((scenario_dir / "run-metadata.json").read_text("utf-8"))
    except Exception as exc:  # noqa: BLE001
        report.fail(f"run-metadata.json is not valid JSON: {exc}")
        meta = None
    try:
        grader = json.loads((scenario_dir / "grader-output.json").read_text("utf-8"))
    except Exception as exc:  # noqa: BLE001
        report.fail(f"grader-output.json is not valid JSON: {exc}")
        grader = None

    meta_ok = validate_metadata_schema(report, meta) if meta is not None else False
    grader_ok = validate_grader_schema(report, grader) if grader is not None else False

    # Cryptographic binding (needs both artifacts + assertions).
    if meta is not None and grader is not None:
        verify_hash_binding(report, scenario_dir, meta, grader, assertions)

    # Structural (deterministic) assertions on the skill output.
    skill_text = (scenario_dir / "skill-output.md").read_text("utf-8")
    handled = {"files-present", "run-metadata-valid", "grader-output-schema-valid",
               "artifact-hashes-bound", "grader-binding-valid"}
    for a in deterministic:
        aid = a.get("id")
        severity = a.get("severity")
        if aid in handled:
            continue
        if a.get("applies_to") not in ("skill", "both"):
            continue
        ok, detail = structural_check(aid, skill_text, dimensions)
        if ok is None:
            report.warn(f"[det/{severity}] {aid}: {detail}")
        elif ok:
            report.ok(f"[det/{severity}] {aid}: {detail}")
        elif severity == "required":
            report.fail(f"[det/required] {aid}: NOT FOUND ({detail})")
        else:
            report.warn(f"[det/advisory] {aid}: not found ({detail})")

    # Semantic result-set integrity and gating.
    if grader is not None and grader_ok:
        semantic_ids = {a.get("id") for a in semantic}
        # Both graders are handed all semantic assertions; both sets cover them.
        baseline_map = results_by_id(report, "baseline", grader.get("baseline", {}), semantic_ids)
        skill_map = results_by_id(report, "skill", grader.get("skill", {}), semantic_ids)
        verify_totals(report, "baseline", grader.get("baseline", {}))
        verify_totals(report, "skill", grader.get("skill", {}))

        for a in semantic:
            aid = a.get("id")
            severity = a.get("severity")
            applies = a.get("applies_to")
            if aid in baseline_map and isinstance(baseline_map[aid], dict):
                report.note(f"[baseline] {aid}: {baseline_map[aid].get('result')}")
            if applies not in ("skill", "both"):
                continue
            entry = skill_map.get(aid)
            if not isinstance(entry, dict):
                report.fail(f"[llm/{severity}] {aid}: no grader result for skill output")
                continue
            result = entry.get("result")
            if result == "pass":
                report.ok(f"[llm/{severity}] {aid}: pass")
            elif severity == "required":
                report.fail(f"[llm/required] {aid}: {result} (required must pass; uncertain counts as fail)")
            else:
                report.warn(f"[llm/advisory] {aid}: {result}")

    return report


def main():
    if not SCENARIOS_DIR.is_dir():
        print(f"No scenarios directory at {SCENARIOS_DIR.relative_to(ROOT)}")
        return 1
    scenario_dirs = sorted(
        d for d in SCENARIOS_DIR.iterdir()
        if d.is_dir() and (d / "assertions.yaml").is_file()
    )
    if not scenario_dirs:
        print(f"No scenarios found under {SCENARIOS_DIR.relative_to(ROOT)}")
        return 1

    total_required = 0
    total_advisory = 0
    print("Eval validation")
    print("=" * 64)
    for scenario_dir in scenario_dirs:
        report = validate_scenario(scenario_dir)
        print(f"\n[{scenario_dir.name}]")
        for line in report.lines:
            print(line)
        total_required += len(report.required_failures)
        total_advisory += len(report.advisory_warnings)

    print("\n" + "=" * 64)
    print(f"Scenarios checked : {len(scenario_dirs)}")
    print(f"Required failures : {total_required}")
    print(f"Advisory warnings : {total_advisory}")
    if total_required:
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
