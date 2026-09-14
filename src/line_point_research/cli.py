from __future__ import annotations

import argparse
import json

from .campaign import ResearchCampaign, campaign_status, launch_campaign
from .lemma_book import LemmaBookEditor, launch_lemma_book
from .publisher import PagesPublisher, launch_pages_publisher
from .roadmaps import RoadmapWorkshop, launch_roadmap_workshop


def cmd_campaign_init(args: argparse.Namespace) -> int:
    campaign = ResearchCampaign(args.config)
    campaign.initialize()
    print(json.dumps(campaign.export_status(), indent=2, sort_keys=True))
    return 0


def cmd_campaign_run(args: argparse.Namespace) -> int:
    print(json.dumps(ResearchCampaign(args.config).run(), indent=2, sort_keys=True))
    return 0


def cmd_campaign_launch(args: argparse.Namespace) -> int:
    payload = {"campaign": launch_campaign(args.config)}
    campaign = ResearchCampaign(args.config)
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
        ("lemma-book-launch", cmd_lemma_book_launch, "launch the lemma-writing agent"),
        ("lemma-book-export", cmd_lemma_book_export, "refresh the public lemma book"),
        ("roadmap-launch", cmd_roadmap_launch, "launch three shared proof-roadmap agents"),
        ("roadmap-export", cmd_roadmap_export, "refresh proof roadmaps and message board"),
        ("dashboard-run", cmd_dashboard_run, "watch and publish GitHub Pages data"),
        ("dashboard-launch", cmd_dashboard_launch, "launch the GitHub Pages publisher"),
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
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))
