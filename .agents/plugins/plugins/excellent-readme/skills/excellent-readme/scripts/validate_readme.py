"""Perform low-dependency checks for common README issues."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import unquote, urlparse


REQUIRED_HINTS = {
    "purpose / introduction": [r"^#\s+", r"^#{1,6}\s+"],
    "installation or getting started": [r"install", r"getting started", r"quick start"],
    "usage or example": [r"usage", r"example", r"quick start"],
}


def local_targets(text: str) -> list[str]:
    targets: list[str] = []
    for match in re.finditer(r"!?(?:\[[^\]]*\])\(([^)]+)\)", text):
        target = match.group(1).strip().split()[0].strip("<>")
        parsed = urlparse(target)
        if not parsed.scheme and not target.startswith("#"):
            targets.append(unquote(target.split("#", 1)[0]))
    return targets


def main() -> int:
    parser = argparse.ArgumentParser(description="Check README headings, TODOs, and local links")
    parser.add_argument("readme", type=Path)
    parser.add_argument("--project", type=Path, default=None)
    args = parser.parse_args()

    readme = args.readme.resolve()
    project = (args.project or readme.parent).resolve()
    text = readme.read_text(encoding="utf-8")
    warnings: list[str] = []

    for label, patterns in REQUIRED_HINTS.items():
        if not any(re.search(pattern, text, re.IGNORECASE | re.MULTILINE) for pattern in patterns):
            warnings.append(f"Missing or unrecognized: {label}")

    if re.search(r"TODO|placeholder|to be confirmed", text, re.IGNORECASE):
        warnings.append("Contains unfinished markers: complete them or report them as gaps")

    for target in local_targets(text):
        candidate = (readme.parent / target).resolve()
        try:
            candidate.relative_to(project)
        except ValueError:
            warnings.append(f"Local link escapes the project directory: {target}")
            continue
        if not candidate.exists():
            warnings.append(f"Local link does not exist: {target}")

    if warnings:
        print("README checks completed with warnings:")
        for warning in warnings:
            print(f"- {warning}")
        return 1

    print("README static checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
