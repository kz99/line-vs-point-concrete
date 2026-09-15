from __future__ import annotations

import base64
import binascii
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT / "external-submissions" / "inbox"
DESTINATION = ROOT / "external-submission"
P2 = 147457 * 147457
BUNDLE_SUFFIX = ".lvp-submission.json"
MAX_DOCUMENT_BYTES = 25 * 1024 * 1024
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def validate_manifest(manifest: object) -> tuple[bool, str]:
    if not isinstance(manifest, dict):
        return False, "manifest must be an object"
    if (manifest.get("fixed_prime"), manifest.get("fixed_degree"), manifest.get("dimension")) != (147457, 87, 2):
        return False, "fixed parameters must be p=147457, d=87, m=2"
    contribution_type = manifest.get("contribution_type", "leaderboard")
    if contribution_type not in {"leaderboard", "research"}:
        return False, "contribution_type must be leaderboard or research"
    agreements = manifest.get("absolute_agreements")
    if contribution_type == "leaderboard":
        if not isinstance(agreements, int) or isinstance(agreements, bool) or not 0 < agreements <= P2:
            return False, "a leaderboard submission needs absolute_agreements in [1,p²]"
    elif agreements is not None:
        return False, "a research contribution must omit absolute_agreements or set it to null"
    return True, "ok"


def validate_document(filename: str, content: bytes, contribution_type: str) -> tuple[bool, str]:
    if Path(filename).name != filename or not re.search(r"\.(md|tex|pdf)$", filename, re.I):
        return False, "document filename must be a basename ending in .md, .tex, or .pdf"
    if not content:
        return False, "document is empty"
    if len(content) > MAX_DOCUMENT_BYTES:
        return False, "document exceeds the 25 MiB limit"
    if contribution_type == "leaderboard" and filename.lower().endswith((".md", ".tex")):
        text = content.decode(errors="replace")
        first_content = next((line.strip() for line in text.splitlines()
                              if line.strip() and not line.lstrip().startswith(("%", "<!--"))), "")
        if not re.search(r"absolute (soundness score|agreements)|agreement count|A\s*=", first_content, re.I):
            return False, "a leaderboard note must state the absolute score on its first content line"
    return True, "ok"


def validate(package: Path) -> tuple[bool, str]:
    manifest_path = package / "manifest.json"
    if not manifest_path.exists():
        return False, "missing manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text())
    except (OSError, json.JSONDecodeError):
        return False, "invalid manifest.json"
    valid, reason = validate_manifest(manifest)
    if not valid:
        return valid, reason
    documents = list(package.glob("*.md")) + list(package.glob("*.tex")) + list(package.glob("*.pdf"))
    if len(documents) != 1:
        return False, "package must contain exactly one .md, .tex, or .pdf document"
    return validate_document(
        documents[0].name,
        documents[0].read_bytes(),
        manifest.get("contribution_type", "leaderboard"),
    )


def read_bundle(bundle_path: Path) -> tuple[dict[str, object] | None, str]:
    try:
        bundle = json.loads(bundle_path.read_text())
    except (OSError, json.JSONDecodeError):
        return None, "invalid handoff JSON"
    if not isinstance(bundle, dict) or bundle.get("schema") != "line-point-handoff-bundle-v1":
        return None, "bundle schema must be line-point-handoff-bundle-v1"
    manifest = bundle.get("manifest")
    valid, reason = validate_manifest(manifest)
    if not valid:
        return None, reason
    document = bundle.get("document")
    if not isinstance(document, dict):
        return None, "bundle document must be an object"
    filename = document.get("filename")
    encoded = document.get("content_base64")
    if not isinstance(filename, str) or not isinstance(encoded, str):
        return None, "bundle document needs filename and content_base64"
    try:
        content = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError):
        return None, "document content_base64 is invalid"
    valid, reason = validate_document(
        filename,
        content,
        str(manifest.get("contribution_type", "leaderboard")),
    )
    if not valid:
        return None, reason
    return {"manifest": manifest, "filename": filename, "content": content}, "ok"


def transfer_bundle(bundle_path: Path) -> tuple[bool, str]:
    name = bundle_path.name.removesuffix(BUNDLE_SUFFIX)
    if not SLUG_PATTERN.fullmatch(name):
        return False, "bundle filename prefix must be a lowercase hyphenated slug"
    target = DESTINATION / name
    if target.exists():
        return False, "destination already exists"
    unpacked, reason = read_bundle(bundle_path)
    if unpacked is None:
        return False, reason
    target.mkdir(parents=False)
    (target / "manifest.json").write_text(json.dumps(unpacked["manifest"], indent=2, sort_keys=True) + "\n")
    (target / str(unpacked["filename"])).write_bytes(bytes(unpacked["content"]))
    shutil.move(str(bundle_path), str(target / "handoff-bundle.json"))
    try:
        display_target = target.relative_to(ROOT)
    except ValueError:
        display_target = target
    return True, str(display_target)


def main() -> int:
    INBOX.mkdir(parents=True, exist_ok=True)
    DESTINATION.mkdir(parents=True, exist_ok=True)
    failures = 0
    for bundle in sorted(INBOX.glob(f"*{BUNDLE_SUFFIX}")):
        valid, reason = transfer_bundle(bundle)
        print(f"{'TRANSFERRED' if valid else 'REJECT'} {reason if valid else bundle.name + ': ' + reason}")
        failures += not valid
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
