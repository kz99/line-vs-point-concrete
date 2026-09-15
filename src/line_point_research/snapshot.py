from __future__ import annotations

import fcntl
import json
import os
import tempfile
from pathlib import Path
from typing import Any


def update_dashboard_sections(
        workspace: Path, updates: dict[str, Any], replace_base: bool = False) -> None:
    """Atomically update independently owned dashboard sections under one file lock."""
    dashboard_public = workspace / "dashboard" / "public"
    if not dashboard_public.is_dir():
        return
    snapshot_path = dashboard_public / "research-data.json"
    lock_path = dashboard_public / ".research-data.lock"
    with lock_path.open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        current: dict[str, Any] = {}
        if snapshot_path.exists():
            try:
                current = json.loads(snapshot_path.read_text())
            except json.JSONDecodeError:
                current = {}
        if replace_base:
            preserved = {
                key: current[key]
                for key in ("lemma_book", "proof_roadmaps", "message_board")
                if key in current
            }
            current = {**updates, **preserved}
        else:
            # A newly initialized campaign can briefly emit an empty auxiliary
            # section while the lemma/roadmap workers are still loading. Never
            # let that transient snapshot erase a populated public section.
            for key in ("lemma_book", "proof_roadmaps", "message_board"):
                incoming = updates.get(key)
                existing = current.get(key)
                if isinstance(incoming, dict) and isinstance(existing, dict):
                    incoming_items = incoming.get("lemmas") if key == "lemma_book" else incoming.get("roadmaps") if key == "proof_roadmaps" else incoming.get("messages")
                    existing_items = existing.get("lemmas") if key == "lemma_book" else existing.get("roadmaps") if key == "proof_roadmaps" else existing.get("messages")
                    if isinstance(incoming_items, list) and isinstance(existing_items, list) and not incoming_items and existing_items:
                        updates = {**updates, key: existing}
            current.update(updates)
        with tempfile.NamedTemporaryFile(
                "w", dir=dashboard_public, prefix="research-data.", suffix=".tmp",
                delete=False) as handle:
            json.dump(current, handle, indent=2, sort_keys=True)
            handle.write("\n")
            temporary = Path(handle.name)
        os.replace(temporary, snapshot_path)
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
