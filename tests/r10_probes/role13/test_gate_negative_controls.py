"""Independent real-CLI controls; synthetic packets are never reviewer signoffs."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[3]
SOURCE_SHA = "3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab"


def run_cli(tmp_path: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PYTHONPATH": str(ROOT / "python/deepviz/src"),
           "PYTHONDONTWRITEBYTECODE": "1", "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
    env.pop("PYTEST_ADDOPTS", None)
    env.pop("PYTEST_PLUGINS", None)
    argv = [sys.executable, *arguments]
    result = subprocess.run(
        argv, cwd=tmp_path, env=env, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=30, check=False,
    )
    if trace := os.environ.get("R10_13_COMMAND_TRACE"):
        entry = {"argv": argv, "cwd": str(tmp_path), "exit": result.returncode,
                 "stdout": result.stdout, "stderr": result.stderr}
        with Path(trace).open("ab") as stream:
            stream.write((json.dumps(entry, ensure_ascii=True) + "\n").encode("utf-8"))
    return result


def fixture_event(*, required: bool = True) -> dict[str, Any]:
    roles = ("reviewer-1", "reviewer-2", "tester-1", "tester-2")
    rows = "\n".join(
        f"| {role} | fixture-{role} | https://reports.invalid/{role} | {SOURCE_SHA} |"
        for role in roles
    )
    return {
        "repository": {"full_name": "sandeshbagmare/deepviz-agent-toolkit"},
        "pull_request": {
            "head": {"sha": SOURCE_SHA},
            "labels": [{"name": "evidence-required"}] if required else [],
            "body": (
                "## Linked issues\nhttps://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/20\n"
                "## Rendered output\n![Synthetic fixture](https://images.invalid/fixture.png)\n"
                "## Correctness explanation\n"
                "Synthetic data tests only the declaration format; no real chart, reviewer or approval is claimed.\n"
                f"## Independent evidence\n{rows}\n"
            ),
        },
    }


def check_event(tmp_path: Path, event: dict[str, Any]) -> subprocess.CompletedProcess[str]:
    path = tmp_path / "synthetic-event.json"
    path.write_text(json.dumps(event), encoding="utf-8", newline="\n")
    original = path.read_bytes()
    result = run_cli(tmp_path, "-I", str(ROOT / "scripts/verify_evidence.py"), str(path))
    assert path.read_bytes() == original, "The declaration gate must not rewrite its input"
    assert not result.stderr, result.stderr
    return result


def test_schema_gate_rejects_valid_json_nested_drift_without_rewriting(tmp_path: Path) -> None:
    """Catches a drift gate that returns success or silently regenerates stale output."""
    path = tmp_path / "scratch-schema.json"
    cli = (str(ROOT / "scripts/export_schema.py"), "--output", str(path))
    assert run_cli(tmp_path, *cli).returncode == 0
    original = path.read_bytes()
    positive = run_cli(tmp_path, *cli, "--check")
    assert positive.returncode == 0, positive.stdout + positive.stderr
    assert path.read_bytes() == original
    stale = json.loads(original)
    stale["$defs"]["ChartSpec"]["properties"]["max_points"]["maximum"] = 100_001
    path.write_text(json.dumps(stale, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    stale_bytes = path.read_bytes()
    negative = run_cli(tmp_path, *cli, "--check")
    assert negative.returncode == 1, negative.stdout + negative.stderr
    assert "missing or stale" in negative.stdout.lower()
    assert not negative.stderr
    assert path.read_bytes() == stale_bytes != original


@pytest.mark.parametrize("image", [
    "http://images.invalid/fixture.png", "file:///fixture.png",
    "javascript:void(0)", "data:image/svg+xml,fixture",
])
def test_required_gate_rejects_non_https_image_packets(tmp_path: Path, image: str) -> None:
    """Catches unsafe image schemes being accepted as required evidence."""
    event = fixture_event()
    event["pull_request"]["body"] = event["pull_request"]["body"].replace(
        "https://images.invalid/fixture.png", image,
    )
    result = check_event(tmp_path, event)
    assert result.returncode == 1, result.stdout
    assert "Rendered output" in result.stdout
    assert "Bootstrap" not in result.stdout and "validated" not in result.stdout


@pytest.mark.parametrize("report", [
    "http://reports.invalid/reviewer-1", "file:///reviewer-1",
    "javascript:void(0)", "data:text/html,fixture", "https://reports.invalid/<script>",
])
def test_required_gate_rejects_unsafe_report_links(tmp_path: Path, report: str) -> None:
    """Catches required report links accepting non-HTTPS or markup-bearing values."""
    event = fixture_event()
    event["pull_request"]["body"] = event["pull_request"]["body"].replace(
        "https://reports.invalid/reviewer-1", report,
    )
    result = check_event(tmp_path, event)
    assert result.returncode == 1, result.stdout
    assert "reviewer-1: link the actual report using HTTPS" in result.stdout
    assert "Bootstrap" not in result.stdout and "validated" not in result.stdout


def test_incomplete_required_packet_cannot_take_the_bootstrap_success_path(tmp_path: Path) -> None:
    event = fixture_event()
    event["pull_request"]["body"] = "## Linked issues\nNo actual evidence is supplied.\n"
    result = check_event(tmp_path, event)
    assert result.returncode == 1, result.stdout
    assert "Evidence policy:" in result.stdout and "Bootstrap" not in result.stdout


def test_label_text_in_body_is_not_an_actual_required_label_or_an_approval(tmp_path: Path) -> None:
    event = fixture_event(required=False)
    event["pull_request"]["body"] = "evidence-required; intentionally no evidence packet"
    result = check_event(tmp_path, event)
    assert result.returncode == 0, result.stdout
    assert "Bootstrap mode:" in result.stdout
    assert "no evidence approval is asserted" in result.stdout
    assert "structure validated" not in result.stdout


def test_complete_synthetic_packet_only_validates_structure_not_real_approval(tmp_path: Path) -> None:
    result = check_event(tmp_path, fixture_event())
    assert result.returncode == 0, result.stdout
    assert "structure validated" in result.stdout
    assert "report truth and independence are not verified" in result.stdout
    assert "no approval is asserted" in result.stdout and "Bootstrap" not in result.stdout


def test_rejected_untrusted_body_stays_inert_in_the_real_cli(tmp_path: Path) -> None:
    event = fixture_event()
    event["pull_request"]["body"] += "\n$(echo R10 > gate-marker.txt)\n`echo R10 > gate-marker.txt`\n"
    event["pull_request"]["body"] = event["pull_request"]["body"].replace(
        "https://images.invalid/fixture.png", "javascript:void(0)",
    )
    result = check_event(tmp_path, event)
    assert result.returncode == 1, result.stdout
    assert "Rendered output" in result.stdout
    assert not (tmp_path / "gate-marker.txt").exists(), "Untrusted event text must not execute"


def test_real_pytest_failure_reaches_exit_status_and_junit(tmp_path: Path) -> None:
    """Catches recipes swallowing a genuine failing-test exit or collection/setup errors."""
    positive = tmp_path / "positive_case.py"
    positive.write_text("def test_control():\n    assert 2 + 2 == 4\n", encoding="utf-8", newline="\n")
    failing = tmp_path / "deliberate_negative_case.py"
    failing.write_text(
        "def test_deliberate_negative():\n    assert False, 'R10 deliberate gate rejection'\n",
        encoding="utf-8", newline="\n",
    )
    args = ("-m", "pytest", "-q", "--strict-markers", "--confcutdir", str(tmp_path))
    good_xml = tmp_path / "positive.xml"
    good = run_cli(tmp_path, *args, str(positive), "--junitxml", str(good_xml))
    assert good.returncode == 0, good.stdout + good.stderr
    assert "1 passed" in good.stdout
    bad_xml = tmp_path / "negative.xml"
    bad = run_cli(tmp_path, *args, str(positive), str(failing), "--junitxml", str(bad_xml))
    assert bad.returncode == 1, bad.stdout + bad.stderr
    assert "1 failed, 1 passed" in bad.stdout
    assert "R10 deliberate gate rejection" in bad.stdout
    cases = list(ET.parse(bad_xml).iter("testcase"))
    assert len(cases) == 2
    assert sum(case.find("failure") is not None for case in cases) == 1
    assert not list(ET.parse(bad_xml).iter("error")), "A setup error is not the intended RED control"
