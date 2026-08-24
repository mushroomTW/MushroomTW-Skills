# README Quality Checklist

## Reader and content

- [ ] The opening sentence explains the project's purpose and target reader.
- [ ] A reader can quickly decide whether the project fits their needs.
- [ ] Important context, terminology, and external dependencies have reliable links.
- [ ] The content is an entry point, not an unstructured complete manual.
- [ ] The section set matches the project size; there are no empty or repetitive sections.

## Smallest successful path

- [ ] Prerequisites are clear.
- [ ] Installation and startup commands have evidence in the repository.
- [ ] There is at least one minimal usage example.
- [ ] The example includes input, execution, and expected output or result.
- [ ] Required environment variables, external services, and database setup are documented.
- [ ] Unverified steps are marked with `TODO:` or reported as gaps.

## Technical accuracy

- [ ] The stack, directory structure, API, CLI options, and versions are not obviously stale.
- [ ] API or CLI documentation covers optional parameters, defaults, types, return values, and errors.
- [ ] Architecture diagrams or descriptions match the current code.
- [ ] Local links, images, GIFs, videos, and example files exist.
- [ ] The table of contents and heading anchors work.
- [ ] Translated README variants carry the same content, or the divergence is reported.

## Adoption risk

- [ ] Limitations, compatibility, known issues, and security notes are disclosed early.
- [ ] The license type matches the LICENSE file.
- [ ] Badges and screenshots have actual value and do not carry the only copy of important information.
- [ ] Badges use a dynamic source where one exists; any hard-coded value records where it came from.
- [ ] Author details, contact information, contribution instructions, and roadmap items are confirmed.

## Writing quality

- [ ] The prose uses concrete nouns and verbs instead of vague marketing language.
- [ ] User-facing information appears before implementation detail.
- [ ] Markdown headings, code blocks, tables, and lists are consistent.
- [ ] All badges share one shields.io style and read as a single row.
- [ ] The same fact is not duplicated in multiple places where it can drift.
- [ ] Important content is not hidden in images or network-only badges.
- [ ] Emoji are sparse and never carry meaning on their own.
- [ ] Prerequisites, warnings, and limitations a reader must not miss use GitHub admonition syntax rather than plain paragraphs.
