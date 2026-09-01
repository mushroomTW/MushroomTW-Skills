# Repository Bug Audit

**English** | [繁體中文](repository-bug-audit.zh.md)

> This document lives in `docs/`. Relative paths and commands below are relative to the project directory `repository-bug-audit/`.

An agent skill for evidence-driven, repository-wide bug discovery and engineering risk assessment. It finds material bugs first, then — in Comprehensive mode — assesses broader engineering quality and produces a risk-weighted 0–100 score.

The skill is deliberately strict about what counts as a finding. A scanner hit, a TODO, a complexity metric, or a search result is a *signal*, not a finding. Before anything is published, the implementation, its major callers and callees, its configuration, and its tests have to be read. Every finding carries a location, direct evidence, impact, confidence, remediation direction, and a verification method, and the whole record is machine-checked before delivery.

Ships as a plain skill folder for any skills-compatible host (Claude Code, Codex, OpenCode, Claude Apps, etc.).

## What It Produces

Every run leaves exactly one file in the audited repository:

- a concise **Markdown report** for humans — the only delivered artifact.

Behind it, the skill builds a machine-readable evidence record — inventory, traced flows, executed checks, findings, limitations, and (in Comprehensive mode) dimension scores — and the validator cross-checks the report against it before delivery. That evidence file is a validation input, not an output: it is deleted when the run ends, and the Markdown never carries it as an appendix.

## Audit Modes

| | Rapid | Comprehensive |
| --- | --- | --- |
| Coverage | Maps the whole repository, reads core and highest-risk paths | Reads every in-scope file |
| Inventory states | `read`, `mapped`, `excluded`, `unreadable` | `mapped` only in a provisional report |
| Finding types | `defect`, `risk` | `defect`, `risk`, `quality-debt` |
| Quality score | None | Seven dimensions, 0–100, with a rating |
| Max confidence | Medium | High |

Rapid answers "are there bugs I should know about, quickly?" Comprehensive answers "how healthy is this codebase, and what is the number?" Rapid never assigns a score — reporting one from partial coverage would misrepresent how much was actually examined.

In Comprehensive mode the skill estimates read cost from the in-scope file count and execution budget; when the whole scope cannot be read within budget it must either partition across agents or narrow to core and highest-risk paths, mark the report provisional, and record each unread file in the inventory as `mapped` with a reason. The inventory is the unread-file list, so coverage drops on its own and `limitations` explains the consequence instead of enumerating filenames.

## Execution Modes

- **Standard** — the primary agent performs the whole audit.
- **Multi-agent partitioned** — the primary agent partitions scope across independent reviewers, then integrates evidence and verifies cross-boundary conclusions itself. Every candidate High finding is cross-reviewed by an agent that is not told the original conclusion, so confirmation reflects independent judgement rather than agreement with a verdict already on the table.

Multi-agent mode does not relax coverage, privacy, validation, or read-only requirements. If independent agents are unavailable on the current host, the skill says so and asks you to switch to Standard rather than silently downgrading — `execution.review_mode` in the evidence JSON is a factual claim about how the audit was performed.

## Install

From the repository root, let the `skills` CLI discover supported agents and install this skill:

```bash
npx skills add . --skill repository-bug-audit
```

Add `--global` for personal scope; without it, the CLI installs at project scope. For a manual installation, copy `repository-bug-audit/` to a skills directory documented by the host instead of assuming a runtime-specific path.

For Claude Apps, upload this repository (or zip) as the skill. Claude Apps has no subagent mechanism, so Multi-agent partitioned execution is unavailable and the skill will ask you to choose Standard.

> [!NOTE]
> The first `npx` invocation may download the CLI. Reload or restart the host when it only discovers skills at session start.

## Usage

Invoke it explicitly — this skill is for whole-repository work, not for a single file, a PR diff, or one known bug:

```text
/repository-bug-audit
```

Or describe the task in your own words: *"audit this whole repository for bugs and give me an engineering quality score."*

The skill then asks you to choose an audit mode and an execution mode. On Claude Code both questions arrive in a single choice prompt. Answer either of them up front in your request and it skips that question.

From there it maps the repository, traces core and high-risk flows, runs only checks the repository already configures, writes the two artifacts, runs the validator, and returns clickable links plus a short summary in chat. It does not paste the artifacts into the conversation.

## Output Artifacts

| Mode | Report |
| --- | --- |
| Rapid | `.docs/repository-bug-audit-rapid-report.md` |
| Comprehensive | `.docs/repository-bug-audit-report.md` |

The report is written to the audited repository's `.docs/` directory, which is created when it does not exist. The evidence file lives beside it as `<report-stem>.evidence.json` only while the validator runs — that name and a `.docs/` parent are what the validator requires — and is removed once the run ends.

If the default path already exists, the report gets a local timestamp — for example `repository-bug-audit-report-20260806-153000.md`. Existing files are never overwritten, so a re-audit cannot destroy the previous report.

Both report layouts use exactly four sections. Rapid uses Executive Summary, Review Coverage and Bug Surfaces, Prioritized Findings, and Limitations; Comprehensive replaces the second with Risk-Weighted Quality Scores. High and Medium findings get detail blocks; Low findings stay in the table. Every row carries its evidence kind, and the executive summary states the evidence mix, so a reader can tell findings an executed check confirmed from findings derived by reading alone. See [`audit-protocol.md`](../repository-bug-audit/references/audit-protocol.md).

## The Evidence Model

### Finding Types

| Type | Bar to clear |
| --- | --- |
| `defect` | Behavior is proven to violate a visible contract or produce an incorrect result. Requires `expected_behavior`, `actual_behavior`, `observed` or `reproduced` evidence, confidence ≥ 7, and `confirmed`/`cross-confirmed` status. |
| `risk` | A control gap or concrete failure condition is directly supported, but the bad outcome has not been fully exercised. Requires non-empty preconditions and verification. |
| `quality-debt` | An engineering problem not proven to cause incorrect runtime behavior. Comprehensive mode only. |

### Evidence Kinds

- `observed` — directly confirmed from code and data flow in the current working tree.
- `reproduced` — confirmed by a repository-configured check that was actually executed.
- `inferred` — multiple facts agree while a named runtime condition stays unverified. Never valid for a `defect`.
- `cross-confirmed` — a `status` value rather than an evidence kind: two independent sources, at least one of them outside the reviewing agents (an executed check, a test, an external specification). Two agents reading the same tree share the same priors and do not count as independent; only a source of the first kind may raise confidence, by at most one point.

### Confidence Bands

Severity expresses impact; confidence expresses evidentiary certainty. They are never substituted for one another.

| Confidence | Handling |
| --- | --- |
| 9–10, 7–8 | Publishable |
| 5–6 | Publishable only as `needs-verification` |
| 3–4 | Kept in evidence, never published, never scored |
| 1–2 | Discarded |

Findings are deduplicated by root cause and remediation rather than by line number, so one underlying defect surfacing in six files is one finding — and it is not deducted twice unless each deduction has a distinct, proven impact.

Full protocol: [`audit-protocol.md`](../repository-bug-audit/references/audit-protocol.md). Field-level authority: [`bug-audit-evidence.schema.json`](../repository-bug-audit/references/bug-audit-evidence.schema.json).

## Scoring (Comprehensive Mode)

Each dimension gets a 0–5 maturity level, which converts to a weighted contribution.

| Dimension | ID | Weight |
| --- | --- | ---: |
| Correctness and reliability | `correctness` | 30 |
| Security and data handling | `security` | 25 |
| Performance and operability | `performance_operability` | 15 |
| Testing and verification | `testing` | 10 |
| Architecture and maintainability | `architecture` | 10 |
| Readability and consistency | `readability` | 5 |
| Dead-code hygiene | `dead_code` | 5 |

Without N/A dimensions, `total = Σ(weight × level ÷ 5)`. With N/A dimensions the score is renormalized as `100 × Σ(applicable score) ÷ Σ(applicable weight)`. The result is rounded half-up. A dimension is N/A only when the project objectively has no relevant behavior or risk — missing implementation, tests, or documentation is a low level, not an exemption.

| Level | Maturity anchor |
| ---: | --- |
| 5 | Verifiable controls consistently cover core risks; no material gap found |
| 4 | Generally sound, only localized Low issues |
| 3 | Usable, but clear control or coverage gaps need near-term work |
| 2 | Multiple gaps, or one confirmed High, creates material risk |
| 1 | Systemic weaknesses make operation or change hard to trust |
| 0 | A major failure, data or security hazard, or effectively absent dimension |

Confirmed findings cap their dimension: one confirmed High caps it at level 2, multiple confirmed Highs cap it at 1, and a confirmed Medium on a core flow caps it at 3. These caps are enforced by the validator, which is what stops a strong score from being written over a known serious defect.

| Score | Rating |
| --- | --- |
| 90–100 | Strong engineering quality |
| 75–89 | Generally good |
| 60–74 | Material technical debt |
| 40–59 | Elevated engineering risk |
| 0–39 | Major engineering risk |

Full rubric: [`audit-protocol.md`](../repository-bug-audit/references/audit-protocol.md) §3.

## Validation

The bundled validator checks the report against the evidence record before delivery. It reads and writes UTF-8 explicitly; `-X utf8` simply keeps non-ASCII text in its console output readable.

```bash
python -X utf8 scripts/validate_bug_audit.py --evidence <evidence.json> --report <report.md>
```

| Exit code | Meaning |
| ---: | --- |
| `0` | The report and evidence satisfy all structural and policy checks |
| `1` | Content violations must be corrected |
| `2` | Arguments or files could not be read |

It enforces schema conformance, filename pairing policy, coverage arithmetic recomputed from the inventory, finding-type and confidence rules, deduplication, canonical ordering, dimension caps, score and rating arithmetic, mode-specific prohibitions, exact-match between the public Markdown findings and the evidence, and local link resolution.

Coverage is recomputed twice: once over all in-scope files, and once over the `core` and `high` risk tiers alone. Confidence above Low requires the second number to be 100% — reading many trivial files never compensates for an unread core file, and the executive summary has to state it.

It also resolves the audited tree as the report's parent directory — the parent of `.docs/` — and rejects any `inventory` path or finding `location` that no file backs, which is the one kind of fabrication a structural validator can catch outright. Add `--repo-root <path>` when the artifacts are validated somewhere other than the tree they describe.

What it does **not** do is prove a finding is true. It proves the record is internally consistent. Ruling out alternative explanations still requires reading the code.

## Guardrails

The skill is read-only apart from its two artifacts. It does not modify code, configuration, tests, or external systems; does not install analyzers or dependencies; and does not write reproduction programs or test probes anywhere, including temporary directories. Only checks the repository already configures may produce `reproduced` evidence.

It uses the entire current working tree as scope — never `git diff`, history, or a changed-file list — because a repository audit that only looks at recent changes is a diff review wearing the wrong name. Secrets, complete source files, personal data, and unnecessary raw command output stay out of the evidence file.

## Repository Layout

```text
repository-bug-audit/                         # 本倉庫即 skill 本體
├── README.md                                 # This file
├── README_zh.md                              # Traditional Chinese version
├── SKILL.md                                  # Skill definition and audit workflow
├── agents/
│   └── openai.yaml                           # Codex skill-picker metadata
├── references/
│   ├── platform-adapters.md                  # Per-host capability mapping
│   ├── audit-protocol.md                     # Evidence, scoring & reporting protocol
│   └── bug-audit-evidence.schema.json        # Authoritative evidence schema (v3.0)
├── scripts/
│   └── validate_bug_audit.py                 # Artifact-pair validator
└── tests/
    └── test_validate_bug_audit.py            # Validator test suite
```

The repository root is the skill — copy the whole folder to install.

## Development

The validator requires `jsonschema` (`pip install jsonschema`). Verified on CPython 3.14.

```bash
pip install jsonschema
python -X utf8 -m unittest discover -s tests -v
```

When changing the rules, keep the three sources of truth in step: `references/bug-audit-evidence.schema.json` defines fields and enums, `references/audit-protocol.md` defines the human-readable protocol and scoring arithmetic, `scripts/validate_bug_audit.py` enforces both, and `tests/test_validate_bug_audit.py` pins the behavior. A rule stated in prose but not enforced by the validator will drift.
