from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "SKILL.md",
    "README.md",
    "LICENSE",
    "NOTICE.md",
    "references/review-rubric.md",
    "references/generation-lenses.md",
    "references/plan-review.md",
    "references/asset-review.md",
    "references/evidence-and-safety.md",
    "assets/review-report-template.md",
    "assets/evidence-register-template.md",
    "evals/README.md",
]

missing = [p for p in REQUIRED if not (ROOT / p).is_file()]
if missing:
    print("Missing required files:")
    for p in missing:
        print(f"- {p}")
    sys.exit(1)

skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
required_frontmatter = [
    "name: generational-marketing-review",
    "license: Apache-2.0",
    "compatibility:",
]
for item in required_frontmatter:
    if item not in skill:
        print(f"SKILL.md is missing required frontmatter: {item}")
        sys.exit(1)

print("Structure validation passed.")
