---
name: repository-bug-audit
description: Perform evidence-driven, repository-wide bug discovery and engineering risk audits in either unscored Rapid mode or Comprehensive mode with a risk-weighted 0-100 quality score. Use when the user explicitly requests a whole-repository bug hunt, repository-wide risk review, overall engineering quality score, or complete technical-debt assessment. Do not use for a single file or module, a PR or diff review, one known bug or vulnerability, a localized performance issue, general coding questions, or a review of this skill itself.
---

# Repository Bug Audit

Audit the current working tree by finding material bugs first, then assess broader engineering quality in Comprehensive mode. Produce one concise Markdown report paired with one machine-readable evidence JSON. Remain read-only except for those two artifacts.

## Required startup choices

🔴 **CHECKPOINT — 取得雙選確認後才可進入 Workflow**：Ask both in one interaction (skip what the user already stated). Follow [platform-adapters](references/platform-adapters.md) for the host's choice UI. If Multi-agent unavailable, explain and ask to switch to Standard. **Never silently fall back — 🛑 STOP and wait for user choice.**

1. **Audit mode** — **Rapid** (map whole repo, read core/high-risk paths, only `defect`/`risk`, no score) or **Comprehensive** (read every in-scope file, all three finding types, 0–100 score).
2. **Execution mode** — **Standard** or **Multi-agent partitioned** (partitions scope, cross-reviews High findings; see [platform-adapters](references/platform-adapters.md)).

## Workflow

1. **Select modes** — Input: user request; Output: `audit_mode=rapid|comprehensive` + `execution.review_mode=standard|multi-agent`; Format: one `AskUserQuestion` with 2 questions (skip if already stated).
2. **Build repository map & inventory** — Input: `AGENTS.md`, `README`, manifests, CI; Output: `inventory[]` (`path`, `status=read|mapped|excluded|unreadable`, `risk_tier=core|high|standard|low`, `reason` when required) covering entire working tree; never use `git diff`/history.
3. **Trace core/high-risk flows** — Input: `inventory` items with `core|high`; Output: `core_flows[]` (`name`, `risk_tier`, `entry_point=path:symbol`, `status=traced|partial|untraced`, `evidence[]`); every known core/high flow must be traced.
4. **Run only repo-configured checks** — Input: commands already in `package.json`/`Makefile`/CI; Output: `verification_checks[]` (`name`, `status=passed|failed|not_run|unavailable`, `scope`, `evidence`); never install analyzers/deps or write repro probes; only `reproduced` from executed configured checks.
5. **Write evidence JSON** — Input: `references/bug-audit-evidence.schema.json` + `references/audit-protocol.md §1,2,5`; Output: `.docs/<pair>.evidence.json` with 12 required top-level fields; never include secrets/full sources.
6. **Write Markdown report** — Input: evidence JSON; Output: `.docs/<pair>.md` with exactly 4 sections (`§4`); render severity as `🔴 High`/`🟡 Medium`/`🟢 Low`; do not duplicate JSON appendix.
7. **Validate & fix** — Input: `python -X utf8 <skill-dir>/scripts/validate_bug_audit.py --evidence <evidence> --report <report> [--repo-root <path>]`; Output: exit 0 pass / 1 content / 2 I/O; fix all policy failures before delivery; return clickable links + 1-paragraph summary, never pasted artifacts.

Rules: validator checks structure/policy, not truth — rule out alternatives by reading implementation, major callers/callees, config, and tests.

## Failure handling — if-then fallbacks

- **If checks not configured / unavailable** → record `verification_checks.status=unavailable` + evidence "no command found"; disclose in `Limitations`; Comprehensive cannot reach High confidence without one `passed`.
- **If Comprehensive cannot read all in-scope files within budget** → switch to Multi-agent partitioned; if still infeasible, narrow to `core|high` paths, mark `execution.provisional=true`, store each unread as `inventory.status=mapped`+`reason`, state consequence in `limitations` (not file list).
- **If Multi-agent unavailable** → explain, ask to switch to Standard; never silently fallback (`execution.review_mode` is factual).
- **If `.docs/` artifact already exists** → add same timestamp `YYYYMMDD-HHMMSS` to both basenames; never overwrite.
- **If no `core|high` item** → treat as mis-tiering: require at least one; re-evaluate tiering per §5, otherwise provisional with reason.

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

## Validate and deliver

🔴 **CHECKPOINT — 驗證通過前不得交付**：未達 exit 0 禁止回傳產物連結；若需縮範圍/切模式，須先獲用戶確認並標 `provisional`。

```text
python -X utf8 <skill-directory>/scripts/validate_bug_audit.py --evidence <evidence.json> --report <report.md>
# --repo-root <path> when artifacts are outside the audited tree
```

Requires `jsonschema` (`pip install jsonschema`). Resolve `<skill-directory>` per [platform-adapters](references/platform-adapters.md); quote paths. Validator checks coverage recomputation, caps, ordering, and that every `inventory`/`location` path exists. Exit 0 = pass, 1 = content violation, 2 = I/O. 🛑 STOP: Do not deliver unvalidated artifacts; return clickable links + short summary, not pasted artifacts.
