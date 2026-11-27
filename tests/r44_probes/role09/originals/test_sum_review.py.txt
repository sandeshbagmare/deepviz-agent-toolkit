"""Independent SUM review oracles: strict failures are deliberately not xfailed."""
from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
from collections import Counter
from dataclasses import asdict
from fractions import Fraction
from pathlib import Path

import pytest

from deepviz import normalize

MODULE = importlib.import_module("deepviz.normalize")
SPEC = {"kind": "bar", "x": "g", "y": "v", "aggregation": "sum"}
CASES = json.loads(Path(__file__).with_name("exact-cases.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["name"])
def test_sum_equals_independent_exact_oracle(case: dict) -> None:
    expected = float(sum(map(Fraction, case["values"]), Fraction()))
    assert expected == case["expected"]
    result = normalize(({"g": "a", "v": value} for value in case["values"]), SPEC)
    assert result.records == [{"g": "a", "v": expected}]
    assert result.input_count == len(case["values"])
    assert result.warnings == []


@pytest.mark.parametrize("bits", (96, 512, 4096))
def test_pure_integer_policy_remains_exact(bits: int) -> None:
    large = 1 << bits
    result = normalize([{"g": "a", "v": v} for v in [large, 17, -large]], SPEC)
    assert result.records == [{"g": "a", "v": 17}]
    assert type(result.records[0]["v"]) is int


def test_promoted_state_has_one_integer_not_a_partial_list() -> None:
    reducer = MODULE._Reducer("sum", ["g"], "v", 10, Counter())
    reducer.add({"g": "a", "v": 1e308})
    reducer.add({"g": "a", "v": 1e308})
    for _ in range(8192):
        reducer.add({"g": "a", "v": 1e308})
    state = next(iter(reducer.groups.values()))
    assert len(reducer.groups) == 1 and reducer.other is None
    assert len(state) == 5 and all(not isinstance(value, (list, dict, set)) for value in state)
    assert state[3] == -1074 and isinstance(state[1], int)
    assert state[1].bit_length() <= 2098 + state[0].bit_length()
    assert state[4] >= sum(len(repr(value)) for value in (state[0], state[1], state[2], state[3]))
    assert reducer.retained_bytes < 2048


def unaffected() -> dict:
    source = [{"g": "a", "v": v} for v in [1e308, 1e308, -1e308]]
    result = {"mean": asdict(normalize(source, SPEC | {"aggregation": "mean"}))}
    rows = ({"g": f"group{i % 7}", "v": i} for i in range(1001))
    result["sample"] = asdict(normalize(rows, SPEC | {"aggregation": "sample", "max_points": 17}))
    return result


def test_mean_and_sample_match_untouched_base() -> None:
    base = os.environ["R13_BASE_PYTHONPATH"]
    child = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--unaffected"],
        capture_output=True, text=True, timeout=60, check=True,
        env={**os.environ, "PYTHONPATH": base, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert json.loads(child.stdout) == unaffected()


if __name__ == "__main__":
    assert sys.argv[1:] == ["--unaffected"]
    print(json.dumps(unaffected(), allow_nan=False))
@pytest.mark.parametrize("sign", (-1, 1))
def test_truly_unrepresentable_sum_remains_warned_null(sign: int) -> None:
    result = normalize([{"g": "a", "v": sign * 1e308}] * 2, SPEC)
    assert result.records == [{"g": "a", "v": None}]
    assert any("finite" in warning for warning in result.warnings)
    json.dumps(asdict(result), allow_nan=False)


def test_promoted_integer_is_charged_against_existing_budget(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(MODULE, "_MAX_RETAINED_BYTES", 512)
    assert normalize([{"g": "a", "v": 1}, {"g": "a", "v": 2}], SPEC).records == [{"g": "a", "v": 3}]
    with pytest.raises(ValueError, match="retained"):
        normalize([{"g": "a", "v": 1e308}] * 2, SPEC)
