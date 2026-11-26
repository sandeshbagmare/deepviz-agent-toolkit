"""Versioned, execution-free contracts shared by all rendering adapters."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ChartKind = Literal[
    "bar", "line", "scatter", "area", "pie", "heatmap", "histogram", "box", "violin",
    "bubble", "radar", "treemap", "sunburst", "funnel", "gauge", "geo", "table", "dashboard",
]
Engine = Literal["matplotlib", "plotly", "vega", "echarts", "antv"]


class ChartSpec(BaseModel):
    """Map normalized record fields to a bounded chart or composed dashboard."""

    model_config = ConfigDict(extra="forbid")
    version: Literal[1] = 1
    kind: ChartKind = "bar"
    title: str = Field(default="Visualization", max_length=500)
    description: str = Field(default="", max_length=2000)
    x: str | None = None
    y: str | None = None
    color: str | None = None
    size: str | None = None
    data_path: str | None = None
    format: Literal["auto", "json", "jsonl", "csv", "tsv", "parquet", "arrow"] = "auto"
    aggregation: Literal["auto", "none", "sample", "sum", "mean", "count", "min", "max"] = "auto"
    max_points: int = Field(default=2000, ge=10, le=100000)
    width: int = Field(default=900, ge=240, le=4096)
    height: int = Field(default=520, ge=200, le=4096)
    theme: Literal["light", "dark"] = "light"
    charts: list[ChartSpec] = Field(default_factory=list, max_length=24)
    columns: int = Field(default=2, ge=1, le=6)

    @model_validator(mode="before")
    @classmethod
    def preserve_json_numeric_types(cls, value: Any) -> Any:
        if isinstance(value, dict):
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
