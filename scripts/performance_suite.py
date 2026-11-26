"""Measure the real streaming path in fresh workers, never a prebuilt input list."""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import importlib
import json
import math
import platform
import struct
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from collections.abc import Iterator
from pathlib import Path
from typing import Any

COUNTS = (10, 1_000, 100_000, 1_000_000, 10_000_000)
CASES = ("numeric_sample", "category_sum", "category_mean")
ENGINES = ("matplotlib", "plotly", "vega", "echarts", "antv")
ROOT = Path(__file__).resolve().parents[1]


class CountedSource(Iterator[dict[str, Any]]):
    """Observe actual pulls without retaining rows or exposing a length hint."""

    def __init__(self, rows: Iterator[dict[str, Any]]) -> None:
        self.rows = rows
        self.consumed = 0
        self.exhausted = False

    def __next__(self) -> dict[str, Any]:
        try:
            row = next(self.rows)
        except StopIteration:
            self.exhausted = True
            raise
        self.consumed += 1
        return row


def generate_rows(count: int, case: str) -> Iterator[dict[str, Any]]:
    if type(count) is not int or count < 1:
        raise ValueError("count must be a positive integer")
    if case not in CASES:
        raise ValueError(f"Unknown benchmark case: {case}")
    for index in range(count):
        if case == "numeric_sample":
            yield {"x": index, "value": index % 101 - 50}
        else:
            yield {"category": f"group-{index % 7}", "value": index + 1}


def expected_categories(count: int, aggregation: str) -> dict[str, int | float]:
    """Closed-form arithmetic progressions, independent of the reducer."""
    expected: dict[str, int | float] = {}
    for category in range(min(count, 7)):
        size = (count - 1 - category) // 7 + 1
        first = category + 1
        total = size * (2 * first + (size - 1) * 7) // 2
        expected[f"group-{category}"] = total if aggregation == "sum" else total / size
    return expected


def peak_memory() -> dict[str, Any]:
    """Return OS process peak RSS/working set in bytes, not Python allocations."""
    if sys.platform == "win32":
        from ctypes import wintypes

        class Counters(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        kernel.GetCurrentProcess.restype = wintypes.HANDLE
        psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
        psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
        counters = Counters()
        counters.cb = ctypes.sizeof(counters)
        if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
            raise ctypes.WinError(ctypes.get_last_error())
        peak = int(counters.PeakWorkingSetSize)
        method = "GetProcessMemoryInfo.PeakWorkingSetSize"
    else:
        import resource

        raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        peak = int(raw if sys.platform == "darwin" else raw * 1024)
        method = "resource.getrusage(RUSAGE_SELF).ru_maxrss"
    return {"peak_rss_bytes": peak, "method": method, "scope": "inclusive_process_high_water_mark"}


def load_api(source_root: Path, require_render: bool = False) -> tuple[Any, Any, Any]:
    source = source_root.resolve() / "python/deepviz/src"
    if str(source) not in sys.path:
        sys.path.insert(0, str(source))
    modules: dict[str, Any] = {}
    for name in ("models", "normalize", *(("render",) if require_render else ())):
        try:
            module = importlib.import_module(f"deepviz.{name}")
        except ModuleNotFoundError as error:
            raise RuntimeError(f"Real integration unavailable in {source}: {error}; no benchmark pass") from error
        if not module.__file__ or not Path(module.__file__).resolve().is_relative_to(source):
            raise RuntimeError(f"Refusing source outside requested checkout: {module.__file__}")
        modules[name] = module
    return modules["normalize"].normalize, modules["models"].ChartSpec, (
        modules["render"].render if require_render else None
    )


def make_spec(ChartSpec: Any, case: str, max_points: int) -> Any:
    numeric = case == "numeric_sample"
    return ChartSpec(kind="line" if numeric else "bar", x="x" if numeric else "category", y="value",
                     aggregation="sample" if numeric else case.removeprefix("category_"),
                     max_points=max_points, title=f"Streaming verification: {case}")


def normalize_case(source_root: Path, count: int, case: str, max_points: int) -> dict[str, Any]:
    normalize, ChartSpec, _ = load_api(source_root)
    source = CountedSource(generate_rows(count, case))
    result = normalize(source, make_spec(ChartSpec, case, max_points))
    return {"records": result.records, "input_count": result.input_count, "strategy": result.strategy,
            "warnings": result.warnings, "consumed_count": source.consumed, "source_exhausted": source.exhausted}


def validate_normalized(result: dict[str, Any], count: int, case: str, max_points: int) -> dict[str, Any]:
    assert result["input_count"] == count, "Normalizer input_count is not the requested count"
    assert result["consumed_count"] == count, "Generator was not consumed exactly once"
    assert result["source_exhausted"], "Normalizer stopped before source exhaustion"
    records = result["records"]
    assert 0 < len(records) <= max_points, "Normalized output exceeded its bound or is empty"
    if case == "numeric_sample":
        assert len(records) == min(count, max_points), "Reservoir has wrong output count"
        xs = [row["x"] for row in records]
        assert xs == sorted(set(xs)), "Sample must contain unique, input-ordered rows"
        for row in records:
            assert type(row["x"]) is int and 0 <= row["x"] < count, "Sample index outside source"
            assert row["value"] == row["x"] % 101 - 50, "Sample changed a source value"
        if count > max_points:
            assert result["strategy"] == "sample" and result["warnings"], "Lossy sampling was not disclosed"
    else:
        aggregation = case.removeprefix("category_")
        expected = expected_categories(count, aggregation)
        actual = {row["category"]: row["value"] for row in records}
        assert len(actual) == len(records) == len(expected), "Missing or duplicate categories"
        assert set(actual) == set(expected), "Wrong categories"
        for key, value in expected.items():
            assert math.isclose(actual[key], value, rel_tol=1e-10, abs_tol=1e-9), f"Wrong {aggregation}: {key}"
        total = sum(actual.values()) if aggregation == "sum" else sum(
            actual[f"group-{c}"] * ((count - 1 - c) // 7 + 1) for c in range(min(count, 7))
        )
        assert math.isclose(total, count * (count + 1) // 2, rel_tol=1e-10), "Aggregate total lost rows"
        assert result["strategy"] == aggregation, "Reduction metadata is inaccurate"
        return {"category_values": actual, "observed_grand_total": total}
    return {}


def source_snapshot(root: Path) -> dict[str, Any]:
    commit = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], check=True,
                            capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", str(root), "status", "--porcelain"], check=True,
                           capture_output=True, text=True).stdout.splitlines()
    hashes = {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in sorted((root / "python/deepviz/src/deepviz").rglob("*.py"))}
    return {"root": str(root.resolve()), "commit": commit, "dirty_paths": dirty, "sha256": hashes}


def require_same_source(before: dict[str, Any], after: dict[str, Any]) -> None:
    assert before["commit"] == after["commit"] and before["sha256"] == after["sha256"], (
        "Source changed during the benchmark; refuse mixed-source evidence"
    )


def inspect_artifact(path: Path) -> dict[str, Any]:
    assert path.is_file() and path.stat().st_size > 0, f"Missing/empty artifact: {path}"
    suffix = path.suffix.lower()
    if suffix == ".svg":
        root = ET.parse(path).getroot()
        assert root.tag.rsplit("}", 1)[-1] == "svg", "Invalid SVG root"
        marks = sum(node.tag.rsplit("}", 1)[-1] in {"path", "rect", "circle", "polyline", "polygon"}
                    for node in root.iter())
        assert marks > 0, "SVG has no drawable geometry"
        inspection = "svg_xml_and_drawable_geometry_not_visual_review"
    elif suffix == ".png":
        from PIL import Image

        with path.open("rb") as stream:
            header = stream.read(24)
        assert header[:8] == b"\x89PNG\r\n\x1a\n", "Invalid PNG signature"
        width, height = struct.unpack(">II", header[16:24])
        assert width > 0 and height > 0
        with Image.open(path) as image:
            histogram = image.convert("RGB").histogram()
        assert sum(value > 0 for value in histogram) > 3, "PNG is a single flat color"
        inspection = "png_decoded_nonuniform_pixels_not_visual_review"
    elif suffix in {".html", ".htm"}:
        from html.parser import HTMLParser

        class Tags(HTMLParser):
            def __init__(self) -> None:
                super().__init__()
                self.tags: set[str] = set()

            def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
                self.tags.add(tag)

        parser = Tags()
        parser.feed(path.read_text(encoding="utf-8"))
        assert {"html", "script"}.issubset(parser.tags), "HTML lacks document/scripts"
        inspection = "html_structure_only_browser_execution_not_verified"
    else:
        raise AssertionError(f"Unsupported artifact inspection: {suffix}")
    return {"path": str(path), "bytes": path.stat().st_size, "inspection": inspection}


def run_case(source_root: Path, *, count: int, case: str, max_points: int,
             engine: str | None = None, artifact_dir: Path | None = None) -> dict[str, Any]:
    _, ChartSpec, render = load_api(source_root, require_render=engine is not None)
    baseline = peak_memory()
    started = time.perf_counter()
    normalized = normalize_case(source_root, count, case, max_points)
    elapsed = time.perf_counter() - started
    checked = validate_normalized(normalized, count, case, max_points)
    records = normalized.pop("records")
    encoded = json.dumps(records, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    result = normalized | {"status": "passed", "count": count, "case": case, "max_points": max_points,
                           "output_count": len(records), "elapsed_seconds": elapsed,
                           "output_sha256": hashlib.sha256(encoded).hexdigest()} | checked
    if engine is not None:
        if artifact_dir is not None:
            artifact_dir.mkdir(parents=True, exist_ok=True)
        directory = Path(tempfile.mkdtemp(prefix=f"deepviz-{engine}-{count}-", dir=artifact_dir))
        # Only the bounded result crosses the renderer boundary, never the raw stream.
        render_spec = make_spec(ChartSpec, case, max_points).model_copy(update={"aggregation": "none"})
        started = time.perf_counter()
        artifact = render(records, render_spec, engine=engine, output_dir=directory)
        result["render_elapsed_seconds"] = time.perf_counter() - started
        assert artifact.input_count == len(records), "Renderer did not receive the bounded dataset"
        assert 0 < artifact.output_count <= max_points, "Renderer output exceeded its bound"
        result.update(engine=engine, renderer_input_count=artifact.input_count,
                      renderer_output_count=artifact.output_count,
                      artifacts=[inspect_artifact(Path(path)) for path in artifact.paths])
        assert result["artifacts"], "Renderer returned no artifacts"
    memory = peak_memory()
    result.update(memory)
    result["baseline_peak_rss_bytes"] = baseline["peak_rss_bytes"]
    result["peak_high_water_growth_bytes"] = max(0, memory["peak_rss_bytes"] - baseline["peak_rss_bytes"])
    result["growth_scope"] = "difference_of_process_high_water_marks_not_operation_peak_allocation"
    return result


def run_worker(source_root: Path, *, count: int, case: str, max_points: int,
               engine: str | None = None, artifact_dir: Path | None = None, timeout: float = 300) -> dict[str, Any]:
    command = [sys.executable, str(Path(__file__).resolve()), "--worker", "--source-root", str(source_root),
               "--counts", str(count), "--cases", case, "--max-points", str(max_points)]
    if engine is not None:
        command.extend(["--engine", engine])
    if artifact_dir is not None:
        command.extend(["--artifact-dir", str(artifact_dir)])
    started = time.perf_counter()
    process = subprocess.run(command, check=False, capture_output=True, text=True, timeout=timeout)
    if process.returncode:
        raise RuntimeError(f"Worker failed ({case}, {count}, {engine}):\n{process.stderr}\n{process.stdout}")
    result: dict[str, Any] = json.loads(process.stdout)
    result["subprocess_wall_seconds"] = time.perf_counter() - started
    return result


def check_peak_growth(results: list[dict[str, Any]], limit_bytes: int) -> list[dict[str, Any]]:
    checks = []
    for case in CASES:
        rows = [row for row in results if row["case"] == case and "engine" not in row]
        if len({row["count"] for row in rows}) < 2:
            continue
        smallest = min(row["count"] for row in rows)
        baseline = min(row["peak_rss_bytes"] for row in rows if row["count"] == smallest)
        growth = max(row["peak_rss_bytes"] for row in rows) - baseline
        assert growth <= limit_bytes, f"{case}: peak RSS grew {growth} bytes above small-stream baseline"
        checks.append({"case": case, "inclusive_peak_growth_bytes": growth, "limit_bytes": limit_bytes})
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=ROOT)
    parser.add_argument("--counts", nargs="+", type=int, default=list(COUNTS))
    parser.add_argument("--cases", nargs="+", choices=CASES, default=list(CASES))
    parser.add_argument("--max-points", type=int, default=2000)
    parser.add_argument("--render-counts", nargs="*", type=int, default=[10, 1000])
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--timeout", type=float, default=300)
    parser.add_argument("--max-peak-growth-mib", type=float, default=64)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--artifact-dir", type=Path)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--engine", choices=ENGINES, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if any(count < 1 for count in [*args.counts, *args.render_counts]) or args.repeats < 1:
        parser.error("counts and repeats must be positive")
    if not 10 <= args.max_points <= 100_000 or args.timeout <= 0 or args.max_peak_growth_mib < 0:
        parser.error("invalid bound, timeout or peak growth limit")
    if args.output and args.output.exists():
        parser.error("output already exists; choose a unique evidence path")
    root = args.source_root.resolve()
    initial_source = source_snapshot(root)
    if args.worker:
        result = run_case(root, count=args.counts[0], case=args.cases[0], max_points=args.max_points,
                          engine=args.engine, artifact_dir=args.artifact_dir)
        require_same_source(initial_source, source_snapshot(root))
        result["source"] = initial_source
        print(json.dumps(result, allow_nan=False))
        return 0
    results = []
    errors = []
    for case in args.cases:
        for count in args.counts:
            repeats = args.repeats if case == "numeric_sample" else 1
            repeated = []
            for repeat in range(repeats):
                print(f"{case}: count={count}, repeat={repeat + 1}", file=sys.stderr, flush=True)
                try:
                    result = run_worker(root, count=count, case=case, max_points=args.max_points,
                                        timeout=args.timeout)
                    require_same_source(initial_source, result["source"])
                    result["repeat"] = repeat + 1
                    results.append(result)
                    repeated.append(result["output_sha256"])
                except Exception as error:
                    errors.append({"case": case, "count": count, "error": str(error)})
                    break
            if len(set(repeated)) > 1:
                errors.append({"case": case, "count": count, "error": "sampling is not deterministic"})
    for count in args.render_counts:
        for engine in ENGINES:
            try:
                result = run_worker(root, count=count, case="numeric_sample",
                                    max_points=min(args.max_points, 100), engine=engine,
                                    artifact_dir=args.artifact_dir, timeout=args.timeout)
                require_same_source(initial_source, result["source"])
                results.append(result)
            except Exception as error:
                errors.append({"engine": engine, "count": count, "error": str(error)})
    try:
        memory_checks = check_peak_growth(results, int(args.max_peak_growth_mib * 1024**2))
    except AssertionError as error:
        errors.append({"error": str(error)})
        memory_checks = []
    try:
        require_same_source(initial_source, source_snapshot(root))
    except AssertionError as error:
        errors.append({"error": str(error)})
    report = {"status": "failed" if errors else "passed", "source": initial_source,
              "harness": source_snapshot(ROOT), "python": sys.version, "platform": platform.platform(),
              "requested_counts": args.counts, "requested_cases": args.cases,
              "numeric_repeats": args.repeats, "render_counts": args.render_counts,
              "browser_execution": "not_verified_by_this_harness", "results": results,
              "memory_growth_checks": memory_checks, "errors": errors}
    encoded = json.dumps(report, indent=2, allow_nan=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(encoded + "\n")
    else:
        print(encoded)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
