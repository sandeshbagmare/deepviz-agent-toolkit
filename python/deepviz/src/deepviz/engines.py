"""Independent chart adapters; schemas contain data, never executable callbacks.

Flat records describe one hierarchy level for treemap/sunburst. Geographic charts
use longitude=x and latitude=y; offline coordinate plots do not invent a basemap.
Vega-Lite lacks hierarchy/radar/gauge layouts: its explicit fallbacks are recorded
in the artifact manifest, not silently advertised as those native marks.
"""
from __future__ import annotations

import json
import math
import textwrap
from collections import defaultdict
from datetime import UTC, datetime
from html import escape
from importlib.resources import files
from typing import Any, overload

import numpy as np

from .models import ChartSpec

ENGINES = ("matplotlib", "plotly", "vega", "echarts", "antv")
PALETTE = ["#386cb0", "#b85c00", "#2a9d73", "#c44964", "#8861a9", "#a67c42"]
MARKERS = ["o", "s", "^", "D", "v", "P", "X", "*"]
LINESTYLES = ["-", "--", "-.", ":"]
DASHES = [[], [6, 3], [2, 2], [6, 2, 2, 2], [10, 2], [2, 4], [8, 2, 2, 2, 2, 2], [10, 3, 1, 3]]
ECHARTS_URL = "https://cdn.jsdelivr.net/npm/echarts@6.1.0/dist/echarts.min.js"
ANTV_URL = "https://cdn.jsdelivr.net/npm/@antv/g2@5.4.8/dist/g2.min.js"
_MAX_TABLE_CELLS = 10_000
_MAX_TABLE_BYTES = 16 * 1024 * 1024


def _table_budget(tables: list[list[dict]]) -> None:
    """Bound expanded header/body cells before allocating native or HTML tables.

    Across the request, reserve 256 structural bytes per cell plus six bytes per
    UTF-8 text byte. Column names may be repeated for every native text mark.
    This conservative planning allowance is not an RSS or final-file-size bound.
    Scan only existing keys/values, never the dense row-by-column product.
    """
    cells = estimated_bytes = 0
    for records in tables:
        columns: set[str] = set()
        for row in records:
            for key in row:
                columns.add(key)
                if cells + (len(records) + 1) * len(columns) > _MAX_TABLE_CELLS:
                    raise ValueError(f"Dense table exceeds {_MAX_TABLE_CELLS} cell budget (including headers)")
        table_cells = (len(records) + 1) * len(columns)
        cells += table_cells
        estimated_bytes += table_cells * 256
        for key in columns:
            estimated_bytes += 6 * len(key.encode("utf-8")) * (len(records) + 1)
            if estimated_bytes > _MAX_TABLE_BYTES:
                raise ValueError(f"Dense table exceeds {_MAX_TABLE_BYTES} estimated byte budget")
        for row in records:
            for value in row.values():
                estimated_bytes += 6 * len(str(value).encode("utf-8"))
                if estimated_bytes > _MAX_TABLE_BYTES:
                    raise ValueError(f"Dense table exceeds {_MAX_TABLE_BYTES} estimated byte budget")


def safe_json(value: Any) -> str:
    """JSON safe inside either an HTML script element or JavaScript source."""
    result = json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":"), default=str)
    for raw, encoded in [("&", "\\u0026"), ("<", "\\u003c"), (">", "\\u003e"),
                         ("\u2028", "\\u2028"), ("\u2029", "\\u2029")]:
        result = result.replace(raw, encoded)
    return result


@overload
def _number(value: Any, default: float) -> float: ...


@overload
def _number(value: Any, default: None = None) -> float | None: ...


def _number(value: Any, default: float | None = None) -> float | None:
    try:
        value = float(value)
        return value if math.isfinite(value) else default
    except (TypeError, ValueError, OverflowError):
        return default


def channels(records: list[dict], spec: ChartSpec) -> list[dict]:
    """Map fields once without changing the bounded normalized source records."""
    fields = list(dict.fromkeys(key for row in records for key in row))
    numeric = [key for key in fields if any(
        isinstance(row.get(key), (int, float)) and not isinstance(row.get(key), bool) for row in records
    )]
    x = spec.x or next((key for key in fields if key not in numeric), fields[0] if fields else None)
    y = spec.y or next((key for key in numeric if key != x), numeric[0] if numeric else None)
    if spec.kind == "histogram" and spec.x is None:
        x = spec.y or next((key for key in numeric if key != "index"), x)
    heat = spec.color or ("count" if spec.kind == "heatmap" else y)
    return [{"_x": row.get(x, i) if x else i,
             "_y": row.get(y, "") if spec.kind == "heatmap" else _number(row.get(y)) if y else 1,
             "_color": str(row.get(spec.color, "Series")) if spec.color else "Series",
             "_size": max(0, _number(row.get(spec.size, 8), 8)) if spec.size else 8,
             "_heat": _number(row.get(heat, 1)),
             "_row": i} for i, row in enumerate(records)]


def _groups(data: list[dict]) -> dict[str, list[dict]]:
    result: dict[str, list[dict]] = defaultdict(list)
    for row in data:
        result[row["_color"]].append(row)
    return dict(result)


def _geometry(data: list[dict], spec: ChartSpec) -> tuple[list[dict], list[str]]:
    warnings = []
    if spec.kind == "heatmap":
        missing = sum(row["_heat"] is None for row in data)
        if missing:
            data = [row for row in data if row["_heat"] is not None]
            warnings.append(f"{missing} heatmap records with missing/non-numeric color values omitted from geometry.")
    elif spec.kind == "histogram":
        missing = len(data) - len(_histogram_values(data))
        if missing:
            warnings.append(f"{missing} missing/non-numeric histogram observations omitted from geometry.")
    elif spec.kind != "table":
        missing = sum(row["_y"] is None for row in data)
        if missing:
            if spec.kind in {"line", "area", "radar"}:
                warnings.append(f"{missing} missing/non-numeric y observations are shown as gaps, not zeros.")
            else:
                data = [row for row in data if row["_y"] is not None]
                warnings.append(f"{missing} records with missing/non-numeric y observations omitted from geometry.")
    if spec.kind in {"pie", "treemap", "sunburst", "funnel"} and any(r["_y"] < 0 for r in data):
        return [{**r, "_y": max(0, r["_y"])} for r in data], warnings + [
            f"{spec.kind} geometry displays negative weights as zero; original records remain in the manifest."]
    return data, warnings


def _boxes(data: list[dict]) -> list[dict]:
    groups: dict[str, list[float]] = defaultdict(list)
    for row in data:
        groups[str(row["_x"])].append(row["_y"])
    return [{"name": name, "values": values,
             "stats": [float(v) for v in np.quantile(values, [0, .25, .5, .75, 1])]}
            for name, values in groups.items()]


def _histogram_values(data: list[dict]) -> list[float]:
    values = [_number(row["_x"]) for row in data]
    if not any(value is not None for value in values):
        values = [row["_y"] for row in data]
    return [value for value in values if value is not None]


def _histogram(data: list[dict]) -> list[dict]:
    values = _histogram_values(data)
    if not values:
        return []
    counts, edges = np.histogram(values, bins=min(20, max(1, math.ceil(math.sqrt(len(values))))))
    return [{"_x": float((left + right) / 2), "_y": int(count), "_left": float(left),
             "_right": float(right), "_color": "Series"}
            for count, left, right in zip(counts, edges[:-1], edges[1:], strict=True)]


def _tiles(data: list[dict]) -> list[dict]:
    """A one-level slice-and-dice treemap; area is proportional to nonnegative y."""
    total = sum(max(0, r["_y"]) for r in data)
    offset = 0.0
    tiles = []
    for row in data:
        width = max(0, row["_y"]) / total if total else 1 / max(1, len(data))
        tiles.append({**row, "_left": offset, "_right": offset + width, "_bottom": 0, "_top": 1})
        offset += width
    return tiles


def _heatmap(data: list[dict]) -> tuple[list, list, list]:
    xs = list(dict.fromkeys(str(r["_x"]) for r in data))
    ys = list(dict.fromkeys(str(r["_y"]) for r in data))
    xi, yi = {x: i for i, x in enumerate(xs)}, {y: i for i, y in enumerate(ys)}
    values = [[xi[str(r["_x"])], yi[str(r["_y"])], r["_heat"]] for r in data]
    return xs, ys, values


def _colors(spec: ChartSpec) -> tuple[str, str]:
    return ("#171b26", "#edf1f7") if spec.theme == "dark" else ("#ffffff", "#202938")


def _label_color(color: str) -> str:
    rgb = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb]
    luminance = sum(v * w for v, w in zip(linear, [.2126, .7152, .0722], strict=True))
    return "#000000" if luminance > .179 else "#ffffff"


def _wrap(value: Any, width: int) -> str:
    return "\n".join(textwrap.fill(line, width=max(8, width)) for line in str(value).splitlines())


def _fallback(engine: str, kind: str) -> tuple[str, list[str]]:
    mapping = {"vega": {"radar": "line", "sunburst": "pie", "gauge": "bar"},
               "echarts": {"violin": "box"}, "antv": {"violin": "box"}}
    actual = mapping.get(engine, {}).get(kind, kind)
    warnings = []
    if actual != kind:
        warnings.append(f"{engine} fallback: {kind} is rendered as {actual}; this adapter has no native {kind} layout.")
    if kind == "geo" and engine != "plotly":
        warnings.append("Geographic coordinates use longitude=x, latitude=y without a basemap (offline coordinate plot).")
    if kind in {"treemap", "sunburst"}:
        warnings.append("Flat-record hierarchy: each x value is a first-level child; no parent hierarchy is inferred.")
    if kind == "gauge":
        warnings.append("Gauge uses the first mapped y value on a fixed 0–100 scale; displayed fill is clamped.")
    return actual, warnings


def matplotlib_figure(charts: list[tuple[list[dict], ChartSpec]], dashboard: ChartSpec | None = None):
    """Return an Agg figure: the same artists back both PNG and SVG."""
    _table_budget([records for records, spec in charts if spec.kind == "table"])
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.dates import AutoDateLocator, ConciseDateFormatter
    from matplotlib.figure import Figure

    parent = dashboard or charts[0][1]
    bg, outer_fg = _colors(parent)
    fig = Figure(figsize=(parent.width / 100, parent.height / 100), dpi=100, facecolor=bg)
    FigureCanvasAgg(fig)
    columns = min(parent.columns, len(charts)) if dashboard else 1
    rows = math.ceil(len(charts) / columns)
    warnings = []
    for i, (records, spec) in enumerate(charts):
        bg, fg = _colors(spec)
        _, notes = _fallback("matplotlib", spec.kind)
        warnings.extend(notes)
        polar = spec.kind in {"radar", "gauge"}
        ax: Any = fig.add_subplot(rows, columns, i + 1, projection="polar" if polar else None)
        ax.set_facecolor(bg)
        ax.tick_params(colors=outer_fg)
        for spine in ax.spines.values():
            spine.set_color(fg)
        chart_width = parent.width / columns
        ax.set_title(_wrap(spec.title, int(chart_width / 8)), color=outer_fg, fontsize=11)
        data = channels(records, spec)
        data, notes = _geometry(data, spec)
        warnings.extend(notes)
        if not data:
            ax.text(.5, .5, "No data", ha="center", color=fg, transform=ax.transAxes)
            ax.set_axis_off()
            continue
        x, y = [r["_x"] for r in data], [r["_y"] for r in data]
        groups = _groups(data)
        kind = spec.kind
        if kind in {"bar", "line", "area", "scatter", "bubble", "geo"}:
            categories = list(dict.fromkeys(str(v) for v in x))
            category_index = {value: j for j, value in enumerate(categories)}
            temporal_x = kind in {"line", "area", "scatter", "bubble"} and _iso_dates(x)
            for j, (name, group) in enumerate(groups.items()):
                gx, gy = [r["_x"] for r in group], [r["_y"] for r in group]
                if temporal_x:
                    gx = [datetime.fromisoformat(value) for value in gx]
                color = PALETTE[j % len(PALETTE)]
                if kind == "bar":
                    width = .8 / len(groups)
                    positions = [category_index[str(value)] - .4 + width * (j + .5) for value in gx]
                    ax.bar(positions, gy, width=width, color=color, label=name,
                           hatch=["", "//", "\\\\", "xx", "..", "++", "oo"][j % 7], edgecolor=fg,
                           linewidth=.5)
                elif kind in {"line", "area"}:
                    gy = [value if value is not None else math.nan for value in gy]
                    ax.plot(gx, gy, color=color, label=name, marker=MARKERS[j % len(MARKERS)],
                            linestyle=LINESTYLES[j % len(LINESTYLES)], markersize=4)
                    if kind == "area":
                        ax.fill_between(gx, gy, color=color, alpha=.3)
                else:
                    ax.scatter(gx, gy, s=[max(4, r["_size"] * 8) for r in group], color=color, label=name,
                               marker=MARKERS[j % len(MARKERS)])
            if kind == "bar":
                ax.set_xticks(range(len(categories)), categories)
            if temporal_x:
                locator = AutoDateLocator(minticks=3, maxticks=max(3, min(7, int(chart_width / 100))))
                ax.xaxis.set_major_locator(locator)
                ax.xaxis.set_major_formatter(ConciseDateFormatter(locator))
                ax.xaxis.get_offset_text().set_color(outer_fg)
            if spec.color:
                ax.legend(labelcolor=fg, facecolor=bg)
            if kind == "geo":
                ax.set(xlim=(-180, 180), ylim=(-90, 90), xlabel="Longitude", ylabel="Latitude")
            else:
                ax.set_xlabel(spec.x or "Category", color=outer_fg)
                ax.set_ylabel(spec.y or "Value", color=outer_fg)
        elif kind in {"pie", "sunburst"}:
            if sum(max(0, value) for value in y) == 0:
                ax.text(.5, .5, "No positive values", ha="center", color=fg)
            else:
                ax.pie([max(0, value) for value in y], labels=[str(v) for v in x], colors=PALETTE,
                       textprops={"color": outer_fg}, wedgeprops={"width": .55} if kind == "sunburst" else {})
        elif kind == "histogram":
            hist = _histogram(data)
            ax.bar([r["_x"] for r in hist], [r["_y"] for r in hist],
                   width=[r["_right"] - r["_left"] for r in hist], color=PALETTE[0], edgecolor=bg)
            ax.set_ylabel("Count", color=outer_fg)
        elif kind in {"box", "violin"}:
            boxes = _boxes(data)
            values = [b["values"] for b in boxes]
            if kind == "box":
                ax.boxplot(values, tick_labels=[b["name"] for b in boxes], patch_artist=True,
                           boxprops={"facecolor": PALETTE[0]}, medianprops={"color": PALETTE[1]})
            else:
                # Constant/singleton samples have no KDE; show their exact values rather than fail.
                for j, value in enumerate(values, 1):
                    if len(value) > 1 and max(value) > min(value):
                        ax.violinplot([value], positions=[j], showmedians=True)
                    else:
                        ax.scatter([j] * len(value), value, color=PALETTE[0])
                ax.set_xticks(range(1, len(boxes) + 1), [b["name"] for b in boxes])
        elif kind == "heatmap":
            xs, ys, values = _heatmap(data)
            image = ax.scatter([v[0] for v in values], [v[1] for v in values],
                               c=[v[2] for v in values], marker="s", s=200, cmap="viridis")
            ax.set_xticks(range(len(xs)), xs)
            ax.set_yticks(range(len(ys)), ys)
            colorbar = fig.colorbar(image, ax=ax)
            colorbar.ax.tick_params(colors=outer_fg)
            colorbar.ax.set_facecolor(bg)
            colorbar.outline.set_edgecolor(fg)
        elif kind == "radar":
            y = [value if value is not None else math.nan for value in y]
            angles = np.linspace(0, 2 * math.pi, len(data), endpoint=False).tolist()
            ax.plot(angles + angles[:1], y + y[:1], color=PALETTE[0])
            ax.fill(angles + angles[:1], y + y[:1], color=PALETTE[0], alpha=.2)
            ax.set_xticks(angles, [str(v) for v in x])
        elif kind == "treemap":
            from matplotlib.patches import Rectangle
            for j, tile in enumerate(_tiles(data)):
                width = tile["_right"] - tile["_left"]
                ax.add_patch(Rectangle((tile["_left"], 0), width, 1, color=PALETTE[j % len(PALETTE)], ec=bg))
                ax.text(tile["_left"] + width / 2, .5, f'{tile["_x"]}\n{tile["_y"]:g}', ha="center",
                        va="center", color=_label_color(PALETTE[j % len(PALETTE)]), clip_on=True)
            ax.set(xlim=(0, 1), ylim=(0, 1))
            ax.set_axis_off()
        elif kind == "funnel":
            maximum = max(y) or 1
            ax.barh([str(v) for v in x], y, left=[(maximum - value) / 2 for value in y], color=PALETTE[0])
            ax.invert_yaxis()
        elif kind == "gauge":
            value = min(100, max(0, y[0]))
            ax.set_theta_direction(-1)
            ax.set_theta_offset(math.pi)
            ax.bar(math.pi / 2, 1, width=math.pi, bottom=.8, color="#707784", alpha=.3)
            ax.bar(value / 100 * math.pi / 2, 1, width=value / 100 * math.pi, bottom=.8, color=PALETTE[0])
            ax.set_ylim(0, 2)
            ax.text(0, 0, f"{y[0]:g}", ha="center", color=fg, fontsize=20)
            ax.set_axis_off()
        elif kind == "table":
            table_columns = list(dict.fromkeys(key for row in records for key in row))
            table = ax.table(cellText=[[str(row.get(key, "")) for key in table_columns] for row in records],
                             colLabels=table_columns, loc="center")
            table.auto_set_font_size(False)
            table.set_fontsize(8)
            for cell in table.get_celld().values():
                cell.set_facecolor(bg)
                cell.set_text_props(color=fg)
                cell.set_edgecolor(fg)
            ax.set_axis_off()
        for axis in (ax.xaxis, ax.yaxis):
            labels = axis.get_ticklabels()
            if any(len(label.get_text()) > 18 for label in labels):
                positions = axis.get_ticklocs()
                wrapped = [_wrap(label.get_text(), min(22, int(chart_width / max(1, len(labels)) / 8)))
                           for label in labels]
                axis.set_ticks(positions, labels=wrapped)
                if axis is ax.xaxis:
                    for label in axis.get_ticklabels():
                        label.set_rotation(20)
                        label.set_ha("right")
    if dashboard:
        fig.suptitle(_wrap(dashboard.title, int(parent.width / 8)), color=_colors(dashboard)[1])
    from matplotlib.text import Text
    for text in fig.findobj(match=Text):
        text.set_parse_math(False)
    fig.tight_layout(pad=2)
    return fig, warnings


def _plotly(data: list[dict], records: list[dict], spec: ChartSpec) -> dict:
    def literal(value: Any) -> Any:
        return escape(value, quote=False) if isinstance(value, str) else value

    kind = spec.kind
    traces: list[dict] = []
    if kind in {"bar", "line", "area", "scatter", "bubble"}:
        for j, (name, group) in enumerate(_groups(data).items()):
            trace: dict = {"type": "bar" if kind == "bar" else "scatter", "name": literal(name),
                     "x": [literal(r["_x"]) for r in group], "y": [r["_y"] for r in group],
                     "marker": {"color": PALETTE[j % len(PALETTE)]}}
            if kind != "bar":
                trace["mode"] = "markers" if kind in {"scatter", "bubble"} else "lines+markers"
                trace["marker"]["symbol"] = ["circle", "square", "diamond", "cross", "triangle-up", "star", "x"][j % 7]
                trace["line"] = {"dash": ["solid", "dash", "dot", "dashdot", "longdash", "longdashdot", "dot"][j % 7]}
            if kind == "area":
                trace["fill"] = "tozeroy"
            if kind == "bubble":
                trace["marker"]["size"] = [max(4, math.sqrt(r["_size"]) * 6) for r in group]
            traces.append(trace)
    elif kind in {"pie", "treemap", "sunburst", "funnel"}:
        trace = {"type": kind, "labels": [literal(str(r["_x"])) for r in data],
                 "values": [max(0, r["_y"]) for r in data]}
        if kind == "funnel":
            trace = {"type": "funnel", "y": trace["labels"], "x": trace["values"]}
        elif kind in {"treemap", "sunburst"}:
            trace["parents"] = [""] * len(data)
            trace["ids"] = [str(i) for i in range(len(data))]
        traces.append(trace)
    elif kind in {"box", "violin"}:
        traces = [{"type": kind, "x": [literal(r["_x"]) for r in data], "y": [r["_y"] for r in data]}]
    elif kind == "histogram":
        hist = _histogram(data)
        traces = [{"type": "bar", "x": [r["_x"] for r in hist], "y": [r["_y"] for r in hist],
                   "width": [r["_right"] - r["_left"] for r in hist]}]
    elif kind == "heatmap":
        traces = [{"type": "scatter", "mode": "markers", "x": [literal(str(r["_x"])) for r in data],
                   "y": [literal(str(r["_y"])) for r in data], "marker": {"symbol": "square", "size": 22,
                    "color": [r["_heat"] for r in data], "colorscale": "Viridis", "showscale": True}}]
    elif kind == "radar":
        theta, values = [literal(str(r["_x"])) for r in data], [r["_y"] for r in data]
        traces = [{"type": "scatterpolar", "theta": theta + theta[:1], "r": values + values[:1],
                   "fill": "toself"}]
    elif kind == "gauge":
        traces = [{"type": "indicator", "mode": "gauge+number", "value": data[0]["_y"] if data else 0,
                   "gauge": {"axis": {"range": [0, 100]}}}]
    elif kind == "geo":
        # Cartesian longitude/latitude avoids Plotly's network-fetched topojson.
        traces = [{"type": "scatter", "mode": "markers", "x": [r["_x"] for r in data],
                   "y": [r["_y"] for r in data], "text": [literal(r["_color"]) for r in data]}]
    elif kind == "table":
        columns = list(dict.fromkeys(key for row in records for key in row))
        traces = [{"type": "table", "header": {"values": [literal(c) for c in columns]},
                   "cells": {"values": [[literal(str(row.get(key, ""))) for row in records] for key in columns]}}]
    bg, fg = _colors(spec)
    layout: dict[str, Any] = {"title": {"text": literal(spec.title)}, "width": spec.width, "height": spec.height,
              "paper_bgcolor": bg, "plot_bgcolor": bg, "font": {"color": fg}, "showlegend": bool(spec.color),
              "xaxis": {"title": {"text": literal(spec.x or "Category")}},
              "yaxis": {"title": {"text": literal(spec.y or "Value")}}}
    if kind == "geo":
        layout["xaxis"].update(range=[-180, 180], title={"text": "Longitude"})
        layout["yaxis"].update(range=[-90, 90], title={"text": "Latitude"})
    return {"data": traces, "layout": layout}


def _iso_dates(values: list[Any]) -> bool:
    if not values:
        return False
    for value in values:
        if not isinstance(value, str) or len(value) < 10 or value[4] != "-" or value[7] != "-":
            return False
        try:
            datetime.fromisoformat(value)
        except ValueError:
            return False
    return True


def _vega(data: list[dict], records: list[dict], spec: ChartSpec, kind: str) -> dict:
    x_type = "quantitative" if all(isinstance(r["_x"], (int, float)) for r in data) else "nominal"
    if kind in {"line", "area", "scatter", "bubble"} and _iso_dates([r["_x"] for r in data]):
        x_type = "temporal"
    encoding: dict = {"x": {"field": "_x", "type": x_type, "title": spec.x or "Category"},
                      "y": {"field": "_y", "type": "quantitative", "title": spec.y or "Value"}}
    if spec.color:
        encoding["color"] = {"field": "_color", "type": "nominal", "title": spec.color, "scale": {"range": PALETTE}}
        if kind == "bar":
            encoding["xOffset"] = {"field": "_color"}
            encoding["y"]["stack"] = None
        elif kind in {"line", "area"}:
            encoding["strokeDash"] = {"field": "_color", "type": "nominal", "title": spec.color,
                                      "scale": {"range": DASHES}}
            if kind == "area":
                encoding["y"]["stack"] = None
    mark: Any = {"type": {"bar": "bar", "line": "line", "scatter": "point", "bubble": "point",
                         "area": "area", "box": "boxplot", "violin": "area", "geo": "point"}.get(kind, "bar"),
                 "color": PALETTE[0]}
    if kind == "line":
        mark["point"] = True
    transforms = []
    if kind == "bubble":
        encoding["size"] = {"field": "_size", "type": "quantitative", "title": spec.size or "Size"}
    elif kind == "pie":
        mark = {"type": "arc", "tooltip": True}
        encoding = {"theta": {"field": "_y", "type": "quantitative"},
                    "color": {"field": "_x", "type": "nominal"}}
    elif kind == "histogram":
        data = _histogram(data)
        encoding = {"x": {"field": "_left", "type": "quantitative", "bin": "binned"},
                    "x2": {"field": "_right"}, "y": {"field": "_y", "type": "quantitative", "title": "Count"}}
    elif kind == "heatmap":
        mark = "rect"
        encoding["x"]["type"] = "nominal"
        encoding["y"]["type"] = "nominal"
        encoding["color"] = {"field": "_heat", "type": "quantitative"}
    elif kind == "violin":
        transforms = [{"density": "_y", "groupby": ["_x"], "as": ["value", "density"]}]
        encoding = {"y": {"field": "value", "type": "quantitative"},
                    "x": {"field": "density", "type": "quantitative", "stack": "center", "axis": None},
                    "column": {"field": "_x", "type": "nominal"}}
        mark = {"type": "area", "orient": "horizontal"}
    elif kind == "treemap":
        data = _tiles(data)
        mark = "rect"
        encoding = {"x": {"field": "_left", "type": "quantitative", "axis": None},
                    "x2": {"field": "_right"}, "y": {"field": "_bottom", "type": "quantitative", "axis": None},
                    "y2": {"field": "_top"}, "color": {"field": "_x", "type": "nominal"},
                    "tooltip": [{"field": "_x"}, {"field": "_y"}]}
    elif kind == "funnel":
        maximum = max((r["_y"] for r in data), default=1)
        data = [{**r, "_left": (maximum - r["_y"]) / 2, "_right": (maximum + r["_y"]) / 2} for r in data]
        encoding = {"x": {"field": "_left", "type": "quantitative", "title": spec.y or "Value"},
                    "x2": {"field": "_right"}, "y": {"field": "_x", "type": "nominal", "sort": None}}
    elif kind == "table":
        columns = list(dict.fromkeys(key for row in records for key in row))
        data = [{"column": key, "row": "Header", "text": key} for key in columns] + [
            {"column": key, "row": str(i + 1), "text": str(row.get(key, ""))}
            for i, row in enumerate(records) for key in columns]
        mark = {"type": "text", "align": "center"}
        encoding = {"x": {"field": "column", "type": "ordinal", "axis": None, "sort": columns},
                    "y": {"field": "row", "type": "ordinal", "axis": None,
                          "sort": ["Header"] + [str(i + 1) for i in range(len(records))]},
                    "text": {"field": "text"}}
    bg, fg = _colors(spec)
    if kind == "table":
        mark["color"] = fg
    result = {"$schema": "https://vega.github.io/schema/vega-lite/v5.json", "data": {"values": data},
              "mark": mark, "encoding": encoding, "width": max(100, spec.width - 100),
              "height": max(100, spec.height - 100), "title": spec.title,
              "background": bg, "config": {"axis": {"labelColor": fg, "titleColor": fg},
                                             "title": {"color": fg}, "text": {"color": fg},
                                             "legend": {"labelColor": fg, "titleColor": fg}}}
    if transforms:
        result["transform"] = transforms
    return result


def _echarts(data: list[dict], records: list[dict], spec: ChartSpec, kind: str) -> dict:
    bg, fg = _colors(spec)
    xs = list(dict.fromkeys(str(r["_x"]) for r in data))
    option: dict = {"animation": False, "backgroundColor": bg, "color": PALETTE,
                    "title": {"text": spec.title, "textStyle": {"color": fg}},
                    "textStyle": {"color": fg}, "tooltip": {"trigger": "item", "renderMode": "richText"},
                    "legend": {"show": bool(spec.color), "top": 30, "textStyle": {"color": fg}},
                    "grid": {"containLabel": True, "left": 50, "right": 30, "top": 65, "bottom": 35},
                    "xAxis": {"type": "category", "data": xs, "name": spec.x or ""},
                    "yAxis": {"type": "value", "name": spec.y or ""}, "series": []}
    series = option["series"]
    if kind in {"bar", "line", "area"}:
        temporal_x = kind != "bar" and _iso_dates([row["_x"] for row in data])
        numeric_x = kind != "bar" and all(isinstance(row["_x"], (int, float)) for row in data)
        if temporal_x or numeric_x:
            option["xAxis"] = {"type": "time" if temporal_x else "value", "name": spec.x or ""}
        for j, (name, group) in enumerate(_groups(data).items()):
            item: dict = {"type": "bar" if kind == "bar" else "line", "name": name,
                    "data": [[r["_x"] if temporal_x or numeric_x else str(r["_x"]), r["_y"]] for r in group]}
            if kind == "area":
                item["areaStyle"] = {}
            if kind != "bar":
                item.update(symbol=["circle", "rect", "triangle", "diamond", "pin", "roundRect", "arrow"][j % 7],
                            symbolSize=7, showSymbol=True,
                            lineStyle={"type": ["solid", "dashed", "dotted"][j % 3]})
            series.append(item)
    elif kind in {"scatter", "bubble", "geo"}:
        option["xAxis"] = {"type": "value", "name": spec.x or ""}
        for name, group in _groups(data).items():
            series.append({"type": "scatter", "name": name, "data": [
                {"value": [r["_x"], r["_y"], r["_size"]],
                 "symbolSize": max(4, math.sqrt(r["_size"]) * 6) if kind == "bubble" else 9} for r in group]})
        if kind == "geo":
            option["xAxis"].update(min=-180, max=180, name="Longitude")
            option["yAxis"].update(min=-90, max=90, name="Latitude")
    elif kind in {"pie", "treemap", "sunburst", "funnel", "gauge"}:
        values: list = [{"name": str(r["_x"]), "value": max(0, r["_y"])} for r in data]
        item = {"type": kind, "data": values}
        if kind == "gauge":
            item.update(min=0, max=100, data=[{"value": data[0]["_y"] if data else 0}])
        if kind == "funnel":
            item["sort"] = "none"
        series.append(item)
        option.pop("xAxis")
        option.pop("yAxis")
    elif kind == "histogram":
        hist = _histogram(data)
        option["xAxis"]["data"] = [f'{r["_left"]:g}–{r["_right"]:g}' for r in hist]
        series.append({"type": "bar", "barCategoryGap": "0%", "data": [r["_y"] for r in hist]})
    elif kind == "box":
        boxes = _boxes(data)
        option["xAxis"]["data"] = [b["name"] for b in boxes]
        series.append({"type": "boxplot", "data": [b["stats"] for b in boxes]})
    elif kind == "radar":
        option.pop("xAxis")
        option.pop("yAxis")
        option["radar"] = {"indicator": [{"name": str(r["_x"]), "max": max(1, max(v["_y"] for v in data))}
                                          for r in data]}
        series.append({"type": "radar", "data": [{"value": [r["_y"] for r in data]}]})
    elif kind == "heatmap":
        xs, ys, values = _heatmap(data)
        option["xAxis"]["data"] = xs
        option["yAxis"] = {"type": "category", "data": ys}
        option["visualMap"] = {"min": min((v[2] for v in values), default=0),
                               "max": max((v[2] for v in values), default=1), "show": False}
        series.append({"type": "heatmap", "data": values})
    elif kind == "table":
        columns = list(dict.fromkeys(key for row in records for key in row))
        option.pop("xAxis")
        option.pop("yAxis")
        option["graphic"] = [{"type": "text", "left": 20 + j * (spec.width - 40) / max(1, len(columns)),
                               "top": 60 + i * 20, "style": {"text": str(value), "fill": fg, "fontSize": 12}}
                              for i, row in enumerate([dict(zip(columns, columns, strict=True)), *records])
                               for j, value in enumerate(row.get(key, "") for key in columns)]
    if "xAxis" in option:
        option["xAxis"].update(nameLocation="middle", nameGap=30)
        option["grid"]["bottom"] = 55
    return option


def _antv(data: list[dict], records: list[dict], spec: ChartSpec, kind: str) -> dict:
    temporal_x = kind in {"line", "area", "scatter", "bubble"} and _iso_dates([row["_x"] for row in data])
    if temporal_x:
        times = [datetime.fromisoformat(row["_x"]) for row in data]
        data = [{**row, "_x": (value if value.tzinfo else value.replace(tzinfo=UTC)).timestamp() * 1000}
                for row, value in zip(data, times, strict=True)]
    mark = {"bar": "interval", "line": "line", "area": "area", "scatter": "point", "bubble": "point",
            "pie": "interval", "heatmap": "cell", "histogram": "interval", "box": "box",
            "radar": "line", "treemap": "rect", "sunburst": "interval", "funnel": "interval",
            "gauge": "interval", "geo": "point", "table": "text"}[kind]
    result: dict = {"type": mark, "data": data, "encode": {"x": "_x", "y": "_y"},
                    "animate": False, "theme": spec.theme, "title": spec.title, "tooltip": False,
                    "axis": {"x": {"title": spec.x or "Category", "labelFill": _colors(spec)[1], "titleFill": _colors(spec)[1]},
                             "y": {"title": spec.y or "Value", "labelFill": _colors(spec)[1], "titleFill": _colors(spec)[1]}}}
    encode = result["encode"]
    if spec.color:
        encode["color"] = "_color"
        result["scale"] = {"color": {"range": PALETTE}}
    else:
        result["style"] = {"fill": PALETTE[0], "stroke": PALETTE[0]}
    if temporal_x:
        result.setdefault("scale", {})["x"] = {"type": "time"}
    if kind == "line":
        groups = _groups(data)
        result["type"] = "view"
        result.pop("encode")
        result.pop("style", None)
        shapes = ["point", "square", "triangle", "diamond", "hexagon", "bowtie", "cross"]
        if spec.color:
            result["scale"]["color"]["domain"] = list(groups)
            result["scale"]["shape"] = {"domain": list(groups), "range": shapes}
        children = []
        for j, group in enumerate(groups.values()):
            encode = {"x": "_x", "y": "_y"}
            if spec.color:
                encode["color"] = "_color"
            line_style: dict = {"lineDash": DASHES[j % len(DASHES)], "lineWidth": 2}
            point_style: dict = {"r": 3}
            if not spec.color:
                line_style["stroke"] = PALETTE[0]
                point_style["fill"] = PALETTE[0]
            children.append({"type": "line", "data": group, "encode": encode,
                             "style": line_style, "animate": False})
            children.append({"type": "point", "data": [row for row in group if row["_y"] is not None],
                             "encode": {**encode, **({"shape": "_color"} if spec.color else {})},
                             "style": point_style, "animate": False})
        result["children"] = children
    elif kind == "bar" and spec.color:
        result["transform"] = [{"type": "dodgeX"}]
    elif kind == "bubble":
        encode["size"] = "_size"
    elif kind in {"pie", "sunburst"}:
        result["coordinate"] = {"type": "theta", "innerRadius": .45 if kind == "sunburst" else 0}
        result["transform"] = [{"type": "stackY"}]
        encode.pop("x")
        encode["color"] = "_x"
        result["legend"] = {"color": {"position": "right"}}
    elif kind == "radar":
        result["coordinate"] = {"type": "polar"}
        result["data"] = data + data[:1]
    elif kind == "histogram":
        result["data"] = _histogram(data)
    elif kind == "heatmap":
        encode["color"] = "_heat"
        result.pop("scale", None)
        result.pop("style", None)
    elif kind == "box":
        result["data"] = [{"_x": b["name"], "_y": b["stats"]} for b in _boxes(data)]
    elif kind == "treemap":
        result["data"] = _tiles(data)
        result["encode"] = {"x": ["_left", "_right"], "y": ["_bottom", "_top"], "color": "_x"}
        result["axis"] = False
    elif kind == "funnel":
        result["coordinate"] = {"transform": [{"type": "transpose"}]}
        result["transform"] = [{"type": "symmetryY"}]
    elif kind == "gauge":
        value = min(100, max(0, data[0]["_y"])) if data else 0
        result["data"] = [{"_x": "Value", "_y": value}, {"_x": "Remaining", "_y": 100 - value}]
        result["coordinate"] = {"type": "theta", "innerRadius": .75, "startAngle": -math.pi,
                                 "endAngle": 0}
        result["encode"] = {"y": "_y", "color": "_x"}
        result["transform"] = [{"type": "stackY"}]
        result["axis"] = False
    elif kind == "geo":
        result["scale"] = {"x": {"domain": [-180, 180]}, "y": {"domain": [-90, 90]}}
    elif kind == "table":
        columns = list(dict.fromkeys(key for row in records for key in row))
        result["data"] = [{"_x": key, "_y": str(i), "_text": str(row.get(key, ""))}
                          for i, row in enumerate([dict(zip(columns, columns, strict=True)), *records])
                          for key in columns]
        result["encode"] = {"x": "_x", "y": "_y", "text": "_text"}
        result["axis"] = False
        result["style"] = {"fill": _colors(spec)[1], "stroke": _colors(spec)[1]}
    return result


def native_spec(engine: str, records: list[dict], spec: ChartSpec) -> tuple[dict, list[str], str]:
    """Build only the selected engine's native declarative payload."""
    if engine not in ENGINES or engine == "matplotlib":
        raise ValueError(f"No JSON spec for engine {engine!r}")
    if spec.kind == "table":
        _table_budget([records])
    kind, warnings = _fallback(engine, spec.kind)
    if spec.kind == "geo" and engine == "plotly":
        warnings.append("Geographic coordinates use longitude=x, latitude=y without a basemap (offline coordinate plot).")
    data, notes = _geometry(channels(records, spec), spec)
    warnings.extend(notes)
    if engine == "plotly":
        native = _plotly(data, records, spec)
    elif engine == "vega":
        native = _vega(data, records, spec, kind)
    elif engine == "echarts":
        native = _echarts(data, records, spec, kind)
    else:
        native = _antv(data, records, spec, kind)
    return native, warnings, kind


def browser_html(
    engine: str, payloads: list[dict], specs: list[ChartSpec], parent: ChartSpec,
    metadata: list[dict] | None = None, image: str | None = None,
) -> str:
    """Inert JSON, fixed bootstrap, and keyboard-discoverable real data tables.

    Static PNG/SVG outputs receive the same companion HTML with a relative image
    path. Only a concise summary is aria-described; tables stay navigable tables.
    """
    _table_budget([info.get("records", []) for info in metadata] if metadata else [])
    bg, fg = _colors(parent)
    cards = []
    for i, spec in enumerate(specs):
        info = metadata[i] if metadata else {}
        records = info.get("records", [])
        columns = list(dict.fromkeys(key for row in records for key in row))
        summary = (f'{spec.kind} chart. {info.get("output_count", len(records))} displayed records from '
                   f'{info.get("input_count", len(records))} input records. '
                   f'Reduction strategy: {info.get("strategy", "none")}. {spec.description}')
        warnings = "".join(f'<li>{escape(str(w))}</li>' for w in info.get("warnings", []))
        header = "".join(f'<th scope="col">{escape(str(key))}</th>' for key in columns)
        body = "".join('<tr>' + "".join(f'<td>{escape(str(row.get(key, "")))}</td>' for key in columns) + '</tr>'
                       for row in records)
        graph = "" if image else (
            f'<div id="chart-{i}" role="img" aria-label="{escape(spec.title, quote=True)}" '
            f'aria-describedby="chart-summary-{i}" '
            f'style="width:100%;height:{spec.height}px;background:{_colors(spec)[0]}"></div>')
        cards.append(f'<section><h2>{escape(spec.title)}</h2>{graph}'
                     f'<p id="chart-summary-{i}">{escape(summary)}</p>'
                     f'{"<ul>" + warnings + "</ul>" if warnings else ""}'
                     f'<details><summary>View chart data ({len(records)} records)</summary><div class="data-scroll">'
                     f'<table><caption>Data for {escape(spec.title)}</caption><thead><tr>{header}</tr></thead>'
                     f'<tbody>{body}</tbody></table></div></details></section>')
    scripts = ""
    if not image:
        if engine == "plotly":
            from plotly.offline import get_plotlyjs, get_plotlyjs_version
            notice = files("deepviz").joinpath("resources/plotly-js-LICENSE.txt").read_text(encoding="utf-8")
            dependency = (f"<!-- Plotly.js runtime v{get_plotlyjs_version()}; notice from upstream v3.7.0 LICENSE.\n"
                          f"{notice}--><script>{get_plotlyjs()}</script>")
            bootstrap = "return Plotly.newPlot(el,p.data,p.layout,{responsive:true,displaylogo:false});"
        elif engine == "echarts":
            dependency = f'<script src="{ECHARTS_URL}"></script>'
            bootstrap = "const c=echarts.init(el,null,{renderer:'svg'});c.setOption(p);return Promise.resolve(c);"
        else:
            dependency = f'<script src="{ANTV_URL}"></script>'
            bootstrap = ("const c=new G2.Chart({container:el,width:el.clientWidth,height:el.clientHeight});"
                         "c.options(p);return c.render();")
        scripts = (f'<script id="deepviz-data" type="application/json">{safe_json(payloads)}</script>{dependency}'
                   '<script>const payloads=JSON.parse(document.getElementById("deepviz-data").textContent);'
                   'window.deepvizReady=Promise.all(payloads.map((p,i)=>{const el=document.getElementById("chart-"+i);'
                   f'{bootstrap}'
                   '})).catch(e=>{document.body.dataset.renderError=String(e);throw e;});</script>')
    columns_count = parent.columns if parent.kind == "dashboard" else 1
    picture = (f'<figure><img src="{escape(image, quote=True)}" alt="{escape(parent.title, quote=True)}. '
               'Chart data and reduction details follow." style="max-width:100%;height:auto"></figure>') if image else ""
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{escape(parent.title)}</title><style>'
            f'body{{background:{bg};color:{fg};font:14px system-ui;margin:20px}}'
            f'main{{max-width:{parent.width}px;display:grid;grid-template-columns:repeat({columns_count},minmax(0,1fr));gap:20px}}'
            'section{min-width:0}p,h1,h2,td,th{overflow-wrap:anywhere}summary{cursor:pointer;padding:8px}'
            '.data-scroll{overflow:auto;max-height:28rem}table{border-collapse:collapse;width:100%}'
            'td,th{border:1px solid #7a8494;padding:6px;text-align:left}caption{text-align:left;font-weight:600;padding:8px}'
            'summary:focus-visible{outline:3px solid #2a9d73;outline-offset:2px}'
            '@media(max-width:650px){main{grid-template-columns:1fr}}'
            f'</style></head><body><h1>{escape(parent.title)}</h1>{picture}<main>{"".join(cards)}</main>{scripts}</body></html>')
