"""One fresh source-pinned build/pack/manual consumer; no dependency installation."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

SOURCE_COMMIT = "f9c437286c9dfe2245a7d914995d90346e29c233"
BASE_COMMIT = "ca25af486bf443949125df789f5b5fd1fda8bba8"
PROMPTS = ("README.md", "system.md", "request.md")
HERE = Path(__file__).resolve().parent


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def blob(repository: Path, commit: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=repository)


def validate_members(members: list[tarfile.TarInfo]) -> None:
    assert len(members) <= 256 and sum(member.size for member in members) <= 32_000_000
    seen = set()
    for member in members:
        parts = PurePosixPath(member.name).parts
        assert parts and parts[0] == "package" and ".." not in parts, member.name
        assert not member.name.startswith("/") and "\\" not in member.name and ":" not in member.name, member.name
        assert member.name not in seen, f"Duplicate tar member: {member.name}"
        assert member.isfile() or member.isdir(), f"Tar link/device rejected: {member.name}"
        assert not set(parts) & {"node_modules", "src", "test", "tests", ".git", ".env"}, member.name
        assert member.size <= 2_000_000, member.name
        seen.add(member.name)


def materialize(tarball: Path, installed: Path) -> list[dict]:
    assert not installed.exists()
    installed.mkdir(parents=True)
    receipt = []
    with tarfile.open(tarball, "r:gz") as archive:
        members = archive.getmembers()
        validate_members(members)
        for member in members:
            target = installed.joinpath(*PurePosixPath(member.name).parts[1:])
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            stream = archive.extractfile(member)
            assert stream is not None
            with stream:
                data = stream.read()
            assert len(data) == member.size
            target.write_bytes(data)
            receipt.append({"path": member.name, "bytes": len(data), "sha256": sha256(data)})
    return receipt


def run(repository: Path, artifact_root: Path, node: Path, npm_cli: Path, typescript: Path,
        resume: Path | None = None) -> dict:
    output = resume.resolve() if resume is not None else Path(tempfile.mkdtemp(prefix="consumer-run-", dir=artifact_root))
    assert output.is_relative_to(artifact_root)
    commands: list[dict[str, Any]] = json.loads((output / "commands.json").read_text(encoding="utf-8")) if resume else []
    env = dict(os.environ)
    env.pop("NODE_PATH", None)
    env["PATH"] = str(typescript.parent / ".bin") + os.pathsep + env.get("PATH", "")
    env["npm_config_cache"] = str(output / "npm-cache")
    env["npm_config_userconfig"] = str(output / "empty.npmrc")
    (output / "empty.npmrc").write_text("", encoding="utf-8")

    def command(args: list[str], cwd: Path, label: str, *, expected_exit: int = 0) -> str:
        result = subprocess.run(args, cwd=cwd, env=env, capture_output=True, timeout=180)
        (output / f"{label}.stdout").write_bytes(result.stdout)
        (output / f"{label}.stderr").write_bytes(result.stderr)
        commands.append({"args": args, "cwd": str(cwd), "exit": result.returncode, "expected_exit": expected_exit})
        (output / "commands.json").write_text(json.dumps(commands, indent=2), encoding="utf-8")
        assert result.returncode == expected_exit, f"{label}: exit{result.returncode}; logs under {output}"
        return result.stdout.decode("utf-8")

    # Independent expected bytes come ONLY from immutable canonical Git blobs.
    expected: dict[str, Any] = {"commit": SOURCE_COMMIT, "prompts": {}}
    for name in PROMPTS:
        data = blob(repository, SOURCE_COMMIT, f"prompts/v1/{name}")
        expected["prompts"][name] = {"bytes": len(data), "sha256": sha256(data),
                                     "base64": base64.b64encode(data).decode("ascii"),
                                     "cr_bytes": data.count(b"\r"), "lf_bytes": data.count(b"\n")}
    (output / "canonical-git-blobs.json").write_text(json.dumps(expected, indent=2), encoding="utf-8")

    source = output / "source"
    if resume is None:
        command(["git", "worktree", "add", "--detach", str(source), SOURCE_COMMIT], repository, "checkout")
    assert command(["git", "rev-parse", "HEAD"], source, "source-sha").strip() == SOURCE_COMMIT
    assert not command(["git", "status", "--porcelain"], source, "source-clean-before").strip()
    tracked = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", SOURCE_COMMIT,
                                     "--", "packages/deepviz", "prompts/v1"], cwd=repository, text=True).splitlines()
    source_receipt = []
    for relative in tracked:
        committed = blob(repository, SOURCE_COMMIT, relative)
        working = (source / relative).read_bytes()
        assert working == committed, f"Working checkout newline/source mismatch: {relative}"
        source_receipt.append({"path": relative, "git_sha256": sha256(committed),
                               "working_sha256": sha256(working), "bytes": len(working)})
    for relative in (path for path in tracked if path.startswith("packages/deepviz/src/")):
        assert blob(repository, BASE_COMMIT, relative) == blob(repository, SOURCE_COMMIT, relative), relative
    (output / "source-hashes.json").write_text(json.dumps(source_receipt, indent=2), encoding="utf-8")

    packed = output / "packed"
    if resume is None:
        command([str(node), str(npm_cli), "run", "build", "--workspace", "@deepviz/agent-toolkit"], source, "build")
        packed.mkdir()
        packs = json.loads(command([str(node), str(npm_cli), "pack", "--json", "--ignore-scripts", "--offline",
                                   "--workspace", "@deepviz/agent-toolkit", "--pack-destination", str(packed)],
                                  source, "pack"))
    else:
        packs = json.loads((output / "pack.stdout").read_text(encoding="utf-8"))
        assert all(entry["exit"] == 0 for entry in commands if "pack" in entry["args"] or "build" in entry["args"])
    assert len(packs) == 1
    tarball = packed / packs[0]["filename"]
    consumer = output / "consumer"
    consumer.mkdir(exist_ok=resume is not None)
    (consumer / "package.json").write_text('{"name":"r18-independent-consumer","private":true,"type":"module"}',
                                          encoding="utf-8")
    installed = consumer / "node_modules/@deepviz/agent-toolkit"
    if resume is None:
        members = materialize(tarball, installed)
    else:
        members = []
        with tarfile.open(tarball, "r:gz") as archive:
            validate_members(archive.getmembers())
            for member in archive.getmembers():
                if member.isfile():
                    source_stream = archive.extractfile(member)
                    assert source_stream is not None
                    with source_stream:
                        content = source_stream.read()
                    target = installed.joinpath(*PurePosixPath(member.name).parts[1:])
                    assert target.read_bytes() == content, f"Existing materialized package changed: {member.name}"
                    members.append({"path": member.name, "bytes": len(content), "sha256": sha256(content)})
    names = {item["path"].removeprefix("package/") for item in members}
    assert names == {item["path"] for item in packs[0]["files"]}, "Actual tarball and npm file receipt disagree"
    metadata = json.loads((installed / "package.json").read_text(encoding="utf-8"))
    assert not metadata.get("dependencies")
    type_names = sorted(name for file in ("models.d.ts", "render.d.ts")
                        for name in re.findall(r"^export (?:declare )?(?:type|interface) (\w+)",
                                               (installed / "dist" / file).read_text(encoding="utf-8"), re.MULTILINE))
    assert type_names == sorted(["ChartKind", "Engine", "BrowserEngine", "DataFormat", "Aggregation",
                                 "ChartSpec", "ChartSpecInput", "Scalar", "DataRecord", "NormalizedData", "Artifact",
                                 "AssetName", "RenderOptions", "RendererResult", "HtmlArtifact", "RenderTool"])
    for name in PROMPTS:
        assert metadata["exports"][f"./prompts/v1/{name}"] == f"./dist/prompts/v1/{name}"
    for name in ("consumer.test.mjs", "types.mts"):
        if resume and (output / "corrected-positive-node-tests.stdout").exists():
            assert (consumer / name).read_bytes() == (HERE / name).read_bytes(), "Cannot reuse changed consumer tests"
        shutil.copyfile(HERE / name, consumer / name)
    shutil.copyfile(output / "canonical-git-blobs.json", consumer / "canonical-git-blobs.json")
    if resume and (output / "corrected-positive-node-tests.stdout").exists():
        positive = (output / "corrected-positive-node-tests.stdout").read_text(encoding="utf-8")
        assert any(entry["exit"] == 0 and "consumer.test.mjs" in entry["args"] for entry in commands)
    else:
        positive = command([str(node), "--test", "--test-reporter=tap", "consumer.test.mjs"], consumer,
                           "corrected-positive-node-tests" if resume else "positive-node-tests")
    assert "# tests 9" in positive and "# pass 9" in positive and "# fail 0" in positive, positive

    config = {"compilerOptions": {"strict": True, "noEmit": True, "module": "NodeNext", "target": "ES2022",
                                    "skipLibCheck": False, "types": []}, "files": ["types.mts"]}
    (consumer / "tsconfig.json").write_text(json.dumps(config), encoding="utf-8")
    if resume and (output / "external-types.stdout").exists():
        type_log = (output / "external-types.stdout").read_text(encoding="utf-8")
        assert any(entry["exit"] == 0 and "--listFiles" in entry["args"] for entry in commands)
    else:
        type_log = command([str(node), str(typescript / "bin/tsc"), "-p", "tsconfig.json", "--listFiles"],
                           consumer, "external-types")
    declaration_paths = [Path(line.strip()).resolve() for line in type_log.splitlines() if "/dist/" in line.replace("\\", "/")]
    assert declaration_paths and all(path.is_relative_to(installed.resolve()) for path in declaration_paths)
    negative = consumer / "invalid-types.mts"
    negative.write_text("import type {ChartSpecInput,BrowserEngine} from '@deepviz/agent-toolkit';\n"
                        "const invalid:ChartSpecInput={kind:'execute-code'};\n"
                        "const engine:BrowserEngine='matplotlib';\nconsole.log(invalid,engine);\n", encoding="utf-8")
    config["files"] = [negative.name]
    (consumer / "negative-tsconfig.json").write_text(json.dumps(config), encoding="utf-8")
    if resume and (output / "strict-negative-types.stdout").exists():
        errors = (output / "strict-negative-types.stdout").read_text(encoding="utf-8")
        assert any(entry["exit"] == 1 and "negative-tsconfig.json" in entry["args"] for entry in commands)
    else:
        errors = command([str(node), str(typescript / "bin/tsc"), "-p", "negative-tsconfig.json"],
                         consumer, "strict-negative-types", expected_exit=1)
    assert errors.count("error TS2322") == 2

    # Deliberate corruption in separate own consumer copies must be detected.
    negatives = []
    for label in ("changed-system", "missing-request", "export-outside", "extra-public-export"):
        control = output / label
        shutil.copytree(consumer, control)
        local = control / "node_modules/@deepviz/agent-toolkit"
        if label == "changed-system":
            with (local / "dist/prompts/v1/system.md").open("ab") as stream:
                stream.write(b"\nInjected fixture only\n")
        elif label == "missing-request":
            (local / "dist/prompts/v1/request.md").unlink()
        elif label == "export-outside":
            meta = json.loads((local / "package.json").read_text(encoding="utf-8"))
            meta["exports"]["./prompts/v1/system.md"] = "../outside-system.md"
            (local / "package.json").write_text(json.dumps(meta), encoding="utf-8")
        else:
            with (local / "dist/index.js").open("a", encoding="utf-8") as text_stream:
                text_stream.write("\nexport const unexpectedReader = true;\n")
        text = command([str(node), "--test", "--test-reporter=tap", "consumer.test.mjs"], control, label, expected_exit=1)
        assert re.search(r"# fail [1-9]", text), label
        negatives.append(label)

    assert not command(["git", "status", "--porcelain"], source, "source-clean-after").strip()
    receipt = {"source_commit": SOURCE_COMMIT, "api_comparison_base": BASE_COMMIT,
               "source_worktree": str(source), "source_clean_after": True,
               "node": command([str(node), "--version"], consumer, "node-version").strip(),
               "typescript": json.loads((typescript / "package.json").read_text(encoding="utf-8"))["version"],
               "tarball": {"path": str(tarball), "bytes": tarball.stat().st_size,
                           "sha256": sha256(tarball.read_bytes()), "members": members},
               "prompts": {name: {key: value for key, value in oracle.items() if key != "base64"}
                           for name, oracle in expected["prompts"].items()},
               "manual_materialization_not_npm_install": True, "public_runtime_exports": 13,
               "public_type_names_compiled": 16, "node_consumer_tests_passed": 9,
               "actual_public_type_names": type_names,
               "negative_consumer_controls": negatives, "negative_type_errors": 2,
               "declarations_resolved": [str(path) for path in declaration_paths], "commands": commands,
               "limits": ["Not npm install/ci or prepack-hook validation; build explicit, pack --ignore-scripts",
                          "No browser/CDN/provider/scale/full-test/final-head approval"],
               "output": str(output)}
    (output / "summary.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False), encoding="utf-8")
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--node", type=Path, required=True)
    parser.add_argument("--npm-cli", type=Path, required=True)
    parser.add_argument("--typescript", type=Path, required=True)
    parser.add_argument("--resume", type=Path, help="Continue a recorded own run without repeating build/pack")
    args = parser.parse_args()
    args.artifact_root.mkdir(parents=True, exist_ok=True)
    summary = run(args.repository.resolve(), args.artifact_root.resolve(), args.node.resolve(),
                  args.npm_cli.resolve(), args.typescript.resolve(), args.resume)
    print(json.dumps({"summary": summary["output"] + "/summary.json", "tarball": summary["tarball"]["sha256"],
                      "consumer_tests": summary["node_consumer_tests_passed"],
                      "negative_controls": summary["negative_consumer_controls"]}, indent=2))
