# Local SonarQube Setup

**English** | [繁體中文](local-sonarqube-setup.zh.md)

> This document lives in `docs/`. The skill itself is at [`local-sonarqube-setup/SKILL.md`](../local-sonarqube-setup/SKILL.md).

Initial setup of a project on a **local Docker SonarQube** instance (default `http://127.0.0.1:9000`): create the project, write the scan configuration, generate native coverage reports, and run the first analysis to confirm it works.

The skill stops once the first analysis succeeds. It reports the Quality Gate status as-is, and fixing issues or a failing Quality Gate is out of scope.

## When It Applies

Triggered when the user asks to connect, onboard, or set up a repository with a local SonarQube, or when that first setup fails.

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
- **Default Server Settings**: Quality Profile, Quality Gate, and other server-side settings are left at their defaults unless the user asks to change them; projects are never deleted.
- **Preserve User Changes**: Always preserve existing uncommitted workspace modifications.

The complete list is in the Rules section of [`SKILL.md`](../local-sonarqube-setup/SKILL.md).

## Workflow

| # | Step | Key Points |
| --- | --- | --- |
| 1 | **Discover** | Read `AGENTS.md`, README, build files, and existing Sonar config; list the languages and stop if the main one is not supported by Community Build. |
| 2 | **Check Server & Scanner** | `GET /api/system/status` returns `UP`; pick the scanner for the ecosystem and confirm it runs. |
| 3 | **Create Project** | Derive the key and the project's own name, reuse an existing project, otherwise confirm with the user and create it. |
| 4 | **Write Configuration** | Minimally merge into `sonar-project.properties` (or `begin` arguments for .NET), add language keys, and show the diff before writing. |
| 5 | **Generate Coverage** | Run the repo's own tests and coverage tool, then check that the report has real content. |
| 6 | **First Analysis** | Run the scanner in the same process as the token; it must exit 0 and report success. |
| 7 | **Confirm** | CE task reaches `SUCCESS`, `ncloc` > 0, and the Quality Gate status is reported as-is; add scan artifacts to the ignore rules. |

## References

- [`reference/languages.md`](../local-sonarqube-setup/reference/languages.md) — Languages supported by Community Build, the scanner for each ecosystem, and per-language required properties, coverage keys, and pitfalls (read from Step 1 onward).
- [`reference/commands.md`](../local-sonarqube-setup/reference/commands.md) — PowerShell snippets for each step, including the `sonar-project.properties` template and the .NET flow.
- [`reference/troubleshooting.md`](../local-sonarqube-setup/reference/troubleshooting.md) — Diagnostic and recovery steps when an execution step fails.

## Install

From the repository root, use the `skills` CLI to discover supported agent hosts and install this skill:

```bash
npx skills add . --skill local-sonarqube-setup
```

Add `--global` for personal user scope; omitting it installs at project scope. For manual installation, copy `local-sonarqube-setup/` directly into your agent host's configured skills directory.

> [!NOTE]
> The initial `npx` invocation may download the CLI. Reload or restart your agent host if it only discovers skills during session startup.
