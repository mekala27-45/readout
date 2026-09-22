"""Compose the actual recorded browser frames into the requested short demonstration."""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    paths = sorted((ROOT / "docs/demo-frames").glob("frame-*.png"))
    if len(paths) < 4:
        raise ValueError("Record health, primary, decision and calibration browser frames first")
    frames = []
    for path in paths:
        with Image.open(path) as image:
            frame = image.convert("RGB")
            frame.thumbnail((1200, 800), Image.Resampling.LANCZOS)
            canvas = Image.new("RGB", (1200, 800), "#0B0F14")
            canvas.paste(frame, ((1200 - frame.width) // 2, (800 - frame.height) // 2))
            frames.append(canvas.quantize(colors=128))
    frames[0].save(
        ROOT / "docs/demo.gif",
        save_all=True,
        append_images=frames[1:],
        duration=2250,
        loop=0,
        optimize=False,
    )
    print(f"Saved {len(frames)} captured browser frames to docs/demo.gif")


if __name__ == "__main__":
    main()
