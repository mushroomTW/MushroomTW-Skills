---
name: sonarqube-fix-all
description: Batch-fix code quality and security issues reported by a self-hosted SonarQube instance via an already-configured SonarQube MCP connection, then verify and rescan. Use whenever the user asks to fix, clear, triage, or work through SonarQube issues, or mentions their Sonar quality gate failing. Language-agnostic; handles projects with no automated test suite, and protects semantically sensitive code such as bytecode/IL manipulation, runtime patching, and reflection-driven code from unsafe rewrites.
---

# Fix All SonarQube Issues

Resolve SonarQube findings at the source, verify each batch, and distinguish fixed, suppressed, and left-open results.

## Constraints

These hold for the entire workflow:

- Target **self-hosted SonarQube in Docker**, never SonarCloud; do not request an organization key or use SonarCloud setup.
- Query through the configured MCP connection. Scan only with the `SONAR_TOKEN` system environment variable; never request, create, display, modify, print, echo, or log credentials.
- Do not change server-side status or propose candidates for approval. `Accepted`, `False positive`, `Won't fix`, exclusions, and disabled rules require an explicit target (issue keys, or one rule scoped to a named file/module) and the desired status. Vague targets such as "unimportant issues" are invalid: 🛑 **STOP reclassification**, say why, continue source fixes, and report unsafe/unfixable findings as left-open for the user to reclassify.
- Never reset, revert, or discard the user's existing changes. Never push.
- Keep output lean: summaries and relevant excerpts, not full payloads, issue dumps, or raw logs.

## 1. Detect the project's toolchain

Infer these from repository manifests, lockfiles, scripts, and config; do not assume a language or runner:

| Need | Resolve from |
|---|---|
| Build / compile command | project manifest and its documented scripts |
| Formatter and linter | project config files, or the ecosystem default already in use |
| Test command | test config present in the repo |
| Warning baseline | output of the build command before any change |
| Local suppression syntax | the language's own mechanism (see §6) |

For monorepos, resolve per module and do not mix modules in a batch.

## 2. Preflight

🛑 **STOP — do not edit a single file until all three pass.** If any of them fails, report which one and wait for the user:

- Working tree is clean, or the user confirms the existing changes should be carried along.
- The project builds green **before** any changes. Never start batch-fixing on a project that does not build — the build is the only verification signal available in later steps.
- Work happens on a dedicated branch, created if needed.

## 3. Resolve the environment

Resolve workspace root, MCP connection, server URL, and project key from the conversation and repository configuration. Ask only when deterministic discovery fails; never guess a project key.

## 4. Fetch and triage

Fetch all open issues with the largest practical page size, retaining only key, rule, severity, type, file, line, and message. Query Security Hotspots and Quality Gate concurrently where supported.

Group by severity → rule → file. Process Blocker/Critical/High before Medium/Low; combine compatible same-file fixes and fetch each rule definition once per round.

Read the affected symbol and the context a fix needs — its definition, its callers, and the blast radius; broaden only when needed.

## 5. Sensitive regions — do not rewrite

Treat these as **sensitive** because correctness may depend on structure the analyzer cannot model:

- **Bytecode/IL manipulation or runtime patching** — instruction matching, code generation, interception hooks
- **Reflection/metaprogramming** — string-resolved members, annotations, decorators, or conventions
- **Order/timing-dependent code** — initialization, lifecycle hooks, concurrency primitives
- **Native, FFI, or serialization boundaries** — contract-sensitive order, layout, or naming
- **Generated, vendored, or third-party** sources

In sensitive regions, allow only semantics-preserving fixes such as null/bounds checks, resource release, or a genuine shared-state race fix. **Skip and report** changes to control flow, signatures, declaration order, or instruction sequences for human review.

Detect sensitivity by behavior, not a fixed path list. Record and consistently reuse any reliable repository convention discovered.

## 6. Fix, or justify

Fix at the source by default. Two legitimate exceptions:

**Suppress in place** only when the rule conflicts with design intent. Use the language's narrowest-scope mechanism, name the rule, and include a reason; never use blanket or file-wide suppression:

```
<local suppression directive> <rule id>  // reason: why this rule does not apply here
```

For cognitive complexity in a single linear narrative (instruction matcher, state machine, parser dispatch), use this test: **extract an honestly nameable unit; if the best name is `part2`, suppress instead.** Tedious work alone never justifies suppression.

**Leave open** false positives, third-party findings, and issues that cannot be fixed safely. List every suppression and left-open issue individually with its reason.

## 7. Verify each batch

After each file/module batch, run that module's formatter, linter, and build. Then:

- **With tests:** run targeted tests; *source-fixed* requires a clean build and passing tests.
- **Without tests:** *source-fixed* requires a clean build, no warnings beyond baseline, and no sensitive-region change. Never invent tests. Mark changes needing host/runtime verification **pending manual smoke test** and give concrete steps.

Resolve red verification inside the causing batch; never carry it forward:

| Trigger | First fix | If that still fails |
|---|---|---|
| Batch-caused build/lint failure | Correct and rerun the same checks | Revert to the last checkpoint; mark issues **left-open** with the failure |
| Build failure unexplained by the diff | Rerun the §2 baseline at the last checkpoint | If pre-existing, 🛑 **STOP and report**; the verification signal is gone |
| New warnings without tests | Fix or narrow until back at baseline | Revert; mark **pending manual smoke test** and quote warnings |
| Previously passing tests fail | Fix within the batch | Revert; never weaken, edit, or skip tests to pass |

Checkpoint-commit each passing batch; never commit red verification.

## 8. Rescan

After all batches, run the full build and test suite once, then the toolchain-appropriate SonarScanner.

Use `SONAR_TOKEN` only from the system environment. Pass it by reference so its value never appears in commands or output:

| Shell | Reference |
|---|---|
| PowerShell | `-Dsonar.token=$env:SONAR_TOKEN` |
| POSIX shell | `-Dsonar.token=$SONAR_TOKEN` |

If the scanner reads `SONAR_TOKEN` itself, pass no token argument.

If unset/empty, skip rescanning but continue source fixes from the MCP report. State that confirmation awaits external analysis; do not request or search elsewhere for a token.

If the scanner exits non-zero, report the failing line and keep locally verified results. Never retry rejected authentication or ask for credentials.

After a successful scan, poll every 15 seconds for at most 5 minutes. On timeout, report submitted-but-unconfirmed and retain local *source-fixed* results. On success, compare unresolved/new issues by **issue-key set difference**, never total count.

🛑 **STOP if expected keys remain.** Diagnose branch, scanner module coverage, and rule mismatch. Allow at most three automatic scan rounds; after the third, report remaining keys and each round's changes, then wait for the user.

## 9. Report

Report, each as its own section:

- Files changed
- **Source-fixed** issues (verified locally) — kept distinct from **SonarQube-confirmed** closures
- Pending manual smoke tests, with steps
- Suppressed issues, each with its justification
- Left-open issues, each with its reason
- Verification commands run, scan status, Quality Gate status

Never present a closed issue, a cleared warning, or a green Quality Gate as a defect reduction or a quality improvement. Closure evidences that a rule stopped triggering, not that the code has fewer faults — the two are weakly related, and analyzer severity is not a fault forecast. Report what was actually verified (build, tests, scan status) and let it stand on its own.

Do not print complete issue lists or logs unless asked.
