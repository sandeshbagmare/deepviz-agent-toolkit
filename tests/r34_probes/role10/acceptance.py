"""Run immutable COUNT gates once on exact857; never modify source or old oracles."""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib
import io
import json
import os
import shutil
import struct
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

SOURCE = "85796dbe3360fb88686f2e7188122e2da80d54c2"
ORACLE = "76cac9d05b0b4abc94e5ff316e3de4d3bc835b79"
AUTHOR_HASH = "8270a4748ee5c5f20e9d7cce92674aefad43d7c151dd41709c702446a1b5c683"
ORACLE_HASHES = {
    "test_count_measure.py": "c09f6a052afb4822e3bf06e6877d2e061810fd71d423049152c2b098f9325d54",
    "count_contract.py": "0e0d468a5d70a3f36f8dda088ffa09e73da031952168e0ecd0cd6918b1940cd1",
    "collect_visuals.py": "afd8a6c65809dfa858ac61d1b9ed2406ba41f709cec253d7bf0e7b9ac893c929",
    "browser-count.cjs": "84ca2c022efdb08624f8e082fd0d6dc8d8a22cc8ce1097f91f843aff52159eee",
}
PRODUCT_HASHES = {
    "engines": "54b9b6ced08b276b87c143334c8b54110ea7f15e52e0b283d65c911fdba6bb18",
    "normalize": "34e8ed94a479acb2d7360a79ba4f62897bb453928fc1eec97efceb052a5e76f2",
    "models": "890ecb0e29e1345364b2bf4840bdea7a542067003caf54d7b0855536ee2b6a76",
    "render": "69357040b7f94da6b92b66a91e378645d3108a77d8c55dc7c60d950f174ab5a3",
}
PAIRS = [["A", 2], ["B", 3], ["C", 1]]
RECORDS = [{"group": "A", "series": 90, "count": 2}, {"group": "B", "series": 80, "count": 3},
           {"group": "C", "series": 70, "count": 1}]


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def git(source: Path, *arguments: str) -> bytes:
    return subprocess.run(["git", "-C", str(source), *arguments], check=True,
                          capture_output=True, timeout=30).stdout


def prove(source: Path, oracle: Path, loaded: bool) -> dict[str, Any]:
    assert git(source, "rev-parse", "HEAD").decode().strip() == SOURCE
    assert not git(source, "status", "--porcelain", "--untracked-files=no")
    modules = []
    for name, expected in PRODUCT_HASHES.items():
        relative = f"python/deepviz/src/deepviz/{name}.py"
        path = (source / relative).resolve()
        data = path.read_bytes()
        assert data == git(source, "show", f"{SOURCE}:{relative}")
        assert digest(data) == expected
        if loaded:
            module = importlib.import_module("deepviz." + name)
            assert module.__file__ is not None and Path(module.__file__).resolve() == path
        modules.append({"module": name, "origin": str(path), "sha256": expected, "loaded_checked": loaded})
    for name, expected in ORACLE_HASHES.items():
        data = (oracle / name).read_bytes()
        assert digest(data) == expected
        assert data == git(source, "show", f"{ORACLE}:tests/r15_probes/role17/{name}")
    author = source / "python/deepviz/tests/test_r23_count_channel.py"
    assert digest(author.read_bytes()) == AUTHOR_HASH
    assert author.read_bytes() == git(source, "show", f"{SOURCE}:python/deepviz/tests/{author.name}")
    return {"source_sha": SOURCE, "four_modules": modules, "oracle_commit": ORACLE,
            "unchanged_oracle_hashes": ORACLE_HASHES, "unchanged_author_hash": AUTHOR_HASH}


def pytest_once(target: Path, output: Path, label: str, expected: int, semantic: bool = False) -> dict[str, Any]:
    pytest = importlib.import_module("pytest")
    xml = output / f"{label}.xml"
    arguments = [str(target), "-q", "-rs", "--strict-markers", "-p", "no:cacheprovider",
                 "--basetemp", str(output / f"{label}-tmp"), "--junitxml", str(xml)]
    if semantic:
        arguments += ["-k", "not loaded_modules_match_pinned_source_identity"]
    stdout, stderr = io.StringIO(), io.StringIO()
    start = time.perf_counter()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        code = int(pytest.main(arguments))
    elapsed = time.perf_counter() - start
    (output / f"{label}.stdout.log").write_text(stdout.getvalue(), encoding="utf-8")
    (output / f"{label}.stderr.log").write_text(stderr.getvalue(), encoding="utf-8")
    suite = ET.parse(xml).getroot().find("testsuite") if xml.exists() else None
    counts = {key: int(suite.get(key, "0")) if suite is not None else -1
              for key in ("tests", "failures", "errors", "skipped")}
    expected_counts = {"tests": expected, "failures": 0, "errors": 0, "skipped": 0}
    return {"invocation": "pytest.main(argv), unchanged files", "argv": arguments, "exit": code,
            "elapsed_seconds": elapsed, "counts": counts, "pass": code == 0 and counts == expected_counts,
            "deselected_obsolete_identity_only": 1 if semantic else 0,
            "old_identity_not_numeric_waiver": semantic, "xml_sha256": digest(xml.read_bytes()) if xml.exists() else None}


def payload_pairs(engine: str, payload: dict[str, Any]) -> list[list[Any]]:
    if engine == "plotly":
        return [[x, y] for trace in payload["data"] for x, y in zip(trace["x"], trace["y"], strict=True)]
    if engine == "vega":
        encoding = payload["encoding"]
        assert encoding["y"]["type"] == "quantitative"
        return [[row[encoding["x"]["field"]], row[encoding["y"]["field"]]] for row in payload["data"]["values"]]
    if engine == "echarts":
        assert payload["yAxis"]["type"] == "value"
        return [list(item["value"][:2]) if isinstance(item, dict) else list(item[:2])
                for series in payload["series"] for item in series["data"]]
    return [[row[payload["encode"]["x"]], row[payload["encode"]["y"]]] for row in payload["data"]]


def retained_outputs(output: Path) -> dict[str, Any]:
    manifests = list((output / "semantic55-tmp").rglob("manifest.json"))
    assert len(manifests) == 5
    observed = {}
    for path in manifests:
        manifest = json.loads(path.read_text(encoding="utf-8"))
        engine = manifest["engine"]
        assert engine not in observed
        chart = manifest["charts"][0]
        assert len(manifest["charts"]) == 1 and chart["records"] == RECORDS
        assert (chart["input_count"], chart["output_count"], chart["strategy"]) == (6, 3, "count")
        assert chart["requested_kind"] == chart["rendered_kind"] == "bar"
        entry = {"manifest_path": str(path), "manifest_sha256": digest(path.read_bytes()),
                 "input_count": 6, "output_count": 3, "strategy": "count", "retained_series": [90, 80, 70],
                 "warnings": manifest["warnings"]}
        if engine != "matplotlib":
            pairs = payload_pairs(engine, manifest["native_specs"][0])
            assert pairs == PAIRS
            entry["actual_native_pairs"] = pairs
            entry["browser_paint"] = "NOT RUN; payload is not paint/CDN acceptance"
        else:
            folder = path.parent
            png, svg = folder / "chart.png", folder / "chart.svg"
            raw = png.read_bytes()
            assert raw.startswith(b"\x89PNG\r\n\x1a\n")
            assert struct.unpack(">II", raw[16:24]) == (720, 440)
            xml = ET.fromstring(svg.read_bytes())
            assert xml.tag.endswith("}svg") and any(node.tag.endswith("}path") for node in xml.iter())
            retained = output / "inspect-matplotlib"
            retained.mkdir()
            for artifact in (png, svg, path):
                shutil.copyfile(artifact, retained / artifact.name)
            entry.update({"PNG": str(retained / "chart.png"), "SVG": str(retained / "chart.svg"),
                          "PNG_sha256": digest(raw), "SVG_sha256": digest(svg.read_bytes()),
                          "dimensions": [720, 440], "artist_pairs_verified_by": "unchanged17 native measure oracle",
                          "visual_inspection": "PENDING actual image-open by tester, not file existence proof"})
        observed[engine] = entry
    assert set(observed) == {"matplotlib", "plotly", "vega", "echarts", "antv"}
    return observed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--oracle-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source, oracle, output = args.source.resolve(), args.oracle_dir.resolve(), args.output.resolve()
    assert sys.flags.no_site == 1 and not sys.flags.optimize, "Use python -S without -O; keep assertions active"
    assert output != source and not output.is_relative_to(source), "Output must be a unique OWN temp root"
    output.mkdir(parents=True, exist_ok=False)
    for name in ("tmp", "mpl"):
        (output / name).mkdir()
    os.environ.update({"MPLBACKEND": "Agg", "MPLCONFIGDIR": str(output / "mpl"), "PYTHONDONTWRITEBYTECODE": "1",
                       "TMP": str(output / "tmp"), "TEMP": str(output / "tmp"), "TMPDIR": str(output / "tmp")})
    result: dict[str, Any] = {"source_sha": SOURCE, "oracle_commit": ORACLE, "results": [],
                              "browser": "NOT RUN; bounded Matplotlib PNG+SVG selected", "visual_inspection": "PENDING"}
    try:
        result["before_import"] = prove(source, oracle, False)
        sys.path.insert(0, str(source / "python/deepviz/src"))
        sys.path.insert(0, str(oracle))
        result["before_tests"] = prove(source, oracle, True)
        os.chdir(source)
        for target, label, count, semantic in ((source / "python/deepviz/tests/test_r23_count_channel.py", "author16", 16, False),
                                                (oracle / "test_count_measure.py", "semantic55", 55, True)):
            result["results"].append(pytest_once(target, output, label, count, semantic))
            result[label + "_post_identity"] = prove(source, oracle, True)
        if all(entry["pass"] for entry in result["results"]):
            result["actual_artifacts"] = retained_outputs(output)
        result["after_tests_and_collection"] = prove(source, oracle, True)
        result["status"] = "PASS_SELECTED_TESTS" if all(entry["pass"] for entry in result["results"]) else "FAIL_SELECTED_TESTS"
        return 0 if result["status"] == "PASS_SELECTED_TESTS" else 1
    except Exception as error:
        result.update({"status": "ERROR", "error_type": type(error).__name__, "error": str(error)})
        raise
    finally:
        (output / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({key: value for key, value in result.items() if key in {"status", "results", "error_type", "error"}}, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
