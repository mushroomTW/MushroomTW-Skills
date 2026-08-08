# Bug Audit Report Templates

## Shared rules

Use exactly four level-two headings for the selected mode. When `execution.provisional` is true, place `**Provisional report**` directly below the title. Do not include per-file inventory, fingerprints, complete evidence records, raw command output, or appendices.

Every executive summary carries a `Core-path coverage` row reporting `critical_read_files / critical_in_scope_files` and `critical_percentage`. Overall file coverage can be inflated by reading many trivial files, so this is the number a conclusion actually rests on — and the confidence rules are enforced against it.

Start section 3 with one findings table:

```markdown
| ID | Type | Severity / confidence | Location | Problem and impact | Recommendation |
| --- | --- | --- | --- | --- | --- |
```

Sort by `defect`, `risk`, and `quality-debt`; within each type sort by High, Medium, and Low, then by descending confidence and ID. Include every public finding exactly once. Add `### FINDING-ID: Summary` detail blocks for High and Medium only, containing Location, no more than three Evidence bullets, Impact, Recommendation, and Verification. Never expand Low findings.

If no public findings exist, write: `No reportable findings were identified within the reviewed scope.`

## Rapid

```markdown
# Repository Bug Audit — Rapid

## 1. Executive Summary

| Metric | Result |
| --- | --- |
| Risk signal | High / Medium / Low |
| Assessment confidence | Medium / Low with a short rationale |
| Review coverage | Files read / non-excluded files, percentage, and boundary |
| Core-path coverage | Core and high-risk files read / in scope, and percentage |
| Verification summary | Main passed, failed, not-run, or unavailable checks |

State explicitly that Rapid does not assign a quality score.

## 2. Review Coverage and Bug Surfaces

Describe entry points, core and high-risk flows, state and trust boundaries, and material mapped areas.

## 3. Prioritized Findings

Use the shared findings format. Include only defect and risk findings.

## 4. Limitations

List no more than five conclusion-changing gaps or unverified assumptions.
```

## Comprehensive

```markdown
# Repository Bug Audit

## 1. Executive Summary

| Metric | Result |
| --- | --- |
| Total score | 0-100 and rating; disclose N/A renormalization when used |
| Overall risk | High / Medium / Low |
| Assessment confidence | High / Medium / Low with a short rationale |
| File coverage | Files read / files in scope and percentage |
| Core-path coverage | Core and high-risk files read / in scope, and percentage |
| Verification summary | Main passed, failed, not-run, or unavailable checks |

## 2. Risk-Weighted Quality Scores

| Dimension | Weight | Level | Score | Primary rationale |
| --- | ---: | ---: | ---: | --- |

Keep each rationale to two sentences and reference only related finding IDs. Do not output a Compliance table.

## 3. Prioritized Findings

Use the shared findings format. All three finding types are allowed.

## 4. Limitations

List no more than five conclusion-changing gaps or unverified assumptions.
```

Before submission, confirm every local Markdown link resolves from the report directory. Because the report lives in `.docs/`, link to repository-root files with a `../` prefix, for example `[src/main.py](../src/main.py:1)`.
