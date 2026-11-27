"""Reject ambiguous/raw oversized data before tools or the MCP SDK discard it."""
from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

from deepviz import normalize
from deepviz.mcp_server import create_server
from deepviz.tools import ToolSession, create_tools

ROWS = [{"label": "東京 📊", "value": 7}]
SPEC = {"kind": "bar", "x": "label", "y": "value", "aggregation": "none"}
DUPLICATES = (
    '{"value":1,"value":2}',
    '[{"point":{"value":1,"value":2}}]',
    '{"file":"first.json","file":"second.json"}',
)


def metadata(result: Any) -> dict[str, Any]:
    """Read actual SDK content/structured output without replacing its dispatch."""
    if isinstance(result, dict):
        return result
    if isinstance(result, tuple):
        return metadata(result[0])
    return json.loads(next(block.text for block in result if block.type == "text"))


def call(api: str, output: Path, data: Any, *, tool: str = "normalize_data", data_dir: Path | None = None) -> Any:
    args = {"data": data}
    if tool == "render_echarts":
        args["spec"] = SPEC
    if api == "session":
        session = ToolSession(output, data_dir=data_dir)
        return session.render_chart("echarts", data, SPEC) if tool == "render_echarts" else getattr(session, tool)(data)
    if api == "structured":
        pytest.importorskip("langchain_core")
        tools = {item.name: item for item in create_tools(output, data_dir=data_dir)}
        return tools[tool].invoke(args)
    pytest.importorskip("mcp")
    server = create_server(output, data_dir=data_dir)
    return metadata(asyncio.run(server.call_tool(tool, args)))


@pytest.mark.parametrize("raw", DUPLICATES, ids=["top", "nested", "file-control"])
@pytest.mark.parametrize("api", ["core", "session", "structured", "sdk"])
def test_duplicate_keys_rejected_before_semantic_loss(api: str, raw: str, tmp_path: Path) -> None:
    for name in ("first.json", "second.json"):
        (tmp_path / name).write_text(json.dumps(ROWS), encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate JSON"):
        if api == "core":
            normalize(raw, {"kind": "table", "format": "json"})
        else:
            call(api, tmp_path / "out", raw, data_dir=tmp_path)
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("tool", ["normalize_data", "recommend_chart", "render_echarts"])
def test_sdk_rejects_raw_oversize_before_decoding_for_every_tool(tool: str, tmp_path: Path) -> None:
    small = json.dumps(ROWS, ensure_ascii=False)
    raw = " " * (1_000_001 - len(small.encode("utf-8"))) + small
    assert len(raw.encode("utf-8")) == 1_000_001
    with pytest.raises(ValueError, match="Inline data exceeds"):
        call("sdk", tmp_path / "out", raw, tool=tool)
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("api", ["session", "structured", "sdk"])
@pytest.mark.parametrize("encoded", [False, True], ids=["object", "encoded"])
@pytest.mark.parametrize("depth", [1500, 10000])
def test_deep_data_has_concise_validation_error(api: str, encoded: bool, depth: int, tmp_path: Path) -> None:
    data: Any = []
    for _ in range(depth):
        data = [data]
    if encoded:
        data = "[" * depth + "]" * depth
    declared_errors: tuple[type[Exception], ...] = (ValueError,)
    if api == "sdk":
        pytest.importorskip("mcp")
        from mcp.server.fastmcp.exceptions import ToolError

        declared_errors = (ValueError, ToolError)
    with pytest.raises(declared_errors, match="deep|nest|recursion") as rejected:
        call(api, tmp_path / "out", data)
    assert len(str(rejected.value)) < 500


@pytest.mark.parametrize("api", ["session", "structured", "sdk"])
def test_exact_raw_limit_with_unicode_is_accepted(api: str, tmp_path: Path) -> None:
    small = json.dumps(ROWS, ensure_ascii=False)
    raw = " " * (1_000_000 - len(small.encode("utf-8"))) + small
    assert len(raw.encode("utf-8")) == 1_000_000
    assert call(api, tmp_path / "out", raw)["input_count"] == 1


@pytest.mark.parametrize("method", ["ainvoke", "arun"])
def test_async_structured_deep_data_is_rejected_before_callback_bookkeeping(tmp_path: Path, method: str) -> None:
    pytest.importorskip("langchain_core")
    tool = next(item for item in create_tools(tmp_path / "out") if item.name == "normalize_data")
    data: Any = []
    for _ in range(10000):
        data = [data]
    with pytest.raises(ValueError, match="deep|nest"):
        asyncio.run(getattr(tool, method)({"data": data}))
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("api", ["session", "structured", "sdk"])
def test_padded_encoded_file_reference_obeys_raw_byte_limit(api: str, tmp_path: Path) -> None:
    (tmp_path / "first.json").write_text(json.dumps(ROWS), encoding="utf-8")
    raw = " " * 1_000_001 + '{"file":"first.json"}'
    with pytest.raises(ValueError, match="Inline data exceeds"):
        call(api, tmp_path / "out", raw, data_dir=tmp_path)


def test_valid_canonical_file_and_copied_handles_survive_eviction(tmp_path: Path) -> None:
    (tmp_path / "first.json").write_text(json.dumps(ROWS), encoding="utf-8")
    session = ToolSession(tmp_path / "out", data_dir=tmp_path)
    first = session.normalize_data('{"file":"first.json"}')
    copied = session.normalize_data(json.dumps({"dataset_id": first["dataset_id"]}))
    for index in range(31):
        session.normalize_data([{"value": index}])
    with pytest.raises(ValueError, match="expired"):
        session.recommend_chart({"dataset_id": first["dataset_id"]})
    result = session.render_chart("echarts", {"dataset_id": copied["dataset_id"]}, SPEC)
    manifest = next(Path(item) for item in result["paths"] if item.endswith("manifest.json"))
    assert json.loads(manifest.read_text(encoding="utf-8"))["charts"][0]["records"] == ROWS
    for source in ('"first.json"', '{"file":"../outside.json"}', '{"file":"https://invalid.test/x"}'):
        with pytest.raises(ValueError):
            session.normalize_data(source)


def test_real_stdio_rejects_raw_bad_requests_then_recovers(tmp_path: Path) -> None:
    pytest.importorskip("mcp")
    from mcp import ClientSession, StdioServerParameters, types
    from mcp.client.stdio import stdio_client

    (tmp_path / "first.json").write_text(json.dumps(ROWS), encoding="utf-8")
    (tmp_path / "second.json").write_text(json.dumps(ROWS), encoding="utf-8")

    async def exercise() -> None:
        source = Path(__file__).resolve().parents[1] / "src"
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "deepviz.mcp_server", "--output-dir", str(tmp_path / "out"), "--data-dir", str(tmp_path)],
            env={**os.environ, "PYTHONPATH": str(source), "PYTHONUTF8": "1"},
        )
        with (tmp_path / "stderr.txt").open("w", encoding="utf-8") as errlog:
            async with stdio_client(params, errlog=errlog) as (read, write):
                async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=45)) as client:
                    await client.initialize()
                    rejected = []
                    bad = [*DUPLICATES, " " * 1_000_001 + json.dumps(ROWS),
                           " " * 1_000_001 + '{"file":"first.json"}', "[" * 1500 + "]" * 1500]
                    for raw in bad:
                        response = await client.call_tool("normalize_data", {"data": raw})
                        rejected.append(response.isError)
                    valid = await client.call_tool("normalize_data", {"data": json.dumps(ROWS, ensure_ascii=False)})
                    assert not valid.isError
                    info = json.loads(next(block.text for block in valid.content if isinstance(block, types.TextContent)))
                    rendered = await client.call_tool("render_echarts", {"data": {"dataset_id": info["dataset_id"]}, "spec": SPEC})
                    assert not rendered.isError
                    summary = json.loads(next(block.text for block in rendered.content if isinstance(block, types.TextContent)))
                    manifest_uri = next(item["uri"] for item in summary["resources"] if item["name"] == "manifest.json")
                    resource = await client.read_resource(manifest_uri)
                    content = resource.contents[0]
                    assert isinstance(content, types.TextResourceContents)
                    assert json.loads(content.text)["charts"][0]["records"] == ROWS
                    assert all(rejected), f"Raw bad requests incorrectly accepted: {rejected}"

    asyncio.run(asyncio.wait_for(exercise(), timeout=90))
