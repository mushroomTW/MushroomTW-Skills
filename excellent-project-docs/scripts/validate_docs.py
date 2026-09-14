"""Perform low-dependency checks for common project-documentation issues.

Accepts one or more Markdown documents (README.md, CONTRIBUTING.md,
SECURITY.md, ARCHITECTURE.md, ...) and runs the same checks on each. Local
SVG images a document references are opened and checked too, and Mermaid
blocks are checked for the mistakes that make GitHub render an error box.

Scope is deliberately narrow: only checks whose result is a verifiable fact.
Judging whether a section or a companion document is present and useful
belongs to `references/quality-checklist.md`, not to keyword matching.

Every warning is a heuristic lead, not a verdict: read the flagged line and
decide whether it is a real problem before editing the document.
"""

from __future__ import annotations

import argparse
import json
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
LICENSE_HEADING = re.compile(r"(?i)\blicen[sc]e\b|授權|授权|許可|许可")
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

# The license lives in the LICENSE file; a badge or a README section repeats
# it in a place that drifts.
LICENSE_BADGE = re.compile(r"(?i)shields\.io/[^\s)\"']*licen[sc]e|/badge/licen[sc]e")

# GitHub renders block-level HTML as raw HTML and only parses the Markdown
# inside it when a blank line separates the two. A `<div>` opening (or the end
# of a `<summary>`) followed directly by a Markdown line, or a Markdown line
# followed directly by `</div>` / `</details>`, shows the Markdown source.
HTML_OPEN_NEEDS_BLANK = re.compile(r"^\s*<div\b[^>]*>\s*$|</summary>\s*$")
HTML_CLOSE_NEEDS_BLANK = re.compile(r"^\s*</(?:div|details)>\s*$")

MARKDOWN_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
HTML_IMG = re.compile(r"(?is)<img\b[^>]*>")
HTML_SRC = re.compile(r"""(?is)\b(?:src|srcset)\s*=\s*["']([^"']+)["']""")
HTML_ALT = re.compile(r"""(?is)\balt\s*=\s*["'][^"']*\S[^"']*["']""")

# Facts about an SVG that decide whether it renders on GitHub at all:
# `viewBox` lets it scale with the page; an external URL is blocked by the
# image proxy and fails silently; `<script>` is stripped. A font-size under
# one hundredth of the canvas width is under 12 units on a 1200-unit banner,
# which is under 9 px at README width.
SVG_ROOT = re.compile(r"(?is)<svg\b[^>]*>")
SVG_VIEWBOX = re.compile(
    r"""(?i)\bviewBox\s*=\s*["']\s*[-\d.]+[\s,]+[-\d.]+[\s,]+([\d.]+)[\s,]+[\d.]+\s*["']"""
)
SVG_EXTERNAL = re.compile(
    r"""(?i)(?:href|src|srcset)\s*=\s*["']\s*(?:https?:)?//|@import\b|url\(\s*["']?\s*(?:https?:)?//"""
)
SVG_SCRIPT = re.compile(r"(?i)<script\b")
SVG_FONT_SIZE = re.compile(r"""(?i)font-size\s*[=:]\s*["']?\s*(\d+(?:\.\d+)?)(?:px)?\b""")

MERMAID_BLOCK = re.compile(r"(?ms)^ {0,3}(`{3,}|~{3,})\s*mermaid[^\n]*\n(.*?)^ {0,3}\1[ \t]*$")
MERMAID_INIT = re.compile(r"(?s)%%\{\s*init\s*:\s*(.*?)\}\s*%%")
MERMAID_CLASSDEF = re.compile(r"(?m)^\s*classDef\s+([\w,]+)")
MERMAID_CLASS_REF = re.compile(r"(?m):::(\w+)|^\s*class\s+[\w,\s]+?\s+(\w+)\s*$")


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


def html_block_spacing(prose: str) -> list[str]:
    """Return the HTML tag lines whose Markdown neighbour lacks a blank line."""
    lines = prose.splitlines()
    flagged: list[str] = []
    for index, line in enumerate(lines):
        if HTML_OPEN_NEEDS_BLANK.search(line) and index + 1 < len(lines):
            following = lines[index + 1].strip()
            if following and not following.startswith("<"):
                flagged.append(line.strip())
        if HTML_CLOSE_NEEDS_BLANK.match(line) and index > 0:
            preceding = lines[index - 1].strip()
            if preceding and not preceding.startswith("<"):
                flagged.append(line.strip())
    return flagged


def image_sources(prose: str) -> tuple[list[str], list[str]]:
    """Return (local image paths, images without alt text) from Markdown and HTML."""
    sources: list[str] = []
    missing_alt: list[str] = []
    for match in MARKDOWN_IMAGE.finditer(prose):
        target = link_target(match.group(2))
        if not match.group(1).strip():
            missing_alt.append(target)
        sources.append(target)
    for tag in HTML_IMG.findall(prose):
        if not HTML_ALT.search(tag):
            src = HTML_SRC.search(tag)
            missing_alt.append(src.group(1) if src else tag[:60])
    for src in HTML_SRC.findall(prose):
        for candidate in src.split(","):
            parts = candidate.split()
            if parts:
                sources.append(parts[0])
    local: list[str] = []
    for target in sources:
        try:
            if not target or target.startswith("#") or urlparse(target).scheme:
                continue
        except ValueError:
            continue
        base = unquote(target.split("#", 1)[0])
        if base and base not in local:
            local.append(base)
    return local, missing_alt


def check_svg(path: Path, label: str) -> list[str]:
    """Static facts about one SVG that decide whether it renders on GitHub."""
    warnings: list[str] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return warnings
    root = SVG_ROOT.search(text)
    if not root:
        return warnings
    width = None
    viewbox = SVG_VIEWBOX.search(root.group(0))
    if viewbox:
        width = float(viewbox.group(1))
    else:
        warnings.append(f"SVG has no viewBox, so it cannot scale with the page: {label}")
    if SVG_EXTERNAL.search(text):
        warnings.append(
            f"SVG loads a resource from outside the repository: {label}"
            " -- GitHub's image proxy blocks it, so fonts and images fall back silently"
        )
    if SVG_SCRIPT.search(text):
        warnings.append(f"SVG contains a <script> element, which GitHub strips: {label}")
    if width:
        floor = width / 100
        small = sorted({float(size) for size in SVG_FONT_SIZE.findall(text) if float(size) < floor})
        if small:
            warnings.append(
                f"SVG sets text at {small[0]:g} units on a {width:g}-unit canvas: {label}"
                f" -- below the {floor:g}-unit legibility floor at README width"
            )
    return warnings


def check_mermaid(text: str) -> list[str]:
    """Check each Mermaid block for the mistakes that render as an error box."""
    warnings: list[str] = []
    for index, match in enumerate(MERMAID_BLOCK.finditer(text), start=1):
        body = match.group(2)
        for init in MERMAID_INIT.findall(body):
            try:
                json.loads(init)
            except ValueError as error:
                warnings.append(
                    f"Mermaid block {index} has an init directive that is not valid JSON"
                    f" ({error}): the whole diagram renders as an error"
                )
        defined = {name for group in MERMAID_CLASSDEF.findall(body) for name in group.split(",")}
        referenced = {a or b for a, b in MERMAID_CLASS_REF.findall(body)}
        undefined = sorted(referenced - defined - {"default"})
        if undefined:
            warnings.append(
                f"Mermaid block {index} applies classes with no classDef: {', '.join(undefined)}"
            )
    return warnings


def check_document(document: Path, project: Path) -> list[str]:
    """Run every static check on one document and return its warnings."""
    text = document.read_text(encoding="utf-8")
    prose = strip_code(text)
    warnings: list[str] = []

    markers = sorted({match.group(0).strip() for match in UNFINISHED_MARKERS.finditer(prose)})
    if markers:
        warnings.append(
            "Contains unfinished markers ({}): resolve them -- ask the user or report the gap"
            " in the delivery summary; a document ships no placeholders".format(", ".join(markers))
        )

    if EMPTY_LINK.search(prose):
        warnings.append("Contains a link with an empty target")

    if LICENSE_BADGE.search(prose):
        warnings.append(
            "Carries a license badge -- the LICENSE file is the only place the license"
            " lives; remove the badge"
        )
    if document.name.upper().startswith("README") and any(
        HEADING_LINE.match(line) and LICENSE_HEADING.search(line) for line in prose.splitlines()
    ):
        warnings.append(
            "README carries a License section -- omit it unless the licensing needs"
            " explaining (dual licence, per-directory terms), and then keep it to one line"
        )

    for line in html_block_spacing(prose):
        warnings.append(
            "HTML block needs a blank line between the tag and the Markdown beside it,"
            f" or GitHub shows the Markdown source: {line[:80]}"
        )

    images, missing_alt = image_sources(prose)
    for target in missing_alt:
        warnings.append(f"Image has no alt text: {target[:80]}")

    warnings.extend(check_mermaid(text))

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

    targets = local_targets(prose)
    targets += [image for image in images if image not in targets]
    for target in targets:
        candidate = (document.parent / target).resolve()
        try:
            candidate.relative_to(project)
        except ValueError:
            warnings.append(f"Local link escapes the project directory: {target}")
            continue
        if not candidate.exists():
            warnings.append(f"Local link does not exist: {target}")
        elif candidate.suffix.lower() == ".svg":
            warnings.extend(check_svg(candidate, target))

    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check project documents for unfinished markers, local links,"
        " license placement, HTML block spacing, referenced SVGs, and Mermaid blocks"
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
