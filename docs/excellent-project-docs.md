# Excellent Project Docs

**English** | [繁體中文](excellent-project-docs.zh.md)

> This document lives in `docs/`. The skill itself is at [`excellent-project-docs/SKILL.md`](../excellent-project-docs/SKILL.md).

An installable skill for Codex and Claude Code that creates, improves, audits, and synchronizes a repository's documentation set — `README.md` plus the standard companion files GitHub reads from the root or `.github/` (`CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `SUPPORT.md`, `CHANGELOG.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `GOVERNANCE.md`, issue and pull request templates) — using evidence from the repository.

It treats the README as the hub and the companion files as satellites: the README helps readers decide whether the project fits their needs and gives them a small, copyable, verified path to success; each satellite owns one topic that would bloat the README, and the README links to it. Every feature, command, version, configuration detail, contact, and link must be traceable to repository evidence. Unknown information is disclosed instead of guessed.

## Quick Start

Invoke the skill explicitly in Codex:

```text
$excellent-project-docs Improve this repository's README using its actual contents, verify every installation and usage command, and tell me which companion documents the evidence justifies.
```

Invoke the skill in Claude Code:

```text
/excellent-project-docs Improve this repository's README using its actual contents, verify every installation and usage command, and tell me which companion documents the evidence justifies.
```

Both products may also load the skill automatically when a request matches its description. The expected result is a README sized to the project, any companion documents you approved at the proposal checkpoint, and a summary of verified items, checks that were not run, and missing information.

## Features

- Supports create, improve, audit, and synchronize workflows across the whole document set.
- Builds an evidence inventory from source code, manifests, tests, configuration, release history, and existing documentation before writing.
- Organizes content around the reader's adoption decisions instead of the implementation order.
- Decides which companion documents the evidence justifies, proposes them, and creates only the ones you approve; a document you name is handled directly.
- Keeps one owner per fact: the README summarizes and links, satellites do not restate the README, and contradictions between documents are resolved or reported.
- Treats presentation as your decision: asks which languages the document set carries, which badges, logo, or screenshots to include and in which style, which install channel leads Getting Started when several exist, and — when creating — which of two or three taglines opens the README.
- Leaves the license to the `LICENSE` file, which GitHub shows in the repository sidebar: no License section or badge in the README unless the licensing needs explaining (dual licensing, a non-OSI license, terms that differ by version), and then only a one-line SPDX identifier with a link.
- Verifies installation, startup, test, example, path, and local-link claims in every document it touches.
- Adapts the README structure to CLIs, libraries, services, frontends, and research tools.
- Keeps translated variants aligned, or reports the divergence when it cannot.
- Asks the user or reports evidence gaps in the delivery summary instead of shipping `TODO:` placeholders or inventing contribution rules, security contacts, or release history.

## How It Works

1. Identify the language, audience, purpose, target documents, and output paths.
2. Build an evidence inventory from source code, manifests, tests, configuration, examples, release history, and every existing companion document.
3. Select the README sections and the companion documents the evidence justifies; propose any new companion file, ask the presentation questions (badges and images, badge style, leading install channel, tagline), and wait for approval.
4. Draft each document from purpose and a minimal example toward installation, configuration, limitations, and maintenance details, with the README linking to every satellite.
5. Check that commands, links, headings, assets, and examples are traceable and runnable, and that no fact is owned by two documents.
6. Review each document as its first-time reader and report validation results, proposed-but-not-created files, and information gaps.

The complete workflow is in [`SKILL.md`](../excellent-project-docs/SKILL.md). Its README framework, companion-document rules, delivery checklist, and style exemplars are in the skill's [`references/`](../excellent-project-docs/references/) directory.

## Scope

In scope: `README.md` and the companion files listed above, wherever GitHub reads them (`.github/`, the repository root, or `docs/`). `LICENSE` is reported on, never written — choosing a license is your decision.

Out of scope: a complete API reference, a documentation website, the pages under `docs/`, and articles unrelated to a repository. The skill reads `docs/` as evidence and links to it; it does not author it.

## Canonical Skill Location

The only skill entry point is [`SKILL.md`](../excellent-project-docs/SKILL.md). Its supporting files stay beside it in the same directory:

```text
excellent-project-docs/
├── SKILL.md
├── agents/openai.yaml
├── references/
└── scripts/validate_docs.py
```

Do not duplicate this skill elsewhere in the repository. Installation copies this single directory, so there is one maintained source of instructions.

## Validation

The included static checker uses only the Python standard library. It accepts one or more Markdown documents and, for each, checks for unfinished markers, empty link targets, broken local links, and prose that points readers at a nonexistent license file, ignoring code blocks and inline code. Judging whether a section or a companion document is present and useful stays with the quality checklist, not with keyword matching:

```powershell
python scripts/validate_docs.py README.md CONTRIBUTING.md SECURITY.md --project .
```

A successful run prints one line per document:

```text
README.md: static checks passed.
CONTRIBUTING.md: static checks passed.
SECURITY.md: static checks passed.
```

> [!NOTE]
> The checker performs static checks only. It does not replace executing documented commands, testing external links, checking that every satellite is linked from the README, or reviewing each document as a reader.

## Project Structure

```text
excellent-project-docs/
├── SKILL.md                         # Core instructions and trigger scope
├── agents/openai.yaml               # Codex UI metadata and default prompt
├── references/                      # README framework, companion-document rules, checklist, exemplars
└── scripts/                         # Static checker for one or more documents
```

## Limitations

- This skill does not replace a complete API reference, documentation website, tutorial collection, or unrelated article-writing workflow.
- It does not write `LICENSE`, and it does not invent the content only you can supply: security contacts, contribution policy, code-of-conduct standard, roadmap.
- Validation quality depends on the source code, configuration, documentation, and tools available in the repository.
- Checks that require network access, credentials, paid services, or data mutations still require appropriate authorization.

## Install

From the repository root, let the `skills` CLI discover supported agents and install this skill:

```bash
npx skills add . --skill excellent-project-docs
```

Add `--global` for personal scope; without it, the CLI installs at project scope. For a manual installation, copy `excellent-project-docs/` to a skills directory documented by the host instead of assuming a runtime-specific path.

> [!NOTE]
> The first `npx` invocation may download the CLI. Reload or restart the host when it only discovers skills at session start.

## Development and Contributions

After changing the skill, test the create, improve, and audit workflows against a real repository — including one where a companion document is justified — then rerun the static checker above against both READMEs. Before committing, confirm that every new command, feature, and link has supporting repository evidence.
