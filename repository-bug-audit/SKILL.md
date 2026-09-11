---
name: repository-bug-audit
disable-model-invocation: true
description: Whole-repository bug hunt and engineering-risk audit with one validated Markdown report.
---

# Repository Bug Audit

Audit the current working tree by finding material bugs first, then assess broader engineering quality in Comprehensive mode. Deliver exactly one artifact: a concise Markdown report. The evidence JSON behind it is a validation input, deleted when the run ends. Remain read-only except for those two files.

## Required startup choices

This skill runs only when invoked by name.

The one choice is **audit mode** — **Rapid** (map whole repo, read core/high-risk paths, only `defect`/`risk`, no score) or **Comprehensive** (read every in-scope file, all three finding types, 0–100 score). Execution mode is fixed: **Multi-agent partitioned** (one subagent per partition, cross-reviews High findings; see [platform-adapters](references/platform-adapters.md)).

🔴 **CHECKPOINT — Obtain confirmation for the choice before entering Workflow**: Ask in one interaction (skip what the user already stated). Follow [platform-adapters](references/platform-adapters.md) for the host's choice UI. If Multi-agent is unavailable, explain and 🛑 STOP. The audit runs multi-agent or not at all.

## Workflow

1. **Select modes** — In: user request; Out: `audit_mode`+`review_mode=multi-agent`; Format: single `AskUserQuestion` (skip if already answered).
2. **Build map & inventory** — In: `AGENTS.md`/`README`/manifests/CI; Out: `inventory[]` (`path`,`status`,`risk_tier`,`reason`); Scope is the entire working tree, not `git diff`/history.
3. **Trace flows** — In: `core|high` items; Out: `core_flows[]` (`name`,`entry_point`,`status`,`evidence[]`); Every known core/high must be traced.
4. **Run checks** — In: configured commands; Out: `verification_checks[]` (`status=passed|failed|not_run|unavailable`); Run only configured commands — no tool installs, no written probes; `reproduced` only from executed configured checks.
5. **Write evidence** — In: `schema.json`+`audit-protocol.md §1,2,5`; Out: `.docs/<report-stem>.evidence.json` (12 required fields), a validation input only; carry excerpts and paths, leaving secrets and full sources out.
6. **Write report** — In: evidence; Out: `.docs/<report>.md` exactly 4 sections (§4), render severity as `🔴/🟡/🟢`, written from evidence rather than copied from JSON.
7. **Validate & fix** — In: the validator command in **Validate and deliver**; Out: exit 0/1/2; Fix, delete the evidence file, then return the report link + a short summary.

Rules: validator checks structure/policy, not truth — rule out alternatives by reading implementation, major callers/callees, config, and tests.

## Failure handling

| Trigger | Recovery | Terminal condition |
|---|---|---|
| Configured check unavailable | Record `status=unavailable` and disclose the lost signal in `Limitations` | Continue; Comprehensive confidence cannot be High without one `passed` check |
| One partition agent fails | Reassign that unchanged partition once to a fresh agent | If no replacement can run, Multi-agent is unavailable → 🛑 STOP before conclusions |
| Multi-agent capability unavailable | Explain that partitioning and High cross-review cannot be performed | 🛑 STOP; never run or claim a single-agent audit |
| Comprehensive cannot read every file within budget | Repartition once; if still infeasible, request confirmation to narrow to `core|high` | On approval, set `provisional=true` and mark every unread item `mapped` with a reason; on rejection, 🛑 STOP |
| `.docs/` report already exists | Add one `YYYYMMDD-HHMMSS` suffix to the report, and the same stem to the evidence file | Continue without overwriting |
| Inventory has no `core|high` | Re-evaluate tiers once from entry points, trust boundaries, state, and deployment paths | If still empty, 🛑 STOP as invalid inventory; never invent a tier or produce artifacts the validator must reject |
| Validator exits 1 | Correct only the reported artifact violations, then rerun | Do not deliver until exit 0 |
| Validator exits 2 | Correct a deterministic path, encoding, or I/O error and retry once | If unresolved, 🛑 STOP without artifact links |
| `jsonschema` is unavailable | State that validation cannot run and name the missing prerequisite | 🛑 STOP without artifact links; never install it within the audit |

## Scope & inventory

Build the map per `references/audit-protocol.md §5`:

- every item: `read` / `mapped` / `excluded` / `unreadable` + `risk_tier` `core/high/standard/low`; at least one in-scope item is `core`/`high`; core/high coverage gates confidence.
- Rapid may leave `mapped`; Comprehensive only in `provisional` with `reason`. Details → `references/audit-protocol.md`.

Establish callers and callees by reading the implementation and searching the tree; a search miss means "Not found within the reviewed scope" (do not claim absent/secure/unused from it alone).

## Priorities & findings

Prioritize contract mismatches, boundaries/partial failures/timeouts, state/consistency/concurrency, trust boundaries, unbounded work/N+1, and observable assertions. Scanner/TODO/complexity are signals only — read implementation, callers, config, tests before filing.

Finding bars (→ `references/audit-protocol.md §1`): `defect` ≥7 `observed`/`reproduced` `confirmed`; `risk` needs `preconditions`+`verification`; `quality-debt` only Comprehensive. Deduplicate by root cause; severity `High/Medium/Low` (report `🔴/🟡/🟢`).

## Artifacts

Deliver one Markdown report in `.docs/` (create if missing):

| Mode | Report |
|---|---|
| Rapid | `.docs/repository-bug-audit-rapid-report.md` |
| Comprehensive | `.docs/repository-bug-audit-report.md` |

The evidence file sits beside it as `<report-stem>.evidence.json` only while the validator needs it — the validator requires that name and a `.docs/` parent. Delete it once the run ends, whether validation passed or the run stopped; it stays invisible to the reader (unlinked, unmentioned).

## Prohibitions — Do Not

- Modify code, config, tests, or external systems (unless explicitly requested); stay read-only except the two artifacts
- Install analyzers/dependencies or write reproduction probes; `reproduced` comes only from executed configured checks
- Narrow scope to `git diff`/history, or claim fixed/tested/secure from a search miss; scope is the working tree, and search misses are reported as "Not found within the reviewed scope"
- Overwrite `.docs/` artifacts, publish the evidence JSON, or write secrets/full sources; deliver one report link + short summary and delete the evidence file when the run ends

## Validate and deliver

🔴 **CHECKPOINT — Deliver only on validation exit 0**: Return links only after exit 0. Obtain confirmation before narrowing scope and mark `provisional`.

```text
python -X utf8 <skill-directory>/scripts/validate_bug_audit.py --evidence <evidence.json> --report <report.md>
# --repo-root <path> when artifacts are outside the audited tree
```

Requires a preinstalled `jsonschema`. Resolve `<skill-directory>` per [platform-adapters](references/platform-adapters.md); quote paths. Validator checks coverage recomputation, caps, ordering, and that every `inventory`/`location` path exists. Exit 0 = pass, 1 = content violation, 2 = I/O. Follow the failure matrix for nonzero exits or a missing prerequisite. 🛑 STOP: without exit 0 there is no delivery; after exit 0 delete the evidence file and return the report link + a short summary.
