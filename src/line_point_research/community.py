from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .campaign import RESEARCH_SCHEMA, SCHEMA, ResearchCampaign, utc_timestamp


COMMUNITY_SCHEMA = "line-point-community-submission-v1"
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
METADATA_KEYS = {"schema", "slug", "contributor"}
NOTE_HEADINGS = (
    "Abstract",
    "Test and Notation",
    "Prior Results",
    "Proof",
    "Soundness Ledger",
    "Counterexample Attempts",
    "Characteristic Audit",
    "Limitations",
)


def canonical_json_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_community_package(package_path: Path | str) -> dict[str, Any]:
    package = Path(package_path).resolve()
    errors: list[str] = []
    submission_path = package / "submission.json"
    note_path = package / "note.md"
    if not package.is_dir():
        return {"valid": False, "errors": [f"not a directory: {package}"]}
    if not submission_path.is_file():
        errors.append("missing submission.json")
    if not note_path.is_file():
        errors.append("missing note.md")
    if errors:
        return {"valid": False, "errors": errors, "package": str(package)}

    try:
        data = json.loads(submission_path.read_text())
    except json.JSONDecodeError as exc:
        return {
            "valid": False,
            "errors": [f"submission.json is invalid JSON: {exc}"],
            "package": str(package),
        }
    if not isinstance(data, dict):
        return {
            "valid": False,
            "errors": ["submission.json must contain one JSON object"],
            "package": str(package),
        }

    if data.get("schema") != COMMUNITY_SCHEMA:
        errors.append(f"schema must equal {COMMUNITY_SCHEMA}")
    slug = str(data.get("slug", ""))
    if not SLUG_PATTERN.fullmatch(slug):
        errors.append("slug must contain lowercase letters, digits, and single hyphens only")
    if package.name != slug:
        errors.append("the package directory name must exactly equal slug")
    contributor = data.get("contributor")
    if not isinstance(contributor, dict):
        errors.append("contributor must be an object")
    else:
        for key in ("name", "github", "ai_assistance"):
            if not str(contributor.get(key, "")).strip():
                errors.append(f"contributor.{key} must be nonempty")

    response = {key: value for key, value in data.items() if key not in METADATA_KEYS}
    if "note_markdown" in response:
        errors.append("put the note in note.md; do not add note_markdown to submission.json")
    note = note_path.read_text()
    response["note_markdown"] = note.rstrip() + "\n"
    for key in RESEARCH_SCHEMA["required"]:
        if key not in response:
            errors.append(f"missing required submission field: {key}")
    expected = {
        "dimension": 2,
        "field_regime": "prime",
        "fixed_prime": 147457,
        "fixed_degree": 87,
    }
    for key, value in expected.items():
        if response.get(key) != value:
            errors.append(f"{key} must equal {value!r}")
    if response.get("claim_scope") not in {
        "bivariate_theorem", "algebraic_lemma", "combinatorial_lemma",
        "obstruction", "counterexample", "proof_tool",
    }:
        errors.append("invalid claim_scope")
    if response.get("result_status") not in {
        "proved", "conditional", "conjectural", "refuted",
    }:
        errors.append("invalid result_status")
    proof_steps = response.get("proof_steps")
    if not isinstance(proof_steps, list) or not proof_steps:
        errors.append("proof_steps must be a nonempty array")
    soundness_ledger = response.get("soundness_ledger")
    if not isinstance(soundness_ledger, list) or not soundness_ledger:
        errors.append("soundness_ledger must be a nonempty array")
    lowered_note = note.lower()
    if len(note) < 1200:
        errors.append("note.md must contain at least 1200 characters")
    for heading in NOTE_HEADINGS:
        if heading.lower() not in lowered_note:
            errors.append(f"note.md is missing the {heading} section")

    leaderboard = response.get("leaderboard_submission") is True
    if leaderboard:
        if response.get("claim_scope") != "bivariate_theorem":
            errors.append("a leaderboard submission must have claim_scope=bivariate_theorem")
        if response.get("result_status") != "proved":
            errors.append("a leaderboard submission must have result_status=proved")
        if response.get("benchmark_improved") is not True:
            errors.append("a leaderboard submission must have benchmark_improved=true")
        soundness = response.get("claimed_soundness")
        if (not isinstance(soundness, (int, float)) or isinstance(soundness, bool) or
                not 0 < float(soundness) <= 1):
            errors.append("a leaderboard submission needs claimed_soundness in (0,1]")
        for step in proof_steps if isinstance(proof_steps, list) else []:
            if not isinstance(step, dict) or step.get("status") != "proved":
                errors.append("every leaderboard proof step must be proved")
                break
        for stage in soundness_ledger if isinstance(soundness_ledger, list) else []:
            if not isinstance(stage, dict) or stage.get("status") != "proved":
                errors.append("every leaderboard soundness-ledger stage must be proved")
                break
    elif response.get("benchmark_improved") is True:
        errors.append("benchmark_improved=true requires leaderboard_submission=true")

    return {
        "valid": not errors,
        "errors": errors,
        "package": str(package),
        "slug": slug,
        "contributor": contributor,
        "leaderboard_submission": leaderboard,
        "submission_sha256": canonical_json_sha256(data),
        "note_sha256": hashlib.sha256(note.encode()).hexdigest(),
        "response": response,
    }


def validate_community_directory(root: Path | str) -> dict[str, Any]:
    directory = Path(root).resolve()
    packages = []
    if directory.is_dir():
        packages = sorted(path for path in directory.iterdir() if path.is_dir())
    results = [validate_community_package(path) for path in packages]
    return {
        "valid": all(result["valid"] for result in results),
        "root": str(directory),
        "package_count": len(results),
        "results": results,
    }


def ingest_community_package(
        config_path: Path | str, package_path: Path | str) -> dict[str, Any]:
    validation = validate_community_package(package_path)
    if not validation["valid"]:
        raise ValueError("invalid community submission: " + "; ".join(validation["errors"]))
    campaign = ResearchCampaign(config_path)
    response = validation["response"]
    static = campaign._static_check("researcher", response)
    if not static["passed"]:
        raise ValueError("submission failed campaign checks: " + "; ".join(static["errors"]))

    slug = validation["slug"]
    job_id = f"community-{slug}"
    output_dir = campaign.paths.campaign_dir / "submissions" / job_id
    response_sha = canonical_json_sha256(response)
    existing = output_dir / "response.json"
    if existing.exists():
        existing_sha = canonical_json_sha256(json.loads(existing.read_text()))
        if existing_sha != response_sha:
            raise ValueError(f"immutable submission {job_id} already exists with different content")
    else:
        output_dir.mkdir(parents=True, exist_ok=False)
        (output_dir / "response.json").write_text(
            json.dumps(response, indent=2, sort_keys=True) + "\n")
        (output_dir / "note.md").write_text(response["note_markdown"])
        (output_dir / "manifest.json").write_text(json.dumps({
            "schema": "line-point-community-ingest-v1",
            "job_id": job_id,
            "source_package": str(Path(package_path).resolve()),
            "contributor": validation["contributor"],
            "source_submission_sha256": validation["submission_sha256"],
            "response_sha256": response_sha,
            "note_sha256": validation["note_sha256"],
            "static_check": static,
            "ingested_at": utc_timestamp(),
        }, indent=2, sort_keys=True) + "\n")

    with campaign.connect() as connection:
        connection.executescript(SCHEMA)
        connection.execute(
            """INSERT OR IGNORE INTO campaign_jobs
            (id,role,ordinal,direction,dependency,status,attempts,max_attempts,output_dir,error,
             model,reasoning_effort,created_at,started_at,finished_at)
            VALUES (?, 'researcher', NULL, ?, NULL, 'succeeded', 1, 1, ?, NULL,
                    'community-contributor', 'external', ?, ?, ?)""",
            (job_id, f"community submission by {validation['contributor']['github']}",
             str(output_dir), utc_timestamp(), utc_timestamp(), utc_timestamp()),
        )
    if validation["leaderboard_submission"]:
        campaign._enqueue_verifier(job_id)
    status = campaign.export_status()
    return {
        "job_id": job_id,
        "leaderboard_submission": validation["leaderboard_submission"],
        "verification_queued": validation["leaderboard_submission"],
        "submission_sha256": validation["submission_sha256"],
        "campaign": status,
    }

