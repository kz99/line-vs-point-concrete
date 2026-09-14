from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from .agents import AgentError, CommandAgentProvider
from .campaign import load_campaign_config, utc_timestamp
from .snapshot import update_dashboard_sections


ROADMAP_DEFINITIONS = (
    {
        "id": "exact-analytic",
        "title": "Exact analytic chain",
        "focus": "constant-optimized pruning, interpolation, factorization, and one-polynomial recovery",
        "target": (
            "Prove the strongest explicit soundness bound $\\varepsilon$ for "
            "$p=147457$ and total degree $d=87$ by an exact analytic argument."
        ),
    },
    {
        "id": "certified-computation",
        "title": "Certified finite computation",
        "focus": "integer programs, exhaustive finite reductions, rational arithmetic, and independently checkable certificates",
        "target": (
            "Reduce fixed-instance soundness to finite exact obligations and certify them with "
            "reproducible checkers at $p=147457$ and $d=87$."
        ),
    },
    {
        "id": "end-to-end-soundness",
        "title": "End-to-end soundness chain",
        "focus": "a complete fixed-parameter dependency chain ending in one global polynomial",
        "target": (
            "Prove that acceptance at least an explicit $\\varepsilon$ yields agreement with one "
            "total-degree-at-most-$87$ polynomial on at least $\\varepsilon/10$ of $\\mathbb F_{147457}^2$."
        ),
    },
)


ROADMAP_NODE = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "id", "label", "statement_markdown", "kind", "work_state", "dependencies",
        "evidence_refs", "owner", "notes",
    ],
    "properties": {
        "id": {"type": "string"},
        "label": {"type": "string"},
        "statement_markdown": {"type": "string"},
        "kind": {
            "type": "string",
            "enum": [
                "definition", "literature_input", "reduction", "lemma", "theorem", "obligation",
            ],
        },
        "work_state": {
            "type": "string",
            "enum": ["open", "drafting", "candidate", "blocked", "refuted"],
        },
        "dependencies": {"type": "array", "items": {"type": "string"}},
        "evidence_refs": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["source_job_id", "source_step_id", "source_response_sha256"],
                "properties": {
                    "source_job_id": {"type": "string"},
                    "source_step_id": {"type": "string"},
                    "source_response_sha256": {"type": "string"},
                },
            },
        },
        "owner": {"type": "string"},
        "notes": {"type": "string"},
    },
}


DISCUSSION_DRAFT = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "channel", "kind", "subject", "body_markdown", "in_reply_to",
        "related_node_ids", "references",
    ],
    "properties": {
        "channel": {"type": "string"},
        "kind": {
            "type": "string",
            "enum": ["question", "idea", "objection", "request", "reply"],
        },
        "subject": {"type": "string"},
        "body_markdown": {"type": "string"},
        "in_reply_to": {"type": ["string", "null"]},
        "related_node_ids": {"type": "array", "items": {"type": "string"}},
        "references": {"type": "array", "items": {"type": "string"}},
    },
}


ROADMAP_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "roadmap_id", "corpus_sha256", "round", "title", "focus", "target_statement",
        "summary", "goal_node_id", "nodes", "critical_path", "messages",
    ],
    "properties": {
        "roadmap_id": {"type": "string"},
        "corpus_sha256": {"type": "string"},
        "round": {"type": "integer", "minimum": 1},
        "title": {"type": "string"},
        "focus": {"type": "string"},
        "target_statement": {"type": "string"},
        "summary": {"type": "string"},
        "goal_node_id": {"type": "string"},
        "nodes": {"type": "array", "items": ROADMAP_NODE},
        "critical_path": {"type": "array", "items": {"type": "string"}},
        "messages": {"type": "array", "items": DISCUSSION_DRAFT, "maxItems": 4},
    },
}


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_roadmap_response(
        definition: dict[str, str], corpus_sha: str, round_number: int,
        response: dict[str, Any], evidence_index: dict[str, Any] | None = None,
        known_message_ids: set[str] | None = None) -> list[str]:
    errors: list[str] = []
    if response.get("roadmap_id") != definition["id"]:
        errors.append("roadmap_id does not match the assigned roadmap")
    if response.get("corpus_sha256") != corpus_sha:
        errors.append("corpus_sha256 does not match the assigned snapshot")
    if response.get("round") != round_number:
        errors.append("round does not match the assigned round")
    nodes = response.get("nodes", [])
    if not nodes:
        errors.append("roadmap contains no dependency nodes")
        return errors
    node_ids = [str(node.get("id", "")) for node in nodes]
    if any(not node_id for node_id in node_ids) or len(set(node_ids)) != len(node_ids):
        errors.append("roadmap node ids must be nonempty and unique")
    known = set(node_ids)
    for node in nodes:
        node_id = str(node.get("id", ""))
        unknown = sorted(set(node.get("dependencies", [])) - known)
        if unknown:
            errors.append(f"{node_id} has unknown dependencies: {', '.join(unknown)}")
        if not str(node.get("statement_markdown", "")).strip():
            errors.append(f"node {node_id} has an empty statement")
        for reference in node.get("evidence_refs", []):
            key = "|".join(str(reference.get(field, "")) for field in (
                "source_job_id", "source_step_id", "source_response_sha256"))
            if evidence_index is not None and key not in evidence_index:
                errors.append(f"{node_id} cites unknown or stale evidence: {key}")
    goal = str(response.get("goal_node_id", ""))
    if goal not in known:
        errors.append("goal_node_id is not a roadmap node")
    critical = response.get("critical_path", [])
    if not critical or any(node_id not in known for node_id in critical):
        errors.append("critical_path must be a nonempty list of known nodes")
    elif critical[-1] != goal:
        errors.append("critical_path must end at goal_node_id")

    visiting: set[str] = set()
    visited: set[str] = set()
    dependencies = {
        str(node.get("id", "")): [str(value) for value in node.get("dependencies", [])]
        for node in nodes
    }

    def visit(node_id: str) -> None:
        if node_id in visiting:
            errors.append(f"dependency cycle detected at {node_id}")
            return
        if node_id in visited:
            return
        visiting.add(node_id)
        for dependency in dependencies.get(node_id, []):
            visit(dependency)
        visiting.remove(node_id)
        visited.add(node_id)

    for node_id in node_ids:
        visit(node_id)
    board_ids = known_message_ids or set()
    for message in response.get("messages", []):
        channel = str(message.get("channel", ""))
        if channel not in {"global", *(item["id"] for item in ROADMAP_DEFINITIONS)}:
            errors.append(f"unknown message channel: {channel}")
        reply = message.get("in_reply_to")
        if reply is not None and reply not in board_ids:
            errors.append(f"message replies to unknown post: {reply}")
        related = set(message.get("related_node_ids", []))
        if not related.issubset(known):
            errors.append("message references a node outside its submitted roadmap")
    return errors


class RoadmapWorkshop:
    """Run three focused roadmap agents over one shared mathematical corpus."""

    def __init__(self, config_path: Path | str):
        self.config, self.paths = load_campaign_config(config_path)
        self.cfg = self.config["campaign"]
        self.root = self.paths.campaign_dir / "roadmaps"
        self.runtime = self.root / "runtime"
        self.root.mkdir(parents=True, exist_ok=True)
        self.runtime.mkdir(parents=True, exist_ok=True)
        self.provider = CommandAgentProvider(
            self.paths.workspace,
            self.root / "agent_logs",
            executable=str(self.cfg.get("executable", "codex")),
            model=str(self.cfg.get("model", "gpt-5.6-sol")),
            reasoning_effort=str(self.cfg.get("reasoning_effort", "ultra")),
            disable_nested_agents=True,
            timeout_seconds=int(self.cfg.get("roadmap_timeout_seconds", 5400)),
        )

    def corpus_snapshot(self) -> dict[str, Any]:
        patterns = (
            "submissions/*/response.json",
            "reviews/*/*/audit.json",
            "lemma_book/submissions/*/response.json",
        )
        paths = sorted({
            path for pattern in patterns
            for path in self.paths.campaign_dir.glob(pattern)
            if path.is_file()
        })
        digest = hashlib.sha256()
        receipts = []
        for path in paths:
            relative = path.relative_to(self.paths.workspace).as_posix()
            value = file_sha256(path)
            digest.update(relative.encode())
            digest.update(value.encode())
            receipts.append({"path": relative, "sha256": value})
        evidence: dict[str, Any] = {}
        submissions_root = self.paths.campaign_dir / "submissions"
        for response_path in sorted(submissions_root.glob("*/response.json")):
            source_job_id = response_path.parent.name
            source = json.loads(response_path.read_text())
            source_sha = hashlib.sha256(
                json.dumps(source, sort_keys=True).encode()).hexdigest()
            claim = source.get("theorem_statement") or source.get("integrated_theorem", "")
            claim_sha = hashlib.sha256(str(claim).encode()).hexdigest()
            audits = []
            for seat in ("a", "b"):
                audit_path = (self.paths.campaign_dir / "reviews" / source_job_id /
                              f"verifier-{seat}-{source_job_id}" / "audit.json")
                if audit_path.exists():
                    audits.append(json.loads(audit_path.read_text()))
            double_audit_exact = bool(
                len(audits) == 2 and
                all(audit.get("verified_claim_sha256") == claim_sha for audit in audits))
            double_accepted = bool(
                double_audit_exact and
                all(audit.get("verdict") == "accept" for audit in audits))
            lemma_path = self.paths.campaign_dir / "lemma_book" / "submissions" / source_job_id / "response.json"
            lemma_parts: dict[str, list[str]] = {}
            if lemma_path.exists():
                lemma_response = json.loads(lemma_path.read_text())
                for lemma in lemma_response.get("lemmas", []):
                    lemma_parts.setdefault(str(lemma.get("source_step_id", "")), []).append(
                        str(lemma.get("id", "")))
            for step in source.get("proof_steps", []):
                key = "|".join((source_job_id, str(step["id"]), source_sha))
                evidence[key] = {
                    "source_job_id": source_job_id,
                    "source_step_id": str(step["id"]),
                    "source_response_sha256": source_sha,
                    "source_status": step.get("status", "conditional"),
                    "audit_verdicts": [audit.get("verdict", "pending") for audit in audits],
                    "double_audit_exact": double_audit_exact,
                    "double_accepted": double_accepted,
                    "lemma_ids": sorted(lemma_parts.get(str(step["id"]), [])),
                }
        payload = {"sha256": digest.hexdigest(), "files": receipts, "evidence": evidence}
        (self.root / "corpus-index.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n")
        return payload

    def _current(self, roadmap_id: str) -> dict[str, Any] | None:
        path = self.root / roadmap_id / "current.json"
        return json.loads(path.read_text()) if path.exists() else None

    def _message_board(self) -> dict[str, Any]:
        path = self.root / "message-board.json"
        if path.exists():
            return json.loads(path.read_text())
        return {"schema": "line-point-concrete-roadmap-message-board-v1", "messages": []}

    def _prompt(
            self, definition: dict[str, str], snapshot: dict[str, Any],
            round_number: int) -> str:
        current = self._current(definition["id"])
        board = self._message_board()
        history_path = self.paths.campaign_dir / "leaderboards" / "soundness-history.json"
        points = []
        if history_path.exists():
            try:
                points = list(json.loads(history_path.read_text()).get("points", []))
            except (json.JSONDecodeError, OSError, TypeError):
                points = []
        record = (
            f"epsilon={min(float(point['soundness']) for point in points):.17g}"
            if points else
            f"no verified point yet (comparison threshold epsilon={float(self.cfg.get('initial_soundness', 1.0)):.17g})"
        )
        return f"""You are the proof-roadmap agent for `{definition['id']}` in the bivariate
prime-field line-versus-point campaign. Work at the level of a Lean-style proof plan: give a
concise but complete directed acyclic chain of definitions, reductions, lemmas, obligations, and
the final theorem. Your focus is {definition['focus']}.

All work is shared. Read TARGET.md, the complete submissions, verifier audits, Lemma Book,
all roadmaps under {self.root}, and the informal message board at
{self.root / 'message-board.json'}. You may cite and reuse lemmas from any source or roadmap.
Treat message-board claims as informal suggestions, never as verified mathematics. Give roughly
60 percent of your attention to your assigned focus so the three agents explore distinct routes,
but import any useful shared lemma. Cite it in evidence_refs by the exact stable triple
(source_job_id, source_step_id, source_response_sha256) from corpus-index.json. Editorial lemma
splits are display-only and never change this proof reference.

The scope is fixed at $m=2$ over $\\mathbb F_{{147457}}$ with total degree $d=87$. Do not vary
these parameters or work on dimension bootstrapping. The target is the lowest explicit soundness
$\\varepsilon$ for which acceptance at least $\\varepsilon$ forces agreement with one global
total-degree-at-most-$87$ polynomial on at least $\\varepsilon/10$ of all points. Lower is
better. Use work_state only to report activity: `open`,
`drafting`, `candidate`, `blocked`, or `refuted`. The harness—not you—derives proof status from
exact source hashes and two independent matching verifier accepts. Never convert confidence, a polished lemma,
or informal discussion into verified proof progress.

The authoritative leaderboard is {history_path}; its current record is {record}. Your purpose is
not to complete a large roadmap for its own sake. Concentrate on the shortest dependency chain
that can yield a rigorously numerical epsilon below that record, and delete or deprioritize nodes
that do not plausibly move the leaderboard. Every proposed lemma should identify which numerical
loss it improves and how that improvement propagates to the final epsilon.

This is roadmap round {round_number}. The shared corpus snapshot SHA-256 is
{snapshot['sha256']}. Set those exact values in the response. Preserve useful nodes from your
previous roadmap while making dependencies more complete and concise. Every dependency must
refer to another node in this roadmap. The critical_path must list the shortest dependency chain
ending at goal_node_id. Keep node statements mathematical and minimal; put short planning context
in notes. Enclose math in $...$ or $$...$$ using KaTeX-supported LaTeX.

Post up to four informal messages for the other roadmap agents: questions, warnings, proposed
lemma imports, or requests for help. Messages may be candid and exploratory, but must cite the
relevant roadmap/node/lemma ids when possible. Use channel `global` or one of the three roadmap
ids. Use in_reply_to only for an id already present on the shared board. related_node_ids may
contain only nodes in this submitted roadmap.

ASSIGNED ROADMAP:
{json.dumps(definition, indent=2, sort_keys=True)}

PREVIOUS VERSION OF THIS ROADMAP:
{json.dumps(current, indent=2, sort_keys=True) if current else 'None'}

CURRENT SHARED MESSAGE BOARD:
{json.dumps(board, indent=2, sort_keys=True)}

CORPUS RECEIPT:
{json.dumps(snapshot['files'], indent=2, sort_keys=True)}

STABLE PROOF-EVIDENCE INDEX:
{json.dumps(snapshot['evidence'], indent=2, sort_keys=True)}
"""

    def _node_executable(self) -> str:
        node = shutil.which("node")
        if node:
            return node
        pnpm = shutil.which("pnpm")
        bundled = (Path(pnpm).resolve().parents[2] / "node" / "bin" / "node") if pnpm else None
        if bundled and bundled.exists():
            return str(bundled)
        raise AgentError("node executable not found for deterministic KaTeX validation")

    def _render_check(self, response: dict[str, Any]) -> dict[str, Any]:
        script = self.paths.workspace / "dashboard" / "scripts" / "validate-roadmap-math.mjs"
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump(response, handle)
            temporary = Path(handle.name)
        try:
            completed = subprocess.run(
                [self._node_executable(), str(script), str(temporary)],
                cwd=self.paths.workspace / "dashboard",
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=120,
                check=False,
            )
        finally:
            temporary.unlink(missing_ok=True)
        if completed.returncode != 0:
            raise AgentError(
                "roadmap KaTeX validation failed: " +
                (completed.stderr or completed.stdout).strip())
        return json.loads(completed.stdout)

    def _run_agent(
            self, definition: dict[str, str], snapshot: dict[str, Any],
            round_number: int) -> tuple[dict[str, Any], dict[str, Any]]:
        errors: list[str] = []
        max_attempts = int(self.cfg.get("roadmap_max_attempts", 4))
        for _ in range(max_attempts):
            prompt = self._prompt(definition, snapshot, round_number)
            if errors:
                prompt += "\n\nThe previous attempt was rejected for:\n- " + "\n- ".join(errors)
            response, metadata = self.provider.run(
                f"roadmap-{definition['id']}-round-{round_number:04d}",
                prompt,
                ROADMAP_SCHEMA,
            )
            errors = validate_roadmap_response(
                definition, snapshot["sha256"], round_number, response,
                evidence_index=snapshot["evidence"],
                known_message_ids={
                    str(message.get("id"))
                    for message in self._message_board().get("messages", [])
                },
            )
            if errors:
                continue
            try:
                render_validation = self._render_check(response)
            except AgentError as exc:
                errors = [str(exc)]
                continue
            response["render_validation"] = render_validation
            return response, metadata
        raise AgentError(
            f"roadmap agent exhausted {max_attempts} attempts for {definition['id']}: " +
            "; ".join(errors))

    @staticmethod
    def _derive_progress(
            nodes: list[dict[str, Any]], goal_node_id: str,
            evidence_index: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, int]]:
        node_map = {str(node["id"]): node for node in nodes}
        base: dict[str, str] = {}
        enriched: dict[str, dict[str, Any]] = {}
        for node_id, node in node_map.items():
            references = node.get("evidence_refs", [])
            evidence = []
            for reference in references:
                key = "|".join(str(reference.get(field, "")) for field in (
                    "source_job_id", "source_step_id", "source_response_sha256"))
                if key in evidence_index:
                    evidence.append(evidence_index[key])
            if node.get("kind") in {"definition", "literature_input"}:
                initial = "external"
            elif node.get("work_state") == "refuted":
                initial = "invalid"
            elif not references or len(evidence) != len(references):
                initial = "open"
            elif any(
                    item["source_status"] == "refuted" or
                    "reject" in item["audit_verdicts"]
                    for item in evidence):
                initial = "invalid"
            elif all(
                    item["source_status"] == "proved" and
                    item["double_accepted"] and item["double_audit_exact"]
                    for item in evidence):
                initial = "verified"
            else:
                initial = "provisional"
            base[node_id] = initial
            enriched[node_id] = {
                **node,
                "resolved_lemma_ids": sorted({
                    lemma_id for item in evidence for lemma_id in item.get("lemma_ids", [])
                }),
            }

        resolved: dict[str, str] = {}

        def resolve(node_id: str) -> str:
            if node_id in resolved:
                return resolved[node_id]
            dependency_states = [resolve(value) for value in node_map[node_id]["dependencies"]]
            state = base[node_id]
            if state == "verified" and all(
                    dependency in {"verified", "external"}
                    for dependency in dependency_states):
                derived = "verified"
            elif state == "invalid" or "invalid" in dependency_states:
                derived = "invalid"
            elif node_map[node_id].get("work_state") == "blocked":
                derived = "blocked"
            elif state == "provisional" or "provisional" in dependency_states:
                derived = "provisional"
            elif state == "external":
                derived = "external"
            else:
                derived = "open"
            resolved[node_id] = derived
            return derived

        for node_id in node_map:
            enriched[node_id]["proof_state"] = resolve(node_id)

        required: set[str] = set()

        def collect(node_id: str) -> None:
            if node_id in required or node_id not in node_map:
                return
            required.add(node_id)
            for dependency in node_map[node_id]["dependencies"]:
                collect(dependency)

        collect(goal_node_id)
        internal = [node_id for node_id in required
                    if node_map[node_id].get("kind") not in {"definition", "literature_input"}]
        verified = sum(resolved[node_id] == "verified" for node_id in internal)
        provisional = sum(resolved[node_id] == "provisional" for node_id in internal)
        blocked = sum(resolved[node_id] == "blocked" for node_id in internal)
        invalid = sum(resolved[node_id] == "invalid" for node_id in internal)
        opened = sum(resolved[node_id] == "open" for node_id in internal)
        mapped = sum(bool(node_map[node_id].get("evidence_refs")) for node_id in internal)
        total = len(internal)
        progress = {
            "percent": (100 * verified) // total if total else 0,
            "verified": verified,
            "provisional": provisional,
            "open": opened,
            "blocked": blocked,
            "invalid": invalid,
            "mapped": mapped,
            "total": total,
        }
        return [enriched[str(node["id"])] for node in nodes], progress

    def _save_response(
            self, response: dict[str, Any], metadata: dict[str, Any],
            evidence_index: dict[str, Any]) -> None:
        roadmap_id = str(response["roadmap_id"])
        round_number = int(response["round"])
        enriched_nodes, progress = self._derive_progress(
            response["nodes"], response["goal_node_id"], evidence_index)
        output = {
            **response,
            "nodes": enriched_nodes,
            "progress": progress,
            "updated_at": utc_timestamp(),
        }
        out_dir = self.root / roadmap_id
        out_dir.mkdir(parents=True, exist_ok=True)
        round_path = out_dir / f"round-{round_number:04d}.json"
        round_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
        (out_dir / "current.json").write_text(
            json.dumps(output, indent=2, sort_keys=True) + "\n")
        (out_dir / f"round-{round_number:04d}.manifest.json").write_text(json.dumps({
            "schema": "line-point-proof-roadmap-v1",
            "roadmap_id": roadmap_id,
            "round": round_number,
            "corpus_sha256": response["corpus_sha256"],
            "response_sha256": file_sha256(round_path),
            "model": self.provider.model,
            "reasoning_effort": self.provider.reasoning_effort,
            "agent": metadata,
            "written_at": utc_timestamp(),
        }, indent=2, sort_keys=True) + "\n")

    def _merge_messages(self, responses: list[dict[str, Any]]) -> None:
        board = self._message_board()
        messages = list(board.get("messages", []))
        known = {message.get("id") for message in messages}
        posts_dir = self.root / "message_board" / "posts"
        posts_dir.mkdir(parents=True, exist_ok=True)
        for response in responses:
            for draft in response.get("messages", []):
                basis = json.dumps({
                    "author": response["roadmap_id"],
                    "round": response["round"],
                    **draft,
                }, sort_keys=True)
                message_id = "msg-" + hashlib.sha256(basis.encode()).hexdigest()[:12]
                if message_id in known:
                    continue
                known.add(message_id)
                message = {
                    "id": message_id,
                    "author": response["roadmap_id"],
                    "roadmap_id": response["roadmap_id"],
                    "round": response["round"],
                    "created_at": utc_timestamp(),
                    "informal": True,
                    **draft,
                }
                messages.append(message)
                post_path = posts_dir / f"{message_id}.json"
                if not post_path.exists():
                    post_path.write_text(json.dumps(
                        message, indent=2, sort_keys=True) + "\n")
        payload = {
            "schema": "line-point-roadmap-message-board-v1",
            "updated_at": utc_timestamp(),
            "messages": messages,
        }
        (self.root / "message-board.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n")

    def run_round(self) -> dict[str, Any]:
        snapshot = self.corpus_snapshot()
        rounds = [int((self._current(item["id"]) or {}).get("round", 0))
                  for item in ROADMAP_DEFINITIONS]
        round_number = min(rounds) + 1
        (self.runtime / "status.json").write_text(json.dumps({
            "status": "running",
            "round": round_number,
            "active_roadmaps": [item["id"] for item in ROADMAP_DEFINITIONS],
            "corpus_sha256": snapshot["sha256"],
            "updated_at": utc_timestamp(),
        }, indent=2, sort_keys=True) + "\n")
        self.export_snapshot()

        successes: list[tuple[dict[str, Any], dict[str, Any]]] = []
        max_workers = max(3, int(self.cfg.get("roadmap_max_workers", 3)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self._run_agent, definition, snapshot, round_number): definition
                for definition in ROADMAP_DEFINITIONS
            }
            for future in as_completed(futures):
                definition = futures[future]
                try:
                    successes.append(future.result())
                except Exception as exc:
                    (self.runtime / f"{definition['id']}.error.txt").write_text(
                        f"{utc_timestamp()} {type(exc).__name__}: {exc}\n")
        for response, metadata in successes:
            self._save_response(response, metadata, snapshot["evidence"])
        self._merge_messages([response for response, _ in successes])
        completed = sorted(response["roadmap_id"] for response, _ in successes)
        (self.runtime / "status.json").write_text(json.dumps({
            "status": "watching",
            "round": round_number,
            "active_roadmaps": [],
            "completed_roadmaps": completed,
            "corpus_sha256": snapshot["sha256"],
            "updated_at": utc_timestamp(),
        }, indent=2, sort_keys=True) + "\n")
        (self.runtime / "last-corpus-sha256").write_text(snapshot["sha256"] + "\n")
        return self.export_snapshot()

    def export_snapshot(self) -> dict[str, Any]:
        runtime_path = self.runtime / "status.json"
        runtime = json.loads(runtime_path.read_text()) if runtime_path.exists() else {
            "status": "queued", "round": 0, "active_roadmaps": [],
        }
        roadmaps = []
        for definition in ROADMAP_DEFINITIONS:
            current = self._current(definition["id"])
            if current:
                roadmaps.append(current)
            else:
                roadmaps.append({
                    "roadmap_id": definition["id"],
                    "title": definition["title"],
                    "focus": definition["focus"],
                    "target_statement": definition["target"],
                    "summary": "The first dependency audit is queued.",
                    "goal_node_id": "",
                    "nodes": [],
                    "critical_path": [],
                    "round": 0,
                    "progress": {
                        "percent": 0, "verified": 0, "provisional": 0, "open": 0,
                        "blocked": 0, "invalid": 0, "mapped": 0, "total": 0,
                    },
                    "updated_at": utc_timestamp(),
                })
        board = self._message_board()
        roadmap_payload = {
            "schema": "line-point-proof-roadmaps-v1",
            "model": self.provider.model,
            "reasoning_effort": self.provider.reasoning_effort,
            "status": runtime.get("status", "queued"),
            "round": runtime.get("round", 0),
            "active_roadmaps": runtime.get("active_roadmaps", []),
            "roadmaps": roadmaps,
            "updated_at": utc_timestamp(),
        }
        (self.root / "proof-roadmaps.json").write_text(
            json.dumps(roadmap_payload, indent=2, sort_keys=True) + "\n")
        update_dashboard_sections(self.paths.workspace, {
            "proof_roadmaps": roadmap_payload,
            "message_board": board,
        })
        return roadmap_payload

    def run(self, watch: bool = False) -> dict[str, Any]:
        initial_rounds = max(1, int(self.cfg.get("roadmap_initial_rounds", 1)))
        while True:
            current_rounds = [int((self._current(item["id"]) or {}).get("round", 0))
                              for item in ROADMAP_DEFINITIONS]
            corpus_sha = self.corpus_snapshot()["sha256"]
            last_path = self.runtime / "last-corpus-sha256"
            last_sha = last_path.read_text().strip() if last_path.exists() else ""
            if min(current_rounds) < initial_rounds or corpus_sha != last_sha:
                result = self.run_round()
            else:
                result = self.export_snapshot()
            if not watch or (
                    (self.paths.campaign_dir / "COMPLETED").exists() and
                    corpus_sha == self.corpus_snapshot()["sha256"] and
                    min(current_rounds) >= initial_rounds):
                return result
            time.sleep(int(self.cfg.get("roadmap_poll_seconds", 45)))


def launch_roadmap_workshop(config_path: Path | str) -> dict[str, Any]:
    workshop = RoadmapWorkshop(config_path)
    pid_path = workshop.runtime / "runner.json"
    if pid_path.exists():
        old = json.loads(pid_path.read_text())
        try:
            os.kill(int(old["pid"]), 0)
            return {"status": "already_running", **old}
        except (OSError, KeyError, ValueError):
            pass
    log_path = workshop.runtime / "roadmap-workshop.log"
    log_handle = log_path.open("a")
    environment = os.environ.copy()
    source_path = str(workshop.paths.workspace / "src")
    environment["PYTHONPATH"] = (
        source_path + os.pathsep + environment["PYTHONPATH"]
        if environment.get("PYTHONPATH") else source_path)
    environment["PYTHONPYCACHEPREFIX"] = str(workshop.runtime / "python-cache")
    process = subprocess.Popen(
        [sys.executable, "-m", "line_point_research", "roadmap-run",
         str(Path(config_path).resolve()), "--watch"],
        cwd=workshop.paths.workspace,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
        env=environment,
    )
    log_handle.close()
    payload = {
        "status": "launched",
        "pid": process.pid,
        "config": str(Path(config_path).resolve()),
        "log": str(log_path),
        "started_at": utc_timestamp(),
    }
    pid_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return payload
