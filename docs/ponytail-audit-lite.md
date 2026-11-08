# Ponytail Audit Lite

**English** | [繁體中文](ponytail-audit-lite.zh.md)

> This document lives in `docs/`. The skill itself is at [`ponytail-audit-lite/SKILL.md`](../ponytail-audit-lite/SKILL.md).

A lightweight, one-shot audit that scans an entire repository for over-engineering and returns a ranked table of code to delete, simplify, or replace with standard-library or platform-native equivalents. It is strictly report-only and never modifies code.

## Origin

Adapted from the `ponytail-audit` skill in [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) (MIT License, Copyright (c) 2026 DietrichGebert). The upstream license is packaged within the skill directory at [`ponytail-audit-lite/LICENSE`](../ponytail-audit-lite/LICENSE) and accompanies every installation.

Key differences from upstream:

- **Manual Trigger Only**: The frontmatter declares `disable-model-invocation: true` for Claude Code, `agents/openai.yaml` specifies `policy.allow_implicit_invocation: false` for Codex, and auto-trigger phrases are removed from the description. Neither agent will invoke it unprompted; invoke explicitly via `/ponytail-audit-lite`.
- **Evidence-Based Tagging**: A finding is tagged `delete:` or `yagni:` only after an exhaustive repository-wide reference search. Code reached via reflection, dependency injection, framework conventions, main entry points, or published public APIs is never marked. Generated files, vendored code, and dependency folders are skipped automatically.
- **Self-Contained**: Removed all dependencies on the companion `ponytail-review` skill and mode-switching commands; the tag taxonomy is completely defined within this skill.
- **Structured Table Output**: Findings are consolidated into an easy-to-read Markdown table rather than single-line outputs.

## When It Applies

Applies only upon explicit manual invocation. Designed for whole-codebase audits rather than incremental PR diffs. Standard bugs, security vulnerabilities, and low-level performance bottlenecks are out of scope and should be handled by regular code review workflows.

## What It Hunts

- Dependencies that duplicate existing standard-library or platform capabilities
- Single-implementation interfaces and one-product factory patterns
- Thin wrappers that only forward calls without adding behavior
- Source files exporting only a single trivial helper
- Obsolete feature flags, unused configuration options, and dead logic branches
- Hand-rolled utilities replicating standard-library functions

Each finding is assigned exactly one tag:

| Tag | Category | Description |
| --- | --- | --- |
| `delete:` | Dead Code | Dead code, unused flexibility, or speculative features. Recommended replacement: delete entirely. |
| `stdlib:` | Standard Library | Hand-rolled functionality that the language standard library already provides; names the standard function. |
| `native:` | Platform Feature | Third-party dependency or code doing what the runtime platform already provides; names the platform capability. |
| `yagni:` | Speculative Abstraction | Abstractions with only one implementation, configurations nobody sets, or layers with only one caller. |
| `shrink:` | Code Simplification | Equivalent business logic achievable with significantly fewer lines; provides the concise replacement below the table. |

## Output Format

Outputs a Markdown table ranked by estimated lines saved (largest cuts first), followed by an estimated net reduction:

```md
| # | Tag | Cut | Replacement | Path |
|---|-----|-----|-------------|------|
| 1 | `yagni:` | <what to cut> | <replacement> | `<path>` |
| 2 | `shrink:` | <what to cut> | shorter form in #2 | `<path>` |

#2
<shorter form, as a fenced code block>

net: -<N> lines, -<M> deps possible.
```

- `N` represents the cumulative lines removed across all findings (including any omitted past the top 20 limit), calculated from actual file lengths.
- `M` represents the total count of external dependencies that can be dropped.
- If findings exceed 20, the table retains the top 20 highest-impact items and indicates how many additional findings were truncated.
- Table cells remain single-line. Multi-line code replacements for `shrink:` are indexed and displayed as numbered code blocks beneath the table.
- When the codebase is already lean and no over-engineering is found, the skill outputs only: `Lean already. Ship.`

## Install

From the repository root, use the `skills` CLI to discover supported agent hosts and install this skill:

```bash
npx skills add . --skill ponytail-audit-lite
```

Add `--global` for personal user scope; omitting it installs at project scope. For manual installation, copy `ponytail-audit-lite/` (including its `LICENSE`) directly into your agent host's configured skills directory.

> [!NOTE]
> The initial `npx` invocation may download the CLI. Reload or restart your agent host if it only discovers skills during session startup.
