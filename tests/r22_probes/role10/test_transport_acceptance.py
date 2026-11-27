"""Missing P1 transport combinations; no SDK/dispatch/parser replacements."""
from __future__ import annotations

import asyncio
import base64
import hashlib
import importlib
import json
import os
import re
import sys
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

from deepviz.mcp_server import create_server
from deepviz.tools import create_tools

ROWS = [{"category": "North", "value": 7, "note": "東京 📊"},
        {"category": "South", "value": -3, "note": "München"}]
SPEC = {"kind": "bar", "x": "category", "y": "value", "aggregation": "none", "title": "R22 P1 recovery"}


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def frozen_source() -> Path:
    source = Path(os.environ["R22_PINNED_SOURCE"]).resolve()
    for name in ("deepviz.tools", "deepviz.mcp_server", "deepviz.normalize"):
        origin = importlib.import_module(name).__file__
        assert origin is not None
        path = Path(origin).resolve()
        assert path.is_relative_to(source / "python/deepviz/src"), f"Wrong source module: {path}"
    return source


def setup(root: Path) -> Path:
    frozen_source()
    data = root / "data"
    data.mkdir()
    (data / "rows.json").write_text(json.dumps(ROWS, ensure_ascii=False), encoding="utf-8")
    (data / "poison.json").write_text('[{"category":"wrong-authority","value":999}]', encoding="utf-8")
    (root / "outside.json").write_text('[{"category":"outside-secret","value":999}]', encoding="utf-8")
    return data


def bad_cases() -> list[tuple[str, str, str, str]]:
    multibyte = json.dumps([{"category": "oversize", "value": 1, "note": "é" * 499_900}], ensure_ascii=False)
    multibyte = " " * (1_000_001 - len(multibyte.encode("utf-8"))) + multibyte
    assert len(multibyte) < 1_000_000 and len(multibyte.encode("utf-8")) == 1_000_001
    return [
        ("escaped-file-key", "normalize_data", r'{"f\u0069le":"rows.json","file":"poison.json"}', "Duplicate JSON"),
        ("multibyte-raw-1000001", "recommend_chart", multibyte, "Inline data exceeds"),
        ("render-encoded-depth10000", "render_matplotlib", "[" * 10_000 + "]" * 10_000, "deep|nest|recursion"),
        ("encoded-traversal", "normalize_data", '{"file":"../outside.json"}', "escapes"),
        ("encoded-literal-path", "render_matplotlib", '"rows.json"', "array or object"),
    ]


def args(name: str, data: Any) -> dict[str, Any]:
    return {"data": data, **({"spec": SPEC} if name.startswith("render_") else {})}


def metadata(result: Any) -> dict[str, Any]:
    if isinstance(result, dict):
        return result
    if isinstance(result, tuple):
        result = result[0]
    return json.loads(next(block.text for block in result if block.type == "text"))


def observe_error(name: str, operation: str, raw: str, message: str, expected: str) -> dict[str, Any]:
    assert re.search(expected, message, re.IGNORECASE), (name, message)
    assert len(message.encode("utf-8")) < 1024 and "Traceback" not in message
    assert "outside-secret" not in message and "wrong-authority" not in message
    return {"case": name, "tool": operation, "input_chars": len(raw), "raw_utf8_bytes": len(raw.encode("utf-8")),
            "error": message, "error_utf8_bytes": len(message.encode("utf-8")), "rejected": True}


@pytest.mark.parametrize("method", ["run", "arun"])
def test_public_structured_run_arun_raw_admission_and_recovery(tmp_path: Path, method: str) -> None:
    pytest.importorskip("langchain_core")
    from langchain_core.callbacks import BaseCallbackHandler

    class Starts(BaseCallbackHandler):
        def __init__(self) -> None:
            self.names: list[str] = []

        def on_tool_start(self, serialized: dict[str, Any], input_str: str, **kwargs: Any) -> None:
            self.names.append(serialized["name"])

    starts = Starts()
    output = tmp_path / "output"
    tools = {tool.name: tool for tool in create_tools(output, data_dir=setup(tmp_path))}

    async def call(name: str, data: Any) -> Any:
        tool = tools[name]
        if method == "run":
            return tool.run(args(name, data), callbacks=[starts])
        return await tool.arun(args(name, data), callbacks=[starts])

    async def exercise() -> None:
        observed = []
        for index, (case, name, raw, expected) in enumerate(bad_cases()):
            before = len(starts.names)
            with pytest.raises(ValueError) as rejected:
                await call(name, raw)
            error = observe_error(case, name, raw, str(rejected.value), expected)
            assert not output.exists()
            if index < 3:
                assert len(starts.names) == before, "Invalid raw input reached actual LangChain callback bookkeeping"
                error["before_callback_bookkeeping"] = True
            recovered = await call("normalize_data", json.dumps(ROWS, ensure_ascii=False))
            assert recovered["input_count"] == recovered["output_count"] == 2
            error["ordinary_unicode_recovery_count"] = 2
            observed.append(error)
        info = await call("normalize_data", '{"file":"rows.json"}')
        copied = await call("normalize_data", json.dumps({"dataset_id": info["dataset_id"]}))
        advice = await call("recommend_chart", {"dataset_id": copied["dataset_id"]})
        assert advice["input_count"] == 2 and not output.exists()
        (tmp_path / "observed.json").write_text(json.dumps({"method": method, "observations": observed,
            "actual_callback_starts": starts.names, "file_and_copied_handle_recovery": True}, indent=2), encoding="utf-8")

    asyncio.run(exercise())


def test_actual_fastmcp_sdk_missing_combinations_recover_without_output(tmp_path: Path) -> None:
    pytest.importorskip("mcp")
    from mcp.server.fastmcp.exceptions import ToolError

    output = tmp_path / "output"
    server = create_server(output, data_dir=setup(tmp_path))

    async def exercise() -> None:
        observed = []
        for case, name, raw, expected in bad_cases():
            with pytest.raises((ValueError, ToolError)) as rejected:
                await server.call_tool(name, args(name, raw))
            error = observe_error(case, name, raw, str(rejected.value), expected)
            assert not output.exists() and not await server.list_resources()
            info = metadata(await server.call_tool("normalize_data", {"data": json.dumps(ROWS, ensure_ascii=False)}))
            assert info["input_count"] == info["output_count"] == 2
            error["ordinary_unicode_recovery_count"] = 2
            observed.append(error)
        info = metadata(await server.call_tool("normalize_data", {"data": '{"file":"rows.json"}'}))
        copied = metadata(await server.call_tool("normalize_data", {"data": json.dumps({"dataset_id": info["dataset_id"]})}))
        advice = metadata(await server.call_tool("recommend_chart", {"data": {"dataset_id": copied["dataset_id"]}}))
        assert advice["input_count"] == 2 and not output.exists()
        (tmp_path / "observed.json").write_text(json.dumps({"api": "real FastMCP.call_tool", "observations": observed,
            "file_and_copied_handle_recovery": True}, indent=2), encoding="utf-8")

    asyncio.run(exercise())


def test_real_stdio_missing_admissions_then_matplotlib_resources_are_readable(tmp_path: Path) -> None:
    pytest.importorskip("mcp")
    from mcp import ClientSession, StdioServerParameters, types
    from mcp.client.stdio import stdio_client

    data = setup(tmp_path)
    output = tmp_path / "output"
    params = StdioServerParameters(command=sys.executable,
        args=["-m", "deepviz.mcp_server", "--output-dir", str(output), "--data-dir", str(data)],
        cwd=str(tmp_path), env={"PYTHONPATH": str(frozen_source() / "python/deepviz/src"),
            "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1", "MPLBACKEND": "Agg"})

    async def exercise() -> None:
        with (tmp_path / "server.stderr").open("w", encoding="utf-8") as stderr:
            async with stdio_client(params, errlog=stderr) as (read, write):
                async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=60)) as client:
                    assert (await client.initialize()).serverInfo.name == "DeepViz"
                    assert len((await client.list_tools()).tools) == 7
                    observed = []
                    for case, name, raw, expected in bad_cases():
                        rejected = await client.call_tool(name, args(name, raw))
                        assert rejected.isError and all(isinstance(block, types.TextContent) for block in rejected.content)
                        message = "\n".join(block.text for block in rejected.content if isinstance(block, types.TextContent))
                        error = observe_error(case, name, raw, message, expected)
                        assert not output.exists() and not (await client.list_resources()).resources
                        recovered = await client.call_tool("normalize_data", {"data": json.dumps(ROWS, ensure_ascii=False)})
                        assert not recovered.isError
                        info = metadata(recovered.content)
                        assert info["input_count"] == info["output_count"] == 2
                        error["ordinary_unicode_recovery_count"] = 2
                        observed.append(error)
                    file_info = await client.call_tool("normalize_data", {"data": '{"file":"rows.json"}'})
                    assert not file_info.isError
                    copied = await client.call_tool("normalize_data", {"data": json.dumps({
                        "dataset_id": metadata(file_info.content)["dataset_id"]})})
                    assert not copied.isError
                    handle = {"dataset_id": metadata(copied.content)["dataset_id"]}
                    advice = await client.call_tool("recommend_chart", {"data": handle})
                    assert not advice.isError and metadata(advice.content)["input_count"] == 2
                    result = await client.call_tool("render_matplotlib", args("render_matplotlib", handle))
                    assert not result.isError
                    info = metadata(result.content)
                    assert info["input_count"] == info["output_count"] == 2
                    text = next(block.text for block in result.content if isinstance(block, types.TextContent))
                    assert len(text.encode("utf-8")) < 2048 and "records" not in info and "html" not in info
                    resources = []
                    for resource in info["resources"]:
                        retrieved = (await client.read_resource(resource["uri"])).contents[0]
                        if isinstance(retrieved, types.BlobResourceContents):
                            content = base64.b64decode(retrieved.blob)
                        else:
                            content = retrieved.text.encode("utf-8")
                        if resource["mime_type"] == "image/png":
                            assert content.startswith(b"\x89PNG\r\n\x1a\n")
                            inline = next(block for block in result.content if isinstance(block, types.ImageContent))
                            assert base64.b64decode(inline.data) == content
                            (tmp_path / "recovered.png").write_bytes(content)
                        if resource["name"] == "manifest.json":
                            manifest = json.loads(content)
                            assert manifest["charts"][0]["records"] == ROWS
                            assert manifest["charts"][0]["input_count"] == 2
                        resources.append({**resource, "bytes": len(content), "sha256": sha256(content)})
                    assert len(resources) >= 3 and any(resource["mime_type"] == "image/png" for resource in resources)
                    (tmp_path / "observed.json").write_text(json.dumps({"api": "real stdio", "observations": observed,
                        "profile_and_render_input_count": 2, "render_output_count": 2,
                        "text_metadata_utf8_bytes": len(text.encode("utf-8")), "file_and_copied_handle_recovery": True,
                        "inline_png_matches_resource": True, "resources": resources}, indent=2), encoding="utf-8")

    asyncio.run(asyncio.wait_for(exercise(), timeout=150))
