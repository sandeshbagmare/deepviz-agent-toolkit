"""Public rendering boundary: validate, normalize bounded data, then render."""
from __future__ import annotations

import json
import math
import tempfile
import xml.etree.ElementTree as ET
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from .engines import ENGINES, _colors, _fallback, browser_html, matplotlib_figure, native_spec
from .models import Artifact, ChartSpec


def render(
    data: Any,
    spec: ChartSpec | dict,
    engine: str = "matplotlib",
    output_dir: str | Path | None = None,
) -> Artifact:
    """Render a bounded chart into a fresh directory, never replacing user files.

    A dashboard spools one-shot iterators once to temporary JSONL on disk. Each
    child then applies its own mapping/reducer to that file in bounded memory.
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
    with tempfile.TemporaryDirectory(prefix="deepviz-input-") as scratch:
        source = data
        spooled = chart.kind == "dashboard" and isinstance(data, Iterator)
        if spooled:
            source = Path(scratch) / "source.jsonl"
            with source.open("w", encoding="utf-8") as stream:
                for row in data:
                    stream.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
        normalized = [normalize(source, child.model_copy(update={"format": "jsonl"}) if spooled else child)
                      for child in specs]
    warnings = [message for result in normalized for message in result.warnings]
    payloads = []
    charts = []
    for result, child in zip(normalized, specs, strict=True):
        actual_kind = child.kind
        if engine != "matplotlib":
            native, notes, actual_kind = native_spec(engine, result.records, child)
            payloads.append(native)
            warnings.extend(notes)
        else:
            _, notes = _fallback(engine, child.kind)
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
            payload = {"$schema": "https://vega.github.io/schema/vega-lite/v5.json", "concat": payloads,
                       "columns": chart.columns, "title": chart.title, "background": _colors(chart)[0],
                       "config": {"axis": {"labelColor": _colors(chart)[1], "titleColor": _colors(chart)[1]},
                                  "title": {"color": _colors(chart)[1]},
                                  "legend": {"labelColor": _colors(chart)[1], "titleColor": _colors(chart)[1]}},
                       "resolve": {"scale": {"color": "independent"}}}
            for child_payload in payloads:
                child_payload.pop("$schema", None)
                child_payload.pop("config", None)
                child_payload.pop("background", None)
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
    manifest = {"engine": engine, "charts": charts, "warnings": list(dict.fromkeys(warnings)),
                "native_specs": payloads, "strategy": strategy, "accessible_path": "chart.html"}
    metadata = folder / "manifest.json"
    metadata.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    paths.append(str(metadata.resolve()))
    return Artifact(paths=paths, mime_type=mime, engine=engine,
                    input_count=max(n.input_count for n in normalized),
                    output_count=sum(len(n.records) for n in normalized), strategy=strategy,
                    warnings=manifest["warnings"])
