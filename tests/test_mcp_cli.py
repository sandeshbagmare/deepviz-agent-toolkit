"""Exercise CLI commands and the real MCP SDK/stdio trust boundary."""
from __future__ import annotations

import asyncio
import base64
import json
import os
import subprocess
import sys
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

ROWS = [{"label": "東京 📊", "value": 3}, {"label": "B", "value": 7}]
SPEC = {"kind": "bar", "x": "label", "y": "value", "aggregation": "none"}
TOOL_NAMES = {
    "normalize_data", "recommend_chart", "render_matplotlib", "render_plotly",
    "render_vega", "render_echarts", "render_antv",
}
SOURCE = Path(__file__).resolve().parents[1] / "src"


def metadata(result: Any) -> dict[str, Any]:
    if isinstance(result, tuple):
        result = result[0]
    return json.loads(next(block.text for block in result if block.type == "text"))


def command(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "deepviz.cli", *args], cwd=cwd,
        env={**os.environ, "PYTHONPATH": str(SOURCE), "PYTHONUTF8": "1"}, capture_output=True, text=True,
        encoding="utf-8", timeout=60, check=False,
    )


def test_cli_help_is_available_without_running_a_server(tmp_path: Path) -> None:
    response = command("--help", cwd=tmp_path)
    assert response.returncode == 0, response.stderr
    assert all(name in response.stdout for name in ("render", "normalize", "recommend", "mcp"))
    assert list(tmp_path.iterdir()) == []


def test_cli_file_commands_return_json_and_preserve_the_source(tmp_path: Path) -> None:
    source = tmp_path / "rows.json"
    source.write_text(json.dumps(ROWS, ensure_ascii=False), encoding="utf-8")
    spec = tmp_path / "chart.json"
    spec.write_text(json.dumps(SPEC), encoding="utf-8")
    output = tmp_path / "out"
    for operation in ("normalize", "recommend", "render"):
        args = [operation, str(source), "--output-dir", str(output)]
        if operation == "render":
            args += ["--spec", str(spec), "--engine", "matplotlib"]
        response = command(*args, cwd=tmp_path)
        assert response.returncode == 0, response.stderr
        info = json.loads(response.stdout)
        assert info["input_count"] == 2
        if operation == "render":
            png = next(Path(name) for name in info["paths"] if name.endswith(".png"))
            assert png.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    assert json.loads(source.read_text(encoding="utf-8")) == ROWS


@pytest.mark.parametrize("raw", ['{"kind":"bar","kind":"table"}', '{"kind":"bar","width":true}'])
def test_cli_rejects_invalid_spec_without_allocating_output(tmp_path: Path, raw: str) -> None:
    source, spec, output = tmp_path / "rows.json", tmp_path / "chart.json", tmp_path / "out"
    source.write_text(json.dumps(ROWS), encoding="utf-8")
    spec.write_text(raw, encoding="utf-8")
    response = command("render", str(source), "--spec", str(spec), "--output-dir", str(output), cwd=tmp_path)
    assert response.returncode == 2
    assert response.stdout == "" and "error:" in response.stderr
    assert not output.exists()


def test_sdk_discovery_and_errors_share_a_strict_input_contract(tmp_path: Path) -> None:
    pytest.importorskip("mcp")
    from deepviz.mcp_server import create_server

    async def exercise() -> None:
        server = create_server(tmp_path / "out")
        tools = {tool.name: tool for tool in await server.list_tools()}
        assert set(tools) == TOOL_NAMES
        assert all(item.inputSchema["additionalProperties"] is False for item in tools.values())
        for arguments in (
            {"data": ROWS, "extra": True}, {"data": '[{"value":1,"value":2}]'},
            {"data": "[" * 1500 + "]" * 1500}, {"data": " " * 1_000_001 + json.dumps(ROWS)},
        ):
            with pytest.raises(ValueError):
                await server.call_tool("normalize_data", arguments)
        valid = metadata(await server.call_tool("normalize_data", {"data": json.dumps(ROWS)}))
        assert valid["input_count"] == valid["output_count"] == 2
        assert not (tmp_path / "out").exists()

    asyncio.run(exercise())


def test_sdk_resource_capacity_preserves_issued_artifacts_and_recovers(tmp_path: Path) -> None:
    pytest.importorskip("mcp")
    from deepviz.mcp_server import create_server
    from mcp.server.fastmcp.exceptions import ToolError

    async def exercise() -> None:
        output = tmp_path / "out"
        output.mkdir()
        sentinel = output / "host-owned.txt"
        sentinel.write_text("preserve", encoding="utf-8")
        server = create_server(output)
        first_uri = None
        for _ in range(64):
            info = metadata(await server.call_tool("render_echarts", {"data": ROWS, "spec": SPEC}))
            assert len(info["resources"]) == 2
            first_uri = first_uri or next(item["uri"] for item in info["resources"] if item["name"] == "manifest.json")
        before = {path: path.read_bytes() for path in output.rglob("*") if path.is_file()}
        with pytest.raises((ValueError, ToolError), match="capacity"):
            await server.call_tool("render_echarts", {"data": ROWS, "spec": SPEC})
        assert {path: path.read_bytes() for path in output.rglob("*") if path.is_file()} == before
        assert len(await server.list_resources()) == 128
        resource = list(await server.read_resource(first_uri))[0]
        assert json.loads(resource.content)["charts"][0]["records"] == ROWS
        assert sentinel.read_text(encoding="utf-8") == "preserve"
        assert metadata(await server.call_tool("normalize_data", {"data": ROWS}))["input_count"] == 2

    asyncio.run(exercise())


def test_failed_render_releases_slots_and_removes_only_failed_request_output(tmp_path: Path) -> None:
    pytest.importorskip("mcp")
    from deepviz.mcp_server import create_server
    from mcp.server.fastmcp.exceptions import ToolError

    async def exercise() -> None:
        output = tmp_path / "out"
        output.mkdir()
        sentinel = output / "host-owned.txt"
        sentinel.write_text("preserve", encoding="utf-8")
        server = create_server(output)
        for _ in range(35):
            with pytest.raises((ValueError, ToolError)):
                await server.call_tool("render_matplotlib", {"data": [{"label": "A"}], "spec": SPEC})
        assert list(output.iterdir()) == [sentinel]
        assert await server.list_resources() == []
        valid = metadata(await server.call_tool("render_matplotlib", {"data": ROWS, "spec": SPEC}))
        assert valid["input_count"] == 2 and valid["resources"]

    asyncio.run(exercise())


def test_concurrent_renders_cannot_overcommit_resource_capacity(tmp_path: Path) -> None:
    pytest.importorskip("mcp")
    from deepviz.mcp_server import create_server
    from mcp.server.fastmcp.exceptions import ToolError

    async def exercise() -> None:
        server = create_server(tmp_path / "out")
        arguments = {"data": ROWS, "spec": SPEC}
        for _ in range(62):
            await server.call_tool("render_echarts", arguments)
        results = await asyncio.gather(
            *(server.call_tool("render_echarts", arguments) for _ in range(4)), return_exceptions=True,
        )
        successful = [result for result in results if not isinstance(result, BaseException)]
        rejected = [result for result in results if isinstance(result, BaseException)]
        assert len(successful) == len(rejected) == 2
        assert all(isinstance(error, (ValueError, ToolError)) for error in rejected)
        assert len(await server.list_resources()) == 128
        assert all(len(metadata(result)["resources"]) == 2 for result in successful)

    asyncio.run(exercise())


@pytest.mark.parametrize("entrypoint", [["deepviz.mcp_server"], ["deepviz.cli", "mcp"]])
def test_real_stdio_roundtrip_errors_resource_reads_and_shutdown(tmp_path: Path, entrypoint: list[str]) -> None:
    pytest.importorskip("mcp")
    from mcp import ClientSession, StdioServerParameters, types
    from mcp.client.stdio import stdio_client
    from mcp.shared.exceptions import McpError

    async def exercise() -> None:
        output = tmp_path / "out"
        output.mkdir()
        sentinel = output / "host-owned.txt"
        sentinel.write_text("preserve", encoding="utf-8")
        params = StdioServerParameters(
            command=sys.executable, args=["-m", *entrypoint, "--output-dir", str(output)],
            cwd=str(tmp_path), env={**os.environ, "PYTHONPATH": str(SOURCE), "PYTHONUTF8": "1"},
        )
        with (tmp_path / "stderr.txt").open("w", encoding="utf-8") as stderr:
            async with stdio_client(params, errlog=stderr) as (read, write):
                async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=45)) as client:
                    initialized = await client.initialize()
                    (tmp_path / "protocol.json").write_text(json.dumps({
                        "protocol_version": initialized.protocolVersion,
                        "server_info": initialized.serverInfo.model_dump(),
                    }), encoding="utf-8")
                    assert {tool.name for tool in (await client.list_tools()).tools} == TOOL_NAMES
                    for arguments in (
                        {"data": '[{"value":1,"value":2}]'}, {"data": "[not-json"},
                        {"data": " " * 1_000_001 + json.dumps(ROWS)}, {"data": ROWS, "extra": True},
                        {"data": {"file": "../outside.json"}},
                    ):
                        rejected = await client.call_tool("normalize_data", arguments)
                        assert rejected.isError
                        assert len(json.dumps(rejected.model_dump()).encode("utf-8")) < 16_384
                    normalized = await client.call_tool("normalize_data", {"data": ROWS})
                    assert not normalized.isError
                    reference = {"dataset_id": metadata(normalized.content)["dataset_id"]}
                    recommendation = await client.call_tool("recommend_chart", {"data": reference})
                    assert not recommendation.isError
                    rendered = await client.call_tool("render_matplotlib", {"data": reference, "spec": SPEC})
                    assert not rendered.isError
                    info = metadata(rendered.content)
                    assert info["input_count"] == info["output_count"] == 2 and "paths" not in info
                    assert len(json.dumps(rendered.model_dump()).encode("utf-8")) < 1_000_000
                    preview = next(block for block in rendered.content if isinstance(block, types.ImageContent))
                    assert base64.b64decode(preview.data).startswith(b"\x89PNG\r\n\x1a\n")
                    manifest_uri = next(item["uri"] for item in info["resources"] if item["name"] == "manifest.json")
                    manifest = (await client.read_resource(manifest_uri)).contents[0]
                    assert isinstance(manifest, types.TextResourceContents)
                    assert json.loads(manifest.text)["charts"][0]["records"] == ROWS
                    with pytest.raises(McpError):
                        await client.read_resource(sentinel.as_uri())
                    assert sentinel.read_text(encoding="utf-8") == "preserve"

    asyncio.run(asyncio.wait_for(exercise(), timeout=120))


@pytest.mark.parametrize("method", ["run", "arun"])
def test_invalid_bare_json_is_rejected_before_agent_callbacks(tmp_path: Path, method: str) -> None:
    pytest.importorskip("langchain_core")
    from deepviz.tools import create_tools
    from langchain_core.callbacks import BaseCallbackHandler

    class Trace(BaseCallbackHandler):
        def __init__(self) -> None:
            self.payloads: list[str] = []

        def on_tool_start(self, serialized: dict[str, Any], input_str: str, **kwargs: Any) -> None:
            self.payloads.append(input_str)

    tool = next(tool for tool in create_tools(tmp_path / "out") if tool.name == "normalize_data")
    trace = Trace()
    with pytest.raises(ValueError):
        result = getattr(tool, method)('[{"value":1,"value":2}]', callbacks=[trace])
        if method == "arun":
            asyncio.run(result)
    assert trace.payloads == []
    result = getattr(tool, method)(json.dumps(ROWS), callbacks=[trace])
    result = asyncio.run(result) if method == "arun" else result
    assert result["input_count"] == 2 and len(trace.payloads) == 1
