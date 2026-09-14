from __future__ import annotations

import hashlib
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
        if not last_path.exists():
            last_path.write_text(file_sha256(self.snapshot) + "\n")
        poll_seconds = max(30, int(self.cfg.get("pages_poll_seconds", 60)))
        while True:
            current = file_sha256(self.snapshot)
            previous = last_path.read_text().strip()
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
                    file_sha256(self.snapshot) == last_path.read_text().strip()):
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
