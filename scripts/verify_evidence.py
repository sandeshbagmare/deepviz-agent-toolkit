"""Validate declared PR evidence; never manufacture approvals or claim to verify identity."""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any


def section(body: str, title: str) -> str:
    match = re.search(rf"^## {re.escape(title)}\s*\n(.*?)(?=^## |\Z)", body, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def validate_event(event: dict[str, Any]) -> list[str]:
    pr = event.get("pull_request", {})
    if "evidence-required" not in {label["name"] for label in pr.get("labels", [])}:
        return []
    errors: list[str] = []
    body = pr.get("body") or ""
    repository = event["repository"]["full_name"]
    if not re.search(
        rf"https://github\.com/{re.escape(repository)}/issues/[1-9][0-9]*(?:\s|[)#]|$)",
        section(body, "Linked issues"),
    ):
        errors.append("Linked issues must include a full issue URL in this repository")
    if not re.search(r"!\[[^\]\n]+\]\(https://[^\s)]+\)", section(body, "Rendered output")):
        errors.append("Rendered output must embed an HTTPS image, not just name an artifact")
    explanation = section(body, "Correctness explanation")
    if len(explanation) < 40 or re.search(r"\b(TODO|TBD|placeholder)\b", explanation, re.IGNORECASE):
        errors.append("Correctness explanation must describe the observed result (at least 40 characters)")
    identities: list[str] = []
    evidence = section(body, "Independent evidence")
    for role in ("reviewer-1", "reviewer-2", "tester-1", "tester-2"):
        rows = re.findall(rf"^\|\s*{role}\s*\|([^\n]+)\|\s*$", evidence, re.MULTILINE)
        fields = [value.strip() for value in rows[0].split("|")] if len(rows) == 1 else []
        if len(fields) != 3:
            errors.append(f"{role}: supply one identity, report URL, and exact tested commit")
            continue
        identity, report, sha = fields
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:/-]{2,199}", identity) or identity.lower() in {
            "todo", "tbd", "placeholder", "agent/session-id",
        }:
            errors.append(f"{role}: supply the actual independent agent/session identifier")
        identities.append(identity.casefold())
        if not re.fullmatch(r"https://[^\s<>|]+", report):
            errors.append(f"{role}: link the actual report using HTTPS")
        if not re.fullmatch(r"[a-f0-9]{40}", sha) or sha != pr.get("head", {}).get("sha"):
            errors.append(f"{role}: report must cover the current PR head SHA")
    if len(set(identities)) != len(identities):
        errors.append("All four reviewer/tester agent/session identifiers must be distinct")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("event", nargs="?", type=Path, default=os.environ.get("GITHUB_EVENT_PATH"))
    args = parser.parse_args()
    if args.event is None:
        parser.error("supply an event JSON path or GITHUB_EVENT_PATH")
    event = json.loads(args.event.read_text(encoding="utf-8"))
    errors = validate_event(event)
    for error in errors:
        print(f"Evidence policy: {error}")
    if not errors:
        required = any(label["name"] == "evidence-required" for label in event["pull_request"]["labels"])
        print("Declared evidence is complete; human review still required" if required else
              "Bootstrap mode: evidence-required label absent; no evidence approval is asserted")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
