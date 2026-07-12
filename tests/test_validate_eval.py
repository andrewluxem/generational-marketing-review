#!/usr/bin/env python3
"""Standard-library unit tests for scripts/validate_eval.py.

Each test builds a hermetic, self-consistent scenario in a temp directory using
the validator's own hashing/prompt helpers, then either asserts it passes or
mutates exactly one thing and asserts the specific required failure. No network,
no third-party dependencies, and no tests/scenarios/ tree is created.
"""
import contextlib
import copy
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("ve", str(REPO / "scripts" / "validate_eval.py"))
ve = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ve)

DIMENSIONS = [
    "Audience definition", "Customer need and context", "Value proposition",
    "Message and tone", "Creative and format", "Channel and platform fit",
    "Trust and proof", "Offer and purchase friction",
    "Customer experience and fulfillment",
    "Inclusion, accessibility, privacy, and ethics",
    "Measurement and experimentation", "Evidence quality",
]

SEMANTIC = [
    ("sem-req-both", "required", "both"),
    ("sem-req-skill", "required", "skill"),
    ("sem-adv-both", "advisory", "both"),
]

INPUT_MD = "# Tiny scenario\n\nReview this fictional plan for its audience.\n"

GRADER_PROMPT_MD = (
    "# Grader Prompt\n\n"
    "```text\n"
    "Grade ONE review.\n\n"
    "SCENARIO:\n<scenario>\n{{SCENARIO}}\n</scenario>\n\n"
    "REVIEW:\n<review>\n{{REVIEW}}\n</review>\n\n"
    "ASSERTIONS:\n{{ASSERTIONS}}\n\n"
    "Return only JSON {\"results\": [...]}.\n"
    "```\n"
)


def assertions_yaml(extra_det=()):
    lines = ["version: 2", "scenario: unit-fixture", "", "rubric_dimensions:"]
    for d in DIMENSIONS:
        lines.append(f"  - {d}")
    lines += ["", "deterministic:"]
    det = [
        ("files-present", "required", "both"),
        ("run-metadata-valid", "required", "both"),
        ("grader-output-schema-valid", "required", "both"),
        ("artifact-hashes-bound", "required", "both"),
        ("grader-binding-valid", "required", "both"),
        ("verdict-present", "required", "skill"),
        ("confidence-present", "required", "skill"),
        ("audience-definition-check-present", "required", "skill"),
        ("scorecard-present", "required", "skill"),
        ("twelve-dimensions-present", "required", "skill"),
        ("priority-fixes-present", "required", "skill"),
        ("test-plan-present", "required", "skill"),
        ("final-recommendation-present", "required", "skill"),
    ]
    for aid, sev, applies in det:
        lines += [f"  - id: {aid}", f"    description: check {aid.replace('-', ' ')}",
                  f"    severity: {sev}", "    evaluation: deterministic",
                  f"    applies_to: {applies}"]
    # Optional extra deterministic assertions carrying a data-driven any_of field:
    # (id, severity, applies_to, pipe-delimited-phrases).
    for aid, sev, applies, any_of in extra_det:
        lines += [f"  - id: {aid}", f"    description: check {aid.replace('-', ' ')}",
                  f"    severity: {sev}", "    evaluation: deterministic",
                  f"    applies_to: {applies}", f'    any_of: "{any_of}"']
    lines += ["", "semantic:"]
    for aid, sev, applies in SEMANTIC:
        lines += [f"  - id: {aid}", f"    description: semantic check {aid.replace('-', ' ')}",
                  f"    severity: {sev}", "    evaluation: llm",
                  f"    applies_to: {applies}"]
    return "\n".join(lines) + "\n"


def skill_output():
    parts = [
        "# Generational Marketing Review\n",
        "## Verdict\n**Fit:** Weak fit\n**Confidence:** Medium\n",
        "## Audience-definition check\n- Cohort: test\n",
        "## Scorecard\n\n| Dimension | Score |\n|---|---|\n",
    ]
    for d in DIMENSIONS:
        parts.append(f"| {d} | 2 |\n")
    parts += [
        "## Priority fixes\n### Critical\n1. Fix\n",
        "## Test plan\n\n| Hypothesis | Metric |\n|---|---|\n| h | m |\n",
        "## Final recommendation\nRevise and retest.\n",
    ]
    return "".join(parts)


def totals(results):
    t = {"pass": 0, "fail": 0, "uncertain": 0}
    for r in results:
        t[r["result"]] = t.get(r["result"], 0) + 1
    t["total"] = len(results)
    return t


def build_valid(dirpath, assertions_text=None):
    """Write a fully consistent, passing scenario into dirpath.

    assertions_text overrides the default fixture assertions.yaml (used to
    exercise the data-driven any_of deterministic check); the semantic set is
    unchanged, so grader coverage and binding stay consistent.
    """
    d = Path(dirpath)
    (d / "input.md").write_text(INPUT_MD, "utf-8")
    (d / "assertions.yaml").write_text(assertions_text or assertions_yaml(), "utf-8")
    (d / "grader-prompt.md").write_text(GRADER_PROMPT_MD, "utf-8")
    (d / "baseline-output.md").write_text("# Baseline\n\nFree-form review text of adequate length. " * 5 + "\n", "utf-8")
    (d / "skill-output.md").write_text(skill_output(), "utf-8")

    assertions = ve.load_assertions(d)
    art = {n: ve.sha256_file(d / n) for n in
           ["input.md", "baseline-output.md", "skill-output.md", "assertions.yaml", "grader-prompt.md"]}

    def results():
        return [{"assertion_id": aid, "result": "pass", "reason": "ok", "excerpt": None,
                 "confidence": "high"} for aid, _, _ in SEMANTIC]

    def rset(kind):
        return {
            "output_file": f"{kind}-output.md",
            "graded_output_sha256": art[f"{kind}-output.md"],
            "input_sha256": art["input.md"],
            "assertions_sha256": art["assertions.yaml"],
            "grader_prompt_sha256": art["grader-prompt.md"],
            "grader_model": "test-model",
            "grader_client": "test",
            "results": results(),
            "totals": totals(results()),
        }

    grader_output = {
        "grader": {"model": "test-model", "client": "test", "method": "blind test", "blind": True},
        "baseline": rset("baseline"),
        "skill": rset("skill"),
        "totals": {"baseline": totals(results()), "skill": totals(results())},
    }
    (d / "grader-output.json").write_text(json.dumps(grader_output, indent=2), "utf-8")

    def gp(kind):
        text = (d / f"{kind}-output.md").read_text("utf-8")
        prompt = ve.regenerate_grader_prompt(d, assertions, text)
        return {"output_file": f"{kind}-output.md", "exact_prompt": prompt,
                "exact_prompt_sha256": ve.sha256_text(prompt)}

    baseline_prompt = INPUT_MD
    skill_prompt = "SKILL provided inline\n" + INPUT_MD
    meta = {
        "scenario": "unit-fixture",
        "artifact_hashes": art,
        "runs": {
            "baseline": {"model": "test-model", "isolation_method": "isolated no-repo",
                         "exact_prompt": baseline_prompt,
                         "exact_prompt_sha256": ve.sha256_text(baseline_prompt)},
            "skill": {"model": "test-model", "loading_method": "isolated inline skill",
                      "exact_prompt": skill_prompt,
                      "exact_prompt_sha256": ve.sha256_text(skill_prompt)},
        },
        "grader": {"model": "test-model", "method": "blind test",
                   "prompts": {"baseline": gp("baseline"), "skill": gp("skill")}},
    }
    (d / "run-metadata.json").write_text(json.dumps(meta, indent=2), "utf-8")
    return d


def failures(dirpath):
    return ve.validate_scenario(dirpath).required_failures


def load_json(d, name):
    return json.loads((Path(d) / name).read_text("utf-8"))


def dump_json(d, name, obj):
    (Path(d) / name).write_text(json.dumps(obj, indent=2), "utf-8")


class ValidateEvalTests(unittest.TestCase):
    def _dir(self):
        tmp = tempfile.mkdtemp(prefix="ve-test-")
        self.addCleanup(lambda: __import__("shutil").rmtree(tmp, ignore_errors=True))
        return build_valid(tmp)

    def assertHasFailure(self, fails, needle):
        self.assertTrue(any(needle in f for f in fails),
                        msg=f"expected a failure containing {needle!r}; got: {fails}")

    def test_valid_scenario_passes(self):
        self.assertEqual(failures(self._dir()), [])

    def test_changed_output_after_grading(self):
        d = self._dir()
        (Path(d) / "skill-output.md").write_text(skill_output() + "\nTAMPERED\n", "utf-8")
        fails = failures(d)
        self.assertHasFailure(fails, "artifact-hashes-bound")
        self.assertHasFailure(fails, "grader-binding-valid")

    def test_changed_assertions_after_grading(self):
        d = self._dir()
        with open(Path(d) / "assertions.yaml", "a", encoding="utf-8") as f:
            f.write("\n# tampered comment\n")
        self.assertHasFailure(failures(d), "assertions")

    def test_changed_grader_prompt_after_grading(self):
        d = self._dir()
        with open(Path(d) / "grader-prompt.md", "a", encoding="utf-8") as f:
            f.write("\nextra line\n")
        self.assertHasFailure(failures(d), "grader")

    def test_missing_assertion_result(self):
        d = self._dir()
        g = load_json(d, "grader-output.json")
        g["skill"]["results"] = g["skill"]["results"][:-1]
        dump_json(d, "grader-output.json", g)
        self.assertHasFailure(failures(d), "missing assertion results")

    def test_duplicate_assertion_result(self):
        d = self._dir()
        g = load_json(d, "grader-output.json")
        g["skill"]["results"].append(copy.deepcopy(g["skill"]["results"][0]))
        dump_json(d, "grader-output.json", g)
        self.assertHasFailure(failures(d), "duplicate assertion ids")

    def test_incorrect_totals(self):
        d = self._dir()
        g = load_json(d, "grader-output.json")
        g["skill"]["totals"]["pass"] = 999
        dump_json(d, "grader-output.json", g)
        self.assertHasFailure(failures(d), "totals")

    def test_uncertain_required_skill_result(self):
        d = self._dir()
        g = load_json(d, "grader-output.json")
        for r in g["skill"]["results"]:
            if r["assertion_id"] == "sem-req-both":
                r["result"] = "uncertain"
        g["skill"]["totals"] = totals(g["skill"]["results"])  # keep totals consistent to isolate gating
        dump_json(d, "grader-output.json", g)
        self.assertHasFailure(failures(d), "sem-req-both")

    def test_missing_rubric_dimension_in_skill_output(self):
        d = self._dir()
        text = (Path(d) / "skill-output.md").read_text("utf-8").replace("Evidence quality", "Evidence xyz")
        (Path(d) / "skill-output.md").write_text(text, "utf-8")
        # This changes the file hash too, so binding fails; the structural check
        # also fails. Assert the structural signal is present.
        self.assertHasFailure(failures(d), "twelve-dimensions-present")

    def test_run_metadata_root_is_list_does_not_crash(self):
        d = self._dir()
        dump_json(d, "run-metadata.json", [1, 2, 3])
        fails = failures(d)  # must return normally, not raise
        self.assertHasFailure(fails, "run-metadata.json is not an object")

    def test_grader_output_root_is_list_skips_binding(self):
        d = self._dir()
        dump_json(d, "grader-output.json", ["not", "an", "object"])
        called = []
        orig = ve.verify_hash_binding
        ve.verify_hash_binding = lambda *a, **k: called.append(True)
        try:
            fails = failures(d)  # must return normally, not raise
        finally:
            ve.verify_hash_binding = orig
        self.assertHasFailure(fails, "grader-output.json is not an object")
        self.assertEqual(called, [],
                         "verify_hash_binding must not run on an invalid grader-output.json root")

    def test_any_of_section_present_helper(self):
        # Case- and punctuation-insensitive substring match across pipe-delimited
        # phrases; the normalizer drops conjunctions like "and" on both sides.
        ok, _ = ve.any_of_section_present(
            "Cross-generation comparison | shared versus adapted",
            "## Shared Versus Adapted\nbody")
        self.assertTrue(ok)
        ok2, _ = ve.any_of_section_present(
            "Nonexistent zzz | another absent phrase", "no matching heading here")
        self.assertFalse(ok2)
        ok3, _ = ve.any_of_section_present(
            "Shared and adapted", "we cover SHARED / ADAPTED elements")
        self.assertTrue(ok3)

    def test_any_of_required_absent_fails(self):
        # A required any_of deterministic assertion whose phrases are absent from
        # the skill output fails the build, like any other required structural
        # check — driven entirely by assertions.yaml, not by scenario name.
        text = assertions_yaml(extra_det=[
            ("cross-generation-section-present", "required", "skill",
             "Zzz Missing Heading | Another Absent Phrase")])
        tmp = tempfile.mkdtemp(prefix="ve-anyof-")
        self.addCleanup(lambda: __import__("shutil").rmtree(tmp, ignore_errors=True))
        build_valid(tmp, assertions_text=text)
        self.assertHasFailure(failures(tmp), "cross-generation-section-present")

    def test_any_of_present_passes(self):
        # "Scorecard" appears in the fixture skill output, so a required any_of
        # assertion listing it passes and the scenario stays green.
        text = assertions_yaml(extra_det=[
            ("cross-generation-section-present", "required", "skill",
             "Scorecard | Zzz Absent Phrase")])
        tmp = tempfile.mkdtemp(prefix="ve-anyof-")
        self.addCleanup(lambda: __import__("shutil").rmtree(tmp, ignore_errors=True))
        build_valid(tmp, assertions_text=text)
        self.assertEqual(failures(tmp), [])

    def test_quoted_colon_scalar_sequence_item_must_be_quoted(self):
        # A colon-bearing scalar sequence item MUST be quoted to parse as a string.
        parsed = ve.parse_block_yaml('rubric_dimensions:\n  - "Category: Household cleaning"\n')
        self.assertEqual(parsed["rubric_dimensions"], ["Category: Household cleaning"])
        # By design, the UNQUOTED "- key: value" form is YAML mapping syntax.
        parsed2 = ve.parse_block_yaml('seq:\n  - Category: Household cleaning\n')
        self.assertEqual(parsed2["seq"], [{"Category": "Household cleaning"}])

    def _scenarios_root(self, names):
        """Build a temp SCENARIOS_DIR holding one valid scenario per name."""
        root = Path(tempfile.mkdtemp(prefix="ve-multi-"))
        self.addCleanup(lambda: __import__("shutil").rmtree(root, ignore_errors=True))
        for name in names:
            (root / name).mkdir()
            build_valid(root / name)
        return root

    def test_multiple_scenarios_discovered_and_independent(self):
        # main() discovers and validates every scenario directory under
        # SCENARIOS_DIR independently, using the same data-driven per-scenario
        # path — no scenario name is hardcoded. Adding a second scenario must not
        # disturb a passing one, and a required failure in one scenario must not
        # mask or corrupt the other. This guards the multi-scenario guarantee the
        # asset-review (email-gen-x) scenario relies on: the plan-review scenario
        # keeps passing unchanged while a second, independently graded scenario is
        # added alongside it.
        root = self._scenarios_root(["scenario-a", "scenario-b"])
        orig = ve.SCENARIOS_DIR
        ve.SCENARIOS_DIR = root
        self.addCleanup(lambda: setattr(ve, "SCENARIOS_DIR", orig))

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = ve.main()
        out = buf.getvalue()
        self.assertEqual(rc, 0, msg=out)
        self.assertIn("[scenario-a]", out)
        self.assertIn("[scenario-b]", out)
        self.assertIn("Scenarios checked : 2", out)

        # Break ONLY scenario-b; scenario-a must still validate with no failures.
        (root / "scenario-b" / "skill-output.md").write_text(
            skill_output() + "\nTAMPERED\n", "utf-8")
        self.assertEqual(failures(root / "scenario-a"), [])
        self.assertHasFailure(failures(root / "scenario-b"), "artifact-hashes-bound")

        # main() now fails overall (exit 1) but still reports BOTH scenarios.
        buf2 = io.StringIO()
        with contextlib.redirect_stdout(buf2):
            rc2 = ve.main()
        out2 = buf2.getvalue()
        self.assertEqual(rc2, 1)
        self.assertIn("[scenario-a]", out2)
        self.assertIn("[scenario-b]", out2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
