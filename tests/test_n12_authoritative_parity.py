"""Independent current-candidate contract and semantic regression oracles.

Python ChartSpec is authoritative; do not copy historical coercion expectations.
Run `npm ci && npm run build` in this worktree before integration tests. Node
imports this worktree's public package, never a sibling or pre-existing dist.
No xfails hide failures: baseline b6abc8d has known red regressions, recorded in
the N12 report. Numeric JSON 1 and 1.0 are value-equivalent, but True and 1 are not.
"""
from __future__ import annotations

import importlib
import json
import math
import shutil
import subprocess
from dataclasses import asdict
from pathlib import Path
from typing import Any

import jsonschema
import pytest
from pydantic import ValidationError

from deepviz.models import ChartSpec
from deepviz.normalize import normalize

ROOT = Path(__file__).resolve().parents[1]
NORMALIZATION = json.loads(
    (Path(__file__).parent / "fixtures" / "n12-normalization-parity.json").read_text(encoding="utf-8")
)
NUMERIC_BOUNDS = {"max_points": (10, 100000), "width": (240, 4096), "height": (200, 4096), "columns": (1, 6)}
CONTRACT: list[dict[str, Any]] = [
    {"id": "defaults", "input": {}, "accepted": True},
    {"id": "nullable-mapping", "input": {"x": None, "y": None, "color": None, "size": None, "data_path": None}, "accepted": True},
    {"id": "version-integral-number", "input": {"version": 1.0}, "accepted": True},
    {"id": "version-boolean-rejected", "input": {"version": True}, "accepted": False},
    {"id": "version-string-rejected", "input": {"version": "1"}, "accepted": False},
    {"id": "extra-expression-rejected", "input": {"expression": "datum.value * 2"}, "accepted": False},
    {"id": "extra-proto-key-rejected", "input": {"__proto__": {}}, "accepted": False},
    {"id": "null-charts-rejected", "input": {"charts": None}, "accepted": False},
    {"id": "empty-dashboard", "input": {"kind": "dashboard"}, "accepted": False},
    {"id": "non-dashboard-child", "input": {"charts": [{}]}, "accepted": False},
    {"id": "nested-dashboard", "input": {"kind": "dashboard", "charts": [{"kind": "dashboard", "charts": [{}]}]}, "accepted": False},
    {"id": "dashboard-24", "input": {"kind": "dashboard", "charts": [{} for _ in range(24)]}, "accepted": True},
    {"id": "dashboard-25", "input": {"kind": "dashboard", "charts": [{} for _ in range(25)]}, "accepted": False},
    {"id": "dashboard-child-defaults", "input": {"kind": "dashboard", "charts": [{"kind": "line"}]}, "accepted": True},
    {"id": "dashboard-child-extra", "input": {"kind": "dashboard", "charts": [{"script": "arbitrary"}]}, "accepted": False},
    {"id": "dashboard-child-numeric-string", "input": {"kind": "dashboard", "charts": [{"width": "240"}]}, "accepted": False},
]
for field, (low, high) in NUMERIC_BOUNDS.items():
    for label, value, accepted in [
        ("minimum", low, True), ("maximum", high, True),
        ("integral-float", float(low), True), ("below", low - 1, False),
        ("above", high + 1, False), ("fraction", low + 0.5, False),
        ("string", str(low), False), ("boolean", True, False), ("null", None, False),
    ]:
        CONTRACT.append({"id": f"{field}-{label}", "input": {field: value}, "accepted": accepted})
for field, maximum in [("title", 500), ("description", 2000)]:
    for length, accepted in [(maximum, True), (maximum + 1, False)]:
        CONTRACT.append({"id": f"{field}-unicode-{length}", "input": {field: "\U0001f600" * length}, "accepted": accepted})

# Large cases are generated, not bloated fixture files. Other-bucket mean is
# (9 + 10 + 100 + 100 + 100) / 5 = 63.8, not an unweighted group-mean average.
NORMALIZATION.append({
    "id": "overflow-weighted-mean-and-retained-group-update",
    "data": [{"g": f"g{i}", "v": i} for i in range(11)]
    + [{"g": "g10", "v": 100} for _ in range(3)] + [{"g": "g0", "v": 90}],
    "spec": {"x": "g", "y": "v", "aggregation": "mean", "max_points": 10},
    "expected": {
        "records": [{"g": "g0", "v": 45}] + [{"g": f"g{i}", "v": i} for i in range(1, 9)]
        + [{"g": "__deepviz_other__", "v": 63.8}],
        "input_count": 15, "strategy": "mean",
    },
    "warning_categories": ["overflow"],
})
NORMALIZATION.append({
    "id": "overflow-label-avoids-source-category-collision",
    "data": [{"g": "__deepviz_other__", "v": 1}] + [{"g": f"g{i}", "v": i} for i in range(11)],
    "spec": {"x": "g", "y": "v", "aggregation": "sum", "max_points": 10},
    "expected": {
        "records": [{"g": "__deepviz_other__", "v": 1}] + [{"g": f"g{i}", "v": i} for i in range(8)]
        + [{"g": "__deepviz_other___", "v": 27}],
        "input_count": 12, "strategy": "sum",
    },
    "warning_categories": ["overflow"],
})

NODE_RUNNER = r"""
import {readFileSync} from 'node:fs';
import {normalize, normalizeStream, validateSpec, chartSpecSchema} from '@deepviz/agent-toolkit';
const input=JSON.parse(readFileSync(0,'utf8'));
const contracts=input.contracts.map(({id,input})=>{
  try {return {id,accepted:true,dump:validateSpec(input)}}
  catch (error) {return {id,accepted:false,error:String(error)}}
});
const normalization=input.normalization.map(({id,data,spec})=>{
  try {return {id,accepted:true,result:normalize(data,spec)}}
  catch (error) {return {id,accepted:false,error:String(error)}}
});
const rows=Array.from({length:1000},(_,id)=>({id,value:id%7}));
const sampleSpec={kind:'table',aggregation:'none',max_points:10};
const sample=normalize(rows,sampleSpec), repeated=normalize(rows,sampleSpec);
async function* source(){for(const row of rows)yield row}
const stream=await normalizeStream(source(),sampleSpec);
const directNonfinite=normalize([{id:1,value:NaN},{id:2,value:Infinity},{id:3,value:-Infinity}],{kind:'table',aggregation:'none'});
process.stdout.write(JSON.stringify({contracts,normalization,schema:chartSpecSchema,sample,repeated,stream,directNonfinite}));
"""


def _assert_json_values(actual: Any, expected: Any) -> None:
    """Compare semantic JSON values, without bool/int equality or float noise."""
    if expected is None or isinstance(expected, (str, bool)):
        assert type(actual) is type(expected)
        assert actual == expected
    elif isinstance(expected, (int, float)):
        assert type(actual) in (int, float)
        assert math.isfinite(actual)
        assert actual == pytest.approx(expected, rel=1e-12, abs=1e-12)
    elif isinstance(expected, list):
        assert isinstance(actual, list)
        assert len(actual) == len(expected)
        for got, want in zip(actual, expected, strict=True):
            _assert_json_values(got, want)
    else:
        assert isinstance(expected, dict)
        assert isinstance(actual, dict)
        assert actual.keys() == expected.keys()
        for key in expected:
            _assert_json_values(actual[key], expected[key])


def _python_contract(value: Any) -> dict[str, Any]:
    try:
        return {"accepted": True, "dump": ChartSpec.model_validate(value).model_dump(mode="json")}
    except ValidationError:
        return {"accepted": False}


def _python_normalization(case: dict[str, Any]) -> dict[str, Any]:
    try:
        return {"accepted": True, "result": asdict(normalize(case["data"], case["spec"]))}
    except (ValueError, TypeError, OverflowError) as error:
        return {"accepted": False, "error": str(error)}


@pytest.fixture(scope="module")
def public_npm() -> dict[str, Any]:
    node = shutil.which("node")
    assert node, "Node and npm run build in this worktree are required; this gate never silently skips."
    assert (ROOT / "packages" / "deepviz" / "dist" / "index.js").is_file(), "Run npm run build here."
    completed = subprocess.run(
        [node, "--input-type=module", "--eval", NODE_RUNNER],
        input=json.dumps({"contracts": CONTRACT, "normalization": NORMALIZATION}, allow_nan=False),
        cwd=ROOT / "packages" / "deepviz", text=True, encoding="utf-8",
        capture_output=True, timeout=120, check=False,
    )
    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    for category in ("contracts", "normalization"):
        assert len({case["id"] for case in result[category]}) == len(result[category])
        result[category] = {case.pop("id"): case for case in result[category]}
    return result


def test_n12_imports_own_python_and_schema_copies_match_authority() -> None:
    for name in ("deepviz.models", "deepviz.normalize"):
        imported = Path(importlib.import_module(name).__file__).resolve()
        assert imported.is_relative_to(ROOT), f"Wrong source imported: {imported}"
    expected = ChartSpec.model_json_schema()
    for relative in ("schemas/chart-spec.schema.json", "packages/deepviz/src/chart-spec.schema.json"):
        assert json.loads((ROOT / relative).read_text(encoding="utf-8")) == expected


@pytest.mark.parametrize("case", CONTRACT, ids=lambda case: case["id"])
def test_n12_python_authoritative_acceptance(case: dict[str, Any]) -> None:
    assert _python_contract(case["input"])["accepted"] is case["accepted"]


@pytest.mark.integration
@pytest.mark.parametrize("case", CONTRACT, ids=lambda case: case["id"])
def test_n12_public_npm_acceptance_and_complete_defaults(
    case: dict[str, Any], public_npm: dict[str, Any],
) -> None:
    expected = _python_contract(case["input"])
    actual = public_npm["contracts"][case["id"]]
    assert actual["accepted"] is expected["accepted"]
    if expected["accepted"]:
        _assert_json_values(actual["dump"], expected["dump"])


@pytest.mark.parametrize("case", CONTRACT, ids=lambda case: case["id"])
def test_n12_raw_json_schema_acceptance_matches_python(case: dict[str, Any]) -> None:
    validator = jsonschema.Draft202012Validator(ChartSpec.model_json_schema())
    assert validator.is_valid(case["input"]) is _python_contract(case["input"])["accepted"]


@pytest.mark.integration
def test_n12_public_npm_schema_export_matches_python(public_npm: dict[str, Any]) -> None:
    assert public_npm["schema"] == ChartSpec.model_json_schema()
    built = ROOT / "packages" / "deepviz" / "dist" / "chart-spec.schema.json"
    assert json.loads(built.read_text(encoding="utf-8")) == public_npm["schema"]


@pytest.mark.parametrize("case", NORMALIZATION, ids=lambda case: case["id"])
def test_n12_python_normalization_independent_oracles(case: dict[str, Any]) -> None:
    _assert_normalized(_python_normalization(case), case)


@pytest.mark.integration
@pytest.mark.parametrize("case", NORMALIZATION, ids=lambda case: case["id"])
def test_n12_public_npm_normalization_independent_oracles(
    case: dict[str, Any], public_npm: dict[str, Any],
) -> None:
    _assert_normalized(public_npm["normalization"][case["id"]], case)


def _assert_normalized(actual: dict[str, Any], case: dict[str, Any]) -> None:
    assert actual["accepted"] is not case.get("rejected", False), actual
    if not case.get("rejected", False):
        _assert_json_values({key: actual["result"][key] for key in case["expected"]}, case["expected"])


def _warning_categories(warnings: list[str]) -> set[str]:
    text = " ".join(warnings).lower().replace("-", "").replace("_", "")
    terms = {
        "nonnumeric": "nonnumeric", "nonfinite": "nonfinite", "mixed": "mixed",
        "missing": "missing mapped", "null-skipped": "null graphql/path",
        "path-missing": "path branches", "graphql-errors": "errors alongside usable data",
        "overflow": "group cardinality exceeded",
    }
    return {category for category, term in terms.items() if term in text}


@pytest.mark.parametrize("case", [case for case in NORMALIZATION if case.get("warning_categories")], ids=lambda case: case["id"])
def test_n12_python_discloses_important_data_loss(case: dict[str, Any]) -> None:
    actual = _python_normalization(case)
    assert actual["accepted"], actual
    assert set(case["warning_categories"]) <= _warning_categories(actual["result"]["warnings"])


@pytest.mark.integration
@pytest.mark.parametrize("case", [case for case in NORMALIZATION if case.get("warning_categories")], ids=lambda case: case["id"])
def test_n12_public_npm_discloses_important_data_loss(case: dict[str, Any], public_npm: dict[str, Any]) -> None:
    actual = public_npm["normalization"][case["id"]]
    assert actual["accepted"], actual
    assert set(case["warning_categories"]) <= _warning_categories(actual["result"]["warnings"])


def _assert_sample(result: dict[str, Any]) -> None:
    assert result["input_count"] == 1000
    assert result["strategy"] == "sample"
    assert len(result["records"]) == 10
    indices = [row["id"] for row in result["records"]]
    assert indices == sorted(set(indices))
    assert all(row["value"] == row["id"] % 7 for row in result["records"])
    assert any("sample" in warning.lower() for warning in result["warnings"])


def test_n12_python_sample_is_bounded_ordered_and_repeatable() -> None:
    rows = [{"id": i, "value": i % 7} for i in range(1000)]
    spec = {"kind": "table", "aggregation": "none", "max_points": 10}
    first = asdict(normalize(rows, spec))
    _assert_sample(first)
    assert first == asdict(normalize(iter(rows), spec)) == asdict(normalize(rows, spec))


@pytest.mark.integration
def test_n12_npm_sample_matches_its_stream_and_repeat_not_python_rng(public_npm: dict[str, Any]) -> None:
    # Different deterministic RNGs are not asserted to select identical rows.
    _assert_sample(public_npm["sample"])
    assert public_npm["sample"] == public_npm["repeated"] == public_npm["stream"]


@pytest.mark.integration
def test_n12_nonfinite_direct_values_null_in_both_languages(public_npm: dict[str, Any]) -> None:
    py = asdict(normalize(
        [{"id": i, "value": value} for i, value in enumerate([float("nan"), float("inf"), -float("inf")], 1)],
        {"kind": "table", "aggregation": "none"},
    ))
    ts = public_npm["directNonfinite"]
    expected = [{"id": i, "value": None} for i in range(1, 4)]
    _assert_json_values(py["records"], expected)
    _assert_json_values(ts["records"], expected)
    assert "nonfinite" in _warning_categories(py["warnings"])
    assert "nonfinite" in _warning_categories(ts["warnings"])
