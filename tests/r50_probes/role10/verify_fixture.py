"""Validate bounded R50 proposal literals without importing product code."""
from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    path = Path(__file__).with_name("selected_record_contract_cases.json")
    fixture = json.loads(path.read_text(encoding="utf-8"))
    assert fixture["product_pin"] == "546c25ea75ee9d8a41b3832aa639664bc9a683b5"
    cases = fixture["cases"]
    assert [case["id"] for case in cases] == [
        "f1-object", "f1-json", "bounded-nested-record",
        "ordinary-protocol-looking-sibling", "graphql-partial-control",
        "graphql-error-only-control",
    ]
    for case in cases:
        assert len(json.dumps(case, ensure_ascii=False)) < 16 * 1024
        assert case["spec"]["data_path"]
    for case in cases[:2]:
        expected = case["expected"]
        assert expected["input_count"] == 2
        assert len(expected["records"]) == 2
        assert expected["warnings"] == []
        assert case["current_observation"]["python"].startswith("ValueError:")
        assert case["current_observation"]["typescript"].startswith("ValidationError:")
    assert cases[4]["expected"]["records"] == [{"id": 1}]
    assert cases[5]["expected_error"].startswith("GraphQL")
    print("R50_FIXTURE_INTEGRITY_PASS=6_CASES/0_PRODUCT_EXECUTIONS")


if __name__ == "__main__":
    main()
