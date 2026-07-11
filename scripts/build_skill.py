from pathlib import Path
import hashlib
import os
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
DIST.mkdir(exist_ok=True)

TOP = "generational-marketing-review"
OUT = DIST / f"{TOP}.skill"

ALLOW = [
    "SKILL.md",
    "LICENSE",
    "NOTICE.md",
    "references/review-rubric.md",
    "references/generation-lenses.md",
    "references/plan-review.md",
    "references/asset-review.md",
    "references/evidence-and-safety.md",
    "assets/review-report-template.md",
    "assets/evidence-register-template.md",
]

with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for rel in sorted(ALLOW):
        path = ROOT / rel
        if not path.is_file():
            raise SystemExit(f"Missing allowlisted file: {rel}")
        info = zipfile.ZipInfo(f"{TOP}/{rel}")
        info.date_time = (1980, 1, 1, 0, 0, 0)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        zf.writestr(info, path.read_bytes())

digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
sha = OUT.with_suffix(OUT.suffix + ".sha256")
sha.write_text(f"{digest}  {OUT.name}\n", encoding="utf-8")
print(f"Built {OUT}")
print(f"SHA-256 {digest}")
