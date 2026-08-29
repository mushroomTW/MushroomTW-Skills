# Excellent README

**English** | [繁體中文](excellent-readme.zh.md)

> This document lives in `docs/`. The skill itself is at [`excellent-readme/SKILL.md`](../excellent-readme/SKILL.md).

An installable skill for Codex and Claude Code that creates, improves, audits, and synchronizes `README.md` files using evidence from the repository.

It treats a README as a project entry point: help readers decide whether the project fits their needs, then give them a small, copyable, verified path to success. Every feature, command, version, configuration detail, and link must be traceable to repository evidence. Unknown information is disclosed instead of guessed.

## Quick Start

Invoke the skill explicitly in Codex:

```text
$excellent-readme Improve this repository's README using its actual contents, and verify every installation and usage command.
```

Invoke the skill in Claude Code:

```text
/excellent-readme Improve this repository's README using its actual contents, and verify every installation and usage command.
```

Both products may also load the skill automatically when a request matches its description. The expected result is a README sized to the project, followed by a summary of verified items, checks that were not run, and missing information.

## Features

- Supports create, improve, audit, and synchronize workflows.
- Builds an evidence inventory from source code, manifests, tests, configuration, and existing documentation before writing.
- Organizes content around the reader's adoption decisions instead of the implementation order.
- Verifies installation, startup, test, example, path, and local-link claims.
- Adapts the README structure to CLIs, libraries, services, frontends, and research tools.
- Keeps translated README variants aligned, or reports the divergence when it cannot.
- Asks the user or reports evidence gaps in the delivery summary instead of shipping `TODO:` placeholders or inventing claims.

## How It Works

1. Identify the README language, audience, purpose, and output path.
2. Build an evidence inventory from source code, manifests, tests, configuration, examples, and existing documentation.
3. Select only the sections that help readers understand or adopt this type of project.
4. Draft from purpose and a minimal example toward installation, configuration, limitations, and maintenance details.
5. Check that commands, links, headings, assets, and examples are traceable and runnable.
6. Review the result as a first-time reader and report validation results and information gaps.

The complete workflow is in [`SKILL.md`](../excellent-readme/SKILL.md). Its README framework, delivery checklist, and style exemplars are in the skill's [`references/`](../excellent-readme/references/) directory.

## Canonical Skill Location

The only skill entry point is [`SKILL.md`](../excellent-readme/SKILL.md). Its supporting files stay beside it in the same directory:

```text
excellent-readme/
├── SKILL.md
├── agents/openai.yaml
├── references/
└── scripts/validate_readme.py
```

Do not duplicate this skill elsewhere in the repository. Installation copies this single directory, so there is one maintained source of instructions.

## Validation

The included static checker uses only the Python standard library. It checks for unfinished markers, empty link targets, broken local links, and prose that points readers at a nonexistent license file, ignoring code blocks and inline code. Judging whether a section is present and useful stays with the quality checklist, not with keyword matching:

```powershell
python scripts/validate_readme.py README.md --project .
```

A successful run prints:

```text
README static checks passed.
```

> [!NOTE]
> The README checker performs static checks only. It does not replace executing documented commands, testing external links, or reviewing the document as a reader.

## Project Structure

```text
excellent-readme/
├── SKILL.md                         # Core instructions and trigger scope
├── agents/openai.yaml               # Codex UI metadata and default prompt
├── references/                      # Framework, checklist, and exemplars
└── scripts/                         # README static checker
```

## Limitations

- This skill does not replace a complete API reference, documentation website, tutorial collection, or unrelated article-writing workflow.
- Validation quality depends on the source code, configuration, documentation, and tools available in the repository.
- Checks that require network access, credentials, paid services, or data mutations still require appropriate authorization.
- This repository does not currently include license terms. Do not assume permission to use, modify, or redistribute it until a `LICENSE` is added.

## Install

This directory is the skill itself. Copy it into the host's skills directory:

| Host | Personal scope | Project scope |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/` | `<repo>/.claude/skills/` |
| Codex | `~/.codex/skills/` | — |

```powershell
$dest = "$HOME/.claude/skills/excellent-readme"
Remove-Item -Recurse -Force $dest -ErrorAction SilentlyContinue
Copy-Item -Recurse excellent-readme $dest
```

```powershell
$dest = "$HOME/.codex/skills/excellent-readme"
Remove-Item -Recurse -Force $dest -ErrorAction SilentlyContinue
Copy-Item -Recurse excellent-readme $dest
```

The `Remove-Item` line makes the same commands work for a reinstall: without it, `Copy-Item` nests a second copy inside the existing skill directory. To install the skill for one repository instead of the whole account, use that repository's `.claude/skills/` as the destination (Claude Code).

> [!NOTE]
> Both hosts read their skills directories when a session starts, so start a new session after copying.

## Development and Contributions

After changing the skill, test the create, improve, and audit workflows against a real repository, then rerun the static checker above against both READMEs. Before committing, confirm that every new command, feature, and link has supporting repository evidence.
