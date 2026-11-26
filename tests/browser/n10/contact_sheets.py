"""Make labelled QA contact sheets from genuine engine/screenshot artifacts."""
import json
from io import BytesIO
from pathlib import Path

import vl_convert
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "artifacts/local/N10"
SHEETS = OUT / "contact-sheets"
SHEETS.mkdir(exist_ok=True)
cases = json.loads(Path(__file__).with_name("cases.json").read_text())
manifests = {}
for language in ["python", "typescript"]:
    file = OUT / (language + "-manifest.json")
    if file.exists():
        manifests[language] = json.loads(file.read_text(encoding="utf-8"))
font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 18)
small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 14)
evidence = []
for case in cases:
    tiles = []
    for language, engines in [("python", ["matplotlib", "plotly", "vega", "echarts", "antv"]), ("typescript", ["svg", "plotly", "vega", "echarts", "antv"])]:
        for engine in engines:
            prefix = "py" if language == "python" else "ts"
            id_ = f"{prefix}-{engine}-{case['id']}"
            tile = Image.new("RGB", (400, 320), "#e5e7eb")
            draw = ImageDraw.Draw(tile)
            draw.text((8, 4), id_, font=font, fill="black")
            candidates = ([OUT / "browser-python-default" / (id_ + "-region-0.png")] if language == "python" else [OUT / "browser-ts-default" / (id_ + "-region-0.png"), OUT / "browser-ts-local" / (id_ + "-region-0.png")])
            if case["id"] == "dashboard":
                candidates = [p.with_name(id_ + ".png") for p in candidates]
            file = next((p for p in candidates if p.exists()), None)
            mode = "browser screenshot"
            image = None
            if file:
                image = Image.open(file).convert("RGB")
            elif language == "python" and engine in {"matplotlib", "vega"}:
                item = next((c for c in manifests.get(language, {}).get("cases", []) if c["id"] == id_), None)
                if item:
                    if engine == "matplotlib":
                        file = next(Path(p) for p in item["artifact"]["paths"] if p.endswith(".png"))
                        image = Image.open(file).convert("RGB")
                    else:
                        file = next(Path(p) for p in item["artifact"]["paths"] if p.endswith(".svg"))
                        image = Image.open(BytesIO(vl_convert.svg_to_png(file.read_text(encoding="utf-8")))).convert("RGB")
                    mode = "native static engine artifact"
            if image:
                image.thumbnail((396, 270))
                tile.paste(image, ((400 - image.width) // 2, 46))
                draw.text((8, 27), mode, font=small, fill="#374151")
                evidence.append({"id": id_, "file": str(file), "mode": mode})
            else:
                draw.text((12, 100), "No captured renderer region", font=small, fill="#991b1b")
            tiles.append(tile)
    sheet = Image.new("RGB", (2000, 640), "white")
    for i, tile in enumerate(tiles):
        sheet.paste(tile, ((i % 5) * 400, (i // 5) * 320))
    sheet.save(SHEETS / (case["id"] + ".png"))
(SHEETS / "sources.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
print(f"Wrote {len(cases)} labelled contact sheets from {len(evidence)} actual captured artifacts.")
