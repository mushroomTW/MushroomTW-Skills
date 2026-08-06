# Evidence and Reporting Protocol

## Contents

- [Canonical evidence record](#canonical-evidence-record)
- [Finding types](#finding-types)
- [Evidence and confidence](#evidence-and-confidence)
- [Deduplication and conflicts](#deduplication-and-conflicts)
- [Completion gates](#completion-gates)

## Canonical evidence record

Use [`bug-audit-evidence.schema.json`](bug-audit-evidence.schema.json) as the only authoritative definition of fields, required values, and enums. Keep one evidence JSON file beside the Markdown report. Record mode, scope, inventory, core flows, checks actually executed, complete findings, limitations, and Comprehensive-only dimensions and scores.

Evidence is an audit record, not a source archive. Never include credentials, secrets, complete source files, personal data, or unnecessary raw command output.

## Finding types

- `defect`: Current behavior is proven to violate a visible contract or produce an incorrect result. Require `expected_behavior` and `actual_behavior`, use `observed` or `reproduced`, require confidence of at least 7, and use `confirmed` or `cross-confirmed` status.
- `risk`: A control gap or concrete failure condition is directly supported, but the incorrect outcome has not been fully exercised or verified. Require non-empty `preconditions` and `verification`. Use `needs-verification` when a material alternative explanation remains.
- `quality-debt`: An architecture, testing, readability, dead-code, or similar engineering problem is not proven to cause incorrect runtime behavior. Allow it only in Comprehensive mode.

Rapid must not create `quality-debt`. Treat scanner hits, TODOs, complexity, search results, and code smells only as candidate signals. Read implementation, callers, configuration, and tests before creating a finding.

## Evidence and confidence

Severity expresses impact; confidence expresses evidentiary certainty. Never substitute one for the other.

- `observed` means directly confirmed from code and data flow in the current working tree.
- `reproduced` means confirmed by a repository-configured test, build, linter, or analyzer that was actually executed.
- `inferred` means multiple facts agree while a named runtime condition remains unverified. Never use it for a `defect`.
- `cross-confirmed` requires two independent sources. Independent review may raise confidence by at most one point.
- Confidence 9-10 and 7-8 may be published. Confidence 5-6 may be published only as `needs-verification`. Keep 3-4 in evidence only. Discard 1-2.
- A High finding below confidence 7 cannot be `confirmed` or `cross-confirmed`.

Sort public findings by `defect`, `risk`, and `quality-debt`; then by High, Medium, and Low; then by descending confidence and finally by ID.

## Deduplication and conflicts

Deduplicate by root cause and remediation, not by line number. Normalize fingerprints as lowercase English `category|root-cause|primary-symbol` values. Do not deduct one fact across multiple dimensions unless each dimension has a distinct, proven impact.

In Multi-agent mode, the primary agent reads the relevant source and tests to resolve disagreements. If conflict remains, lower confidence and use `needs-verification`. Never average agent scores.

## Completion gates

Shared gates:

- inventory paths are unique and coverage can be recalculated from inventory;
- every known core or high-risk flow has a trace state;
- findings satisfy type, confidence, deduplication, and ordering rules;
- public Markdown findings exactly match evidence;
- check states are truthful and limitations disclose conclusion-changing unknowns;
- report and evidence names form one non-overwritten pair;
- the validator exits with code `0`.

Rapid may contain `mapped` items, must not output scores, and cannot exceed Medium confidence. Mark it provisional when the repository map, selected high-risk flows, or minimum evidence record is incomplete.

Comprehensive forbids `mapped`, requires every in-scope item to be `read` or `unreadable`, traces every known core or high-risk flow, and completes all seven dimensions and the total score. Mark it provisional when any conclusion-changing boundary is incomplete.
