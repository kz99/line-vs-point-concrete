from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT / "external-submissions" / "inbox"
DESTINATION = ROOT / "external-submission"
P2 = 147457 * 147457


def validate(package: Path) -> tuple[bool, str]:
    manifest_path = package / "manifest.json"
    if not manifest_path.exists():
        return False, "missing manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text())
    except (OSError, json.JSONDecodeError):
        return False, "invalid manifest.json"
    agreements = manifest.get("absolute_agreements")
    if not isinstance(agreements, int) or isinstance(agreements, bool) or not 0 < agreements <= P2:
        return False, "absolute_agreements must be an integer in [1,p²]"
    if (manifest.get("fixed_prime"), manifest.get("fixed_degree"), manifest.get("dimension")) != (147457, 87, 2):
        return False, "fixed parameters must be p=147457, d=87, m=2"
    documents = list(package.glob("*.tex")) + list(package.glob("*.pdf"))
    if len(documents) != 1:
        return False, "package must contain exactly one .tex or .pdf document"
    document = documents[0]
    if document.suffix == ".tex":
        first_content = next((line.strip() for line in document.read_text(errors="replace").splitlines()
                              if line.strip() and not line.lstrip().startswith("%")), "")
        if not re.search(r"absolute agreements|agreement count|A\s*=", first_content, re.I):
            return False, "the first non-comment TeX line must state the absolute agreement count"
    return True, "ok"


def main() -> int:
    INBOX.mkdir(parents=True, exist_ok=True)
    DESTINATION.mkdir(parents=True, exist_ok=True)
    failures = 0
    for package in sorted(path for path in INBOX.iterdir() if path.is_dir()):
        valid, reason = validate(package)
        if not valid:
            print(f"REJECT {package.name}: {reason}")
            failures += 1
            continue
        target = DESTINATION / package.name
        if target.exists():
            print(f"REJECT {package.name}: destination already exists")
            failures += 1
            continue
        shutil.move(str(package), str(target))
        print(f"TRANSFERRED {target.relative_to(ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
