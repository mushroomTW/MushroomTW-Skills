---
name: repository-bug-audit
description: Perform evidence-driven, repository-wide bug discovery and engineering risk audits in either unscored Rapid mode or Comprehensive mode with a risk-weighted 0-100 quality score. Use when the user explicitly requests a whole-repository bug hunt, repository-wide risk review, overall engineering quality score, or complete technical-debt assessment. Do not use for a single file or module, a PR or diff review, one known bug or vulnerability, a localized performance issue, general coding questions, or a review of this skill itself.
allowed-tools: Read, Grep, Glob, Bash, Write, Task
---

# Repository Bug Audit

Audit the current working tree by finding material bugs first, then assess broader engineering quality in Comprehensive mode. Produce one concise Markdown report paired with one machine-readable evidence JSON file. Remain read-only except for those two artifacts. Do not modify code, configuration, tests, or external systems unless the user separately requests it.

## Required startup choices

Before inventorying or reading the project, ask the user to choose both options in one interaction:

1. **Audit mode**
   - **Rapid bug audit:** Map the repository, inspect core and high-risk paths, publish only `defect` and `risk` findings, and do not assign a score.
   - **Comprehensive bug and quality audit:** Read every included file, find bugs first, then include `quality-debt` findings and calculate a seven-dimension 0-100 score.
2. **Execution mode**
   - **Standard:** The primary agent performs the audit.
   - **Multi-agent partitioned:** The primary agent partitions scope, integrates evidence, and verifies cross-boundary conclusions.

Use the platform choice interface when available, following the [platform adapters](references/platform-adapters.md) for the host you are running in. Skip a choice already made explicitly by the user. If Multi-agent is selected but independent agents are unavailable, explain the limitation and ask the user to switch to Standard. Never silently fall back.

## Workflow

Follow these phases in order:

1. Select audit and execution modes.
2. Read repository instructions and build the repository map and inventory.
3. Review the mode-specific scope and trace every known core or high-risk flow.
4. Run only safe checks already configured by the project, such as tests, builds, linters, type checks, or analyzers.
5. Write the evidence JSON using the [evidence schema](references/bug-audit-evidence.schema.json) and [evidence protocol](references/evidence-and-reporting.md).
6. Write the paired Markdown report using the [report templates](references/report-template.md).
7. Run the bundled validator and fix structural or policy failures before delivery.

Never install an analyzer, dependency, or other tool. Never write a reproduction program or test probe in either the repository or a temporary directory. Only results from checks already configured by the repository may use `reproduced` evidence.

The validator proves schema and policy consistency only. It does not prove that a finding is true. Eliminate reasonable alternative explanations by reading code, callers, configuration, and tests.

## Build the repository map

1. Read applicable `AGENTS.md` files, development rules, README and architecture documents, public contracts, schemas, manifests, test configuration, CI, and deployment configuration.
2. Identify languages, package managers, entry points, services, data layers, background jobs, external integrations, persistence, state boundaries, trust boundaries, tests, and deployment units.
3. Inventory first-party runtime code, tests, build scripts, migrations, deployment code, programmatic CI, manifests, schemas, and behavior-affecting configuration.
4. Mark generated artifacts, dependencies, vendored code, caches, binaries, build output, and large fixtures as `excluded` with a reason. Include ambiguous generated, example, snapshot, seed, or compatibility code whenever it enters a build, deployment, test, or public contract.
5. Give every item one status: `read`, `mapped`, `excluded`, or `unreadable`. Allow `mapped` only in Rapid mode.

Use the entire current working tree as scope. Do not use `git diff`, history, or changed-file lists to narrow the audit. Prefer repository-provided code-navigation tools. A search result or tool summary does not count as reading a file.

## Bug discovery priorities

Prioritize:

- mismatches between public contracts and actual behavior;
- boundary values, error paths, partial failures, timeouts, retries, and cancellation;
- state transitions, transactions, consistency, concurrency, and resource lifecycle;
- external input, authorization, sensitive data, and trust boundaries;
- unbounded work, N+1 behavior, blocking I/O, backpressure, and material performance degradation;
- whether observable assertions cover core, failure, and security behavior.

Treat scanner output, compiler or linter output, TODOs, metrics, complexity, and code smells only as search signals. Before creating a finding, read the relevant implementation, major callers and callees, configuration, and tests.

## Mode rules

### Rapid

- Map the whole repository and read core and highest-risk paths plus their major callers, callees, configuration, and tests.
- Allow lower-risk items to remain `mapped`, but state the review boundary clearly.
- Create only `defect` and `risk` findings. Never create `quality-debt` findings.
- Do not include `dimensions`, `total_score`, or `rating`. Assessment confidence cannot exceed Medium.
- Mark the report provisional when the repository map, selected flows, or minimum evidence record is incomplete.

### Comprehensive

- Read every included file. Forbid `mapped`; every in-scope item must be `read` or `unreadable`.
- Trace every known core and high-risk flow and inspect major shared use sites.
- After inventory, estimate read cost from in-scope file count, size, and the current execution budget. If the whole scope cannot be read within budget, you must either switch to Multi-agent partitioned execution to divide the scope, or narrow to core and highest-risk paths, mark the report provisional, and list every unread in-scope file in `limitations`. Never claim 100% coverage or High confidence over unread files — the validator enforces coverage recomputation and the confidence rules.
- Create `defect` and `risk` findings first, then assess `quality-debt`.
- Calculate seven dimensions and a 0-100 score using the [scoring rubric](references/scoring-rubric.md) only after coverage and evidence are complete.
- Produce a provisional report when coverage, a core flow, or a conclusion-changing boundary is incomplete. Never claim whole-repository completion in that state.

## Findings and evidence

- A `defect` must prove that expected and actual behavior differ, use `observed` or `reproduced` evidence, have confidence of at least 7, and use `confirmed` or `cross-confirmed` status.
- A `risk` must prove a control gap or concrete failure condition and include non-empty preconditions and verification. Use `needs-verification` when a material alternative explanation remains.
- A `quality-debt` finding describes an engineering problem not proven to cause incorrect runtime behavior and is allowed only in Comprehensive mode.
- Every finding requires a concrete location, direct evidence, impact, confidence, remediation direction, and verification method.
- Deduplicate by root cause and remediation. Do not deduct the same root cause more than once without distinct, proven impacts.
- Keep confidence 3-4 candidates in evidence only. Do not publish or score them. Discard confidence 1-2 speculation.
- Before claiming behavior is absent, handled, tested, secure, or unused, inspect likely implementations, registrations, callers, configuration, and tests. A search miss supports only "Not found within the reviewed scope."

Read the [evidence protocol](references/evidence-and-reporting.md) completely before creating findings or integrating multi-agent results.

## Artifact names

Create exactly one paired report and evidence file:

| Mode | Report | Evidence |
| --- | --- | --- |
| Rapid | `repository-bug-audit-rapid-report.md` | `repository-bug-audit-rapid-report.evidence.json` |
| Comprehensive | `repository-bug-audit-report.md` | `repository-bug-audit-report.evidence.json` |

If either default path already exists, add the same local timestamp to both basenames, for example `repository-bug-audit-report-YYYYMMDD-HHMMSS.md` and `repository-bug-audit-report-YYYYMMDD-HHMMSS.evidence.json`. Never overwrite either existing file.

Do not put secrets, complete source files, or unnecessary raw command output in evidence. Keep Markdown concise and do not duplicate evidence JSON as an appendix.

## Validate and deliver

Use UTF-8 mode on every platform, because the evidence JSON carries emoji severity values:

```text
python -X utf8 <skill-directory>/scripts/validate_bug_audit.py --evidence <evidence.json> --report <report.md>
```

Resolve `<skill-directory>` from the [platform adapters](references/platform-adapters.md) — it is
`${CLAUDE_PLUGIN_ROOT}` for a Claude Code plugin install and a fixed skills path otherwise. Quote the
path; installed plugin directories contain version segments and, on Windows, spaces.

Exit code `0` means the artifact pair satisfies structural and policy checks. Exit code `1` means content violations must be corrected. Exit code `2` means arguments or files could not be read. Do not deliver unvalidated artifacts. When missing evidence prevents correction, mark the affected conclusion provisional and keep evidence internally consistent.

In chat, return clickable links to both artifacts and a very short summary. Do not paste either artifact.

## Multi-agent execution

See the [platform adapters](references/platform-adapters.md) for the subagent mechanism on the current host. The primary agent owns inventory, shared interfaces, cross-boundary flows, final evidence, validation, and the report. Assign every file or risk area one primary reviewer. Require each subagent to return inventory states, traced flows, structured candidate findings, and limitations. Subagents never assign the final score.

Independently cross-review every candidate High finding without disclosing the original conclusion. The primary agent reads relevant source and tests, resolves conflicts, deduplicates, recalibrates severity and score, and records source agents and confirmation state. Multi-agent mode does not relax coverage, privacy, validation, or read-only requirements.
