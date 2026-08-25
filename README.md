# Excellent README

**English** | [繁體中文](README_ZH.md)

An installable skill for Codex and Claude Code that creates, improves, audits, and synchronizes `README.md` files using evidence from the repository.

It treats a README as a project entry point: help readers decide whether the project fits their needs, then give them a small, copyable, verified path to success. Every feature, command, version, configuration detail, and link must be traceable to repository evidence. Unknown information is disclosed instead of guessed.

## Quick Start

Invoke the skill explicitly in Codex:

```text
$excellent-readme Improve this repository's README using its actual contents, and verify every installation and usage command.
```

Run the namespaced skill in Claude Code:

```text
/excellent-readme:excellent-readme Improve this repository's README using its actual contents, and verify every installation and usage command.
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

## Install from the Marketplace

This repository contains self-hosted marketplace catalogs for Codex and Claude Code. Add the GitHub marketplace first, then install the `excellent-readme` plugin.

### Codex

```powershell
codex plugin marketplace add mushroomTW/excellent-readme
codex plugin add excellent-readme@mushroomtw-skills
```

### Claude Code

```powershell
claude plugin marketplace add mushroomTW/excellent-readme
claude plugin install excellent-readme@mushroomtw-skills
```

> [!IMPORTANT]
> The GitHub repository must be readable by the machine performing the installation. Configure the appropriate Git credentials before installing from a private repository.

Both catalogs install the same plugin directory, so the skill instructions, references, and validation script have a single source of truth. The package follows the official [OpenAI Build plugins](https://learn.chatgpt.com/docs/build-plugins) and [Claude Code plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces) documentation.

## Canonical Skill Location

The only skill entry point is [`SKILL.md`](plugins/excellent-readme/skills/excellent-readme/SKILL.md). Its supporting files stay beside it in the same directory:

```text
plugins/excellent-readme/skills/excellent-readme/
├── SKILL.md
├── agents/openai.yaml
├── references/
└── scripts/validate_readme.py
```

Do not copy this skill to the repository root. Both marketplaces install the plugin containing this directory, so there is one maintained source of instructions.

## How It Works

1. Identify the README language, audience, purpose, and output path.
2. Build an evidence inventory from source code, manifests, tests, configuration, examples, and existing documentation.
3. Select only the sections that help readers understand or adopt this type of project.
4. Draft from purpose and a minimal example toward installation, configuration, limitations, and maintenance details.
5. Check that commands, links, headings, assets, and examples are traceable and runnable.
6. Review the result as a first-time reader and report validation results and information gaps.

The complete workflow is in [`SKILL.md`](plugins/excellent-readme/skills/excellent-readme/SKILL.md). Its README framework, delivery checklist, and style exemplars are in the skill's [`references/`](plugins/excellent-readme/skills/excellent-readme/references/) directory.

## Validation

The included static checker uses only the Python standard library. It checks for unfinished markers, empty link targets, broken local links, and prose that points readers at a nonexistent license file, ignoring code blocks and inline code. Judging whether a section is present and useful stays with the quality checklist, not with keyword matching:

```powershell
python plugins/excellent-readme/skills/excellent-readme/scripts/validate_readme.py README.md --project .
```

A successful run prints:

```text
README static checks passed.
```

Validate both plugin manifests and marketplace catalogs with:

```powershell
claude plugin validate .
python C:/Users/<user>/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/excellent-readme
```

> [!NOTE]
> The README checker performs static checks only. It does not replace executing documented commands, testing external links, or reviewing the document as a reader. The Codex validator path depends on the local Codex installation.

## Does It Work? An Eight-README Experiment

One test project — a FastAPI + WebSocket Werewolf game with no README, no LICENSE, and a booby-trapped configuration (a hardcoded placeholder API key that looks like it should be an environment variable) — was given to four Claude models (Haiku 4.5, Sonnet 5, Opus 5, Fable 5) twice each: once following this skill, once with the skill explicitly forbidden. All eight verbatim outputs and the full comparison live in [docs/experiment/](docs/experiment/README.md) (report in Traditional Chinese).

- For the small model, the skill fixed hard errors: a dependency-incomplete install command, the directory name used as the project title, and quick start buried behind ten other sections.
- For the frontier models, the facts were already right; the skill changed delivery discipline — funnel ordering, gaps disclosed as plain facts instead of papered over, badges only where one answers a real question, and staying in documentation scope.
- The most stable signal across all eight runs: every skill run proactively executed verification checks; every baseline ran none.
- Verified by hand across all four skill runs: zero `TODO:` placeholders, zero decorative badges, honest license disclosure, and stated audience assumptions.
- One honest caveat, since fixed: an earlier version's section framework tempted the small model into inventing a license reference. The placeholder rule that invited it was removed in v1.5.0, and the re-run confirms the fabrication is gone — but a section framework can invite the very filler it is meant to prevent.
- A second experiment runs the same design against [a trap project committed to this repository](docs/experiment/fixture/), so anyone can reproduce it. Nine deliberate traps; trap scores are machine-checked rather than self-reported. It found that the skill blocked *invented* claims but not *inherited* ones — an unbacked `MIT` line survived from the original README — which is what v1.8.1 fixes.

## Project Structure

```text
excellent-readme/
├── .claude-plugin/
│   └── marketplace.json                 # Claude Code marketplace catalog
├── .agents/plugins/
│   └── marketplace.json                 # Codex marketplace catalog
├── docs/experiment/                     # Model experiments: exhibits, report, reproducible fixture
├── plugins/excellent-readme/
│   ├── .claude-plugin/plugin.json       # Claude Code plugin manifest
│   ├── .codex-plugin/plugin.json        # Codex plugin manifest
│   └── skills/excellent-readme/
│       ├── SKILL.md                     # Core instructions and trigger scope
│       ├── agents/openai.yaml           # Codex UI metadata and default prompt
│       ├── references/                  # Framework, checklist, and exemplars
│       └── scripts/                     # README static checker
├── README.md                            # English documentation
└── README_ZH.md                         # Traditional Chinese documentation
```

## Limitations

- This skill does not replace a complete API reference, documentation website, tutorial collection, or unrelated article-writing workflow.
- Validation quality depends on the source code, configuration, documentation, and tools available in the repository.
- Checks that require network access, credentials, paid services, or data mutations still require appropriate authorization.
- This repository does not currently include license terms. Do not assume permission to use, modify, or redistribute it until a `LICENSE` is added.
- This repository provides self-hosted marketplaces that users can add directly. Listings in the official OpenAI or Anthropic public marketplace require separate submission and platform review.

## Development and Contributions

After changing the skill or either manifest, test the create, improve, and audit workflows against a real repository, then rerun the three validation commands above. Before committing, confirm that every new command, feature, and link has supporting repository evidence.
