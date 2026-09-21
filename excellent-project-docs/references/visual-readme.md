# Showcase README

Two presentation levels exist. **Plain** is the default: text, tables, code blocks, and the badges or images the user picked. **Showcase** turns the same facts into a designed page — a header block with a banner designed for the project and a facts line, one figure per concept (themed Mermaid or hand-drawn SVG), feature cards, and collapsed reference tables — in the style of highly visual open-source pages. Read this file only when the user chose showcase at the step 3 checkpoint; never apply it on your own initiative.

Everything else in [readme-framework](readme-framework.md) still holds. Showcase changes how facts are presented, not which facts exist: every node in a diagram, every fact in the banner, every card in the grid is a component, command, number, or step the evidence inventory recorded; the license stays in the LICENSE file with no badge or section; no image or diagram carries the only copy of a fact, because renderers outside GitHub (npm, PyPI, crates.io, editor previews) may show nothing in its place.

The bar for every element below: **it must be recognisably this project's.** A banner, card grid, or diagram that would fit any repository unchanged is a template, not a design — give it the project's colour, its shapes, its numbers.

## Style proposal

The style is derived from the project and then chosen by the user — never guessed silently, never asked as an open question. Before the step 3 checkpoint, read three things off the repository and turn them into a proposal:

| Dimension | Read it from | Proposal |
| --- | --- | --- |
| Accent | Logo, existing assets, a site's CSS, a favicon; failing those, the palette rule below | The brand colour, or the rule's pick with the reason ("emerald, since the stack's own colours are purple and blue") |
| Mood | The existing README, docs site, or screenshots: terminal-style projects and CLIs read dark; design-system, education, and documentation-heavy projects read light | Dark by default; light when the evidence leans that way |
| Domain cue | What the project's subject looks like to its own users, read from the files the program writes or prints (`examples/`, fixtures, scaffold templates in the source), the vocabulary in its tool and command names, and the name itself — a game's map grid and mod manifest, a terminal, a spreadsheet, a graph, a timeline | The one artefact a reader from that domain recognises on sight (the mod manifest `create_mod` writes, the migration file, the request body) and one or two shapes or textures that echo the domain, plus a colour lean if the domain has one (earth tones for a colony game, cool greys for infrastructure) |
| Direction | What the project is: a library, a CLI or server with a session, a pipeline or architecture, a project with a brand asset | One of the four banner directions below, with the figure or mockup it would carry named in the project's own terms — the domain artefact first when there is one, an internal mechanism (a cache tier, a pipeline stage) only when there is not |

Put the proposal and one alternative to the user in the same checkpoint message as the other presentation questions ("dark, warm earth tones with an orange accent, the map-grid texture, and a card showing the `About.xml` that `create_mod` writes — or figure-first with the three index tiers"), and take whatever they answer, including a colour or mood of their own. Colour alone never carries identity — a dark ground and one accent fit any CLI — so a proposal without a domain cue is incomplete.

The banner is the highest-variance element on the page, so it is judged before the page is written: draft the banner first, run the render check, and 🔴 **CHECKPOINT** with the PNG attached — the user judges an image, not SVG source. Continue to the rest of the README only after they accept it or after one revision round on their notes; a rejected banner costs one file, not the whole delivery.

## Palette

Choose once, reuse everywhere — banner, diagrams, cards:

- **Accent**: the project's existing brand colour when its assets, site, or logo have one. Otherwise pick one of `#f97316` (orange), `#10b981` (emerald), `#0ea5e9` (sky), `#8b5cf6` (violet) — the one the domain cue leans toward when it leans, and otherwise whichever is furthest from the colours of the technologies the README names, so the accent reads as the project rather than as a framework logo.
- **Ground**, by mood, tinted toward the domain when the cue gives one: the dark ground may lean warm (`#14110e`) or cool (`#0e1116`), the light ground likewise, with every text colour re-sampled for contrast against the tinted ground. Dark: `#0f0f0f` ground, `#ffffff` wordmark, `#c8c8c8` body, `#8a8a8a` captions, `#2a2a2a` rules, motif greys `#3d3d3d` → `#242424`. Light editorial: `#fafafa` ground, `#111111` wordmark, `#444444` body, `#6f6f6f` captions, `#e0e0e0` rules, motif greys `#c4c4c4` → `#e6e6e6`. One accent and one ground are the scheme; a second hue only where it carries meaning (success, error, a second party in a diagram). Depth — a gradient ground, a glow behind a card, layered panels — is a taste decision for the direction chosen below, kept subtle enough that every text still passes contrast against what is directly behind it.
- **Theme adaptation** is opt-in: the fixed ground already reads the same in GitHub's light and dark modes. When the user wants the banner to follow the viewer's theme, write both moods as two SVG files and reference them with `<picture>` and `prefers-color-scheme` sources — the mechanism GitHub documents — rather than a media query inside one SVG, which some renderers ignore.
- **Animation** is out: a README banner is read, not watched, and a moving banner says nothing a static one does not.
- **Diagrams** render on GitHub's light and dark backgrounds alike, so node fills are light tints of the accent with dark text (`#0b1220`) and the accent as border; never white text on a light fill or dark text on the ground colour.

## The header block

The first screen becomes a centered block. Include only the lines whose input exists:

````markdown
<div align="right">

**[English](README.md)** | [繁體中文](README.zh-TW.md)

</div>

![<Project name>](assets/banner.svg)

<p align="center">
  <img src="assets/demo.gif" alt="<what the demo shows, in one sentence>" />
</p>

<div align="center">

# <Project name>

**<The tagline the user chose.>**

<One sentence of context: who it is for, or what it replaces.>

**Windows · macOS · Linux** &nbsp;·&nbsp; **18 tools** &nbsp;·&nbsp; **100% local, no network**

[![npm version](https://img.shields.io/npm/v/<package>.svg)](https://www.npmjs.com/package/<package>)
[![CI](https://github.com/<owner>/<repo>/actions/workflows/ci.yml/badge.svg)](https://github.com/<owner>/<repo>/actions/workflows/ci.yml)

```bash
<the one install or run command the user chose as the primary path>
```

</div>

---
````

Rules for the block:

- The language switch line appears only when translated variants exist, and it appears in every variant.
- The hero `<img>` uses a demo, screenshot, or animation that already exists in the repository. This skill does not produce raster images or animations; when none exists, drop the `<p>` and list "hero image or demo animation" as a recommendation in the delivery report.
- The **facts line** carries three to five numbers or nouns a reader uses to decide fit — platforms, tool or command count, package size, "no network", supported versions — each traced to a manifest, a directory listing, or code. A count is computed from the repository at writing time and recorded in the report as `counted from <path>`.
- Badges follow the badge rules and the user's answer at the checkpoint; a showcase README with zero badges is valid.
- Leave a blank line after every opening HTML tag and before every closing one, or GitHub will not render the Markdown inside it.
- The install command is the primary path the user chose; the full Getting Started section still follows later.

## The banner

When the repository has no banner, write one as an SVG so the user can replace it later with their own artwork. Put it where the repository already keeps images (`assets/`, `docs/images/`, `.github/`); create `assets/` only when no such directory exists. List the file under **Documents** in the delivery report as created.

Design it the way a front-end designer would: choose a direction that fits what the project *is*, then compose for this project. This recipe fixes what must be true of the result and how to check it — not what it looks like. Two banners made with it for two different projects should not share a layout.

### Directions

| Direction | Fits | What carries the design |
| --- | --- | --- |
| Editorial poster | A library, a tool with one clear concept, a project with a strong name | Typographic hierarchy — a small letter-spaced eyebrow, the name as a heavy display wordmark, the tagline — with one figure of the core concept beside it |
| Product or terminal mockup | A CLI, a server, an agent tool: anything with a session a reader would recognise | A window or terminal card showing a real invocation and the text the program actually prints, with the name and tagline set beside it |
| Figure-first | A pipeline, an architecture, a protocol: anything whose shape *is* the pitch | The figure fills the banner — real stages, ports, limits, boundaries — and the wordmark sits in a corner of it |
| Split panel | A project with a brand colour or a logo asset in the repository | One panel in the brand colour carrying the mark, the other carrying name, tagline, and facts |

Pick by fit, not by habit; when two directions fit, the one that shows more of the project's own concept wins. Depth (gradient, glow, cards), flat, dark, or light are taste decisions inside the direction, made for the mood chosen at the checkpoint.

### What every banner carries

- The project name as the heaviest element on the canvas.
- The tagline the user chose.
- At least one figure, mockup, or fact set drawn from this project's own concepts — the thing that makes the swap test fail: swap in another project's name, tagline, and facts, and the banner should look wrong.
- The domain cue from the proposal: an element a reader from the project's domain recognises in a glance without reading the name — the artefact the program writes in that domain, or a shape or texture the domain owns. Domain shapes are drawn with SVG primitives, never copied: no third-party logo, trademark, screenshot, font, or asset that is not in the repository, however recognisable it would be.
- Facts on the banner — counts, platforms, ports, limits, versions — traced to the repository and recorded in the report with their source. A count is computed from the repository at writing time (`counted from <path>`).

### What a mockup may show

A terminal or window card shows only what the program actually emits: commands that exist in the CLI or manifest, and output text that exists as a string in the source, in a test fixture, or was captured from a run the user authorised. Sample identifiers, sample error messages, and "typical" results the repository does not contain are invented content, and the credibility they cost outweighs any design they add. When the real output is dull, show the command alone with a cursor, or choose another direction.

Each output line on a mockup is recorded in the delivery report under **Verified** with its provenance, the way counts are: `printed by <file>:<line>` for a string in the source or a fixture, `captured from <command>` for a run the user authorised. A line with neither is removed before delivery. Output built from a format string (`Indexed {n} symbols`, a runtime path, a timestamp) appears only when a `captured from` run supplied the values; without one the line is left out — a template line cited as `printed by` never carries values the agent chose. Lines are shown in the order the program emits them for that command; a card that stitches lines from different commands into one session is a fabricated session even when every line is real.

### Fitting text

With `W` the width available to a line — the column or card it sits in — compute every size before writing: an overflowing wordmark, tagline, or command line is the most common way a banner fails. The coefficients are Latin per-character advances measured in Chrome, and the reader's browser renders the banner with whatever font its system resolves the stack to, so read them as a floor:

| Text | Per-character width | Rule |
| --- | --- | --- |
| Display wordmark, weight 800–900 | 0.58 × font-size | `font-size = min(110, floor(W / (0.58 × chars)))`; a name too long for 48 breaks at a hyphen or word boundary onto a second line |
| Body and tagline, regular | 0.48 × font-size | `font-size = min(24, floor(W / (0.48 × chars)))`; below 18, wrap to a second line or ask for a shorter tagline |
| Monospace (commands, output, flow lines) | 0.6 × font-size per character | Total ≤ `W` of the card or column, arrows and prompts included |
| Uppercase letter-spaced labels | 0.65 × font-size + letter-spacing | ≤ 60 characters |
| Labels inside a shape | 0.5 × font-size | 16 units to spare on each side, or it moves beneath the shape |
| CJK (Chinese, Japanese, Korean) | 1.0 × font-size per character | A full-width glyph advances one em in every CJK font, so this is arithmetic rather than an estimate. Count the CJK and Latin runs of a mixed line separately and add them |

A line whose overflow would break the composition is pinned with `textLength="<W>"`, and `lengthAdjust` decides how. Pick it by script:

- **Latin**: `lengthAdjust="spacingAndGlyphs"`, with `W` within a tenth of what the string measures in your own font — a target far from the natural width visibly opens or closes the tracking. It reaches any width by scaling the glyphs, which is the only way to fit a line narrower than the string.
- **CJK**: do not pin. Size the line from its coefficient, and when it does not fit its column lower the font-size or shorten it. A pin that must exist uses `lengthAdjust="spacing"`, and only to widen, because `spacingAndGlyphs` scales the glyphs and a square glyph that has been scaled is no longer square. `spacing` cannot compress below the natural width either: asked for less it collapses the spaces and overflows anyway.

Legibility thresholds, checked on every text on the banner and in every hand-drawn figure:

- Size: nothing below 12 units. A 1200-unit canvas renders at about 900 px at README width on a desktop (0.75 px per unit), and about 360 px on a phone (0.3 px per unit), where only the name and the largest labels survive.
- Contrast: at least 4.5:1 (WCAG relative-luminance formula) between each text and the ground actually rendered under it — a card's fill, or on a gradient or glow the ground colour beside the glyphs at the darkest and lightest points along the line of text, both of which must pass; sample the rendered PNG, or without a renderer interpolate the stops at those offsets, never the nearest stop. The 3:1 large-text allowance starts at 32 units regular or 25 units at weight 700 or heavier. Fix a failing pair by changing the text colour, the ground, or the glow, then render again. Grey captions fail first: `#7a7a7a` on `#0f0f0f` is 4.47:1 and fails at 14 units; `#8a8a8a` passes at 5.55:1.
- Margins: at least 60 units from any text or shape to the canvas edge, and 16 from text to the edge of the card or column it sits in.

The measurements behind the coefficients and the two adjustments, and the test that tells them apart, are in [svg-text-measurements](svg-text-measurements.md).

### Constraints that keep the banner rendering everywhere

- Every string is the name, the tagline, a fact with a source, a real command or output line, or a label on a figure — no slogan, statistic, or claim the README does not already make.
- A fixed `viewBox="0 0 1200 400"` and no `width`/`height`, so it scales with the page. An SVG with only a `viewBox` stretches to whatever contains it — the README column, roughly 900–1000 px on a desktop and 360 px on a phone — but its intrinsic size resolves to 300 × 100, so a renderer that does not apply `max-width: 100%`, such as a third-party README viewer or a package page, shows it 300 px wide.
- The first drawing element after `<svg>` is a `<rect>` covering the whole `viewBox` with an opaque `fill`. An SVG image has no background of its own: without it GitHub's dark theme shows through, and a light-ground banner loses its ground while its dark text disappears into it.
- Text that aligns on consecutive spaces carries `xml:space="preserve"` on that `<text>`. Without it the renderer collapses the runs the way HTML does, so `A     B` draws as `A B` and every column below it misaligns. One `<tspan x="...">` per line is the alternative and needs no attribute.
- A `font-family` stack of system fonts. No `@import`, no `<image href>`, no external URL of any kind: GitHub serves SVGs through a proxy that blocks outbound requests, so an imported font fails silently and the text falls back anyway.
- No `<image>` and no `<foreignObject>` anywhere. An SVG loaded through `<img>` fetches no external file, so an `<image>` with a file href draws nothing; a `data:` URI does render (Chrome, headless, `<img>`-embedded — measured) but embeds a raster the recipe never produces. A `<foreignObject>` renders in Chrome the same way, yet not every browser draws it inside `<img>`, so some readers get a hole where the HTML block should be.
- A fixed ground so the banner reads the same in light and dark. To follow the viewer's theme instead, use `<picture>` with `prefers-color-scheme` sources — GitHub's documented mechanism — and confirm on the rendered page that the dark source loads rather than assuming the relative `srcset` is rewritten for you.
- GitHub serves repository images through a CDN cache, so a committed change can keep rendering the old file for a while. Keep the relative path — it survives forks and branches — and confirm on github.com that the new file is what renders once the change is pushed. Pointing `<img src>` at a commit's raw URL is a last resort for a banner that must update the moment it lands: it is an absolute URL that breaks the relative-link rule and has to be edited by hand at every banner change.
- For a project with translated variants, one banner in the base README's language unless the user asks for one per variant.

### Render check

Look at the SVG before delivering, in the reader's context rather than your own: a wrapper page exactly as wide as the `viewBox` renders at scale 1, with your fonts, without `max-width`, over a page background instead of the theme, and hides every failure below.

Reference the SVG through `<img>` — never inlined — with `img { max-width: 100% }`, inside a container about 1000 px wide and again about 360 px wide, each on a white page and a `#0d1117` page. Screenshot all four — Chrome and Edge both take `--headless=new --disable-gpu --hide-scrollbars --window-size=<width>,<height> --screenshot=<out.png> <file.html>`, the window at least as wide as the container — or open it in the browser preview when the host provides one, and read the images.

Then check that no text crosses the edge of its card, column, or the canvas; that the name is the heaviest element; that every text meets the thresholds above; that the canvas is not a quarter empty; and the domain glance — name the one element a reader from the domain recognises in two seconds, and if the honest answer is "the colour" or "the name", the banner is a template and goes back to the proposal. The four combinations add three checks:

- At the desktop width every text clears the size and contrast thresholds. At the phone width the banner is a strip: the name and the composition must hold, not every caption, because a caption sized for the desktop cannot survive 0.3 px per unit. If the name itself stops reading, it was sized for your screen, not the reader's.
- On the `#0d1117` page nothing has lost its ground, which is where a missing covering `<rect>` shows.
- The columns of a mockup still line up, which is where a missing `xml:space="preserve"` shows.

Fix and render again until it passes; two or three rounds are normal. Even this page cannot reproduce GitHub's stylesheet, its image proxy, or its cache, so the last look is on github.com: when the change is already pushed, open the README — or the raw asset URL — there once; when it is not, which is the usual case before delivery, record under **Unrun checks** that no GitHub-side render was seen and what would unblock it. With no renderer available at all, verify every line against the fitting table and every text pair against the contrast ratio by arithmetic, and record that too.

## One figure per concept

Each major concept section — how the tool works, how the components fit, what the lifecycle is — opens with a figure followed by prose that states the same facts. Two ways to draw one; a page may mix them under one palette:

| Way | Reach for it when | Cost and reach |
| --- | --- | --- |
| Mermaid in the Markdown | The concept is a flow, a sequence, or a state machine, and a themed default rendering says it well | Cheapest; diffs with the text; renders on GitHub and GitLab, not on npm, PyPI, or crates.io pages |
| Hand-drawn SVG in `assets/` | The concept deserves a designed panel — an architecture with boundaries and labelled flows, a tiered index with its costs, a request path across processes — in the banner's own palette | More work; same render check and fitting rules as the banner; renders everywhere an image does |

Either way the shape follows the concept:

| Concept | Shape |
| --- | --- |
| Pipeline, loop, or workflow | Steps left to right; a decision as a diamond; a loop as an edge back to the start |
| Tiers, layers, or a timeline | Left to right in the order they complete, each with its cost or duration |
| Components and their boundaries | One region per service, package, or layer; edges labelled with what flows |
| Request or message exchange | One lane per real process; messages named after the actual call or event |
| Lifecycle or mode transitions | States named as the code names them |

### Theme Mermaid to the palette

Open each Mermaid diagram with an init directive carrying the palette, and give nodes a class by role, so every diagram on the page reads as one set and matches the banner:

```mermaid
%%{init: {"theme": "base", "themeVariables": {
  "primaryColor": "#fff7ed", "primaryTextColor": "#0b1220", "primaryBorderColor": "#f97316",
  "lineColor": "#64748b", "secondaryColor": "#f1f5f9", "tertiaryColor": "#e2e8f0",
  "fontFamily": "system-ui, -apple-system, Segoe UI, Roboto, sans-serif"}}}%%
flowchart LR
    classDef step fill:#fff7ed,stroke:#f97316,color:#0b1220,stroke-width:2px
    classDef gate fill:#fef3c7,stroke:#d97706,color:#0b1220
    classDef keep fill:#dcfce7,stroke:#16a34a,color:#0b1220
    classDef drop fill:#fee2e2,stroke:#dc2626,color:#0b1220

    A[1. Evaluate]:::step -->|score| B[2. Propose change]:::step
    B -->|patch| C[3. Run checks]:::step
    C --> D{Improved?}:::gate
    D -- yes --> E[Keep · git commit]:::keep
    D -- no --> F[Revert · git revert]:::drop
    E --> A
    F --> A
```

- `primaryColor` is a light tint of the accent (`#fff7ed` for orange, `#ecfdf5` emerald, `#f0f9ff` sky, `#f5f3ff` violet); `primaryBorderColor` is the accent itself. Substitute both when the accent changes.
- Three or four `classDef` roles per page at most — for example step, gate, storage, external — reused across every diagram so the same colour means the same thing everywhere.
- For `sequenceDiagram`, set `actorBkg`, `actorBorder`, and `signalColor` in the same directive; for `stateDiagram-v2`, `primaryColor` and `primaryBorderColor` are enough.

### Richness floor

A figure earns its place when it shows something the prose beside it cannot show as quickly. The floor: **at least four nodes, and at least one edge label or region.** Three boxes in a row, or three boxes stacked, is a list wearing a diagram's clothes — either enrich it with what the evidence contains (what flows on each edge, which boundary each node sits in, the cost of each tier) or drop it and keep the table.

### Rules for every figure

- Every node, lane, region, and state maps to something recorded in the evidence inventory: a directory, module, service, command, CI job, or documented step. A box that exists only to balance the picture is invented content.
- Edges say what flows: a call name, a file type, a message, a token. A bare arrow between two named boxes is the minimum, not the norm.
- Eight nodes or fewer. When a concept needs more, it belongs in `ARCHITECTURE.md`, and the README figure shows only the top level.
- Labels in the README's language; identifiers (`src/cli/`, `POST /jobs`) stay as written in code.
- The prose beside the figure is complete on its own, so a renderer that drops the figure still tells the reader the same thing.
- A chart or figure that already exists in the repository is used instead of a new one when it matches the current code; when it has drifted, report the drift and draw the current version.
- A hand-drawn SVG has its own budget: `viewBox` 1200 units wide, as tall as the content needs (300–600 is the usual range), the same margins, fitting rules, legibility thresholds, and rendering constraints as the banner — a covering ground rect, `xml:space="preserve"` wherever alignment depends on spaces, pinned lines where overflow would break the figure — the same node ceiling as any figure, and the same render check at its own height before delivery. Raster images are not produced.

## Feature cards

The Highlights or Features section becomes a card grid instead of a bullet list. GitHub renders an HTML table; each cell is one card: a glyph, a bold title, one sentence. The title carries the meaning; the glyph is a visual anchor only, so the existing emoji rule holds.

```html
<table>
  <tr>
    <td align="center" width="33%">
      <h3>⚡ IL metadata index</h3>
      <sub>~100 k symbols in seconds, with full inheritance chains and real type signatures.</sub>
    </td>
    <td align="center" width="33%">
      <h3>🧪 Isolated test sessions</h3>
      <sub>Temporary save folder and linked mods; your real saves and settings are never touched.</sub>
    </td>
    <td align="center" width="33%">
      <h3>🔒 Local only</h3>
      <sub>No network calls; game files, indexes, and diagnostics stay on your machine.</sub>
    </td>
  </tr>
</table>
```

- Three columns on a page of six or nine features; two columns for four. A single leftover feature becomes prose under the grid, never a lone cell.
- One glyph per card, distinct across the grid; pick from a small set (⚡ speed, 🧪 testing, 🔒 security, 🧩 extensibility, 📦 packaging, 🔍 search, 🛠 build, 🌐 platforms) so the grid reads as a system rather than a sticker sheet.
- Every sentence is a fact the evidence inventory holds — a number, a mechanism, a guarantee — not an adjective.

## Collapsed reference

Long reference tables — a tool or command catalogue, environment variables, configuration keys — go inside `<details>`, with the count and the grouping in the summary so the page keeps its rhythm and a scanning reader still gets the number:

````markdown
<details>
<summary><b>18 tools in 4 groups</b> — research · installed mods · build · testing</summary>

### Researching the game

| Tool | Purpose |
| --- | --- |
| `rimworld_status` | Detected paths and index state. |
| … | … |

</details>
````

- The blank line after `<summary>` and before `</details>` is required, or the Markdown inside will not render.
- Collapse a table when it has more than eight rows or when there are two or more such tables in a row; a single short table stays open.
- Getting Started, configuration a reader must set, and security notes are never collapsed.

## Section rhythm

- Separate top-level sections with `---` so each concept reads as its own panel.
- Each panel opens with its visual — diagram, card grid, or collapsed summary — followed by prose; a panel that is only prose is fine when the concept has no shape, but two in a row means a diagram or grid was missed.
- At most one admonition per screen, reserved for the fact a reader must not miss; a page of callouts has none.
- Headings stay plain text. Emoji in headings only when the repository's existing documents already use them.
- The cognitive funnel is unchanged: the header block and the first diagram must still lead the reader to the smallest runnable example before any architecture.

## What showcase never does

- Adds a banner, hero, diagram, or card grid when the user chose plain, or did not answer.
- Draws a component, step, or flow the code does not contain, puts a number in the banner or a card that was not counted from the repository, or shows output in a mockup that the program does not print, or stitches real lines from different commands into one session.
- Replaces the Getting Started commands with a picture of them.
- Restores a license badge or License section.
- Imports fonts, scripts, or images from outside the repository into the banner.
