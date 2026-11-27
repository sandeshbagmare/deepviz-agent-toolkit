"""Offline controls for one captured publication audit, not worker signoffs."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[3]
SNAPSHOT = ROOT / "docs/coordination/evidence/R10-21/recovery-snapshot.json"
SESSION = "ses_de5678018ffezK8JGDUaSzvcWn"
BRANCH = "agents/r10-21-recovery-git-bootstrap"
SHA = "a" * 40


def classify(branch: str, session: str, remote_sha: str | None, report: str) -> str:
    """Never infer completion or publication from an absent receipt/ref."""
    if not re.fullmatch(r"agents/r10-[0-9]{2}-[a-z0-9-]{1,80}", branch):
        raise ValueError("not an owned R10 worker branch")
    if not re.fullmatch(r"ses_[A-Za-z0-9]{8,80}", session):
        raise ValueError("invalid actual-session identity")
    if remote_sha is None:
        return "pending-unverified"
    if not re.fullmatch(r"[0-9a-f]{40}", remote_sha):
        raise ValueError("invalid observed remote SHA")
    if branch in report and session in report and remote_sha in report:
        return "receipt-ref-linked-not-product-signoff"
    return "remote-present-receipt-unverified"


@pytest.mark.parametrize(
    ("remote", "report", "expected"),
    [
        (None, "finished", "pending-unverified"),
        (None, BRANCH + SESSION + SHA, "pending-unverified"),
        (SHA, "push planned", "remote-present-receipt-unverified"),
        (SHA, BRANCH + SESSION + "b" * 40, "remote-present-receipt-unverified"),
        (SHA, BRANCH + SHA, "remote-present-receipt-unverified"),
        (SHA, SESSION + SHA, "remote-present-receipt-unverified"),
        (SHA, BRANCH + SESSION + SHA, "receipt-ref-linked-not-product-signoff"),
    ],
)
def test_receipt_positive_and_negative_controls(
    remote: str | None, report: str, expected: str
 ) -> None:
    assert classify(BRANCH, SESSION, remote, report) == expected


@pytest.mark.parametrize(
    ("branch", "session", "remote"),
    [
        ("release/candidate", SESSION, SHA),
        ("agents/r10-21-../../main", SESSION, SHA),
        (BRANCH, "guessed", SHA),
        (BRANCH, SESSION, "not-a-commit"),
    ],
)
def test_invalid_authority_or_receipt_is_rejected(
    branch: str, session: str, remote: str
 ) -> None:
    with pytest.raises(ValueError):
        classify(branch, session, remote, "finished")


@pytest.fixture(scope="module")
def packet() -> dict[str, Any]:
    assert SNAPSHOT.stat().st_size <= 131072
    return json.loads(SNAPSHOT.read_text(encoding="utf-8"))


def test_snapshot_source_and_one_query_boundary(packet: dict[str, Any]) -> None:
    assert packet["source_pin"] == "3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab"
    assert packet["no_runtime_query"] is True
    assert packet["no_progress_polling"] is True
    assert len(packet["commands"]) == 1
    assert packet["remote_refs"]["exit"] == 0


def test_pending_startup_receipts_are_not_finished(packet: dict[str, Any]) -> None:
    rows = packet["roles"]
    assert len(rows) == len({row["session"] for row in rows}) == 21
    for row in rows:
        assert row["remote_sha"] is None
        assert row["authored_receipt_matches_observed_ref"] is False
        assert classify(row["branch"], row["session"], None, "") == row[
            "publication_state"
        ] == "pending-unverified"


def test_published_candidate_bootstrap_has_real_git_blob_bytes(
    packet: dict[str, Any],
 ) -> None:
    observed = packet["remote_bootstrap"]["release/candidate"]
    assert observed["commit"] == "5340bc69b7203ad7a9166543062482d819f9b705"
    assert len(observed["entries"]) == 4
    for entry in observed["entries"].values():
        assert entry["http"] == 200
        assert entry["content_matches_git_blob"] is True
        assert len(entry["sha256"]) == 64
    assert observed["entries"]["RESUME.md"]["mentions_MAIN_bootstrap"] is True


def test_real_recovery_gaps_remain_visible(packet: dict[str, Any]) -> None:
    assert packet["assertions"] == {"pass": 8, "fail": 3}
    failed = {c["name"] for c in packet["checks"] if c["status"] == "fail"}
    assert failed == {
        "legacy_entry_redirect_current:docs/coordination/STATE.md",
        "legacy_entry_redirect_current:docs/coordination/ROSTER.md",
        "old_isolated_pin_has_current_bootstrap",
    }
