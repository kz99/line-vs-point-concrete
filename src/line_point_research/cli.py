from __future__ import annotations

import argparse
import json

from .campaign import ResearchCampaign, campaign_status, launch_campaign, launch_campaign_job
from .community import (
    ingest_community_package,
    validate_community_directory,
    validate_community_package,
)
from .lemma_book import LemmaBookEditor, launch_lemma_book
from .publisher import (
    PagesPublisher,
    RepositoryPublisher,
    launch_pages_publisher,
    launch_repository_publisher,
)
from .roadmaps import RoadmapWorkshop, launch_roadmap_workshop


def cmd_campaign_init(args: argparse.Namespace) -> int:
    campaign = ResearchCampaign(args.config)
    campaign.initialize()
    print(json.dumps(campaign.export_status(), indent=2, sort_keys=True))
    return 0


def cmd_campaign_run(args: argparse.Namespace) -> int:
    print(json.dumps(ResearchCampaign(args.config).run(), indent=2, sort_keys=True))
    return 0


def cmd_campaign_run_job(args: argparse.Namespace) -> int:
    print(json.dumps(
        ResearchCampaign(args.config).run_specific_job(args.job_id), indent=2, sort_keys=True))
    return 0


def cmd_campaign_launch_job(args: argparse.Namespace) -> int:
    print(json.dumps(
        launch_campaign_job(args.config, args.job_id), indent=2, sort_keys=True))
    return 0


def cmd_community_validate(args: argparse.Namespace) -> int:
    result = validate_community_package(args.package)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


def cmd_community_validate_all(args: argparse.Namespace) -> int:
    result = validate_community_directory(args.root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


def cmd_community_ingest(args: argparse.Namespace) -> int:
    print(json.dumps(
        ingest_community_package(args.config, args.package), indent=2, sort_keys=True))
    return 0


def cmd_campaign_launch(args: argparse.Namespace) -> int:
    payload = {"campaign": launch_campaign(args.config)}
    campaign = ResearchCampaign(args.config)
    if bool(campaign.cfg.get("repository_publisher_enabled", True)):
        payload["repository"] = launch_repository_publisher(args.config)
    if bool(campaign.cfg.get("lemma_writer_enabled", True)):
        payload["lemma_book"] = launch_lemma_book(args.config)
    if bool(campaign.cfg.get("roadmap_agents_enabled", True)):
        payload["proof_roadmaps"] = launch_roadmap_workshop(args.config)
    if bool(campaign.cfg.get("pages_publisher_enabled", True)):
        payload["dashboard"] = launch_pages_publisher(args.config)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def cmd_campaign_status(args: argparse.Namespace) -> int:
    print(json.dumps(campaign_status(args.config), indent=2, sort_keys=True))
    return 0


def cmd_campaign_rebalance(args: argparse.Namespace) -> int:
    print(json.dumps(
        ResearchCampaign(args.config).rebalance_for_leaderboard(), indent=2, sort_keys=True))
    return 0


def cmd_campaign_reconcile_audits(args: argparse.Namespace) -> int:
    print(json.dumps(
        ResearchCampaign(args.config).reconcile_verifier_queue(), indent=2, sort_keys=True))
    return 0


def cmd_lemma_book_run(args: argparse.Namespace) -> int:
    print(json.dumps(
        LemmaBookEditor(args.config).run(watch=args.watch), indent=2, sort_keys=True))
    return 0


def cmd_lemma_book_launch(args: argparse.Namespace) -> int:
    print(json.dumps(launch_lemma_book(args.config), indent=2, sort_keys=True))
    return 0


def cmd_lemma_book_export(args: argparse.Namespace) -> int:
    print(json.dumps(
        LemmaBookEditor(args.config).export_snapshot(), indent=2, sort_keys=True))
    return 0


def cmd_roadmap_run(args: argparse.Namespace) -> int:
    print(json.dumps(
        RoadmapWorkshop(args.config).run(watch=args.watch), indent=2, sort_keys=True))
    return 0


def cmd_roadmap_launch(args: argparse.Namespace) -> int:
    print(json.dumps(launch_roadmap_workshop(args.config), indent=2, sort_keys=True))
    return 0


def cmd_roadmap_export(args: argparse.Namespace) -> int:
    print(json.dumps(
        RoadmapWorkshop(args.config).export_snapshot(), indent=2, sort_keys=True))
    return 0


def cmd_dashboard_run(args: argparse.Namespace) -> int:
    print(json.dumps(PagesPublisher(args.config).run(), indent=2, sort_keys=True))
    return 0


def cmd_dashboard_launch(args: argparse.Namespace) -> int:
    print(json.dumps(launch_pages_publisher(args.config), indent=2, sort_keys=True))
    return 0


def cmd_repository_publish_run(args: argparse.Namespace) -> int:
    print(json.dumps(RepositoryPublisher(args.config).run(), indent=2, sort_keys=True))
    return 0


def cmd_repository_publish_launch(args: argparse.Namespace) -> int:
    print(json.dumps(launch_repository_publisher(args.config), indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="line-point-concrete")
    subparsers = parser.add_subparsers(dest="command", required=True)
    commands = (
        ("campaign-init", cmd_campaign_init, "initialize the durable proof campaign"),
        ("campaign-run", cmd_campaign_run, "run or resume the proof campaign"),
        ("campaign-launch", cmd_campaign_launch, "launch the campaign in the background"),
        ("campaign-status", cmd_campaign_status, "show durable campaign progress"),
        ("campaign-rebalance", cmd_campaign_rebalance,
         "add the literature seat and retarget untouched researchers at the leaderboard"),
        ("campaign-reconcile-audits", cmd_campaign_reconcile_audits,
         "audit only explicit end-to-end leaderboard submissions"),
        ("lemma-book-launch", cmd_lemma_book_launch, "launch the lemma-writing agent"),
        ("lemma-book-export", cmd_lemma_book_export, "refresh the public lemma book"),
        ("roadmap-launch", cmd_roadmap_launch, "launch three shared proof-roadmap agents"),
        ("roadmap-export", cmd_roadmap_export, "refresh proof roadmaps and message board"),
        ("dashboard-run", cmd_dashboard_run, "watch and publish GitHub Pages data"),
        ("dashboard-launch", cmd_dashboard_launch, "launch the GitHub Pages publisher"),
        ("repository-publish-run", cmd_repository_publish_run,
         "watch and upload durable campaign artifacts"),
        ("repository-publish-launch", cmd_repository_publish_launch,
         "launch the durable artifact uploader"),
    )
    for name, function, help_text in commands:
        item = subparsers.add_parser(name, help=help_text)
        item.add_argument("config")
        item.set_defaults(func=function)
    item = subparsers.add_parser("lemma-book-run", help="run the lemma-writing agent")
    item.add_argument("config")
    item.add_argument("--watch", action="store_true")
    item.set_defaults(func=cmd_lemma_book_run)
    item = subparsers.add_parser("roadmap-run", help="run three shared proof-roadmap agents")
    item.add_argument("config")
    item.add_argument("--watch", action="store_true")
    item.set_defaults(func=cmd_roadmap_run)
    for name, function, help_text in (
        ("campaign-run-job", cmd_campaign_run_job, "run one queued campaign job now"),
        ("campaign-launch-job", cmd_campaign_launch_job,
         "launch one queued campaign job independently"),
    ):
        item = subparsers.add_parser(name, help=help_text)
        item.add_argument("config")
        item.add_argument("job_id")
        item.set_defaults(func=function)
    item = subparsers.add_parser(
        "community-validate", help="validate one external contribution package")
    item.add_argument("package")
    item.set_defaults(func=cmd_community_validate)
    item = subparsers.add_parser(
        "community-validate-all", help="validate every external contribution package")
    item.add_argument("root")
    item.set_defaults(func=cmd_community_validate_all)
    item = subparsers.add_parser(
        "community-ingest", help="ingest a merged contribution and queue any required audits")
    item.add_argument("config")
    item.add_argument("package")
    item.set_defaults(func=cmd_community_ingest)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))
