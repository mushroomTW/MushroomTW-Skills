"""Perform low-dependency checks for common README issues.

Scope is deliberately narrow: only checks whose result is a verifiable fact.
Judging whether a section is present and useful belongs to
`references/quality-checklist.md`, not to keyword matching.

Every warning is a heuristic lead, not a verdict: read the flagged line and
decide whether it is a real problem before editing the README.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import unquote, urlparse

# Only formatted markers count as unfinished work. Bare prose words such as
# "todo" or "placeholder" are legitimate content in many READMEs (task apps,
# template engines), so matching them would bury real markers in noise.
UNFINISHED_MARKERS = re.compile(
    r"\bTODO:|\bFIXME:|\bTBD\b|(?i:\bto be (?:confirmed|determined)\b)"
)

FENCED_BLOCK = re.compile(r"(?ms)^ {0,3}(`{3,}|~{3,}).*?^ {0,3}\1[ \t]*$")
INLINE_CODE = re.compile(r"`+[^`\n]+`+")
EMPTY_LINK = re.compile(r"\[[^\]]*\]\(\s*\)")
LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def strip_code(text: str) -> str:
    """Remove fenced blocks and inline code spans.

    Links and markers inside code are examples shown to the reader, not
    claims about this repository, so the checks skip them.
    """
    return INLINE_CODE.sub("", FENCED_BLOCK.sub("", text))


def link_target(raw: str) -> str:
    """Extract the destination from the inside of a Markdown link.

    Handles `<...>`-wrapped destinations, which may contain spaces, and
    plain destinations optionally followed by a title.
    """
    raw = raw.strip()
    if raw.startswith("<"):
        end = raw.find(">")
        return raw[1:end] if end != -1 else raw[1:]
    parts = raw.split()
    return parts[0] if parts else ""


def local_targets(text: str) -> list[str]:
    targets: list[str] = []
    for match in LINK.finditer(text):
        target = link_target(match.group(1))
        if not target or target.startswith("#"):
            continue
        try:
            if urlparse(target).scheme:
                continue
        except ValueError:
            continue
        base = unquote(target.split("#", 1)[0])
        if base:
            targets.append(base)
    return targets


def main() -> int:
    parser = argparse.ArgumentParser(description="Check README unfinished markers and local links")
    parser.add_argument("readme", type=Path)
    parser.add_argument("--project", type=Path, default=None)
    args = parser.parse_args()

    readme = args.readme.resolve()
    project = (args.project or readme.parent).resolve()
    prose = strip_code(readme.read_text(encoding="utf-8"))
    warnings: list[str] = []

    markers = sorted({match.group(0).strip() for match in UNFINISHED_MARKERS.finditer(prose)})
    if markers:
        warnings.append(
            "Contains unfinished markers ({}): complete them or report them as gaps".format(
                ", ".join(markers)
            )
        )

    if EMPTY_LINK.search(prose):
        warnings.append("Contains a link with an empty target")

    for target in local_targets(prose):
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
