"""Perform low-dependency checks for common README issues.

Scope is deliberately narrow: only checks whose result is a verifiable fact.
Judging whether a section is present and useful belongs to
`references/quality-checklist.md`, not to keyword matching.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import unquote, urlparse


def local_targets(text: str) -> list[str]:
    targets: list[str] = []
    for match in re.finditer(r"!?(?:\[[^\]]*\])\(([^)]+)\)", text):
        target = match.group(1).strip().split()[0].strip("<>")
        parsed = urlparse(target)
        if not parsed.scheme and not target.startswith("#"):
            targets.append(unquote(target.split("#", 1)[0]))
    return targets


def main() -> int:
    parser = argparse.ArgumentParser(description="Check README unfinished markers and local links")
    parser.add_argument("readme", type=Path)
    parser.add_argument("--project", type=Path, default=None)
    args = parser.parse_args()

    readme = args.readme.resolve()
    project = (args.project or readme.parent).resolve()
    text = readme.read_text(encoding="utf-8")
    warnings: list[str] = []

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
