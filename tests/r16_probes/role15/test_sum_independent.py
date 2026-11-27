"""NEW bounded non-author SUM value tests against exact committed ec9f669 source."""
from __future__ import annotations

import importlib
import json
import math
import os
import subprocess
from collections.abc import Iterator
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pytest
from sum_oracle_cases import Row, bits, cases, expected, rows

from deepviz import normalize

PIN = "ec9f669eff28cd5351da142765b7755e3b2f484f"
CASES = cases()


def _spec(case) -> dict[str, Any]:
    return {"kind": "table", "x": "g", "y": "v", "aggregation": "sum", "max_points": case.max_points}


@pytest.fixture(scope="module")
def node_outputs(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    root = Path(os.environ["R16_SOURCE_ROOT"]).resolve()
    assert subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip() == PIN
    assert not subprocess.check_output(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=no"], text=True).strip()
    module = importlib.import_module("deepviz.normalize")
    assert module.__file__ is not None
    assert Path(module.__file__).resolve() == root / "python/deepviz/src/deepviz/normalize.py"
    for name in ("python/deepviz/src/deepviz/normalize.py", "packages/deepviz/src/normalize.ts",
                 "python/deepviz/tests/test_r07_finite_overflow.py", "packages/deepviz/test/test_r07_finite_overflow.test.mjs"):
        assert (root / name).read_bytes() == subprocess.check_output(["git", "-C", str(root), "show", PIN + ":" + name])
    payload = [{"name": case.name, "rows": rows(case), "spec": _spec(case)} for case in CASES]
    bridge = subprocess.run(
        ["node", str(Path(__file__).with_name("sum_bridge.mjs"))],
        input=json.dumps(payload, allow_nan=False), text=True, capture_output=True,
        check=False, timeout=60, cwd=root,
    )
    assert bridge.returncode == 0, bridge.stderr
    packet = json.loads(bridge.stdout)
    result_file = tmp_path_factory.mktemp("r16-new-node") / "node-results.json"
    result_file.write_text(bridge.stdout, encoding="utf-8")
    return {entry["name"]: entry for entry in packet["results"]}


class OnePass:
    def __init__(self, data: list[Row]):
        self.data = data
        self.consumed = 0
        self.iterations = 0
        self.exhausted = False

    def __iter__(self) -> Iterator[Row]:
        self.iterations += 1
        assert self.iterations == 1, "Python source must be one-pass"
        for row in self.data:
            self.consumed += 1
            yield row
        self.exhausted = True


def _check(output: dict[str, Any], case, expected_records, expected_bits, is_overflow: bool) -> None:
    assert output["records"] == expected_records
    assert [bits(row["v"]) for row in output["records"]] == expected_bits
    assert output["input_count"] == len(case.rows) and output["strategy"] == "sum"
    assert all(row["v"] is None or math.isfinite(row["v"]) for row in output["records"])
    warnings = output["warnings"]
    assert isinstance(warnings, list)
    assert any("non-finite" in warning.lower() for warning in warnings) is is_overflow
    assert any("other bucket" in warning.lower() for warning in warnings) is case.expects_other_warning
    if not is_overflow and not case.expects_other_warning:
        assert warnings == []
    else:
        assert all("non-finite" in warning.lower() or "other bucket" in warning.lower() for warning in warnings)
    assert len(warnings) == int(is_overflow) + int(case.expects_other_warning), "Every loss warning is unique and disclosed"
    assert json.loads(json.dumps(output, allow_nan=False)) == output


@pytest.mark.parametrize("case", CASES, ids=[case.name for case in CASES])
def test_literal_binary64_sum_records_and_one_pass_streams(case, node_outputs, record_property) -> None:
    data = rows(case)
    oracle_records, oracle_bits, is_overflow = expected(case)
    one_pass = OnePass(data)
    python_outputs = [asdict(normalize(data, _spec(case))), asdict(normalize(one_pass, _spec(case)))]
    assert one_pass.consumed == len(data) and one_pass.iterations == 1 and one_pass.exhausted
    for output in python_outputs:
        _check(output, case, oracle_records, oracle_bits, is_overflow)
    assert python_outputs[0] == python_outputs[1], "Python records/stream metadata including exact warnings must agree"
    packet = node_outputs[case.name]
    assert packet["input_bits"] == [bits(row["v"]) for row in data], "JSON transport must preserve actual input binary64 bits"
    assert packet["syncConsumed"] == packet["asyncConsumed"] == len(data)
    assert packet["syncIterations"] == packet["asyncIterations"] == 1
    assert packet["syncExhausted"] and packet["asyncExhausted"]
    for output in packet["outputs"]:
        _check(output["result"], case, oracle_records, oracle_bits, is_overflow)
        assert output["bits"] == oracle_bits
        assert output["result"] == packet["outputs"][0]["result"], "TS records/sync/async metadata and exact warnings must agree"
    record_property("source_commit", PIN)
    record_property("input_count", len(data))
    record_property("oracle_binary64_bits", json.dumps(oracle_bits))
    record_property("overflow_warned_null", str(is_overflow))
    record_property("other_bucket_disclosed", str(case.expects_other_warning))
    record_property("verified_public_modes", "Python records+onepass, TS records+syncstream+asyncstream")
