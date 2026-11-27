"""Read-only official-origin identity check; credentials stay captured in memory."""
from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit

import httpx


def main() -> None:
    origin = urlsplit(subprocess.check_output(["git", "remote", "get-url", "origin"], text=True).strip())
    if (origin.scheme, origin.netloc, origin.path) != (
        "https", "github.com", "/sandeshbagmare/deepviz-agent-toolkit.git",
    ):
        raise SystemExit("STOP: unexpected repository origin")
    result = subprocess.run(
        ["git", "-c", "credential.interactive=false", "credential", "fill"],
        input="protocol=https\nhost=github.com\n\n", capture_output=True, text=True,
        timeout=20, check=False,
    )
    if result.returncode:
        raise SystemExit("STOP: captured credential lookup failed")
    credential = dict(line.split("=", 1) for line in result.stdout.splitlines() if "=" in line)
    token = credential.get("password")
    if not token:
        raise SystemExit("STOP: no stored credential")
    with httpx.Client(headers={"Authorization": f"Bearer {token}",
                               "Accept": "application/vnd.github+json", "User-Agent": "DeepViz-R27-18"},
                      timeout=30, follow_redirects=False) as client:
        user = client.get("https://api.github.com/user")
        if user.status_code != 200 or user.json().get("login") != "sandeshbagmare":
            raise SystemExit(f"STOP: expected authenticated identity not verified; HTTP{user.status_code}")
        repo = client.get("https://api.github.com/repos/sandeshbagmare/deepviz-agent-toolkit")
        if repo.status_code != 200 or repo.json().get("full_name") != "sandeshbagmare/deepviz-agent-toolkit":
            raise SystemExit(f"STOP: expected repository not verified; HTTP{repo.status_code}")
    receipt = {"utc": datetime.now(UTC).isoformat(), "user_get": 200, "login": "sandeshbagmare",
               "repository_get": 200, "full_name": "sandeshbagmare/deepviz-agent-toolkit",
               "api_mutations": 0, "redirects_followed": 0,
               "branch": subprocess.check_output(["git", "branch", "--show-current"], text=True).strip(),
               "head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()}
    Path(__file__).with_name("publication-preflight.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8",
    )
    print(json.dumps(receipt))


if __name__ == "__main__":
    try:
        main()
    except (httpx.HTTPError, subprocess.SubprocessError, ValueError):
        raise SystemExit("STOP: read-only identity preflight failed; no API mutation") from None
