# Repository Bug Audit Calibration

## Rapid risk calibration

Rapid does not assign a total score, rating, dimension level, or dimension score.

- **High:** At least one confirmed High `defect` or `risk` exists, or multiple confirmed Medium runtime findings form a proven systemic major risk.
- **Medium:** No confirmed High exists, but at least one public High or Medium `defect` or `risk` exists, or a major unknown requires uncertainty-driven escalation.
- **Low:** No public High or Medium `defect` or `risk` exists, selected core and high-risk flows are traced, and no known major unknown requires escalation.
- **Medium confidence:** The repository map identifies core areas, every `core` and `high` risk-tier file is read, selected flows are traced, and unknowns do not invalidate the limited conclusion.
- **Low confidence:** The map is incomplete, a core or high-risk file is unread, a critical flow is untraced, or an unknown could materially change the conclusion.

Rapid confidence is never High.

## Comprehensive scoring

Assign a 0-5 maturity level to each applicable dimension, then calculate its weighted contribution:

| Dimension | ID | Weight |
| --- | --- | ---: |
| Correctness and reliability | `correctness` | 30 |
| Security and data handling | `security` | 25 |
| Performance and operability | `performance_operability` | 15 |
| Testing and verification | `testing` | 10 |
| Architecture and maintainability | `architecture` | 10 |
| Readability and consistency | `readability` | 5 |
| Dead-code hygiene | `dead_code` | 5 |

Without N/A dimensions, `total = Σ(weight × level ÷ 5)`. With N/A dimensions, renormalize as `100 × Σ(applicable score) ÷ Σ(applicable weight)`. Round the final result half-up.

Mark a dimension N/A only when the project objectively has no relevant behavior or risk. Missing implementation, tests, documentation, or verification is not N/A.

| Level | Maturity anchor |
| ---: | --- |
| 5 | Verifiable controls consistently cover core risks and no material gap was found |
| 4 | Generally sound with only localized Low issues |
| 3 | Usable, but clear control or coverage gaps require near-term work |
| 2 | Multiple gaps or one confirmed High creates material risk |
| 1 | Systemic weaknesses or several severe issues make operation or change difficult to trust |
| 0 | A major failure, data or security hazard, or effectively absent dimension is confirmed |

- One confirmed High normally caps its dimension at level 2. Multiple confirmed High findings cap it at level 1.
- A confirmed Medium affecting a core flow normally caps its dimension at level 3.
- Confidence 3-4 cannot reduce maturity. Confidence 5-6 affects maturity only when the control gap is proven.
- Choose maturity anchors from evidence. Never choose the total first and reverse-engineer dimensions.

## Dimension checks

- **Correctness:** Contracts, boundaries, partial failures, timeouts, retries, cancellation, state transitions, transactions, consistency, concurrency, and resource release.
- **Security:** External input, paths, queries, serialization, authorization, credentials, personal data, logs, injection, SSRF, deserialization, cryptography, and defaults.
- **Performance and operability:** Unbounded work, N+1 behavior, blocking I/O, hot-path allocation, resource limits, backpressure, observability, startup, and deployment resilience.
- **Testing:** Core, failure, boundary, and security behavior; observable assertions; mocks; and risk-appropriate integration evidence.
- **Architecture:** Responsibility boundaries, dependency direction, cycles, duplication, global state, error contracts, and sources of truth.
- **Readability:** Naming, organization, control flow, comments, magic values, and project conventions. Do not inflate pure formatting preferences into findings.
- **Dead code:** Unreachable code, unused symbols or dependencies, obsolete paths, flags, migrations, and compatibility layers. A search miss is only a candidate signal.

## Comprehensive confidence and rating

- High confidence requires 100% coverage, every core and high-risk flow traced, at least one primary configured check passed, non-provisional status, and no conclusion-changing invisible boundary.
- Medium confidence requires at least 90% coverage with every known core flow traced, or 100% coverage with unavailable runtime or external verification that does not invalidate the conclusion.
- High and Medium both additionally require 100% core-path coverage: every `core` and `high` risk-tier file read. An unread core file caps the audit at Low confidence no matter how many trivial files were read.
- All other cases have Low confidence.

| Score | Rating |
| --- | --- |
| 90-100 | Strong engineering quality |
| 75-89 | Generally good |
| 60-74 | Material technical debt |
| 40-59 | Elevated engineering risk |
| 0-39 | Major engineering risk |
