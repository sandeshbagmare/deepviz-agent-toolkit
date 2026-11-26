"""Public handle-copy regressions: equivalent JSON encodings retain source authority."""
from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import timedelta
from pathlib import Path

import pytest

from deepviz.tools import create_tools

ROWS = [{"category": "Alpha", "amount": 1} for _ in range(300)] + [{"category": "Beta", "amount": 5}]
EXPECTED = [{"category": "Alpha", "amount": 300.0}, {"category": "Beta", "amount": 5.0}]
FILLER = [{"category": "unused", "amount": 9}]


@pytest.mark.parametrize("source_form", ["inline", "rooted-file", "encoded-rooted-file"])
def test_public_copied_handle_chains_survive_original_eviction(tmp_path: Path, source_form: str):
    """Caching JSON text as an alias must not break the still-live copy's render."""
    pytest.importorskip("langchain_core")
    root = tmp_path / "data"
    root.mkdir()
    (root / "rows.json").write_text(json.dumps(ROWS), encoding="utf-8")
    source = ROWS if source_form == "inline" else {"file": "rows.json"}
    if source_form == "encoded-rooted-file":
        source = json.dumps(source)
    tools = {tool.name: tool for tool in create_tools(tmp_path / "out", data_dir=root)}
    normalize = tools["normalize_data"]
    original = normalize.invoke({"data": source})
    assert (original["input_count"], original["output_count"]) == (301, 200)
    reference = {"dataset_id": original["dataset_id"]}
    direct = normalize.invoke({"data": reference})
    encoded = normalize.invoke({"data": json.dumps(reference)})
    for _ in range(30):
        normalize.invoke({"data": FILLER})

    with pytest.raises(ValueError, match="expired"):
        tools["recommend_chart"].invoke({"data": reference})

    for copied in (direct, encoded):
        handle = {"dataset_id": copied["dataset_id"]}
        advice = tools["recommend_chart"].invoke({"data": handle})
        assert advice["dataset_id"] == copied["dataset_id"]
        assert advice["input_count"] == 301
        artifact = tools["render_echarts"].invoke({"data": handle, "spec": advice["spec"]})
        assert (artifact["input_count"], artifact["output_count"]) == (301, 2)
        paths = [Path(value) for value in artifact["paths"]]
        assert all(path.is_file() for path in paths)
        manifest = json.loads(next(path for path in paths if path.name == "manifest.json").read_text(encoding="utf-8"))
        assert manifest["charts"][0]["records"] == EXPECTED

    # Re-reading either source must retain all301 rows, not the200-row profile.
    for copied in (direct, encoded):
        profiled = normalize.invoke({"data": {"dataset_id": copied["dataset_id"]}})
        assert (profiled["input_count"], profiled["output_count"]) == (301, 200)


@pytest.mark.parametrize("configured", [False, True])
def test_encoded_reference_canonicalization_does_not_grant_file_authority(tmp_path: Path, configured: bool):
    """Caching must not accept an unauthorized file, URL, or raw resolved Path."""
    pytest.importorskip("langchain_core")
    root = tmp_path / "data"
    root.mkdir()
    secret = tmp_path / "secret.json"
    secret.write_text('[{"secret":"not-model-readable"}]', encoding="utf-8")
    authorized = root / "rows.json"
    authorized.write_text(json.dumps(ROWS), encoding="utf-8")
    tools = {tool.name: tool for tool in create_tools(tmp_path / "out", data_dir=root if configured else None)}
    denied = [
        {"file": "../secret.json"},
        json.dumps({"file": "../secret.json"}),
        {"file": str(secret)},
        json.dumps({"file": str(secret)}),
        json.dumps({"file": "https://example.invalid/rows.json"}),
        authorized,
        json.dumps(str(authorized)),
    ]
    if not configured:
        denied.extend([{"file": "rows.json"}, json.dumps({"file": "rows.json"})])
    for source in denied:
        with pytest.raises(ValueError):
            tools["normalize_data"].invoke({"data": source})
    assert secret.read_text(encoding="utf-8") == '[{"secret":"not-model-readable"}]'
    assert not (tmp_path / "out").exists()


def test_actual_mcp_encoded_copy_control_keeps_working_after_eviction(tmp_path: Path):
    """SDK preprocessing already canonicalizes this case; it is not an MCP bypass."""
    pytest.importorskip("mcp")
    from mcp import ClientSession, StdioServerParameters, types
    from mcp.client.stdio import stdio_client

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

                    async def call(name, arguments):
                        result = await session.call_tool(name, arguments)
                        assert not result.isError, result
                        return json.loads(next(block.text for block in result.content if isinstance(block, types.TextContent)))

                    original = await call("normalize_data", {"data": ROWS})
                    reference = {"dataset_id": original["dataset_id"]}
                    direct = await call("normalize_data", {"data": reference})
                    encoded = await call("normalize_data", {"data": json.dumps(reference)})
                    for _ in range(30):
                        await call("normalize_data", {"data": FILLER})
                    assert (await session.call_tool("recommend_chart", {"data": reference})).isError

                    for copied in (direct, encoded):
                        handle = {"dataset_id": copied["dataset_id"]}
                        advice = await call("recommend_chart", {"data": handle})
                        assert advice["input_count"] == 301
                        artifact = await call("render_echarts", {"data": handle, "spec": advice["spec"]})
                        assert "paths" not in artifact
                        assert (artifact["input_count"], artifact["output_count"]) == (301, 2)
                        uri = next(item["uri"] for item in artifact["resources"] if item["mime_type"] == "application/json")
                        response = await session.read_resource(uri)
                        manifest = json.loads(response.contents[0].text)
                        assert manifest["charts"][0]["records"] == EXPECTED

    asyncio.run(asyncio.wait_for(exercise(), timeout=90))
