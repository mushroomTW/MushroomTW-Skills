---
name: repository-bug-audit
description: Perform evidence-driven, repository-wide bug discovery and engineering risk audits in either unscored Rapid mode or Comprehensive mode with a risk-weighted 0-100 quality score. Use when the user explicitly requests a whole-repository bug hunt, repository-wide risk review, overall engineering quality score, or complete technical-debt assessment. Do not use for a single file or module, a PR or diff review, one known bug or vulnerability, a localized performance issue, general coding questions, or a review of this skill itself.
---

# Repository Bug Audit

Audit the current working tree by finding material bugs first, then assess broader engineering quality in Comprehensive mode. Produce one concise Markdown report paired with one machine-readable evidence JSON. Remain read-only except for those two artifacts.

## Required startup choices

Ask both in one interaction (skip what the user already stated). Follow [platform-adapters](references/platform-adapters.md) for the host's choice UI. Never silently fall back.

1. **Audit mode** — **Rapid** (map whole repo, read core/high-risk paths, only `defect`/`risk`, no score) or **Comprehensive** (read every in-scope file, all three finding types, 0–100 score).
2. **Execution mode** — **Standard** or **Multi-agent partitioned** (partitions scope, cross-reviews High findings; see [platform-adapters](references/platform-adapters.md)).

## Workflow

1. Select modes → 2. Build repository map & inventory → 3. Trace core/high-risk flows → 4. Run only repo-configured checks → 5. Write evidence JSON (schema `references/bug-audit-evidence.schema.json`, protocol `references/audit-protocol.md`) → 6. Write Markdown report (`references/audit-protocol.md`) → 7. Validate & fix before delivery.

Rules: never install tools/deps; never write repro probes; only `reproduced` from repo-configured checks. Validator checks structure/policy, not truth — rule out alternatives by reading code/callers/config/tests.

## Scope & inventory

Use the entire working tree; never `git diff`/history. Build the map per `references/audit-protocol.md §5`:

- every item: `read` / `mapped` / `excluded` / `unreadable` + `risk_tier` `core/high/standard/low`; at least one in-scope item is `core`/`high`; core/high coverage gates confidence.
- Rapid may leave `mapped`; Comprehensive only in `provisional` with `reason`. Details → `references/audit-protocol.md`.

Prefer code-navigation tools (LSP/graph) over grep; a search miss = "Not found within the reviewed scope."

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

## Validate and deliver

```text
python -X utf8 <skill-directory>/scripts/validate_bug_audit.py --evidence <evidence.json> --report <report.md>
# --repo-root <path> when artifacts are outside the audited tree
```

Requires `jsonschema` (`pip install jsonschema`). Resolve `<skill-directory>` per [platform-adapters](references/platform-adapters.md); quote paths. Validator checks coverage recomputation, caps, ordering, and that every `inventory`/`location` path exists. Exit 0 = pass, 1 = content violation, 2 = I/O. Do not deliver unvalidated artifacts; return clickable links + short summary, not pasted artifacts.
