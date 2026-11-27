"""Build an exact Git checkpoint and test two genuinely independent installed consumers.

Only declared public dependencies are installed, exclusively into new owned venvs.
Run with --source, --expected-sha and a NEW short --output path outside the checkout.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tarfile
import time
import tomllib
from pathlib import Path
from typing import Any


def isolated_env(environment: dict[str, str], temp: Path) -> dict[str, str]:
    result = {
        key: value for key, value in environment.items()
        if not key.upper().startswith(("PYTHON", "PIP_", "UV_"))
        and key.upper() not in {"VIRTUAL_ENV", "MYPYPATH", "CONDA_PREFIX"}
    }
    result.update({
        "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1", "PIP_CONFIG_FILE": os.devnull,
        "PIP_INDEX_URL": "https://pypi.org/simple", "PIP_NO_INPUT": "1",
        "PIP_DISABLE_PIP_VERSION_CHECK": "1", "TEMP": str(temp), "TMP": str(temp),
        "MPLCONFIGDIR": str(temp / "mpl-config"),
    })
    return result


def build_requirements(config: dict) -> list[str]:
    dev = config["project"]["optional-dependencies"]["dev"]
    return config["build-system"]["requires"] + [
        item for item in dev if (match := re.match(r"[\w-]+", item)) and match.group() in {"build", "twine"}
    ]


def fresh_output(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=False)


def require_origin(origin: Path, prefix: Path) -> None:
    assert origin.resolve().is_relative_to(prefix.resolve()), f"Non-isolated origin: {origin}"


def fingerprint(path: Path) -> dict:
    return {"path": str(path), "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    assert not output.is_relative_to(source), "Keep environments/artifacts outside checkout"
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip()
    assert head == args.expected_sha, (head, args.expected_sha)
    fresh_output(output)
    temp = output / "temp"
    temp.mkdir()
    environment = isolated_env(dict(os.environ), temp)
    result: dict[str, Any] = {
        "source_sha": head,
        "source_tree": subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=source, text=True).strip(),
        "branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=source, text=True).strip(),
        "source_status_before": subprocess.check_output(["git", "status", "--porcelain"], cwd=source, text=True),
        "output": str(output), "commands": [], "complete": False,
        "scope": "Current checkpoint, clean build venv, wheel base consumer, sdist mcp consumer; not final freeze",
    }

    def save():
        (output / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    def run(label: str, command: list[str], timeout: int = 900, expected: int = 0):
        start = time.perf_counter()
        process = subprocess.run(command, cwd=output, env=environment, capture_output=True, text=True,
                                 timeout=timeout, check=False)
        (output / f"{label}.stdout.log").write_text(process.stdout, encoding="utf-8")
        (output / f"{label}.stderr.log").write_text(process.stderr, encoding="utf-8")
        item = {"label": label, "argv": command, "cwd": str(output), "exit": process.returncode,
                "expected_exit": expected,
                "seconds": time.perf_counter() - start}
        result["commands"].append(item)
        save()
        print(json.dumps(item), flush=True)
        if process.returncode != expected:
            raise RuntimeError(f"{label} failed; preserved stdout/stderr and result.json")
        return process

    def create_venv(name: str) -> Path:
        path = output / name
        assert not path.exists()
        run(name + "-create", [sys.executable, "-B", "-I", "-m", "venv", str(path)])
        config = (path / "pyvenv.cfg").read_text(encoding="utf-8").lower()
        assert "include-system-site-packages = false" in config
        return path / ("Scripts/python.exe" if os.name == "nt" else "bin/python")

    try:
        archive = output / "checkpoint.tar"
        with archive.open("xb") as stream:
            subprocess.run(["git", "archive", "--format=tar", head], cwd=source, stdout=stream, check=True)
        result["git_archive"] = fingerprint(archive)
        snapshot = output / "src"
        snapshot.mkdir()
        with tarfile.open(archive) as stream:
            stream.extractall(snapshot, filter="data")
        config = tomllib.loads((snapshot / "pyproject.toml").read_text(encoding="utf-8"))
        result["declared_build_requirements"] = build_requirements(config)
        result["declared_runtime_requirements"] = config["project"]["dependencies"]
        result["declared_mcp_requirements"] = config["project"]["optional-dependencies"]["mcp"]
        build_python = create_venv("build-env")
        run("build-dependencies", [str(build_python), "-B", "-I", "-m", "pip", "install", "--no-cache-dir",
                                   *result["declared_build_requirements"]])
        dist = output / "dist"
        run("build", [str(build_python), "-B", "-I", "-m", "build", "--no-isolation", "--outdir", str(dist),
                      "--sdist-extract-dir", str(output / "sdist-source"), str(snapshot)])
        wheel, sdist = next(dist.glob("*.whl")), next(dist.glob("*.tar.gz"))
        result["artifacts"] = [fingerprint(wheel), fingerprint(sdist)]
        run("twine", [str(build_python), "-B", "-I", "-m", "twine", "check", "--strict", str(wheel), str(sdist)])
        probe_dir = Path(__file__).resolve().parent
        run("archive", [sys.executable, "-B", "-I", str(probe_dir / "inspect_archives.py"),
                        str(snapshot), str(wheel), str(sdist), str(output / "archive-result.json")])
        run("build-inventory", [str(build_python), "-B", "-I", str(probe_dir / "consumer_smoke.py"),
                                "--inventory-only", "--output", str(output / "build-inventory")])
        for kind, artifact, extra in (("wheel", wheel, ""), ("sdist", sdist, "[mcp]")):
            python = create_venv(kind + "-env")
            if kind == "sdist":
                run("sdist-backend", [str(python), "-B", "-I", "-m", "pip", "install", "--no-cache-dir",
                                      *config["build-system"]["requires"]])
            run(kind + "-install", [str(python), "-B", "-I", "-m", "pip", "install", "--no-cache-dir",
                                    "--no-build-isolation", str(artifact) + extra])
            run(kind + "-pip-check", [str(python), "-B", "-I", "-m", "pip", "check"])
            command = [str(python), "-B", "-I", str(probe_dir / "consumer_smoke.py"), "--source", str(snapshot),
                       "--artifact", str(artifact), "--output", str(output / (kind + "-consumer"))]
            if kind == "sdist":
                command.append("--mcp")
            run(kind + "-consumer", command)
        mypy_requirement = next(
            item for item in config["project"]["optional-dependencies"]["dev"] if item.startswith("mypy>=")
        )
        run("typing-tool", [str(build_python), "-B", "-I", "-m", "pip", "install", "--no-cache-dir",
                            mypy_requirement])
        for kind in ("wheel", "sdist"):
            python = output / (kind + "-env") / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            base = [str(build_python), "-B", "-I", "-m", "mypy", "--strict", "--follow-imports=silent",
                    "--no-incremental", "--python-executable", str(python),
                    "--cache-dir", str(temp / ("mypy-" + kind))]
            run(kind + "-typing-positive", base + [str(probe_dir / "typing_accept.py")])
            negative = run(kind + "-typing-negative", base + [str(probe_dir / "typing_reject.py")], expected=1)
            assert 'expression has type "str", variable has type "int"' in negative.stdout
            assert "[assignment]" in negative.stdout and "import-untyped" not in negative.stdout
        run("build-final-inventory", [str(build_python), "-B", "-I", str(probe_dir / "consumer_smoke.py"),
                                      "--inventory-only", "--output", str(output / "build-final-inventory")])
        result["complete"] = True
    except (RuntimeError, OSError, AssertionError, subprocess.SubprocessError) as error:
        result["error"] = {"type": type(error).__name__, "message": str(error)}
    finally:
        result["source_status_after"] = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=source, text=True)
        save()
    print(json.dumps({"complete": result["complete"], "result": str(output / "result.json"),
                      "error": result.get("error")}), flush=True)
    return 0 if result["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
