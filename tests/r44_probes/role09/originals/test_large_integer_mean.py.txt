"""An accepted Python integer pair has an exactly representable zero mean."""
import json

from deepviz import normalize


def test_large_valid_integer_cancellation_mean_does_not_need_decimal_unit_encoding():
    large = 10**4000
    rows = [{"g": "only", "v": large}, {"g": "only", "v": -large}]
    pristine = json.dumps(rows)
    assert len(pristine) < 16384
    result = normalize(iter(rows), {"x": "g", "y": "v", "aggregation": "mean", "max_points": 10})
    assert result.records == [{"g": "only", "v": 0.0}]
    assert result.input_count == 2 and result.strategy == "mean"
    assert result.warnings == []
    assert json.dumps(rows) == pristine
