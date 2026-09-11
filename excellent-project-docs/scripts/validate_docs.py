"""Perform low-dependency checks for common project-documentation issues.

Accepts one or more Markdown documents (README.md, CONTRIBUTING.md,
SECURITY.md, ARCHITECTURE.md, ...) and runs the same checks on each.

Scope is deliberately narrow: only checks whose result is a verifiable fact.
Judging whether a section or a companion document is present and useful
belongs to `references/quality-checklist.md`, not to keyword matching.

Every warning is a heuristic lead, not a verdict: read the flagged line and
decide whether it is a real problem before editing the document.
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

# A prose reference to a license file (uppercase filename convention only, so
# ordinary words like "license" stay out of scope). Lines that negate or
# discuss the absence ("no LICENSE file", 「未包含 LICENSE」) are legitimate
# disclosures and must not be flagged.
LICENSE_FILE_WORD = re.compile(r"\b(?:LICENSE|LICENCE|COPYING)\b")

# A License section that names a license but has no file to back it. Scoped to
# the document's own License heading so a dependency's license mentioned
# elsewhere in the prose stays out of range.
LICENSE_HEADING = re.compile(r"(?i)\blicen[sc]e\b")
HEADING_LINE = re.compile(r"^ {0,3}#{1,6}\s")
SPDX_ID = re.compile(
    r"(?i)\b(?:MIT|ISC|Unlicense|Zlib|BSD(?:[- ](?:2|3)[- ]Clause)?"
    r"|Apache(?:[- ]?2(?:\.0)?)?|(?:A|L)?GPL[- ]?v?[23](?:\.0)?"
    r"|MPL[- ]?2(?:\.0)?|CC0(?:[- ]1\.0)?|CC[- ]BY[- \w]*)\b"
)

# A line that both names a license and admits the file is missing is the most
# dangerous case, not an exempt one: it still asserts the project's license.
# So an assertion outranks the absence-talk exemption.
LICENSE_ASSERTION = re.compile(
    r"(?i)\b(?:released|licen[sc]ed|distributed|published|provided|shipped)\b[^.]{0,40}\bunder\b"
)
LICENSE_ABSENCE_TALK = re.compile(
    r"(?i)\bno\b|\bnot\b|missing|without|lacks|to be added|\badd(?:ed|ing)?\b"
    r"|invent|fabricat|未|沒有|没有|尚未|缺|補上|无|無|不|虛構|虚构"
)


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


def license_section_lines(text: str) -> list[str]:
    """Return the body lines under the document's own License heading."""
    body: list[str] = []
    inside = False
    for line in text.splitlines():
        if HEADING_LINE.match(line):
            inside = bool(LICENSE_HEADING.search(line))
            continue
        if inside:
            body.append(line)
    return body


def check_document(document: Path, project: Path) -> list[str]:
    """Run every static check on one document and return its warnings."""
    prose = strip_code(document.read_text(encoding="utf-8"))
    warnings: list[str] = []

    markers = sorted({match.group(0).strip() for match in UNFINISHED_MARKERS.finditer(prose)})
    if markers:
        warnings.append(
            "Contains unfinished markers ({}): resolve them -- ask the user or report the gap"
            " in the delivery summary; a document ships no placeholders".format(", ".join(markers))
        )

    if EMPTY_LINK.search(prose):
        warnings.append("Contains a link with an empty target")

    has_license_file = (
        any(project.glob("LICENSE*"))
        or any(project.glob("LICENCE*"))
        or any(project.glob("COPYING*"))
    )
    if not has_license_file:
        for line in prose.splitlines():
            if (
                LICENSE_FILE_WORD.search(line)
                and not LICENSE_ABSENCE_TALK.search(line)
                and "TODO" not in line
            ):
                warnings.append(
                    f"References a license file that does not exist: {line.strip()[:80]}"
                    " -- disclose the gap instead of pointing readers at a missing file"
                )

        for line in license_section_lines(prose):
            if not SPDX_ID.search(line):
                continue
            if LICENSE_ABSENCE_TALK.search(line) and not LICENSE_ASSERTION.search(line):
                continue
            warnings.append(
                "License section names a license with no LICENSE file to back"
                f" it: {line.strip()[:80]} -- confirm it with the user or state"
                " the absence as a fact; an inherited claim is not evidence"
            )
            break

    for target in local_targets(prose):
        candidate = (document.parent / target).resolve()
        try:
            candidate.relative_to(project)
        except ValueError:
            warnings.append(f"Local link escapes the project directory: {target}")
            continue
        if not candidate.exists():
            warnings.append(f"Local link does not exist: {target}")

    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check project documents for unfinished markers and local links"
    )
    parser.add_argument("documents", type=Path, nargs="+", metavar="document")
    parser.add_argument("--project", type=Path, default=None)
    args = parser.parse_args()

    documents = [document.resolve() for document in args.documents]
    project = (args.project or documents[0].parent).resolve()

    failed = False
    for document in documents:
        warnings = check_document(document, project)
        try:
            label = document.relative_to(project).as_posix()
        except ValueError:
            label = str(document)
        if warnings:
            failed = True
            print(f"{label}: checks completed with warnings:")
            for warning in warnings:
                print(f"- {warning}")
        else:
            print(f"{label}: static checks passed.")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
