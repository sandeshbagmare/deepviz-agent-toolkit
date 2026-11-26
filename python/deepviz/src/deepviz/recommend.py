"""Small, deterministic chart recommendations from a bounded observed profile."""
from __future__ import annotations

import math
from datetime import datetime
from typing import Any, Literal

from .models import ChartKind, ChartSpec, NormalizedData

Goal = Literal["comparison", "trend", "relationship", "distribution", "composition"]


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        number = float(value)
    except (ValueError, TypeError, OverflowError):
        return None
    return number if math.isfinite(number) else None


def _date(value: Any) -> bool:
    if not isinstance(value, str) or len(value) < 10:
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def profile(data: NormalizedData) -> dict[str, Any]:
    """Describe at most 100 fields without copying raw values into model context."""
    fields: dict[str, None] = {}
    truncated = False
    for row in data.records:
        for key in row:
            if not isinstance(key, str) or len(key) > 256:
                truncated = True
            elif key not in fields:
                if len(fields) == 100:
                    truncated = True
                    break
                fields[key] = None
    numeric: list[str] = []
    temporal: list[str] = []
    categorical: list[str] = []
    nonnegative: list[str] = []
    positive_total: list[str] = []
    for name in fields:
        values = [row[name] for row in data.records if row.get(name) is not None]
        if not values:
            continue
        numbers = [_number(value) for value in values]
        if all(value is not None for value in numbers):
            numeric.append(name)
            if all(value is not None and value >= 0 for value in numbers):
                nonnegative.append(name)
                if any(value is not None and value > 0 for value in numbers):
                    positive_total.append(name)
        elif all(_date(value) for value in values):
            temporal.append(name)
        else:
            categorical.append(name)
    return {
        "fields": list(fields),
        "numeric_fields": numeric,
        "temporal_fields": temporal,
        "categorical_fields": categorical,
        "nonnegative_fields": nonnegative,
        "positive_total_fields": positive_total,
        "fields_truncated": truncated,
        "profiled_rows": len(data.records),
    }


def recommend(observed: dict[str, Any], goal: Goal = "comparison") -> dict[str, Any]:
    """Suggest an editable spec, not a claim of semantic understanding."""
    if goal not in {"comparison", "trend", "relationship", "distribution", "composition"}:
        raise ValueError("Unsupported recommendation goal")
    numbers = observed["numeric_fields"]
    categories = observed["categorical_fields"]
    dates = observed["temporal_fields"]
    kind: ChartKind = "table"
    x: str | None = None
    y: str | None = None
    rationale = "No suitable numeric mapping observed; inspect a table and choose fields explicitly."
    if goal == "relationship" and len(numbers) >= 2:
        kind, x, y = "scatter", numbers[0], numbers[1]
        rationale = "Two observed numeric fields permit a relationship plot; this does not establish causality."
    elif goal == "distribution" and numbers:
        kind, x = "histogram", numbers[0]
        rationale = "A histogram summarizes the observed numeric distribution."
    elif goal == "trend" and numbers and (dates or len(numbers) >= 2):
        kind, x, y = "line", (dates or numbers)[0], numbers[0] if dates else numbers[1]
        rationale = "An ordered date/numeric field is available; verify ordering and time semantics."
    elif categories and numbers:
        kind, x, y = "bar", categories[0], numbers[0]
        rationale = "Compare an observed numeric measure across categories; verify the aggregation and units."
        if goal == "composition" and numbers[0] in observed["positive_total_fields"]:
            kind = "pie"
            rationale = "Nonnegative observed values allow composition; confirm categories are parts of one whole."
        elif goal == "composition":
            rationale = "Pie slices require nonnegative values and a positive total; compare these values with bars."
    elif numbers:
        kind, x = "histogram", numbers[0]
        rationale = "Only a numeric field was available; a distribution is safer than inventing category semantics."
    spec = ChartSpec(kind=kind, x=x, y=y, aggregation="auto")
    return {
        "spec": spec.model_dump(exclude_none=True),
        "engine": "matplotlib",
        "rationale": rationale,
        "warnings": ["Recommendation uses bounded observed rows/types only; review fields, units, and reduction."],
    }
