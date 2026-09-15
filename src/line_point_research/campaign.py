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
from fractions import Fraction
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
    "required": ["title", "dimension", "field_regime", "result_status", "claim_scope",
                 "leaderboard_submission", "benchmark_improved",
                 "fixed_prime", "fixed_degree", "claimed_soundness", "theorem_statement", "parameter_regime",
                 "guaranteed_recovery_fraction", "guaranteed_recovery_agreement_count",
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
        "leaderboard_submission": {"type": "boolean"},
        "benchmark_improved": {"type": "boolean"},
        "claimed_soundness": {"type": ["number", "null"], "exclusiveMinimum": 0, "maximum": 1},
        "guaranteed_recovery_fraction": {"type": ["number", "null"], "exclusiveMinimum": 0, "maximum": 1},
        "guaranteed_recovery_agreement_count": {"type": ["integer", "null"], "minimum": 0},
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
    "required": ["title", "dimension", "field_regime", "fixed_prime", "fixed_degree", "result_status",
                 "leaderboard_submission", "benchmark_improved", "snapshot", "evidence_ledger", "bottleneck_map",
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
        "leaderboard_submission": {"type": "boolean"},
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
                 "coverage_complete", "proof_chain_complete", "proof_chain_audit",
                 "quantifier_audit", "soundness_audit",
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
        "proof_chain_complete": {"type": "boolean"},
        "proof_chain_audit": {"type": "array", "items": AUDIT_ITEM},
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
    "new architecture 5: combine compatible verified lemmas from the shared corpus into a new end-to-end soundness proof, but judge success solely by the concrete verified leaderboard epsilon",
    "use direction structure in the fixed affine plane",
    "derive a finite-field energy increment with explicit constants",
    "specialize bivariate Reed--Muller list recovery to d=87",
    "convert a polynomial list into one polynomial with explicit agreement",
    "search for adversarial line and point tables that limit the theorem",
    "derive a direct affine-plane proof avoiding lossy generic lemmas",
    "exploit pencils of accepted lines through popular points",
    "prove direction-by-direction consistency with exact counts",
    "construct a machine-checkable integer or rational certificate",
        "optimize the final max(2d/p, epsilon/10) recovery step",
]

COHORT_PREFIXES = (
    "COHORT A (10 agents): sharpen the latest verified construction and its exact finite ledger.",
    "COHORT B (10 agents): pursue black-box/list-decoding and constant-removal improvements over the latest record.",
    "COHORT C (10 agents): search genuinely new bivariate structures, while targeting a strict leaderboard improvement.",
)

# One coordinated 30-seat proof team. Each tuple is
# (phase, mission, upstream researcher ordinals). Later seats are released only
# after their named upstreams finish, and every seat reads the complete shared
# corpus before working.
COORDINATED_TEAM = (
    ("foundation", "Maintain the exact current-record ledger and identify the three numerically dominant losses.", ()),
    ("foundation", "Normalize the complete bivariate KTZ chain into modular fixed-parameter inequalities.", ()),
    ("foundation", "Develop sharp affine-plane incidence, direction, and pencil estimates for the fixed instance.", ()),
    ("foundation", "Develop fixed-field algebraic reconstruction, interpolation, and separability tools.", ()),
    ("foundation", "Extract the strongest applicable bivariate list-decoding and list-to-one recovery statements.", ()),
    ("foundation", "Build adversarial tables and counterexamples that constrain every proposed architecture.", ()),
    ("module", "Optimize KTZ pruning and popularity thresholds using the exact ledger.", (1, 2)),
    ("module", "Optimize weighted interpolation multiplicities and monomial regions.", (2, 4)),
    ("module", "Tighten resultant, discriminant, derivative, and exceptional-line accounting.", (2, 4)),
    ("module", "Turn affine pencils and direction structure into a quantitative reconstruction module.", (3, 6)),
    ("module", "Build an explicit energy or dependent-random-choice replacement for popularity pruning.", (3, 6)),
    ("module", "Build an explicit list-to-one polynomial recovery module with max(2d/p, epsilon/10) output.", (5, 6)),
    ("integration", "Assemble the best KTZ modules into one complete candidate and expose its remaining loss.", (7, 8, 9)),
    ("integration", "Assemble the pencil, energy, and algebraic modules into a geometric candidate.", (4, 10, 11)),
    ("integration", "Assemble the energy and decoding modules into a decoding-based candidate.", (5, 11, 12)),
    ("certification", "Create exact integer certificates for the pruning and interpolation parameter region.", (7, 8)),
    ("certification", "Create exact certificates for algebraic cleanup and exceptional-set bounds.", (8, 9)),
    ("red-team", "Compare and attack all three integrated candidates; isolate only repairable fatal gaps.", (13, 14, 15)),
    ("repair", "Repair and sharpen the integrated KTZ candidate using the red-team report and certificates.", (13, 16, 18)),
    ("repair", "Repair and sharpen the geometric candidate using the red-team report and certificates.", (14, 17, 18)),
    ("repair", "Repair and sharpen the decoding candidate using the red-team report and certificates.", (15, 16, 18)),
    ("hybrid", "Combine the strongest compatible KTZ and pencil modules into a new candidate.", (13, 14, 18)),
    ("hybrid", "Combine the strongest compatible energy and decoding modules into a new candidate.", (14, 15, 18)),
    ("optimization", "Jointly optimize every surviving integer parameter across the certified modules.", (16, 17, 18)),
    ("candidate", "Close the best repaired KTZ or KTZ-pencil proof into a leaderboard submission.", (19, 22, 24)),
    ("candidate", "Close the best repaired geometric or energy-decoding proof into a leaderboard submission.", (20, 23, 24)),
    ("candidate", "Close the best repaired decoding proof into a leaderboard submission.", (21, 23, 24)),
    ("final-red-team", "Audit the three candidate proofs against adversarial tables and identify the strongest survivor.", (25, 26, 27)),
    ("consolidation", "Consolidate the strongest survivor into a minimal complete proof with an exact loss ledger.", (25, 26, 27, 28)),
    ("submission", "Produce the team's strongest fully proved leaderboard submission, or precisely record the final obstruction.", (28, 29)),
)

# A token-efficient ten-seat funnel. The first six seats produce short evidence
# cards in parallel; only two builders, one critic, and one integrator receive
# the resulting context. This preserves complementary work without paying ten
# agents to independently rewrite an end-to-end proof.
FRUGAL_TEAM = (
    ("scout", "Sharpen the exact component-survival inequality near the incumbent parameters and identify the smallest rigorously feasible trigger score below 7349491214.", ()),
    ("scout", "Audit the derivative, resultant, separability, and exceptional-line charges for factor-aware savings that propagate to at least one lower trigger point.", ()),
    ("scout", "Develop a label-sensitive direction or pencil selector that improves the current incidence retention constant, with exact finite counts.", ()),
    ("scout", "Search the exact integer parameter neighborhood around the incumbent interpolation and pruning choices; return a reproducible rational certificate for every feasible improvement.", ()),
    ("scout", "Adversarially test the incumbent proof and proposed one-point improvements; isolate false shortcuts and the weakest repairable inequality.", ()),
    ("scout", "Seek an alternative component-mass, spectral-incidence, or energy inequality that plugs into the incumbent proof and lowers its concrete score.", ()),
    ("builder", "Combine the component, parameter-search, and alternative-incidence outputs into one concise end-to-end candidate or one exact minimal obstruction.", (1, 4, 6)),
    ("builder", "Combine the algebraic-cleanup, direction-selector, and adversarial outputs into one concise end-to-end candidate or one exact minimal obstruction.", (2, 3, 5)),
    ("red-team", "Audit both builder routes line by line, reject invalid imports, and specify the smallest repairs or strongest surviving strict improvement.", (7, 8)),
    ("integrator", "Use both builder notes and the red-team report to publish the strongest fully proved strict leaderboard improvement; otherwise publish the exact frontier and next decisive calculation.", (7, 8, 9)),
)


LITERATURE_DIRECTION = """Establish the campaign's rigorous state-of-the-art baseline from
primary literature. Locate the strongest published or publicly posted theorem actually
applicable to the uniform affine line-versus-point test on F_147457^2 with total degree 87,
including Kominers--Thaler--Zheng and any later refinement. Record exact paper versions,
theorem or lemma numbers, hypotheses, constants, and the exact conversion from the source's
agreement conclusion to this campaign's max(2d/p, epsilon/10) convention. Compare all applicable
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


GENIUS_DIRECTION = """Global synthesis of the strongest fixed-instance soundness theorem.
Treat the pure scale epsilon=(d/q)^(1/3), with unit leading constant, as a serious conjectural
target: at p=147457 and d=87 this is approximately 0.0838721841647049. Work backward from the
campaign conclusion Agr_87(f)>=max(2d/p,epsilon/10) and try to remove every constant-factor loss that
inflates the current effective constant from about 8.5 to 1. Do not assume the target is true.
Either produce a complete proof, identify a compatible new lemma that makes a discontinuous
advance toward it, or isolate an explicit mathematical obstruction showing which step cannot
reach the pure cubic-root scale. Prioritize structural replacements for popularity pruning,
two-sided peeling, weighted interpolation cleanup, and component-mass conversion over marginal
retuning of the existing ledger.

In particular, search for a black-box constant-removal or self-improvement lemma. Starting only
from a theorem at threshold C*(d/q)^(1/3), test whether popularity bucketing, local list recovery,
and Reed--Muller list decoding can recover a bounded global list already at
epsilon=(d/q)^(1/3), after which incidence agreement or pairwise polynomial intersection bounds
collapse the list to one polynomial agreeing on at least max(2d/p,epsilon/10) of the plane. Track the mass
lost in every bucket and the list size exactly. Also test conditioning on dense incidence cores,
random restrictions, and iterative decoding as possible ways to amplify conditional acceptance
by C without changing p, d, dimension, sampling, or the final quantifiers. State explicitly why
ordinary repetition or rescaling does not suffice if that is the obstruction."""


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
    if effort not in {"xhigh", "max", "ultra"}:
        raise ValueError("campaign.reasoning_effort must be xhigh, max, or ultra")
    researcher_efforts = campaign.get("researcher_reasoning_efforts", [effort])
    if not isinstance(researcher_efforts, list) or not researcher_efforts or any(
            str(item) not in {"xhigh", "max", "ultra"} for item in researcher_efforts):
        raise ValueError("campaign.researcher_reasoning_efforts must contain xhigh, max, or ultra")
    architecture = str(campaign.get("team_architecture", "independent"))
    if architecture == "frugal-funnel-v1" and count != len(FRUGAL_TEAM):
        raise ValueError("frugal-funnel-v1 requires exactly 10 researchers")
    if int(campaign.get("dimension", 2)) != 2:
        raise ValueError("campaign.dimension must be exactly 2")
    if str(campaign.get("field_regime", "prime")) != "prime":
        raise ValueError("campaign.field_regime must be prime")
    if int(campaign.get("fixed_prime", 0)) != 147457:
        raise ValueError("campaign.fixed_prime must be 147457")
    if int(campaign.get("fixed_degree", 0)) != 87:
        raise ValueError("campaign.fixed_degree must be 87")
    if int(campaign.get("verifier_count", 0)) != 1:
        raise ValueError("campaign.verifier_count must be exactly 1")
    verifier_effort = str(campaign.get("verifier_reasoning_effort", "xhigh"))
    if verifier_effort not in {"xhigh", "max", "ultra"}:
        raise ValueError("campaign.verifier_reasoning_effort must be xhigh, max, or ultra")
    if int(campaign.get("recovery_divisor", 0)) != 10:
        raise ValueError("campaign.recovery_divisor must be 10")
    if str(campaign.get("minimum_soundness_numerator", "")) != "957" or \
            str(campaign.get("minimum_soundness_denominator", "")) != "1474570":
        raise ValueError("campaign minimum soundness must be 957/1474570 = 1.1d/p")
    if int(campaign.get("minimum_recovery_agreement_count", 0)) != 25657518:
        raise ValueError("campaign minimum recovery count must be 2dp = 25657518")
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
            checkpoint_root=(
                self.paths.campaign_dir / "live_notes"
                if bool(self.cfg.get("live_checkpoints_enabled", True)) else None),
        )
        self.max_workers = int(self.cfg.get("max_workers", 4))
        self.retry_seconds = int(self.cfg.get("retry_seconds", 120))

    def _researcher_effort(self, ordinal: int) -> str:
        efforts = [str(item) for item in self.cfg.get("researcher_reasoning_efforts", [self.cfg.get("reasoning_effort", "ultra")])]
        return efforts[(ordinal - 1) % len(efforts)]

    def _provider_for(self, row: dict[str, Any]) -> CommandAgentProvider:
        effort = str(row.get("reasoning_effort") or self.provider.reasoning_effort or "ultra")
        if effort == self.provider.reasoning_effort:
            return self.provider
        return CommandAgentProvider(
            self.paths.workspace, self.paths.campaign_dir / "agent_logs",
            executable=self.provider.executable, model=self.provider.model,
            reasoning_effort=effort, disable_nested_agents=self.provider.disable_nested_agents,
            timeout_seconds=self.provider.timeout_seconds,
            checkpoint_root=self.provider.checkpoint_root)

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
                if (str(self.cfg.get("team_architecture", "")) == "frugal-funnel-v1" and
                        ordinal <= len(FRUGAL_TEAM)):
                    phase, mission, upstream_ordinals = FRUGAL_TEAM[ordinal - 1]
                    direction = f"FRUGAL FUNNEL / {phase.upper()}: {mission}"
                    dependency = (json.dumps([
                        f"researcher-{item:04d}" for item in upstream_ordinals])
                        if upstream_ordinals else None)
                elif int(self.cfg["researcher_count"]) == 30 and ordinal <= len(COORDINATED_TEAM):
                    phase, mission, upstream_ordinals = COORDINATED_TEAM[ordinal - 1]
                    direction = f"ONE TEAM / {phase.upper()}: {mission}"
                    dependency = (json.dumps([
                        f"researcher-{item:04d}" for item in upstream_ordinals])
                        if upstream_ordinals else None)
                else:
                    direction = DIRECTIONS[(ordinal - 1) % len(DIRECTIONS)]
                    dependency = None
                connection.execute(
                    """INSERT OR IGNORE INTO campaign_jobs
                    (id,role,ordinal,direction,dependency,status,max_attempts,model,reasoning_effort,created_at)
                    VALUES (?,?,?,?,?,'queued',?,?,?,?)""",
                    (job_id, "researcher", ordinal, direction, dependency,
                     int(self.cfg.get("max_attempts", 8)), self.provider.model,
                     self._researcher_effort(ordinal), utc_timestamp()),
                )
                connection.execute(
                    "UPDATE campaign_jobs SET direction=?,dependency=? WHERE id=? AND role='researcher' "
                    "AND status='queued'",
                    (direction, dependency, job_id),
                )
                connection.execute(
                    "UPDATE campaign_jobs SET reasoning_effort=? WHERE id=? AND role='researcher' "
                    "AND status='queued'",
                    (self._researcher_effort(ordinal), job_id),
                )
            self._insert_literature_agent(connection)
            if bool(self.cfg.get("genius_enabled", True)):
                connection.execute(
                    """INSERT OR IGNORE INTO campaign_jobs
                    (id,role,ordinal,direction,dependency,status,max_attempts,model,reasoning_effort,created_at)
                    VALUES ('GENIUS','genius',NULL,?,'__swarm_reviews__','queued',?,?,?,?)""",
                    (GENIUS_DIRECTION,
                     int(self.cfg.get("max_attempts", 8)), self.provider.model,
                     self.provider.reasoning_effort, utc_timestamp()),
                )
                connection.execute(
                    "UPDATE campaign_jobs SET direction=? WHERE id='GENIUS' AND role='genius' "
                    "AND status='queued' AND attempts=0",
                    (GENIUS_DIRECTION,),
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
            if row["role"] == "genius" and not bool(self.cfg.get("genius_enabled", False)):
                continue
            dependency = row["dependency"]
            if dependency is None:
                ready.append(row)
            elif dependency.startswith("["):
                try:
                    upstreams = json.loads(dependency)
                except json.JSONDecodeError:
                    upstreams = []
                if (isinstance(upstreams, list) and upstreams and
                        all(states.get(str(item)) in {"succeeded", "failed"}
                            for item in upstreams)):
                    ready.append(row)
            elif dependency == "__swarm_reviews__":
                researcher_terminal = all(
                    states.get(f"researcher-{index:04d}") in {"succeeded", "failed"}
                    for index in range(1, int(self.cfg["researcher_count"]) + 1))
                successful = [
                    item["id"] for item in all_jobs
                    if item["role"] == "researcher" and item["status"] == "succeeded" and
                    self._is_leaderboard_submission_id(item["id"])
                ]
                verifier_terminal = all(
                    states.get(f"verifier-a-{source_id}") in {"succeeded", "failed"}
                    for source_id in successful)
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
            verifier_id = f"verifier-a-{source_id}"
            connection.execute(
                """INSERT OR IGNORE INTO campaign_jobs
                (id,role,ordinal,direction,dependency,status,max_attempts,model,reasoning_effort,created_at)
                VALUES (?, 'verifier', NULL, ?, ?, 'queued', ?, ?, ?, ?)""",
                (verifier_id, "independent verifier audit of " + source_id, source_id,
                 int(self.cfg.get("max_attempts", 8)), self.provider.model,
                 str(self.cfg.get("verifier_reasoning_effort", "xhigh")), utc_timestamp()),
            )

    def _submission_response(self, source_id: str) -> dict[str, Any] | None:
        path = self.paths.campaign_dir / "submissions" / source_id / "response.json"
        if not path.exists():
            return None
        try:
            value = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            return None
        return value if isinstance(value, dict) else None

    @staticmethod
    def _is_leaderboard_submission(response: dict[str, Any] | None) -> bool:
        if not response:
            return False
        explicit = response.get("leaderboard_submission")
        if explicit is not None:
            return bool(explicit)
        # Backward compatibility for submissions produced before the explicit flag existed.
        return bool(
            response.get("claim_scope") == "bivariate_theorem" and
            response.get("result_status") == "proved" and
            response.get("benchmark_improved") and
            isinstance(response.get("claimed_soundness"), (int, float)) and
            not isinstance(response.get("claimed_soundness"), bool)
        )

    def _is_leaderboard_submission_id(self, source_id: str) -> bool:
        return self._is_leaderboard_submission(self._submission_response(source_id))

    def reconcile_verifier_queue(self) -> dict[str, Any]:
        """Audit only end-to-end submissions explicitly offered to the leaderboard."""
        enqueue: list[str] = []
        with self.connect() as connection:
            connection.executescript(SCHEMA)
            sources = [dict(row) for row in connection.execute(
                "SELECT id,status FROM campaign_jobs WHERE role IN ('researcher','genius')")]
            for source in sources:
                source_id = str(source["id"])
                is_submission = self._is_leaderboard_submission_id(source_id)
                if is_submission and source["status"] == "succeeded":
                    enqueue.append(source_id)
                elif not is_submission:
                    connection.execute(
                        "UPDATE campaign_jobs SET status='skipped',error=? "
                        "WHERE role='verifier' AND dependency=? AND status='queued'",
                        ("source is not a leaderboard submission", source_id),
                    )
        for source_id in enqueue:
            self._enqueue_verifier(source_id)
        return self.export_status()

    def _corpus_instruction(self) -> str:
        return f"""The repository is {self.paths.workspace}. The durable corpus root is
{self.paths.corpus_root}. Begin by reading TARGET.md, references/LITERATURE.md,
references/bibliography.json, research_state/DATA_MANIFEST.json, all prior submissions,
leaderboards, and verifier audits. Treat the corpus as read-only except for any explicitly
assigned live-checkpoint outbox. Treat literature summaries as
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
            record_count = int((Fraction(str(best)) * (147457 ** 2) + 1 - 1).__ceil__())
            record = f"The current verified leaderboard record is {record_count} agreement points (epsilon={best:.17g})."
        else:
            initial = float(self.cfg.get("initial_soundness", 1.0))
            incumbent_count = self.cfg.get("incumbent_agreement_count")
            if incumbent_count is not None:
                record = (
                    f"The imported verified incumbent is {int(incumbent_count)} agreement points "
                    f"(epsilon approximately {initial:.17g}).")
            else:
                record = (
                    "There is no verified leaderboard point yet; "
                    f"the comparison threshold is epsilon={initial:.17g}.")
        return f"""LEADERBOARD OBJECTIVE: {record} Read the authoritative history at
{history_path}. Every constructive choice must be evaluated by whether it can produce a smaller
fully proved absolute agreement-count score ceil(epsilon*p^2) for the fixed instance. Do not optimize elegance, generality,
roadmap completeness, or exposition at the expense of that objective. Conditional work is
useful only when it isolates the shortest concrete route to a smaller certifiable epsilon."""

    def _research_prompt(self, row: dict[str, Any]) -> str:
        if row["id"] == "literature-sota-0001":
            return self._literature_prompt(row)
        modes = ["proof-first", "bottleneck-first", "adversarial", "synthesis-first"]
        mode = modes[(int(row["ordinal"]) - 1) % len(modes)]
        upstreams: list[str] = []
        dependency = row.get("dependency")
        if isinstance(dependency, str) and dependency.startswith("["):
            try:
                upstreams = [str(item) for item in json.loads(dependency)]
            except json.JSONDecodeError:
                upstreams = []
        coordination = (
            "You are a foundation seat. Produce reusable exact statements, explicit parameters, "
            "and a concise Team Handoff section naming the downstream modules that should use them."
            if not upstreams else
            f"Your named upstream seats are {', '.join(upstreams)}. Read their complete submissions, "
            "proof steps, ledgers, and audits before beginning. Reuse their strongest valid pieces, "
            "repair rather than duplicate their gaps, and end with a Team Handoff section giving exact "
            "lemma IDs, parameter values, obstructions, and recommended downstream actions."
        )
        frugal = str(self.cfg.get("team_architecture", "")) == "frugal-funnel-v1"
        team_description = (
            "a token-efficient ten-seat scout-to-proof funnel"
            if frugal else
            f"one coordinated {self.cfg['researcher_count']}-agent proof team"
        )
        budget_instruction = ""
        if frugal:
            ordinal = int(row["ordinal"])
            if ordinal <= 6:
                budget_instruction = """TOKEN BUDGET DISCIPLINE: You are a scout. Do not rewrite the incumbent proof.
Investigate at most two concrete approaches and return a compact evidence card (target at most
2,500 words) containing exact statements, calculations or counterexamples, source paths, and a
precise handoff. Write a full theorem proof only if you have already found a strict score
improvement."""
            elif ordinal <= 8:
                budget_instruction = """TOKEN BUDGET DISCIPLINE: You are a proof builder. Start from the named
upstream evidence cards. Do not repeat their derivations. Write a full end-to-end proof only when
the combined inequalities plausibly beat 7349491214; otherwise give the shortest exact obstruction."""
            elif ordinal == 9:
                budget_instruction = """TOKEN BUDGET DISCIPLINE: You are the red-team critic. Audit only the
load-bearing steps of the two builder routes. Prefer a compact accept/reject/repair table over a
new exposition of the whole literature."""
            else:
                budget_instruction = """TOKEN BUDGET DISCIPLINE: You are the final integrator. Spend your
context on the strongest surviving route and its load-bearing chain. Publish one complete proof
only for a strict improvement; otherwise record the exact frontier without speculative padding."""
        return f"""You are {row['id']}, one of {self.cfg['researcher_count']} coordinated
mathematical research seats improving soundness of the affine line-versus-point low-degree
test. Your assigned direction is: {row['direction']}. Your mode is {mode}. Your primary objective
is to lower the concrete agreement-count score ceil(epsilon*p^2); proof roadmaps are shared reference material, not
your principal deliverable.

You belong to {team_description}, not an independent cohort. {coordination}
All successful upstream work is shared through the repository. Consult the message board for
cross-branch warnings and useful imports; do not redo a calculation already certified upstream.

{budget_instruction}

{self._corpus_instruction()}

The instance is immutable: m=2, p=147457, and total degree d=87. The verifier samples a uniformly
random affine line in F_p^2 and then a uniformly random point on it. A number epsilon is an
admissible verified soundness bound only if epsilon >= 957/1474570 = 1.1d/p and every line
table and point table accepted with probability at least epsilon admits a total-degree-at-most-87
bivariate polynomial agreeing with the point table on at least max(174/147457, epsilon/10) of
all p^2 points (thus at least 25,657,518 points). Lower absolute agreement-count scores are stronger. Do genuine
mathematical work: isolate one bottleneck, optimize exact constants, attempt a new lemma or
counterexample, and write a fully quantified fixed-instance result.

Do not work on m>2, dimension bootstrapping, extension fields, or descent: the standard
general-dimensional lift is a routine downstream corollary and earns no campaign credit. Do not
silently change uniform affine-line sampling, replace total degree by individual degree, vary the
fixed parameters, or return only a large list of candidate global polynomials.

Every numerical loss must appear in the soundness ledger. State p=147457, d=87, acceptance
epsilon, all auxiliary parameters, and the final max(2d/p,epsilon/10) agreement, both as a
fraction and an absolute count. Use exact rational or
integer arithmetic whenever possible. Audit division
by derivatives, discriminants, irreducibility, interpolation multiplicities, and every
union/Markov/Cauchy--Schwarz loss. Test adversarial tables, inseparability, and concentrated good
directions. A rigorous obstruction or correction is valuable. Set benchmark_improved=true only
when the proved claimed_soundness produces a strictly smaller agreement-count score than the
current verified record. Set dimension=2, field_regime=prime, fixed_prime=147457, and
fixed_degree=87 in the structured response.

The old score-one/constant-polynomial argument is below the admissible epsilon floor and is not a
leaderboard result. Treat earlier artifacts using only epsilon/10 as superseded, except for
lemmas that remain valid independently of that recovery contract. Set leaderboard_submission=true only for a fully proved, numerical, end-to-end bivariate
soundness theorem that strictly improves the record. Put its complete load-bearing logic chain
in proof_steps, including exact citations and statements for imported lemmas. One independent
xhigh verifier will verify that chain and its lemmas immediately. For a standalone lemma, obstruction,
counterexample, conditional architecture, or proof tool, set leaderboard_submission=false and
benchmark_improved=false. It remains available to the Lemma Book and later researchers but does
not consume verifier work until a leaderboard proof depends on it.

Return a standard academic Markdown note with Abstract, Test and Notation, Prior Results,
Theorem, Proof or Conditional Proof, Soundness Ledger, Counterexample Attempts,
Characteristic Audit, and Limitations. Number all proof steps [P1], [P2], ... and mark each as
proved, conditional, conjectural, or refuted. RULE: A lemma statement contains only its
quantified objects, hypotheses, and conclusion. It contains no motivation, derivation,
commentary, proof sketch, interpretation, history, or explanation; put all such material in the
proof. A Lemma Writer may post-edit and split a lemma without changing its content when that
optional publishing pass is enabled.
"""

    def _genius_prompt(self) -> str:
        return f"""You are GENIUS, the global proof-synthesis mathematician for the
line-versus-point concrete campaign. You must inspect the complete accumulated corpus and attempt
an integrated proof minimizing the absolute agreement-count score ceil(epsilon*p^2) for the fixed instance. Your sole
research objective is a new verified leaderboard record; do not optimize roadmap
coverage or generality for its own sake. The target accepts only epsilon >= 957/1474570 and
requires recovery max(174/147457,epsilon/10), never merely epsilon/10.

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
max(174/147457,epsilon/10). Set dimension=2, field_regime=prime, fixed_prime=147457, and fixed_degree=87. Do not average
incompatible lemmas or use finite evidence as proof.

Set leaderboard_submission=true, result_status=proved, and benchmark_improved=true only if every
dependency is proved and the claimed_soundness strictly improves the current verified
record. Include the complete load-bearing proof chain for its one downstream audit. Otherwise
record the honest status and set leaderboard_submission=false and benchmark_improved=false.

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
total-degree-at-most-87 polynomial on at least max(174/147457,epsilon/10) of all p^2 points;
epsilon itself must be at least 957/1474570.

For every candidate baseline, give the exact title, authors, version/date, stable URL or
bibliographic identifier, result number, verbatim mathematical hypotheses in your own notation,
and a careful specialization to p=147457,d=87. Track the source's recovery constant and all
strict versus weak inequalities. Distinguish a theorem explicitly stated by the source from a
derivation you reconstructed. Compare candidates under identical sampling and degree
conventions. Do not treat asymptotic O-notation, an unspecified universal constant, or a
non-effective existence proof as a concrete number. If constants are insufficient, set
claimed_soundness=null, leaderboard_submission=false, benchmark_improved=false, and state the
smallest missing information.
Only set result_status=proved with a numerical claimed_soundness when the complete fixed-instance
conversion is rigorous and reproducible. Set leaderboard_submission=true only for that complete
end-to-end theorem; partial literature specializations stay unaudited until a leaderboard proof
actually depends on them.

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
{source_id}. You did not author it. Your priority is the claimed end-to-end soundness theorem and
whether its numerical epsilon deserves a leaderboard point. Recompute the complete soundness
ledger and check its quantifiers, fixed-field hypotheses, sampling convention, literature
dependencies, and load-bearing proof edges. Accept only the exact claim whose SHA-256 is
{claim_hash}; never silently weaken it.

Use a risk-based audit. Read every proof step, but do not spend the bulk of the review reproving
routine algebra, elementary counting, or a standard lemma whose exact statement and applicable
hypotheses are clear. Audit deeply the lemmas on which the final epsilon actually depends,
especially parameter thresholds, exceptional-set bounds, interpolation feasibility,
characteristic assumptions, list-to-one-polynomial recovery, and the max(2d/p,epsilon/10) conversion. A
lemma-level issue blocks acceptance only when it creates a real gap in the submitted theorem or
its numerical ledger; purely editorial lemma imperfections belong to the Lemma Writer and are
not a reason to delay a sound leaderboard decision.

The submission must expose one clear dependency chain from acceptance to the final global
agreement conclusion. Set proof_chain_complete=true only if every load-bearing step appears in
proof_steps and every dependency is available. In proof_chain_audit, include one item for every
load-bearing proof step or imported lemma, using its exact step id or citation as reference. This
is where downstream lemma verification occurs. Do not audit unrelated lemmas merely because they
exist elsewhere in the corpus.

Your judgment must be independent of the submission's author. The instance is exactly m=2,
p=147457, total degree d=87, uniform affine-line then
uniform point sampling. The submitted epsilon is valid only if acceptance at least epsilon forces
agreement with one total-degree-at-most-87 bivariate polynomial on at least
max(174/147457,epsilon/10) of p^2 points, and epsilon must be at least 957/1474570. Lower epsilon is stronger.

An accept requires complete coverage; a correct exact soundness ledger; valid arithmetic at the
fixed prime; a proved conversion to the stated
single-polynomial global conclusion; no required changes; and no fatal obstruction. Use reject
with unfixable=true only for a concrete counterexample or false theorem. Use revise for repairable
gaps. Recompute the claimed epsilon, enforce epsilon >= 957/1474570, and verify its
max(174/147457,epsilon/10) conclusion and absolute recovery count. Reject or request revision if
the proof changes p, d, m, sampling, total-degree convention, or the one-polynomial conclusion.
Set every fixed-parameter verification boolean true only after checking all load-bearing claims.
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
        leaderboard_submission = bool(response.get("leaderboard_submission", False))
        if role in {"researcher", "genius"} and leaderboard_submission:
            if role == "researcher" and response.get("claim_scope") != "bivariate_theorem":
                errors.append("leaderboard_submission requires claim_scope=bivariate_theorem")
            if response.get("result_status") != "proved":
                errors.append("leaderboard_submission requires result_status=proved")
            if not response.get("benchmark_improved"):
                errors.append("leaderboard_submission requires benchmark_improved=true")
            soundness = response.get("claimed_soundness")
            if not isinstance(soundness, (int, float)) or isinstance(soundness, bool):
                errors.append("leaderboard_submission requires numeric claimed_soundness")
            elif not 0 < float(soundness) < float(self.cfg.get("initial_soundness", 1.0)):
                errors.append("claimed soundness must strictly improve the initial threshold")
            elif Fraction(str(soundness)) < Fraction(957, 1474570):
                errors.append("claimed soundness must be at least 957/1474570 = 1.1d/p")
            recovery_fraction = response.get("guaranteed_recovery_fraction")
            recovery_count = response.get("guaranteed_recovery_agreement_count")
            if not isinstance(recovery_fraction, (int, float)) or isinstance(recovery_fraction, bool):
                errors.append("leaderboard_submission requires numeric guaranteed_recovery_fraction")
            elif Fraction(str(recovery_fraction)) < max(Fraction(174, 147457), Fraction(str(soundness)) / 10):
                errors.append("guaranteed recovery fraction is below max(2d/p, epsilon/10)")
            if not isinstance(recovery_count, int) or isinstance(recovery_count, bool):
                errors.append("leaderboard_submission requires integer guaranteed_recovery_agreement_count")
            else:
                required_fraction = max(Fraction(174, 147457), Fraction(str(soundness)) / 10)
                required_count = (required_fraction * (147457 ** 2))
                required_count = (required_count.numerator + required_count.denominator - 1) // required_count.denominator
                if recovery_count < required_count:
                    errors.append("guaranteed recovery agreement count is below the required floor")
            if any(step.get("status") != "proved" for step in response.get("proof_steps", [])):
                errors.append("every leaderboard proof step must be proved")
            if any(stage.get("status") != "proved" for stage in response.get("soundness_ledger", [])):
                errors.append("every leaderboard soundness stage must be proved")
        elif role in {"researcher", "genius"} and response.get("benchmark_improved"):
            errors.append("benchmark_improved requires leaderboard_submission=true")
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
                response, metadata = self._provider_for(row).run(
                    job_id, self._research_prompt(row), RESEARCH_SCHEMA)
                schema = "line-point-concrete-submission-v1"
            elif role == "genius":
                response, metadata = self._provider_for(row).run(
                    "GENIUS", self._genius_prompt(), GENIUS_SCHEMA)
                schema = "line-point-concrete-genius-synthesis-v1"
            else:
                source_id = str(row["dependency"])
                response, metadata = self._provider_for(row).run(
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
                    response["proof_chain_complete"] and
                    not response["required_changes"] and
                    response["fatal_obstruction"] is None and
                    response["line_audit"] and
                    response["quantifier_audit"] and
                    response["soundness_audit"] and
                    source_response.get("claimed_soundness") is not None and
                    response["verified_soundness"] == source_response.get("claimed_soundness") and
                    response["proof_chain_audit"] and
                    all(item["verdict"] == "valid" for key in (
                        "proof_chain_audit", "line_audit", "quantifier_audit",
                        "soundness_audit", "literature_audit")
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
        if (succeeded and not job_id.startswith("verifier-") and
                self._is_leaderboard_submission_id(job_id)):
            self._enqueue_verifier(job_id)

    def export_status(self) -> dict[str, Any]:
        with self.connect() as connection:
            counts = {row["status"]: row["count"] for row in connection.execute(
                "SELECT status,COUNT(*) AS count FROM campaign_jobs GROUP BY status")}
            roles = {row["role"]: row["count"] for row in connection.execute(
                "SELECT role,COUNT(*) AS count FROM campaign_jobs GROUP BY role")}
            rows = [dict(row) for row in connection.execute(
                "SELECT * FROM campaign_jobs ORDER BY id")]
        payload: dict[str, Any] = {
            "campaign_dir": str(self.paths.campaign_dir),
            "model": self.provider.model,
            "reasoning_effort": self.provider.reasoning_effort,
            "dimension": int(self.cfg.get("dimension", 2)),
            "field_regime": str(self.cfg.get("field_regime", "prime")),
            "fixed_prime": int(self.cfg.get("fixed_prime", 147457)),
            "fixed_degree": int(self.cfg.get("fixed_degree", 87)),
            "verifier_count": int(self.cfg.get("verifier_count", 1)),
            "verifier_reasoning_effort": str(self.cfg.get("verifier_reasoning_effort", "xhigh")),
            "verification_policy": "one independent high-reasoning audit for leaderboard submissions",
            "recovery_divisor": int(self.cfg.get("recovery_divisor", 10)),
            "minimum_soundness": "957/1474570",
            "minimum_recovery_fraction": "174/147457",
            "minimum_recovery_agreement_count": int(self.cfg.get("minimum_recovery_agreement_count", 25657518)),
            "initial_soundness": float(self.cfg.get("initial_soundness", 1.0)),
            "researcher_count": int(self.cfg["researcher_count"]),
            "literature_agent_count": (
                1 if self.cfg.get("literature_agent_enabled", True) else 0),
            "planned_agent_invocations": (
                (int(self.cfg["researcher_count"]) +
                 (1 if self.cfg.get("literature_agent_enabled", True) else 0)) *
                 ((1 if self.cfg.get("verifier_enabled", True) else 0) +
                 (1 if self.cfg.get("lemma_writer_enabled", True) else 0)) +
                ((3 if self.cfg.get("genius_enabled", True) else 0) +
                 (1 if self.cfg.get("genius_enabled", True) and
                  self.cfg.get("lemma_writer_enabled", True) else 0))),
            "counts": counts,
            "roles": roles,
        }
        status_path = self.paths.campaign_dir / "status.json"
        previous: dict[str, Any] = {}
        if status_path.exists():
            try:
                previous = json.loads(status_path.read_text())
            except (json.JSONDecodeError, OSError):
                previous = {}
        previous_semantics = {key: value for key, value in previous.items() if key != "updated_at"}
        payload["updated_at"] = (
            previous.get("updated_at", utc_timestamp())
            if previous_semantics == payload else utc_timestamp())
        status_path.write_text(
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
            for stage in response.get("soundness_ledger", []):
                bottlenecks.append({"job_id": row["id"], **stage})
            leaderboard_submission = self._is_leaderboard_submission(response)
            if not leaderboard_submission:
                continue
            audits = []
            for seat in ("a",):
                verifier_id = f"verifier-{seat}-{row['id']}"
                audit_path = (self.paths.campaign_dir / "reviews" / row["id"] /
                              verifier_id / "audit.json")
                if audit_path.exists():
                    audits.append({"verifier_id": verifier_id, **json.loads(audit_path.read_text())})
            claim = response.get("theorem_statement") or response.get("integrated_theorem", "")
            claim_hash = hashlib.sha256(claim.encode()).hexdigest()
            claimed = response.get("claimed_soundness")
            agreement_count = None
            if claimed is not None:
                normalized = Fraction(str(claimed)) * (147457 ** 2)
                agreement_count = (normalized.numerator + normalized.denominator - 1) // normalized.denominator
            def chain_verified(audit: dict[str, Any]) -> bool:
                chain = audit.get("proof_chain_audit") or audit.get("line_audit") or []
                complete = (
                    audit.get("proof_chain_complete") is True or
                    ("proof_chain_complete" not in audit and
                     audit.get("coverage_complete") is True)
                )
                return bool(complete and chain and
                            all(item.get("verdict") == "valid" for item in chain))
            independently_verified = (
                leaderboard_submission and len(audits) == 1 and claimed is not None and
                response.get("result_status") == "proved" and
                all(audit.get("verdict") == "accept" for audit in audits) and
                all(audit.get("verified_claim_sha256") == claim_hash for audit in audits) and
                all(audit.get("verified_soundness") == claimed for audit in audits) and
                all(chain_verified(audit) for audit in audits))
            if independently_verified:
                review_verdict = "accept"
            elif any(audit.get("verdict") == "reject" for audit in audits):
                review_verdict = "rejected"
            elif audits:
                review_verdict = f"awaiting ({sum(a.get('verdict') == 'accept' for a in audits)}/1 accept)"
            else:
                review_verdict = "awaiting (0/1 accept)"
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
                "agreement_count": agreement_count,
                "recovery_agreement_count": max(
                    int(self.cfg.get("minimum_recovery_agreement_count", 25657518)),
                    ((agreement_count + 9) // 10 if agreement_count is not None else 0),
                ) if agreement_count is not None else None,
                "leaderboard_submission": leaderboard_submission,
                "benchmark_improved": response.get("benchmark_improved", False),
                "theorem_statement": claim,
                "theorem_sha256": claim_hash,
                "note_path": str(response_path.parent / "note.md"),
                "review_verdict": review_verdict,
                "double_verified": independently_verified,
                "audits": audits,
            }
            if independently_verified:
                verified.append(entry)
            elif review_verdict == "rejected":
                rejected.append(entry)
            else:
                promising.append(entry)
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
                "agreement_count": entry["agreement_count"],
                "recovery_agreement_count": entry["recovery_agreement_count"],
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
                "score_metric": "guaranteed agreement-count equivalent ceil(epsilon * p^2)",
                "score_unit": "points in F_p^2",
                "verification_threshold": 1,
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
        for entries in candidate_groups.values():
            for entry in entries:
                entry.setdefault("campaign", self.paths.campaign_dir.name)
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
            "bottlenecks": [
                {**entry, "campaign": self.paths.campaign_dir.name}
                for entry in load_board("bottleneck-ledger")
            ],
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

    def run_specific_job(self, job_id: str) -> dict[str, Any]:
        """Run one queued job immediately without disturbing the main campaign runner."""
        while True:
            with self.connect() as connection:
                stored = connection.execute(
                    "SELECT * FROM campaign_jobs WHERE id=?", (job_id,)).fetchone()
            if stored is None:
                raise ValueError(f"unknown campaign job: {job_id}")
            row = dict(stored)
            if row["status"] != "queued":
                return {"job_id": job_id, "status": row["status"], **self.export_status()}
            if not self._claim(job_id):
                continue
            job_id, succeeded, error = self._run_job(row)
            self._finish(job_id, succeeded, error)
            status = self.export_status()
            with self.connect() as connection:
                final = connection.execute(
                    "SELECT status,attempts,error FROM campaign_jobs WHERE id=?",
                    (job_id,)).fetchone()
            if final["status"] != "queued":
                return {
                    "job_id": job_id,
                    "job_status": final["status"],
                    "attempts": final["attempts"],
                    "error": final["error"],
                    **status,
                }
            time.sleep(min(self.retry_seconds, 30))


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


def launch_campaign_job(config_path: Path | str, job_id: str) -> dict[str, Any]:
    _, paths = load_campaign_config(config_path)
    if not job_id or any(character not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for character in job_id):
        raise ValueError("job_id contains unsupported characters")
    runtime = paths.campaign_dir / "specific-jobs" / job_id
    runtime.mkdir(parents=True, exist_ok=True)
    pid_path = runtime / "runner.json"
    if pid_path.exists():
        old = json.loads(pid_path.read_text())
        try:
            os.kill(int(old["pid"]), 0)
            return {"status": "already_running", **old}
        except (OSError, KeyError, ValueError):
            pass
    log_path = runtime / "job.log"
    log_handle = log_path.open("a")
    environment = os.environ.copy()
    source_path = str(paths.workspace / "src")
    environment["PYTHONPATH"] = (
        source_path + os.pathsep + environment["PYTHONPATH"]
        if environment.get("PYTHONPATH") else source_path)
    environment["PYTHONPYCACHEPREFIX"] = str(runtime / "python-cache")
    process = subprocess.Popen(
        [sys.executable, "-m", "line_point_research", "campaign-run-job",
         str(Path(config_path).resolve()), job_id],
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
        "job_id": job_id,
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
