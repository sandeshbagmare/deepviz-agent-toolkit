"""Discover/call a real stdio MCP server and save resources without shared filesystem access."""
from __future__ import annotations

import argparse
import asyncio
import base64
import json
import re
import sys
import tempfile
from pathlib import Path


async def run(output_dir: str | Path) -> list[str]:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    root = Path(output_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    saved = Path(tempfile.mkdtemp(prefix="client-", dir=root))
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "deepviz.mcp_server", "--output-dir", str(root / "server")],
    )
    paths: list[str] = []
    async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
        await session.initialize()
        print("Discovered:", ", ".join(tool.name for tool in (await session.list_tools()).tools), file=sys.stderr)
        for engine in ("matplotlib", "echarts"):
            result = await session.call_tool(f"render_{engine}", {
                "data": [{"month": "Jan", "revenue": 12}, {"month": "Feb", "revenue": 18}],
                "spec": {"kind": "bar", "x": "month", "y": "revenue", "title": "Monthly revenue"},
            })
            if result.isError:
                raise RuntimeError(str(result.content))
            metadata = json.loads(next(block.text for block in result.content if block.type == "text"))
            for index, item in enumerate(metadata["resources"]):
                response = await session.read_resource(item["uri"])
                for part in response.contents:
                    content = part.text.encode("utf-8") if hasattr(part, "text") else base64.b64decode(part.blob)
                    name = re.sub(r"[^A-Za-z0-9._-]", "_", item["name"])
                    destination = saved / f"{engine}-{index}-{name}"
                    with destination.open("xb") as handle:
                        handle.write(content)
                    paths.append(str(destination))
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="artifacts/local/mcp-demo")
    args = parser.parse_args()
    print(json.dumps(asyncio.run(run(args.output_dir)), indent=2))


if __name__ == "__main__":
    main()
