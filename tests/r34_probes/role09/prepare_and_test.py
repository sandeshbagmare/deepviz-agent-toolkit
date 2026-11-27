"""Fixed c3ee finite-only preparation and two immutable, scoped test commands."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

PIN = "c3ee1edbfc65406cef7fd809f5a6887471d576a5"
ORACLE_PIN = "38ce71e50ce59e58dc647417de26e547d5e42d5a"
ORACLE_PATH = "tests/r17_probes/role13/finite-range-regression.mjs"
OLD_PIN = "5e595a8f893955ce34a0e26553bb7bf257ea93ae"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--compiler", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    compiler = args.compiler.resolve(strict=True)
    output = args.output.resolve(strict=True)
    own = Path(__file__).resolve().parent

    def git(*parts: str) -> bytes:
        return subprocess.check_output(["git", "-C", str(source), *parts])

    def snapshot() -> dict[str, object]:
        assert git("rev-parse", "HEAD").decode().strip() == PIN
        assert not git("status", "--porcelain", "--untracked-files=no").strip()
        names = git("ls-tree", "-r", "--name-only", PIN, "--",
                    "packages/deepviz/src", "packages/deepviz/tsconfig.json",
                    "packages/deepviz/package.json",
                    "packages/deepviz/test/test_r23_svg_finite_density.test.mjs").decode().splitlines()
        files = {}
        for name in names:
            raw = (source / name).read_bytes()
            blob = git("show", f"{PIN}:{name}")
            assert raw.replace(b"\r\n", b"\n") == blob.replace(b"\r\n", b"\n"), name
            files[name] = {"raw_sha256": digest(raw), "git_blob_sha256": digest(blob),
                           "raw_equals_git": raw == blob, "lf_equivalent": True}
        return {"source_sha": PIN, "tracked_clean": True, "files": files}

    before = snapshot()
    assert not (source / "packages/deepviz/dist").exists(), "Require a fresh checkout: dist must be absent"
    original = git("show", f"{ORACLE_PIN}:{ORACLE_PATH}")
    assert original.count(OLD_PIN.encode()) == 1
    adapted = original.replace(OLD_PIN.encode(), PIN.encode(), 1)
    adapter = own / "original-finite-setup-adapted.test.mjs"
    adapter.write_bytes(adapted)
    (output / "original-oracle.mjs.txt").write_bytes(original)
    record: dict[str, object] = {
        **before, "source_root": str(source), "runner": str(Path(__file__).resolve()),
        "runner_sha256": digest(Path(__file__).read_bytes()),
        "compiler": str(compiler), "compiler_sha256": digest(compiler.read_bytes()),
        "original_oracle": {"commit": ORACLE_PIN, "path": ORACLE_PATH,
                            "sha256": digest(original), "adapter_sha256": digest(adapted),
                            "only_change": f"one setup HEAD constant {OLD_PIN} -> {PIN}",
                            "semantic_assertions_changed": False},
    }
    cmd = ["node", str(compiler), "-p", "packages/deepviz/tsconfig.json"]
    built = subprocess.run(cmd, cwd=source, capture_output=True, check=False)
    (output / "build.stdout.log").write_bytes(built.stdout)
    (output / "build.stderr.log").write_bytes(built.stderr)
    record["build"] = {"argv": cmd, "cwd": str(source), "exit": built.returncode}
    assert built.returncode == 0, "Compiler failed; raw logs preserved"
    assert snapshot() == before, "Tracked source changed during build"
    record["dist"] = {p.relative_to(source).as_posix(): digest(p.read_bytes())
                      for p in sorted((source / "packages/deepviz/dist").rglob("*")) if p.is_file()}
    (output / "source-build.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    env = {**os.environ, "R34_SOURCE": str(source), "R17_13_SOURCE": str(source),
           "R34_EVIDENCE": str(output)}
    commands = []
    for stem, target in [("author-units", source / "packages/deepviz/test/test_r23_svg_finite_density.test.mjs"),
                         ("original-two-bar", adapter)]:
        argv = ["node", "--import", (own / "source-proof.mjs").as_uri(), "--test", "--test-reporter=tap", str(target)]
        ran = subprocess.run(argv, cwd=source, env=env, capture_output=True, check=False, timeout=60)
        (output / f"{stem}.tap").write_bytes(ran.stdout)
        (output / f"{stem}.stderr.log").write_bytes(ran.stderr)
        commands.append({"name": stem, "argv": argv, "cwd": str(source), "exit": ran.returncode})
        print(ran.stdout.decode("utf-8", errors="replace"), end="")
        print(ran.stderr.decode("utf-8", errors="replace"), end="", file=sys.stderr)
        (output / "unit-commands.json").write_text(json.dumps(commands, indent=2) + "\n", encoding="utf-8")
        assert snapshot() == before, "Tracked source changed during tests"
        if ran.returncode:
            return ran.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
