"""Isolate AntV's emitted quantitative heatmap and an explicit library-only control."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from deepviz.engines import browser_html, native_spec
from deepviz.models import ChartSpec


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    output = parser.parse_args().output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    cases = []
    for label, values in (("negative", (-7, -2)), ("positive", (2, 7)), ("signed", (-7, 2)),
                          ("constant", (1, 1)), ("negative-legend-off-control", (-7, -2))):
        rows = [{"day": "Mon", "slot": "AM", "z": values[0]},
                {"day": "Tue", "slot": "PM", "z": values[1]}]
        spec = ChartSpec(kind="heatmap", x="day", y="slot", color="z", title=f"AntV heatmap {label}")
        native, warnings, _ = native_spec("antv", rows, spec)
        if label.endswith("control"):
            native = copy.deepcopy(native)
            native["legend"] = False
        html = browser_html("antv", [native], [spec], spec, [{"records": rows, "input_count": 2,
                            "output_count": 2, "strategy": "none", "warnings": warnings}])
        (output / f"{label}.html").write_text(html, encoding="utf-8")
        cases.append({"id": label, "html": f"{label}.html", "native": native,
                      "production_equivalent": not label.endswith("control")})
    (output / "cases.json").write_text(json.dumps(cases, indent=2), encoding="utf-8")
    print(json.dumps({"cases": len(cases), "output": str(output)}))


if __name__ == "__main__":
    main()
