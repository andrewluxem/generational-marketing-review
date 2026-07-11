from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = [ROOT / "SKILL.md", ROOT / "references", ROOT / "assets"]
EXCLUDED = {ROOT / "README.md"}

patterns = {
    "email address": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "social handle": re.compile(r"(?<!\w)@[A-Za-z0-9_.]{2,}"),
    "uncited percentage": re.compile(r"\b\d{1,3}(?:\.\d+)?\s*%"),
}

files = []
for entry in SCAN_DIRS:
    if entry.is_file():
        files.append(entry)
    elif entry.is_dir():
        files.extend(p for p in entry.rglob("*") if p.is_file())

problems = []
for path in files:
    if path in EXCLUDED:
        continue
    text = path.read_text(encoding="utf-8")
    for label, pattern in patterns.items():
        for match in pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            problems.append((path.relative_to(ROOT), line, label, match.group(0)))

if problems:
    print("Public-claim scan failed:")
    for path, line, label, value in problems:
        print(f"- {path}:{line}: {label}: {value}")
    sys.exit(1)

print("Public-claim scan passed.")
