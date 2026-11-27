"""Future real-native-head consumer; no product imports or execution on import.

Run ONLY after R04 supplies the actual new native head and source-hash manifest.
Arguments below belong to this test harness, not to the DeepViz product CLI.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.util
import json
import os
import re
import struct
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

PACKAGE = Path("python/deepviz/src/deepviz")
INLINE_CSV = "category,value\nInline North,9\nInline South,-4\nInline West,7\n"
FILE_CSV = "category,value\nFile East,2\nFile West,5\nFile North,-8\nFile South,1\n"
INLINE_ROWS = [("Inline North", 9), ("Inline South", -4), ("Inline West", 7)]
FILE_ROWS = [("File East", 2), ("File West", 5), ("File North", -8), ("File South", 1)]
SPEC = {"kind": "bar", "x": "category", "y": "value", "format": "csv",
        "aggregation": "none", "max_points": 100, "width": 640, "height": 400,
        "title": "R33 literal $(NOT_A_COMMAND) ../outside.csv"}
INVALID_SPEC = {"kind": "not-a-chart", "command": "__R33_COMMAND_IS_DATA__"}
ARTIFACT_NAMES = {"chart.png", "chart.svg", "chart.html", "manifest.json"}


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def git(source: Path, *arguments: str) -> bytes:
    return subprocess.run(["git", "-C", str(source), *arguments], check=True,
                          capture_output=True, timeout=30).stdout


def verify_source(source: Path, commit: str, manifest: dict[str, Any]) -> dict[str, Any]:
    """Prove the complete Python package against immutable Git bytes BEFORE import."""
    require(re.fullmatch(r"[0-9a-f]{40}", commit) is not None, "Need the actual full native commit")
    require(manifest.get("commit") == commit, "Hash manifest must name this exact native head")
    require(git(source, "rev-parse", "HEAD").decode().strip() == commit, "Source HEAD drift")
    package = source / PACKAGE
    files = manifest.get("files")
    if not isinstance(files, dict) or not files:
        raise AssertionError("Need explicit complete package SHA256 files")
    actual = {path.relative_to(source).as_posix() for path in package.rglob("*.py")}
    require(set(files) == actual and bool(actual), "Missing/extra Python package source")
    origins = {}
    for relative in sorted(actual):
        path = source / relative
        require(path.resolve().is_relative_to(package.resolve()), "Source escapes explicit package root")
        blob = git(source, "show", f"{commit}:{relative}")
        working = path.read_bytes()
        require(working.replace(b"\r\n", b"\n") == blob.replace(b"\r\n", b"\n"), "Uncommitted source drift")
        require(files[relative] == sha256(blob), f"Wrong supplied Git SHA256: {relative}")
        origins[relative] = {"git_sha256": sha256(blob), "working_sha256": sha256(working)}
    return {"commit": commit, "source_root": str(source), "modules": origins}


def loaded_origins(source: Path, proof: dict[str, Any]) -> list[dict[str, str]]:
    result = []
    for name, module in sorted(sys.modules.items()):
        if name != "deepviz" and not name.startswith("deepviz."):
            continue
        origin = getattr(module, "__file__", None)
        if not isinstance(origin, str):
            raise AssertionError(f"Unproven package namespace {name}")
        path = Path(origin).resolve()
        require(path.is_relative_to(source / PACKAGE), f"Editable/other-checkout leak: {name}")
        relative = path.relative_to(source).as_posix()
        require(relative in proof["modules"], f"Unmanifested loaded module: {name}")
        observed = sha256(path.read_bytes())
        require(observed == proof["modules"][relative]["working_sha256"], f"Post-proof drift: {name}")
        result.append({"module": name, "origin": str(path), "sha256": observed})
    require(any(row["module"] == "deepviz.render" for row in result), "Public render module not loaded")
    return result


def snapshot(root: Path) -> dict[str, Any]:
    return {"directories": sorted(path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_dir()),
            "files": {path.relative_to(root).as_posix(): sha256(path.read_bytes())
                      for path in root.rglob("*") if path.is_file()}}


def check_artifact(result: dict[str, Any], output: Path, rows: list[tuple[str, int]]) -> dict[str, Any]:
    require(result.get("engine") == "matplotlib", "Not the requested native engine")
    for key in ("input_count", "output_count"):
        require(type(result.get(key)) is int and result[key] == len(rows), f"Wrong {key}")
    paths = result.get("paths")
    if not isinstance(paths, list) or len(paths) != 4:
        raise AssertionError("Need four actual native artifact paths")
    resolved = []
    for item in paths:
        require(isinstance(item, str), "Artifact path must be text")
        path = Path(item)
        require(path.is_absolute() and not path.is_symlink(), "Artifact is not an absolute regular file")
        path = path.resolve(strict=True)
        require(path.is_file() and path.is_relative_to(output.resolve()), "Artifact escapes own output root")
        resolved.append(path)
    require({path.name for path in resolved} == ARTIFACT_NAMES, "Missing/duplicate artifact formats")
    require(len({path.parent for path in resolved}) == 1, "Artifact set split across directories")
    folder = resolved[0].parent
    require(folder != output.resolve(), "Expected a fresh artifact child, not overwrite-prone output root")
    require({path.name for path in folder.iterdir()} == ARTIFACT_NAMES, "Unexpected artifact-set files")
    png = (folder / "chart.png").read_bytes()
    require(png.startswith(b"\x89PNG\r\n\x1a\n") and png[12:16] == b"IHDR", "Not an actual PNG header")
    dimensions = struct.unpack(">II", png[16:24])
    require(all(value > 0 for value in dimensions) and b"IDAT" in png and b"IEND" in png, "Incomplete PNG")
    svg = ET.fromstring((folder / "chart.svg").read_bytes())
    require(svg.tag.endswith("}svg") and any(node.tag.endswith("}path") for node in svg.iter()), "No SVG graphics")
    html = (folder / "chart.html").read_text(encoding="utf-8")
    require("<html" in html.lower() and "chart.svg" in html, "Native HTML must reference its own SVG")
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    require(manifest.get("engine") == "matplotlib" and len(manifest.get("charts", [])) == 1, "Wrong manifest engine/chart")
    chart = manifest["charts"][0]
    require(chart.get("requested_kind") == chart.get("rendered_kind") == "bar", "Unexpected fallback")
    require(chart.get("input_count") == chart.get("output_count") == len(rows), "Manifest counts differ")
    require(chart.get("spec", {}).get("title") == SPEC["title"], "Model title was not retained literally")
    records = chart.get("records")
    require(isinstance(records, list) and len(records) == len(rows), "Manifest rows missing")
    # CSV values can remain numeric strings or normalized numbers; never compute expected data with product code.
    actual = [(record["category"], float(record["value"])) for record in records]
    require(actual == rows, "Literal CSV versus authorized-file contents were confused or lost")
    require((output / "chart.png").read_bytes() == b"HOST OWNED - DO NOT REPLACE\n", "Host file overwritten")
    return {"counts": len(rows), "png_dimensions": list(dimensions), "files": [
        {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path.read_bytes())} for path in resolved]}


def api_worker(config: dict[str, Any]) -> dict[str, Any]:
    source = Path(config["source"]).resolve(strict=True)
    proof = verify_source(source, config["commit"], config["manifest"])
    candidate = importlib.util.find_spec("deepviz")
    if candidate is None or candidate.origin is None:
        raise AssertionError("No explicit source package")
    require(Path(candidate.origin).resolve() == source / PACKAGE / "__init__.py", "Wrong package before import")
    renderer = importlib.import_module("deepviz.render").render
    cli = importlib.util.find_spec("deepviz.cli")
    if cli is None or cli.origin is None:
        raise AssertionError("Actual CLI module absent")
    require(Path(cli.origin).resolve() == source / PACKAGE / "cli.py", "Wrong actual CLI entry point")
    root = Path(config["root"])
    checks = {}
    for name, data, rows in (("api-inline", INLINE_CSV, INLINE_ROWS),
                             ("api-path", root / "inputs/authorized.csv", FILE_ROWS)):
        artifact = renderer(data, dict(SPEC), engine="matplotlib", output_dir=root / "outputs" / name)
        checks[name] = check_artifact(artifact.model_dump(mode="json"), root / "outputs" / name, rows)
    for name, spec in (("api-invalid", INVALID_SPEC),
                       ("api-model-selector", {**SPEC, "data_path": str(root / "outside/outside.csv")})):
        output = root / "outputs" / name
        before = snapshot(output)
        try:
            renderer(INLINE_CSV, spec, engine="matplotlib", output_dir=output)
        except ValueError as rejected:
            require(0 < len(str(rejected).encode()) < 4096, "Expected concise declared validation error")
            checks[name] = {"rejected_type": type(rejected).__name__, "new_artifacts": 0}
        else:
            raise AssertionError(f"Model/spec strings gained unsupported execution/path behavior: {name}")
        require(snapshot(output) == before, "Invalid specification allocated artifacts or touched host files")
    return {"source_proof": proof, "loaded_modules": loaded_origins(source, proof), "checks": checks,
            "CLI_origin": str(Path(cli.origin).resolve()), "execution_mode": "real API, isolated -S child"}


def invoke(arguments: list[str], root: Path, environment: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(arguments, cwd=root, env=environment, capture_output=True,
                          text=True, encoding="utf-8", timeout=120, shell=False)


def consume(args: argparse.Namespace) -> dict[str, Any]:
    source = args.source_root.resolve(strict=True)
    manifest = json.loads(args.hash_manifest.read_text(encoding="utf-8"))
    proof = verify_source(source, args.expected_commit, manifest)
    dependency = args.dependency_root.resolve(strict=True)
    require(dependency.is_dir() and not dependency.is_relative_to(source / PACKAGE), "Need explicit read-only dependency root")
    parent = args.work_root.resolve(strict=True)
    require(parent.is_dir() and not parent.is_relative_to(source), "Use an OWN work parent outside product source")
    root = Path(tempfile.mkdtemp(prefix="r33-native-consumer-", dir=parent)).resolve()
    for name in ("inputs", "outside", "scratch", "mpl-config", "outputs"):
        (root / name).mkdir()
    (root / "inputs/inline.csv").write_text(INLINE_CSV, encoding="utf-8")
    (root / "inputs/authorized.csv").write_text(FILE_CSV, encoding="utf-8")
    (root / "inputs/spec.json").write_text(json.dumps(SPEC), encoding="utf-8")
    (root / "inputs/invalid.json").write_text(json.dumps(INVALID_SPEC), encoding="utf-8")
    (root / "outside/outside.csv").write_text("category,value\nMUST NOT BE INGESTED,987654\n", encoding="utf-8")
    (root / "outside/command-sentinel").write_bytes(b"NOT COMMAND AUTHORITY\n")
    case_names = ("api-inline", "api-path", "api-invalid", "api-model-selector", "cli-inline", "cli-path", "cli-invalid")
    for name in case_names:
        output = root / "outputs" / name
        output.mkdir()
        (output / "chart.png").write_bytes(b"HOST OWNED - DO NOT REPLACE\n")
    protected = {name: snapshot(root / name) for name in ("inputs", "outside")}
    config = {"source": str(source), "commit": args.expected_commit, "manifest": manifest, "root": str(root)}
    config_path = root / "consumer-config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    environment = {**os.environ, "PYTHONPATH": os.pathsep.join([str(source / PACKAGE.parent), str(dependency)]),
                   "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1", "MPLBACKEND": "Agg",
                   "MPLCONFIGDIR": str(root / "mpl-config"), "TMP": str(root / "scratch"), "TEMP": str(root / "scratch"),
                   "TMPDIR": str(root / "scratch")}
    # -S bypasses editable-main .pth hooks; no installed source/dependency copying or installation.
    process = invoke([sys.executable, "-S", str(Path(__file__).resolve()), "_api", str(config_path)], root, environment)
    require(process.returncode == 0, f"API child failed ({process.returncode}): {process.stderr[-4096:]}")
    observed = {"API": json.loads(process.stdout), "CLI": {}, "source_proof": proof}
    for name, filename, rows in (("cli-inline", "inline.csv", INLINE_ROWS), ("cli-path", "authorized.csv", FILE_ROWS)):
        output = root / "outputs" / name
        # These are the actual read candidate's flags, not a test-only replacement entry point.
        command = [sys.executable, "-S", "-m", "deepviz.cli", "render", str(root / "inputs" / filename),
                   "--spec", str(root / "inputs/spec.json"), "--engine", "matplotlib", "--output-dir", str(output)]
        response = invoke(command, root, environment)
        require(response.returncode == 0 and "Traceback" not in response.stderr, "Real CLI success/exit contract failed")
        result = json.loads(response.stdout)
        require(isinstance(result, dict), "CLI stdout is not one JSON object")
        observed["CLI"][name] = {"command": command, "exit": response.returncode,
                                 "artifact": check_artifact(result, output, rows)}
    output = root / "outputs/cli-invalid"
    before = snapshot(output)
    command = [sys.executable, "-S", "-m", "deepviz.cli", "render", str(root / "inputs/authorized.csv"),
               "--spec", str(root / "inputs/invalid.json"), "--engine", "matplotlib", "--output-dir", str(output)]
    response = invoke(command, root, environment)
    require(response.returncode == 2 and not response.stdout.strip(), "CLI invalid-spec exit/stdout contract failed")
    require("deepviz: error:" in response.stderr and "Traceback" not in response.stderr
            and len(response.stderr.encode()) < 4096, "Expected existing concise CLI stderr, not invented JSON error")
    require(snapshot(output) == before, "Invalid CLI spec allocated output or overwrote host sentinel")
    observed["CLI"]["cli-invalid"] = {"command": command, "exit": response.returncode, "new_artifacts": 0}
    require(all(snapshot(root / name) == value for name, value in protected.items()), "Input/outside sentinel mutation")
    for name in case_names:
        require((root / "outputs" / name / "chart.png").read_bytes() == b"HOST OWNED - DO NOT REPLACE\n", "Host sentinel mutation")
    observed.update({"work_root": str(root), "status": "PASS", "visual_inspection": "NOT RUN; separate06 gate",
                     "raw_path_string_API_contract": "NOT CLAIMED; R04 decision required", "protected_roots_unchanged": True})
    (root / "consumer-result.json").write_text(json.dumps(observed, indent=2) + "\n", encoding="utf-8")
    return observed


def main() -> int:
    if len(sys.argv) == 3 and sys.argv[1] == "_api":
        print(json.dumps(api_worker(json.loads(Path(sys.argv[2]).read_text(encoding="utf-8")))))
        return 0
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--hash-manifest", type=Path, required=True)
    parser.add_argument("--dependency-root", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    print(json.dumps(consume(parser.parse_args()), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
