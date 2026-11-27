"""Run from the newly installed venv with -I; never import the source checkout."""
from __future__ import annotations

import argparse
import asyncio
import base64
import hashlib
import importlib
import importlib.metadata as metadata
import importlib.resources as resources
import importlib.util
import json
import os
import site
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

ROWS = [{"label": "A", "value": 2}, {"label": "B", "value": 5}]
SPEC = {"kind": "bar", "x": "label", "y": "value", "title": "R10 installed A=2, B=5"}
TOOLS = {"normalize_data", "recommend_chart", *("render_" + name for name in (
    "matplotlib", "plotly", "vega", "echarts", "antv"))}


def identity(path: Path) -> dict:
    return {"path": str(path), "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def module_path(name: str) -> Path:
    module = importlib.import_module(name)
    assert module.__file__ is not None
    return Path(module.__file__).resolve()


def static_image(paths: list[Path], mime_type: str) -> Path:
    assert mime_type in {"image/png", "image/svg+xml"}, mime_type
    suffix = ".png" if mime_type == "image/png" else ".svg"
    path = next((path for path in paths if path.suffix == suffix), None)
    assert path is not None, "Static image missing for " + mime_type
    if mime_type == "image/png":
        assert path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    else:
        assert ElementTree.fromstring(path.read_bytes()).tag.rsplit("}", 1)[-1] == "svg"
    return path


def inventory() -> dict:
    prefix = Path(sys.prefix).resolve()
    assert sys.prefix != sys.base_prefix
    assert site.ENABLE_USER_SITE is False
    assert not os.environ.get("PYTHONPATH")
    assert "include-system-site-packages = false" in (prefix / "pyvenv.cfg").read_text().lower()
    distributions = []
    for dist in sorted(metadata.distributions(), key=lambda item: item.metadata["Name"].lower()):
        root = Path(str(dist.locate_file(""))).resolve()
        assert root.is_relative_to(prefix), root
        text = dist.read_text("METADATA")
        assert text is not None
        distributions.append({"name": dist.metadata["Name"], "version": dist.version,
                              "metadata_root": str(root),
                              "metadata_sha256": hashlib.sha256(text.encode()).hexdigest()})
    return {"python": sys.executable, "python_version": sys.version, "prefix": sys.prefix,
            "base_prefix": sys.base_prefix, "sys_path": sys.path, "user_site": site.ENABLE_USER_SITE,
            "distributions": distributions}


async def mcp_round_trip(output: Path, executable: Path) -> dict:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from mcp.types import BlobResourceContents

    params = StdioServerParameters(command=str(executable), args=["--output-dir", str(output / "mcp-output")],
                                   env=dict(os.environ))
    methods = []
    with (output / "mcp-server.stderr.log").open("w", encoding="utf-8") as error_log:
        async with stdio_client(params, errlog=error_log) as (read, write), ClientSession(read, write) as session:
            initialized = await session.initialize()
            methods.append("initialize")
            discovered = await session.list_tools()
            assert {tool.name for tool in discovered.tools} == TOOLS
            methods.append("tools/list")
            normalized = await session.call_tool("normalize_data", {"data": ROWS, "spec": SPEC})
            assert not normalized.isError
            profile = json.loads(next(block.text for block in normalized.content if block.type == "text"))
            assert profile["input_count"] == profile["output_count"] == 2
            handle = {"dataset_id": profile["dataset_id"]}
            methods.append("tools/call normalize_data")
            advice = await session.call_tool("recommend_chart", {"data": handle, "goal": "comparison"})
            assert not advice.isError
            methods.append("tools/call recommend_chart")
            rendered = await session.call_tool("render_matplotlib", {"data": handle, "spec": SPEC})
            assert not rendered.isError
            payload = json.loads(next(block.text for block in rendered.content if block.type == "text"))
            assert payload["input_count"] == payload["output_count"] == 2
            inline_png = base64.b64decode(next(block.data for block in rendered.content if block.type == "image"))
            assert inline_png.startswith(b"\x89PNG\r\n\x1a\n")
            png_uri = next(item["uri"] for item in payload["resources"] if item["mime_type"] == "image/png")
            methods.append("tools/call render_matplotlib")
            resource = await session.read_resource(png_uri)
            assert isinstance(resource.contents[0], BlobResourceContents)
            assert base64.b64decode(resource.contents[0].blob) == inline_png
            methods.append("resources/read PNG equals inline PNG")
            denied = await session.call_tool("normalize_data", {"data": {"file": "../outside.csv"}, "spec": SPEC})
            assert denied.isError
            methods.append("tools/call unauthorized-file denied")
    methods.append("stdio context shutdown")
    return {"methods": methods, "server": initialized.serverInfo.model_dump(), "tool_count": 7,
            "input_count": 2, "output_count": 2, "png_sha256": hashlib.sha256(inline_png).hexdigest()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--artifact", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--mcp", action="store_true")
    parser.add_argument("--inventory-only", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(exist_ok=False)
    result: dict[str, Any] = {
        "environment": inventory(), "checks": [], "commands": [], "artifacts": [], "skipped": [],
    }

    def check(name, operation):
        try:
            detail = operation()
            result["checks"].append({"name": name, "status": "pass", "detail": detail})
        except Exception as error:
            result["checks"].append({"name": name, "status": "fail", "type": type(error).__name__,
                                     "error": str(error), "traceback": traceback.format_exc()})

    def require(condition, detail):
        assert condition, detail
        return detail

    def command(argv: list[str], expected=0):
        process = subprocess.run(argv, cwd=output, env=dict(os.environ), capture_output=True,
                                 text=True, timeout=90, check=False)
        result["commands"].append({"argv": argv, "exit": process.returncode,
                                   "stdout": process.stdout, "stderr": process.stderr})
        assert process.returncode == expected, process.stderr
        return process

    if not args.inventory_only:
        import deepviz

        source, prefix = args.source.resolve(), Path(sys.prefix).resolve()
        check("deepviz installed in own venv", lambda: require(module_path("deepviz").is_relative_to(prefix),
                                                               identity(module_path("deepviz"))))
        for path in sorted((source / "python/deepviz/src/deepviz").glob("*.py")):
            name = "deepviz" if path.stem == "__init__" else "deepviz." + path.stem

            def module_control(name=name, path=path):
                origin = module_path(name)
                assert origin.is_relative_to(prefix) and origin.read_bytes() == path.read_bytes()
                return identity(origin)

            check("installed module " + name, module_control)
        for name in ("system", "request"):
            check("public prompt " + name, lambda name=name: require(deepviz.read_prompt(name).encode() == (
                source / f"prompts/v1/{name}.md").read_bytes(), "exact source bytes"))
        for relative, expected in (
            ("py.typed", source / "python/deepviz/src/deepviz/py.typed"),
            ("resources/chart-spec.schema.json", source / "schemas/chart-spec.schema.json"),
            ("resources/plotly-js-LICENSE.txt", source / "python/deepviz/src/deepviz/resources/plotly-js-LICENSE.txt"),
        ):
            check("resource " + relative, lambda relative=relative, expected=expected: require(
                resources.files("deepviz").joinpath(relative).read_bytes() == expected.read_bytes(), "exact source bytes"))

        def direct_url_control():
            dist = metadata.distribution("deepviz-agent-toolkit")
            assert dist.version == "0.1.0"
            text = dist.read_text("direct_url.json")
            assert text is not None
            direct = json.loads(text)
            actual = hashlib.sha256(args.artifact.read_bytes()).hexdigest()
            assert direct["archive_info"]["hashes"]["sha256"] == actual
            return {"version": dist.version, "archive_sha256": actual, "direct_url": direct}

        check("installed provenance matches current archive", direct_url_control)
        for name in ("pydantic", "numpy", "matplotlib", "plotly", "vl_convert"):
            check("runtime origin " + name, lambda name=name: require(
                module_path(name).is_relative_to(prefix), identity(module_path(name))))

        def invalid_prompt():
            try:
                deepviz.read_prompt("../system")
            except ValueError:
                return "ValueError as expected"
            raise AssertionError("Traversal prompt accepted")

        check("prompt traversal rejected", invalid_prompt)
        bin_dir = prefix / ("Scripts" if os.name == "nt" else "bin")
        suffix = ".exe" if os.name == "nt" else ""
        for name in ("deepviz", "deepviz-mcp"):
            check("actual console help " + name, lambda name=name: command(
                [str(bin_dir / (name + suffix)), "--help"]).returncode)
        data, spec = output / "data.json", output / "spec.json"
        data.write_text(json.dumps(ROWS), encoding="utf-8")
        spec.write_text(json.dumps(SPEC), encoding="utf-8")

        def static_render(engine):
            process = command([str(bin_dir / ("deepviz" + suffix)), "render", str(data), "--spec", str(spec),
                               "--engine", engine, "--output-dir", str(output / ("render-" + engine))])
            payload = json.loads(process.stdout)
            assert payload["input_count"] == payload["output_count"] == 2
            assert payload["engine"] == engine
            files = [identity(Path(path)) for path in payload["paths"]]
            assert all(Path(item["path"]).resolve().is_relative_to(output) for item in files)
            image = static_image([Path(item["path"]) for item in files], payload["mime_type"])
            item = {"engine": engine, "metadata": payload, "files": files}
            if image.suffix == ".svg":
                import vl_convert

                preview = output / (engine + "-preview.png")
                preview.write_bytes(vl_convert.svg_to_png(image.read_text(encoding="utf-8")))
                item["svg_raster_preview"] = identity(preview)
            result["artifacts"].append(item)
            return {"input_count": 2, "output_count": 2, "files": len(files)}

        for engine in ("matplotlib", "vega"):
            check("installed CLI static " + engine, lambda engine=engine: static_render(engine))
        if args.mcp:
            check("installed real stdio MCP initialize/list/chain/resource/deny/shutdown", lambda: asyncio.run(
                asyncio.wait_for(mcp_round_trip(output, bin_dir / ("deepviz-mcp" + suffix)), timeout=90)))
        else:
            check("base install has no undeclared optional MCP/agents", lambda: require(all(
                importlib.util.find_spec(name) is None for name in ("mcp", "langchain_core", "deepagents")),
                "all optional packages absent, no inherited sites"))
            result["skipped"].append("Actual MCP transport in base-only wheel consumer; exercised in independent sdist[mcp] consumer")
    result["passed"] = sum(item["status"] == "pass" for item in result["checks"])
    result["failed"] = sum(item["status"] == "fail" for item in result["checks"])
    with (output / "result.json").open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"passed": result["passed"], "failed": result["failed"], "skipped": result["skipped"],
                      "output": str(output / "result.json")}))
    return 1 if result["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
