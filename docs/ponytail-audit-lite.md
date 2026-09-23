# Ponytail Audit Lite

**English** | [繁體中文](ponytail-audit-lite.zh.md)

> This document lives in `docs/`. The skill itself is at [`ponytail-audit-lite/SKILL.md`](../ponytail-audit-lite/SKILL.md).

A one-shot audit that scans a whole repository for over-engineering and returns a ranked table of what to delete, simplify, or replace with a standard-library or platform equivalent. It reports; it does not edit.

## Origin

Adapted from the `ponytail-audit` skill in [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) (MIT, Copyright (c) 2026 DietrichGebert). The upstream license ships inside the skill directory as [`ponytail-audit-lite/LICENSE`](../ponytail-audit-lite/LICENSE), so it travels with every install.

Differences from upstream:

- **Manual trigger only.** The frontmatter declares `disable-model-invocation: true` and the trigger phrases were dropped from `description`, so the host never fires it on its own. Invoke it by name (`/ponytail-audit-lite`).
- **Standalone.** References to the companion `ponytail-review` skill and the "stop ponytail-audit" mode switch were removed; the tag list is spelled out in full.
- **Table output.** Findings come back as a Markdown table instead of one line each.

## When It Applies

Only when you invoke it. Use it on a whole codebase, not a diff. Correctness bugs, security holes, and performance problems are out of scope; route those to a normal review.

## What It Hunts

Dependencies the standard library or platform already ships, single-implementation interfaces, factories with one product, wrappers that only delegate, files exporting one thing, dead flags and config, hand-rolled standard-library functions.

Each finding carries one tag:

| Tag | Meaning |
| --- | --- |
| `delete:` | Dead code, unused flexibility, speculative feature. Replacement: nothing. |
| `stdlib:` | Hand-rolled thing the standard library ships; names the function. |
| `native:` | Dependency or code doing what the platform already does; names the feature. |
| `yagni:` | Abstraction with one implementation, config nobody sets, layer with one caller. |
| `shrink:` | Same logic, fewer lines; shows the shorter form. |

## Output

A Markdown table ranked biggest cut first, followed by an estimated total:

```md
| # | Tag | Cut | Replacement | Path |
|---|-----|-----|-------------|------|
| 1 | `yagni:` | <what to cut> | <replacement> | `<path>` |

net: -<N> lines, -<M> deps possible.
```

When there is nothing to cut, it prints no table, only `Lean already. Ship.`

## Install

From the repository root, let the `skills` CLI discover supported agents and install this skill:

```bash
npx skills add . --skill ponytail-audit-lite
```

Add `--global` for personal scope; without it, the CLI installs at project scope. For a manual installation, copy `ponytail-audit-lite/` (including its `LICENSE`) to a skills directory documented by the host.

> [!NOTE]
> The first `npx` invocation may download the CLI. Reload or restart the host when it only discovers skills at session start.
