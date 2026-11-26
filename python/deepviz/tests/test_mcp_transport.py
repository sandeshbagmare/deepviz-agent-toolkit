"""Black-box MCP interoperability against the real stdio server and SDK client."""
from __future__ import annotations

import asyncio
import base64
import errno
import json
import os
import sys
from contextlib import asynccontextmanager
from datetime import timedelta
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree

import anyio
import pytest

pytest.importorskip("mcp", reason="Install the mcp extra to exercise the actual stdio transport")
from mcp import ClientSession, StdioServerParameters, types
from mcp.client import stdio
from mcp.shared.exceptions import McpError

RENDERERS = ("matplotlib", "plotly", "vega", "echarts", "antv")
TOOL_NAMES = {f"render_{engine}" for engine in RENDERERS} | {"normalize_data", "recommend_chart"}
ROWS = [{"month": "Jan", "revenue": 12}, {"month": "Feb", "revenue": 18}]
SPEC = {"kind": "bar", "x": "month", "y": "revenue", "title": "Revenue"}


@asynccontextmanager
async def running_server(tmp_path: Path):
    source = Path(__file__).resolve().parents[1] / "src"
    env = {
        **os.environ,
        "PYTHONPATH": os.pathsep.join(filter(None, (str(source), os.environ.get("PYTHONPATH")))),
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUTF8": "1",
        "MPLBACKEND": "Agg",
    }
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "deepviz.mcp_server", "--output-dir", str(tmp_path / "artifacts"),
              "--data-dir", str(tmp_path)],
        env=env,
        cwd=str(tmp_path),
    )
    with (tmp_path / "server.stderr").open("w", encoding="utf-8") as errlog, anyio.fail_after(90):
        async with stdio.stdio_client(params, errlog=errlog) as (read, write):
            async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=45)) as session:
                initialized = await session.initialize()
                assert initialized.serverInfo.name == "DeepViz"
                assert initialized.capabilities.tools is not None
                yield session


def metadata(result: types.CallToolResult) -> dict:
    assert result.isError is False, result
    text = next(block.text for block in result.content if isinstance(block, types.TextContent))
    return json.loads(text)


def resource_links(result: types.CallToolResult) -> list[types.ResourceLink]:
    return [block for block in result.content if isinstance(block, types.ResourceLink)]


def test_stdio_initialize_and_discover_five_renderer_schemas(tmp_path):
    async def exercise():
        async with running_server(tmp_path) as session:
            result = await session.list_tools()
            tools = {tool.name: tool for tool in result.tools}
            assert set(tools) == TOOL_NAMES
            for engine in RENDERERS:
                schema = tools[f"render_{engine}"].inputSchema
                assert {"data", "spec"} <= set(schema["properties"])
                assert {"data", "spec"} <= set(schema["required"])
                assert "output_dir" not in schema["properties"]

    asyncio.run(exercise())


@pytest.mark.parametrize("engine", RENDERERS)
def test_stdio_renderer_returns_retrievable_mcp_content_not_only_local_paths(tmp_path, engine):
    async def exercise():
        async with running_server(tmp_path) as session:
            result = await session.call_tool(f"render_{engine}", {"data": ROWS, "spec": SPEC})
            info = metadata(result)
            assert info["engine"] == engine
            assert info["input_count"] == info["output_count"] == len(ROWS)
            links = resource_links(result)
            assert links, "A filesystem path alone cannot be consumed by an MCP client"
            assert {item["uri"] for item in info["resources"]} == {str(link.uri) for link in links}
            chart_content = []
            for link in links:
                resource = await session.read_resource(link.uri)
                assert resource.contents
                for block in resource.contents:
                    assert str(block.uri) == str(link.uri)
                    if isinstance(block, types.BlobResourceContents):
                        data = base64.b64decode(block.blob, validate=True)
                        assert data
                        if block.mimeType == "image/png":
                            assert data.startswith(b"\x89PNG\r\n\x1a\n")
                            chart_content.append(data)
                        elif block.mimeType == "image/svg+xml":
                            assert ElementTree.fromstring(data).tag.endswith("}svg")
                            chart_content.append(data)
                    else:
                        assert block.text
                        if block.mimeType == "image/svg+xml":
                            assert ElementTree.fromstring(block.text).tag.endswith("}svg")
                            chart_content.append(block.text)
                        elif block.mimeType == "text/html":
                            assert "<html" in block.text.lower() or "<!doctype" in block.text.lower()
                            chart_content.append(block.text)
                        elif block.mimeType == "application/json":
                            assert json.loads(block.text)["engine"] == engine
            assert chart_content, "Only metadata, not a chart, was retrievable"
            if engine == "matplotlib":
                images = [block for block in result.content if isinstance(block, types.ImageContent)]
                assert images and images[0].mimeType == "image/png"
                assert base64.b64decode(images[0].data, validate=True) in chart_content

    asyncio.run(exercise())


def test_stdio_schema_invalid_tool_calls_are_mcp_errors_without_artifacts(tmp_path):
    async def exercise():
        async with running_server(tmp_path) as session:
            invalid_arguments = [
                {"data": ROWS},
                {"data": ROWS, "spec": {**SPEC, "kind": "not-a-chart"}},
                {"data": ROWS, "spec": {**SPEC, "untrusted_expression": "do not execute"}},
            ]
            for arguments in invalid_arguments:
                result = await session.call_tool("render_matplotlib", arguments)
                assert result.isError is True, result
                assert any(isinstance(block, types.TextContent) and block.text for block in result.content)
                assert not resource_links(result)
            assert not list((tmp_path / "artifacts").rglob("*"))
            assert {tool.name for tool in (await session.list_tools()).tools} == TOOL_NAMES

    asyncio.run(exercise())


def test_stdio_artifact_reads_reject_traversal_and_arbitrary_file_uris(tmp_path):
    secret = tmp_path / "secret.txt"
    secret.write_text("outside-output-root-sentinel", encoding="utf-8")

    async def exercise():
        async with running_server(tmp_path) as session:
            result = await session.call_tool("render_echarts", {"data": ROWS, "spec": SPEC})
            metadata(result)
            link = resource_links(result)[0]
            parent = str(link.uri).rsplit("/", 1)[0]
            for uri in (f"{parent}/../../secret.txt", f"{parent}/%2e%2e/%2e%2e/secret.txt", secret.as_uri()):
                with pytest.raises(McpError) as denied:
                    await session.read_resource(uri)
                assert "outside-output-root-sentinel" not in str(denied.value)
            assert (await session.read_resource(link.uri)).contents

    asyncio.run(exercise())


def test_stdio_registered_artifact_symlink_swap_cannot_read_outside_output_root(tmp_path):
    secret = tmp_path / "secret.html"
    secret.write_text("outside-output-root-symlink-sentinel", encoding="utf-8")
    probe = tmp_path / "symlink-probe"
    try:
        probe.symlink_to(secret)
    except OSError as error:
        if error.errno in {errno.EPERM, errno.EACCES, errno.ENOSYS} or getattr(error, "winerror", None) == 1314:
            pytest.skip(f"Host does not permit symlink creation: {error}")
        raise
    probe.unlink()

    async def exercise():
        async with running_server(tmp_path) as session:
            result = await session.call_tool("render_echarts", {"data": ROWS, "spec": SPEC})
            metadata(result)
            link = next(link for link in resource_links(result) if link.mimeType == "text/html")
            assert (await session.read_resource(link.uri)).contents
            artifacts = list((tmp_path / "artifacts").rglob(Path(urlsplit(str(link.uri)).path).name))
            assert len(artifacts) == 1
            artifact = artifacts[0]
            artifact.unlink()
            artifact.symlink_to(secret)
            with pytest.raises(McpError) as denied:
                await session.read_resource(link.uri)
            assert "outside-output-root-symlink-sentinel" not in str(denied.value)

    asyncio.run(exercise())


def test_stdio_unicode_roundtrip_protocol_only_stdout_and_graceful_exit(tmp_path, monkeypatch):
    # Observe real SDK subprocess creation/decoding; do not replace the server or its transport.
    start_process = stdio._create_platform_compatible_process
    text_receive_stream = stdio.TextReceiveStream
    processes = []
    stdout = []

    async def record_process(*args, **kwargs):
        process = await start_process(*args, **kwargs)
        processes.append(process)
        return process

    async def record_stdout(*args, **kwargs):
        async for chunk in text_receive_stream(*args, **kwargs):
            stdout.append(chunk)
            yield chunk

    monkeypatch.setattr(stdio, "_create_platform_compatible_process", record_process)
    monkeypatch.setattr(stdio, "TextReceiveStream", record_stdout)
    unicode_root = tmp_path / "résultats-売上-📊"
    unicode_root.mkdir()
    title = 'Répartition — 売上 📊 </script><script>alert("untrusted")</script>'
    rows = [{"café": "東京 ☕", "売上": 12}, {"café": "München", "売上": 18}]
    spec = {"kind": "bar", "x": "café", "y": "売上", "title": title}

    async def exercise():
        async with running_server(unicode_root) as session:
            result = await session.call_tool("render_echarts", {"data": rows, "spec": spec})
            metadata(result)
            links = resource_links(result)
            manifest = next(link for link in links if link.mimeType == "application/json")
            response = await session.read_resource(manifest.uri)
            decoded = json.loads(response.contents[0].text)
            assert decoded["charts"][0]["spec"]["title"] == title
            assert decoded["charts"][0]["records"] == rows
            html = next(link for link in links if link.mimeType == "text/html")
            content = (await session.read_resource(html.uri)).contents[0].text
            assert title not in content, "The untrusted closing-script sequence must be escaped"
            assert "\ufffd" not in content

    asyncio.run(exercise())
    assert len(processes) == 1 and processes[0].returncode == 0, "Server needed forced termination"
    lines = "".join(stdout).splitlines()
    assert lines, "No stdio protocol output was observed"
    for line in lines:
        types.JSONRPCMessage.model_validate_json(line)
