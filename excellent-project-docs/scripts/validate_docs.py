"""Perform low-dependency checks for common project-documentation issues.

Accepts one or more Markdown documents (README.md, CONTRIBUTING.md,
SECURITY.md, ARCHITECTURE.md, ...) and runs the same checks on each. Local
SVG images a document references are opened and checked too, and Mermaid
blocks are checked for the mistakes that make GitHub render an error box.

Scope is deliberately narrow: only checks whose result is a verifiable fact
or a direct violation of a documented recipe rule (animation, accessible
name). Judging whether a section or a companion document is present and
useful belongs to `references/quality-checklist.md`, not to keyword matching.

Every warning is a heuristic lead, not a verdict: read the flagged line and
decide whether it is a real problem before editing the document.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter
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

# Headings and explicit anchors a `#fragment` link can land on. Setext
# headings count too, because a paragraph line directly above `---` is one.
ATX_HEADING = re.compile(r"^ {0,3}#{1,6}[ \t]+(.*?)(?:[ \t]+#+)?[ \t]*$")
SETEXT_UNDERLINE = re.compile(r"^ {0,3}(?:=+|-+)[ \t]*$")
HTML_ANCHOR = re.compile(r"""(?i)<[a-z][^>]*?\b(?:name|id)\s*=\s*["']([^"']+)["']""")
LINK_TEXT = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
MARKDOWN_FILE = re.compile(r"(?i)\.(?:md|markdown)$")

# A prose reference to a license file (uppercase filename convention only, so
# ordinary words like "license" stay out of scope). Lines that negate or
# discuss the absence ("no LICENSE file", 「未包含 LICENSE」) are legitimate
# disclosures and must not be flagged.
LICENSE_FILE_WORD = re.compile(r"\b(?:LICENSE|LICENCE|COPYING)\b")

# A License section that names a license but has no file to back it. Scoped to
# the document's own License heading so a dependency's license mentioned
# elsewhere in the prose stays out of range. In Chinese 授權/授权 also means
# authorization (an OAuth flow) and 許可 means permission, so a bare
# occurrence counts only when it is the whole heading; compounds that can only
# mean a license count anywhere in it.
LICENSE_HEADING = re.compile(
    r"(?i)\blicen[sc]e\b"
    r"|授權條款|授权条款|授權協議|授权协议|許可證|许可证"
    r"|^ {0,3}#{1,6}\s+(?:[^\w\s]+\s*)?(?:開源|开源)?(?:授權|授权)\s*#*\s*$"
)
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
#
# The rest are the failures that only appear once GitHub renders the file,
# never in a local preview: an SVG image has no background of its own, so a
# canvas with no covering rect lets the dark theme through; `<text>` collapses
# runs of whitespace the way HTML does, so an aligned mockup loses its columns
# without `xml:space="preserve"`; an `<image>` with a file href is an external
# resource the `<img>`-embedded SVG never fetches, and a `<foreignObject>` is
# not drawn by every browser in that mode; a group scaled below 1 shrinks its
# text under the canvas-relative floor; and CJK advances one em per glyph,
# about twice the Latin coefficient the recipe uses.
#
# Animation and accessible-name warnings are recipe-rule leads rather than
# render facts; rationale sits with their regexes below.
SVG_ROOT = re.compile(r"(?is)<svg\b[^>]*>")
SVG_VIEWBOX = re.compile(
    r"""(?i)\bviewBox\s*=\s*["']\s*[-\d.]+[\s,]+[-\d.]+[\s,]+([\d.]+)[\s,]+([\d.]+)\s*["']"""
)
SVG_EXTERNAL = re.compile(
    r"""(?i)(?:href|src|srcset)\s*=\s*["']\s*(?:https?:)?//|@import\b|url\(\s*["']?\s*(?:https?:)?//"""
)
SVG_SCRIPT = re.compile(r"(?i)<script\b")
# A README is read, not watched: any CSS keyframes, SMIL animation element, or
# animate* attribute on a referenced SVG is out of the recipe, with or without
# a prefers-reduced-motion guard.
SVG_ANIMATION = re.compile(
    r"(?i)@keyframes\b|\banimation\s*[:=]|<(?:animate|animateTransform|animateMotion)\b"
    r"|\banimate(?:Transform|Motion|Color)?\s*=\s*[\"']"
)
# The accessible name a screen-reader user gets when the image is the only
# copy of the figure: aria-label on the <svg> root, or a non-empty <title>
# as the root's first element child. role="img" is the recipe's preferred
# pairing with aria-label and is named in the fix message, but either
# mechanism alone still names the image. The title body must start with a
# non-whitespace, non-`<` character: `\s*\S` alone would accept `<title></title>`
# because `\S` matches the `<` of the closing tag.
SVG_ARIA_LABEL = re.compile(r"""(?i)\baria-label\s*=\s*["'][^"']*\S[^"']*["']""")
SVG_TITLE_CHILD = re.compile(
    r"(?is)\A\s*(?:<!--.*?-->\s*)*<title\b[^>]*>\s*[^<\s][^<]*</title\s*>"
)
# A relative unit (em, rem, %) cannot be resolved without the cascade, so the
# lookahead drops it instead of reading "1.5em" as 1 unit.
SVG_FONT_SIZE = re.compile(
    r"""(?i)font-size\s*[=:]\s*["']?\s*(\d+(?:\.\d+)?)(?:px)?(?![\w.%])"""
)
# Each quote style is matched on its own so a style="font-family:'Segoe UI';
# font-size:20" keeps its whole value instead of stopping at the first '.
SVG_ATTR = re.compile(r"""(?i)\b([\w:-]+)\s*=\s*(?:"([^"]*)"|'([^']*)')""")
SVG_RECT = re.compile(r"(?is)<rect\b[^>]*>")
# Rects inside these containers define a resource, not the drawing.
SVG_RESOURCE_BLOCK = re.compile(
    r"(?is)<(defs|pattern|clipPath|mask|marker|symbol)\b.*?</\1\s*>"
)
SVG_TEXT = re.compile(r"(?is)<text\b([^>]*)>(.*?)</text>")
SVG_TSPAN = re.compile(r"(?is)<tspan\b([^>]*)>(.*?)</tspan>")
SVG_TAG = re.compile(r"(?is)<[^>]*>")
SVG_ID = re.compile(r"""(?i)(?<![\w:-])id\s*=\s*["']([^"']+)["']""")
SVG_SCALE = re.compile(r"(?i)\bscale\s*\(\s*([\d.]+)")
SVG_FOREIGN_OBJECT = re.compile(r"(?i)<foreignObject\b")
SVG_IMAGE_ELEMENT = re.compile(r"(?i)<image\b")
SVG_XML_SPACE = re.compile(r"""(?i)xml:space\s*=\s*["']preserve["']""")
STYLE_FONT_SIZE = re.compile(r"""(?i)font-size\s*:\s*([^;"'}]+)""")
SPACE_RUN = re.compile(r"\S {2,}\S")
CJK_TEXT = re.compile(
    r"[\u1100-\u11ff\u3000-\u303f\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff"
    r"\uac00-\ud7af\uf900-\ufaff\uff01-\uff60\uff66-\uff9f]"
)

# Below this canvas width an SVG is an icon or a badge, not a banner or a
# figure; a transparent ground and a single short label are legitimate there,
# so the ground and text checks stay out of its way.
BANNER_CANVAS = 300

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


def fragment_links(text: str) -> list[tuple[str, str]]:
    """Return (path, fragment) for every Markdown link carrying a #fragment.

    The path is "" for a link into the same document.
    """
    links: list[tuple[str, str]] = []
    for match in LINK.finditer(text):
        target = link_target(match.group(1))
        if "#" not in target:
            continue
        try:
            if urlparse(target).scheme:
                continue
        except ValueError:
            continue
        base, fragment = target.split("#", 1)
        if fragment:
            links.append((unquote(base), unquote(fragment)))
    return links


def github_slug(heading: str) -> str:
    """Return the anchor GitHub derives from a heading's text.

    Mirrors github-slugger: lowercase, drop every character that is not a
    letter, number, mark, hyphen, underscore, or space, then turn spaces into
    hyphens. Link syntax, HTML tags, and code backticks are markup, not text.
    """
    text = LINK_TEXT.sub(r"\1", heading)
    text = SVG_TAG.sub("", text).replace("`", "")
    kept = "".join(
        char
        for char in text.lower()
        if char in "-_ " or unicodedata.category(char)[0] in "LNM"
    )
    return kept.replace(" ", "-")


def document_anchors(text: str) -> set[str]:
    """Return every anchor a document defines, lowercased."""
    body = FENCED_BLOCK.sub("", text)
    lines = body.splitlines()
    anchors = {"top"}
    seen: Counter[str] = Counter()
    for index, line in enumerate(lines):
        match = ATX_HEADING.match(line)
        heading = match.group(1) if match else None
        if (
            heading is None
            and line.strip()
            and index + 1 < len(lines)
            and SETEXT_UNDERLINE.match(lines[index + 1])
        ):
            heading = line.strip()
        if heading is None:
            continue
        slug = github_slug(heading)
        count = seen[slug]
        seen[slug] += 1
        anchors.add(slug if count == 0 else f"{slug}-{count}")
    anchors.update(anchor.lower() for anchor in HTML_ANCHOR.findall(body))
    return anchors


def resolve_local(document: Path, project: Path, target: str) -> Path:
    """Resolve a local link the way GitHub does: a leading / is the repository root."""
    if target.startswith("/"):
        return (project / target.lstrip("/")).resolve()
    return (document.parent / target).resolve()


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


def _attribute(tag: str, name: str) -> str:
    """Return the value of one attribute of a tag, or "" when absent.

    SVG attribute names are case-sensitive in the file (`textLength`,
    `lengthAdjust`, `viewBox`) but callers should not have to remember which
    spelling each one uses, so the lookup is case-insensitive.
    """
    wanted = name.lower()
    for key, double_quoted, single_quoted in SVG_ATTR.findall(tag):
        if key.lower() == wanted:
            return (double_quoted or single_quoted).strip()
    return ""


_LENGTH_RE = re.compile(
    r"""(?i)^\s*([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*([a-z%]*)\s*$"""
)
_LENGTH_UNIT_TO_PX = {
    "": 1.0,
    "px": 1.0,
    "pt": 96.0 / 72.0,
    "pc": 16.0,
    "in": 96.0,
    "cm": 96.0 / 2.54,
    "mm": 96.0 / 25.4,
    "q": 96.0 / 101.6,
}


def _length_in_px(value: str) -> float | None:
    """Return an SVG length in user units (1px == 1 user unit), or None."""
    match = _LENGTH_RE.match(value)
    if not match:
        return None
    number, unit = float(match.group(1)), match.group(2).lower()
    if unit == "%":
        return None
    factor = _LENGTH_UNIT_TO_PX.get(unit)
    return number * factor if factor is not None else None


def _resolved_size(value: str, canvas: float) -> float:
    """Return an SVG length in user units, treating a percentage of the canvas."""
    stripped = value.strip()
    if stripped.endswith("%"):
        try:
            return float(stripped[:-1].strip()) / 100 * canvas
        except ValueError:
            return 0.0
    parsed = _length_in_px(stripped)
    return parsed if parsed is not None else 0.0


def _covers_canvas(tag: str, canvas_width: float, canvas_height: float) -> bool:
    """Whether one <rect> covers the whole canvas with a visible fill."""
    if _attribute(tag, "fill").lower() in {"none", "transparent"}:
        return False
    for name in ("fill-opacity", "opacity"):
        value = _attribute(tag, name)
        if value and _length_in_px(value) == 0:
            return False
    width = _resolved_size(_attribute(tag, "width"), canvas_width)
    height = _resolved_size(_attribute(tag, "height"), canvas_height)
    x = _resolved_size(_attribute(tag, "x"), canvas_width)
    y = _resolved_size(_attribute(tag, "y"), canvas_height)
    return (
        x <= 0
        and y <= 0
        and x + width >= canvas_width
        and y + height >= canvas_height
    )


def _font_size(attributes: str) -> float | None:
    """Return the font-size declared on a tag, inline attribute or style, or None."""
    raw = _attribute(attributes, "font-size")
    if raw:
        return _length_in_px(raw)
    style = STYLE_FONT_SIZE.search(_attribute(attributes, "style"))
    if not style:
        return None
    return _length_in_px(style.group(1))


_CONTAINER_TAG = re.compile(r"(?is)<\s*(/?)\s*(svg|g)\b([^>]*)>")


def _ancestor_attributes(text: str, pos: int) -> list[str]:
    """Return attribute strings of the <svg>/<g> elements enclosing pos."""
    stack: list[str] = []
    for match in _CONTAINER_TAG.finditer(text, 0, pos):
        full, is_close, attrs = match.group(0), match.group(1), match.group(3) or ""
        if full.endswith("/>"):
            continue
        if is_close:
            if stack:
                stack.pop()
        else:
            stack.append(attrs)
    return stack


def _inherited_font_size(
    attributes: str, ancestors: list[str], body: str
) -> float | None:
    """Return the font-size for a <text>: own, else nearest ancestor, else None.

    Sizes set via CSS class or external stylesheet are not resolved (no
    stylesheet parsing), so those still return None and the caller skips the
    arithmetic check rather than guessing. An inner <tspan> size overrides the
    line size; the largest one is used so an overflowing run is not missed.
    """
    size = _font_size(attributes)
    if size is None:
        for ancestor in reversed(ancestors):
            size = _font_size(ancestor)
            if size is not None:
                break
    for tspan in re.finditer(r"(?is)<tspan\b([^>]*)>", body):
        tspan_size = _font_size(tspan.group(1))
        if tspan_size is not None and (size is None or tspan_size > size):
            size = tspan_size
    return size


def _enclosing_scale(ancestors: list[str]) -> float:
    """Return the product of scale() factors on enclosing <g> elements."""
    scale = 1.0
    for ancestor in ancestors:
        factor = SVG_SCALE.search(ancestor)
        if factor:
            try:
                scale *= float(factor.group(1))
            except ValueError:
                continue
    return scale


def _widest_cjk_line(body: str, size: float | None) -> tuple[int, float | None]:
    """Return (CJK glyph count, font-size) of the widest rendered line in a <text>.

    A <tspan> that repositions itself (`x`, `y`, or `dy`) starts a new line, so
    a multi-line block written the way the recipe recommends is measured one
    line at a time rather than as one run. Bare text and a <tspan> that only
    restyles continue the current line at the largest size it carries.
    """
    lines: list[list[float | None | int]] = [[0, size]]
    cursor = 0

    def extend(text: str, run_size: float | None) -> None:
        current = lines[-1]
        current[0] += len(CJK_TEXT.findall(SVG_TAG.sub("", text)))
        if run_size is not None and (current[1] is None or run_size > current[1]):
            current[1] = run_size

    for tspan in SVG_TSPAN.finditer(body):
        extend(body[cursor : tspan.start()], None)
        tspan_attrs, tspan_body = tspan.group(1), tspan.group(2)
        if any(_attribute(tspan_attrs, name) for name in ("x", "y", "dy")):
            lines.append([0, size])
        extend(tspan_body, _font_size(tspan_attrs))
        cursor = tspan.end()
    extend(body[cursor:], None)

    widest = max(lines, key=lambda line: (line[0] * (line[1] or 0), line[0]))
    return int(widest[0]), widest[1]


def _cjk_warnings(
    attributes: str,
    body: str,
    width: float,
    label: str,
    fallback_size: float | None = None,
) -> list[str]:
    """Check one <text> holding CJK against the facts that are arithmetic.

    A CJK glyph advances one em in every CJK font, so both the natural width
    of the line and the effect of a `textLength` pin are computable rather
    than estimated. `lengthAdjust="spacingAndGlyphs"` scales the glyphs along
    the inline axis, which visibly stretches or squeezes a square glyph;
    `lengthAdjust="spacing"` cannot compress below the natural width, so a pin
    narrower than the string collapses its spaces and then overflows anyway.
    """
    warnings: list[str] = []
    if not CJK_TEXT.search(body):
        return warnings
    glyphs, size = _widest_cjk_line(body, _font_size(attributes) or fallback_size)
    if not glyphs:
        return warnings
    target = _attribute(attributes, "textLength")
    adjust = _attribute(attributes, "lengthAdjust").lower() or "spacing"
    natural = glyphs * size if size else None

    if natural is not None and natural > width - 120:
        warnings.append(
            f"CJK line of {glyphs} glyphs at font-size {size:g} needs {natural:g} units"
            f" on a {width:g}-unit canvas: {label}"
            " -- wider than the canvas once its margins are kept, so it overflows"
            " wherever it sits; lower the font-size or shorten the line"
        )
    if not target:
        return warnings
    if adjust == "spacingandglyphs":
        warnings.append(
            f"CJK text is pinned with lengthAdjust=\"spacingAndGlyphs\": {label}"
            " -- that scales the glyphs along the inline axis, so square CJK glyphs"
            " come out stretched or squeezed; size the line from the CJK coefficient"
            " instead and pin it, if at all, with lengthAdjust=\"spacing\""
        )
    elif natural is not None:
        pinned = _length_in_px(target)
        if pinned is not None and pinned < natural:
            warnings.append(
                f"CJK text is pinned to {pinned:g} units but needs {natural:g}: {label}"
                " -- lengthAdjust=\"spacing\" cannot compress below the natural width,"
                " so the spaces collapse and the line overflows anyway; lower the"
                " font-size instead"
            )
    return warnings


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
    height = 0.0
    viewbox = SVG_VIEWBOX.search(root.group(0))
    if viewbox:
        width = float(viewbox.group(1))
        height = float(viewbox.group(2))
    else:
        warnings.append(f"SVG has no viewBox, so it cannot scale with the page: {label}")
    fixed = [
        name
        for name in ("width", "height")
        if _attribute(root.group(0), name)
        and not _attribute(root.group(0), name).endswith("%")
    ]
    if fixed:
        warnings.append(
            f"SVG root sets a fixed width or height ({', '.join(fixed)}): {label}"
            " -- the recipe keeps only the viewBox so the image scales with the"
            " README column; remove them"
        )
    if SVG_EXTERNAL.search(text):
        warnings.append(
            f"SVG loads a resource from outside the repository: {label}"
            " -- GitHub's image proxy blocks it, so fonts and images fall back silently"
        )
    if SVG_SCRIPT.search(text):
        warnings.append(f"SVG contains a <script> element, which GitHub strips: {label}")
    if SVG_ANIMATION.search(text):
        warnings.append(
            f"SVG contains an animation: {label} -- a README banner or figure is read,"
            " not watched; remove the @keyframes, animation, or <animate> element (a"
            " prefers-reduced-motion guard is not an exception, because the animation"
            " itself is never written)"
        )
    # An accessible name is aria-label on the root or a non-empty <title> as
    # its first element child; role="img" is what the recipe asks for alongside
    # aria-label, and the fix message says so, but a title alone still names
    # the image for a screen reader.
    root_body = text[root.end() :]
    if not (
        SVG_ARIA_LABEL.search(root.group(0)) or SVG_TITLE_CHILD.search(root_body)
    ):
        warnings.append(
            f"SVG has no accessible name: {label} -- add role=\"img\" and an aria-label"
            " on the <svg> root (or a non-empty <title> as its first child) stating the"
            " facts the figure shows, so a reader who cannot see the image still gets"
            " what the prose beside it gives"
        )
    if SVG_FOREIGN_OBJECT.search(text):
        warnings.append(
            f"SVG contains a <foreignObject>: {label} -- not every browser draws it"
            " inside an SVG loaded through <img>, so some readers see a hole; draw the"
            " content with SVG elements instead"
        )
    if SVG_IMAGE_ELEMENT.search(text):
        warnings.append(
            f"SVG contains an <image> element: {label} -- an SVG loaded through <img>"
            " fetches no external file, so a file href draws nothing, and a data: URI"
            " embeds a raster the recipe never produces; draw the shape with SVG"
            " elements instead"
        )

    duplicated = sorted(name for name, count in Counter(SVG_ID.findall(text)).items() if count > 1)
    if duplicated:
        warnings.append(
            f"SVG repeats an id ({', '.join(duplicated)}): {label}"
            " -- a url(#id) reference resolves to the first match, so the wrong fill or"
            " clip can be applied"
        )

    if width:
        floor = width / 100
        sizes = {float(size) for size in SVG_FONT_SIZE.findall(text)}
        small = sorted(size for size in sizes if size < floor)
        if small:
            warnings.append(
                f"SVG sets text at {small[0]:g} units on a {width:g}-unit canvas: {label}"
                f" -- below the {floor:g}-unit legibility floor at README width"
            )
        shrunk: list[tuple[float, float, float]] = []
        for text_match in SVG_TEXT.finditer(text):
            text_attrs, text_body = text_match.group(1), text_match.group(2)
            ancestors = _ancestor_attributes(text, text_match.start())
            scale = _enclosing_scale(ancestors)
            if scale >= 1:
                continue
            size = _inherited_font_size(text_attrs, ancestors, text_body)
            if size is None:
                continue
            if size * scale < floor:
                shrunk.append((size, scale, size * scale))
        if shrunk:
            size, scale, effective = sorted(shrunk, key=lambda item: item[2])[0]
            warnings.append(
                f"SVG scales a group to {scale:g} on a {width:g}-unit canvas: {label}"
                f" -- text at {size:g} units inside it renders at {effective:g} units,"
                f" under the {floor:g}-unit legibility floor, which the size above"
                " does not show"
            )

    if width and width >= BANNER_CANVAS and SVG_TEXT.search(text):
        drawing = SVG_RESOURCE_BLOCK.sub("", text)
        if not any(_covers_canvas(tag, width, height) for tag in SVG_RECT.findall(drawing)):
            warnings.append(
                f"SVG carries text but no rect covers the whole canvas: {label}"
                " -- an SVG image has no background of its own, so the page shows through"
                " and a light-ground banner loses its ground in GitHub's dark theme"
            )
        text_matches = list(SVG_TEXT.finditer(text))
        root_preserved = bool(SVG_XML_SPACE.search(root.group(0)))
        if not root_preserved:
            misaligned = False
            for text_match in text_matches:
                if SVG_XML_SPACE.search(text_match.group(1)):
                    continue
                plain = SVG_TAG.sub("", text_match.group(2))
                if any(SPACE_RUN.search(line) for line in plain.splitlines()):
                    misaligned = True
                    break
            if misaligned:
                warnings.append(
                    f"SVG aligns text with runs of spaces and has no xml:space=\"preserve\":"
                    f" {label} -- the renderer collapses them the way HTML does, so the"
                    " columns of a mockup misalign; add the attribute to that <text> or place"
                    " one <tspan x=\"...\"> per line"
                )
        for text_match in text_matches:
            attributes, body, start = (
                text_match.group(1),
                text_match.group(2),
                text_match.start(),
            )
            ancestors = _ancestor_attributes(text, start)
            # Per-line <tspan> sizes are resolved inside the CJK check itself.
            fallback = _inherited_font_size(attributes, ancestors, "")
            warnings.extend(_cjk_warnings(attributes, body, width, label, fallback))
    return warnings


def check_mermaid(text: str) -> list[str]:
    """Check each Mermaid block for the mistakes that render as an error box."""
    warnings: list[str] = []
    for index, match in enumerate(MERMAID_BLOCK.finditer(text), start=1):
        body = match.group(2)
        for init in MERMAID_INIT.findall(body):
            try:
                # Mermaid swaps single quotes for double before parsing, and
                # its own directive examples are written that way.
                json.loads(init.replace("'", '"'))
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

    # Compared by name rather than glob, which is case-sensitive on Linux and
    # would miss License.md or license.
    has_license_file = any(
        entry.name.upper().startswith(("LICENSE", "LICENCE", "COPYING"))
        for entry in project.iterdir()
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
        candidate = resolve_local(document, project, target)
        try:
            candidate.relative_to(project)
        except ValueError:
            warnings.append(f"Local link escapes the project directory: {target}")
            continue
        if not candidate.exists():
            warnings.append(f"Local link does not exist: {target}")
        elif candidate.suffix.lower() == ".svg":
            warnings.extend(check_svg(candidate, target))

    # Only Markdown targets are checked: a fragment on a source file (#L10) is
    # a line range GitHub generates, not a heading.
    anchor_cache: dict[Path, set[str]] = {document: document_anchors(text)}
    for base, fragment in fragment_links(prose):
        if base:
            if not MARKDOWN_FILE.search(base):
                continue
            candidate = resolve_local(document, project, base)
            if not candidate.is_file():
                continue  # the missing file is already reported above
        else:
            candidate = document
        if candidate not in anchor_cache:
            anchor_cache[candidate] = document_anchors(
                candidate.read_text(encoding="utf-8", errors="replace")
            )
        if fragment.lower() not in anchor_cache[candidate]:
            warnings.append(f"Anchor does not exist: {base}#{fragment}")

    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check project documents for unfinished markers, local links and"
        " anchors, license placement, HTML block spacing, referenced SVGs (including animation"
        " and accessible name), and Mermaid blocks"
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
