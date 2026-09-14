from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .agents import AgentError, CommandAgentProvider
from .snapshot import update_dashboard_sections


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


PROOF_STEP = {
    "type": "object", "additionalProperties": False,
    "required": ["id", "statement", "status", "proof", "dependencies"],
    "properties": {
        "id": {"type": "string"},
        "statement": {"type": "string"},
        "status": {"type": "string", "enum": ["proved", "conditional", "conjectural", "refuted"]},
        "proof": {"type": "string"},
        "dependencies": {"type": "array", "items": {"type": "string"}},
    },
}


SOUNDNESS_STAGE = {
    "type": "object", "additionalProperties": False,
    "required": ["stage", "input_bound", "output_bound", "loss", "justification", "status"],
    "properties": {
        "stage": {"type": "string"},
        "input_bound": {"type": "string"},
        "output_bound": {"type": "string"},
        "loss": {"type": "string"},
        "justification": {"type": "string"},
        "status": {"type": "string", "enum": ["proved", "conditional", "conjectural", "refuted"]},
    },
}


LITERATURE_DEPENDENCY = {
    "type": "object", "additionalProperties": False,
    "required": ["paper", "version", "result_id", "hypotheses", "used_for"],
    "properties": {
        "paper": {"type": "string"},
        "version": {"type": "string"},
        "result_id": {"type": "string"},
        "hypotheses": {"type": "string"},
        "used_for": {"type": "string"},
    },
}


RESEARCH_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["title", "dimension", "field_regime", "result_status", "claim_scope", "benchmark_improved",
                 "fixed_prime", "fixed_degree", "claimed_soundness", "theorem_statement", "parameter_regime",
                 "sampling_model", "global_conclusion", "literature_dependencies",
                 "proof_steps", "soundness_ledger", "counterexample_attempts",
                 "characteristic_audit", "finite_sanity_checks", "obstructions",
                 "next_tasks", "note_markdown"],
    "properties": {
        "title": {"type": "string"},
        "dimension": {"type": "integer", "const": 2},
        "field_regime": {"type": "string", "enum": ["prime"]},
        "fixed_prime": {"type": "integer", "const": 147457},
        "fixed_degree": {"type": "integer", "const": 87},
        "result_status": {"type": "string", "enum": ["proved", "conditional", "conjectural", "refuted"]},
        "claim_scope": {"type": "string", "enum": ["bivariate_theorem", "algebraic_lemma", "combinatorial_lemma", "obstruction", "counterexample", "proof_tool"]},
        "benchmark_improved": {"type": "boolean"},
        "claimed_soundness": {"type": ["number", "null"], "exclusiveMinimum": 0, "maximum": 1},
        "theorem_statement": {"type": "string"},
        "parameter_regime": {"type": "string"},
        "sampling_model": {"type": "string"},
        "global_conclusion": {"type": "string"},
        "literature_dependencies": {"type": "array", "items": LITERATURE_DEPENDENCY},
        "proof_steps": {"type": "array", "items": PROOF_STEP},
        "soundness_ledger": {"type": "array", "items": SOUNDNESS_STAGE},
        "counterexample_attempts": {"type": "array", "items": {"type": "string"}},
        "characteristic_audit": {"type": "array", "items": {"type": "string"}},
        "finite_sanity_checks": {"type": "array", "items": {"type": "string"}},
        "obstructions": {"type": "array", "items": {"type": "string"}},
        "next_tasks": {"type": "array", "items": {"type": "string"}},
        "note_markdown": {"type": "string"},
    },
}


GENIUS_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["title", "dimension", "field_regime", "fixed_prime", "fixed_degree", "result_status", "benchmark_improved", "snapshot", "evidence_ledger", "bottleneck_map",
                 "architectures", "selected_architecture_id", "integrated_theorem",
                 "fixed_prime", "fixed_degree", "claimed_soundness", "proof_steps", "soundness_ledger",
                 "counterexample_attempts", "research_directives", "limitations",
                 "abstain_reason", "note_markdown"],
    "properties": {
        "title": {"type": "string"},
        "dimension": {"type": "integer", "const": 2},
        "field_regime": {"type": "string", "enum": ["prime"]},
        "fixed_prime": {"type": "integer", "const": 147457},
        "fixed_degree": {"type": "integer", "const": 87},
        "result_status": {"type": "string", "enum": ["proved", "conditional", "conjectural", "refuted"]},
        "benchmark_improved": {"type": "boolean"},
        "snapshot": {
            "type": "object", "additionalProperties": False,
            "required": ["data_manifest_sha256", "durable_file_count", "examined_paths",
                         "omitted_paths", "coverage_complete"],
            "properties": {
                "data_manifest_sha256": {"type": "string"},
                "durable_file_count": {"type": "integer"},
                "examined_paths": {"type": "array", "items": {"type": "string"}},
                "omitted_paths": {"type": "array", "items": {"type": "string"}},
                "coverage_complete": {"type": "boolean"},
            },
        },
        "evidence_ledger": {
            "type": "array", "items": {
                "type": "object", "additionalProperties": False,
                "required": ["claim_id", "statement", "status", "supporting_paths"],
                "properties": {
                    "claim_id": {"type": "string"},
                    "statement": {"type": "string"},
                    "status": {"type": "string", "enum": ["proved", "conditional", "conjectural", "refuted"]},
                    "supporting_paths": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
        "bottleneck_map": {"type": "array", "items": SOUNDNESS_STAGE},
        "architectures": {
            "type": "array", "items": {
                "type": "object", "additionalProperties": False,
                "required": ["id", "name", "claimed_soundness", "core_idea", "proved_components",
                             "missing_obligations", "known_attacks", "priority"],
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "claimed_soundness": {"type": ["number", "null"], "exclusiveMinimum": 0, "maximum": 1},
                    "core_idea": {"type": "string"},
                    "proved_components": {"type": "array", "items": {"type": "string"}},
                    "missing_obligations": {"type": "array", "items": {"type": "string"}},
                    "known_attacks": {"type": "array", "items": {"type": "string"}},
                    "priority": {"type": "integer"},
                },
            },
        },
        "selected_architecture_id": {"type": ["string", "null"]},
        "integrated_theorem": {"type": "string"},
        "claimed_soundness": {"type": ["number", "null"], "exclusiveMinimum": 0, "maximum": 1},
        "proof_steps": {"type": "array", "items": PROOF_STEP},
        "soundness_ledger": {"type": "array", "items": SOUNDNESS_STAGE},
        "counterexample_attempts": {"type": "array", "items": {"type": "string"}},
        "research_directives": {"type": "array", "items": {"type": "string"}},
        "limitations": {"type": "array", "items": {"type": "string"}},
        "abstain_reason": {"type": ["string", "null"]},
        "note_markdown": {"type": "string"},
    },
}


AUDIT_ITEM = {
    "type": "object", "additionalProperties": False,
    "required": ["reference", "claim", "verdict", "justification"],
    "properties": {
        "reference": {"type": "string"},
        "claim": {"type": "string"},
        "verdict": {"type": "string", "enum": ["valid", "gap", "false", "unclear"]},
        "justification": {"type": "string"},
    },
}


AUDIT_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["verdict", "unfixable", "verified_claim_sha256", "dimension_verified",
                 "field_regime_verified", "fixed_prime_verified", "fixed_degree_verified", "scope_verified",
                 "benchmark_improved", "verified_soundness", "recovery_ratio_verified", "fatal_obstruction",
                 "coverage_complete", "quantifier_audit", "soundness_audit",
                 "literature_audit", "line_audit", "required_changes",
                 "counterexample_attempts", "summary"],
    "properties": {
        "verdict": {"type": "string", "enum": ["accept", "revise", "reject"]},
        "unfixable": {"type": "boolean"},
        "verified_claim_sha256": {"type": ["string", "null"]},
        "dimension_verified": {"type": "boolean"},
        "field_regime_verified": {"type": "boolean"},
        "fixed_prime_verified": {"type": "boolean"},
        "fixed_degree_verified": {"type": "boolean"},
        "scope_verified": {"type": "string", "enum": ["none", "bivariate_theorem", "algebraic_lemma", "combinatorial_lemma", "obstruction", "counterexample", "proof_tool"]},
        "benchmark_improved": {"type": "boolean"},
        "verified_soundness": {"type": ["number", "null"], "exclusiveMinimum": 0, "maximum": 1},
        "recovery_ratio_verified": {"type": "boolean"},
        "fatal_obstruction": {"type": ["string", "null"]},
        "coverage_complete": {"type": "boolean"},
        "quantifier_audit": {"type": "array", "items": AUDIT_ITEM},
        "soundness_audit": {"type": "array", "items": AUDIT_ITEM},
        "literature_audit": {"type": "array", "items": AUDIT_ITEM},
        "line_audit": {"type": "array", "items": AUDIT_ITEM},
        "required_changes": {"type": "array", "items": {"type": "string"}},
        "counterexample_attempts": {"type": "array", "items": {"type": "string"}},
        "summary": {"type": "string"},
    },
}


DIRECTIONS = [
    "KTZ parameter hack 1: reproduce the bivariate KTZ proof as an exact finite optimization problem, jointly tune every popularity, pruning, interpolation, and cleanup threshold at p=147457 and d=87, and submit the best rigorously derived numerical epsilon",
    "KTZ parameter hack 2: replace each coarse Markov, union-bound, and integer-rounding choice in KTZ by the sharp fixed-instance inequality, search the admissible rational parameter region, and submit a concrete improved epsilon with a complete loss ledger",
    "KTZ parameter hack 3: optimize the weighted-interpolation multiplicities and monomial region in the KTZ architecture for p=147457 and d=87, using exact integer arithmetic and a reproducible certificate for every finite inequality",
    "KTZ parameter hack 4: optimize incidence pruning, popular points, popular lines, and exceptional-direction thresholds in the KTZ architecture simultaneously rather than sequentially, with the leaderboard epsilon as the primary objective",
    "KTZ parameter hack 5: tighten the resultant, Bezout, discriminant, separability, and exceptional-line constants in the KTZ proof at the fixed prime and propagate every marginal saving to one explicit final soundness value",
    "new architecture 1: seek a genuinely different bivariate proof using affine-plane directions and pencils through popular points; target a discontinuous improvement over the tuned KTZ constant, not a general-dimensional theorem",
    "new architecture 2: seek a higher-moment, energy-increment, or dependent-random-choice replacement for KTZ popularity pruning that preserves substantially more accepted incidence mass and yields an explicit fixed-instance epsilon",
    "new architecture 3: seek an algebraic reconstruction argument that exploits d=87 and p=147457 directly, including nonrectangular interpolation regions, Hasse derivatives, or curve geometry unavailable to the generic asymptotic proof",
    "new architecture 4: search for a direct agreement theorem across line pencils or directions that avoids the lossy list-to-one-polynomial conversion and gives a substantially smaller concrete epsilon",
    "new architecture 5: combine compatible verified lemmas from the shared corpus into a new end-to-end soundness proof, but judge success solely by the concrete doubly-verifiable leaderboard epsilon",
    "use direction structure in the fixed affine plane",
    "derive a finite-field energy increment with explicit constants",
    "specialize bivariate Reed--Muller list recovery to d=87",
    "convert a polynomial list into one polynomial with explicit agreement",
    "search for adversarial line and point tables that limit the theorem",
    "derive a direct affine-plane proof avoiding lossy generic lemmas",
    "exploit pencils of accepted lines through popular points",
    "prove direction-by-direction consistency with exact counts",
    "construct a machine-checkable integer or rational certificate",
    "optimize the final epsilon-to-epsilon/10 recovery step",
]


LITERATURE_DIRECTION = """Establish the campaign's rigorous state-of-the-art baseline from
primary literature. Locate the strongest published or publicly posted theorem actually
applicable to the uniform affine line-versus-point test on F_147457^2 with total degree 87,
including Kominers--Thaler--Zheng and any later refinement. Record exact paper versions,
theorem or lemma numbers, hypotheses, constants, and the exact conversion from the source's
agreement conclusion to this campaign's epsilon/10 convention. Compare all applicable
candidates and explain mathematical dominance. Never infer a numerical constant hidden by
O-notation or an existence statement: if the primary theorem does not expose enough constants
to calculate a concrete epsilon, record that obstruction and do not invent a leaderboard point."""


SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS campaign_meta (
  key TEXT PRIMARY KEY, value_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS campaign_jobs (
  id TEXT PRIMARY KEY, role TEXT NOT NULL, ordinal INTEGER, direction TEXT,
  dependency TEXT, status TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0,
  max_attempts INTEGER NOT NULL, output_dir TEXT, error TEXT,
  model TEXT NOT NULL, reasoning_effort TEXT NOT NULL,
  created_at TEXT NOT NULL, started_at TEXT, finished_at TEXT
);
"""


@dataclass
class CampaignPaths:
    config: Path
    workspace: Path
    campaign_dir: Path
    corpus_root: Path


def load_campaign_config(path: Path | str) -> tuple[dict[str, Any], CampaignPaths]:
    config_path = Path(path).resolve()
    config = yaml.safe_load(config_path.read_text())
    if not isinstance(config, dict):
        raise ValueError("campaign configuration must be a YAML mapping")
    campaign = config.get("campaign", {})
    count = int(campaign.get("researcher_count", 0))
    if count < 1:
        raise ValueError("campaign.researcher_count must be at least 1")
    effort = str(campaign.get("reasoning_effort", ""))
    if effort != "ultra":
        raise ValueError("campaign.reasoning_effort must be ultra")
    if int(campaign.get("dimension", 2)) != 2:
        raise ValueError("campaign.dimension must be exactly 2")
    if str(campaign.get("field_regime", "prime")) != "prime":
        raise ValueError("campaign.field_regime must be prime")
    if int(campaign.get("fixed_prime", 0)) != 147457:
        raise ValueError("campaign.fixed_prime must be 147457")
    if int(campaign.get("fixed_degree", 0)) != 87:
        raise ValueError("campaign.fixed_degree must be 87")
    if int(campaign.get("verifier_count", 0)) != 2:
        raise ValueError("campaign.verifier_count must be exactly 2")
    if int(campaign.get("recovery_divisor", 0)) != 10:
        raise ValueError("campaign.recovery_divisor must be 10")
    base = config_path.parent

    def resolve(value: str) -> Path:
        candidate = Path(value)
        return (base / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()

    paths = CampaignPaths(
        config_path,
        resolve(config.get("workspace", "..")),
        resolve(config["campaign_dir"]),
        resolve(config.get("corpus_root", "../research_state")),
    )
    return config, paths


class ResearchCampaign:
    def __init__(self, config_path: Path | str):
        self.config, self.paths = load_campaign_config(config_path)
        self.cfg = self.config["campaign"]
        self.paths.campaign_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.paths.campaign_dir / "campaign.sqlite3"
        self.lock = threading.Lock()
        self.provider = CommandAgentProvider(
            self.paths.workspace,
            self.paths.campaign_dir / "agent_logs",
            executable=str(self.cfg.get("executable", "codex")),
            model=str(self.cfg.get("model", "gpt-5.6-sol")),
            reasoning_effort=str(self.cfg.get("reasoning_effort", "ultra")),
            disable_nested_agents=bool(self.cfg.get("disable_nested_agents", True)),
            timeout_seconds=int(self.cfg.get("timeout_seconds", 3600)),
        )
        self.max_workers = int(self.cfg.get("max_workers", 4))
        self.retry_seconds = int(self.cfg.get("retry_seconds", 120))

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=60)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self, recover_running: bool = True) -> None:
        with self.connect() as connection:
            connection.executescript(SCHEMA)
            connection.execute("INSERT OR REPLACE INTO campaign_meta VALUES (?,?)",
                               ("config", json.dumps(self.config, sort_keys=True)))
            connection.execute("INSERT OR REPLACE INTO campaign_meta VALUES (?,?)",
                               ("created_or_resumed_at", json.dumps(utc_timestamp())))
            if recover_running:
                connection.execute(
                    "UPDATE campaign_jobs SET status='queued',error='recovered stale running lease' WHERE status='running'")
            for ordinal in range(1, int(self.cfg["researcher_count"]) + 1):
                job_id = f"researcher-{ordinal:04d}"
                direction = DIRECTIONS[(ordinal - 1) % len(DIRECTIONS)]
                connection.execute(
                    """INSERT OR IGNORE INTO campaign_jobs
                    (id,role,ordinal,direction,dependency,status,max_attempts,model,reasoning_effort,created_at)
                    VALUES (?,?,?,?,?,'queued',?,?,?,?)""",
                    (job_id, "researcher", ordinal, direction, None,
                     int(self.cfg.get("max_attempts", 8)), self.provider.model,
                     self.provider.reasoning_effort, utc_timestamp()),
                )
                connection.execute(
                    "UPDATE campaign_jobs SET direction=? WHERE id=? AND role='researcher' "
                    "AND status='queued' AND attempts=0",
                    (direction, job_id),
                )
            self._insert_literature_agent(connection)
            if bool(self.cfg.get("genius_enabled", True)):
                connection.execute(
                    """INSERT OR IGNORE INTO campaign_jobs
                    (id,role,ordinal,direction,dependency,status,max_attempts,model,reasoning_effort,created_at)
                    VALUES ('GENIUS','genius',NULL,?,'__swarm_reviews__','queued',?,?,?,?)""",
                    ("global synthesis of the strongest fixed-instance soundness theorem",
                     int(self.cfg.get("max_attempts", 8)), self.provider.model,
                     self.provider.reasoning_effort, utc_timestamp()),
                )
                connection.execute(
                    "UPDATE campaign_jobs SET direction=? WHERE id='GENIUS' AND role='genius' "
                    "AND status='queued' AND attempts=0",
                    ("global synthesis of the strongest fixed-instance soundness theorem",),
                )
        self.export_status()

    def _insert_literature_agent(self, connection: sqlite3.Connection) -> None:
        if not bool(self.cfg.get("literature_agent_enabled", True)):
            return
        connection.execute(
            """INSERT OR IGNORE INTO campaign_jobs
            (id,role,ordinal,direction,dependency,status,max_attempts,model,reasoning_effort,created_at)
            VALUES ('literature-sota-0001','researcher',0,?,NULL,'queued',?,?,?,?)""",
            (LITERATURE_DIRECTION, int(self.cfg.get("max_attempts", 8)), self.provider.model,
             self.provider.reasoning_effort, utc_timestamp()),
        )
        connection.execute(
            "UPDATE campaign_jobs SET direction=? WHERE id='literature-sota-0001' "
            "AND role='researcher' AND status='queued' AND attempts=0",
            (LITERATURE_DIRECTION,),
        )

    def rebalance_for_leaderboard(self) -> dict[str, Any]:
        """Add the literature seat and retarget untouched researchers at concrete epsilon."""
        with self.connect() as connection:
            connection.executescript(SCHEMA)
            self._insert_literature_agent(connection)
            for ordinal in range(1, int(self.cfg["researcher_count"]) + 1):
                direction = DIRECTIONS[(ordinal - 1) % len(DIRECTIONS)]
                connection.execute(
                    "UPDATE campaign_jobs SET direction=? WHERE id=? AND role='researcher' "
                    "AND status='queued' AND attempts=0",
                    (direction, f"researcher-{ordinal:04d}"),
                )
        return self.export_status()

    def _ready(self, limit: int) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = [dict(row) for row in connection.execute(
                "SELECT * FROM campaign_jobs WHERE status='queued' "
                "ORDER BY CASE role WHEN 'verifier' THEN 0 WHEN 'researcher' THEN 1 ELSE 2 END, ordinal, id")]
            all_jobs = [dict(row) for row in connection.execute(
                "SELECT id,role,status FROM campaign_jobs")]
        states = {row["id"]: row["status"] for row in all_jobs}
        ready: list[dict[str, Any]] = []
        for row in rows:
            dependency = row["dependency"]
            if dependency is None:
                ready.append(row)
            elif dependency == "__swarm_reviews__":
                researcher_terminal = all(
                    states.get(f"researcher-{index:04d}") in {"succeeded", "failed"}
                    for index in range(1, int(self.cfg["researcher_count"]) + 1))
                successful = [item["id"] for item in all_jobs
                              if item["role"] == "researcher" and item["status"] == "succeeded"]
                verifier_terminal = all(
                    states.get(f"verifier-{seat}-{source_id}") in {"succeeded", "failed"}
                    for source_id in successful for seat in ("a", "b"))
                if researcher_terminal and verifier_terminal:
                    ready.append(row)
            elif states.get(dependency) == "succeeded":
                ready.append(row)
            if len(ready) >= limit:
                break
        return ready

    def _claim(self, job_id: str) -> bool:
        with self.lock, self.connect() as connection:
            changed = connection.execute(
                """UPDATE campaign_jobs SET status='running',attempts=attempts+1,
                started_at=?,error=NULL WHERE id=? AND status='queued'""",
                (utc_timestamp(), job_id)).rowcount
        return changed == 1

    def _enqueue_verifier(self, source_id: str) -> None:
        if not bool(self.cfg.get("verifier_enabled", True)):
            return
        with self.lock, self.connect() as connection:
            for seat in ("a", "b"):
                verifier_id = f"verifier-{seat}-{source_id}"
                connection.execute(
                    """INSERT OR IGNORE INTO campaign_jobs
                    (id,role,ordinal,direction,dependency,status,max_attempts,model,reasoning_effort,created_at)
                    VALUES (?, 'verifier', NULL, ?, ?, 'queued', ?, ?, ?, ?)""",
                    (verifier_id, f"independent verifier {seat.upper()} audit of {source_id}", source_id,
                     int(self.cfg.get("max_attempts", 8)), self.provider.model,
                     self.provider.reasoning_effort, utc_timestamp()),
                )

    def _corpus_instruction(self) -> str:
        return f"""The repository is {self.paths.workspace}. The durable corpus root is
{self.paths.corpus_root}. Begin by reading TARGET.md, references/LITERATURE.md,
references/bibliography.json, research_state/DATA_MANIFEST.json, all prior submissions,
leaderboards, and verifier audits. You have a read-only shell. Treat literature summaries as
navigation aids and identify exact primary-source theorem dependencies. Distinguish quoted
theorems from your own fixed-parameter derivation. Exact deterministic computation may certify
finite inequalities only with reproducible code and a checkable certificate; floating-point or
randomized evidence is not proof. Ignore every directory named
superseded: those files are retained only as provenance and are not part of the active corpus.

{self._leaderboard_instruction()}"""

    def _leaderboard_instruction(self) -> str:
        history_path = self.paths.campaign_dir / "leaderboards" / "soundness-history.json"
        points: list[dict[str, Any]] = []
        if history_path.exists():
            try:
                points = list(json.loads(history_path.read_text()).get("points", []))
            except (json.JSONDecodeError, OSError, TypeError):
                points = []
        if points:
            best = min(float(point["soundness"]) for point in points)
            record = f"The current doubly verified leaderboard record is epsilon={best:.17g}."
        else:
            initial = float(self.cfg.get("initial_soundness", 1.0))
            record = (
                "There is no doubly verified leaderboard point yet; "
                f"the comparison threshold is epsilon={initial:.17g}.")
        return f"""LEADERBOARD OBJECTIVE: {record} Read the authoritative history at
{history_path}. Every constructive choice must be evaluated by whether it can produce a smaller
fully proved numerical epsilon for the fixed instance. Do not optimize elegance, generality,
roadmap completeness, or exposition at the expense of that objective. Conditional work is
useful only when it isolates the shortest concrete route to a smaller certifiable epsilon."""

    def _research_prompt(self, row: dict[str, Any]) -> str:
        if row["id"] == "literature-sota-0001":
            return self._literature_prompt(row)
        modes = ["proof-first", "bottleneck-first", "adversarial", "synthesis-first"]
        mode = modes[(int(row["ordinal"]) - 1) % len(modes)]
        return f"""You are {row['id']}, one of {self.cfg['researcher_count']} independent
mathematical research agents improving soundness of the affine line-versus-point low-degree
test. Your assigned direction is: {row['direction']}. Your mode is {mode}. Your primary objective
is to lower the concrete leaderboard epsilon; proof roadmaps are shared reference material, not
your principal deliverable.

{self._corpus_instruction()}

The instance is immutable: m=2, p=147457, and total degree d=87. The verifier samples a uniformly
random affine line in F_p^2 and then a uniformly random point on it. A number epsilon in (0,1]
is a verified soundness bound if every line table and point table accepted with probability at
least epsilon admits a total-degree-at-most-87 bivariate polynomial agreeing with the point
table on at least epsilon/10 of all p^2 points. Lower epsilon is stronger. Do genuine
mathematical work: isolate one bottleneck, optimize exact constants, attempt a new lemma or
counterexample, and write a fully quantified fixed-instance result.

Do not work on m>2, dimension bootstrapping, extension fields, or descent: the standard
general-dimensional lift is a routine downstream corollary and earns no campaign credit. Do not
silently change uniform affine-line sampling, replace total degree by individual degree, vary the
fixed parameters, or return only a large list of candidate global polynomials.

Every numerical loss must appear in the soundness ledger. State p=147457, d=87, acceptance
epsilon, all auxiliary parameters, and the final epsilon/10 agreement. Use exact rational or
integer arithmetic whenever possible. Audit division
by derivatives, discriminants, irreducibility, interpolation multiplicities, and every
union/Markov/Cauchy--Schwarz loss. Test adversarial tables, inseparability, and concentrated good
directions. A rigorous obstruction or correction is valuable. Set benchmark_improved=true only
when the proved claimed_soundness is below the current doubly verified record; the initial
comparison threshold is 1. Set dimension=2, field_regime=prime, fixed_prime=147457, and
fixed_degree=87 in the structured response.

Return a standard academic Markdown note with Abstract, Test and Notation, Prior Results,
Theorem, Proof or Conditional Proof, Soundness Ledger, Counterexample Attempts,
Characteristic Audit, and Limitations. Number all proof steps [P1], [P2], ... and mark each as
proved, conditional, conjectural, or refuted. RULE: A lemma statement contains only its
quantified objects, hypotheses, and conclusion. It contains no motivation, derivation,
commentary, proof sketch, interpretation, history, or explanation; put all such material in the
proof. A dedicated Lemma Writer will post-edit and may split a lemma without changing its content.
"""

    def _genius_prompt(self) -> str:
        return f"""You are GENIUS, the global proof-synthesis mathematician for the
line-versus-point concrete campaign. You must inspect the complete accumulated corpus and attempt
an integrated proof of the lowest valid soundness epsilon for the fixed instance. Your sole
research objective is a new doubly verifiable leaderboard record; do not optimize roadmap
coverage or generality for its own sake.

{self._corpus_instruction()}

Inspect every submission and audit under {self.paths.campaign_dir}. Produce a coverage receipt
and abstain from a global theorem if material data are omitted. Reconstruct a single normalized
soundness ledger for the m=2 prime-field portions of Arora--Sudan, HKSS, KTZ, and every new
architecture, specialized all the way to p=147457 and d=87. Identify whether each loss is
algebraic, incidence-combinatorial, probabilistic, list-decoding, or numerical.

Propose at most three compatible proof architectures. For the selected architecture, state one
exact theorem with all quantifiers and write every dependency as a numbered proof step. A claimed
soundness improvement requires every stage to be proved; otherwise publish the strongest honest
conditional theorem and its minimal missing obligations. Red-team small prime characteristic,
inseparability, adversarial line tables, and conversion from a list to one global polynomial.
Work only with m=2 over F_147457 at total degree 87; do not spend effort on higher dimension or
extension fields. Lower epsilon is stronger, and recovered point agreement must be at least
epsilon/10. Set dimension=2, field_regime=prime, fixed_prime=147457, and fixed_degree=87. Do not average
incompatible lemmas or use finite evidence as proof.

Set result_status=proved and benchmark_improved=true only if every dependency is proved and the
claimed_soundness strictly improves the current doubly verified record. Otherwise record the
honest status and set benchmark_improved=false.

RULE: Every lemma statement must contain only its quantified objects, hypotheses, and conclusion.
Put all motivation, derivation, commentary, proof sketches, interpretation, history, and
explanation in the proof. A dedicated Lemma Writer will post-edit and may split a lemma without
changing its content.
"""

    def _literature_prompt(self, row: dict[str, Any]) -> str:
        return f"""You are {row['id']}, the dedicated state-of-the-art literature researcher for
the concrete line-versus-point campaign.

{self._corpus_instruction()}

Your assignment is: {row['direction']}

Search primary sources, including Arora--Sudan, HKSS, Kominers--Thaler--Zheng, revisions of
those works, and later papers that cite or sharpen the relevant theorem. The target is exactly
m=2 over the prime field F_147457, total degree d=87, with a uniformly random affine line and
then a uniformly random point on that line. Under the campaign convention, epsilon is valid
only if acceptance at least epsilon implies agreement of the point table with one bivariate
total-degree-at-most-87 polynomial on at least epsilon/10 of all p^2 points.

For every candidate baseline, give the exact title, authors, version/date, stable URL or
bibliographic identifier, result number, verbatim mathematical hypotheses in your own notation,
and a careful specialization to p=147457,d=87. Track the source's recovery constant and all
strict versus weak inequalities. Distinguish a theorem explicitly stated by the source from a
derivation you reconstructed. Compare candidates under identical sampling and degree
conventions. Do not treat asymptotic O-notation, an unspecified universal constant, or a
non-effective existence proof as a concrete number. If constants are insufficient, set
claimed_soundness=null, benchmark_improved=false, and state the smallest missing information.
Only set result_status=proved with a numerical claimed_soundness when the complete fixed-instance
conversion is rigorous and reproducible.

Write an academic Markdown note with Abstract, Scope and Test, Search Method, Exact Source
Results, Fixed-Parameter Specialization, State-of-the-Art Baseline, Soundness Ledger, and
Limitations. Number derivation steps [P1], [P2], ... . A lemma statement must contain only
quantified objects, hypotheses, and conclusion; all explanation belongs in its proof. Set
dimension=2, field_regime=prime, fixed_prime=147457, and fixed_degree=87.
"""

    def _verifier_prompt(self, source_id: str, verifier_id: str) -> str:
        source_dir = self.paths.campaign_dir / "submissions" / source_id
        response = json.loads((source_dir / "response.json").read_text())
        note = (source_dir / "note.md").read_text()
        numbered = "\n".join(
            f"{index:04d}: {line}" for index, line in enumerate(note.splitlines(), 1))
        claim = response.get("theorem_statement") or response.get("integrated_theorem", "")
        claim_hash = hashlib.sha256(claim.encode()).hexdigest()
        return f"""You are {verifier_id}, an independent hostile mathematical verifier. Audit submission
{source_id} line by line. You did not author it. Recompute every numerical bound and check every
quantifier, field hypothesis, sampling convention, literature dependency, and proof-step edge.
Accept only the exact claim whose SHA-256 is {claim_hash}; never silently weaken it.

Do not inspect, infer, or coordinate with the other verifier's audit. Your judgment must be
independent. The instance is exactly m=2, p=147457, total degree d=87, uniform affine-line then
uniform point sampling. The submitted epsilon is valid only if acceptance at least epsilon forces
agreement with one total-degree-at-most-87 bivariate polynomial on at least epsilon/10 of p^2
points. Lower epsilon is stronger.

An accept requires complete coverage; a correct exact soundness ledger; valid arithmetic at the
fixed prime; a proved conversion to the stated
single-polynomial global conclusion; no required changes; and no fatal obstruction. Use reject
with unfixable=true only for a concrete counterexample or false theorem. Use revise for repairable
gaps. Recompute the claimed epsilon and its epsilon/10 conclusion. Reject or request revision if
the proof changes p, d, m, sampling, total-degree convention, or the one-polynomial conclusion.
Set every fixed-parameter verification boolean true only after checking every theorem and lemma.
Exact deterministic computation is admissible only with reproducible code and a checkable
certificate; random or floating-point experiments cannot support accept.

{self._leaderboard_instruction()}

SUBMISSION MANIFEST:
{json.dumps(response, indent=2, sort_keys=True)}

NUMBERED NOTE:
{numbered}
"""

    def _static_check(self, role: str, response: dict[str, Any]) -> dict[str, Any]:
        note = response.get("note_markdown", "")
        errors: list[str] = []
        if len(note) < 1200:
            errors.append("academic note is shorter than 1200 characters")
        for heading in ("Abstract", "Theorem", "Soundness Ledger", "Limitations"):
            if heading.lower() not in note.lower():
                errors.append(f"missing {heading} section")
        if not response.get("proof_steps"):
            errors.append("no structured proof steps")
        if not response.get("soundness_ledger"):
            errors.append("no structured soundness ledger")
        if response.get("dimension") != 2:
            errors.append("submission dimension must be exactly 2")
        if response.get("field_regime") != "prime":
            errors.append("submission field_regime must be prime")
        if response.get("fixed_prime") != 147457:
            errors.append("submission fixed_prime must be 147457")
        if response.get("fixed_degree") != 87:
            errors.append("submission fixed_degree must be 87")
        if role in {"researcher", "genius"} and response.get("benchmark_improved"):
            if response.get("result_status") != "proved":
                errors.append("benchmark_improved requires result_status=proved")
            soundness = response.get("claimed_soundness")
            if not isinstance(soundness, (int, float)) or isinstance(soundness, bool):
                errors.append("benchmark_improved requires numeric claimed_soundness")
            elif not 0 < float(soundness) < float(self.cfg.get("initial_soundness", 1.0)):
                errors.append("claimed soundness must strictly improve the initial threshold")
        if role == "genius":
            snapshot = response.get("snapshot", {})
            if snapshot.get("coverage_complete") and snapshot.get("omitted_paths"):
                errors.append("coverage_complete conflicts with omitted_paths")
        return {
            "passed": not errors,
            "errors": errors,
            "note_sha256": hashlib.sha256(note.encode()).hexdigest(),
        }

    def _run_job(self, row: dict[str, Any]) -> tuple[str, bool, str | None]:
        role, job_id = row["role"], row["id"]
        try:
            if role == "researcher":
                response, metadata = self.provider.run(
                    job_id, self._research_prompt(row), RESEARCH_SCHEMA)
                schema = "line-point-concrete-submission-v1"
            elif role == "genius":
                response, metadata = self.provider.run(
                    "GENIUS", self._genius_prompt(), GENIUS_SCHEMA)
                schema = "line-point-concrete-genius-synthesis-v1"
            else:
                source_id = str(row["dependency"])
                response, metadata = self.provider.run(
                    job_id, self._verifier_prompt(source_id, job_id), AUDIT_SCHEMA)
                schema = "line-point-concrete-proof-audit-v1"

            if role == "verifier":
                source_id = str(row["dependency"])
                source_response = json.loads(
                    (self.paths.campaign_dir / "submissions" / source_id / "response.json").read_text())
                claim = source_response.get("theorem_statement") or source_response.get(
                    "integrated_theorem", "")
                expected = hashlib.sha256(claim.encode()).hexdigest()
                accept_consistent = (
                    response["verified_claim_sha256"] == expected and
                    response["dimension_verified"] and
                    response["field_regime_verified"] and
                    response["fixed_prime_verified"] and
                    response["fixed_degree_verified"] and
                    response["recovery_ratio_verified"] and
                    response["coverage_complete"] and
                    not response["required_changes"] and
                    response["fatal_obstruction"] is None and
                    response["line_audit"] and
                    response["quantifier_audit"] and
                    response["soundness_audit"] and
                    source_response.get("claimed_soundness") is not None and
                    response["verified_soundness"] == source_response.get("claimed_soundness") and
                    all(item["verdict"] == "valid" for key in (
                        "line_audit", "quantifier_audit", "soundness_audit", "literature_audit")
                        for item in response[key])
                )
                if response["verdict"] == "accept" and not accept_consistent:
                    response["verdict"] = "revise"
                    response["unfixable"] = False
                    response["fatal_obstruction"] = None
                    response["required_changes"] = list(response["required_changes"]) + [
                        "Harness rejected an internally inconsistent accept verdict."]
                out_dir = self.paths.campaign_dir / "reviews" / source_id / job_id
                out_dir.mkdir(parents=True, exist_ok=True)
                (out_dir / "audit.json").write_text(
                    json.dumps(response, indent=2, sort_keys=True) + "\n")
                (out_dir / "metadata.json").write_text(
                    json.dumps(metadata, indent=2, sort_keys=True) + "\n")
            else:
                out_dir = self.paths.campaign_dir / "submissions" / job_id
                out_dir.mkdir(parents=True, exist_ok=True)
                static = self._static_check(role, response)
                (out_dir / "note.md").write_text(response["note_markdown"].rstrip() + "\n")
                (out_dir / "response.json").write_text(
                    json.dumps(response, indent=2, sort_keys=True) + "\n")
                (out_dir / "manifest.json").write_text(json.dumps({
                    "schema": schema,
                    "job_id": job_id,
                    "model": self.provider.model,
                    "reasoning_effort": self.provider.reasoning_effort,
                    "response_sha256": hashlib.sha256(
                        json.dumps(response, sort_keys=True).encode()).hexdigest(),
                    "static_check": static,
                    "agent": metadata,
                }, indent=2, sort_keys=True) + "\n")
                if not static["passed"]:
                    raise AgentError(
                        "static submission check failed: " + "; ".join(static["errors"]))
            return job_id, True, None
        except Exception as exc:
            return job_id, False, f"{type(exc).__name__}: {exc}"

    def _finish(self, job_id: str, succeeded: bool, error: str | None) -> None:
        with self.lock, self.connect() as connection:
            row = connection.execute(
                "SELECT attempts,max_attempts,role,dependency FROM campaign_jobs WHERE id=?",
                (job_id,)).fetchone()
            status = "succeeded" if succeeded else (
                "failed" if row["attempts"] >= row["max_attempts"] else "queued")
            if row["role"] == "verifier":
                output_dir = self.paths.campaign_dir / "reviews" / str(row["dependency"]) / job_id
            else:
                output_dir = self.paths.campaign_dir / "submissions" / job_id
            connection.execute(
                "UPDATE campaign_jobs SET status=?,output_dir=?,error=?,finished_at=? WHERE id=?",
                (status, str(output_dir), error, utc_timestamp(), job_id))
        if succeeded and not job_id.startswith("verifier-"):
            self._enqueue_verifier(job_id)

    def export_status(self) -> dict[str, Any]:
        with self.connect() as connection:
            counts = {row["status"]: row["count"] for row in connection.execute(
                "SELECT status,COUNT(*) AS count FROM campaign_jobs GROUP BY status")}
            roles = {row["role"]: row["count"] for row in connection.execute(
                "SELECT role,COUNT(*) AS count FROM campaign_jobs GROUP BY role")}
            rows = [dict(row) for row in connection.execute(
                "SELECT * FROM campaign_jobs ORDER BY id")]
        payload = {
            "campaign_dir": str(self.paths.campaign_dir),
            "model": self.provider.model,
            "reasoning_effort": self.provider.reasoning_effort,
            "dimension": int(self.cfg.get("dimension", 2)),
            "field_regime": str(self.cfg.get("field_regime", "prime")),
            "fixed_prime": int(self.cfg.get("fixed_prime", 147457)),
            "fixed_degree": int(self.cfg.get("fixed_degree", 87)),
            "verifier_count": 2,
            "recovery_divisor": int(self.cfg.get("recovery_divisor", 10)),
            "initial_soundness": float(self.cfg.get("initial_soundness", 1.0)),
            "researcher_count": int(self.cfg["researcher_count"]),
            "literature_agent_count": (
                1 if self.cfg.get("literature_agent_enabled", True) else 0),
            "planned_agent_invocations": (
                (int(self.cfg["researcher_count"]) +
                 (1 if self.cfg.get("literature_agent_enabled", True) else 0)) *
                ((3 if self.cfg.get("verifier_enabled", True) else 1) +
                 (1 if self.cfg.get("lemma_writer_enabled", True) else 0)) +
                ((3 if self.cfg.get("genius_enabled", True) else 0) +
                 (1 if self.cfg.get("genius_enabled", True) and
                  self.cfg.get("lemma_writer_enabled", True) else 0))),
            "counts": counts,
            "roles": roles,
            "updated_at": utc_timestamp(),
        }
        (self.paths.campaign_dir / "status.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n")
        (self.paths.campaign_dir / "jobs.json").write_text(
            json.dumps(rows, indent=2, sort_keys=True) + "\n")
        self._export_leaderboards(rows)
        self._export_dashboard_snapshot(payload, rows)
        return payload

    def _export_leaderboards(self, rows: list[dict[str, Any]]) -> None:
        board_dir = self.paths.campaign_dir / "leaderboards"
        board_dir.mkdir(parents=True, exist_ok=True)
        promising: list[dict[str, Any]] = []
        verified: list[dict[str, Any]] = []
        rejected: list[dict[str, Any]] = []
        bottlenecks: list[dict[str, Any]] = []
        for row in rows:
            if row["role"] not in {"researcher", "genius"} or row["status"] != "succeeded":
                continue
            response_path = self.paths.campaign_dir / "submissions" / row["id"] / "response.json"
            if not response_path.exists():
                continue
            response = json.loads(response_path.read_text())
            audits = []
            for seat in ("a", "b"):
                verifier_id = f"verifier-{seat}-{row['id']}"
                audit_path = (self.paths.campaign_dir / "reviews" / row["id"] /
                              verifier_id / "audit.json")
                if audit_path.exists():
                    audits.append({"verifier_id": verifier_id, **json.loads(audit_path.read_text())})
            claim = response.get("theorem_statement") or response.get("integrated_theorem", "")
            claim_hash = hashlib.sha256(claim.encode()).hexdigest()
            claimed = response.get("claimed_soundness")
            double_verified = (
                len(audits) == 2 and claimed is not None and
                response.get("result_status") == "proved" and
                all(audit.get("verdict") == "accept" for audit in audits) and
                all(audit.get("verified_claim_sha256") == claim_hash for audit in audits) and
                all(audit.get("verified_soundness") == claimed for audit in audits))
            if double_verified:
                review_verdict = "double-accept"
            elif any(audit.get("verdict") == "reject" for audit in audits):
                review_verdict = "rejected"
            elif audits:
                review_verdict = f"awaiting ({sum(a.get('verdict') == 'accept' for a in audits)}/2 accepts)"
            else:
                review_verdict = "awaiting (0/2 accepts)"
            entry = {
                "job_id": row["id"],
                "role": row["role"],
                "title": response.get("title", "GENIUS synthesis"),
                "result_status": response.get("result_status", "conditional"),
                "dimension": response.get("dimension", 2),
                "field_regime": response.get("field_regime", "prime"),
                "claim_scope": response.get("claim_scope", "bivariate_theorem"),
                "fixed_prime": response.get("fixed_prime", 147457),
                "fixed_degree": response.get("fixed_degree", 87),
                "claimed_soundness": claimed,
                "benchmark_improved": response.get("benchmark_improved", False),
                "theorem_statement": claim,
                "theorem_sha256": claim_hash,
                "note_path": str(response_path.parent / "note.md"),
                "review_verdict": review_verdict,
                "double_verified": double_verified,
                "audits": audits,
            }
            if double_verified:
                verified.append(entry)
            elif review_verdict == "rejected":
                rejected.append(entry)
            else:
                promising.append(entry)
            for stage in response.get("soundness_ledger", []):
                bottlenecks.append({"job_id": row["id"], **stage})
        verified.sort(key=lambda item: (float(item["claimed_soundness"]), item["job_id"]))
        completed = sorted(
            (entry for entry in verified),
            key=lambda item: next((row.get("finished_at") or "" for row in rows
                                   if row["id"] == item["job_id"]), ""))
        history: list[dict[str, Any]] = []
        best = float(self.cfg.get("initial_soundness", 1.0))
        for entry in completed:
            epsilon = float(entry["claimed_soundness"])
            if epsilon >= best:
                continue
            previous = best
            best = epsilon
            finished_at = next((row.get("finished_at") for row in rows
                                if row["id"] == entry["job_id"]), None)
            history.append({
                "job_id": entry["job_id"],
                "title": entry["title"],
                "soundness": epsilon,
                "previous_best": previous,
                "gain": previous - epsilon,
                "verified_at": finished_at,
                "verifier_ids": [audit["verifier_id"] for audit in entry["audits"]],
                "theorem_sha256": entry["theorem_sha256"],
            })
        for name, data in (
            ("promising-results", promising),
            ("verified-results", verified),
            ("rejected-results", rejected),
            ("bottleneck-ledger", bottlenecks),
        ):
            (board_dir / f"{name}.json").write_text(
                json.dumps(data, indent=2, sort_keys=True) + "\n")
        (board_dir / "soundness-history.json").write_text(
            json.dumps({
                "fixed_prime": 147457,
                "fixed_degree": 87,
                "lower_is_better": True,
                "verification_threshold": 2,
                "points": history,
            }, indent=2, sort_keys=True) + "\n")

    def _export_dashboard_snapshot(
            self, status: dict[str, Any], rows: list[dict[str, Any]]) -> None:
        dashboard_public = self.paths.workspace / "dashboard" / "public"
        if not dashboard_public.is_dir():
            return

        board_dir = self.paths.campaign_dir / "leaderboards"

        def load_board(name: str) -> list[dict[str, Any]]:
            path = board_dir / f"{name}.json"
            return json.loads(path.read_text()) if path.exists() else []

        def enrich(entry: dict[str, Any]) -> dict[str, Any]:
            job_id = str(entry["job_id"])
            submission_dir = self.paths.campaign_dir / "submissions" / job_id
            response_path = submission_dir / "response.json"
            note_path = submission_dir / "note.md"
            response = json.loads(response_path.read_text()) if response_path.exists() else {}
            return {
                **entry,
                "parameter_regime": response.get("parameter_regime", ""),
                "sampling_model": response.get("sampling_model", ""),
                "global_conclusion": response.get("global_conclusion", ""),
                "proof_steps": response.get("proof_steps", []),
                "soundness_ledger": response.get("soundness_ledger", []),
                "limitations": response.get("limitations", response.get("obstructions", [])),
                "note_markdown": note_path.read_text() if note_path.exists() else "",
            }

        candidate_groups = {
            "verified": [enrich(entry) for entry in load_board("verified-results")],
            "promising": [enrich(entry) for entry in load_board("promising-results")],
            "rejected": [enrich(entry) for entry in load_board("rejected-results")],
        }
        dashboard_jobs = [{
            "id": row["id"],
            "role": row["role"],
            "ordinal": row["ordinal"],
            "direction": row["direction"],
            "status": row["status"],
            "attempts": row["attempts"],
            "max_attempts": row["max_attempts"],
            "started_at": row["started_at"],
            "finished_at": row["finished_at"],
            "error": row["error"],
        } for row in rows]
        snapshot = {
            "schema": "line-point-concrete-dashboard-v1",
            "campaign": self.paths.campaign_dir.name,
            "status": status,
            "candidates": candidate_groups,
            "bottlenecks": load_board("bottleneck-ledger"),
            "soundness_history": json.loads(
                (board_dir / "soundness-history.json").read_text()),
            "jobs": dashboard_jobs,
        }
        update_dashboard_sections(self.paths.workspace, snapshot, replace_base=True)

    def run(self) -> dict[str, Any]:
        self.initialize()
        stop_file = self.paths.campaign_dir / "STOP"
        while not stop_file.exists():
            ready = self._ready(self.max_workers)
            if not ready:
                status = self.export_status()
                if status["counts"].get("queued", 0) == 0 and status["counts"].get("running", 0) == 0:
                    (self.paths.campaign_dir / "COMPLETED").write_text(utc_timestamp() + "\n")
                    return status
                time.sleep(min(self.retry_seconds, 30))
                continue
            claimed = [row for row in ready if self._claim(row["id"])]
            batch_failed = False
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [executor.submit(self._run_job, row) for row in claimed]
                for future in as_completed(futures):
                    job_id, succeeded, error = future.result()
                    batch_failed = batch_failed or not succeeded
                    self._finish(job_id, succeeded, error)
                    self.export_status()
            if batch_failed:
                time.sleep(self.retry_seconds)
        return self.export_status()


def launch_campaign(config_path: Path | str) -> dict[str, Any]:
    _, paths = load_campaign_config(config_path)
    paths.campaign_dir.mkdir(parents=True, exist_ok=True)
    pid_path = paths.campaign_dir / "runner.json"
    if pid_path.exists():
        old = json.loads(pid_path.read_text())
        try:
            os.kill(int(old["pid"]), 0)
            return {"status": "already_running", **old}
        except (OSError, KeyError, ValueError):
            pass
    log_path = paths.campaign_dir / "campaign.log"
    log_handle = log_path.open("a")
    environment = os.environ.copy()
    source_path = str(paths.workspace / "src")
    environment["PYTHONPATH"] = (
        source_path + os.pathsep + environment["PYTHONPATH"]
        if environment.get("PYTHONPATH") else source_path)
    environment["PYTHONPYCACHEPREFIX"] = str(paths.campaign_dir / "python-cache")
    process = subprocess.Popen(
        [sys.executable, "-m", "line_point_research", "campaign-run",
         str(Path(config_path).resolve())],
        cwd=paths.workspace,
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


def campaign_status(config_path: Path | str) -> dict[str, Any]:
    campaign = ResearchCampaign(config_path)
    if not campaign.db_path.exists():
        campaign.initialize()
    return campaign.export_status()
