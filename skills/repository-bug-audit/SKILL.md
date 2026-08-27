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

1. **Select modes** — In: user request; Out: `audit_mode`+`review_mode`; Format: one `AskUserQuestion` 2問（已答則跳過）。
2. **Build map & inventory** — In: `AGENTS.md`/`README`/manifests/CI; Out: `inventory[]` (`path`,`status`,`risk_tier`,`reason`); 全工作樹，禁用 `git diff`/history。
3. **Trace flows** — In: `core|high` items; Out: `core_flows[]` (`name`,`entry_point`,`status`,`evidence[]`)；每個已知 core/high 必須 traced。
4. **Run checks** — In: 已配置指令；Out: `verification_checks[]` (`status=passed|failed|not_run|unavailable`)；禁裝工具/寫探針，`reproduced` 僅來自已執行配置。
5. **Write evidence** — In: `schema.json`+`audit-protocol.md §1,2,5`; Out: `.docs/<pair>.evidence.json`（12 必填欄位）；禁機密/全源碼。
6. **Write report** — In: evidence; Out: `.docs/<pair>.md` 恰 4 章（§4），severity 渲染 `🔴/🟡/🟢`，不抄 JSON。
7. **Validate & fix** — In: `python -X utf8 <skill-dir>/scripts/validate_bug_audit.py --evidence --report [--repo-root]`; Out: exit 0/1/2；修復後回傳連結+摘要，不貼全文。

Rules: validator checks structure/policy, not truth — rule out alternatives by reading implementation, major callers/callees, config, and tests.

## Failure handling — if-then

- **If checks unavailable** → `status=unavailable` + `Limitations`揭露；Comprehensive High 需一 `passed`。
- **If 全量讀取超預算** → 切 Multi-agent；仍不可行則縮至 `core|high`、`provisional=true`、未讀記 `mapped`+`reason`。
- **If Multi-agent 不可用** → 明述並詢問切 Standard；禁靜默降級。
- **If `.docs/` 已存在** → 兩檔同加 `YYYYMMDD-HHMMSS`，永不覆蓋。
- **If 無 `core|high`** → 視為分層錯誤，須至少一項，重評 §5 否則 provisional。

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

## 禁止事項 — 不要做

- 單檔/PR diff/單一漏洞/單點效能/一般提問 — 禁用本 skill
- 改程式碼/設定/測試/外部系統（需用戶另行明確要求）
- 裝分析器/相依、寫重現探針；`reproduced` 僅來自已執行配置
- 以 `git diff`/history 縮範圍；以搜尋不到斷言已修/已測/安全
- 覆蓋 `.docs/` 產物、抄 JSON 附錄、寫機密/全源碼

## Validate and deliver

🔴 **CHECKPOINT — 驗證通過前不得交付**：未達 exit 0 禁止回傳產物連結；若需縮範圍/切模式，須先獲用戶確認並標 `provisional`。

```text
python -X utf8 <skill-directory>/scripts/validate_bug_audit.py --evidence <evidence.json> --report <report.md>
# --repo-root <path> when artifacts are outside the audited tree
```

Requires `jsonschema` (`pip install jsonschema`). Resolve `<skill-directory>` per [platform-adapters](references/platform-adapters.md); quote paths. Validator checks coverage recomputation, caps, ordering, and that every `inventory`/`location` path exists. Exit 0 = pass, 1 = content violation, 2 = I/O. 🛑 STOP: Do not deliver unvalidated artifacts; return clickable links + short summary, not pasted artifacts.
