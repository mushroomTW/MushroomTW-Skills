---
name: sonarqube-fix-all
description: Batch-fix code quality and security issues reported by a self-hosted SonarQube instance via an already-configured SonarQube MCP connection, then verify and rescan. Use whenever the user asks to fix, clear, triage, or work through SonarQube issues, or mentions their Sonar quality gate failing. Language-agnostic; handles projects with no automated test suite, and protects semantically sensitive code such as bytecode/IL manipulation, runtime patching, and reflection-driven code from unsafe rewrites.
---

# Fix All SonarQube Issues

Batch-resolve SonarQube findings at the source, verify each batch, and report honestly on what was fixed, what was suppressed with justification, and what was left alone.

## Constraints

These hold for the entire workflow:

- The analysis server is **self-hosted SonarQube in Docker**, never SonarCloud. Never ask for a SonarCloud organization key or apply SonarCloud-specific setup.
- Never ask the user to provide, create, display, or modify a SonarQube credential. Use the configured MCP connection for queries, and read the scan token from the `SONAR_TOKEN` system environment variable. Never print, echo, or log its value.
- Never change an issue's status on the server. `Accepted`, `False positive`, `Won't fix`, file exclusions, and disabling rules in the quality profile are all off-limits unless the user explicitly asks for that specific reclassification.
- Never reset, revert, or discard the user's existing changes. Never push.
- Keep output lean: summaries and relevant excerpts, not full payloads, issue dumps, or raw logs.

## 1. Detect the project's toolchain

Do not assume a language, build tool, or test runner. Identify them from the manifest and lockfiles present, then use whatever that ecosystem provides. Determine and record:

| Need | Resolve from |
|---|---|
| Build / compile command | project manifest and its documented scripts |
| Formatter and linter | project config files, or the ecosystem default already in use |
| Test command | test config present in the repo |
| Warning baseline | output of the build command before any change |
| Local suppression syntax | the language's own mechanism (see §5) |

If several toolchains coexist in a monorepo, resolve them per module and keep batches within a single module.

## 2. Preflight

🛑 **STOP — do not edit a single file until all three pass.** If any of them fails, report which one and wait for the user:

- Working tree is clean, or the user confirms the existing changes should be carried along.
- The project builds green **before** any changes. Never start batch-fixing on a project that does not build — the build is the only verification signal available in later steps.
- Work happens on a dedicated branch, created if needed.

## 3. Resolve the environment

Determine the workspace root, MCP connection, server URL, and project key from the conversation, the SonarQube configuration in the repo, the build manifest, and the Docker configuration. Ask only when deterministic discovery fails — never guess a project key.

## 4. Fetch and triage

Pull all open issues using the largest practical page size, retaining only key, rule, severity, type, file, line, and message. Query Security Hotspots and Quality Gate status concurrently where supported.

Group by severity, then rule, then file. Process Blocker/Critical/High before Medium/Low, combining compatible fixes within the same file into one batch. Fetch each rule definition at most once per round.

Prefer code-graph or symbol tools to locate definitions, callers, and impact. Read the affected symbol plus necessary context only; broaden the search only when those tools fall short.

## 5. Sensitive regions — do not rewrite

Some code is correct in ways a static analyzer cannot see, because its correctness depends on structure the analyzer does not model. Treat as **sensitive** any code that is:

- **Bytecode or IL manipulation**, or runtime patching of code the project does not own — instruction-sequence matching, code generation, and interception hooks
- **Reflection- or metaprogramming-driven**, where members are resolved by string name, or behaviour is attached by annotation, decorator, or convention rather than by a call the analyzer can see
- **Order- or timing-dependent**, such as initialization sequencing, lifecycle hooks, and concurrency primitives
- **Native, FFI, or serialization boundaries**, where field order, layout, or exact naming is part of a contract
- **Generated, vendored, or third-party** sources

In sensitive regions, only **semantics-preserving** edits are permitted: adding a null or bounds check, releasing a resource, fixing a genuine race on shared state. Any change to control flow, signatures, declaration order, or instruction sequences is **skipped and reported** for human review — a silent semantic change here builds fine and fails only at runtime in the user's environment.

Detect sensitive code from what it does, not from a fixed path list. If a repository convention makes it identifiable (a directory, an annotation, a naming pattern), note it and apply it consistently for the rest of the run.

## 6. Fix, or justify

Fix at the source by default. Two legitimate exceptions:

**Suppress in place** when the rule genuinely conflicts with the design intent of that code. Use the language's own narrowest-scope mechanism, attached to the specific rule and carrying a written reason — never a blanket or file-wide suppression:

```
<local suppression directive> <rule id>  // reason: why this rule does not apply here
```

The canonical case is cognitive complexity on a routine that is a single linear narrative — an instruction matcher, a protocol state machine, a parser dispatch — where splitting it forces the reader to reassemble the order across several helpers. Apply this test everywhere: **if the extracted unit can be given an honest name describing what it does, extract it; if the best available name is `part2`, suppress instead.** Cognitive complexity is a real defect-correlated signal, not a style rule — do not suppress it merely because the fix is tedious.

**Leave open** when the finding is a false positive, belongs to third-party code, or cannot be fixed safely.

Every suppressed and every left-open issue is listed individually in the final report with its reason.

## 7. Verify each batch

After each file or module batch, run only that module's formatter, linter, and build. Then:

- **With an automated test suite:** run the targeted tests. An issue is *source-fixed* when the build is clean and its tests pass.
- **Without one** — common for plugins, mods, embedded targets, and anything whose behaviour depends on a runtime host: an issue is *source-fixed* when the build is clean with no new warnings against the baseline and the change touched no sensitive region. Do not invent tests to satisfy this step. Changes needing in-application verification are marked **pending manual smoke test**, with concrete steps listed in the report.

When that verification comes back red, resolve it inside the batch that caused it — never carry a red build into the next batch:

| Trigger | First fix | If that still fails |
|---|---|---|
| Build or lint fails after a batch and the batch's own diff explains it | Correct it within the same batch, re-run the same verification | Revert the batch to the last checkpoint commit, mark its issues **left-open** with the failure quoted, continue with the next batch |
| Build fails but the diff does not explain it | Re-run the §2 baseline build on the last checkpoint commit to establish whether this batch caused it | Failure is pre-existing → 🛑 **STOP and report**: the verification signal is gone, so no later batch can be called source-fixed |
| New warnings against the §1 baseline, on a project with no test suite | Not source-fixed — fix the warning or narrow the change until the count returns to baseline | Revert the batch, mark it **pending manual smoke test**, and list the warnings verbatim |
| Tests that passed before the batch now fail | Fix within the batch | Revert the batch. Never edit, weaken, or skip a test to make a batch pass |

Commit a checkpoint after each passing batch so a later regression can be bisected. Never commit a batch whose verification did not come back clean.

## 8. Rescan

After the batch set completes, run the full build and any full test suite once, then run SonarScanner — using the scanner variant appropriate to the toolchain detected in §1.

The scan token comes from the `SONAR_TOKEN` system environment variable, never from a repo file, a prompt, or the conversation. Pass it by reference so the value never appears in a command line, in output, or in the transcript:

| Shell | Reference |
|---|---|
| PowerShell | `-Dsonar.token=$env:SONAR_TOKEN` |
| POSIX shell | `-Dsonar.token=$SONAR_TOKEN` |

Where the scanner reads `SONAR_TOKEN` on its own, just let the inherited environment supply it and pass no token argument at all.

If `SONAR_TOKEN` is unset or empty in the environment, skip rescanning, continue fixing from the current MCP report, and state that confirmation awaits the next externally triggered analysis. Report only that the variable is unset — never request a token, never read it from elsewhere, and never halt the fix workflow over its absence.

If the scanner itself exits non-zero — server unreachable, authentication rejected, no scanner variant for this toolchain — report the failing error line, skip rescanning, and keep the locally verified results. Never retry a rejected authentication, and never route around it by asking the user for a credential.

After a successful scan, poll the analysis task until it reports success — at 15-second intervals, for at most 5 minutes. If it has not finished by then, report the scan as submitted but unconfirmed and leave the local *source-fixed* results standing. Then fetch unresolved and newly introduced issues and compare by **issue key set difference**, not by total count — a flat count can hide equal numbers of issues closed and introduced.

🛑 **STOP if the expected keys did not close.** Diagnose instead of retrying blindly; the usual causes are a scan that analysed a different branch, a module the scanner did not include, or a fix that did not address what the rule actually flagged. At most three automatic scan rounds — if keys remain open after the third, hand back the remaining key set with what each round changed, and start no further fix pass without the user.

## 9. Report

Report, each as its own section:

- Files changed
- **Source-fixed** issues (verified locally) — kept distinct from **SonarQube-confirmed** closures
- Pending manual smoke tests, with steps
- Suppressed issues, each with its justification
- Left-open issues, each with its reason
- Verification commands run, scan status, Quality Gate status

Do not print complete issue lists or logs unless asked.