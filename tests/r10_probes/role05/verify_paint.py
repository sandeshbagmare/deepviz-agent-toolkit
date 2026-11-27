"""Relate actual raster controls to the inspector's deliberately structural claim."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]


def verify(directory: Path) -> dict[str, object]:
    source = ROOT / "scripts/performance_suite.py"
    spec = importlib.util.spec_from_file_location("r10_role05_inspector", source)
    assert spec is not None and spec.loader is not None
    inspector = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(inspector)
    report = json.loads((directory / "browser.json").read_text(encoding="utf-8"))
    report["source_commit"] = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True,
    ).stdout.strip()
    report["inspector_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
    report["method"] = "64x64 Chromium RGB captures; nonwhite pixels counted; metadata is structural only"
    contact = Image.new("RGB", (850, 280), "#eeeeee")
    draw = ImageDraw.Draw(contact)
    draw.text((8, 6), "Structural acceptance is NOT geometry validation or paint approval", fill="black")
    for index, row in enumerate(report["cases"]):
        svg = directory / f'{row["name"]}.svg'
        png = directory / f'{row["name"]}.png'
        metadata = inspector.inspect_artifact(svg)
        assert metadata["inspection"] == "svg_xml_structure_only_not_visual_review"
        with Image.open(png) as image:
            rgb = image.convert("RGB")
            assert rgb.size == (64, 64)
            nonwhite = sum(rgb.getpixel((x, y)) != (255, 255, 255) for x in range(64) for y in range(64))
            x, y = (index % 5) * 170 + 8, (index // 5) * 125 + 48
            contact.paste(rgb, (x, y))
        draw.text((x, y - 18), row["name"], fill="black")
        draw.text((x, y + 67), f'{nonwhite} painted pixels', fill="black")
        assert not row["requests"], "Fixed local fixtures unexpectedly requested external resources"
        if row["expected_visible"]:
            assert nonwhite > 0 and not row["console_errors"], "Positive primitive failed to paint cleanly"
        else:
            assert nonwhite == 0 and row["bbox"]["width"] == row["bbox"]["height"] == 0
        row.update(
            nonwhite_pixels=nonwhite, inspection=metadata["inspection"],
            svg_sha256=hashlib.sha256(svg.read_bytes()).hexdigest(),
            png_sha256=hashlib.sha256(png.read_bytes()).hexdigest(),
        )
        del row["requests"]
    report["limitation"] = "Four negative SVGs remain invalid/nonpainting; their structural acceptance is not a pass."
    contact.save(directory / "contact.png")
    (directory / "verified.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(verify(Path(sys.argv[1])), indent=2))
