"""Render, profile, or recommend charts from local files; stdout is JSON."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .models import ChartSpec
from .tools import ENGINES, ToolSession


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("render", "normalize", "recommend"):
        command = commands.add_parser(name)
        command.add_argument("input", type=Path, help="Local JSON, JSONL, CSV/TSV, or optional columnar file")
        command.add_argument("--output-dir", default="deepviz-output")
        if name != "recommend":
            command.add_argument("--spec", type=Path, required=name == "render", help="ChartSpec v1 JSON file")
        if name == "render":
            command.add_argument("--engine", choices=ENGINES, default="matplotlib")
        if name == "recommend":
            command.add_argument("--goal", choices=["comparison", "trend", "relationship", "distribution", "composition"],
                                 default="comparison")
    server = commands.add_parser("mcp", help="Start the local stdio MCP server")
    server.add_argument("--output-dir", default="deepviz-output")
    server.add_argument("--data-dir")
    args = parser.parse_args(argv)
    try:
        if args.command == "mcp":
            from .mcp_server import create_server

            create_server(args.output_dir, data_dir=args.data_dir).run(transport="stdio")
            return 0
        source = args.input.resolve(strict=True)
        session = ToolSession(args.output_dir, data_dir=source.parent)
        data = {"file": source.name}
        spec: ChartSpec | None = None
        if getattr(args, "spec", None):
            if args.spec.stat().st_size > 128 * 1024:
                raise ValueError("Spec file exceeds 128 KiB")
            spec = ChartSpec.model_validate_json(args.spec.read_text(encoding="utf-8"))
        result: dict[str, Any]
        if args.command == "render":
            assert spec is not None
            result = session.render_chart(args.engine, data, spec)
        elif args.command == "normalize":
            result = session.normalize_data(data, spec)
        else:
            result = session.recommend_chart(data, args.goal)
        print(json.dumps(result, allow_nan=False))
    except (ValueError, OSError, ImportError) as error:
        parser.exit(2, f"deepviz: error: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
