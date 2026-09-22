"""Draw a source-labeled repository preview using measured evidence."""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    evidence = json.loads((ROOT / "web/public/results/bundle.json").read_text())
    final = evidence["calibration"]["peeking"][-1]
    image = Image.new("RGB", (1200, 630), "#0B0F14")
    draw = ImageDraw.Draw(image)
    font_path = Path("C:/Windows/Fonts/consola.ttf")

    def font(size: int) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(str(font_path), size) if font_path.exists() else ImageFont.load_default(size=size)

    draw.rounded_rectangle((54, 53, 68, 90), radius=5, fill="#0891B2")
    draw.text((87, 45), "readout", font=font(48), fill="#FAFAFA")
    draw.text((58, 157), "Health first.", font=font(66), fill="#FAFAFA")
    draw.text((58, 231), "Evidence before decisions.", font=font(55), fill="#94A3B8")
    for x, label, data, color in [(60, "NAIVE DAILY PEEKING", final["naive"], "#94A3B8"), (630, "SEQUENTIAL MONITORING", final["sequential"], "#67E8F9")]:
        draw.line((x, 342, x + 500, 342), fill="#334155", width=2)
        draw.text((x, 363), label, font=font(21), fill="#CBD5E1")
        draw.text((x, 404), f"{data['rate']:.1%}", font=font(52), fill=color)
        draw.text((x, 470), f"95% interval [{data['low']:.1%}, {data['high']:.1%}]", font=font(21), fill="#CBD5E1")
    draw.text((60, 567), f"SIMULATED NULL  /  seed {evidence['calibration']['seed']}  /  {final['naive']['total']} experiments", font=font(20), fill="#94A3B8")
    image.save(ROOT / "docs/social-preview.png")


if __name__ == "__main__":
    main()
