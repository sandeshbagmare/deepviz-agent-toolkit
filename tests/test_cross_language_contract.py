"""Exercise Python and the built npm package against one JSON contract corpus.

Python-only: python -m pytest tests/test_cross_language_contract.py -m "not integration"
Parity: npm ci && npm run build, then python -m pytest tests/test_cross_language_contract.py
Run npm commands at the repository root. Node >=22 and the built public package
are required for integration tests; missing prerequisites FAIL, never silently skip.
DEEPVIZ_TS_PACKAGE_ROOT may point at another worktree's packages/deepviz directory.
The Node subprocess imports @deepviz/agent-toolkit through its public exports;
it does not duplicate validation or load an internal source module.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from deepviz.models import ChartSpec

ROOT = Path(__file__).resolve().parents[1]
CORPUS = json.loads((Path(__file__).parent / "fixtures" / "schema-parity.json").read_text(encoding="utf-8"))
CASES = CORPUS["cases"]
for boundary in CORPUS["string_boundaries"]:
    text = boundary["character"] * boundary["length"]
    CASES.append({
        "id": boundary["id"],
        "input": {boundary["field"]: text},
        "accepted": boundary["accepted"],
        "expected": {boundary["field"]: text},
    })

NODE_RUNNER = r"""
import {readFileSync} from 'node:fs';
import {validateSpec, ValidationError} from '@deepviz/agent-toolkit';

const cases = JSON.parse(readFileSync(0, 'utf8'));
const results = cases.map(({id, input}) => {
  try {
    return {id, accepted: true, dump: validateSpec(input)};
  } catch (error) {
    if (!(error instanceof ValidationError)) throw error;
    return {id, accepted: false};
  }
});
process.stdout.write(JSON.stringify(results));
"""


def _expected_dump(overrides: dict[str, Any]) -> dict[str, Any]:
    """Expand hand-authored expectations, including each child's own defaults."""
    result = CORPUS["default_dump"] | overrides
    result["charts"] = [_expected_dump(child) for child in result["charts"]]
    return result


def _python_result(value: Any) -> dict[str, Any]:
    try:
        parsed = ChartSpec.model_validate(value)
    except ValidationError:
        return {"accepted": False}
    return {"accepted": True, "dump": parsed.model_dump(mode="json")}


def _assert_same_json(actual: Any, expected: Any) -> None:
    # Python's True == 1 would otherwise conceal a broken JSON boolean contract.
    assert json.dumps(actual, sort_keys=True, ensure_ascii=False) == json.dumps(
        expected, sort_keys=True, ensure_ascii=False
    )


@pytest.fixture(scope="session")
def node_results() -> dict[str, dict[str, Any]]:
    node = shutil.which("node")
    if node is None:
        pytest.fail("Schema parity requires Node >=22; install Node or select -m 'not integration'.")
    package_root = Path(os.environ.get("DEEPVIZ_TS_PACKAGE_ROOT", ROOT / "packages" / "deepviz")).resolve()
    package_json = package_root / "package.json"
    if not package_json.is_file():
        pytest.fail(
            f"Schema parity needs the built @deepviz/agent-toolkit package at {package_root}. "
            "Run npm ci and npm run build at the repository root, or set DEEPVIZ_TS_PACKAGE_ROOT. "
            "Select -m 'not integration' only for the explicitly Python-only lane."
        )
    completed = subprocess.run(
        [node, "--input-type=module", "--eval", NODE_RUNNER],
        input=json.dumps([{"id": case["id"], "input": case["input"]} for case in CASES]),
        text=True,
        encoding="utf-8",
        capture_output=True,
        cwd=package_root,
        timeout=120,
        check=False,
    )
    assert completed.returncode == 0, (
        "Public npm validation failed to execute. Build the package with npm ci and npm run build; "
        f"Node stderr:\n{completed.stderr}\nstdout:\n{completed.stdout}"
    )
    results = json.loads(completed.stdout)
    assert [result["id"] for result in results] == [case["id"] for case in CASES]
    return {result.pop("id"): result for result in results}


def test_corpus_includes_every_kind_and_unambiguous_case_ids() -> None:
    ids = [case["id"] for case in CASES]
    assert len(ids) == len(set(ids))
    kinds = {
        case["input"]["kind"]
        for case in CASES
        if case["accepted"] and isinstance(case["input"], dict) and "kind" in case["input"]
    }
    assert kinds == {
        "bar", "line", "scatter", "area", "pie", "heatmap", "histogram", "box", "violin",
        "bubble", "radar", "treemap", "sunburst", "funnel", "gauge", "geo", "table", "dashboard",
    }


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
def test_python_chart_spec_matches_contract_corpus(case: dict[str, Any]) -> None:
    expected: dict[str, Any] = {"accepted": case["accepted"]}
    if case["accepted"]:
        expected["dump"] = _expected_dump(case["expected"])
    _assert_same_json(_python_result(case["input"]), expected)


@pytest.mark.integration
@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
def test_public_npm_validator_matches_python(
    case: dict[str, Any], node_results: dict[str, dict[str, Any]]
) -> None:
    # Compare complete dumps, not merely acceptance or a subset of default fields.
    _assert_same_json(node_results[case["id"]], _python_result(case["input"]))
