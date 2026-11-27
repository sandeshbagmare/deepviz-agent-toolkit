"""Export the Python source of truth; --check is a read-only drift gate."""
from __future__ import annotations

import argparse
from pathlib import Path

from deepviz.models import ChartSpec


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path,
        default=Path(__file__).resolve().parents[1] / "schemas" / "chart-spec.schema.json",
    )
    parser.add_argument("--check", action="store_true", help="Fail on missing/stale schema without writing")
    args = parser.parse_args()
    import json

    content = json.dumps(ChartSpec.model_json_schema(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != content:
            print(f"Schema missing or stale: {args.output}; run python scripts/export_schema.py")
            return 1
        print(f"Schema matches Python contract: {args.output}")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(content, encoding="utf-8", newline="\n")
    print(f"Exported {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
