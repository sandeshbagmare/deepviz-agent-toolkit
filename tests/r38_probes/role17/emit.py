"""Emit distinct caller-authored AntV acceptance artifacts from exact Git source."""
from __future__ import annotations

import copy
import hashlib
import importlib
import json
import sys
from pathlib import Path


def main():
    identity_path = Path(sys.argv[1]).resolve(strict=True)
    identity = json.loads(identity_path.read_text(encoding="utf-8"))
    assert identity["source"] == "3185e0d9936c7d6f1a9d30b94089b804d75fe991" and sys.flags.no_site == 1
    source = Path(identity["source_root"])
    sys.path[:0] = [str(source / "python/deepviz/src"), identity["readonly_site_packages"]]
    output = Path(sys.argv[2]).resolve()
    output.mkdir(parents=True, exist_ok=False)
    fixtures_path = Path(__file__).with_name("fixtures.json")
    fixtures = json.loads(fixtures_path.read_text(encoding="utf-8"))

    def proof():
        for row in identity["Git_exact_source_files"]:
            assert hashlib.sha256((source / row["path"]).read_bytes()).hexdigest() == row["sha256"]
        for row in identity["own_probe_files"]:
            assert hashlib.sha256(Path(row["path"]).read_bytes()).hexdigest() == row["sha256"]
        assert hashlib.sha256(Path(identity["G2"]["path"]).read_bytes()).hexdigest() == identity["G2"]["sha256"]

    proof()
    modules = []
    for name in ("deepviz", "deepviz.models", "deepviz.engines", "deepviz.render", "deepviz.normalize"):
        module = importlib.import_module(name)
        actual = Path(module.__file__).resolve()
        relative = actual.relative_to(source).as_posix()
        expected = next(row for row in identity["Git_exact_source_files"] if row["path"] == relative)
        assert hashlib.sha256(actual.read_bytes()).hexdigest() == expected["sha256"]
        modules.append({"module": name, "actual_file": str(actual), "sha256": expected["sha256"]})
    from deepviz import render

    emitted, checks = [], []

    def check(case, name, condition, actual):
        checks.append({"id": case, "name": name, "pass": bool(condition), "actual": actual})

    for original in fixtures["cases"]:
        case = copy.deepcopy(original)
        mode = case["mode"]
        spec = {"aggregation": "none", "width": 1280 if mode == "dashboard" else 960,
                "height": 520, "title": "Independent R38-17 " + case["id"], **case.get("spec", {})}
        if mode == "heat":
            rows = [{"column": xy[0], "row": xy[1], "heat": value}
                    for xy, value in zip(fixtures["grid"], case["values"], strict=True)]
            spec.update(kind="heatmap", x="column", y="row", color="heat", theme="light")
        elif mode == "position":
            rows = copy.deepcopy(case["rows"])
            spec.update(kind="scatter", x="x", y="y", theme="dark")
        else:
            rows = copy.deepcopy(fixtures["category_rows"])
            spec.update(x="sector", y="quantity")
        before = copy.deepcopy((rows, spec))
        artifact = render(rows, spec, "antv", output / case["id"])
        manifest_path = next(Path(name) for name in artifact.paths if name.endswith("manifest.json"))
        html_path = next(Path(name) for name in artifact.paths if name.endswith(".html"))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        check(case["id"], "public-input-and-spec-not-mutated", (rows, spec) == before, True)
        check(case["id"], "literal-input-and-record-count-preserved", artifact.input_count == 4 and
              all(chart["records"] == rows and chart["input_count"] == 4 and chart["output_count"] == 4
                  for chart in manifest["charts"]), artifact.to_dict())
        for native in manifest["native_specs"]:
            if mode == "heat":
                check(case["id"], "literal-heat-values", [row["_heat"] for row in native["data"]] ==
                      case["expected_values"], native["data"])
                check(case["id"], "literal-finite-domain", native["scale"]["color"]["domain"] ==
                      case["expected_domain"], native["scale"]["color"])
                check(case["id"], "missing-is-omission-not-zero", ("missing" not in case["id"] or
                      any("omitted" in warning for warning in artifact.warnings)), artifact.warnings)
            elif mode == "position":
                check(case["id"], "literal-numeric-x-y", [[row["_x"], row["_y"]] for row in native["data"]]
                      == case["expected_xy"], native["data"])
            else:
                check(case["id"], "literal-four-category-labels-true-values",
                      [[row["_x"], row["_y"]] for row in native["data"]] == fixtures["category_expected"], native["data"])
                check(case["id"], "categorical-color-not-fixed-paint", not {"fill", "stroke"}.intersection(
                      native.get("style", {})) and native["encode"]["color"] == "_x", native)
        if mode == "dashboard":
            check(case["id"], "literal-child-native-themes", [native["theme"] for native in manifest["native_specs"]]
                  == case["expected_child_themes"], [native["theme"] for native in manifest["native_specs"]])
        emitted.append({**case, "spec": spec, "rows": rows, "manifest": manifest, "artifact": artifact.to_dict(),
                        "html": str(html_path.relative_to(output)),
                        "html_sha256": hashlib.sha256(html_path.read_bytes()).hexdigest()})
    proof()
    result = {"identity": identity, "actual_modules": modules, "python": sys.version, "sys_path": sys.path,
              "fixtures_sha256": hashlib.sha256(fixtures_path.read_bytes()).hexdigest(),
              "category_expected": fixtures["category_expected"], "category_ratios": fixtures["category_ratios"],
              "checks": checks, "cases": emitted, "source_and_probe_and_G2_before_after_exact": True}
    (output / "cases.json").write_text(json.dumps(result, indent=2), encoding="utf-8", newline="\n")
    totals = {"cases": len(emitted), "checks": len(checks), "failed": sum(not row["pass"] for row in checks), "skipped": 0}
    print(json.dumps(totals))
    return int(bool(totals["failed"]))


if __name__ == "__main__":
    raise SystemExit(main())
