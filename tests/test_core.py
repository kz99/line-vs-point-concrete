import json
import hashlib
import tempfile
import unittest
from pathlib import Path

from line_point_research.agents import CommandAgentProvider
from line_point_research.campaign import ResearchCampaign
from line_point_research.community import ingest_community_package, validate_community_package
from line_point_research.lemma_book import LEMMA_STATEMENT_RULE, canonical_sha256, validate_editorial_response
from line_point_research.roadmaps import ROADMAP_DEFINITIONS, RoadmapWorkshop


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

    def test_prompt_uses_exact_soundness_definition(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign = ResearchCampaign(write_config(Path(directory), 1))
            prompt = campaign._research_prompt({"id": "researcher-0001", "ordinal": 1, "direction": "test"})
            self.assertIn("p=147457", prompt)
            self.assertIn("total degree d=87", prompt)
            self.assertIn("epsilon/10", prompt)
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
            snapshot = json.loads((root / "dashboard" / "public" / "research-data.json").read_text())
            self.assertEqual(snapshot["soundness_history"]["verification_threshold"], 1)
            self.assertEqual(snapshot["soundness_history"]["points"], [])

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

    def test_three_roadmaps_require_double_accept_for_progress(self):
        self.assertEqual([item["id"] for item in ROADMAP_DEFINITIONS], ["exact-analytic", "certified-computation", "end-to-end-soundness"])
        nodes, progress = RoadmapWorkshop._derive_progress([{
            "id": "R1", "kind": "lemma", "work_state": "candidate", "dependencies": [],
            "evidence_refs": [{"source_job_id": "researcher-0001", "source_step_id": "P1", "source_response_sha256": "hash"}],
        }], "R1", {"researcher-0001|P1|hash": {
            "source_status": "proved", "audit_verdicts": ["accept", "accept"],
            "double_audit_exact": True, "double_accepted": True, "lemma_ids": [],
        }})
        self.assertEqual(progress["percent"], 100)
        self.assertEqual(nodes[0]["proof_state"], "verified")


if __name__ == "__main__":
    unittest.main()
