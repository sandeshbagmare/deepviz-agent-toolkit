"""Finite MCP lifetime issuance must reject before output and preserve prior files."""
from __future__ import annotations

import asyncio
import base64
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

pytest.importorskip("mcp")
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

from deepviz.mcp_server import create_server

ROWS = [{"category": "Alpha", "value": 3}, {"category": "Beta", "value": 7}]
SPEC = {"kind": "bar", "x": "category", "y": "value", "aggregation": "none"}


def call(server: Any, data: Any = ROWS, spec: Any = SPEC) -> list[Any]:
    return asyncio.run(server.call_tool("render_echarts", {"data": data, "spec": spec}))


def metadata(content: Any) -> dict[str, Any]:
    return json.loads(next(item.text for item in content if isinstance(item, types.TextContent)))


def files(output: Path) -> dict[str, bytes]:
    return {str(path.relative_to(output)): path.read_bytes() for path in output.rglob("*") if path.is_file()}


def test_sdk_capacity_rejects_before_output_and_preserves_earliest_resource(tmp_path: Path) -> None:
    output = tmp_path / "out"
    output.mkdir()
    (output / "host-owned.txt").write_text("preserve caller output", encoding="utf-8")
    server = create_server(output)
    first = call(server)
    first_uri = metadata(first)["resources"][0]["uri"]
    original = list(asyncio.run(server.read_resource(first_uri)))[0].content
    for _ in range(63):
        call(server)
    assert len(asyncio.run(server.list_resources())) == 128
    before = files(output)
    rejected = []
    for _ in range(3):
        try:
            call(server)
        except Exception as error:
            rejected.append(str(error))
    assert len(rejected) == 3, "Successful renders must not retain unbounded closures/resources"
    assert all("resource" in note.lower() and ("limit" in note.lower() or "capacity" in note.lower()) for note in rejected)
    assert files(output) == before, "Capacity rejection must precede generation; do not delete successful host files"
    assert len(asyncio.run(server.list_resources())) == 128
    assert not asyncio.run(server.list_resource_templates())
    assert list(asyncio.run(server.read_resource(first_uri)))[0].content == original
    with pytest.raises(ValueError, match="Unknown resource"):
        asyncio.run(create_server(output).read_resource(first_uri))
    assert (output / "host-owned.txt").read_text(encoding="utf-8") == "preserve caller output"
    # A new host-created server is the explicit lifetime reset, not silent expiry/deletion.
    assert metadata(call(create_server(output)))["input_count"] == 2


@pytest.mark.parametrize("engine,remaining", [("matplotlib", 0), ("vega", 1)])
def test_capacity_reserves_the_real_artifact_count_for_static_engines(tmp_path: Path, engine: str, remaining: int) -> None:
    output = tmp_path / "out"
    server = create_server(output)
    for _ in range(62):
        call(server)
    result = asyncio.run(server.call_tool(f"render_{engine}", {"data": ROWS, "spec": SPEC}))
    resources = metadata(result)["resources"]
    assert len(resources) == 4 - remaining
    assert len(asyncio.run(server.list_resources())) == 128 - remaining
    for resource in resources:
        assert list(asyncio.run(server.read_resource(resource["uri"])))
    before = files(output)
    with pytest.raises(Exception, match="capacity"):
        call(server)
    assert files(output) == before


def test_failed_render_does_not_consume_capacity_or_touch_peer_outputs(tmp_path: Path) -> None:
    output = tmp_path / "out"
    server = create_server(output)
    first = call(server)
    before = files(output)
    for _ in range(3):
        with pytest.raises(Exception, match="missing"):
            call(server, spec={**SPEC, "x": "missing"})
    assert files(output) == before
    assert len(asyncio.run(server.list_resources())) == 2
    for _ in range(63):
        call(server)
    assert len(asyncio.run(server.list_resources())) == 128
    with pytest.raises(Exception, match="resource|Resource"):
        call(server)
    assert list(asyncio.run(server.read_resource(metadata(first)["resources"][0]["uri"])))


def test_concurrent_render_reservations_do_not_overissue(tmp_path: Path) -> None:
    output = tmp_path / "out"
    server = create_server(output)
    for _ in range(62):
        call(server)
    before = len(files(output))

    def attempt(_: int) -> bool:
        try:
            call(server)
        except Exception as error:
            assert "resource" in str(error).lower()
            return False
        return True

    with ThreadPoolExecutor(max_workers=8) as pool:
        accepted = list(pool.map(attempt, range(8)))
    assert sum(accepted) == 2, accepted
    assert len(asyncio.run(server.list_resources())) == 128
    assert len(files(output)) == before + 4, "Only two reserved requests may generate files"


def test_real_stdio_resource_capacity_remains_readable_and_normalization_recovers(tmp_path: Path) -> None:
    output = tmp_path / "out"

    async def exercise() -> None:
        source = Path(__file__).resolve().parents[1] / "src"
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "deepviz.mcp_server", "--output-dir", str(output)],
            env={**os.environ, "PYTHONPATH": str(source), "PYTHONUTF8": "1"},
        )
        with (tmp_path / "stderr.txt").open("w", encoding="utf-8") as errlog:
            async with stdio_client(params, errlog=errlog) as (read, write):
                async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=45)) as client:
                    await client.initialize()
                    earliest = None
                    for _ in range(64):
                        result = await client.call_tool("render_echarts", {"data": ROWS, "spec": SPEC})
                        assert not result.isError
                        if earliest is None:
                            earliest = next(item for item in result.content if isinstance(item, types.ResourceLink))
                    listed = await client.list_resources()
                    assert len(listed.resources) == 128
                    before = files(output)
                    response = await client.call_tool("render_echarts", {"data": ROWS, "spec": SPEC})
                    denied = response.isError
                    assert files(output) == before, "Real transport cannot allocate another successful render over capacity"
                    assert denied, "The 65th two-resource render must be an explicit MCP error"
                    assert not any(isinstance(item, types.ResourceLink) for item in response.content)
                    assert len((await client.list_resources()).resources) == 128
                    assert earliest is not None
                    resource = await client.read_resource(earliest.uri)
                    item = resource.contents[0]
                    raw = item.text.encode("utf-8") if isinstance(item, types.TextResourceContents) else base64.b64decode(item.blob)
                    assert raw
                    normalized = await client.call_tool("normalize_data", {"data": ROWS})
                    assert not normalized.isError and metadata(normalized.content)["input_count"] == 2

    asyncio.run(asyncio.wait_for(exercise(), timeout=90))
