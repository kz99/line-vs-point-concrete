#!/usr/bin/env python3
"""Build a deterministic checksum manifest for durable research artifacts."""

from __future__ import annotations

import hashlib
import json
import argparse
import sqlite3
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "research_state"
OUTPUT = DATA_ROOT / "DATA_MANIFEST.json"
EXCLUDED_SUFFIXES = (".sqlite3-shm", ".sqlite3-wal")
EXCLUDED_NAMES = {"campaign.log", "runner.json", "STOP"}
EXCLUDED_PARTS = {"python-cache", "superseded"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_role(path: Path) -> str:
    parts = path.parts
    if "roadmaps" in parts and "agent_logs" in parts:
        return "roadmap_trace"
    if "roadmaps" in parts and "message_board" in parts:
        return "message_board"
    if "roadmaps" in parts:
        return "proof_roadmap"
    if "lemma_book" in parts:
        return "lemma_book"
    if "leaderboards" in parts:
        return "leaderboard"
    if "submissions" in parts:
        return "proof_submission"
    if "reviews" in parts:
        return "proof_review"
    if "agent_logs" in parts:
        return "agent_trace"
    if path.suffix == ".sqlite3":
        return "campaign_queue"
    if path.name in {"jobs.json", "status.json"}:
        return "campaign_index"
    return "documentation"


def database_summary(path: Path) -> dict:
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        tables = {row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}
        jobs = connection.execute("SELECT COUNT(*) FROM campaign_jobs").fetchone()[0]
        grouped = {}
        if "campaign_jobs" in tables:
            grouped = {row[0]: row[1] for row in connection.execute(
                "SELECT status,COUNT(*) FROM campaign_jobs GROUP BY status")}
        return {"integrity_check": integrity, "jobs": jobs, "job_statuses": grouped}
    finally:
        connection.close()


def database_summary_bytes(data: bytes) -> dict:
    with tempfile.NamedTemporaryFile(suffix=".sqlite3") as handle:
        handle.write(data)
        handle.flush()
        return database_summary(Path(handle.name))


def included(relative: Path) -> bool:
    return not (
        relative == OUTPUT.relative_to(ROOT)
        or relative.name in EXCLUDED_NAMES
        or relative.name.endswith(EXCLUDED_SUFFIXES)
        or EXCLUDED_PARTS.intersection(relative.parts)
    )


def index_files() -> list[tuple[Path, bytes]]:
    names = subprocess.run(
        ["git", "ls-files", "--cached", "--", "research_state"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    files = []
    for name in names:
        relative = Path(name)
        if not included(relative):
            continue
        content = subprocess.run(
            ["git", "show", f":{relative.as_posix()}"],
            cwd=ROOT,
            check=True,
            capture_output=True,
        ).stdout
        files.append((relative, content))
    return files


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--index",
        action="store_true",
        help="hash the staged Git index, including newly staged artifacts",
    )
    args = parser.parse_args()
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    files = []
    databases = {}
    if args.index:
        for relative, content in index_files():
            files.append({
                "path": relative.as_posix(),
                "role": file_role(relative.relative_to("research_state")),
                "bytes": len(content),
                "sha256": sha256_bytes(content),
            })
            if relative.name == "campaign.sqlite3":
                databases[relative.parent.name] = database_summary_bytes(content)
    else:
        for path in sorted(DATA_ROOT.rglob("*")):
            relative_path = path.relative_to(ROOT)
            if not path.is_file() or not included(relative_path):
                continue
            files.append({
                "path": relative_path.as_posix(),
                "role": file_role(path.relative_to(DATA_ROOT)),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            })
        databases = {
            path.parent.name: database_summary(path)
            for path in sorted(DATA_ROOT.glob("*/campaign.sqlite3"))
        }
    payload = {
        "schema": "line-point-concrete-data-manifest-v1",
        "hash_algorithm": "sha256",
        "durable_file_count": len(files),
        "total_bytes": sum(item["bytes"] for item in files),
        "campaigns": databases,
        "files": files,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
