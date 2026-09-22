"""Refuse empty inputs and scan tracked text, including all document templates."""

import argparse
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {
    ".git",
    ".venv",
    "node_modules",
    ".next",
    "out",
    "__pycache__",
    ".cache",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    ".hypothesis",
}
SUFFIXES = {
    ".py",
    ".md",
    ".html",
    ".jinja",
    ".j2",
    ".json",
    ".js",
    ".mjs",
    ".ts",
    ".tsx",
    ".css",
    ".yaml",
    ".yml",
    ".toml",
    ".svg",
    ".txt",
}


def check(root: Path) -> list[str]:
    if not root.exists():
        raise ValueError("No files to check")
    files = []
    for directory, subdirectories, names in os.walk(root):
        subdirectories[:] = [name for name in subdirectories if name not in SKIP]
        files.extend(Path(directory) / name for name in names if Path(name).suffix in SUFFIXES)
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
