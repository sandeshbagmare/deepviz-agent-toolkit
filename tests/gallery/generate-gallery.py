"""Generate real public-render artifacts; generation is not visual acceptance.

Example: python tests/gallery/generate-gallery.py --output artifacts/local/gallery-new
Bounded smoke: append --engine matplotlib --case bar-light. Repeat selectors
to choose a subset. The output directory must not already exist. Source snapshots
make every manifest path local and portable without inventing an import identity.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ENGINES = ("matplotlib", "plotly", "vega", "echarts", "antv")
CASES = ("bar-light", "line-numeric", "dashboard-mixed")
ROOT = Path(__file__).resolve().parents[2]


def known_case(name: str) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    """Return fresh input/spec/oracle, independent of any renderer observations."""
    common = {"aggregation": "none", "width": 900, "height": 520, "theme": "light"}
    if name == "bar-light":
        points: list[list[Any]] = [["Alpha", 2], ["Beta", 5], ["Gamma", 9]]
        kind, x, y = "bar", "category", "value"
    elif name == "line-numeric":
        points = [[1, 2], [2, 8], [4, 5]]
        kind, x, y = "line", "x", "y"
    elif name == "dashboard-mixed":
        points = [["A", 3], ["B", 7]]
        children = [{"kind": "bar", "title": f"{theme.title()} panel: A=3, B=7",
                     "x": "category", "y": "value", "theme": theme,
                     "aggregation": "none", "width": 420, "height": 400}
                    for theme in ("light", "dark")]
        return (
            [{"category": label, "value": value} for label, value in points],
            {**common, "kind": "dashboard", "title": "Mixed light/dark dashboard: A=3, B=7",
             "columns": 2, "charts": children},
            {"input_count": 2, "output_count": 4, "charts": [
                {"kind": "bar", "theme": theme, "points": [["A", 3], ["B", 7]], "zero_baseline": True}
                for theme in ("light", "dark")]},
        )
    else:
        raise ValueError(f"Unknown case {name!r}; choose from {', '.join(CASES)}")
    return (
        [{x: label, y: value} for label, value in points],
        {**common, "kind": kind, "title": f"{name}: known measurements", "x": x, "y": y},
        {"input_count": 3, "output_count": 3,
         "charts": [{"kind": kind, "theme": "light", "points": points,
                     "numeric_x": name == "line-numeric", "zero_baseline": name == "bar-light"}]},
    )


def git(repo: Path, *args: str) -> str:
    """Only fixed Git inspection commands below call this; no shell/spec input."""
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True, stderr=subprocess.PIPE).strip()


def snapshot_modules(repo: Path, output: Path) -> list[dict[str, str]]:
    """Verify actual module bytes against HEAD, then preserve those exact bytes."""
    package = repo / "python/deepviz/src/deepviz"
    tracked = {}
    for line in git(repo, "ls-tree", "-r", "HEAD", "--", "python/deepviz/src/deepviz").splitlines():
        metadata, relative = line.split("\t", 1)
        tracked[relative] = metadata.split()[2]
    modules = []
    for path in sorted(package.rglob("*.py")):
        if not path.resolve().is_relative_to(package.resolve()):
            raise ValueError(f"Source module leaves selected package: {path.name}")
        relative = path.relative_to(repo).as_posix()
        content = path.read_bytes()
        blob_hash = hashlib.sha1(f"blob {len(content)}\0".encode() + content, usedforsecurity=False).hexdigest()
        if tracked.get(relative) != blob_hash:
            raise ValueError(f"Source module differs from selected Git HEAD: {relative}")
        destination = output / "source" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as stream:
            stream.write(content)
        modules.append({"path": destination.relative_to(output).as_posix(),
                        "sha256": hashlib.sha256(content).hexdigest()})
    if not modules:
        raise ValueError("Selected source has no Python modules")
    return modules


def generate_item(repo: Path, output: Path, case: str, engine: str) -> dict[str, Any]:
    if engine not in ENGINES:
        raise ValueError(f"Unknown engine {engine!r}; choose from {', '.join(ENGINES)}")
    data, raw_spec, expected = known_case(case)
    public = importlib.import_module("deepviz")
    origin = public.__file__
    if origin is None:
        raise ValueError("Public package has no inspectable source file")
    imported = Path(origin).resolve()
    if imported != repo / "python/deepviz/src/deepviz/__init__.py":
        raise ValueError(f"Public package imported outside selected source: {imported}")
    print(f"gallery source import: {imported}", file=sys.stderr)
    chart = public.ChartSpec.model_validate(raw_spec)
    item_id = f"{case}-{engine}"
    artifact = public.render(data, chart, engine=engine, output_dir=output / item_id)
    files = []
    for name in artifact.paths:
        path = Path(name).resolve(strict=True)
        if not path.is_relative_to((output / item_id).resolve()):
            raise ValueError("Public artifact path leaves its exclusive item directory")
        content = path.read_bytes()
        files.append({"path": path.relative_to(output).as_posix(), "bytes": len(content),
                      "sha256": hashlib.sha256(content).hexdigest()})
    paths = [file["path"] for file in files]
    entry = next((name for suffix in (".html", ".svg", ".png") for name in paths
                  if str(name).lower().endswith(suffix)), None)
    native = next((name for name in paths if Path(str(name)).name == "manifest.json"), None)
    if entry is None or native is None:
        raise ValueError("Public artifact lacks an HTML/SVG/PNG entry or native manifest")
    if (artifact.input_count, artifact.output_count) != (expected["input_count"], expected["output_count"]):
        raise ValueError(f"Public artifact counts differ from known fixture: {artifact.input_count}, "
                         f"{artifact.output_count}; expected {expected['input_count']}, {expected['output_count']}")
    return {"id": item_id, "case": case, "engine": engine, "spec": chart.model_dump(mode="json"),
            "expected": expected, "input_count": artifact.input_count, "output_count": artifact.output_count,
            "strategy": artifact.strategy, "warnings": list(artifact.warnings), "entry_path": entry,
            "files": files, "native_manifest_path": native}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", type=Path, required=True, help="Exclusive new output directory")
    parser.add_argument("--source-root", type=Path, default=ROOT, help="Git checkout to import explicitly")
    parser.add_argument("--engine", action="append", nargs="?", const="", help="Repeat; default all five engines")
    parser.add_argument("--case", action="append", nargs="?", const="", help="Repeat; default all three known cases")
    args = parser.parse_args(argv)
    repo, output = args.source_root.resolve(), args.output.resolve()
    try:
        commit = git(repo, "rev-parse", "HEAD")
        if re.fullmatch(r"[0-9a-f]{40}", commit) is None:
            raise ValueError("Selected source must have a full 40-hex Git commit")
        output.mkdir(parents=True, exist_ok=False)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        return 2
    manifest: dict[str, Any] = {
        "version": 1, "source": {"commit": commit, "module_files": [], "python_version": sys.version},
        "items": [], "failures": [],
    }
    try:
        manifest["source"]["module_files"] = snapshot_modules(repo, output)
        sys.path.insert(0, str(repo / "python/deepviz/src"))
        engines = list(dict.fromkeys(args.engine if args.engine is not None else ENGINES))
        cases = list(dict.fromkeys(args.case if args.case is not None else CASES))
        for case in cases:
            for engine in engines:
                try:
                    manifest["items"].append(generate_item(repo, output, case, engine))
                except Exception as error:
                    manifest["failures"].append({"case": case, "engine": engine,
                                                 "error": f"{type(error).__name__}: {error}"})
                # Preserve successful/failed progress even if a later renderer interrupts.
                (output / "gallery-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    except Exception as error:
        manifest["failures"].append({"error": f"{type(error).__name__}: {error}"})
    (output / "gallery-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"manifest": str(output / "gallery-manifest.json"), "items": len(manifest["items"]),
                      "failures": len(manifest["failures"]), "source_commit": commit}))
    return int(bool(manifest["failures"]))


if __name__ == "__main__":
    raise SystemExit(main())
