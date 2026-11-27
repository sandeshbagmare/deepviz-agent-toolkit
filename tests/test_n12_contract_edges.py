"""Bounded independent raw/default/recursive contract oracles, not data parity.

Run `npm run build` in this checkout first. No previous normalization tests are
imported, relaxed, or rerun here. All payloads are JSON-compatible and bounded to
25 children and eight composition levels. Expected acceptance and defaults below
are literal contract decisions, not snapshots of the implementation under test.
"""
from __future__ import annotations

import copy
import importlib
import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jsonschema
import pytest
from pydantic import ValidationError

from deepviz.models import ChartSpec

ROOT = Path(__file__).resolve().parents[1]
DEFAULTS: dict[str, Any] = {
    "version": 1, "kind": "bar", "title": "Visualization", "description": "",
    "x": None, "y": None, "color": None, "size": None, "data_path": None,
    "format": "auto", "aggregation": "auto", "max_points": 2000,
    "width": 900, "height": 520, "theme": "light", "charts": [], "columns": 2,
}
KINDS = (
    "bar", "line", "scatter", "area", "pie", "heatmap", "histogram", "box", "violin",
    "bubble", "radar", "treemap", "sunburst", "funnel", "gauge", "geo", "table",
)


@dataclass(frozen=True)
class Case:
    name: str
    payload: Any
    accepted: bool


def _cases() -> list[Case]:
    cases = [
        Case("omitted-kind-and-charts", {}, True),
        Case("omitted-kind-empty-charts", {"charts": []}, True),
        Case("omitted-kind-nonempty-charts", {"charts": [{}]}, False),
        Case("omitted-kind-null-charts", {"charts": None}, False),
        Case("dashboard-missing-charts", {"kind": "dashboard"}, False),
        Case("dashboard-empty-charts", {"kind": "dashboard", "charts": []}, False),
        Case("dashboard-null-charts", {"kind": "dashboard", "charts": None}, False),
        Case("dashboard-child-default-kind", {"kind": "dashboard", "charts": [{}]}, True),
        Case("dashboard-child-explicit-empty-charts", {"kind": "dashboard", "charts": [{"charts": []}]}, True),
        Case("child-omitted-kind-nonempty-grandchildren", {"kind": "dashboard", "charts": [{"charts": [{}]}]}, False),
        Case("child-omitted-kind-null-grandchildren", {"kind": "dashboard", "charts": [{"charts": None}]}, False),
        Case("child-dashboard-omits-charts", {"kind": "dashboard", "charts": [{"kind": "dashboard"}]}, False),
        Case("child-null-kind", {"kind": "dashboard", "charts": [{"kind": None}]}, False),
        Case("child-empty-kind", {"kind": "dashboard", "charts": [{"kind": ""}]}, False),
        Case("root-null", None, False),
        Case("root-array", [], False),
        Case("root-boolean", False, False),
        Case("root-number", 1, False),
        Case("root-string", "{}", False),
    ]
    for kind in KINDS:
        cases.extend([
            Case(f"{kind}-omitted-charts", {"kind": kind}, True),
            Case(f"{kind}-empty-charts", {"kind": kind, "charts": []}, True),
            Case(f"{kind}-unexpected-child", {"kind": kind, "charts": [{}]}, False),
        ])
    for count in (1, 23, 24, 25):
        cases.append(Case(
            f"dashboard-{count}-default-children",
            {"kind": "dashboard", "charts": [{} for _ in range(count)]}, count <= 24,
        ))
    for position in (0, 11, 23):
        children = [{} for _ in range(24)]
        children[position] = {"kind": "dashboard", "charts": [{}]}
        cases.append(Case(f"nested-dashboard-at-child-{position}", {"kind": "dashboard", "charts": children}, False))
    for depth in (1, 2, 3, 8):
        payload: dict[str, Any] = {}
        for _ in range(depth):
            payload = {"kind": "dashboard", "charts": [payload]}
        cases.append(Case(f"composition-depth-{depth}", payload, depth == 1))
    numeric = {"version": 1, "max_points": 10, "width": 240, "height": 200, "columns": 1}
    for field, minimum in numeric.items():
        variants = [
            ("integral-float", float(minimum), True),
            ("fractional", minimum + 0.5, False),
            ("true", True, False), ("false", False, False), ("null", None, False),
            ("integer-text", str(minimum), False),
            ("decimal-text", f"{minimum}.0", False),
            ("whitespace-text", f" {minimum} ", False),
        ]
        for label, value, accepted in variants:
            raw = {field: value}
            cases.append(Case(f"root-{field}-{label}", raw, accepted))
            cases.append(Case(
                f"child-{field}-{label}", {"kind": "dashboard", "charts": [raw]}, accepted,
            ))
    for field, maximum in (("title", 500), ("description", 2000)):
        for label, cluster in (("astral", "\U0001f600"), ("combining", "e\u0301"), ("zwj", "\U0001f469\u200d\U0001f4bb")):
            for length in (maximum - 1, maximum, maximum + 1):
                # Boundaries count Unicode code points, not grapheme clusters or UTF-16 units.
                text = (cluster * (length // len(cluster) + 1))[:length]
                cases.append(Case(
                    f"child-{field}-{label}-codepoints-{length}",
                    {"kind": "dashboard", "charts": [{field: text}]}, length <= maximum,
                ))
    for field in ("x", "y", "color", "size", "data_path"):
        for label, value, accepted in (("null", None, True), ("empty", "", True), ("numeric", 1, False), ("boolean", True, False)):
            cases.append(Case(
                f"child-{field}-{label}", {"kind": "dashboard", "charts": [{field: value}]}, accepted,
            ))
    for field, minimum, maximum in (
        ("max_points", 10, 100000), ("width", 240, 4096),
        ("height", 200, 4096), ("columns", 1, 6),
    ):
        for label, value, accepted in (
            ("maximum", maximum, True), ("above-maximum", maximum + 1, False),
            ("below-minimum", minimum - 1, False),
        ):
            cases.append(Case(
                f"child-{field}-{label}", {"kind": "dashboard", "charts": [{field: value}]}, accepted,
            ))
    for label, raw in (
        ("unknown-property", {"script": "never executed"}),
        ("proto-property", {"__proto__": {"kind": "bar"}}),
        ("constructor-property", {"constructor": "inert"}),
        ("bad-format", {"format": "remote-url"}),
        ("bad-theme", {"theme": None}),
        ("bad-title", {"title": None}),
    ):
        cases.append(Case(f"root-{label}", raw, False))
        cases.append(Case(f"child-{label}", {"kind": "dashboard", "charts": [raw]}, False))
    return cases


CASES = _cases()
NODE = r"""
import {readFileSync} from 'node:fs';
import {validateSpec, chartSpecSchema, ValidationError} from '@deepviz/agent-toolkit';
const input=JSON.parse(readFileSync(0,'utf8'));
const results=input.map(({name,payload})=>{
  const before=JSON.stringify(payload);
  try {
    const dump=validateSpec(payload);
    return {name,accepted:true,dump,unchanged:JSON.stringify(payload)===before};
  } catch(error) {
    if (!(error instanceof ValidationError)) throw error;
    return {name,accepted:false,unchanged:JSON.stringify(payload)===before};
  }
});
const original={kind:'dashboard',charts:[{}]};
const first=validateSpec(original), second=validateSpec(original);
first.charts[0].title='mutated'; first.charts.push(validateSpec());
process.stdout.write(JSON.stringify({
  results,schema:chartSpecSchema,module:import.meta.resolve('@deepviz/agent-toolkit'),
  independentDefaults:{original,second},node:process.version,
}));
"""


@pytest.fixture(scope="module")
def public_npm() -> dict[str, Any]:
    node = shutil.which("node")
    assert node is not None, "Node is required; this contract gate must not silently skip."
    built = ROOT / "packages" / "deepviz" / "dist" / "index.js"
    assert built.is_file(), "Build this checkout with npm run build before contract QA."
    completed = subprocess.run(
        [node, "--input-type=module", "--eval", NODE],
        input=json.dumps([{"name": case.name, "payload": case.payload} for case in CASES], allow_nan=False),
        cwd=ROOT / "packages" / "deepviz", text=True, encoding="utf-8",
        capture_output=True, check=False, timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    result: dict[str, Any] = json.loads(completed.stdout)
    assert result["module"] == built.as_uri(), f"Wrong public npm source: {result['module']}"
    assert len(result["results"]) == len(CASES)
    result["results"] = {item.pop("name"): item for item in result["results"]}
    assert len(result["results"]) == len(CASES)
    return result


def _expected_defaults(payload: dict[str, Any]) -> dict[str, Any]:
    expected = copy.deepcopy(DEFAULTS) | payload
    for field in ("version", "max_points", "width", "height", "columns"):
        expected[field] = int(expected[field])
    expected["charts"] = [_expected_defaults(child) for child in expected["charts"]]
    return expected


def _python_result(payload: Any, *, encoded: bool = False) -> dict[str, Any]:
    try:
        parsed = ChartSpec.model_validate_json(json.dumps(payload)) if encoded else ChartSpec.model_validate(payload)
    except ValidationError:
        return {"accepted": False}
    return {"accepted": True, "dump": parsed.model_dump(mode="json")}


def _assert_exact_json(actual: Any, expected: Any) -> None:
    # Dumps use integer fields after parsing. JSON text keeps True distinct from 1.
    assert json.dumps(actual, sort_keys=True, ensure_ascii=True) == json.dumps(
        expected, sort_keys=True, ensure_ascii=True,
    )


@pytest.mark.integration
@pytest.mark.parametrize("case", CASES, ids=lambda case: case.name)
def test_n12_declared_raw_and_default_edges_agree(case: Case, public_npm: dict[str, Any]) -> None:
    before = copy.deepcopy(case.payload)
    direct = _python_result(case.payload)
    encoded = _python_result(case.payload, encoded=True)
    npm = public_npm["results"][case.name]
    validator = jsonschema.Draft202012Validator(public_npm["schema"])
    acceptance = {
        "python": direct["accepted"], "python-json": encoded["accepted"],
        "raw-schema": validator.is_valid(case.payload), "npm": npm["accepted"],
    }
    assert acceptance == dict.fromkeys(acceptance, case.accepted)
    assert npm["unchanged"] is True
    _assert_exact_json(case.payload, before)
    if case.accepted:
        expected = _expected_defaults(case.payload)
        for result in (direct, encoded, npm):
            _assert_exact_json(result["dump"], expected)
        validator.validate(expected)


@pytest.mark.integration
def test_n12_schema_copies_defaults_and_public_source_identity(public_npm: dict[str, Any]) -> None:
    module = Path(importlib.import_module("deepviz.models").__file__).resolve()
    assert module == (ROOT / "python" / "deepviz" / "src" / "deepviz" / "models.py").resolve()
    authority = ChartSpec.model_json_schema()
    jsonschema.Draft202012Validator.check_schema(authority)
    for relative in (
        "schemas/chart-spec.schema.json", "packages/deepviz/src/chart-spec.schema.json",
        "packages/deepviz/dist/chart-spec.schema.json",
    ):
        assert json.loads((ROOT / relative).read_text(encoding="utf-8")) == authority
    assert public_npm["schema"] == authority
    properties = authority["$defs"]["ChartSpec"]["properties"]
    for name, expected in DEFAULTS.items():
        if name != "charts":  # A default_factory has no static schema default annotation.
            _assert_exact_json(properties[name]["default"], expected)


@pytest.mark.integration
def test_n12_recursive_defaults_do_not_alias_or_mutate_inputs(public_npm: dict[str, Any]) -> None:
    original: dict[str, Any] = {"kind": "dashboard", "charts": [{}]}
    first, second = ChartSpec.model_validate(original), ChartSpec.model_validate(original)
    first.charts[0].title = "mutated"
    first.charts.append(ChartSpec())
    _assert_exact_json(original, {"kind": "dashboard", "charts": [{}]})
    _assert_exact_json(second.model_dump(mode="json"), _expected_defaults(original))
    _assert_exact_json(public_npm["independentDefaults"]["original"], original)
    _assert_exact_json(public_npm["independentDefaults"]["second"], _expected_defaults(original))


def test_n12_dashboard_negative_controls_detect_missing_semantic_keywords() -> None:
    authority = ChartSpec.model_json_schema()
    weakened = copy.deepcopy(authority)
    definition = weakened["$defs"]["ChartSpec"]
    for keyword in ("if", "then", "else", "allOf"):
        definition.pop(keyword)
    raw = jsonschema.Draft202012Validator(authority)
    negative_control = jsonschema.Draft202012Validator(weakened)
    for payload in (
        {"kind": "dashboard"}, {"charts": [{}]},
        {"kind": "dashboard", "charts": [{"kind": "dashboard", "charts": [{}]}]},
    ):
        assert not raw.is_valid(payload)
        assert negative_control.is_valid(payload), "Negative control no longer isolates dashboard semantics."


def test_n12_bounded_edge_corpus_is_unique_and_not_derived_from_runtime() -> None:
    names = [case.name for case in CASES]
    assert len(names) == len(set(names))
    assert any(case.accepted for case in CASES) and any(not case.accepted for case in CASES)
    assert max(len(json.dumps(case.payload)) for case in CASES) < 30000
