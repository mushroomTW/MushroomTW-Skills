# Project Docs Quality Checklist

Apply **Reader and content** through **Writing quality** to every document you touched, reading each one as its own reader; apply **Document set** once to the whole set.

## Reader and content

- [ ] The opening sentence explains the project's purpose and target reader.
- [ ] The target audience was confirmed with the user when the evidence left it ambiguous.
- [ ] In create mode, the opening sentence is one the user picked or rewrote from the offered options.
- [ ] Translated variants exist only for languages the repository already had or the user chose.
- [ ] A reader can quickly decide whether the project fits their needs.
- [ ] Important context, terminology, and external dependencies have reliable links.
- [ ] The content is an entry point, not an unstructured complete manual.
- [ ] The section set matches the project size; there are no empty or repetitive sections.
- [ ] In improve mode, no existing section was removed outright without approval; rejected or pending removals are listed in the report.

## Smallest successful path

- [ ] Prerequisites are clear.
- [ ] Installation and startup commands have evidence in the repository.
- [ ] When several install or run channels exist, Getting Started leads with the one the user chose, or the assumption is disclosed.
- [ ] There is at least one minimal usage example.
- [ ] The example includes input, execution, and expected output or result.
- [ ] Required environment variables, external services, and database setup are documented.
- [ ] The README ships no `TODO:` or placeholder text; unverified steps and open questions live in the delivery report.
- [ ] User-decidable gaps (license, contacts, roadmap) were raised as questions when the user could answer; otherwise the section is omitted and the gap reported.

## Technical accuracy

- [ ] The stack, directory structure, API, CLI options, and versions are not obviously stale.
- [ ] API or CLI documentation covers optional parameters, defaults, types, return values, and errors.
- [ ] Architecture diagrams or descriptions match the current code.
- [ ] Local links, images, GIFs, videos, and example files exist.
- [ ] The table of contents and heading anchors work.
- [ ] Translated README variants carry the same content, or the divergence is reported.

## Adoption risk

- [ ] Limitations, compatibility, known issues, and security notes are disclosed early.
- [ ] A dormant or archived project discloses its maintenance status near the top.
- [ ] There is no License section or license badge unless the licensing needs explaining; when one exists, it is a single line whose SPDX identifier matches the LICENSE file.
- [ ] The user confirmed whether the README carries badges, logos, screenshots, or demos and which badge style; none were added or restyled without that answer.
- [ ] Badges and screenshots have actual value and do not carry the only copy of important information.
- [ ] Badges use a dynamic source where one exists; any hard-coded value records where it came from.
- [ ] Author details, contact information, contribution instructions, and roadmap items are confirmed.
- [ ] The README states where readers can ask questions and whether PRs are accepted.

## Writing quality

- [ ] The prose uses concrete nouns and verbs instead of vague marketing language.
- [ ] User-facing information appears before implementation detail.
- [ ] Markdown headings, code blocks, tables, and lists are consistent.
- [ ] All badges share one shields.io style and read as a single row.
- [ ] Showcase elements (header block, banner, facts line, figures, feature cards, collapsed tables, panel breaks) appear only when the user chose showcase.
- [ ] `validate_docs.py` was run on every touched document from the repository root, so its SVG, Mermaid, and HTML-spacing warnings covered the banner and figures; each warning was read and either fixed or explained in the report.
- [ ] In showcase, the style (accent, mood, domain cue, banner direction) was proposed from the project's own assets, artefacts, and concepts and chosen by the user at the checkpoint; the rendered banner was shown to the user as a PNG and accepted before the page was drafted; one palette runs through banner, figures, and cards; the banner follows a direction that fits the project, carries the name as its heaviest element plus a figure, mockup, or fact set that fails the swap test and an element a domain reader recognises at a glance (drawn, never a copied logo or asset), has its text fitted by the width rules, and was checked in a render (or the arithmetic check listed under unrun); a mockup shows only commands and output the program actually emits; every figure — Mermaid themed to the palette or hand-drawn SVG — meets the richness floor (four nodes plus an edge label or region) and maps every node to an evidence-inventory entry; every banner and card fact was counted or read from the repository; the prose beside each visual stands on its own; no SVG loads anything from outside the repository.
- [ ] The same fact is not duplicated in multiple places where it can drift.
- [ ] Important content is not hidden in images or network-only badges.
- [ ] Emoji are sparse and never carry meaning on their own.
- [ ] Prerequisites, warnings, and limitations a reader must not miss use GitHub admonition syntax rather than plain paragraphs.

## Document set

- [ ] Every companion document that exists is linked from the README, and links back to it.
- [ ] Every companion document the evidence justified was either created with approval, or listed as proposed in the delivery report.
- [ ] No fact (version, command, contact, supported platform) is owned by two documents.
- [ ] Companion documents sit where GitHub reads them: `.github/`, the root, or `docs/`; templates sit under `.github/`.
- [ ] `SECURITY.md`, `CONTRIBUTING.md`, and `CODE_OF_CONDUCT.md` name a channel or standard the evidence or the user confirmed.
- [ ] `CHANGELOG.md` entries trace to tags or commit ranges, and the file says whether it or GitHub Releases is canonical.
- [ ] `ARCHITECTURE.md` names components that exist and describes flow, not a file-by-file tour.
- [ ] Translated variants of companion documents follow the README's language set, or the asymmetry is reported.
