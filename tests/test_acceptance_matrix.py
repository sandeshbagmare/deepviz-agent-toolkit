"""Independent acceptance contracts; no implementation mocks or optional-dependency skips.

The 900 primary cases cross five actual ingestion adapters, 18 chart kinds,
five independently selected engines and two themes. One failing assertion can
affect many cells: case counts are never defect or issue counts.
"""

from __future__ import annotations

import copy
import csv
import importlib
import io
import json
import math
import re
import socket
from collections import Counter
from collections.abc import Iterator
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, get_args
from xml.etree import ElementTree as ET

import pytest

from deepviz.models import Artifact, ChartKind, ChartSpec, NormalizedData

FIXTURES = Path(__file__).parent / "fixtures" / "acceptance"
ENGINES = ("matplotlib", "plotly", "vega", "echarts", "antv")
KINDS = get_args(ChartKind)
THEMES = ("light", "dark")
PRIMARY_FORMS = ("records", "nested_json", "graphql", "columns", "csv")
OTHER_FORMS = ("tsv", "jsonl", "generator")
TITLE = 'Acceptance Ω & <img src=x onerror="bad()"> </title></script><script>window.__DV_XSS__=1</script>'
MAX_ARTIFACT_BYTES = 12_000_000  # Allows bundled Plotly, not unbounded raw input.


@pytest.fixture
def records() -> list[dict[str, Any]]:
    return json.loads((FIXTURES / "measurements.json").read_text(encoding="utf-8"))


def normalize(data: Any, spec: ChartSpec) -> NormalizedData:
    """Import lazily so a missing implementation is an explicit test failure."""
    return importlib.import_module("deepviz.normalize").normalize(data, spec)


def render(data: Any, spec: ChartSpec, engine: str, output_dir: Path) -> Artifact:
    return importlib.import_module("deepviz.render").render(
        data, spec, engine=engine, output_dir=output_dir,
    )


def chart_spec(kind: str, theme: str = "light", **overrides: Any) -> ChartSpec:
    fields: dict[str, Any] = {
        "kind": kind, "title": TITLE, "theme": theme,
        "x": "category", "y": "y", "size": "size",
        "max_points": 10, "aggregation": "none", "width": 640, "height": 400,
    }
    if kind in {"line", "scatter", "area", "bubble", "heatmap"}:
        fields["x"] = "x"
    if kind == "geo":
        fields.update(x="longitude", y="latitude")
    if kind == "dashboard":
        fields["charts"] = [
            {"kind": "bar", "x": "category", "y": "y", "title": "Categories"},
            {"kind": "scatter", "x": "x", "y": "y", "title": "Relationship"},
        ]
    fields.update(overrides)
    return ChartSpec(**fields)


def source_spec(spec: ChartSpec, **options: Any) -> ChartSpec:
    """Apply the declared source adapter to the parent and each dashboard child."""
    updates = dict(options)
    if spec.kind == "dashboard":
        updates["charts"] = [child.model_copy(update=options) for child in spec.charts]
    return spec.model_copy(update=updates)


def encode_input(
    form: str, rows: list[dict[str, Any]], spec: ChartSpec,
) -> tuple[Any, ChartSpec]:
    if form == "records":
        return copy.deepcopy(rows), spec
    if form == "nested_json":
        return {"payload": {"measurements": copy.deepcopy(rows)}}, source_spec(
            spec, data_path="payload.measurements",
        )
    if form == "graphql":
        return {"data": {"measurements": {"edges": [{"node": row} for row in rows]}}}, spec
    if form == "columns":
        return {key: [row[key] for row in rows] for key in rows[0]}, spec
    if form in {"csv", "tsv"}:
        output = io.StringIO(newline="")
        writer = csv.DictWriter(output, fieldnames=list(rows[0]), delimiter="," if form == "csv" else "\t")
        writer.writeheader()
        writer.writerows(rows)
        return output.getvalue(), source_spec(spec, format=form)
    if form == "jsonl":
        return "\n".join(json.dumps(row) for row in rows), source_spec(spec, format="jsonl")
    if form == "generator":
        return (copy.deepcopy(row) for row in rows), spec
    raise AssertionError(f"Unknown fixture adapter: {form}")


class ArtifactHTML(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_title = False
        self.title: list[str] = []
        self.script_bodies: list[str] = []
        self.script_attributes: list[dict[str, str | None]] = []
        self.in_script = False
        self.tags: list[tuple[str, dict[str, str | None]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append((tag, dict(attrs)))
        self.in_title = self.in_title or tag == "title"
        if tag == "script":
            self.in_script = True
            self.script_bodies.append("")
            self.script_attributes.append(dict(attrs))

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        if tag == "script":
            self.in_script = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title.append(data)
        if self.in_script:
            self.script_bodies[-1] += data


def json_candidates(text: str) -> Iterator[Any]:
    """Read JSON, never evaluate JavaScript. Limit scanning of bundled libraries."""
    decoder = json.JSONDecoder()
    for marker in ("Plotly.newPlot(", "vegaEmbed(", "echarts.init(", "new G2.Chart(", "new Chart("):
        position = text.rfind(marker)
        if position >= 0:
            # Configuration is usually immediately before/after the bootstrap.
            text = text[max(0, position - 50_000):position + 100_000]
            break
    for match in re.finditer(r"[\[{]", text):
        try:
            result, _ = decoder.raw_decode(text, match.start())
        except (ValueError, RecursionError):
            continue
        yield result


def walk(value: Any) -> Iterator[Any]:
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def has_values(value: Any) -> bool:
    return any(
        isinstance(item, list) and bool(item)
        and any(isinstance(child, (str, int, float, dict, list)) for child in item)
        for item in walk(value)
    )


def assert_browser_semantics(
    engine: str, html: str, candidates: list[Any], spec: ChartSpec, warnings: list[str],
) -> None:
    """A metadata-only HTML page is not a successful renderer artifact."""
    scripts = ArtifactHTML()
    scripts.feed(html)
    assert "".join(scripts.title) == spec.title, "Artifact title is missing, corrupted, or unescaped"
    assert not any(
        name.lower().startswith("on") for _, attrs in scripts.tags for name in attrs
    ), "Untrusted content became an executable HTML attribute"
    assert not any(re.match(r"\s*window\.__DV_XSS__\s*=", body) for body in scripts.script_bodies), (
        "Unescaped closing script tag created executable user content"
    )
    js = "\n".join(scripts.script_bodies)
    embedded = [json.loads(body) for attrs, body in zip(
        scripts.script_attributes, scripts.script_bodies, strict=True,
    ) if attrs.get("id") == "deepviz-data" and attrs.get("type") == "application/json"]
    assert len(embedded) == 1, "Missing or ambiguous inert native chart payload"
    payloads = embedded[0]
    assert isinstance(payloads, list) and payloads and all(isinstance(value, dict) for value in payloads)
    manifests = [item for item in candidates if isinstance(item, dict) and "native_specs" in item]
    assert len(manifests) == 1 and payloads == manifests[0]["native_specs"], (
        "Manifest and the configuration actually bootstrapped in HTML differ"
    )
    assert len(payloads) == (len(spec.charts) if spec.kind == "dashboard" else 1)
    # Read the exact inert script. Searching a 5 MB bundled runtime for the
    # bootstrap cannot find the JSON that occurs before the runtime library.
    if engine == "plotly":
        assert "Plotly.newPlot(" in js or "Plotly.react(" in js
        assert all(
            isinstance(payload.get("data"), list) and payload["data"]
            and all(trace.get("type") and has_values(trace) for trace in payload["data"])
            for payload in payloads
        ), "Plotly has no populated native trace configuration"
    elif engine == "vega":
        assert "vegaEmbed(" in js
        assert any(
            isinstance(value, dict) and "$schema" in value
            and any(key in value for key in ("mark", "layer", "hconcat", "vconcat", "concat"))
            and has_values(value)
            for value in candidates
        ), "Vega has no populated declarative marks/data"
    elif engine == "echarts":
        assert "echarts.init(" in js and ".setOption(" in js
        assert all(
            (isinstance(value.get("series"), list) and value["series"] and has_values(value["series"]))
            or (spec.kind == "table" and value.get("graphic")
                and all(mark.get("type") == "text" and "text" in mark.get("style", {})
                        for mark in value["graphic"]))
            for value in payloads
        ), "ECharts has no populated native series"
    elif engine == "antv":
        assert re.search(r"new\s+(?:G2\.)?Chart\s*\(", js) and ".render(" in js
        assert any(
            isinstance(value, dict) and any(key in value for key in ("type", "children"))
            and has_values(value)
            for value in payloads
        ), "AntV has no populated native mark/data configuration"
    else:
        raise AssertionError(f"Unexpected browser engine: {engine}")

    native_types = {
        item["type"]
        for candidate in payloads for item in walk(candidate)
        if isinstance(item, dict) and isinstance(item.get("type"), str)
    }
    native_types.update(
        item["mark"]
        for candidate in payloads for item in walk(candidate)
        if isinstance(item, dict) and isinstance(item.get("mark"), str)
    )
    expected = {
        "bar": {"bar", "interval"}, "line": {"line", "scatter"},
        "scatter": {"scatter", "point"}, "area": {"area", "scatter", "line"},
        "pie": {"pie", "arc", "interval"}, "heatmap": {"heatmap", "rect", "cell"},
        "histogram": {"histogram", "bar", "interval"}, "box": {"box", "boxplot"},
        "violin": {"violin"}, "bubble": {"scatter", "point"},
        "radar": {"radar", "scatterpolar"}, "treemap": {"treemap"},
        "sunburst": {"sunburst"}, "funnel": {"funnel", "interval"},
        "gauge": {"gauge", "indicator"}, "geo": {"scattergeo", "geoshape", "point", "scatter"},
        "table": {"table"}, "dashboard": set(),
    }[spec.kind]
    supported = spec.kind == "dashboard" or bool(native_types & expected)
    if engine == "plotly" and spec.kind == "heatmap":
        # Sparse square symbols are a legitimate bounded heatmap; require the
        # quantitative colors and square geometry rather than any scatter.
        traces = payloads[0]["data"]
        supported = all(trace.get("type") == "scatter" and trace.get("mode") == "markers"
                        and trace.get("marker", {}).get("symbol") == "square"
                        and trace["marker"].get("colorscale")
                        and len(trace["marker"].get("color", [])) == len(trace.get("x", []))
                        for trace in traces)
    if engine == "echarts" and spec.kind == "table":
        supported = bool(payloads[0].get("graphic"))
    if engine == "antv" and spec.kind in {"radar", "treemap", "sunburst", "gauge", "table"}:
        payload = payloads[0]
        coordinate = payload.get("coordinate", {})
        encoding = payload.get("encode", {})
        data = payload.get("data", [])
        transforms = {item.get("type") for item in payload.get("transform", [])}
        if spec.kind == "radar":
            supported = payload.get("type") == "line" and coordinate.get("type") == "polar"
            supported = supported and len(data) > 1 and data[0] == data[-1]
        elif spec.kind == "treemap":
            supported = payload.get("type") == "rect" and all(
                isinstance(encoding.get(key), list) and len(encoding[key]) == 2 for key in ("x", "y")
            )
            assert supported and data
            assert all(row[encoding["x"][1]] > row[encoding["x"][0]]
                       and row[encoding["y"][1]] > row[encoding["y"][0]] for row in data)
            assert sum((row[encoding["x"][1]] - row[encoding["x"][0]])
                       * (row[encoding["y"][1]] - row[encoding["y"][0]]) for row in data) == pytest.approx(1)
        elif spec.kind in {"sunburst", "gauge"}:
            supported = payload.get("type") == "interval" and coordinate.get("type") == "theta"
            supported = supported and coordinate.get("innerRadius", 0) > 0 and "stackY" in transforms
            if spec.kind == "gauge":
                supported = supported and len(data) == 2 and sum(row[encoding["y"]] for row in data) == 100
                supported = supported and coordinate.get("endAngle") == 0
                supported = supported and coordinate.get("startAngle") == pytest.approx(-math.pi)
        else:
            supported = payload.get("type") == "text" and bool(data) and "text" in encoding
    disclosed = any(
        spec.kind in warning.lower()
        and any(word in warning.lower() for word in ("fallback", "unsupported", "not supported"))
        for warning in warnings
    )
    assert supported or disclosed, (
        f"{engine} silently substituted {native_types!r} for {spec.kind}; fallback must be explicit"
    )


def assert_svg_semantics(svg: str, engine: str, title: str) -> None:
    root = ET.fromstring(svg)
    assert root.tag == "{http://www.w3.org/2000/svg}svg"
    assert not any(node.tag.rsplit("}", 1)[-1] in {"script", "foreignObject"} for node in root.iter())
    assert not any(
        attribute.rsplit("}", 1)[-1].lower().startswith("on")
        for node in root.iter() for attribute in node.attrib
    ), "SVG contains an executable event attribute"
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    full_root = ET.fromstring(svg, parser=parser)
    for node in full_root.iter():
        if node.tag is ET.Comment and node.text:
            # Matplotlib entity-escapes comment text; XML parsers deliberately
            # do not resolve entities inside comments as they do in <text>.
            node.text = unescape(node.text)
    # Matplotlib exports wrapped visible title lines as separate SVG comments.
    # textwrap may insert a newline inside a long token; no non-whitespace title
    # character may be lost, altered, or supplied only by an unrelated manifest.
    visible = re.sub(r"\s+", "", "".join(full_root.itertext()))
    assert re.sub(r"\s+", "", title) in visible, "SVG does not preserve the escaped chart title"
    mark_tags = {"path", "rect", "circle", "polygon", "image", "text", "use"}
    marks = [node for node in root.iter() if node.tag.rsplit("}", 1)[-1] in mark_tags]
    assert len(marks) >= 4, "SVG contains no meaningful visual marks"
    if engine == "vega":
        # Vega's compiled data-mark group, not a hand-written metadata-only SVG.
        data_groups = [node for node in root.iter() if "role-mark" in node.attrib.get("class", "").split()]
        assert data_groups and any(
            child.tag.rsplit("}", 1)[-1] in mark_tags for group in data_groups for child in group.iter()
        ), "Vega SVG has no populated compiled data-mark group"


def assert_vega_spec_semantics(candidates: list[Any], title: str) -> None:
    vega_specs = [
        item for candidate in candidates for item in walk(candidate)
        if isinstance(item, dict) and "vega" in str(item.get("$schema", "")).lower()
    ]
    for payload in vega_specs:
        assert has_values(payload), "Vega spec sidecar contains no data"
        import vl_convert

        if "vega-lite" in payload["$schema"]:
            compiled = vl_convert.vegalite_to_svg(payload)
        else:
            compiled = vl_convert.vega_to_svg(payload)
        assert_svg_semantics(compiled, "vega", title)


def assert_native_xy_values(engine: str, payload: dict, chart: dict) -> None:
    """Check actual numeric payloads, not merely native mark names or metadata."""
    spec = ChartSpec(**chart["spec"])
    if spec.kind not in {"bar", "line", "area", "scatter", "bubble", "geo"}:
        return
    rows = chart["records"]
    expected = [(row[spec.x], float(row[spec.y])) for row in rows]
    pairs = []
    if engine == "plotly":
        pairs = [pair for trace in payload["data"] for pair in zip(trace["x"], trace["y"], strict=True)]
    elif engine == "vega":
        fields = [payload["encoding"][key]["field"] for key in ("x", "y")]
        pairs = [(row[fields[0]], row[fields[1]]) for row in payload["data"]["values"]]
    elif engine == "echarts":
        pairs = [tuple((point["value"] if isinstance(point, dict) else point)[:2])
                 for series in payload["series"] for point in series["data"]]
        # ECharts category axes intentionally stringify numeric bar/line labels.
        if spec.kind in {"bar", "line", "area"}:
            expected = [(str(x), y) for x, y in expected]
    elif engine == "antv":
        children = [child for child in payload.get("children", []) if child.get("type") == spec.kind]
        for mark in children or [payload]:
            encoding = mark["encode"]
            pairs.extend((row[encoding["x"]], row[encoding["y"]]) for row in mark["data"])
    assert Counter(pairs) == Counter(expected), "Native visible coordinates changed a mapped observation"


def assert_aggregate_values(actual: dict, expected: dict, aggregation: str) -> None:
    assert actual.keys() == expected.keys()
    if aggregation == "mean":
        # Streaming means and sum/n differ by ordinary binary rounding. The
        # 1e-12 bound is on the actual small result, never on large operands.
        assert actual == pytest.approx(expected, rel=1e-12, abs=1e-12)
    else:
        assert actual == expected
        if aggregation == "count":
            assert all(type(value) is int for value in actual.values())


def assert_artifact(artifact: Artifact, engine: str, spec: ChartSpec, directory: Path, count: int) -> None:
    assert isinstance(artifact, Artifact)
    assert isinstance(artifact.warnings, list) and all(isinstance(w, str) for w in artifact.warnings)
    actual_engine = artifact.engine
    assert actual_engine in ENGINES, "Unknown actual renderer identity"
    if actual_engine != engine:
        assert any(
            spec.kind in warning.lower() and actual_engine in warning.lower()
            and "fallback" in warning.lower()
            for warning in artifact.warnings
        ), "A different backend requires explicit requested-kind and actual-backend fallback disclosure"
    assert artifact.input_count == count, "Input count must describe source rows, not per-panel copies"
    expected_output_counts = {count}
    if spec.kind == "dashboard":
        expected_output_counts.add(count * len(spec.charts))
    assert artifact.output_count in expected_output_counts, (
        "Unreduced output must account for source rows or all dashboard child row contributions"
    )
    assert artifact.strategy and isinstance(artifact.strategy, str)
    assert artifact.paths and len(artifact.paths) <= 8
    paths = [Path(path).resolve() for path in artifact.paths]
    assert len(paths) == len(set(paths)), "Duplicate artifact path"
    for path in paths:
        assert path.is_relative_to(directory.resolve()), "Artifact escaped its output directory"
        assert path.is_file() and 0 < path.stat().st_size < MAX_ARTIFACT_BYTES
    candidates: list[Any] = []
    for path in paths:
        if path.suffix == ".json":
            payload = json.loads(path.read_text(encoding="utf-8"))
            candidates.append(payload)
            if actual_engine == "vega" and (
                "spec" in path.stem.lower() or path.name.endswith((".vl.json", ".vg.json"))
            ):
                assert any(
                    isinstance(item, dict) and "vega" in str(item.get("$schema", "")).lower()
                    for item in walk(payload)
                ), "Vega spec sidecar is not a native Vega/Vega-Lite specification"
    manifests = [candidate for candidate in candidates if isinstance(candidate, dict) and "native_specs" in candidate]
    assert len(manifests) == 1
    manifest = manifests[0]
    if actual_engine != "matplotlib":
        assert len(manifest["native_specs"]) == len(manifest["charts"])
        for payload, child in zip(manifest["native_specs"], manifest["charts"], strict=True):
            assert_native_xy_values(actual_engine, payload, child)
    svg_paths = [path for path in paths if path.suffix == ".svg"]
    if actual_engine == "matplotlib" or (actual_engine == "vega" and svg_paths):
        png_paths = [path for path in paths if path.suffix == ".png"]
        assert svg_paths or png_paths, "Static engine must produce a native rendered image"
        for path in svg_paths:
            assert_svg_semantics(path.read_text(encoding="utf-8"), actual_engine, spec.title)
        for path in png_paths:
            from PIL import Image, ImageStat

            with Image.open(path) as image:
                assert image.width >= 240 and image.height >= 200
                assert max(ImageStat.Stat(image.convert("RGB")).var) > 1.0, "Blank PNG"
        assert "image/" in artifact.mime_type
    else:
        html_paths = [path for path in paths if path.suffix in {".html", ".htm"}]
        assert html_paths and artifact.mime_type == "text/html"
        html = html_paths[0].read_text(encoding="utf-8")
        assert_browser_semantics(actual_engine, html, candidates, spec, artifact.warnings)
    if actual_engine == "vega":
        assert_vega_spec_semantics(candidates, spec.title)


@pytest.mark.parametrize("form", PRIMARY_FORMS)
@pytest.mark.parametrize("theme", THEMES)
@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize("engine", ENGINES)
def test_engine_kind_theme_source_acceptance(
    engine: str, kind: str, theme: str, form: str,
    records: list[dict[str, Any]], tmp_path: Path,
) -> None:
    spec = chart_spec(kind, theme)
    data, spec = encode_input(form, records, spec)
    artifact = render(data, spec, engine, tmp_path)
    assert_artifact(artifact, engine, spec, tmp_path, len(records))


@pytest.mark.parametrize("form", OTHER_FORMS)
@pytest.mark.parametrize("theme", THEMES)
@pytest.mark.parametrize("engine", ENGINES)
def test_remaining_text_and_stream_sources_render(
    engine: str, theme: str, form: str, records: list[dict[str, Any]], tmp_path: Path,
) -> None:
    data, spec = encode_input(form, records, chart_spec("bar", theme))
    assert_artifact(render(data, spec, engine, tmp_path), engine, spec, tmp_path, len(records))


@pytest.mark.parametrize("form", PRIMARY_FORMS + OTHER_FORMS)
@pytest.mark.parametrize("kind", KINDS)
def test_low_n_normalization_preserves_every_numeric_value(
    form: str, kind: str, records: list[dict[str, Any]],
) -> None:
    original = copy.deepcopy(records)
    data, spec = encode_input(form, records, chart_spec(kind))
    normalized = normalize(data, spec)
    assert isinstance(normalized, NormalizedData)
    assert normalized.input_count == len(records)
    assert len(normalized.records) == len(records)
    assert [float(row["y"]) for row in normalized.records] == [row["y"] for row in records]
    assert [float(row["size"]) for row in normalized.records] == [row["size"] for row in records]
    assert [row["category"] for row in normalized.records] == [row["category"] for row in records]
    assert records == original, "Normalization mutated caller-owned records"


@pytest.mark.parametrize("aggregation", ("sum", "mean", "count", "min", "max"))
@pytest.mark.parametrize("form", PRIMARY_FORMS + OTHER_FORMS)
def test_aggregations_match_independent_exact_totals(aggregation: str, form: str) -> None:
    rows = [{"category": f"group-{i % 3}", "y": (i % 11) - 5} for i in range(101)]
    data, spec = encode_input(form, rows, chart_spec("bar", aggregation=aggregation, size=None))
    normalized = normalize(data, spec)
    assert normalized.input_count == 101
    assert len(normalized.records) == 3
    actual = {row["category"]: row["y"] for row in normalized.records}
    expected: dict[str, float] = {}
    for group in range(3):
        values = [row["y"] for row in rows if row["category"] == f"group-{group}"]
        if aggregation == "sum":
            result = sum(values)
        elif aggregation == "mean":
            result = sum(values) / len(values)
        elif aggregation == "count":
            result = len(values)
        elif aggregation == "min":
            result = min(values)
        else:
            result = max(values)
        expected[f"group-{group}"] = result
    assert_aggregate_values(actual, expected, aggregation)
    assert normalized.strategy != "none"


@pytest.mark.parametrize("kind", ("scatter", "line", "bubble"))
@pytest.mark.parametrize("count", (11, 101, 1001))
def test_sampling_uses_real_observations_and_reports_loss(kind: str, count: int) -> None:
    rows = [{"x": i, "y": i * 0.125 - 17.25, "size": i + 1} for i in range(count)]
    normalized = normalize((row for row in rows), chart_spec(kind, aggregation="sample"))
    assert normalized.input_count == count
    assert 0 < len(normalized.records) <= 10
    source = {(row["x"], row["y"], row["size"]) for row in rows}
    assert all((row["x"], row["y"], row["size"]) in source for row in normalized.records)
    assert normalized.strategy != "none" and normalized.warnings, "Loss must be disclosed"


@pytest.mark.parametrize("engine", ENGINES)
def test_artifact_names_never_overwrite_previous_outputs(
    engine: str, records: list[dict[str, Any]], tmp_path: Path,
) -> None:
    sentinel = tmp_path / "keep.txt"
    sentinel.write_text("not owned by DeepViz", encoding="utf-8")
    first = render(records, chart_spec("bar"), engine, tmp_path)
    saved = {Path(path): Path(path).read_bytes() for path in first.paths}
    second = render(records, chart_spec("bar"), engine, tmp_path)
    assert set(first.paths).isdisjoint(second.paths)
    assert all(path.read_bytes() == content for path, content in saved.items())
    assert sentinel.read_text(encoding="utf-8") == "not owned by DeepViz"


@pytest.mark.parametrize("bad_spec", [
    {"kind": "not-a-chart"}, {"kind": "dashboard"}, {"kind": "bar", "charts": [{"kind": "line"}]},
    {"kind": "dashboard", "charts": [{"kind": "dashboard", "charts": [{"kind": "bar"}]}]},
    {"max_points": 9}, {"max_points": 100001}, {"width": 239}, {"height": 199},
    {"theme": "invisible"}, {"format": "javascript"}, {"version": 2},
    {"expression": "__import__('os').system('whoami')"}, {"title": "x" * 501},
])
def test_malformed_or_executable_spec_is_rejected(bad_spec: dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        ChartSpec(**bad_spec)


@pytest.mark.parametrize("data,options", [
    ("{not json}", {"format": "json"}),
    ('{"x":1}\nnot json', {"format": "jsonl"}),
    ({"a": 1}, {"data_path": "missing.rows"}),
])
def test_malformed_or_remote_input_never_succeeds(data: Any, options: dict[str, Any]) -> None:
    with pytest.raises((ValueError, TypeError, OSError)):
        normalize(data, chart_spec("bar", **options))


def test_url_looking_data_is_never_fetched(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbid_network(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("A data string attempted network ingestion")

    for name in ("create_connection", "getaddrinfo"):
        monkeypatch.setattr(socket, name, forbid_network)
    monkeypatch.setattr(socket.socket, "connect", forbid_network)
    monkeypatch.setattr(socket.socket, "connect_ex", forbid_network)
    # An explicit CSV parser may accept a URL-looking string as a header with
    # zero rows; that is not a remote fetch. Rejection is equally safe.
    try:
        result = normalize("https://example.invalid/private.csv", chart_spec("bar", format="csv", size=None))
    except (ValueError, TypeError, OSError):
        return
    assert result.records == [] and result.input_count == 0


def test_nonfinite_numbers_never_reach_serialized_records() -> None:
    rows = [{"x": index, "y": value} for index, value in enumerate([1.5, math.nan, math.inf, -math.inf])]
    try:
        normalized = normalize(rows, chart_spec("scatter"))
    except ValueError:
        return  # Explicit rejection is safer than invalid engine JSON.
    json.dumps(normalized.records, allow_nan=False)
    assert normalized.input_count == 4
    assert normalized.warnings, "Sanitizing nonfinite input must not be silent"


def test_missing_mapped_field_is_not_silent_success() -> None:
    with pytest.raises((ValueError, KeyError)):
        normalize([{"unrelated": 1}], chart_spec("scatter", y="absent"))


def test_nested_field_mapping_does_not_lose_zero_or_negative_values() -> None:
    rows = [{"metric": {"time": i, "value": value}} for i, value in enumerate([0, -2.25, 0.125])]
    normalized = normalize(rows, chart_spec("line", x="metric.time", y="metric.value", size=None))
    assert normalized.input_count == 3
    assert [row["metric.value"] for row in normalized.records] == [0, -2.25, 0.125]


def test_graphql_page_list_preserves_every_edge(records: list[dict[str, Any]]) -> None:
    pages = [
        {"data": {"measurements": {"edges": [{"cursor": str(i), "node": row} for i, row in enumerate(part)]}}}
        for part in (records[:2], records[2:])
    ]
    normalized = normalize(pages, chart_spec("bar"))
    assert normalized.input_count == len(records)
    assert [row["y"] for row in normalized.records] == [row["y"] for row in records]
