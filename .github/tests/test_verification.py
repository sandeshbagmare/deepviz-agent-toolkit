"""Regression checks for the CI gates themselves; no network or secrets needed."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
from typing import Any

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]


def load_script(name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def evidence_event() -> dict[str, Any]:
    sha = "a" * 40
    reports = "\n".join(
        f"| {role} | session-{index} | https://github.com/owner/repo/issues/1#issuecomment-{index} | {sha} |"
        for index, role in enumerate(("reviewer-1", "reviewer-2", "tester-1", "tester-2"), 1)
    )
    return {
        "repository": {"full_name": "owner/repo"},
        "pull_request": {
            "head": {"sha": sha},
            "labels": [{"name": "evidence-required"}],
            "body": (
                "## Linked issues\nhttps://github.com/owner/repo/issues/1\n"
                "## Rendered output\n![Rendered bar chart](https://github.com/user-attachments/assets/example)\n"
                "## Correctness explanation\n"
                "The three rendered bars have heights in the expected 1:3:2 ratio and retain their category order.\n"
                f"## Independent evidence\n{reports}\n"
            ),
        },
    }


def test_evidence_policy_allows_bootstrap_without_fabricated_reports() -> None:
    event = evidence_event()
    event["pull_request"]["labels"] = []
    event["pull_request"]["body"] = "Bootstrap CI"
    assert load_script("verify_evidence").validate_event(event) == []


def test_evidence_policy_accepts_complete_distinct_reports() -> None:
    assert load_script("verify_evidence").validate_event(evidence_event()) == []


@pytest.mark.parametrize("mutation", ["issue", "image", "explanation", "identity", "sha", "report"])
def test_evidence_policy_rejects_missing_or_stale_evidence(mutation: str) -> None:
    event = copy.deepcopy(evidence_event())
    body = event["pull_request"]["body"]
    replacements = {
        "issue": ("https://github.com/owner/repo/issues/1\n", "TBD\n"),
        "image": ("![Rendered bar chart]", "[Rendered bar chart]"),
        "explanation": (
            "The three rendered bars have heights in the expected 1:3:2 ratio and retain their category order.",
            "TODO",
        ),
        "identity": ("session-2", "session-1"),
        "sha": ("a" * 40, "b" * 40),
        "report": ("https://github.com/owner/repo/issues/1#issuecomment-2", "TODO"),
    }
    old, new = replacements[mutation]
    event["pull_request"]["body"] = body.replace(old, new)
    assert load_script("verify_evidence").validate_event(event)


def bar_image(heights: tuple[int, int, int] = (20, 60, 40)) -> np.ndarray:
    image = np.full((100, 140, 3), 255, dtype=np.uint8)
    for x, height in zip((20, 60, 100), heights, strict=True):
        image[80 - height:80, x:x + 20] = (40, 100, 220)
    return image


def test_visual_gate_compares_rendered_pixels_not_artifact_existence() -> None:
    check = load_script("verify_visual").check_bar_pixels
    result = check(bar_image(), (2.0, 6.0, 4.0))
    assert result["intersection_over_union"] > 0.99


@pytest.mark.parametrize("image", [bar_image((60, 20, 40)), np.full((100, 140, 3), 255)])
def test_visual_gate_rejects_wrong_geometry_and_blank_images(image: np.ndarray) -> None:
    with pytest.raises(AssertionError):
        load_script("verify_visual").check_bar_pixels(image, (2.0, 6.0, 4.0))


def test_scale_gate_requires_full_consumption_and_bounded_output() -> None:
    verify = load_script("verify_scale").check_result
    from deepviz.models import NormalizedData

    verify(NormalizedData([{"x": 1}], 10, strategy="sample", warnings=["sampled"]), 10, 10, 1)
    with pytest.raises(AssertionError, match="input_count"):
        verify(NormalizedData([], 9), 10, 10, 10)
    with pytest.raises(AssertionError, match="consumed"):
        verify(NormalizedData([], 10), 10, 9, 10)
    with pytest.raises(AssertionError, match="bound"):
        verify(NormalizedData([{}, {}], 10), 10, 10, 1)
    with pytest.raises(AssertionError, match="lossy"):
        verify(NormalizedData([{}], 10), 10, 10, 1)
