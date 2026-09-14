from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

from .agents import AgentError, CommandAgentProvider
from .campaign import load_campaign_config, utc_timestamp
from .snapshot import update_dashboard_sections


LEMMA_STATEMENT_RULE = (
    "A lemma statement contains only its quantified objects, hypotheses, and conclusion. "
    "It contains no motivation, derivation, commentary, proof sketch, interpretation, history, "
    "or explanation; put all such material in the proof."
)


LEMMA_ENTRY = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "id", "source_step_id", "part", "title", "statement_markdown",
        "proof_markdown", "status", "dependencies",
    ],
    "properties": {
        "id": {"type": "string"},
        "source_step_id": {"type": "string"},
        "part": {"type": "integer", "minimum": 1},
        "title": {"type": "string"},
        "statement_markdown": {"type": "string"},
        "proof_markdown": {"type": "string"},
        "status": {
            "type": "string",
            "enum": ["proved", "conditional", "conjectural", "refuted"],
        },
        "dependencies": {"type": "array", "items": {"type": "string"}},
    },
}


LEMMA_BOOK_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "source_job_id", "source_response_sha256", "coverage_complete",
        "omitted_source_step_ids", "lemmas",
    ],
    "properties": {
        "source_job_id": {"type": "string"},
        "source_response_sha256": {"type": "string"},
        "coverage_complete": {"type": "boolean"},
        "omitted_source_step_ids": {"type": "array", "items": {"type": "string"}},
        "lemmas": {"type": "array", "items": LEMMA_ENTRY},
    },
}


def canonical_sha256(value: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def validate_editorial_response(
        source_id: str, source: dict[str, Any], response: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected_hash = canonical_sha256(source)
    source_steps = {str(step["id"]): step for step in source.get("proof_steps", [])}
    lemmas = response.get("lemmas", [])
    if response.get("source_job_id") != source_id:
        errors.append("source_job_id does not match the source submission")
    if response.get("source_response_sha256") != expected_hash:
        errors.append("source_response_sha256 does not match the source submission")
    if not response.get("coverage_complete"):
        errors.append("coverage_complete must be true")
    if response.get("omitted_source_step_ids"):
        errors.append("no source proof step may be omitted")
    if not lemmas:
        errors.append("lemma book contains no lemmas")

    seen_ids: set[str] = set()
    covered: set[str] = set()
    parts: dict[str, list[int]] = {}
    for lemma in lemmas:
        lemma_id = str(lemma.get("id", ""))
        step_id = str(lemma.get("source_step_id", ""))
        if not lemma_id or lemma_id in seen_ids:
            errors.append(f"duplicate or empty lemma id: {lemma_id!r}")
        seen_ids.add(lemma_id)
        if step_id not in source_steps:
            errors.append(f"unknown source step: {step_id!r}")
            continue
        covered.add(step_id)
        part = lemma.get("part")
        if not isinstance(part, int) or part < 1:
            errors.append(f"invalid split part for {lemma_id}")
        else:
            parts.setdefault(step_id, []).append(part)
        if lemma.get("status") != source_steps[step_id].get("status"):
            errors.append(f"status changed for {lemma_id}")
        if not str(lemma.get("statement_markdown", "")).strip():
            errors.append(f"empty statement for {lemma_id}")
        if not str(lemma.get("proof_markdown", "")).strip():
            errors.append(f"empty proof for {lemma_id}")

    missing = sorted(set(source_steps) - covered)
    if missing:
        errors.append("uncovered source proof steps: " + ", ".join(missing))
    for step_id, values in parts.items():
        if sorted(values) != list(range(1, len(values) + 1)):
            errors.append(f"nonconsecutive split parts for {step_id}")
    return errors


class LemmaBookEditor:
    """Continuously post-edit immutable submissions into a public lemma book."""

    def __init__(self, config_path: Path | str):
        self.config, self.paths = load_campaign_config(config_path)
        self.cfg = self.config["campaign"]
        self.root = self.paths.campaign_dir / "lemma_book"
        self.submissions = self.root / "submissions"
        self.runtime = self.root / "runtime"
        self.submissions.mkdir(parents=True, exist_ok=True)
        self.runtime.mkdir(parents=True, exist_ok=True)
        self.provider = CommandAgentProvider(
            self.paths.workspace,
            self.root / "agent_logs",
            executable=str(self.cfg.get("executable", "codex")),
            model=str(self.cfg.get("model", "gpt-5.6-sol")),
            reasoning_effort=str(self.cfg.get("reasoning_effort", "ultra")),
            disable_nested_agents=True,
            timeout_seconds=int(self.cfg.get("lemma_writer_timeout_seconds", 5400)),
        )

    def _prompt(self, source_id: str, source: dict[str, Any]) -> str:
        source_hash = canonical_sha256(source)
        return f"""You are the dedicated Lemma Writer for a mathematical autoresearch campaign.
Post-edit every structured proof step in submission {source_id} into a clear lemma-book entry.
You are an editor, not a researcher or verifier. The raw submission is immutable.

The immutable ambient parameters are $m=2$, $p=147457$, and total degree $d=87$. Preserve them
literally; do not generalize a fixed-instance lemma or substitute a nearby degree.

RULE: {LEMMA_STATEMENT_RULE}

Preserve the exact mathematical content, hypotheses, status, and dependency closure of every
source step. Never strengthen, weaken, repair, validate, refute, or omit a claim. A refuted source
step remains visibly refuted. You may split one source step into two or more ordered entries when
that materially improves comprehension; give the pieces consecutive part numbers and repeat the
same source_step_id. Move any explanation removed from a statement into proof_markdown. Retain
all substantive proof content. Titles are short noun phrases and contain no mathematical claim.

Every source proof-step id must occur in at least one output entry. Set coverage_complete=true
and omitted_source_step_ids=[] only after checking this. Use stable ids of the form
{source_id}:<source-step-id>.<part>. Enclose every mathematical expression in $...$ or $$...$$
using KaTeX-supported LaTeX. Do not put mathematics in code spans, and do not leave TeX commands
outside math delimiters. Use Markdown prose outside mathematics. The publication harness will
reject any entry that does not parse with KaTeX.

Set source_job_id to {source_id} and source_response_sha256 to {source_hash}.

SOURCE SUBMISSION:
{json.dumps(source, indent=2, sort_keys=True)}
"""

    def _render_check(self, response: dict[str, Any]) -> dict[str, Any]:
        script = self.paths.workspace / "dashboard" / "scripts" / "validate-lemma-book.mjs"
        if not script.exists():
            raise AgentError(f"missing deterministic lemma renderer: {script}")
        node = shutil.which("node")
        if node is None:
            pnpm = shutil.which("pnpm")
            bundled = (Path(pnpm).resolve().parents[2] / "node" / "bin" / "node") if pnpm else None
            if bundled and bundled.exists():
                node = str(bundled)
        if node is None:
            raise AgentError("node executable not found for deterministic KaTeX validation")
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump(response, handle)
            temporary = Path(handle.name)
        try:
            completed = subprocess.run(
                [node, str(script), str(temporary)],
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
            detail = (completed.stderr or completed.stdout).strip()
            raise AgentError("lemma KaTeX validation failed: " + detail)
        return json.loads(completed.stdout)

    def _is_current(self, source_id: str, source_hash: str) -> bool:
        manifest = self.submissions / source_id / "manifest.json"
        if not manifest.exists():
            return False
        try:
            data = json.loads(manifest.read_text())
        except json.JSONDecodeError:
            return False
        return data.get("source_response_sha256") == source_hash and data.get("passed") is True

    def process_source(self, source_path: Path) -> dict[str, Any]:
        source_id = source_path.parent.name
        source = json.loads(source_path.read_text())
        source_hash = canonical_sha256(source)
        if self._is_current(source_id, source_hash):
            return {"source_job_id": source_id, "status": "current"}

        errors: list[str] = []
        max_attempts = int(self.cfg.get("lemma_writer_max_attempts", 4))
        for attempt in range(1, max_attempts + 1):
            prompt = self._prompt(source_id, source)
            if errors:
                prompt += "\n\nThe previous attempt was rejected for:\n- " + "\n- ".join(errors)
            response, metadata = self.provider.run(
                f"lemma-writer-{source_id}", prompt, LEMMA_BOOK_SCHEMA)
            errors = validate_editorial_response(source_id, source, response)
            if errors:
                continue
            try:
                render_validation = self._render_check(response)
            except AgentError as exc:
                errors = [str(exc)]
                continue

            out_dir = self.submissions / source_id
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "response.json").write_text(
                json.dumps(response, indent=2, sort_keys=True) + "\n")
            (out_dir / "manifest.json").write_text(json.dumps({
                "schema": "line-point-concrete-lemma-book-entry-v1",
                "source_job_id": source_id,
                "source_response_sha256": source_hash,
                "editorial_rule": LEMMA_STATEMENT_RULE,
                "model": self.provider.model,
                "reasoning_effort": self.provider.reasoning_effort,
                "agent": metadata,
                "attempt": attempt,
                "passed": True,
                "render_validation": render_validation,
                "written_at": utc_timestamp(),
            }, indent=2, sort_keys=True) + "\n")
            return {
                "source_job_id": source_id,
                "status": "edited",
                "lemmas": len(response["lemmas"]),
            }

        raise AgentError(
            f"lemma writer exhausted {max_attempts} attempts for {source_id}: " + "; ".join(errors))

    def source_paths(self) -> list[Path]:
        root = self.paths.campaign_dir / "submissions"
        return sorted(root.glob("*/response.json")) if root.exists() else []

    def export_snapshot(self) -> dict[str, Any]:
        lemmas: list[dict[str, Any]] = []
        edited_sources = 0
        source_paths = self.source_paths()
        for source_path in source_paths:
            source_id = source_path.parent.name
            source = json.loads(source_path.read_text())
            source_hash = canonical_sha256(source)
            edited_path = self.submissions / source_id / "response.json"
            manifest_path = self.submissions / source_id / "manifest.json"
            edited = None
            if edited_path.exists() and manifest_path.exists():
                manifest = json.loads(manifest_path.read_text())
                if manifest.get("passed") and manifest.get("source_response_sha256") == source_hash:
                    edited = json.loads(edited_path.read_text())
            if edited:
                edited_sources += 1
                for lemma in edited.get("lemmas", []):
                    lemmas.append({
                        **lemma,
                        "source_job_id": source_id,
                        "editorial_status": "polished",
                    })
        payload = {
            "editorial_rule": LEMMA_STATEMENT_RULE,
            "model": self.provider.model,
            "reasoning_effort": self.provider.reasoning_effort,
            "source_count": len(source_paths),
            "edited_source_count": edited_sources,
            "lemma_count": len(lemmas),
            "updated_at": utc_timestamp(),
            "lemmas": lemmas,
        }
        (self.root / "lemma-book.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n")
        update_dashboard_sections(self.paths.workspace, {"lemma_book": payload})
        return payload

    def run(self, watch: bool = False) -> dict[str, Any]:
        while True:
            pending = []
            for source_path in self.source_paths():
                source = json.loads(source_path.read_text())
                if not self._is_current(source_path.parent.name, canonical_sha256(source)):
                    pending.append(source_path)
            for source_path in pending:
                try:
                    self.process_source(source_path)
                except AgentError as exc:
                    error_path = self.runtime / f"{source_path.parent.name}.error.txt"
                    error_path.write_text(f"{utc_timestamp()} {exc}\n")
                finally:
                    self.export_snapshot()
            result = self.export_snapshot()
            if not watch or (self.paths.campaign_dir / "COMPLETED").exists():
                return result
            time.sleep(int(self.cfg.get("lemma_writer_poll_seconds", 30)))


def launch_lemma_book(config_path: Path | str) -> dict[str, Any]:
    editor = LemmaBookEditor(config_path)
    pid_path = editor.runtime / "runner.json"
    if pid_path.exists():
        old = json.loads(pid_path.read_text())
        try:
            os.kill(int(old["pid"]), 0)
            return {"status": "already_running", **old}
        except (OSError, KeyError, ValueError):
            pass
    log_path = editor.runtime / "lemma-writer.log"
    log_handle = log_path.open("a")
    environment = os.environ.copy()
    source_path = str(editor.paths.workspace / "src")
    environment["PYTHONPATH"] = (
        source_path + os.pathsep + environment["PYTHONPATH"]
        if environment.get("PYTHONPATH") else source_path)
    environment["PYTHONPYCACHEPREFIX"] = str(editor.runtime / "python-cache")
    process = subprocess.Popen(
        [sys.executable, "-m", "line_point_research", "lemma-book-run",
         str(Path(config_path).resolve()), "--watch"],
        cwd=editor.paths.workspace,
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
