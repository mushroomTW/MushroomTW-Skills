---
name: repository-bug-audit
description: Perform evidence-driven, repository-wide bug discovery and engineering risk audits in either unscored Rapid mode or Comprehensive mode with a risk-weighted 0-100 quality score. Use when the user explicitly requests a whole-repository bug hunt, repository-wide risk review, overall engineering quality score, or complete technical-debt assessment. Do not use for a single file or module, a PR or diff review, one known bug or vulnerability, a localized performance issue, general coding questions, or a review of this skill itself.
---

# Repository Bug Audit

Audit the current working tree by finding material bugs first, then assess broader engineering quality in Comprehensive mode. Produce one concise Markdown report paired with one machine-readable evidence JSON. Remain read-only except for those two artifacts.

## Required startup choices

🔴 **CHECKPOINT — Obtain confirmation for both choices before entering Workflow**: Ask both in one interaction (skip what the user already stated). Follow [platform-adapters](references/platform-adapters.md) for the host's choice UI. If Multi-agent unavailable, explain and ask to switch to Standard. **Never silently fall back — 🛑 STOP and wait for user choice.**

1. **Audit mode** — **Rapid** (map whole repo, read core/high-risk paths, only `defect`/`risk`, no score) or **Comprehensive** (read every in-scope file, all three finding types, 0–100 score).
2. **Execution mode** — **Standard** or **Multi-agent partitioned** (partitions scope, cross-reviews High findings; see [platform-adapters](references/platform-adapters.md)).

## Workflow

1. **Select modes** — In: user request; Out: `audit_mode`+`review_mode`; Format: single `AskUserQuestion` with 2 questions (skip if already answered).
2. **Build map & inventory** — In: `AGENTS.md`/`README`/manifests/CI; Out: `inventory[]` (`path`,`status`,`risk_tier`,`reason`); Entire working tree, never use `git diff`/history.
3. **Trace flows** — In: `core|high` items; Out: `core_flows[]` (`name`,`entry_point`,`status`,`evidence[]`); Every known core/high must be traced.
4. **Run checks** — In: configured commands; Out: `verification_checks[]` (`status=passed|failed|not_run|unavailable`); Never install tools/write probes; `reproduced` only from executed configured checks.
5. **Write evidence** — In: `schema.json`+`audit-protocol.md §1,2,5`; Out: `.docs/<pair>.evidence.json` (12 required fields); Never include secrets/full sources.
6. **Write report** — In: evidence; Out: `.docs/<pair>.md` exactly 4 sections (§4), render severity as `🔴/🟡/🟢`, do not copy JSON.
7. **Validate & fix** — In: `python -X utf8 <skill-dir>/scripts/validate_bug_audit.py --evidence --report [--repo-root]`; Out: exit 0/1/2; Fix then return links + summary, never paste full artifacts.

Rules: validator checks structure/policy, not truth — rule out alternatives by reading implementation, major callers/callees, config, and tests.

## Failure handling — if-then

- **If checks unavailable** → `status=unavailable` + disclose in `Limitations`; Comprehensive High requires one `passed`.
- **If reading all files exceeds budget** → Switch to Multi-agent; if still infeasible, narrow to `core|high`, `provisional=true`, mark unread as `mapped`+`reason`.
- **If Multi-agent unavailable** → Explain and ask to switch to Standard; never silently downgrade.
- **If `.docs/` already exists** → Add same timestamp `YYYYMMDD-HHMMSS` to both; never overwrite.
- **If no `core|high`** → Treat as mis-tiering, requires at least one; re-evaluate §5 else `provisional`.

## Scope & inventory

Use the entire working tree; never `git diff`/history. Build the map per `references/audit-protocol.md §5`:

- every item: `read` / `mapped` / `excluded` / `unreadable` + `risk_tier` `core/high/standard/low`; at least one in-scope item is `core`/`high`; core/high coverage gates confidence.
- Rapid may leave `mapped`; Comprehensive only in `provisional` with `reason`. Details → `references/audit-protocol.md`.

Use LSP / code-graph for callers/callees; if unavailable, fallback to grep then mark as "Not found within the reviewed scope" (do not claim absent/secure/unused from a search miss alone).

## Priorities & findings

Prioritize contract mismatches, boundaries/partial failures/timeouts, state/consistency/concurrency, trust boundaries, unbounded work/N+1, and observable assertions. Scanner/TODO/complexity are signals only — read implementation, callers, config, tests before filing.

Finding bars (→ `references/audit-protocol.md §1`): `defect` ≥7 `observed`/`reproduced` `confirmed`; `risk` needs `preconditions`+`verification`; `quality-debt` only Comprehensive. Deduplicate by root cause; severity `High/Medium/Low` (report `🔴/🟡/🟢`).

## Artifacts

Write exactly one pair in `.docs/` (create if missing):

| Mode | Report | Evidence |
|---|---|---|
| Rapid | `.docs/repository-bug-audit-rapid-report.md` | `.docs/repository-bug-audit-rapid-report.evidence.json` |
| Comprehensive | `.docs/repository-bug-audit-report.md` | `.docs/repository-bug-audit-report.evidence.json` |

If either exists, add shared timestamp `YYYYMMDD-HHMMSS` to both; never overwrite. Keep Markdown concise, no secrets/full sources, no JSON appendix.

## Prohibitions — Do Not

- Single file / PR diff / single known vulnerability / single-point performance / general question — do not use this skill
- Modify code, config, tests, or external systems (unless explicitly requested)
- Install analyzers/dependencies or write reproduction probes; `reproduced` only from executed configured checks
- Narrow scope via `git diff`/history; claim fixed/tested/secure from a search miss
- Overwrite `.docs/` artifacts, copy JSON as appendix, or write secrets/full sources

## Validate and deliver

🔴 **CHECKPOINT — Do not deliver before validation**: Prohibit returning links before exit 0; if narrowing scope or switching mode, obtain user confirmation and mark `provisional`.

```text
python -X utf8 <skill-directory>/scripts/validate_bug_audit.py --evidence <evidence.json> --report <report.md>
# --repo-root <path> when artifacts are outside the audited tree
```

Requires `jsonschema` (`pip install jsonschema`). Resolve `<skill-directory>` per [platform-adapters](references/platform-adapters.md); quote paths. Validator checks coverage recomputation, caps, ordering, and that every `inventory`/`location` path exists. Exit 0 = pass, 1 = content violation, 2 = I/O. 🛑 STOP: Do not deliver unvalidated artifacts; return clickable links + short summary, not pasted artifacts.
