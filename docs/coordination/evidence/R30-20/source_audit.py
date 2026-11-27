"""Read immutable Git/installed SDK bytes; never import or execute DeepViz/tests."""
from __future__ import annotations

import ast
import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from importlib.metadata import distribution, version
from pathlib import Path

SEALED = "e47f8701ad18bd3e3bc32a84bf4b2b3ea707ed23"
BASE = "5340bc69b7203ad7a9166543062482d819f9b705"
P1 = "d65dfc0fd807d0335b858476de8cdf7c6b958711"
P2 = "cd75c459ddba9f3d6bc0a5185b570af369fb4980"
MAIN_SNAPSHOT = "0ae2cf26426822135fc10d337fcacf580b7ed833"
ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
SOURCE = "python/deepviz/src/deepviz/"
TESTS = "python/deepviz/tests/"


def git(*args: str) -> bytes:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, timeout=30,
    ).stdout


def blob(commit: str, path: str) -> bytes:
    return git("show", f"{commit}:{path}")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def declared_cases(data: bytes) -> dict[str, int]:
    """Count only explicit literal parametrize products; do not collect pytest."""
    tree = ast.parse(data)
    literals = {
        node.targets[0].id: node.value
        for node in tree.body
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
    }
    counts = {}
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef) or not node.name.startswith("test_"):
            continue
        count = 1
        for decorator in node.decorator_list:
            if (isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute)
                    and decorator.func.attr == "parametrize"):
                values = decorator.args[1]
                if isinstance(values, ast.Name):
                    values = literals[values.id]
                assert isinstance(values, (ast.List, ast.Tuple))
                count *= len(values.elts)
        counts[node.name] = count
    return counts


def main() -> None:
    assert git("rev-parse", f"{SEALED}^{{commit}}").decode().strip() == SEALED
    assert git("rev-parse", f"{P2}^{{commit}}").decode().strip() == P2
    source_paths = [SOURCE + name for name in (
        "tools.py", "mcp_server.py", "__init__.py", "models.py", "normalize.py",
        "recommend.py", "render.py", "engines.py", "cli.py",
    )]
    test_paths = [TESTS + name for name in (
        "test_r14_tool_json_boundary.py", "test_r14_mcp_resource_budget.py",
    )]
    paths = source_paths + test_paths + ["pyproject.toml"]
    identities = []
    for path in paths:
        data = blob(SEALED, path)
        identities.append({
            "path": path, "blob": git("rev-parse", f"{SEALED}:{path}").decode().strip(),
            "sha256": digest(data), "bytes": len(data), "lines": len(data.splitlines()),
            "exact_equal_p2": blob(P2, path) == data,
        })
    assert all(item["exact_equal_p2"] for item in identities)
    assert blob(P1, SOURCE + "tools.py") == blob(SEALED, SOURCE + "tools.py")
    p1_mcp = ast.parse(blob(P1, SOURCE + "mcp_server.py"))
    sealed_mcp = ast.parse(blob(SEALED, SOURCE + "mcp_server.py"))
    p1_class = next(node for node in ast.walk(p1_mcp) if isinstance(node, ast.ClassDef)
                    and node.name == "ValidatedMCP")
    sealed_class = next(node for node in ast.walk(sealed_mcp) if isinstance(node, ast.ClassDef)
                        and node.name == "ValidatedMCP")
    assert ast.dump(p1_class) == ast.dump(sealed_class)
    declared = {path: declared_cases(blob(SEALED, path)) for path in test_paths}
    assert [sum(cases.values()) for cases in declared.values()] == [37, 6]
    sdk_files = {
        "mcp": ["server/fastmcp/server.py", "server/fastmcp/tools/base.py",
                "server/fastmcp/tools/tool_manager.py", "server/fastmcp/utilities/func_metadata.py",
                "server/fastmcp/resources/resource_manager.py", "server/fastmcp/resources/types.py"],
        "langchain-core": ["tools/base.py", "tools/structured.py"],
    }
    sdk = []
    for package, names in sdk_files.items():
        module_name = package.replace("-", "_")
        for name in names:
            data = Path(str(distribution(package).locate_file(f"{module_name}/{name}"))).read_bytes()
            sdk.append({"package": package, "version": version(package), "path": name,
                        "sha256": digest(data), "bytes": len(data)})
    diff = git("diff", BASE, SEALED, "--", SOURCE + "tools.py", SOURCE + "mcp_server.py")
    (OUT / "two-file.diff").write_bytes(diff)
    main_paths = git("ls-tree", "-r", "--name-only", MAIN_SNAPSHOT).decode().splitlines()
    assert len(main_paths) == 7 and SOURCE + "tools.py" not in main_paths
    assert "_table_budget" not in blob(SEALED, SOURCE + "render.py").decode()
    assert "_table_budget" in blob("1c721bb6497746641b897eb2eb938cfad52068d2", SOURCE + "render.py").decode()
    report = {
        "observed_utc": datetime.now(UTC).isoformat(), "mode": "source-only / no product imports",
        "owner": "ses_de567801cffeGZFlt50oYv0Dnt", "source": SEALED,
        "product_p1": P1, "product_p2": P2, "base": BASE,
        "own_head_at_audit": git("rev-parse", "HEAD").decode().strip(),
        "python": sys.version.split()[0], "sealed_files": identities, "installed_sdk_files": sdk,
        "declared_author_cases_not_executed": declared,
        "declared_author_case_total_not_executed": 43,
        "tools_p1_equal_sealed": True, "mcp_admission_p1_ast_equal_sealed": True,
        "two_file_diff_sha256": digest(diff),
        "main_snapshot_not_live_remote": MAIN_SNAPSHOT, "main_snapshot_paths": main_paths,
        "dense_preflight_absent_from_sealed_render": True,
        "known_dense_preflight_dependency": "1c721bb6497746641b897eb2eb938cfad52068d2",
        "product_tests_executed": 0, "sdk_calls": 0, "stdio_calls": 0,
        "browser_calls": 0, "new_counterexamples_required": 0,
        "production_or_existing_probe_writes": 0, "api_mutations": 0, "installs_or_spawns": 0,
    }
    assert not any(name == "deepviz" or name.startswith("deepviz.") for name in sys.modules)
    (OUT / "source-audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"audit_exit": 0, "source": SEALED, "sealed_blobs": len(identities),
                      "sdk_file_hashes": len(sdk), "author43_read_not_run": True,
                      "source_and_tests_unchanged_p2_to_sealed": True,
                      "product_tests_or_sdk_stdio_browser_calls": 0}))


if __name__ == "__main__":
    main()
