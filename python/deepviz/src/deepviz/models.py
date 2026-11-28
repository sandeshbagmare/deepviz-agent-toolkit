"""Versioned, execution-free contracts shared by all rendering adapters."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ChartKind = Literal[
    "bar", "line", "scatter", "area", "pie", "heatmap", "histogram", "box", "violin",
    "bubble", "radar", "treemap", "sunburst", "funnel", "gauge", "geo", "table", "dashboard",
]
Engine = Literal["matplotlib", "plotly", "vega", "echarts", "antv"]
_MAX_DATA_PATH_LENGTH = 1024
_MAX_DATA_PATH_COMPONENTS = 64
_DATA_PATH_PATTERN = r"^[^.]+(?:\.[^.]+){0,63}$"


class ChartSpec(BaseModel):
    """Map normalized record fields to a bounded chart or composed dashboard."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "if": {"properties": {"kind": {"const": "dashboard"}}, "required": ["kind"]},
            "then": {"required": ["charts"], "properties": {"charts": {"minItems": 1}}},
            "else": {"properties": {"charts": {"maxItems": 0}}},
            "allOf": [{
                "properties": {"charts": {"items": {"not": {
                    "properties": {"kind": {"const": "dashboard"}}, "required": ["kind"],
                }}}},
            }],
        },
    )
    version: Literal[1] = 1
    kind: ChartKind = "bar"
    title: str = Field(default="Visualization", max_length=500)
    description: str = Field(default="", max_length=2000)
    x: str | None = None
    y: str | None = None
    color: str | None = None
    size: str | None = None
    data_path: str | None = Field(
        default=None,
        max_length=_MAX_DATA_PATH_LENGTH,
        json_schema_extra={"pattern": _DATA_PATH_PATTERN},
        description=(
            "Dot-separated path with 1 to 64 non-empty components and at most "
            "1,024 Unicode code points (1,024 ASCII characters or at most 4 KiB UTF-8)."
        ),
    )
    format: Literal["auto", "json", "jsonl", "csv", "tsv", "parquet", "arrow"] = "auto"
    aggregation: Literal["auto", "none", "sample", "sum", "mean", "count", "min", "max"] = "auto"
    max_points: int = Field(default=2000, ge=10, le=100000)
    width: int = Field(default=900, ge=240, le=4096)
    height: int = Field(default=520, ge=200, le=4096)
    theme: Literal["light", "dark"] = "light"
    charts: list[ChartSpec] = Field(default_factory=list, max_length=24)
    columns: int = Field(default=2, ge=1, le=6)

    @field_validator("data_path")
    @classmethod
    def validate_data_path(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if value.count(".") + 1 > _MAX_DATA_PATH_COMPONENTS:
            raise ValueError("data_path is nested too deeply")
        if any(not token for token in value.split(".")):
            raise ValueError("data_path must contain non-empty dot-separated components")
        return value

    @model_validator(mode="before")
    @classmethod
    def preserve_json_numeric_types(cls, value: Any) -> Any:
        if isinstance(value, Mapping):
            for key in ("version", "max_points", "width", "height", "columns"):
                if key in value and (
                    isinstance(value[key], bool) or not isinstance(value[key], (int, float))
                ):
                    raise ValueError(f"{key} must be a JSON number, not a string or boolean")
        return value

    @model_validator(mode="after")
    def check_dashboard(self) -> ChartSpec:
        if self.kind == "dashboard" and not self.charts:
            raise ValueError("A dashboard requires at least one chart")
        if self.kind != "dashboard" and self.charts:
            raise ValueError("Only dashboards can contain charts")
        if any(chart.kind == "dashboard" for chart in self.charts):
            raise ValueError("Nested dashboards are not supported")
        return self


@dataclass
class NormalizedData:
    records: list[dict[str, Any]]
    input_count: int
    warnings: list[str] = field(default_factory=list)
    strategy: str = "none"


@dataclass
class Artifact:
    paths: list[str]
    mime_type: str
    engine: str
    input_count: int
    output_count: int
    strategy: str
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        from dataclasses import asdict
        return asdict(self)
