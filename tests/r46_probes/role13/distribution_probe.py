"""Offline declared-backend archive gates; manual unpack is NOT installation."""

from __future__ import annotations

import argparse
import base64
import configparser
import csv
import hashlib
import importlib
import importlib.metadata
import importlib.util
import io
import json
import os
import stat
import subprocess
import sys
import tarfile
import tempfile
import time
import tomllib
import zipfile
from datetime import UTC, datetime
from email.parser import BytesParser
from email.policy import default
from pathlib import Path, PurePosixPath


def digest(data):
    return hashlib.sha256(data).hexdigest()


def save(out, name, value):
    with (out / name).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def source_check(proof):
    source = Path(proof["source"])
    for argv, expected in [
        (["git", "rev-parse", "HEAD"], (proof["actual_default_sha"] + "\n").encode()),
        (["git", "status", "--porcelain"], b""),
    ]:
        result = subprocess.run(argv, cwd=source, capture_output=True, check=True)
        assert result.stdout.replace(b"\r\n", b"\n") == expected
    for item in proof["source_files"]:
        assert digest((source / item["path"]).read_bytes()) == item["raw_sha256"]
    return source


def cached_check(proof, load=False):
    for item in proof["files"]:
        assert digest(Path(item["path"]).read_bytes()) == item["sha256"]
    assert len(proof["files"]) == 183
    if not load:
        return {"files_verified": 183, "unchanged": True}
    sys.path[:0] = proof["process_only_paths"]
    origins = {}
    for name, item in proof["expected_modules"].items():
        module = importlib.import_module(name)
        actual = Path(module.__file__).resolve()
        assert actual == Path(item["origin"]).resolve() and digest(actual.read_bytes()) == item["sha256"]
        origins[name] = str(actual)
    from packaging.requirements import Requirement

    version = importlib.metadata.version("hatchling")
    assert version == proof["expected_version"]
    for item in proof["expected_active_requirements"]:
        requirement = Requirement(item["requirement"])
        actual = importlib.metadata.version(requirement.name)
        assert actual == item["actual_version"] and actual in requirement.specifier
    assert version in Requirement("hatchling>=1.27").specifier
    return {"files_verified": 183, "unchanged": True, "version": version, "origins": origins}


def safe_name(name):
    path = PurePosixPath(name)
    assert name and "\\" not in name and ":" not in name and "\0" not in name
    assert not path.is_absolute() and all(part not in (".", "..") for part in path.parts)
    assert path.parts
    return path


def unpack_sdist(archive, target):
    target.mkdir()
    with tarfile.open(archive, "r:gz") as stream:
        members = stream.getmembers()
        assert len({item.name for item in members}) == len(members)
        roots = {safe_name(item.name).parts[0] for item in members}
        assert len(roots) == 1
        for item in members:
            path = target.joinpath(*safe_name(item.name).parts)
            assert path.resolve().is_relative_to(target.resolve())
            assert item.isfile() or item.isdir(), "No archive links/special files"
            if item.isdir():
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open("xb") as output:
                    output.write(stream.extractfile(item).read())
    return target / roots.pop()


def build_phase(args, source_proof, backend_proof):
    environment = dict(os.environ)
    source = source_check(source_proof)
    context = cached_check(backend_proof, load=True)
    config = tomllib.loads((source / "pyproject.toml").read_text(encoding="utf-8"))
    assert config["build-system"] == {"requires": ["hatchling>=1.27"], "build-backend": "hatchling.build"}
    args.run.mkdir()
    dist = args.run / "dist"
    dist.mkdir()
    temporary = args.run / "backend-tmp"
    temporary.mkdir()
    previous_tmp = tempfile.tempdir
    # Child-only temporary-file location; no environment or product-global mutation.
    tempfile.tempdir = str(temporary)
    backend = importlib.import_module("hatchling.build")
    steps = []
    os.chdir(source)
    assert backend.get_requires_for_build_sdist() == []
    started = time.perf_counter()
    sdist_name = backend.build_sdist(str(dist))
    assert Path(sdist_name).name == sdist_name
    steps.append({"hook": "hatchling.build.build_sdist", "cwd": str(source), "exit": 0,
                  "elapsed_seconds": time.perf_counter() - started})
    save(args.evidence, "sdist-step.json", {"name": sdist_name, "steps": steps})
    unpacked = unpack_sdist(dist / sdist_name, args.run / "sdist-unpacked")
    os.chdir(unpacked)
    assert backend.get_requires_for_build_wheel() == []
    started = time.perf_counter()
    wheel_name = backend.build_wheel(str(dist))
    assert Path(wheel_name).name == wheel_name
    steps.append({"hook": "hatchling.build.build_wheel", "cwd": str(unpacked), "exit": 0,
                  "elapsed_seconds": time.perf_counter() - started})
    tempfile.tempdir = previous_tmp
    source_check(source_proof)
    cached_check(backend_proof)
    assert environment == dict(os.environ)
    assert not any(name == "deepviz" or name.startswith("deepviz.") for name in sys.modules)
    result = {"actual_source_sha": source_proof["actual_default_sha"], "backend": context,
              "kind": "Direct unchanged declared PEP517 hooks: sdist then wheel FROM sdist; NOT isolated frontend",
              "steps": steps, "sdist_unpacked": str(unpacked), "source_clean_hashes_before_after": True,
              "backend_183_hashes_before_after": True, "environment_unchanged": True,
              "installs_downloads_API_writes": 0, "artifacts": []}
    for name in [sdist_name, wheel_name]:
        path = dist / name
        result["artifacts"].append({"path": str(path), "name": name, "bytes": path.stat().st_size,
                                    "sha256": digest(path.read_bytes())})
    save(args.evidence, "build.json", result)
    print(json.dumps(result))
    return 0


def inspect_phase(args, source_proof, backend_proof):
    source = source_check(source_proof)
    cached_check(backend_proof, load=True)
    from packaging.requirements import Requirement

    build = json.loads((args.evidence / "build.json").read_text(encoding="utf-8"))
    wheel = next(Path(item["path"]) for item in build["artifacts"] if item["name"].endswith(".whl"))
    target = args.run / "wheel-consumer"
    target.mkdir()
    with zipfile.ZipFile(wheel) as archive:
        entries = archive.infolist()
        assert len({item.filename for item in entries}) == len(entries)
        for item in entries:
            path = target.joinpath(*safe_name(item.filename).parts)
            assert path.resolve().is_relative_to(target.resolve())
            assert stat.S_IFMT(item.external_attr >> 16) != stat.S_IFLNK
            if item.is_dir():
                path.mkdir(parents=True, exist_ok=True)
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as stream:
                stream.write(archive.read(item))
    files = {p.relative_to(target).as_posix(): p.read_bytes() for p in target.rglob("*") if p.is_file()}
    model = "deepviz/models.py"
    assert files[model] == (source / "python/deepviz/src" / model).read_bytes()
    module_comparisons = []
    for name, raw in files.items():
        if name.startswith("deepviz/"):
            original = source / "python/deepviz/src" / name
            assert original.is_file() and original.read_bytes() == raw
            module_comparisons.append(name)
    metadata_name = next(name for name in files if name.endswith(".dist-info/METADATA"))
    prefix = metadata_name.removesuffix("METADATA")
    metadata = BytesParser(policy=default).parsebytes(files[metadata_name])
    sdist_root = Path(build["sdist_unpacked"])
    sdist_metadata = BytesParser(policy=default).parsebytes((sdist_root / "PKG-INFO").read_bytes())
    config = tomllib.loads((source / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    for field, value in [("Name", config["name"]), ("Version", config["version"]),
                         ("Requires-Python", config["requires-python"])]:
        assert metadata[field] == sdist_metadata[field] == value
    actual_requirements = {str(Requirement(value)) for value in metadata.get_all("Requires-Dist", [])}
    expected_requirements = {str(Requirement(value)) for value in config["dependencies"]}
    for extra, values in config.get("optional-dependencies", {}).items():
        expected_requirements.update(str(Requirement(f'{value}; extra == "{extra}"')) for value in values)
    assert actual_requirements == expected_requirements
    assert set(metadata.get_all("Provides-Extra", [])) == set(config.get("optional-dependencies", {}))
    for field in ["Requires-Dist", "Provides-Extra", "License-Expression"]:
        assert sorted(metadata.get_all(field, [])) == sorted(sdist_metadata.get_all(field, []))
    points = configparser.ConfigParser(interpolation=None)
    points.read_string(files.get(prefix + "entry_points.txt", b"").decode("utf-8"))
    scripts = dict(points["console_scripts"]) if points.has_section("console_scripts") else {}
    assert scripts == config.get("scripts", {})
    targets = [{"name": name, "target": value,
                "module_present": value.split(":")[0].replace(".", "/") + ".py" in files}
               for name, value in scripts.items()]
    rows = list(csv.reader(io.StringIO(files[prefix + "RECORD"].decode("utf-8"))))
    assert len({row[0] for row in rows}) == len(rows) and {row[0] for row in rows} == set(files)
    for row in rows:
        name, checksum, size = row
        assert name in files
        if checksum:
            assert checksum == "sha256=" + base64.urlsafe_b64encode(hashlib.sha256(files[name]).digest()).decode().rstrip("=")
            assert int(size) == len(files[name])
        else:
            assert name == prefix + "RECORD" and size == ""
    source_matches, source_omissions = [], []
    for item in source_proof["source_files"]:
        path = sdist_root / item["path"]
        if path.exists():
            assert digest(path.read_bytes()) == item["raw_sha256"]
            source_matches.append(item["path"])
        else:
            source_omissions.append(item["path"])
    assert all(name in source_matches for name in ["pyproject.toml", "README.md", "LICENSE", "python/deepviz/src/deepviz/models.py"])
    source_check(source_proof)
    cached_check(backend_proof)
    result = {"actual_source_sha": source_proof["actual_default_sha"], "wheel": str(wheel),
              "consumer_root": str(target), "members": [{"path": name, "bytes": len(raw), "sha256": digest(raw)}
                                                       for name, raw in sorted(files.items())],
              "wheel_files_equal_source": module_comparisons, "sdist_source_matches": source_matches,
              "sdist_source_omissions": source_omissions, "metadata_source_sdist_wheel_agree": True,
              "name": metadata["Name"], "version": metadata["Version"], "requires_python": metadata["Requires-Python"],
              "requires_dist": sorted(actual_requirements), "entrypoints": targets, "RECORD_hashes_valid": True,
              "namespace_without_init": "deepviz/__init__.py" not in files,
              "py_typed_present": "deepviz/py.typed" in files,
              "wheel_json_schema_members": [name for name in files if name.endswith(".schema.json")],
              "manual_unpack_NOT_install": True, "model_raw_sha256": digest(files[model])}
    save(args.evidence, "archives.json", result)
    print(json.dumps(result))
    return 0


def consume_phase(args, source_proof):
    archive = json.loads((args.evidence / "archives.json").read_text(encoding="utf-8"))
    target = Path(archive["consumer_root"])
    environment = dict(os.environ)
    assert not (target / "deepviz/__init__.py").exists(), "This frozen main is model-only; do not silently broaden gate"
    sys.path.insert(0, str(target))
    namespace = importlib.import_module("deepviz")
    initial_paths = list(namespace.__path__)
    assert initial_paths == [str(target / "deepviz")]
    namespace.__path__ = initial_paths  # Freeze before adding read-only runtime dependencies.
    sys.path.append(str(args.site_packages))
    models = importlib.import_module("deepviz.models")
    origin = Path(models.__file__).resolve()
    assert origin == (target / "deepviz/models.py").resolve()
    assert digest(origin.read_bytes()) == archive["model_raw_sha256"]
    spec = models.ChartSpec(kind="line", title="R46 actual wheel model", x="day", y="value", max_points=10)
    wire = spec.model_dump_json()
    assert models.ChartSpec.model_validate_json(wire) == spec
    output = args.evidence / "actual-model-output.json"
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(wire + "\n")
    artifact = models.Artifact(paths=[str(output)], mime_type="application/json", engine="model-contract-only",
                               input_count=1, output_count=1, strategy="none")
    actual_artifact = json.loads(json.dumps(artifact.to_dict()))
    assert actual_artifact["paths"] == [str(output)] and actual_artifact["input_count"] == actual_artifact["output_count"] == 1
    entrypoints = []
    for item in archive["entrypoints"]:
        module = item["target"].split(":")[0]
        found = importlib.util.find_spec(module)
        entrypoints.append({**item, "actual_confined_module_resolves": found is not None})
        assert (found is not None) == item["module_present"]
    loaded = {name: str(Path(module.__file__).resolve()) for name, module in sys.modules.items()
              if name.startswith("deepviz.") and getattr(module, "__file__", None)}
    assert loaded == {"deepviz.models": str(origin)}
    runtime = importlib.import_module("pydantic")
    runtime_origin = Path(runtime.__file__).resolve()
    assert runtime_origin.is_relative_to(args.site_packages.resolve())
    assert environment == dict(os.environ)
    unresolved = [item for item in entrypoints if not item["actual_confined_module_resolves"]]
    code = 1 if unresolved else 0
    result = {"actual_source_sha": source_proof["actual_default_sha"], "argv": sys.argv,
              "python": sys.version, "isolated_no_site_no_bytecode": True, "cwd": os.getcwd(),
              "manual_unpacked_model_subset_passed": True, "actual_model_json": json.loads(wire),
              "actual_Artifact_metadata": actual_artifact, "namespace_initial_paths": initial_paths,
              "namespace_file": getattr(namespace, "__file__", None),
              "top_level_ChartSpec_available": hasattr(namespace, "ChartSpec"),
              "top_level_Artifact_available": hasattr(namespace, "Artifact"), "loaded_product_modules": loaded,
              "model_raw_sha256": digest(origin.read_bytes()), "readonly_pydantic_origin": str(runtime_origin),
              "readonly_pydantic_version": runtime.__version__, "entrypoints": entrypoints,
              "known_dangling_entrypoints": len(unresolved), "overall_declared_distribution_gate_exit": code,
              "issue_scope": "Existing #24/#5 model-only capability limits, not new bugs or numeric regressions",
              "clean_install_dependency_resolution_installed_typing": "NOT RUN / NOT CLAIMED",
              "environment_unchanged": True, "API_writes_installs_downloads_test_replays": 0}
    save(args.evidence, "consumer.json", result)
    print(json.dumps(result))
    return code


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["build", "inspect", "consume"])
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--site-packages", type=Path)
    args = parser.parse_args()
    assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
    source_proof = json.loads((args.evidence / "source-freeze.json").read_text(encoding="utf-8"))
    backend_proof = json.loads((args.evidence / "backend-files-current.json").read_text(encoding="utf-8"))

    def audit(event, _arguments):
        if event in {"socket.connect", "socket.getaddrinfo", "os.putenv", "os.unsetenv"}:
            raise RuntimeError("No network or environment mutations in this offline artifact gate")

    sys.addaudithook(audit)
    started = datetime.now(UTC).isoformat()
    save(args.evidence, args.phase + "-started.json", {"utc": started, "argv": sys.argv,
                                                     "actual_source_sha": source_proof["actual_default_sha"]})
    if args.phase == "build":
        return build_phase(args, source_proof, backend_proof)
    if args.phase == "inspect":
        return inspect_phase(args, source_proof, backend_proof)
    return consume_phase(args, source_proof)


if __name__ == "__main__":
    raise SystemExit(main())
