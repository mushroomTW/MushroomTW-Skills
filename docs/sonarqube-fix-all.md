# Fix All SonarQube Issues

**English** | [繁體中文](sonarqube-fix-all.zh.md)

> This document lives in `docs/`. The skill itself is at [`sonarqube-fix-all/SKILL.md`](../sonarqube-fix-all/SKILL.md).

Batch-fix the quality and security issues reported by a self-hosted SonarQube instance through an already-configured SonarQube MCP connection, verify each batch, rescan, and report honestly on what was fixed, what was suppressed, and what was left alone.

Language-agnostic. It handles projects with no automated test suite, and protects semantically sensitive code — bytecode/IL manipulation, runtime patching, reflection-driven code — from unsafe rewrites.

To connect a project to a local SonarQube first, use [local-sonarqube-setup](local-sonarqube-setup.md).

## When It Applies

Invoke it explicitly by name — this skill is manual-trigger-only and never auto-triggers, even when a request mentions SonarQube issues or a failing quality gate. Its frontmatter declares `disable-model-invocation: true`, so the host never fires it on its own:

```text
/sonarqube-fix-all
```

## Constraints

- The analysis server is **self-hosted SonarQube in Docker, never SonarCloud**
- Never ask the user to provide, create, display, or modify a SonarQube credential. Queries go through MCP; the scan token is read from the `SONAR_TOKEN` system environment variable and its value is never printed or logged
- **Never change an issue's status on the server.** `Accepted`, `False positive`, `Won't fix`, file exclusions, and disabling quality-profile rules are all off-limits unless the user explicitly asks for that specific reclassification
- Never reset, revert, or discard the user's existing changes. Never push
- Keep output lean: summaries and relevant excerpts, not full payloads, issue dumps, or raw logs

## Workflow

| # | Stage | Key points |
| --- | --- | --- |
| 1 | Detect the toolchain | Assume no language, build tool, or test runner; identify them from manifests and lockfiles. In a monorepo, resolve per module and keep batches within one module |
| 2 | Preflight | Working tree clean, the project **builds green before any change**, and work happens on a dedicated branch. If any fails, stop and report |
| 3 | Resolve the environment | Derive workspace root, MCP connection, server URL, and project key from the conversation, repo config, build manifest, and Docker config. **Never guess a project key** |
| 4 | Fetch and triage | Group by severity → rule → file; Blocker/Critical/High first; combine compatible fixes in the same file into one batch |
| 5 | Identify sensitive regions | See below |
| 6 | Fix, or justify | Fix at the source by default. Suppressing in place and leaving open each have explicit conditions |
| 7 | Verify each batch | Run that module's formatter, linter, and build; run tests where they exist, otherwise require a clean build with no new warnings and no sensitive region touched. Commit a checkpoint after each passing batch |
| 8 | Rescan | Full build and test suite, then SonarScanner; compare by **issue key set difference**, not totals. At most three automatic scan rounds |
| 9 | Report | Separate sections for: files changed, source-fixed issues, pending manual smoke tests, suppressed issues with justification, left-open issues with reasons, verification commands and Quality Gate status. Closure is never reported as a defect reduction |

## Sensitive Regions — Do Not Rewrite

Some code is correct in ways a static analyzer cannot see, because its correctness rests on structure the analyzer does not model. Treat as sensitive any code that is:

- **Bytecode or IL manipulation**, or runtime patching of code the project does not own — instruction-sequence matching, code generation, interception hooks
- **Reflection- or metaprogramming-driven** — members resolved by string name, or behaviour attached by annotation, decorator, or convention
- **Order- or timing-dependent** — initialization sequencing, lifecycle hooks, concurrency primitives
- **Native, FFI, or serialization boundaries** — where field order, layout, or exact naming is part of a contract
- **Generated, vendored, or third-party** sources

In sensitive regions only **semantics-preserving** edits are permitted (adding a null or bounds check, releasing a resource, fixing a genuine race). Any change to control flow, signatures, declaration order, or instruction sequences is **skipped and reported** for human review — a silent semantic change here builds fine and fails only at runtime in the user's environment.

## The Suppression Test

Suppress in place only when the rule genuinely conflicts with the design intent of that code, using the language's narrowest-scope mechanism, bound to the specific rule, with a written reason:

```txt
<local suppression directive> <rule id>  // reason: why this rule does not apply here
```

The canonical case is cognitive complexity on a single linear narrative — an instruction matcher, a protocol state machine, a parser dispatch. The test is: **if the extracted unit can be given an honest name describing what it does, extract it; if the best available name is `part2`, suppress instead.**

## Install

From the repository root, let the `skills` CLI discover supported agents and install this skill:

```bash
npx skills add . --skill sonarqube-fix-all
```

Add `--global` for personal scope; without it, the CLI installs at project scope. For a manual installation, copy `sonarqube-fix-all/` to a skills directory documented by the host instead of assuming a runtime-specific path.

> [!NOTE]
> The first `npx` invocation may download the CLI. Reload or restart the host when it only discovers skills at session start. This skill requires an already-configured SonarQube MCP connection.
