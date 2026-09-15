from __future__ import annotations

import fcntl
import json
import os
import tempfile
from pathlib import Path
from typing import Any


def _merge_unique(existing: list[Any], incoming: list[Any], identity) -> list[Any]:
    merged: dict[str, Any] = {}
    order: list[str] = []
    for item in [*existing, *incoming]:
        key = str(identity(item))
        if key not in merged:
            order.append(key)
        merged[key] = item
    return [merged[key] for key in order]


def _merge_candidates(existing: Any, incoming: Any) -> Any:
    if not isinstance(existing, dict) or not isinstance(incoming, dict):
        return incoming
    result: dict[str, Any] = {}
    for group in ("verified", "promising", "rejected"):
        old_items = existing.get(group, [])
        new_items = incoming.get(group, [])
        if not isinstance(old_items, list) or not isinstance(new_items, list):
            result[group] = new_items
            continue
        result[group] = _merge_unique(
            old_items, new_items,
            lambda item: item.get("theorem_sha256") or
            f"{item.get('campaign', '')}:{item.get('job_id')}:{item.get('title')}",
        )
    return result


def _merge_history(existing: Any, incoming: Any) -> Any:
    if not isinstance(existing, dict) or not isinstance(incoming, dict):
        return incoming
    old_points = existing.get("points", [])
    new_points = incoming.get("points", [])
    if not isinstance(old_points, list) or not isinstance(new_points, list):
        return incoming
    points = _merge_unique(
        old_points, new_points,
        lambda item: item.get("theorem_sha256") or
        f"{item.get('agreement_count')}:{item.get('title')}",
    )
    points.sort(key=lambda item: (item.get("verified_at") or "9999", item.get("agreement_count", 0)))
    records: list[dict[str, Any]] = []
    best_count: int | None = None
    for point in points:
        count = point.get("agreement_count")
        if not isinstance(count, int) or (best_count is not None and count >= best_count):
            continue
        records.append(point)
        best_count = count
    return {**existing, **incoming, "points": records}


def _has_items(section: Any, item_key: str) -> bool:
    return isinstance(section, dict) and isinstance(section.get(item_key), list) and bool(section[item_key])


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
            # Campaigns are successive layers of one observatory. Updating the
            # active campaign must never erase verified results, prior partial
            # work, or published lemmas from an earlier campaign.
            merged = {**current, **updates}
            merged["candidates"] = _merge_candidates(
                current.get("candidates"), updates.get("candidates"))
            merged["soundness_history"] = _merge_history(
                current.get("soundness_history"), updates.get("soundness_history"))
            old_bottlenecks = current.get("bottlenecks", [])
            new_bottlenecks = updates.get("bottlenecks", [])
            if isinstance(old_bottlenecks, list) and isinstance(new_bottlenecks, list):
                merged["bottlenecks"] = _merge_unique(
                    old_bottlenecks, new_bottlenecks,
                    lambda item: json.dumps(item, sort_keys=True),
                )
            for key, item_key in (
                ("lemma_book", "lemmas"),
                ("proof_roadmaps", "roadmaps"),
                ("message_board", "messages"),
            ):
                if _has_items(current.get(key), item_key) and not _has_items(updates.get(key), item_key):
                    merged[key] = current[key]
            current = merged
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
