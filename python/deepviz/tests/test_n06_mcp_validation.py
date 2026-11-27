"""Real stdio regressions for the model-facing MCP argument boundary."""
from __future__ import annotations

import asyncio
import os
import sys
from datetime import timedelta
from pathlib import Path

import pytest

pytest.importorskip("mcp")
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROWS = [{"month": "Jan", "revenue": 12}, {"month": "Feb", "revenue": 18}]
SPEC = {"kind": "bar", "x": "month", "y": "revenue"}


def test_mcp_unknown_arguments_fail_without_artifacts(tmp_path: Path):
    """MCP must not silently ignore host-only or mistyped tool arguments."""
    async def exercise():
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "deepviz.mcp_server", "--output-dir", str(tmp_path / "out")],
            env=dict(os.environ),
        )
        with (tmp_path / "stderr.log").open("w", encoding="utf-8") as errlog:
            async with stdio_client(params, errlog=errlog) as (read, write):
                async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=45)) as session:
                    await session.initialize()
                    discovery = await session.list_tools()
                    assert len(discovery.tools) == 7
                    assert all(tool.inputSchema.get("additionalProperties") is False for tool in discovery.tools)
                    cases = [
                        ("normalize_data", {"data": ROWS, "output_dir": "model-chosen"}),
                        ("recommend_chart", {"data": ROWS, "output_dir": "model-chosen"}),
                        ("render_echarts", {"data": ROWS, "spec": SPEC, "output_dir": "model-chosen"}),
                    ]
                    for name, args in cases:
                        result = await session.call_tool(name, args)
                        assert result.isError, f"{name} accepted unknown arguments: {result}"
                        assert all(block.type == "text" for block in result.content)
                    valid = await session.call_tool("normalize_data", {"data": ROWS})
                    assert not valid.isError

        assert not list((tmp_path / "out").rglob("*"))

    asyncio.run(asyncio.wait_for(exercise(), timeout=90))
