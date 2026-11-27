"""Public rendering boundary: validate, normalize bounded data, then render."""
from __future__ import annotations

import json
import math
import tempfile
import xml.etree.ElementTree as ET
from collections.abc import Iterator, Mapping
from datetime import date, datetime, time
from decimal import Decimal
from numbers import Integral, Real
from pathlib import Path
from typing import Any

from .engines import (
    ENGINES,
    _colors,
    _fallback,
    _geometry,
    _table_budget,
    browser_html,
    channels,
    matplotlib_figure,
    native_spec,
)
from .models import Artifact, ChartSpec

_MAX_REPLAY_BYTES = 64 * 1024 * 1024
_MAX_REPLAY_ROW_BYTES = 1024 * 1024
_MAX_RENDER_BYTES = 32 * 1024 * 1024


def _payload_budget(value: Any, used: int) -> int:
    encoder = json.JSONEncoder(ensure_ascii=False, allow_nan=False)
    for chunk in encoder.iterencode(value):
        used += len(chunk.encode("utf-8"))
        if used > _MAX_RENDER_BYTES:
            raise ValueError(f"Combined renderer payload exceeds {_MAX_RENDER_BYTES} byte budget")
    return used


def _check_replay(value: Any, depth: int = 0) -> None:
    if depth > 64:
        raise ValueError("Dashboard replay record is nested too deeply or cyclic")
    if isinstance(value, Mapping):
        if len(value) > 1024:
            raise ValueError("Record exceeds 1024 fields")
        for key, child in value.items():
            if not isinstance(key, str) or not key:
                raise ValueError("Record field names must be non-empty strings")
            _check_replay(key, depth + 1)
            _check_replay(child, depth + 1)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _check_replay(child, depth + 1)
    elif isinstance(value, str) and len(value) > _MAX_REPLAY_ROW_BYTES:
        raise ValueError(f"Dashboard replay record exceeds {_MAX_REPLAY_ROW_BYTES} bytes")


def _replay_scalar(value: Any) -> Any:
    """Match supported input scalars without turning numeric types into text."""
    if isinstance(value, Integral):
        return int(value)
    if isinstance(value, (Real, Decimal)):
        return float(value)
    if isinstance(value, (date, datetime, time)):
        return value.isoformat()
    if isinstance(value, Mapping):
        return dict(value)
    if type(value).__module__.split(".", 1)[0] == "numpy" and hasattr(value, "item"):
        return value.item()
    raise TypeError(f"Unsupported record value: {type(value).__name__}")


def render(
    data: Any,
    spec: ChartSpec | dict,
    engine: str = "matplotlib",
    output_dir: str | Path | None = None,
) -> Artifact:
    """Render a bounded chart into a fresh directory, never replacing user files.

    A dashboard spools one-shot iterators once to temporary JSONL on disk. Each
    child then applies its own mapping/reducer to that file in bounded memory.
    Replay rejects records over 1 MiB or a total source over 64 MiB of UTF-8 JSONL.
    Combined retained records/specs and native payloads are limited to 32 MiB;
    engine geometry, image buffers and escaped HTML have additional overhead.
    Expanded tables across all children are preflighted at 10,000 cells including
    headers and 16 MiB estimated bytes before native/HTML allocation. The latter
    is a conservative serialization allowance, not an OS-memory/file-size limit.
    Browser artifacts use pinned CDN libraries except self-contained Plotly.
    """
    if engine not in ENGINES:
        raise ValueError(f"Unknown engine {engine!r}; choose from {', '.join(ENGINES)}")
    chart = spec if isinstance(spec, ChartSpec) else ChartSpec.model_validate(spec)
    from .normalize import normalize

    specs = [chart]
    if chart.kind == "dashboard":
        specs = []
        columns = min(chart.columns, len(chart.charts))
        rows = math.ceil(len(chart.charts) / columns)
        for child in chart.charts:
            inherited = {key: getattr(chart, key) for key in (
                "x", "y", "color", "size", "data_path", "format", "aggregation", "max_points", "theme"
            ) if key not in child.model_fields_set}
            if "width" not in child.model_fields_set:
                inherited["width"] = max(240, (chart.width - 20 * (columns - 1)) // columns)
            if "height" not in child.model_fields_set:
                inherited["height"] = max(200, (chart.height - 60 - 20 * (rows - 1)) // rows)
            specs.append(child.model_copy(update=inherited))
    payload_bytes = 0
    with tempfile.TemporaryDirectory(prefix="deepviz-input-") as scratch:
        source = data
        spooled = chart.kind == "dashboard" and isinstance(data, Iterator)
        if spooled:
            source = Path(scratch) / "source.jsonl"
            encoder = json.JSONEncoder(ensure_ascii=False, default=_replay_scalar)
            total_bytes = 0
            with source.open("wb") as stream:
                for row in data:
                    _check_replay(row)
                    row_bytes = 1
                    for chunk in encoder.iterencode(row):
                        encoded = chunk.encode("utf-8")
                        row_bytes += len(encoded)
                        total_bytes += len(encoded)
                        if row_bytes > _MAX_REPLAY_ROW_BYTES:
                            raise ValueError(f"Dashboard replay record exceeds {_MAX_REPLAY_ROW_BYTES} bytes")
                        if total_bytes + 1 > _MAX_REPLAY_BYTES:
                            raise ValueError(f"Dashboard replay exceeds {_MAX_REPLAY_BYTES} byte source budget")
                        stream.write(encoded)
                    stream.write(b"\n")
                    total_bytes += 1
        normalized = []
        for child in specs:
            payload_bytes = _payload_budget(child.model_dump(), payload_bytes)
            if spooled:
                # Own the replay handle even when validation leaves a generator in its traceback.
                with source.open(encoding="utf-8") as replay:
                    result = normalize(replay, child.model_copy(update={"format": "jsonl"}))
            else:
                result = normalize(source, child)
            payload_bytes = _payload_budget(result.records, payload_bytes)
            normalized.append(result)
    _table_budget([result.records for result in normalized])
    warnings = [message for result in normalized for message in result.warnings]
    payloads = []
    charts: list[dict[str, Any]] = []
    for result, child in zip(normalized, specs, strict=True):
        actual_kind: str = child.kind
        if engine != "matplotlib":
            native, notes, actual_kind = native_spec(engine, result.records, child)
            payload_bytes = _payload_budget(native, payload_bytes)
            payloads.append(native)
        else:
            _, notes = _fallback(engine, child.kind)
            _, geometry_notes = _geometry(channels(result.records, child), child)
            notes.extend(geometry_notes)
        if engine == "vega" and chart.kind == "dashboard" and child.theme != chart.theme:
            notes.append("vega dashboard theme fallback: the composed export uses the parent theme; "
                         "standalone native child specifications retain their requested theme.")
        warnings.extend(notes)
        charts.append({"engine": engine, "requested_kind": child.kind, "rendered_kind": actual_kind,
                       "spec": child.model_dump(), "records": result.records, "input_count": result.input_count,
                       "output_count": len(result.records), "strategy": result.strategy,
                       "warnings": result.warnings + notes})
    if engine in {"echarts", "antv"}:
        network_warning = "HTML requires network access to load its exact-version pinned browser library from jsDelivr."
        warnings.append(network_warning)
        for info in charts:
            info["warnings"].append(network_warning)
    root = Path(output_dir) if output_dir is not None else Path(tempfile.gettempdir()) / "deepviz"
    root.mkdir(parents=True, exist_ok=True)
    folder = Path(tempfile.mkdtemp(prefix="deepviz-", dir=root))
    paths = []
    if engine == "matplotlib":
        fig, notes = matplotlib_figure([(n.records, child) for n, child in zip(normalized, specs, strict=True)],
                                       chart if chart.kind == "dashboard" else None)
        warnings.extend(notes)
        try:
            for extension in ["png", "svg"]:
                path = folder / f"chart.{extension}"
                fig.savefig(path, facecolor=fig.get_facecolor())
                paths.append(str(path.resolve()))
        finally:
            fig.clear()
        mime = "image/png"
    elif engine == "vega":
        import vl_convert as vlc
        payload = payloads[0]
        if chart.kind == "dashboard":
            child_payloads = []
            for native, result, child in zip(payloads, normalized, specs, strict=True):
                if child.theme != chart.theme:
                    native = native_spec(engine, result.records, child.model_copy(update={"theme": chart.theme}))[0]
                child_payloads.append({key: value for key, value in native.items()
                                       if key not in {"$schema", "config", "background"}})
            payload = {"$schema": "https://vega.github.io/schema/vega-lite/v5.json", "concat": child_payloads,
                       "columns": chart.columns, "title": chart.title, "background": _colors(chart)[0],
                       "config": {"axis": {"labelColor": _colors(chart)[1], "titleColor": _colors(chart)[1]},
                                  "title": {"color": _colors(chart)[1]},
                                  "legend": {"labelColor": _colors(chart)[1], "titleColor": _colors(chart)[1]}},
                       "resolve": {"scale": {"color": "independent"}}}
        svg = vlc.vegalite_to_svg(payload)
        root_svg = ET.fromstring(svg)
        root_svg.set("width", str(chart.width))
        root_svg.set("height", str(chart.height))
        ET.register_namespace("", "http://www.w3.org/2000/svg")
        svg = ET.tostring(root_svg, encoding="unicode")
        path = folder / "chart.svg"
        path.write_text(svg, encoding="utf-8")
        paths.append(str(path.resolve()))
        mime = "image/svg+xml"
    else:
        path = folder / "chart.html"
        path.write_text(browser_html(engine, payloads, specs, chart, metadata=charts), encoding="utf-8")
        paths.append(str(path.resolve()))
        mime = "text/html"
    if engine in {"matplotlib", "vega"}:
        path = folder / "chart.html"
        path.write_text(browser_html(engine, [], specs, chart, metadata=charts, image="chart.svg"), encoding="utf-8")
        paths.append(str(path.resolve()))
    strategy = normalized[0].strategy if len(normalized) == 1 else "dashboard:" + ",".join(n.strategy for n in normalized)
    manifest_warnings = list(dict.fromkeys(warnings))
    manifest = {"engine": engine, "charts": charts, "warnings": manifest_warnings,
                "native_specs": payloads, "strategy": strategy, "accessible_path": "chart.html"}
    metadata = folder / "manifest.json"
    metadata.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    paths.append(str(metadata.resolve()))
    return Artifact(paths=paths, mime_type=mime, engine=engine,
                    input_count=max(n.input_count for n in normalized),
                    output_count=sum(len(n.records) for n in normalized), strategy=strategy,
                    warnings=manifest_warnings)
