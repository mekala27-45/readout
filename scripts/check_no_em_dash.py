"""Refuse empty inputs and scan tracked text, including all document templates."""

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", ".venv", "node_modules", ".next", "out", "__pycache__", ".cache", ".mypy_cache", ".ruff_cache", ".pytest_cache", ".hypothesis"}
SUFFIXES = {".py", ".md", ".html", ".jinja", ".j2", ".json", ".js", ".mjs", ".ts", ".tsx", ".css", ".yaml", ".yml", ".toml", ".svg", ".txt"}


def check(root: Path) -> list[str]:
    if not root.exists():
        raise ValueError("No files to check")
    files = [p for p in root.rglob("*") if p.is_file() and p.suffix in SUFFIXES and not SKIP.intersection(p.relative_to(root).parts)]
    if not files:
        raise ValueError("No text files to check")
    errors = []
    for path in sorted(files):
        content = path.read_text(encoding="utf-8-sig")
        for line, value in enumerate(content.splitlines(), 1):
            if chr(0x2014) in value:
                errors.append(f"{path.relative_to(root)}:{line}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors = check(args.root)
    if errors:
        raise SystemExit("Forbidden punctuation: " + ", ".join(errors))
    print("Punctuation gate passed, including readout templates.")


if __name__ == "__main__":
    main()
