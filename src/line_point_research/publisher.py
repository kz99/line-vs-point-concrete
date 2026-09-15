from __future__ import annotations

import hashlib
import fcntl
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from .campaign import load_campaign_config, utc_timestamp


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PagesPublisher:
    """Publish a validated dashboard snapshot whenever its durable data changes."""

    def __init__(self, config_path: Path | str):
        self.config, self.paths = load_campaign_config(config_path)
        self.cfg = self.config["campaign"]
        self.runtime = self.paths.campaign_dir / "pages"
        self.runtime.mkdir(parents=True, exist_ok=True)
        self.snapshot = self.paths.workspace / "dashboard" / "public" / "research-data.json"
        self.publish_script = self.paths.workspace / "scripts" / "publish_pages.sh"

    def run(self) -> dict[str, Any]:
        last_path = self.runtime / "last-published-sha256"
        if not self.snapshot.exists():
            raise FileNotFoundError(self.snapshot)
        poll_seconds = max(30, int(self.cfg.get("pages_poll_seconds", 60)))
        while True:
            current = file_sha256(self.snapshot)
            previous = last_path.read_text().strip() if last_path.exists() else ""
            if current != previous:
                completed = subprocess.run(
                    [str(self.publish_script)],
                    cwd=self.paths.workspace,
                    text=True,
                    check=False,
                )
                if completed.returncode == 0:
                    last_path.write_text(current + "\n")
                    (self.runtime / "last-success.json").write_text(json.dumps({
                        "snapshot_sha256": current,
                        "published_at": utc_timestamp(),
                    }, indent=2, sort_keys=True) + "\n")
            if ((self.paths.campaign_dir / "COMPLETED").exists() and
                    last_path.exists() and
                    file_sha256(self.snapshot) == last_path.read_text().strip()):
                return {"status": "complete", "snapshot_sha256": current}
            time.sleep(poll_seconds)


class RepositoryPublisher:
    """Serialize and upload durable agent artifacts without staging runtime files."""

    def __init__(self, config_path: Path | str):
        self.config, self.paths = load_campaign_config(config_path)
        self.cfg = self.config["campaign"]
        self.runtime = self.paths.campaign_dir / "uploads"
        self.runtime.mkdir(parents=True, exist_ok=True)

    def artifact_paths(self) -> list[Path]:
        campaign = self.paths.campaign_dir
        candidates = [
            campaign / "live_notes",
            campaign / "submissions",
            campaign / "reviews",
            campaign / "leaderboards",
            campaign / "lemma_book" / "lemma-book.json",
            campaign / "lemma_book" / "submissions",
            campaign / "roadmaps" / "proof-roadmaps.json",
            campaign / "roadmaps" / "message-board.json",
            campaign / "status.json",
            campaign / "jobs.json",
            campaign / "COMPLETED",
            self.paths.workspace / "dashboard" / "public" / "research-data.json",
        ]
        return [path for path in candidates if path.exists()]

    def content_sha256(self) -> str:
        digest = hashlib.sha256()
        files: list[Path] = []
        for path in self.artifact_paths():
            files.extend([path] if path.is_file() else [item for item in path.rglob("*") if item.is_file()])
        for path in sorted(set(files)):
            digest.update(str(path.relative_to(self.paths.workspace)).encode())
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
        return digest.hexdigest()

    def publish_once(self) -> dict[str, Any]:
        lock_path = self.runtime / "git-upload.lock"
        with lock_path.open("a") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            staged = subprocess.run(
                ["git", "diff", "--cached", "--name-only"], cwd=self.paths.workspace,
                text=True, capture_output=True, check=True).stdout.strip()
            if staged:
                raise RuntimeError(
                    "refusing automatic upload while unrelated paths are already staged: " + staged)
            paths = [str(path.relative_to(self.paths.workspace)) for path in self.artifact_paths()]
            if paths:
                subprocess.run(
                    ["git", "add", "--", *paths], cwd=self.paths.workspace, check=True)
            changed = subprocess.run(
                ["git", "diff", "--cached", "--quiet"], cwd=self.paths.workspace,
                check=False).returncode != 0
            if changed:
                subprocess.run([
                    "git", "commit", "-m",
                    f"Upload {self.paths.campaign_dir.name} research artifacts",
                ], cwd=self.paths.workspace, check=True)
            remote = str(self.cfg.get("repository_publish_remote", "github"))
            branch = str(self.cfg.get("repository_publish_branch", "main"))
            subprocess.run(
                ["git", "push", remote, f"HEAD:{branch}"],
                cwd=self.paths.workspace, check=True)
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        return {"status": "published", "committed": changed, "sha256": self.content_sha256()}

    def run(self) -> dict[str, Any]:
        last_path = self.runtime / "last-uploaded-sha256"
        poll_seconds = max(15, int(self.cfg.get("repository_poll_seconds", 20)))
        while True:
            current = self.content_sha256()
            previous = last_path.read_text().strip() if last_path.exists() else ""
            if current != previous:
                try:
                    result = self.publish_once()
                    last_path.write_text(result["sha256"] + "\n")
                    (self.runtime / "last-success.json").write_text(json.dumps({
                        **result, "published_at": utc_timestamp(),
                    }, indent=2, sort_keys=True) + "\n")
                    (self.runtime / "last-error.txt").unlink(missing_ok=True)
                except Exception as exc:
                    (self.runtime / "last-error.txt").write_text(
                        f"{utc_timestamp()} {type(exc).__name__}: {exc}\n")
            if ((self.paths.campaign_dir / "COMPLETED").exists() and last_path.exists() and
                    self.content_sha256() == last_path.read_text().strip()):
                return {"status": "complete", "snapshot_sha256": current}
            time.sleep(poll_seconds)


def launch_pages_publisher(config_path: Path | str) -> dict[str, Any]:
    publisher = PagesPublisher(config_path)
    pid_path = publisher.runtime / "runner.json"
    if pid_path.exists():
        old = json.loads(pid_path.read_text())
        try:
            os.kill(int(old["pid"]), 0)
            return {"status": "already_running", **old}
        except (OSError, KeyError, ValueError):
            pass
    log_path = publisher.runtime / "publisher.log"
    log_handle = log_path.open("a")
    environment = os.environ.copy()
    source_path = str(publisher.paths.workspace / "src")
    environment["PYTHONPATH"] = (
        source_path + os.pathsep + environment["PYTHONPATH"]
        if environment.get("PYTHONPATH") else source_path)
    environment["PYTHONPYCACHEPREFIX"] = str(publisher.runtime / "python-cache")
    process = subprocess.Popen(
        [sys.executable, "-m", "line_point_research", "dashboard-run",
         str(Path(config_path).resolve())],
        cwd=publisher.paths.workspace,
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


def launch_repository_publisher(config_path: Path | str) -> dict[str, Any]:
    publisher = RepositoryPublisher(config_path)
    pid_path = publisher.runtime / "runner.json"
    if pid_path.exists():
        old = json.loads(pid_path.read_text())
        try:
            os.kill(int(old["pid"]), 0)
            return {"status": "already_running", **old}
        except (OSError, KeyError, ValueError):
            pass
    log_path = publisher.runtime / "publisher.log"
    log_handle = log_path.open("a")
    environment = os.environ.copy()
    source_path = str(publisher.paths.workspace / "src")
    environment["PYTHONPATH"] = (
        source_path + os.pathsep + environment["PYTHONPATH"]
        if environment.get("PYTHONPATH") else source_path)
    environment["PYTHONPYCACHEPREFIX"] = str(publisher.runtime / "python-cache")
    process = subprocess.Popen(
        [sys.executable, "-m", "line_point_research", "repository-publish-run",
         str(Path(config_path).resolve())],
        cwd=publisher.paths.workspace, stdout=log_handle, stderr=subprocess.STDOUT,
        text=True, start_new_session=True, env=environment)
    log_handle.close()
    payload = {
        "status": "launched", "pid": process.pid,
        "config": str(Path(config_path).resolve()), "log": str(log_path),
        "started_at": utc_timestamp(),
    }
    pid_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return payload
