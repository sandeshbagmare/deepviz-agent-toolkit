"""Portable OFFLINE recovery evidence controls, never product acceptance."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[3]
PACKET = ROOT / "docs/coordination/evidence/R13-21/pre-recovery-snapshot.json"
SOURCE = "5340bc69b7203ad7a9166543062482d819f9b705"


def acceptance_evidenced(
    metadata_outcome: str, accepted_source: str | None, actual_source: str, gates: bool
 ) -> bool:
    """Task evidence cannot be manufactured from a transport outcome."""
    del metadata_outcome
    return bool(accepted_source == actual_source and gates)


def may_reassign_scope(
    active: bool, owner_canceled: bool, explicit_transfer: bool, eligible: bool
 ) -> bool:
    """Inactive/canceled runtime state is not a source transfer."""
    del active, owner_canceled
    return explicit_transfer and eligible


def may_edit_production(
    higher_priority_forbidden: bool, user_release: bool, exact_path_released: bool
 ) -> bool:
    return not higher_priority_forbidden and user_release and exact_path_released


def first_action(
    metadata_outcome: str, saved_exit: int | None, hash_matches: bool, inflight: bool
 ) -> str:
    del metadata_outcome
    if inflight:
        return "reconcile-once-do-not-duplicate"
    if saved_exit == 0 and hash_matches:
        return "retain-saved-result-resume-next-unfinished"
    return "preserve-dirty-work-review-owned-checkpoint"


@pytest.mark.parametrize("outcome", ["succeeded", "failed", "unknown", "inactive"])
@pytest.mark.parametrize(
    ("accepted", "gates", "expected"),
    [(None, False, False), (SOURCE, False, False), ("old-source", True, False), (SOURCE, True, True)],
)
def test_transport_outcome_is_never_task_acceptance(
    outcome: str, accepted: str | None, gates: bool, expected: bool
 ) -> None:
    assert acceptance_evidenced(outcome, accepted, SOURCE, gates) is expected


@pytest.mark.parametrize("active", [True, False])
@pytest.mark.parametrize("canceled", [True, False])
@pytest.mark.parametrize(
    ("transfer", "eligible", "expected"),
    [(False, False, False), (False, True, False), (True, False, False), (True, True, True)],
)
def test_inactive_or_canceled_does_not_free_owned_scope(
    active: bool, canceled: bool, transfer: bool, eligible: bool, expected: bool
 ) -> None:
    assert may_reassign_scope(active, canceled, transfer, eligible) is expected


@pytest.mark.parametrize("tester_ban", [True, False])
@pytest.mark.parametrize("user_release", [True, False])
@pytest.mark.parametrize("exact_path", [True, False])
def test_user_release_cannot_override_higher_priority_tester_ban(
    tester_ban: bool, user_release: bool, exact_path: bool
 ) -> None:
    expected = not tester_ban and user_release and exact_path
    assert may_edit_production(tester_ban, user_release, exact_path) is expected


@pytest.mark.parametrize("outcome", ["succeeded", "failed", "inactive", "unknown"])
@pytest.mark.parametrize(
    ("exit_code", "matches", "inflight", "expected"),
    [
        (0, True, False, "retain-saved-result-resume-next-unfinished"),
        (0, False, False, "preserve-dirty-work-review-owned-checkpoint"),
        (1, True, False, "preserve-dirty-work-review-owned-checkpoint"),
        (None, False, False, "preserve-dirty-work-review-owned-checkpoint"),
        (None, True, True, "reconcile-once-do-not-duplicate"),
    ],
)
def test_runtime_failure_neither_loses_work_nor_repeats_completed_command(
    outcome: str, exit_code: int | None, matches: bool, inflight: bool, expected: str
 ) -> None:
    assert first_action(outcome, exit_code, matches, inflight) == expected


def test_failed_runtime_leaves_saved_dirty_bytes_intact(tmp_path: Path) -> None:
    owned = tmp_path / "owned-uncommitted-report.txt"
    owned.write_bytes(b"genuine RED evidence and unfinished next action")
    before = hashlib.sha256(owned.read_bytes()).hexdigest()
    assert first_action("failed", None, False, False).startswith("preserve-dirty")
    assert owned.exists() and hashlib.sha256(owned.read_bytes()).hexdigest() == before


def test_cancellation_is_explicit_not_inferred_from_inactive() -> None:
    inactive_metadata = {"state": "inactive", "outcome": "succeeded"}
    assert inactive_metadata.get("canceled", False) is False
    canceled_history = {"state": "inactive", "canceled": True}
    assert canceled_history["canceled"] is True
    assert not may_reassign_scope(False, True, False, True)


@pytest.fixture(scope="module")
def snapshot() -> dict[str, Any]:
    assert PACKET.stat().st_size < 131072
    return json.loads(PACKET.read_text(encoding="utf-8"))


def test_actual_own_receipt_recovery_and_no_live_queries(snapshot: dict[str, Any]) -> None:
    assert snapshot["one_bounded_saved_snapshot"] is True
    assert snapshot["fresh_runtime_or_sibling_query_count"] == 0
    assert snapshot["commands"][1]["value"] == "088586f6af28c8db3048fddd34d1c710f5685e6a"
    assert snapshot["commands"][4]["value"] == SOURCE
    assert all(c["exit"] == 0 for c in snapshot["commands"])


def test_literal_collector_miss_remains_visible_not_rewritten(snapshot: dict[str, Any]) -> None:
    assert snapshot["totals"] == {"pass": 9, "fail": 1}
    failed = [c for c in snapshot["assertions"] if c["status"] == "fail"]
    assert [c["name"] for c in failed] == ["canonical_links_latest_recovery_packet"]
