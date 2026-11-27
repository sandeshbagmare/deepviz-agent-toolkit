"""External fixed-command freeze/count envelope, NOT independent scale approval.

Default is PLAN_ONLY (zero performance commands; Git preflight still runs). No arbitrary command or code options.
Actual same-process imports, measurement truth, values/loss/RSS gates and review
remain the fixed runner's + independent validators' responsibility (see README).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any

COUNTS = [10, 1000, 100000, 1000000, 10000000]
CASES = ["numeric_sample", "category_sum", "category_mean"]
RUNNER = "scripts/performance_suite.py"
ORIGIN_LIMIT = "Same-process imported module paths/bytecode are not attested by this external envelope; the frozen child loader must reject wrong origins."


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                          text=True, encoding="utf-8", check=True, timeout=30).stdout


def file_hashes(root: Path, name: str) -> tuple[str, str]:
    path = root / name
    require(path.resolve().is_relative_to(root) and not path.is_symlink(), "Unsafe input path")
    size = path.stat().st_size
    sha = hashlib.sha256()
    blob = hashlib.sha1(b"blob " + str(size).encode() + b"\0")
    with path.open("rb") as stream:
        while chunk := stream.read(65536):
            sha.update(chunk)
            blob.update(chunk)
    return sha.hexdigest(), blob.hexdigest()


def freeze(root: Path, expected_sha: str, allowed_inputs: dict[str, str]) -> dict[str, Any]:
    root = root.resolve(strict=True)
    require(bool(re.fullmatch(r"[0-9a-f]{40}", expected_sha)), "Expected exact full commit")
    require(Path(git(root, "rev-parse", "--show-toplevel").strip()).resolve() == root, "Not a Git root")
    head = git(root, "rev-parse", "HEAD").strip()
    require(head == expected_sha, "HEAD changed or wrong source")
    require(not git(root, "status", "--porcelain", "--untracked-files=no"), "Tracked source dirty")
    # Current directory and script path precede PYTHONPATH. Check even ignored files.
    for directory in (root, root / "scripts", root / "python/deepviz/src"):
        names = ["sitecustomize.py", "usercustomize.py"]
        if directory != root / "python/deepviz/src":
            names += ["deepviz", "deepviz.py"]
        require(not any((directory / name).exists() for name in names), "Unexpected import shadow")
    untracked = set(git(root, "ls-files", "--others", "--exclude-standard", "-z").rstrip("\0").split("\0")) - {""}
    require(untracked <= set(allowed_inputs), "Unexpected or missing untracked input")
    allowed = {}
    for name, digest in allowed_inputs.items():
        path = PurePosixPath(name)
        require(not path.is_absolute() and ".." not in path.parts and "\\" not in name and ":" not in name,
                "Unsafe allowlisted path")
        require(path.suffix in {".json", ".jsonl", ".csv", ".tsv", ".txt", ".parquet", ".arrow"},
                "Allowlisted inputs must be data, never code/config")
        require(bool(re.fullmatch(r"[0-9a-f]{64}", digest)), "Expected data SHA256")
        allowed[name] = file_hashes(root, name)[0]
        require(allowed[name] == digest, "Allowed input changed")
    hashes = {}
    for entry in git(root, "ls-tree", "-r", "-z", "HEAD").rstrip("\0").split("\0"):
        metadata, name = entry.split("\t", 1)
        relevant = name.startswith(("python/", "scripts/", "tests/")) or name.endswith((".toml", ".ini", ".cfg", ".lock")) or name in {".gitattributes", ".gitignore", ".python-version"} or name.startswith("requirements") or name in allowed_inputs
        if relevant:
            mode, kind, oid = metadata.split()
            require(kind == "blob" and mode in {"100644", "100755"}, "Non-regular frozen input")
            digest, raw_blob = file_hashes(root, name)
            require(raw_blob == oid, "Frozen input differs from exact Git bytes: " + name)
            hashes[name] = {"git_blob": oid, "sha256": digest}
    require(RUNNER in hashes, "Tracked performance runner required")
    source = root / "python/deepviz/src/deepviz"
    # Ignored native/code additions in the import directory must not escape Git status.
    actual = {path.relative_to(root).as_posix() for path in source.rglob("*")
              if path.is_file() and "__pycache__" not in path.parts}
    require(actual <= set(hashes), "Unfrozen import directory input")
    python_hashes = {name: value["sha256"] for name, value in hashes.items()
                     if name.startswith("python/deepviz/src/deepviz/") and name.endswith(".py")}
    require(all("python/deepviz/src/deepviz/" + name in python_hashes
                for name in ("models.py", "normalize.py")), "Required Python sources missing")
    return {"root": str(root), "head": head, "git_tree": git(root, "rev-parse", "HEAD^{tree}").strip(),
            "files": hashes, "allowed_inputs": allowed, "untracked_paths": sorted(untracked), "python_sha256": python_hashes,
            "reported_dirty_paths": git(root, "status", "--porcelain").splitlines()}


def same_source(before: dict[str, Any], after: dict[str, Any]) -> None:
    require(before == after, "Frozen source, runner, tests, config or input changed")


def validate_matrix(data: dict[str, Any], before: dict[str, Any]) -> int:
    require(data.get("status") == "passed" and data.get("errors") == [], "Matrix failed or skipped")
    source = {"root": before["root"], "commit": before["head"],
              "dirty_paths": before["reported_dirty_paths"], "sha256": before["python_sha256"]}
    require(data.get("source") == source and data.get("harness") == source, "Report source/runner provenance mismatch")
    require(data.get("requested_counts") == COUNTS and data.get("requested_cases") == CASES
            and data.get("numeric_repeats") == 2 and data.get("render_counts") == [], "Wrong requested matrix")
    rows = data.get("results")
    if not isinstance(rows, list) or len(rows) != 20:
        raise ValueError("Missing or incomplete worker report")
    expected = Counter((case, count, repeat) for case in CASES for count in COUNTS
                       for repeat in ([1, 2] if case == "numeric_sample" else [1]))
    require(all(isinstance(row, dict) and type(row.get("count")) is int and type(row.get("repeat")) is int
                for row in rows), "Wrong worker count/repeat types")
    require(Counter((row.get("case"), row.get("count"), row.get("repeat")) for row in rows) == expected,
            "Wrong count/case/repeat matrix")
    for row in rows:
        count = row["count"]
        require(row.get("status") == "passed" and row.get("source") == source, "Worker skipped/failed or wrong source")
        require(type(row.get("input_count")) is int and type(row.get("consumed_count")) is int
                and row["input_count"] == row["consumed_count"] == count and row.get("source_exhausted") is True,
                "Wrong input/consumed count or unexhausted worker")
        output = min(count, 2000) if row["case"] == "numeric_sample" else 7
        require(type(row.get("output_count")) is int and row["output_count"] == output
                and row.get("max_points") == 2000, "Wrong output bound/count")
    return len(rows)


def verify(root: Path, expected_sha: str, evidence: Path, *, run: bool = False,
           allowed_inputs: dict[str, str] | None = None, timeout: float = 15000) -> dict[str, Any]:
    root, evidence = root.resolve(strict=True), evidence.resolve()
    require(not evidence.is_relative_to(root), "Evidence must be external to candidate")
    require(not evidence.exists(), "Preserve existing evidence; choose a new directory")
    before = freeze(root, expected_sha, allowed_inputs or {})
    own_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    command = [sys.executable, "-B", "-s", str(root / RUNNER), "--source-root", str(root), "--counts",
               *map(str, COUNTS), "--cases", *CASES, "--max-points", "2000", "--repeats", "2",
               "--render-counts", "--max-peak-growth-mib", "64", "--timeout", "600",
               "--output", str(evidence / "matrix.json")]
    # shortcut: same-process imports need a child hash hook before origin attestation.
    receipt: dict[str, Any] = {"status": "PLAN_ONLY_NOT_EXECUTED", "commands_executed": 0,
                              "commands_executed_scope": "fixed performance command only; Git preflight still runs",
                              "command": command, "before": before, "envelope_sha256": own_hash,
                              "measurement_verified": False, "module_origin_limit": ORIGIN_LIMIT,
                              "scope": "External provenance and worker counts only; values/loss/OS memory/measurement truth need independent gates"}
    if not run:
        return receipt
    evidence.mkdir(parents=True, exist_ok=False)
    env = os.environ.copy()
    env.pop("PYTHONHOME", None)
    env.pop("PYTHONOPTIMIZE", None)
    env.update(PYTHONPATH=str(root / "python/deepviz/src"), PYTHONNOUSERSITE="1",
               PYTHONDONTWRITEBYTECODE="1", PYTHONPYCACHEPREFIX=str(evidence / "pycache"))
    try:
        with (evidence / "stdout.log").open("wb") as stdout, (evidence / "stderr.log").open("wb") as stderr:
            receipt["commands_executed"] = 1
            done = subprocess.run(command, cwd=root, env=env, stdout=stdout, stderr=stderr,
                                  timeout=timeout, check=False)
        receipt["exit"] = done.returncode
        require(done.returncode == 0, "Child command failed")
    except Exception as error:
        receipt["error"] = type(error).__name__ + ": " + str(error)
    try:
        after = freeze(root, expected_sha, allowed_inputs or {})
        same_source(before, after)
        require(hashlib.sha256(Path(__file__).read_bytes()).hexdigest() == own_hash, "Envelope changed")
        receipt["after"] = after
        require("error" not in receipt, "Child execution did not succeed")
        path = evidence / "matrix.json"
        require(path.is_file(), "Missing worker report")
        with path.open("rb") as stream:
            raw = stream.read(4 * 1024**2 + 1)
        require(len(raw) <= 4 * 1024**2, "Worker report exceeds 4 MiB")
        receipt["workers_checked"] = validate_matrix(json.loads(raw), before)
        receipt["report_sha256"] = hashlib.sha256(raw).hexdigest()
        receipt["status"] = "PROVENANCE_AND_COUNTS_PASS_NOT_SCALE_APPROVAL"
    except Exception as error:
        receipt["error"] = receipt.get("error", "") + " | " + type(error).__name__ + ": " + str(error)
        receipt["status"] = "REJECTED_NOT_SCALE_APPROVAL"
    with (evidence / "result.json").open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2)
        stream.write("\n")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("expected_sha")
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--allow-input", action="append", default=[], metavar="RELATIVE_PATH=SHA256")
    args = parser.parse_args()
    try:
        allowed = dict(item.rsplit("=", 1) for item in args.allow_input)
        result = verify(args.candidate, args.expected_sha, args.evidence, run=args.run, allowed_inputs=allowed)
        print(json.dumps(result, indent=2))
        return 1 if result["status"] == "REJECTED_NOT_SCALE_APPROVAL" else 0
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print(json.dumps({"status": "PREFLIGHT_REJECTED_NOT_EXECUTED", "error": str(error),
                          "measurement_verified": False}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
