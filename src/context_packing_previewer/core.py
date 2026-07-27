from __future__ import annotations

import fnmatch
import math
from pathlib import Path
from typing import Any

DEFAULT_EXCLUDES = (
    ".git/**",
    "**/.git/**",
    "node_modules/**",
    "**/node_modules/**",
    ".venv/**",
    "**/.venv/**",
    "dist/**",
    "**/dist/**",
    "*.env",
    "**/*.env",
    "*.pem",
    "**/*.pem",
    "*.key",
    "**/*.key",
)


def _matches(path: str, patterns: tuple[str, ...] | list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def estimate_tokens(text: str) -> int:
    return math.ceil(len(text) / 4)


def preview(
    root: Path,
    includes: list[str],
    excludes: list[str] | None = None,
    budget: int = 32_000,
    max_file_bytes: int = 1_000_000,
) -> dict[str, Any]:
    if not root.is_dir():
        raise ValueError("root must be a directory")
    if budget <= 0 or max_file_bytes <= 0:
        raise ValueError("budget and max-file-bytes must be positive")
    patterns = list(DEFAULT_EXCLUDES) + list(excludes or [])
    candidates: dict[str, Path] = {}
    for pattern in includes:
        for path in root.glob(pattern):
            if path.is_file() and not path.is_symlink():
                relative = path.relative_to(root).as_posix()
                candidates[relative] = path
    files: list[dict[str, Any]] = []
    omitted: list[dict[str, str]] = []
    for relative, path in sorted(candidates.items()):
        if _matches(relative, patterns):
            omitted.append({"path": relative, "reason": "excluded"})
            continue
        size = path.stat().st_size
        if size > max_file_bytes:
            omitted.append({"path": relative, "reason": "too-large"})
            continue
        raw = path.read_bytes()
        if b"\0" in raw:
            omitted.append({"path": relative, "reason": "binary"})
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            omitted.append({"path": relative, "reason": "not-utf8"})
            continue
        files.append(
            {
                "path": relative,
                "bytes": size,
                "characters": len(text),
                "estimated_tokens": estimate_tokens(text),
            }
        )
    total = sum(item["estimated_tokens"] for item in files)
    risk = (
        "over-budget"
        if total > budget
        else "near-budget"
        if total > budget * 0.8
        else "within-budget"
    )
    return {
        "version": 1,
        "root": str(root.resolve()),
        "budget": budget,
        "estimated_tokens": total,
        "risk": risk,
        "files": files,
        "omitted": omitted,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Context Packing Preview",
        "",
        f"Estimated tokens: **{report['estimated_tokens']:,} / {report['budget']:,}** ({report['risk']})",
        "",
        "| File | Bytes | Estimated tokens |",
        "|---|---:|---:|",
    ]
    lines.extend(
        f"| `{item['path']}` | {item['bytes']:,} | {item['estimated_tokens']:,} |"
        for item in report["files"]
    )
    if report["omitted"]:
        lines.extend(["", "## Omitted", ""])
        lines.extend(f"- `{item['path']}` — {item['reason']}" for item in report["omitted"])
    return "\n".join(lines).rstrip() + "\n"
