from __future__ import annotations

import hashlib
import json
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any


class AgentError(RuntimeError):
    pass


class CommandAgentProvider:
    """Run an independent ephemeral Codex process and retain its full trace."""

    def __init__(self, workspace: Path | str, log_dir: Path | str,
                 executable: str = "codex", model: str | None = None,
                 timeout_seconds: int = 900,
                 reasoning_effort: str | None = None,
                 disable_nested_agents: bool = True,
                 checkpoint_root: Path | str | None = None):
        self.workspace = Path(workspace).resolve()
        self.log_dir = Path(log_dir).resolve()
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.executable = executable
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.reasoning_effort = reasoning_effort
        self.disable_nested_agents = disable_nested_agents
        self.checkpoint_root = Path(checkpoint_root).resolve() if checkpoint_root else None

    def command(self, schema_path: Path, output_path: Path,
                checkpoint_dir: Path | None = None) -> list[str]:
        command = [self.executable, "exec", "--ephemeral", "--sandbox", "read-only",
                   "--cd", str(self.workspace), "--output-schema", str(schema_path),
                   "--output-last-message", str(output_path), "-"]
        prefix: list[str] = []
        if self.model:
            prefix.extend(["--model", self.model])
        if self.reasoning_effort:
            prefix.extend(["--config", f'model_reasoning_effort="{self.reasoning_effort}"'])
        if self.disable_nested_agents:
            prefix.extend(["--disable", "multi_agent"])
        if checkpoint_dir is not None:
            prefix.extend(["--add-dir", str(checkpoint_dir)])
        command[2:2] = prefix
        return command

    def run(self, role: str, prompt: str,
            schema: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        invocation_id = (time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + "-" +
                         hashlib.sha256((role + prompt).encode()).hexdigest()[:10] + "-" +
                         uuid.uuid4().hex[:10])
        invocation_dir = self.log_dir / invocation_id
        invocation_dir.mkdir(parents=True, exist_ok=True)
        prompt_path = invocation_dir / "prompt.txt"
        schema_path = invocation_dir / "schema.json"
        output_path = invocation_dir / "response.json"
        stderr_path = invocation_dir / "stderr.txt"
        checkpoint_dir: Path | None = None
        effective_prompt = prompt
        if self.checkpoint_root is not None:
            checkpoint_dir = self.checkpoint_root / role
            checkpoint_dir.mkdir(parents=True, exist_ok=True)
            effective_prompt += f"""

LIVE RESEARCH CHECKPOINTS
Your assigned writable checkpoint outbox is {checkpoint_dir}. The rest of the research corpus is
read-only. As soon as you have a concrete reusable mathematical artifact, write a concise Markdown
checkpoint there using apply_patch; do not wait for your final response. Examples are a quantified
lemma, exact inequality, parameter certificate, counterexample, obstruction, or named proof route.
Use monotonically numbered filenames such as 001-component-bound.md. Put STATUS: proved,
conditional, conjectural, refuted, or computation at the top, followed by the statement, evidence
or proof, exact dependencies, and intended downstream use. Update or supersede the checkpoint when
your conclusion changes. Do not publish raw private scratch reasoning or vague brainstorming.
These files are automatically committed and uploaded for the rest of the team.
"""
        prompt_path.write_text(effective_prompt)
        schema_path.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n")
        command = self.command(schema_path, output_path, checkpoint_dir)
        try:
            completed = subprocess.run(
                command, input=effective_prompt, text=True, stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE, timeout=self.timeout_seconds, check=False)
            stderr_path.write_text(completed.stderr)
        except subprocess.TimeoutExpired as exc:
            stderr_path.write_text((exc.stderr or "") +
                                   f"\nTimed out after {self.timeout_seconds} seconds.\n")
            raise AgentError(f"{role} agent timed out; see {stderr_path}") from exc
        if completed.returncode != 0 or not output_path.exists():
            raise AgentError(
                f"{role} agent failed with exit code {completed.returncode}; see {stderr_path}")
        try:
            response = json.loads(output_path.read_text())
        except json.JSONDecodeError as exc:
            raise AgentError(f"{role} agent returned invalid JSON; see {output_path}") from exc
        metadata = {
            "role": role,
            "model": self.model,
            "reasoning_effort": self.reasoning_effort,
            "nested_agents_disabled": self.disable_nested_agents,
            "invocation_id": invocation_id,
            "command": command[:-1],
            "response_path": str(output_path),
            "checkpoint_dir": str(checkpoint_dir) if checkpoint_dir else None,
        }
        return response, metadata
