#!/usr/bin/env python3
"""Build a deterministic checksum manifest for durable research artifacts."""

from __future__ import annotations

import hashlib
import json
import sqlite3
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


def main() -> None:
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    files = []
    for path in sorted(DATA_ROOT.rglob("*")):
        if (not path.is_file() or path == OUTPUT or path.name in EXCLUDED_NAMES or
                path.name.endswith(EXCLUDED_SUFFIXES) or
                EXCLUDED_PARTS.intersection(path.parts)):
            continue
        relative = path.relative_to(ROOT).as_posix()
        files.append({
            "path": relative,
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
