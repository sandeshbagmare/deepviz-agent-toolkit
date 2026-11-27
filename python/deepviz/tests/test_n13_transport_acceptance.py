"""N13 independent real-transport/agent/CLI acceptance on a fixed candidate."""
from __future__ import annotations

import asyncio
import base64
import hashlib
import importlib.metadata
import json
import os
import subprocess
import sys
from contextlib import asynccontextmanager
from datetime import timedelta
from pathlib import Path

import anyio
import pytest
from mcp import ClientSession, StdioServerParameters, types
from mcp.client import stdio
from mcp.shared.exceptions import McpError

ENGINES = ("matplotlib", "plotly", "vega", "echarts", "antv")
TOOL_NAMES = {f"render_{engine}" for engine in ENGINES} | {"normalize_data", "recommend_chart"}
ROWS = [
    {"category": "Alpha", "amount": 2},
    {"category": "Alpha", "amount": 5},
    {"category": "Beta", "amount": 11},
    {"category": "Gamma", "amount": -3},
]
EXPECTED = [
    {"category": "Alpha", "amount": 7},
    {"category": "Beta", "amount": 11},
    {"category": "Gamma", "amount": -3},
]
SPEC = {"kind": "bar", "x": "category", "y": "amount", "title": "N13 transport oracle"}
ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "python/deepviz/src"


def installed_script(name: str) -> str:
    return str(Path(sys.executable).with_name(f"{name}.exe" if os.name == "nt" else name))


def dump(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


@pytest.fixture(scope="session", autouse=True)
def source_identity():
    import deepviz

    versions = {}
    for name in ("deepviz-agent-toolkit", "mcp", "deepagents", "langchain-core", "langchain",
                 "langgraph", "pydantic", "matplotlib", "plotly", "vl-convert-python", "pyarrow", "pytest"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = "NOT INSTALLED"
    assert Path(deepviz.__file__).resolve().is_relative_to(SOURCE)
    identity = {
        "python": sys.version,
        "executable": sys.executable,
        "deepviz_file": deepviz.__file__,
        "git_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "git_status": subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
        "versions": versions,
        "production_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in sorted((SOURCE / "deepviz").glob("*.py"))},
    }
    dump(ROOT / "artifacts/local/N13/source-identity.json", identity)
    return identity


@asynccontextmanager
async def server_at(root: Path, *, data_dir: Path | None = None, entry: str = "source-module"):
    root.mkdir(parents=True, exist_ok=True)
    if entry == "source-module":
        command, args = sys.executable, ["-m", "deepviz.mcp_server"]
    elif entry == "source-cli":
        command, args = sys.executable, ["-m", "deepviz.cli", "mcp"]
    elif entry == "installed-server":
        command, args = installed_script("deepviz-mcp"), []
    elif entry == "installed-cli":
        command, args = installed_script("deepviz"), ["mcp"]
    else:
        raise ValueError(f"Unknown tester entry: {entry}")
    args.extend(["--output-dir", str(root / "server-output")])
    if data_dir is not None:
        args.extend(["--data-dir", str(data_dir)])
    params = StdioServerParameters(
        command=command, args=args, cwd=str(root),
        env={**os.environ, "PYTHONPATH": str(SOURCE), "PYTHONUTF8": "1", "MPLBACKEND": "Agg"},
    )
    with (root / "server.stderr").open("w", encoding="utf-8") as stderr, anyio.fail_after(120):
        async with stdio.stdio_client(params, errlog=stderr) as (read, write):
            async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=60)) as session:
                initialized = await session.initialize()
                dump(root / "initialize.json", initialized.model_dump(mode="json"))
                assert initialized.serverInfo.name == "DeepViz"
                yield session


def metadata(result: types.CallToolResult) -> dict:
    assert not result.isError, result
    return json.loads(next(block.text for block in result.content if isinstance(block, types.TextContent)))


def assert_manifest(manifest: dict, engine: str) -> None:
    assert manifest["engine"] == engine
    assert manifest["strategy"] == "sum"
    chart = manifest["charts"][0]
    assert chart["requested_kind"] == chart["rendered_kind"] == "bar"
    assert chart["input_count"] == 4 and chart["output_count"] == 3
    assert chart["records"] == EXPECTED
    assert chart["spec"]["x"] == "category" and chart["spec"]["y"] == "amount"


def test_n13_one_stdio_session_five_engine_chain_and_retrieved_semantics(tmp_path, monkeypatch):
    processes = []
    original = stdio._create_platform_compatible_process

    async def observe_process(*args, **kwargs):
        process = await original(*args, **kwargs)
        processes.append(process)
        return process

    monkeypatch.setattr(stdio, "_create_platform_compatible_process", observe_process)
    journal = []

    async def exercise():
        async with server_at(tmp_path) as session:
            discovery = await session.list_tools()
            dump(tmp_path / "tools.json", discovery.model_dump(mode="json"))
            assert {tool.name for tool in discovery.tools} == TOOL_NAMES
            assert not (await session.list_resources()).resources
            for tool in discovery.tools:
                assert "output_dir" not in tool.inputSchema["properties"]
            normalized = metadata(await session.call_tool("normalize_data", {"data": ROWS}))
            journal.append({"call": "normalize_data", "result": normalized})
            assert normalized["input_count"] == normalized["output_count"] == 4
            assert "records" not in normalized and "Alpha" not in json.dumps(normalized)
            handle = {"dataset_id": normalized["dataset_id"]}
            advice = metadata(await session.call_tool("recommend_chart", {"data": handle}))
            journal.append({"call": "recommend_chart", "result": advice})
            assert advice["dataset_id"] == handle["dataset_id"] and advice["spec"]["kind"] == "bar"
            all_uris = []
            for engine in ENGINES:
                result = await session.call_tool(f"render_{engine}", {"data": handle, "spec": advice["spec"]})
                info = metadata(result)
                journal.append({"call": f"render_{engine}", "result": info})
                assert "paths" not in info
                assert info["engine"] == engine and info["input_count"] == 4 and info["output_count"] == 3
                links = [block for block in result.content if isinstance(block, types.ResourceLink)]
                assert {str(link.uri) for link in links} == {r["uri"] for r in info["resources"]}
                obtained = {}
                for link in links:
                    response = await session.read_resource(link.uri)
                    assert len(response.contents) == 1
                    block = response.contents[0]
                    data = base64.b64decode(block.blob, validate=True) if isinstance(
                        block, types.BlobResourceContents
                    ) else block.text.encode("utf-8")
                    destination = tmp_path / "retrieved" / engine / link.name
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(data)
                    matches = list((tmp_path / "server-output").rglob(link.name))
                    matching = [p for p in matches if p.read_bytes() == data]
                    assert matching, f"Retrieved {link.uri} differs from every server file"
                    obtained[link.name] = {"uri": str(link.uri), "bytes": len(data),
                                           "sha256": hashlib.sha256(data).hexdigest(), "mime": block.mimeType}
                    all_uris.append(str(link.uri))
                    if link.mimeType == "application/json":
                        assert_manifest(json.loads(data), engine)
                    if link.mimeType == "image/png":
                        inline = next(b for b in result.content if isinstance(b, types.ImageContent))
                        assert base64.b64decode(inline.data, validate=True) == data
                journal.append({"retrieved": engine, "resources": obtained})
            listed = {str(resource.uri) for resource in (await session.list_resources()).resources}
            assert listed == set(all_uris)
            assert len(all_uris) == len(set(all_uris))
            dump(tmp_path / "calls-and-retrieval.json", journal)

    asyncio.run(exercise())
    assert len(processes) == 1 and processes[0].returncode == 0
    dump(tmp_path / "cleanup.json", {"process_count": len(processes), "exit_code": processes[0].returncode})


def test_n13_handle_eviction_session_isolation_and_default_no_filesystem(tmp_path):
    secret = tmp_path / "outside-secret.json"
    sentinel = "N13-DO-NOT-LEAK-RAW-FILE-CONTENT"
    secret.write_text(json.dumps([{"secret": sentinel}]), encoding="utf-8")
    errors = []

    async def exercise():
        async with server_at(tmp_path / "first") as session:
            handles = []
            for index in range(33):
                info = metadata(await session.call_tool("normalize_data", {"data": [{"x": index}]}))
                handles.append(info["dataset_id"])
            for tool in ("normalize_data", "recommend_chart", "render_echarts"):
                arguments = {"data": {"dataset_id": handles[0]}}
                if tool == "render_echarts":
                    arguments["spec"] = SPEC
                denied = await session.call_tool(tool, arguments)
                assert denied.isError
                text = " ".join(b.text for b in denied.content if isinstance(b, types.TextContent))
                assert "expired" in text.lower()
                errors.append({"tool": tool, "error": text})
            assert metadata(await session.call_tool("recommend_chart", {
                "data": {"dataset_id": handles[-1]}
            }))["input_count"] == 1
            for source in ({"file": str(secret)}, {"file": "../outside-secret.json"}, str(secret),
                           json.dumps(str(secret)), {"file": "https://example.invalid/data"}):
                denied = await session.call_tool("normalize_data", {"data": source})
                assert denied.isError
                assert sentinel not in denied.model_dump_json()
                errors.append({"source": source, "error": denied.model_dump(mode="json")})
            rendered = metadata(await session.call_tool("render_echarts", {"data": ROWS, "spec": SPEC}))
            uri = rendered["resources"][0]["uri"]
            for unauthorized in (secret.as_uri(), "deepviz://artifacts/../../outside-secret.json",
                                 "deepviz://artifacts/%2e%2e/outside-secret.json"):
                with pytest.raises(McpError) as error:
                    await session.read_resource(unauthorized)
                assert sentinel not in str(error.value)
                errors.append({"resource": unauthorized, "error": str(error.value)})
        async with server_at(tmp_path / "second") as session:
            assert not (await session.list_resources()).resources
            denied = await session.call_tool("recommend_chart", {"data": {"dataset_id": handles[-1]}})
            assert denied.isError
            with pytest.raises(McpError):
                await session.read_resource(uri)
        dump(tmp_path / "denials.json", errors)

    asyncio.run(exercise())


def test_n13_actual_deep_agent_runs_seven_tool_chain(tmp_path):
    from deepagents import create_deep_agent
    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.messages import AIMessage, ToolMessage
    from langchain_core.outputs import ChatGeneration, ChatResult
    from pydantic import PrivateAttr

    from deepviz.tools import create_tools

    class DeterministicToolChat(BaseChatModel):
        _bound_names: set[str] = PrivateAttr(default_factory=set)

        @property
        def _llm_type(self):
            return "n13-local-transport-oracle"

        def bind_tools(self, tools, **kwargs):
            self._bound_names.update(tool.name for tool in tools)
            return self

        def _generate(self, messages, stop=None, run_manager=None, **kwargs):
            prior = [m for m in messages if isinstance(m, ToolMessage)]
            if len(prior) >= 7:
                message = AIMessage(content="Five chart artifacts ready.")
            else:
                if not prior:
                    name, arguments = "normalize_data", {"data": ROWS}
                elif len(prior) == 1:
                    name, arguments = "recommend_chart", {"data": {
                        "dataset_id": json.loads(prior[0].content)["dataset_id"]
                    }}
                else:
                    advice = json.loads(prior[1].content)
                    name = f"render_{ENGINES[len(prior) - 2]}"
                    arguments = {"data": {"dataset_id": advice["dataset_id"]}, "spec": advice["spec"]}
                message = AIMessage(content="", tool_calls=[{
                    "name": name, "args": arguments, "id": f"n13-{len(prior)}"
                }])
            return ChatResult(generations=[ChatGeneration(message=message)])

    model = DeterministicToolChat()
    agent = create_deep_agent(model=model, tools=create_tools(tmp_path / "agent-output"))
    result = agent.invoke({"messages": [{"role": "user", "content": "Compare the known category amounts."}]},
                          config={"recursion_limit": 40})
    messages = [m for m in result["messages"] if isinstance(m, ToolMessage)]
    assert [m.name for m in messages] == ["normalize_data", "recommend_chart", *[
        f"render_{engine}" for engine in ENGINES
    ]]
    assert TOOL_NAMES <= model._bound_names
    assert all(m.status == "success" for m in messages)
    for message, engine in zip(messages[2:], ENGINES, strict=True):
        info = json.loads(message.content)
        assert info["input_count"] == 4 and info["output_count"] == 3
        manifest = next(Path(p) for p in info["paths"] if Path(p).name == "manifest.json")
        assert_manifest(json.loads(manifest.read_text(encoding="utf-8")), engine)
    dump(tmp_path / "agent-tool-messages.json", [{"name": m.name, "status": m.status,
                                                 "result": json.loads(m.content)} for m in messages])


@pytest.mark.parametrize("entry", ["source-cli", "installed-server", "installed-cli"])
def test_n13_alternate_mcp_entrypoints_use_real_stdio_and_resources(tmp_path, entry):
    async def exercise():
        async with server_at(tmp_path, entry=entry) as session:
            assert {tool.name for tool in (await session.list_tools()).tools} == TOOL_NAMES
            normalized = metadata(await session.call_tool("normalize_data", {"data": ROWS}))
            advice = metadata(await session.call_tool("recommend_chart", {
                "data": {"dataset_id": normalized["dataset_id"]}
            }))
            info = metadata(await session.call_tool("render_echarts", {
                "data": {"dataset_id": advice["dataset_id"]}, "spec": advice["spec"]
            }))
            uri = next(r["uri"] for r in info["resources"] if r["mime_type"] == "application/json")
            response = await session.read_resource(uri)
            manifest = json.loads(response.contents[0].text)
            assert_manifest(manifest, "echarts")
            dump(tmp_path / "retrieved-manifest.json", manifest)

    asyncio.run(exercise())


@pytest.mark.parametrize("entry", ["source-module", "installed-entrypoint"])
@pytest.mark.parametrize("operation", ["normalize", "recommend", "render"])
def test_n13_cli_entrypoints_have_json_and_semantic_output(tmp_path, entry, operation):
    data = tmp_path / "data.json"
    spec = tmp_path / "spec.json"
    dump(data, ROWS)
    dump(spec, SPEC)
    command = [sys.executable, "-m", "deepviz.cli"] if entry == "source-module" else [
        installed_script("deepviz")
    ]
    command += [operation, str(data), "--output-dir", str(tmp_path / "cli-output")]
    if operation == "render":
        command += ["--spec", str(spec), "--engine", "matplotlib"]
    completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", timeout=60)
    dump(tmp_path / "command.json", {"argv": command, "exit_code": completed.returncode,
                                     "stdout": completed.stdout, "stderr": completed.stderr})
    assert completed.returncode == 0, completed.stderr
    info = json.loads(completed.stdout)
    assert info["input_count"] == 4
    if operation == "render":
        manifest = next(Path(p) for p in info["paths"] if Path(p).name == "manifest.json")
        assert_manifest(json.loads(manifest.read_text(encoding="utf-8")), "matplotlib")
    elif operation == "normalize":
        assert "records" not in info
    else:
        assert info["spec"]["kind"] == "bar"


@pytest.mark.parametrize("entry", ["source-module", "installed-entrypoint"])
@pytest.mark.parametrize("bad_case", ["missing-file", "malformed-json", "bad-spec", "missing-spec",
                                     "unsupported-engine", "unsupported-goal"])
def test_n13_cli_errors_are_nonzero_json_free_and_create_no_chart(tmp_path, entry, bad_case):
    data = tmp_path / "data.json"
    spec = tmp_path / "spec.json"
    dump(data, ROWS)
    dump(spec, SPEC)
    command = [sys.executable, "-m", "deepviz.cli"] if entry == "source-module" else [
        installed_script("deepviz")
    ]
    args = ["render", str(data), "--spec", str(spec), "--output-dir", str(tmp_path / "out")]
    if bad_case == "missing-file":
        args[1] = str(tmp_path / "absent.json")
    elif bad_case == "malformed-json":
        data.write_text("{broken JSON", encoding="utf-8")
    elif bad_case == "bad-spec":
        dump(spec, {**SPEC, "executable": "untrusted code is never permitted"})
    elif bad_case == "missing-spec":
        args = ["render", str(data)]
    elif bad_case == "unsupported-engine":
        args.extend(["--engine", "not-an-engine"])
    else:
        args = ["recommend", str(data), "--goal", "not-a-goal"]
    completed = subprocess.run(command + args, capture_output=True, text=True, encoding="utf-8", timeout=30)
    dump(tmp_path / "command.json", {"argv": command + args, "exit_code": completed.returncode,
                                     "stdout": completed.stdout, "stderr": completed.stderr})
    assert completed.returncode == 2
    assert not completed.stdout and "error" in completed.stderr.lower()
    assert "Traceback" not in completed.stderr
    assert not list(tmp_path.rglob("*.png"))
    assert not list(tmp_path.rglob("manifest.json"))
