"""Lazy LangChain adapters and the shared, bounded integration trust boundary."""
from __future__ import annotations

import json
import shutil
import tempfile
from collections import OrderedDict
from pathlib import Path, PureWindowsPath
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from .models import ChartSpec, Engine
from .recommend import Goal, profile, recommend

ENGINES: tuple[Engine, ...] = ("matplotlib", "plotly", "vega", "echarts", "antv")
MAX_INLINE_BYTES = 1_000_000
MAX_ARTIFACT_BYTES = 16 * 1024 * 1024


def _inline_data(data: Any) -> Any:
    """Admit original encoded bytes before any caller can discard JSON details."""
    if isinstance(data, str):
        if len(data.encode("utf-8")) > MAX_INLINE_BYTES:
            raise ValueError("Inline data exceeds 1 MB; configure data_dir and use a file reference")
        from .normalize import _json

        data = _json(data, "inline data")
    if not isinstance(data, (list, dict)):
        raise ValueError("Inline data must be a JSON array or object, not a file path string")
    try:
        encoded = json.dumps(data, allow_nan=False)
    except RecursionError as error:
        raise ValueError("Inline JSON data is nested too deeply") from error
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("Tool inputs must be finite JSON data or an explicit file reference") from error
    if len(encoded.encode("utf-8")) > MAX_INLINE_BYTES:
        raise ValueError("Inline data exceeds 1 MB; configure data_dir and use a file reference")
    return data


def _profile_spec() -> ChartSpec:
    return ChartSpec(kind="table", aggregation="sample", max_points=200)


class RenderInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    data: Any = Field(description="Small JSON data, {file: relative_path}, or {dataset_id: returned_handle}.")
    spec: ChartSpec


class NormalizeInput(RenderInput):
    spec: ChartSpec = Field(default_factory=_profile_spec)


class RecommendInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    data: Any = Field(description="Small JSON data, {file: relative_path}, or {dataset_id: returned_handle}.")
    goal: Goal = "comparison"


class ToolSession:
    """One agent/server's allowed directories and bounded source-handle cache.

    File references are opt-in. Directory containment is a boundary against model-
    authored paths, not a sandbox against a malicious local filesystem owner.
    """

    def __init__(self, output_dir: str | Path | None = None, *, data_dir: str | Path | None = None):
        self.output_dir = Path(output_dir or "deepviz-output").resolve()
        self.data_dir = Path(data_dir).resolve(strict=True) if data_dir is not None else None
        if self.data_dir is not None and not self.data_dir.is_dir():
            raise ValueError("data_dir must be a directory")
        self.datasets: OrderedDict[str, dict[str, Any]] = OrderedDict()

    def _source(self, data: Any) -> Any:
        data = _inline_data(data)
        if isinstance(data, dict) and set(data) == {"dataset_id"}:
            cached = self.datasets.get(str(data["dataset_id"]))
            if cached is None:
                raise ValueError("Unknown or expired dataset_id; normalize the source again")
            return self._source(cached["source"])
        if isinstance(data, dict) and set(data) == {"file"}:
            if self.data_dir is None:
                raise ValueError("File inputs require the host to configure data_dir")
            name = data["file"]
            if not isinstance(name, str) or ":" in name or Path(name).is_absolute() or PureWindowsPath(name).drive:
                raise ValueError("File references must be relative to the configured data directory; no URLs")
            candidate = (self.data_dir / name).resolve()
            if not candidate.is_relative_to(self.data_dir):
                raise ValueError("File reference escapes the configured data directory")
            if not candidate.is_file():
                raise ValueError("File does not exist in the configured data directory")
            return candidate
        return data

    def normalize_data(self, data: Any, spec: ChartSpec | dict[str, Any] | None = None) -> dict[str, Any]:
        """Profile bounded rows; return counts, field types, and a reusable handle, never raw rows."""
        chart = ChartSpec.model_validate(spec) if spec is not None else _profile_spec()
        data = _inline_data(data)
        source = self._source(data)
        from .normalize import normalize

        normalized = normalize(source, chart)
        dataset_id = uuid4().hex
        result = {
            "dataset_id": dataset_id,
            "input_count": normalized.input_count,
            "output_count": len(normalized.records),
            "strategy": normalized.strategy,
            "warnings": normalized.warnings,
            "profile": profile(normalized),
        }
        # Keep original small sources/references, not copied full or reduced datasets.
        # Decode validated JSON references without caching the resolved file Path.
        original = data
        if isinstance(original, dict) and set(original) == {"dataset_id"}:
            original = self.datasets[str(original["dataset_id"])]["source"]
        self.datasets[dataset_id] = {"source": original, "summary": result}
        if len(self.datasets) > 32:
            self.datasets.popitem(last=False)
        return result

    def recommend_chart(self, data: Any, goal: Goal = "comparison") -> dict[str, Any]:
        """Recommend an editable chart using bounded observed types; verify semantic assumptions."""
        if isinstance(data, dict) and set(data) == {"dataset_id"}:
            cached = self.datasets.get(str(data["dataset_id"]))
            if cached is None:
                raise ValueError("Unknown or expired dataset_id; normalize the source again")
            summary = cached["summary"]
        else:
            summary = self.normalize_data(data)
        result = recommend(summary["profile"], goal)
        result.update({"dataset_id": summary["dataset_id"], "input_count": summary["input_count"]})
        result["warnings"] = summary["warnings"] + result["warnings"]
        return result

    def render_chart(self, engine: Engine, data: Any, spec: ChartSpec | dict[str, Any]) -> dict[str, Any]:
        """Re-read/reduce the original source so input counts are not reset to a profile's size."""
        if engine not in ENGINES:
            raise ValueError("Unsupported rendering engine")
        chart = ChartSpec.model_validate(spec)
        source = self._source(data)
        from .render import render

        self.output_dir.mkdir(parents=True, exist_ok=True)
        destination = Path(tempfile.mkdtemp(prefix=f"{engine}-", dir=self.output_dir))
        try:
            result = render(source, chart, engine=engine, output_dir=destination).to_dict()
            if not result["paths"]:
                raise ValueError("Renderer returned no artifacts")
            for value in result["paths"]:
                path = Path(value).resolve(strict=True)
                if not path.is_relative_to(destination) or not path.is_file():
                    raise ValueError("Renderer output escaped the allowed output directory")
                if path.stat().st_size > MAX_ARTIFACT_BYTES:
                    raise ValueError("Artifact exceeds the 16 MiB integration limit; reduce max_points or chart dimensions")
        except BaseException:
            # Only this request's freshly-created subtree belongs to this call.
            # Keep successful artifacts, but never accumulate failed/partial ones.
            shutil.rmtree(destination, ignore_errors=True)
            raise
        return result

    def renderer(self, engine: Engine):
        def render_tool(data: Any, spec: ChartSpec) -> dict[str, Any]:
            return self.render_chart(engine, data, spec)

        render_tool.__name__ = f"render_{engine}"
        render_tool.__doc__ = (
            f"Render a validated chart with {engine}. Pass small JSON, a dataset_id, or an allowed file reference. "
            "Return artifact paths and explicit input/output counts, reduction strategy, and warnings. "
            "Never supply executable code or unbounded raw data."
        )
        return render_tool


def create_tools(output_dir: str | Path | None = None, *, data_dir: str | Path | None = None) -> list[Any]:
    """Attach with create_deep_agent(tools=create_tools(...)); imports LangChain only here."""
    try:
        from langchain_core.tools import StructuredTool
    except ImportError as error:
        raise ImportError("Install the agents extra: pip install -e '.[agents]'") from error

    class ValidatedTool(StructuredTool):
        # LangChain formats inputs for callbacks before invoking our function.
        def run(self, tool_input: str | dict[str, Any], *args: Any, **kwargs: Any) -> Any:
            if isinstance(tool_input, str):
                tool_input = {"data": tool_input}
            if isinstance(tool_input, dict) and "data" in tool_input:
                tool_input = {**tool_input, "data": _inline_data(tool_input["data"])}
            return super().run(tool_input, *args, **kwargs)

        async def arun(self, tool_input: str | dict[str, Any], *args: Any, **kwargs: Any) -> Any:
            if isinstance(tool_input, str):
                tool_input = {"data": tool_input}
            if isinstance(tool_input, dict) and "data" in tool_input:
                tool_input = {**tool_input, "data": _inline_data(tool_input["data"])}
            return await super().arun(tool_input, *args, **kwargs)

    session = ToolSession(output_dir, data_dir=data_dir)
    tools = [
        ValidatedTool.from_function(session.renderer(engine), args_schema=RenderInput)
        for engine in ENGINES
    ]
    tools.extend([
        ValidatedTool.from_function(session.normalize_data, args_schema=NormalizeInput),
        ValidatedTool.from_function(session.recommend_chart, args_schema=RecommendInput),
    ])
    return tools
