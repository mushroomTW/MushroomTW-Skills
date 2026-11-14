# Local SonarQube Setup

**English** | [繁體中文](local-sonarqube-setup.zh.md)

> This document lives in `docs/`. The skill itself is at [`local-sonarqube-setup/SKILL.md`](../local-sonarqube-setup/SKILL.md).

Connect a supported software project to a **local Docker SonarQube** instance (default `http://127.0.0.1:9000`): create the project, generate native test coverage reports, execute code analysis, and verify the Quality Gate.

This skill configures the connection and runs the analysis workflow; it does not apply automatic code fixes to reported issues.

## When It Applies

Triggered when the user requests to set up, configure, execute, or troubleshoot a local SonarQube analysis pipeline.

## Assumptions

- The host environment is the current Windows machine; commands run in PowerShell.
- SonarQube instance defaults to `http://127.0.0.1:9000`, overridden only when explicitly specified.
- A runnable `sonar-scanner` is already installed and available in the system PATH — **this skill does not install, download, or replace scanners**.
- Authentication credentials must be provided via the `SONAR_TOKEN` system environment variable. SonarScanner for .NET does not read `SONAR_TOKEN` in its `begin` step, so the skill builds a `SONARQUBE_SCANNER_PARAMS` JSON variable inside the same process. Tokens never appear in CLI arguments or files.
- Languages, build tools, and coverage generation mechanisms are dynamically discovered from actual repository contents; no speculative language assumptions are made.
- The SonarQube project name is the project's own name (from existing Sonar config, the build manifest, or the repository name). Server-side settings such as Quality Profile, Quality Gate, main branch, and New Code definition stay at the server defaults unless the user asks to change them.

## Hard Rules (Excerpt)

- **Strict Token Safety**: The token resides exclusively in process memory. It must never appear in command-line arguments, URLs, log outputs, `sonar-project.properties`, or conversation replies; externally, it is referenced only as "set" or "not set".
- **Zero Extraneous Modifications**: Do not spin up SonarQube or database containers, modify CI/CD pipelines or Compose files, commit code, or push changes unless explicitly directed.
- **Production Code Integrity**: Do not alter runtime behavior, public APIs, production logic, or build semantics merely to satisfy a scanner.
- **Uncompromised Quality Gate**: Never bypass quality gates or fake a pass via `Accepted`, `False positive`, or rule suppressions.
- **Preserve User Changes**: Always preserve existing uncommitted workspace modifications.

The complete list of operational rules is detailed in the Hard Rules section of [`SKILL.md`](../local-sonarqube-setup/SKILL.md).

## Workflow

| # | Step | Key Points |
| --- | --- | --- |
| 1 | **Discovery** | Inspect `AGENTS.md`, README, build documentation, and existing Sonar configurations; execute `git status --short`; deduce language and test layout from build manifests. |
| 2 | **Confirm Service & Scanner** | Validate `GET /api/system/status` returns `UP`; verify and record the local scanner version. |
| 3 | **Find or Create Project** | Query existing projects via MCP (or REST API fallback); only issue `POST /api/projects/create` if absent, then record the dashboard URL. |
| 4 | **Configure Scan** | Minimally merge necessary properties into existing config without overwriting; exclude build outputs and caches, never exclude test directories or whole language trees. |
| 5 | **Produce Reports** | Execute native project checks and unit tests first, then generate coverage reports using native tooling; verify report files exist and are non-empty. |
| 6 | **Execute Analysis** | Set `SONAR_HOST_URL` and `SONAR_TOKEN` within a single process scope; ensure `EXECUTION SUCCESS` and exit code 0. |
| 7 | **Verify & Wrap Up** | Extract the Compute Engine task ID from `.scannerwork/report-task.txt`, poll until completion, inspect Quality Gate status, and add generated scan artifacts to ignore rules. |

## References

- [`reference/languages.md`](../local-sonarqube-setup/reference/languages.md) — Languages supported by Community Build, the scanner for each ecosystem, and per-language required properties and pitfalls (read from Step 1 onward).
- [`reference/commands.md`](../local-sonarqube-setup/reference/commands.md) — PowerShell command templates, `sonar-project.properties` configuration templates, and MCP tool mappings. (Required reading before Step 2).
- [`reference/troubleshooting.md`](../local-sonarqube-setup/reference/troubleshooting.md) — Diagnostic and recovery steps when an execution step fails.

## Install

From the repository root, use the `skills` CLI to discover supported agent hosts and install this skill:

```bash
npx skills add . --skill local-sonarqube-setup
```

Add `--global` for personal user scope; omitting it installs at project scope. For manual installation, copy `local-sonarqube-setup/` directly into your agent host's configured skills directory.

> [!NOTE]
> The initial `npx` invocation may download the CLI. Reload or restart your agent host if it only discovers skills during session startup.
