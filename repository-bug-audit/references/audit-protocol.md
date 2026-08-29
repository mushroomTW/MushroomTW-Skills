# Audit Protocol — Evidence, Scoring & Reporting

> Single protocol document merging former `evidence-and-reporting.md` + `scoring-rubric.md` + `report-template.md`.
> `SKILL.md` references this file as a skeleton; the authoritative field definitions remain `bug-audit-evidence.schema.json` and `validate_bug_audit.py`.

## Contents

- [1. Evidence Model](#1-evidence-model)
- [2. Deduplication and Conflicts](#2-deduplication-and-conflicts)
- [3. Scoring and Calibration](#3-scoring-and-calibration)
- [4. Report Templates](#4-report-templates)
- [5. Completion Gates](#5-completion-gates)

---

## 1. Evidence Model

### 1.1 Finding Types

| Type | Threshold |
| --- | --- |
| `defect` | Behavior is proven to violate a visible contract or produce an incorrect result. Must have `expected_behavior` / `actual_behavior`, evidence `observed` or `reproduced`, confidence ≥7, status `confirmed` / `cross-confirmed` |
| `risk` | A control gap or concrete failure condition is directly proven, but the incorrect outcome has not been fully exercised. Must have non-empty `preconditions` and `verification`; use `needs-verification` when a material alternative remains |
| `quality-debt` | An engineering problem not yet proven to cause incorrect runtime behavior. Allowed only in Comprehensive; forbidden in Rapid |

Scanner hits, TODOs, complexity, search results, and code smells are candidate signals only — before filing a finding, read the implementation, major callers and callees, configuration, and tests.

### 1.2 Evidence Kinds and Confidence

| Evidence | Meaning |
| --- | --- |
| `observed` | Directly confirmed from code and data flow in the current working tree |
| `reproduced` | Confirmed by actually executing a repository-configured test/build/lint/analyzer |
| `inferred` | Multiple facts agree but a named runtime condition remains unverified; never valid for `defect` |
| `cross-confirmed` | Confirmed by two independent sources; independent review may raise confidence by at most +1 |

| Confidence | Handling |
| --- | --- |
| 9–10, 7–8 | Publishable |
| 5–6 | Publishable only as `needs-verification` |
| 3–4 | Keep in evidence only, do not publish or score |
| 1–2 | Discard |

Severity (`High/Medium/Low`) expresses impact, confidence expresses certainty — never substitute one for the other. Evidence stores `High/Medium/Low`, report renders `🔴 High / 🟡 Medium / 🟢 Low`.

Public findings order: `defect → risk → quality-debt`; within each type `High → Medium → Low`; then by descending confidence and ID.

---

## 2. Deduplication and Conflicts

- Deduplicate by **root cause and remediation**, not line number. Normalize fingerprints as lowercase `category|root-cause|primary-symbol`.
- The same root cause across multiple files counts as one finding; do not deduct twice unless each deduction has independent, proven impact.
- Each finding deducts in exactly one dimension (decided by `category`, see §3.3); the validator enforces this.
- Multi-agent (fixed execution mode): the primary agent reads relevant source and tests to resolve conflicts; if conflict remains, lower confidence and use `needs-verification`, never average scores.

---

## 3. Scoring and Calibration

### 3.1 Mode Differences

| | Rapid | Comprehensive |
| --- | --- | --- |
| Score / rating / dimensions | None | 7 dimensions, 0–100 |
| Max confidence | Medium | High |

Rapid risk calibration:

- **High**: At least one confirmed High `defect`/`risk` exists, or multiple confirmed Medium form a proven systemic major risk
- **Medium**: No confirmed High, but at least one public High/Medium `defect`/`risk` exists, or a major unknown requires escalation
- **Low**: No public High/Medium `defect`/`risk`, selected core/high-risk flows are traced, no major unknown

Rapid confidence is never High; a `provisional` Rapid must be Low.

### 3.2 Dimensions and Weights

| Dimension | ID | Weight |
| --- | --- | ---: |
| Correctness and reliability | `correctness` | 30 |
| Security and data handling | `security` | 25 |
| Performance and operability | `performance_operability` | 15 |
| Testing and verification | `testing` | 10 |
| Architecture and maintainability | `architecture` | 10 |
| Readability and consistency | `readability` | 5 |
| Dead-code hygiene | `dead_code` | 5 |

Maturity 0–5:

| Level | Anchor |
| ---: | --- |
| 5 | Verifiable controls consistently cover core risks, no material gap |
| 4 | Generally sound, only localized Low issues |
| 3 | Usable, but clear control/coverage gaps require near-term work |
| 2 | Multiple gaps or one confirmed High creates material risk |
| 1 | Systemic weaknesses make operation or change hard to trust |
| 0 | Confirmed major failure / data or security hazard, or dimension effectively absent |

Formula: without N/A `total = Σ(weight × level ÷ 5)`; with N/A `total = 100 × Σ(applicable scores) ÷ Σ(applicable weights)`, rounded half-up. N/A only when the project objectively has no relevant behavior or risk — missing implementation/tests/docs is a low level, not an exemption.

### 3.3 Caps and Attribution

- One confirmed High → dimension capped at level 2; multiple confirmed High → capped at 1; confirmed Medium on a core flow → capped at 3 (enforced by `validate_bug_audit.py`).
- To avoid double-deduct, `category → dimension` mapping is fixed: `correctness→correctness`, `security→security`, `testing→testing`, `architecture→architecture`, `readability→readability`, `dead-code→dead_code`, `performance/operability→performance_operability`.

### 3.4 Total and Rating

| Score | Rating |
| --- | --- |
| 90–100 | Strong engineering quality |
| 75–89 | Generally good |
| 60–74 | Material technical debt |
| 40–59 | Elevated engineering risk |
| 0–39 | Major engineering risk |

The total is a two-digit judgment, not a measurement; not comparable across repositories. Within-repo variance of one band between runs is noise. Caps make severity decisions the strongest lever on the total — calibrate severity by impact, not by desired total.

Confidence requirements (Comprehensive):

- **High**: 100% coverage, all core/high-risk flows traced, at least one configured check `passed`, non-provisional, no conclusion-changing invisible boundary
- **Medium**: ≥90% coverage with core flows traced, or 100% with unverifiable external/runtime boundary
- **Both High and Medium additionally require** 100% core-path coverage (every `core`/`high` file is `read`)

### 3.5 Dimension Checklists

- **Correctness**: contracts, boundaries, partial failures, timeouts/retries/cancellation, state transitions/transactions/consistency/concurrency, resource release
- **Security**: external input, paths/queries/serialization, authorization, credentials/PII/logs, injection/SSRF/deserialization/crypto/defaults
- **Performance & Operability**: unbounded work, N+1, blocking I/O, hot-path allocation, resource limits/backpressure, observability/startup/deployment resilience
- **Testing**: observable assertions for core/failure/boundary/security behavior, mocks, risk-proportionate integration evidence
- **Architecture**: responsibility boundaries, dependency direction/cycles, duplication, global state, error contracts, single source of truth
- **Readability**: naming/organization/control flow/comments/magic values/project conventions (do not inflate pure formatting preferences into findings)
- **Dead code**: unreachable code, unused symbols/dependencies, obsolete paths/flags/migrations/compatibility layers (search miss is candidate signal only)

---

## 4. Report Templates

### 4.1 Shared Rules

- Both modes have **exactly four level-two headings**; when `execution.provisional == true`, place `**Provisional report**` directly below the title.
- Executive Summary must include `Core-path coverage`: `critical_read_files / critical_in_scope_files` and percentage.
- Finding severity is stored as `High/Medium/Low`, report renders as `🔴 High / 🟡 Medium / 🟢 Low`; validator checks consistency.
- No per-file inventory, fingerprints, full evidence, raw command output, or appendices; do not copy evidence JSON as appendix.
- Local Markdown links must resolve; report lives in `.docs/`, link to root files with `../`, e.g. `[src/main.py](../src/main.py:1)`.

### 4.2 Findings Table and Details

Section 3 starts with a single table:

```markdown
| ID | Type | Severity / confidence | Location | Problem and impact | Recommendation |
| --- | --- | --- | --- | --- | --- |
```

Order per §1.2. **Each public finding appears exactly once**; High/Medium add `### FINDING-ID: Summary` detail block (Location, ≤3 Evidence, Impact, Recommendation, Verification), Low is table-only. If no public findings: `No reportable findings were identified within the reviewed scope.`

### 4.3 Rapid Template

```markdown
# Repository Bug Audit — Rapid
## 1. Executive Summary
| Metric | Result |
| --- | --- |
| Risk signal | High / Medium / Low |
| Assessment confidence | Medium / Low + rationale |
| Review coverage | Read / non-excluded, % and boundary |
| Core-path coverage | Core+high read / in-scope, % |
| Verification summary | Main passed/failed/not_run/unavailable |
State explicitly that Rapid does not assign a score.
## 2. Review Coverage and Bug Surfaces
## 3. Prioritized Findings
## 4. Limitations (≤5 conclusion-changing gaps)
```

### 4.4 Comprehensive Template

```markdown
# Repository Bug Audit
## 1. Executive Summary
| Metric | Result |
| --- | --- |
| Total score | 0–100 + rating; disclose N/A renormalization when used |
| Overall risk | High / Medium / Low |
| Assessment confidence | High / Medium / Low + rationale |
| File coverage | Read / in-scope, % |
| Core-path coverage | Core+high read / in-scope, % |
| Verification summary | Main passed/failed/not_run/unavailable |
## 2. Risk-Weighted Quality Scores
| Dimension | Weight | Level | Score | Primary rationale |
| --- | ---: | ---: | ---: | --- |
Each rationale ≤2 sentences, reference only related finding IDs, no Compliance table.
## 3. Prioritized Findings
## 4. Limitations (≤5)
```

---

## 5. Completion Gates

### 5.1 Shared

- Inventory paths unique, relative, backed by existing files; `coverage` and `critical_*` are recomputable from inventory
- Every finding `location` points to an existing file
- At least one in-scope item is `core` or `high`
- Confidence > Low requires 100% core-path coverage
- Every known core/high-risk flow has a trace state
- Findings satisfy type/confidence/dedup/ordering; public Markdown exactly matches evidence
- `limitations` discloses conclusion-changing unknowns; report and evidence filenames are paired and never overwritten; validator exits 0

### 5.2 Rapid Only

- `mapped` allowed; must not output `dimensions/total_score/rating`; confidence ≤ Medium; mark `provisional` when map/selected flows/minimum evidence is incomplete

### 5.3 Comprehensive Only

- When non-provisional, no `mapped` (every item `read` or `unreadable`); all known core/high flows traced; all 7 dimensions and total present; mark `provisional` when a conclusion-changing boundary is incomplete
- Over budget: either split further via Multi-agent, or narrow to core/high paths and mark `provisional`, recording each unread as `mapped`+`reason` in inventory, `limitations` states consequence, not file list
- High confidence requires 100% coverage + traced + non-provisional + at least one verification `passed`; Medium requires ≥90% and traced
