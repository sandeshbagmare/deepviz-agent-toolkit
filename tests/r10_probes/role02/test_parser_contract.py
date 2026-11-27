"""Strict RED regressions for parsing before data crosses the tool/MCP boundary."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import pytest

from deepviz import normalize
from deepviz.mcp_server import create_server
from deepviz.tools import MAX_INLINE_BYTES, ToolSession, create_tools

ADAPTERS = ("direct", "structured-tool", "mcp-sdk")
ROWS = [{"category": "Alpha", "value": 3}]
SPEC = {"kind": "table", "aggregation": "none"}


def invoke(adapter: str, source: Any, output: Path, data_dir: Path) -> dict[str, Any]:
    if adapter == "direct":
        return ToolSession(output, data_dir=data_dir).normalize_data(source, SPEC)
    if adapter == "structured-tool":
        pytest.importorskip("langchain_core")
        tool = next(item for item in create_tools(output, data_dir=data_dir) if item.name == "normalize_data")
        return tool.invoke({"data": source, "spec": SPEC})
    pytest.importorskip("mcp")

    async def exercise() -> dict[str, Any]:
        server = create_server(output, data_dir=data_dir)
        result = await server.call_tool("normalize_data", {"data": source, "spec": SPEC})
        blocks = result[0] if isinstance(result, tuple) else result
        return json.loads(next(item.text for item in blocks if item.type == "text"))

    return asyncio.run(asyncio.wait_for(exercise(), timeout=30))


def errors(adapter: str) -> tuple[type[Exception], ...]:
    if adapter == "mcp-sdk":
        pytest.importorskip("mcp")
        from mcp.server.fastmcp.exceptions import ToolError

        return (ValueError, ToolError)
    return (ValueError,)


@pytest.mark.parametrize("adapter", ADAPTERS)
def test_small_inline_and_explicit_file_positive_controls(tmp_path: Path, adapter: str) -> None:
    root = tmp_path / "data"
    root.mkdir()
    (root / "rows.json").write_text(json.dumps(ROWS), encoding="utf-8")
    for source in (ROWS, json.dumps(ROWS), {"file": "rows.json"}):
        result = invoke(adapter, source, tmp_path / "out", root)
        assert result["input_count"] == result["output_count"] == 1
        assert result["warnings"] == []
        assert isinstance(result["dataset_id"], str)
    assert not (tmp_path / "out").exists()


def test_core_normalizer_duplicate_rejection_control() -> None:
    raw = '[{"name":"original","name":"replacement","value":1}]'
    with pytest.raises(ValueError, match="Duplicate JSON object key"):
        normalize(raw, SPEC)


@pytest.mark.parametrize("adapter", ADAPTERS)
@pytest.mark.parametrize("target", ["data-field", "file-control-key"])
def test_tool_decoders_reject_duplicate_keys_before_semantic_loss(
    tmp_path: Path, adapter: str, target: str,
) -> None:
    root = tmp_path / "data"
    root.mkdir()
    (root / "rows.json").write_text(json.dumps(ROWS), encoding="utf-8")
    raw = (
        '[{"name":"original","name":"replacement","value":1}]'
        if target == "data-field" else '{"file":"../not-authorized.json","file":"rows.json"}'
    )
    with pytest.raises(errors(adapter), match="Duplicate JSON object key"):
        invoke(adapter, raw, tmp_path / "out", root)


@pytest.mark.parametrize("adapter", ADAPTERS)
@pytest.mark.parametrize("target", ["row-data", "file-reference"])
def test_inline_raw_byte_limit_precedes_sdk_json_preprocessing(
    tmp_path: Path, adapter: str, target: str,
) -> None:
    root = tmp_path / "data"
    root.mkdir()
    (root / "rows.json").write_text(json.dumps(ROWS), encoding="utf-8")
    source = ROWS if target == "row-data" else {"file": "rows.json"}
    raw = " " * (MAX_INLINE_BYTES + 1) + json.dumps(source)
    assert len(raw.encode("utf-8")) > MAX_INLINE_BYTES
    with pytest.raises(errors(adapter), match="Inline data exceeds"):
        invoke(adapter, raw, tmp_path / "out", root)

@pytest.mark.parametrize("target", ["row-data", "file-reference"])
def test_real_stdio_enforces_the_raw_inline_byte_limit(tmp_path: Path, target: str) -> None:
    """Confirm the new byte-policy case crosses the real transport, not only SDK calls."""
    import sys
    from datetime import timedelta

    pytest.importorskip("mcp")
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    root = tmp_path / "data"
    root.mkdir()
    (root / "rows.json").write_text(json.dumps(ROWS), encoding="utf-8")
    payload = ROWS if target == "row-data" else {"file": "rows.json"}
    raw = " " * (MAX_INLINE_BYTES + 1) + json.dumps(payload)
    source = Path(__file__).resolve().parents[3] / "python" / "deepviz" / "src"

    async def exercise() -> None:
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "deepviz.mcp_server", "--output-dir", str(tmp_path / "out"), "--data-dir", str(root)],
            cwd=str(tmp_path),
            env={"PYTHONPATH": str(source), "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1", "MPLBACKEND": "Agg"},
        )
        with (tmp_path / "server.stderr").open("w", encoding="utf-8") as errlog:
            async with stdio_client(params, errlog=errlog) as (read, write):
                async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=30)) as client:
                    await client.initialize()
                    valid = await client.call_tool("normalize_data", {"data": payload, "spec": SPEC})
                    assert not valid.isError
                    denied = await client.call_tool("normalize_data", {"data": raw, "spec": SPEC})
                    assert denied.isError, "MCP accepted raw JSON text beyond its 1,000,000-byte inline limit"
                    assert "Inline data exceeds" in " ".join(block.text for block in denied.content if block.type == "text")

    asyncio.run(asyncio.wait_for(exercise(), timeout=45))
