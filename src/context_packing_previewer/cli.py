from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import preview, render_markdown


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Preview a local AI context pack without uploading it."
    )
    parser.add_argument("root", type=Path)
    parser.add_argument("--include", action="append", default=[])
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument("--budget", type=int, default=32_000)
    parser.add_argument("--max-file-bytes", type=int, default=1_000_000)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        report = preview(
            args.root, args.include or ["**/*"], args.exclude, args.budget, args.max_file_bytes
        )
        rendered = (
            json.dumps(report, indent=2) + "\n"
            if args.format == "json"
            else render_markdown(report)
        )
        if args.output:
            if args.output.exists():
                raise ValueError(f"output already exists: {args.output}")
            args.output.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0
