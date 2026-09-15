import json
import hashlib
import base64
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from line_point_research.agents import CommandAgentProvider
from line_point_research.campaign import ResearchCampaign
from line_point_research.community import ingest_community_package, validate_community_package
from line_point_research.lemma_book import LEMMA_STATEMENT_RULE, canonical_sha256, validate_editorial_response
from line_point_research.roadmaps import ROADMAP_DEFINITIONS, RoadmapWorkshop
from line_point_research.publisher import RepositoryPublisher
from line_point_research.snapshot import update_dashboard_sections


INGEST_SPEC = importlib.util.spec_from_file_location(
    "ingest_external_submissions",
    Path(__file__).resolve().parents[1] / "scripts" / "ingest_external_submissions.py",
)
assert INGEST_SPEC and INGEST_SPEC.loader
ingest_external = importlib.util.module_from_spec(INGEST_SPEC)
INGEST_SPEC.loader.exec_module(ingest_external)

MANIFEST_SPEC = importlib.util.spec_from_file_location(
    "build_data_manifest",
    Path(__file__).resolve().parents[1] / "scripts" / "build_data_manifest.py",
)
assert MANIFEST_SPEC and MANIFEST_SPEC.loader
ingest_manifest = importlib.util.module_from_spec(MANIFEST_SPEC)
MANIFEST_SPEC.loader.exec_module(ingest_manifest)


def write_config(root: Path, researchers: int = 10, effort: str = "ultra") -> Path:
    path = root / "campaign.yaml"
    path.write_text(f"""workspace: .
corpus_root: ./corpus
campaign_dir: ./state
campaign:
  researcher_count: {researchers}
  dimension: 2
  field_regime: prime
  fixed_prime: 147457
  fixed_degree: 87
  verifier_enabled: true
  verifier_count: 1
  lemma_writer_enabled: true
  genius_enabled: false
  model: gpt-5.6-sol
  reasoning_effort: {effort}
  initial_soundness: 1.0
  recovery_divisor: 10
  minimum_soundness_numerator: 957
  minimum_soundness_denominator: 1474570
  minimum_recovery_agreement_count: 25657518
""")
    return path


class ProviderTests(unittest.TestCase):
    def test_provider_pins_model_and_ultra_reasoning(self):
        with tempfile.TemporaryDirectory() as directory:
            provider = CommandAgentProvider(".", Path(directory) / "logs", model="gpt-5.6-sol", reasoning_effort="ultra", disable_nested_agents=True)
            command = provider.command(Path("schema.json"), Path("output.json"))
            self.assertIn("gpt-5.6-sol", command)
            self.assertIn('model_reasoning_effort="ultra"', command)
            self.assertEqual(command[command.index("--disable") + 1], "multi_agent")

    def test_provider_grants_only_the_checkpoint_outbox(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            provider = CommandAgentProvider(
                root, root / "logs", checkpoint_root=root / "live-notes")
            outbox = root / "live-notes" / "researcher-0001"
            command = provider.command(root / "schema.json", root / "response.json", outbox)
            self.assertEqual(command[command.index("--sandbox") + 1], "read-only")
            self.assertEqual(command[command.index("--add-dir") + 1], str(outbox))


class CampaignTests(unittest.TestCase):
    def test_trial_is_fixed_and_ready_but_not_started(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            campaign = ResearchCampaign(write_config(root))
            campaign.initialize()
            status = campaign.export_status()
            self.assertEqual(status["counts"], {"queued": 11})
            self.assertEqual(status["fixed_prime"], 147457)
            self.assertEqual(status["fixed_degree"], 87)
            self.assertEqual(status["verifier_count"], 1)
            self.assertEqual(status["literature_agent_count"], 1)
            self.assertEqual(status["planned_agent_invocations"], 22)

    def test_each_submission_enqueues_one_verifier(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            campaign = ResearchCampaign(write_config(root, 1))
            campaign.initialize()
            campaign._enqueue_verifier("researcher-0001")
            with campaign.connect() as connection:
                ids = {row[0] for row in connection.execute("SELECT id FROM campaign_jobs WHERE role='verifier'")}
            self.assertEqual(ids, {"verifier-a-researcher-0001"})

    def test_thirty_researchers_form_one_dependency_graph(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign = ResearchCampaign(write_config(Path(directory), 30))
            campaign.initialize()
            with campaign.connect() as connection:
                jobs = {row["id"]: dict(row) for row in connection.execute(
                    "SELECT * FROM campaign_jobs WHERE role='researcher'")}
            self.assertEqual(len(jobs), 31)  # 30 team seats plus the literature seat
            self.assertIsNone(jobs["researcher-0001"]["dependency"])
            self.assertEqual(
                json.loads(jobs["researcher-0007"]["dependency"]),
                ["researcher-0001", "researcher-0002"],
            )
            self.assertEqual(
                json.loads(jobs["researcher-0030"]["dependency"]),
                ["researcher-0028", "researcher-0029"],
            )
            self.assertEqual(
                [row["id"] for row in campaign._ready(30)],
                ["literature-sota-0001"] +
                [f"researcher-{index:04d}" for index in range(1, 7)],
            )

    def test_frugal_ten_seat_funnel_gates_expensive_agents(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = write_config(root, 10)
            text = config.read_text().replace(
                "researcher_count: 10",
                "researcher_count: 10\n  team_architecture: frugal-funnel-v1\n"
                "  literature_agent_enabled: false\n"
                "  researcher_reasoning_efforts: [xhigh, xhigh, xhigh, xhigh, xhigh, xhigh, max, max, xhigh, ultra]",
            )
            config.write_text(text)
            campaign = ResearchCampaign(config)
            campaign.initialize()
            with campaign.connect() as connection:
                jobs = {row["id"]: dict(row) for row in connection.execute(
                    "SELECT * FROM campaign_jobs WHERE role='researcher'")}
            self.assertEqual(len(jobs), 10)
            self.assertTrue(jobs["researcher-0001"]["direction"].startswith("FRUGAL FUNNEL / SCOUT"))
            self.assertEqual(
                json.loads(jobs["researcher-0007"]["dependency"]),
                ["researcher-0001", "researcher-0004", "researcher-0006"],
            )
            self.assertEqual(
                json.loads(jobs["researcher-0010"]["dependency"]),
                ["researcher-0007", "researcher-0008", "researcher-0009"],
            )
            self.assertEqual(jobs["researcher-0001"]["reasoning_effort"], "xhigh")
            self.assertEqual(jobs["researcher-0007"]["reasoning_effort"], "max")
            self.assertEqual(jobs["researcher-0010"]["reasoning_effort"], "ultra")
            self.assertEqual(
                [row["id"] for row in campaign._ready(10)],
                [f"researcher-{index:04d}" for index in range(1, 7)],
            )
            prompt = campaign._research_prompt(jobs["researcher-0001"])
            self.assertIn("token-efficient ten-seat scout-to-proof funnel", prompt)
            self.assertIn("target at most\n2,500 words", prompt)
            self.assertIn("One independent\nxhigh verifier", prompt)
            self.assertNotIn("30-agent proof team", prompt)

    def test_prompt_uses_exact_soundness_definition(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign = ResearchCampaign(write_config(Path(directory), 1))
            prompt = campaign._research_prompt({"id": "researcher-0001", "ordinal": 1, "direction": "test"})
            self.assertIn("p=147457", prompt)
            self.assertIn("total degree d=87", prompt)
            self.assertIn("epsilon >= 957/1474570", prompt)
            self.assertIn("max(174/147457, epsilon/10)", prompt)
            self.assertIn("Lower absolute agreement-count scores are stronger", prompt)
            self.assertIn("A lemma statement contains only", prompt)
            self.assertIn("leaderboard_submission=true", prompt)

    def test_literature_agent_demands_primary_exact_constants(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign = ResearchCampaign(write_config(Path(directory), 1))
            prompt = campaign._research_prompt({
                "id": "literature-sota-0001", "ordinal": 0,
                "direction": "establish the literature baseline",
            })
            self.assertIn("Search primary sources", prompt)
            self.assertIn("Kominers--Thaler--Zheng", prompt)
            self.assertIn("claimed_soundness=null", prompt)
            self.assertIn("p=147457,d=87", prompt)

    def test_rejects_parameter_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            text = write_config(root).read_text().replace("fixed_degree: 87", "fixed_degree: 86")
            (root / "campaign.yaml").write_text(text)
            with self.assertRaisesRegex(ValueError, "fixed_degree must be 87"):
                ResearchCampaign(root / "campaign.yaml")

    def test_dashboard_snapshot_contains_empty_guarded_history(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "dashboard" / "public").mkdir(parents=True)
            (root / "dashboard" / "public" / "research-data.json").write_text("{}")
            campaign = ResearchCampaign(write_config(root, 1))
            campaign.initialize()
            first_updated_at = campaign.export_status()["updated_at"]
            self.assertEqual(campaign.export_status()["updated_at"], first_updated_at)
            snapshot = json.loads((root / "dashboard" / "public" / "research-data.json").read_text())
            self.assertEqual(snapshot["soundness_history"]["verification_threshold"], 1)
            self.assertEqual(snapshot["soundness_history"]["points"], [])

    def test_new_campaign_snapshot_never_erases_prior_research(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            public = workspace / "dashboard" / "public"
            public.mkdir(parents=True)
            old_point = {
                "agreement_count": 7349491214, "soundness": 0.338,
                "title": "incumbent", "theorem_sha256": "old", "verified_at": "2026-01-01",
            }
            old_candidate = {"job_id": "researcher-0002", "title": "incumbent", "theorem_sha256": "old"}
            old_lemma = {"id": "L1"}
            (public / "research-data.json").write_text(json.dumps({
                "campaign": "old", "candidates": {"verified": [old_candidate], "promising": [], "rejected": []},
                "soundness_history": {"points": [old_point]},
                "bottlenecks": [{"stage": "old"}],
                "lemma_book": {"lemmas": [old_lemma]},
            }))
            update_dashboard_sections(workspace, {
                "campaign": "new", "candidates": {"verified": [], "promising": [], "rejected": []},
                "soundness_history": {"points": []}, "bottlenecks": [],
                "jobs": [{"id": "researcher-0001"}],
            }, replace_base=True)
            snapshot = json.loads((public / "research-data.json").read_text())
            self.assertEqual(snapshot["campaign"], "new")
            self.assertEqual(snapshot["candidates"]["verified"], [old_candidate])
            self.assertEqual(snapshot["soundness_history"]["points"], [old_point])
            self.assertEqual(snapshot["bottlenecks"], [{"stage": "old"}])
            self.assertEqual(snapshot["lemma_book"]["lemmas"], [old_lemma])

    def test_repository_publisher_selects_notes_but_not_runtime_data(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = write_config(root, 1)
            notes = root / "state" / "live_notes" / "researcher-0001"
            notes.mkdir(parents=True)
            (notes / "001-lemma.md").write_text("STATUS: conjectural\n")
            (root / "state" / "campaign.sqlite3").write_text("runtime")
            paths = RepositoryPublisher(config).artifact_paths()
            self.assertIn((root / "state" / "live_notes").resolve(), paths)
            self.assertNotIn((root / "state" / "campaign.sqlite3").resolve(), paths)

    def test_index_manifest_ignores_untracked_runtime_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "research_state" / "campaign" / "submissions").mkdir(parents=True)
            tracked = root / "research_state" / "campaign" / "submissions" / "note.md"
            tracked.write_text("durable\n")
            untracked = root / "research_state" / "campaign" / "agent_logs" / "trace.txt"
            untracked.parent.mkdir(parents=True)
            untracked.write_text("runtime\n")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "add", str(tracked.relative_to(root))], cwd=root, check=True)
            previous_root, previous_data_root, previous_output = (
                ingest_manifest.ROOT, ingest_manifest.DATA_ROOT, ingest_manifest.OUTPUT,
            )
            previous_argv = sys.argv
            try:
                ingest_manifest.ROOT = root
                ingest_manifest.DATA_ROOT = root / "research_state"
                ingest_manifest.OUTPUT = root / "research_state" / "DATA_MANIFEST.json"
                sys.argv = ["build_data_manifest.py", "--index"]
                ingest_manifest.main()
            finally:
                ingest_manifest.ROOT, ingest_manifest.DATA_ROOT, ingest_manifest.OUTPUT = (
                    previous_root, previous_data_root, previous_output,
                )
                sys.argv = previous_argv
            manifest = json.loads((root / "research_state" / "DATA_MANIFEST.json").read_text())
            self.assertEqual([item["path"] for item in manifest["files"]], [
                "research_state/campaign/submissions/note.md",
            ])

    def test_graph_requires_one_accept(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "dashboard" / "public").mkdir(parents=True)
            (root / "dashboard" / "public" / "research-data.json").write_text("{}")
            campaign = ResearchCampaign(write_config(root, 1))
            campaign.initialize()
            theorem = "Every accepted table has the required polynomial."
            response = {
                "title": "Candidate", "result_status": "proved", "dimension": 2,
                "field_regime": "prime", "fixed_prime": 147457, "fixed_degree": 87,
                "claim_scope": "bivariate_theorem", "claimed_soundness": 0.2,
                "guaranteed_recovery_fraction": 0.2,
                "guaranteed_recovery_agreement_count": 147457 ** 2,
                "leaderboard_submission": True, "benchmark_improved": True,
                "theorem_statement": theorem,
                "proof_steps": [], "soundness_ledger": [],
            }
            submission = root / "state" / "submissions" / "researcher-0001"
            submission.mkdir(parents=True)
            (submission / "response.json").write_text(json.dumps(response))
            (submission / "note.md").write_text("proof")
            with campaign.connect() as connection:
                connection.execute("UPDATE campaign_jobs SET status='succeeded',finished_at='2026-09-14T00:00:00Z' WHERE id='researcher-0001'")
            claim_hash = hashlib.sha256(theorem.encode()).hexdigest()
            audit = {
                "verdict": "accept", "verified_claim_sha256": claim_hash,
                "verified_soundness": 0.2, "proof_chain_complete": True,
                "proof_chain_audit": [{"reference": "P1", "verdict": "valid"}],
            }
            first = root / "state" / "reviews" / "researcher-0001" / "verifier-a-researcher-0001"
            first.mkdir(parents=True)
            (first / "audit.json").write_text(json.dumps(audit))
            campaign.export_status()
            history = json.loads((root / "state" / "leaderboards" / "soundness-history.json").read_text())
            self.assertEqual([point["soundness"] for point in history["points"]], [0.2])

    def test_reconcile_skips_lemma_audits_and_enqueues_leaderboard_audits(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            campaign = ResearchCampaign(write_config(root, 2))
            campaign.initialize()
            submissions = root / "state" / "submissions"
            for job_id, response in (
                ("researcher-0001", {
                    "leaderboard_submission": False, "claim_scope": "algebraic_lemma",
                }),
                ("researcher-0002", {
                    "leaderboard_submission": True, "claim_scope": "bivariate_theorem",
                    "result_status": "proved", "benchmark_improved": True,
                    "claimed_soundness": 0.2,
                    "guaranteed_recovery_fraction": 0.2,
                    "guaranteed_recovery_agreement_count": 147457 ** 2,
                }),
            ):
                target = submissions / job_id
                target.mkdir(parents=True)
                (target / "response.json").write_text(json.dumps(response))
            with campaign.connect() as connection:
                connection.execute(
                    "UPDATE campaign_jobs SET status='succeeded' "
                    "WHERE id IN ('researcher-0001','researcher-0002')")
            campaign._enqueue_verifier("researcher-0001")
            campaign.reconcile_verifier_queue()
            with campaign.connect() as connection:
                rows = {row[0]: row[1] for row in connection.execute(
                    "SELECT id,status FROM campaign_jobs WHERE role='verifier'")}
            self.assertEqual(rows["verifier-a-researcher-0001"], "skipped")
            self.assertEqual(rows["verifier-a-researcher-0002"], "queued")

    def test_community_leaderboard_package_queues_one_audit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = write_config(root, 1)
            ResearchCampaign(config).initialize()
            package = root / "alice-explicit-bound"
            package.mkdir()
            submission = {
                "schema": "line-point-community-submission-v1",
                "slug": "alice-explicit-bound",
                "contributor": {
                    "name": "Alice", "github": "alice", "ai_assistance": "none",
                },
                "title": "Explicit bound", "dimension": 2, "field_regime": "prime",
                "fixed_prime": 147457, "fixed_degree": 87, "result_status": "proved",
                "claim_scope": "bivariate_theorem", "leaderboard_submission": True,
                "benchmark_improved": True, "claimed_soundness": 0.5,
                "guaranteed_recovery_fraction": 0.5,
                "guaranteed_recovery_agreement_count": 147457 ** 2,
                "theorem_statement": "Pass at least 1/2 implies agreement at least 1/20.",
                "parameter_regime": "m=2,p=147457,d=87",
                "sampling_model": "uniform affine line then uniform point",
                "global_conclusion": "one polynomial has agreement at least 1/20",
                "literature_dependencies": [],
                "proof_steps": [{
                    "id": "P1", "statement": "The theorem holds.", "status": "proved",
                    "proof": "Exact proof.", "dependencies": [],
                }],
                "soundness_ledger": [{
                    "stage": "all", "input_bound": "1/2", "output_bound": "1/20",
                    "loss": "1/10", "justification": "P1", "status": "proved",
                }],
                "counterexample_attempts": [], "characteristic_audit": [],
                "finite_sanity_checks": [], "obstructions": [], "next_tasks": [],
            }
            (package / "submission.json").write_text(json.dumps(submission))
            headings = (
                "# Explicit bound\n\n## Abstract\nResult.\n\n"
                "## Test and Notation\nFixed test.\n\n## Prior Results\nNone.\n\n"
                "## Main Theorem\nClaim.\n\n## Proof\nProof.\n\n"
                "## Soundness Ledger\nExact.\n\n## Counterexample Attempts\nDone.\n\n"
                "## Characteristic Audit\nDone.\n\n## Limitations\nNone.\n\n"
            )
            (package / "note.md").write_text(headings + "Detailed proof. " * 100)
            self.assertTrue(validate_community_package(package)["valid"])
            result = ingest_community_package(config, package)
            self.assertTrue(result["verification_queued"])
            campaign = ResearchCampaign(config)
            with campaign.connect() as connection:
                ids = {row[0] for row in connection.execute(
                    "SELECT id FROM campaign_jobs WHERE role='verifier' AND dependency=?",
                    ("community-alice-explicit-bound",))}
            self.assertEqual(ids, {"verifier-a-community-alice-explicit-bound"})


class EditorialAndRoadmapTests(unittest.TestCase):
    def test_lemma_writer_can_split_without_changing_status(self):
        source = {"proof_steps": [{"id": "P1", "status": "proved"}]}
        response = {
            "source_job_id": "researcher-0001", "source_response_sha256": canonical_sha256(source),
            "coverage_complete": True, "omitted_source_step_ids": [],
            "lemmas": [
                {"id": "researcher-0001:P1.1", "source_step_id": "P1", "part": 1, "statement_markdown": "$x=0$.", "proof_markdown": "Proof.", "status": "proved"},
                {"id": "researcher-0001:P1.2", "source_step_id": "P1", "part": 2, "statement_markdown": "$x^2=0$.", "proof_markdown": "Proof.", "status": "proved"},
            ],
        }
        self.assertEqual(validate_editorial_response("researcher-0001", source, response), [])
        self.assertIn("no motivation", LEMMA_STATEMENT_RULE)

    def test_three_roadmaps_require_one_accept_for_progress(self):
        self.assertEqual([item["id"] for item in ROADMAP_DEFINITIONS], ["exact-analytic", "certified-computation", "end-to-end-soundness"])
        nodes, progress = RoadmapWorkshop._derive_progress([{
            "id": "R1", "kind": "lemma", "work_state": "candidate", "dependencies": [],
            "evidence_refs": [{"source_job_id": "researcher-0001", "source_step_id": "P1", "source_response_sha256": "hash"}],
        }], "R1", {"researcher-0001|P1|hash": {
            "source_status": "proved", "audit_verdicts": ["accept"],
            "audit_exact": True, "accepted": True, "lemma_ids": [],
        }})
        self.assertEqual(progress["percent"], 100)
        self.assertEqual(nodes[0]["proof_state"], "verified")


class ExternalContributionTests(unittest.TestCase):
    def test_research_bundle_needs_no_agreement_score(self):
        note = b"# Standalone lemma\n\nA proved incidence statement.\n"
        bundle = {
            "schema": "line-point-handoff-bundle-v1",
            "manifest": {
                "schema": "line-point-external-submission-v2",
                "contribution_type": "research",
                "title": "Standalone lemma",
                "author": "anonymous",
                "filename": "note.md",
                "absolute_agreements": None,
                "fixed_prime": 147457,
                "fixed_degree": 87,
                "dimension": 2,
            },
            "document": {
                "filename": "note.md",
                "media_type": "text/markdown",
                "content_base64": base64.b64encode(note).decode(),
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inbox, destination = root / "inbox", root / "destination"
            inbox.mkdir()
            destination.mkdir()
            path = inbox / "standalone-lemma.lvp-submission.json"
            path.write_text(json.dumps(bundle))
            previous_destination = ingest_external.DESTINATION
            try:
                ingest_external.DESTINATION = destination
                valid, result = ingest_external.transfer_bundle(path)
            finally:
                ingest_external.DESTINATION = previous_destination
            self.assertTrue(valid, result)
            self.assertEqual((destination / "standalone-lemma" / "note.md").read_bytes(), note)
            manifest = json.loads((destination / "standalone-lemma" / "manifest.json").read_text())
            self.assertEqual(manifest["contribution_type"], "research")
            self.assertIsNone(manifest["absolute_agreements"])

    def test_leaderboard_bundle_requires_score(self):
        valid, reason = ingest_external.validate_manifest({
            "contribution_type": "leaderboard",
            "absolute_agreements": None,
            "fixed_prime": 147457,
            "fixed_degree": 87,
            "dimension": 2,
        })
        self.assertFalse(valid)
        self.assertIn("needs absolute_agreements", reason)

    def test_contributor_prompt_bootstraps_and_uses_one_verifier(self):
        prompt = (Path(__file__).resolve().parents[1] / "how_to_contribute" / "RESEARCH_PROMPT.md").read_text()
        self.assertIn("git clone https://github.com/kz99/line-vs-point-concrete.git", prompt)
        self.assertIn("validation is **deferred**", prompt)
        self.assertIn("valid research contribution even when", prompt)
        self.assertIn("One independent `xhigh` verifier", prompt)
        self.assertNotIn("Two independent AI auditors", prompt)
        self.assertNotIn("external intake inbox", prompt)


if __name__ == "__main__":
    unittest.main()
