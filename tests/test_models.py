"""Trust-boundary tests for the shared, execution-free chart contract."""
from dataclasses import asdict

import pytest
from pydantic import ValidationError

from deepviz.models import Artifact, ChartSpec, NormalizedData


@pytest.mark.parametrize("key,value", [
    ("kind", "arbitrary-code"), ("version", 2), ("max_points", 0),
    ("max_points", 100001), ("width", 1), ("width", 5000),
    ("height", 1), ("height", 5000), ("theme", "injected"),
    ("format", "pickle"), ("aggregation", "eval"), ("columns", 0),
    ("columns", 7), ("title", "x" * 501), ("description", "x" * 2001),
])
def test_invalid_schema_values_fail_closed(key, value):
    with pytest.raises(ValidationError):
        ChartSpec.model_validate({key: value})


@pytest.mark.parametrize("key", ["code", "expression", "javascript", "sql", "url"])
def test_executable_and_remote_schema_fields_are_not_supported(key):
    with pytest.raises(ValidationError):
        ChartSpec.model_validate({key: "not executable"})


def test_defaults_are_bounded_and_serializable():
    spec = ChartSpec()
    assert spec.max_points == 2000
    assert spec.model_dump(mode="json")["version"] == 1
    assert ChartSpec.model_validate_json(spec.model_dump_json()) == spec


def test_dashboard_requires_children_and_rejects_nesting():
    with pytest.raises(ValidationError, match="requires at least one"):
        ChartSpec(kind="dashboard")
    with pytest.raises(ValidationError, match="Only dashboards"):
        ChartSpec(charts=[ChartSpec()])
    with pytest.raises(ValidationError, match="Nested dashboards"):
        ChartSpec(kind="dashboard", charts=[ChartSpec(kind="dashboard", charts=[ChartSpec()])])
    with pytest.raises(ValidationError):
        ChartSpec(kind="dashboard", charts=[ChartSpec()] * 25)


def test_artifact_metadata_does_not_share_mutable_defaults():
    first = Artifact(["chart.svg"], "image/svg+xml", "vega", 10, 10, "none")
    second = Artifact(["other.svg"], "image/svg+xml", "vega", 10, 10, "none")
    first.warnings.append("example")
    assert not second.warnings
    assert first.to_dict() == asdict(first)
    normalized = NormalizedData([], 0)
    assert normalized.strategy == "none"
    assert normalized.warnings == []
