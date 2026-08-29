---
name: local-sonarqube-setup
description: Connect any code project to a local Docker SonarQube (default http://127.0.0.1:9000), creating the project, running the analysis, and verifying the Quality Gate with the host's existing sonar-scanner or the build tool's sonar plugin. Use when the user asks to introduce, configure, run, or troubleshoot a local SonarQube analysis.
---

# Local SonarQube Setup

## Assumptions

- The execution environment is the current Windows host; commands run in PowerShell.
- SonarQube is at `http://127.0.0.1:9000` by default; override it only when the user or existing configuration says otherwise.
- A directly runnable `sonar-scanner` is already installed on the host; JVM projects go through the build tool's sonar plugin instead (see step 2). This skill does not install, download, or replace a scanner.
- Authentication comes from the system environment variable `SONAR_TOKEN`. Language, build system, and how coverage is produced are always discovered from what the repository actually contains; no default language assumptions.
- SCM checkout is a full clone. Shallow clones skip blame and may fail analysis — check with `git rev-parse --is-shallow-repository` and run `git fetch --unshallow` when needed.
- Java runtime for the scanner is 21+ (or 11+ when JRE auto-provisioning is active). Version is verified in step 2 before any scan.

## Hard rules

- The token exists only in the memory of the current process. It must never reach command-line arguments, URLs, logs, `sonar-project.properties`, or any reply; describe it externally only as set or not set, never its length, prefix, or any part of its value.
- Read `SONAR_TOKEN` once and finish the query, creation, scan, and verification inside that same process. Do not use `setx`; clear the `SONAR_TOKEN` process variable only after every step has finished.
- If the token has ever appeared in chat, a commit, a log, or any other uncontrolled place, tell the user to revoke and reissue it once done; "it is only a local token" is not a reason to skip this.
- Do not add SonarQube or database services, modify CI or compose files, commit, or push (unless the user explicitly asks).
- Do not change runtime behavior, public APIs, production code, or build semantics for the sake of the scan.
- Never fake completion with `Accepted`, `False positive`, or by disabling rules.
- Preserve the user's existing uncommitted changes; do not overwrite, reset, or delete files unrelated to this task.
- Keep output to non-sensitive summaries — HTTP status, project key, CE task status, Quality Gate, dashboard URL — never the full scanner log or API response.
- Query issues, measures, and detailed logs only when verification fails or the user asks; after the initial discovery, read only the configuration blocks and report summaries you need, never reloading the whole repository, a full scanner log, or a complete API response.

## Workflow

1. **Discovery** — *Input*: `AGENTS.md`, README, build/test docs, existing sonar config. *Output*: language, sources, tests, report formats. *Format*: table of confirmed paths.
   - Read `AGENTS.md`, README, build/test docs, and any existing sonar configuration; run `git status --short`.
   - Derive language, source directories, test layout, and report formats from those docs or manifests, not from guesswork.
   - `git rev-parse --is-shallow-repository` returns `true` → shallow clone → run `git fetch --unshallow` before analysis, otherwise blame is skipped. `git rev-parse` fails (not a git repository) → skip every git check in steps 1 and 7, and state in the delivery summary that there is no version-control safety net, so the changes leave no rollback trail.
   - Completion: evidence table exists; every path traces to a manifest or doc.

2. **Confirm the service and the scanner** — *Input*: `SONAR_HOST_URL`, scanner binary. *Output*: server `UP`, scanner version, Java version, chosen scanner variant. *Format*: one-line summary each.
   - `GET /api/system/status` must return `UP`; record the scanner version with `sonar-scanner --version` (401 troubleshooting needs it). HTTP being reachable while the Docker CLI lacks permissions is not a blocker.
   - Verify Java: `java -version` must be 21+; if JRE auto-provisioning is enabled (CLI 6.0+ default, CLI 7.2+ requires 11+) no manual upgrade is needed — detect via `sonar-scanner --version` output and cache at `.sonar/cache`. If auto-provisioning is disabled or unsupported (NPM/.NET/Python scanners), require 21+ explicitly. See `reference/commands.md §1.6` and official `general-requirements.md`.
   - Choose scanner by build system (see `reference/commands.md §1.6` selection table):

     | Build system | Scanner |
     |---|---|
     | Maven | `mvn verify sonar:sonar` (SonarScanner for Maven) |
     | Gradle | `gradle sonar` (SonarScanner for Gradle) |
     | .NET / MSBuild | SonarScanner for .NET |
     | NPM | SonarScanner for NPM |
     | Python | SonarScanner for Python |
     | Other | `sonar-scanner` CLI |

     `pom.xml` or `build.gradle[.kts]` detected → use that build tool's sonar plugin rather than the CLI `sonar-scanner`: the CLI cannot read bytecode for a JVM project, and the analysis silently degrades to text-only rules. When both are present, follow the project's actual build command.
   - 🔴 **CHECKPOINT — scanner variant and Java version**: report chosen scanner + Java version and wait for user confirmation if the project mixes toolchains.

3. **Find or create the project** — *Input*: existing config, git remote, dir name. *Output*: confirmed project key/name, dashboard URL. *Format*: `key / name / url`.
   - **Decide the key**: take, in order, `sonar.projectKey` from an existing `sonar-project.properties` → `.sonarlint/connectedMode.json` → the repo name from the git remote → the directory name. Replace whitespace and illegal characters with `-` (only alphanumerics plus `-`, `_`, `.`, `:` are allowed, and the key cannot be all digits). A monorepo subproject, or an ambiguous conversion → ask the user first.
   - **Query**: use `mcp__sonarqube__search_my_sonarqube_projects`. The MCP connection and the scanner must point at the same server; a result that disagrees with `SONAR_HOST_URL` → stop and report, never mix data from the two.
   - **Reuse or create**: if the project exists, verify its key/name and reuse it; only call `POST /api/projects/create` when it does not. 🔴 **CHECKPOINT — give the user the key and name and wait for a reply before creating**: this workflow cannot delete a project once it exists. After creating, query again and note the dashboard URL. Insufficient permissions → report which permission is missing and ask the user to create the project in the UI.

4. **Scan configuration** — *Input*: existing `sonar-project.properties`, discovery table. *Output*: merged config file. *Format*: diff shown to user.
   - Merge minimally into existing configuration instead of overwriting the whole file; create a root `sonar-project.properties` only when there is none. 🔴 **CHECKPOINT — show the user the full content or the merge diff and wait before writing**: this touches the user's repo.
   - Exclude build output, dependency caches, coverage output, the scanner work directory, VCS directories, and binary assets; never exclude an entire language directory, the test directory, or unknown source code. Parameter hierarchy is Global < Project < Scanner config file < Scanner CLI args (`reference/commands.md §5.1`); CLI/file values are not persisted to DB, and Global Source/Test Exclusions cannot be overridden. Template and `sonar.projectBaseDir` / `project.settings` alternatives in `reference/commands.md §5`.
   - For Community Build, only files recognized by the edition are loaded — unrecognized extensions are silently ignored (see `analysis-overview.md`).

5. **Produce the reports** — *Input*: toolchain from step 1. *Output*: non-empty coverage/test reports on disk. *Format*: `path (bytes, format)` list.
   - First run the repository's own format checks, static analysis, and tests (report failures first, and do not pass SonarQube findings off as test fixes), then produce coverage with the project's native tooling **before** the SonarScanner step.
   - Coverage must match the scanner's expected format per language — see `reference/coverage.md` (B 選項對照表) and canonical `test-coverage/overview.md`. Confirm the report paths exist, files are non-empty, and temporary artifacts fall within the ignore rules. When there is no report to import, state plainly that none is provided — never create an empty placeholder.

6. **Run the scan** — *Input*: merged config, reports, `SONAR_HOST_URL`+`SONAR_TOKEN` in process. *Output*: `EXECUTION SUCCESS`, exit 0, matching key/url. *Format*: 3-line summary.
   - Inside a single process, set `SONAR_HOST_URL`, confirm `SONAR_TOKEN` is in effect, then run the chosen scanner (`sonar-scanner` or build-tool plugin). You must confirm the output contains `EXECUTION SUCCESS`, the exit code is 0, and the project key and server URL match what you expect.
   - Docker fallback (when host scanner unavailable): `docker run --rm -e SONAR_HOST_URL -e SONAR_TOKEN -v repo:/usr/src sonarsource/sonar-scanner-cli` with cache `-v cache:/opt/sonar-scanner/.sonar/cache` (user 1000 needs RW). See `reference/commands.md §8`.
   - On `OutOfMemoryError` set `SONAR_SCANNER_JAVA_OPTS="-Xmx512m"` (CLI 6.0+, older uses `SONAR_SCANNER_OPTS`); on Windows avoid double quotes.

7. **Verify and wrap up** — *Input*: `.scannerwork/report-task.txt`, server URL. *Output*: CE status, Quality Gate, delivery report. *Format*: `CE / Gate / dashboard URL`.
   - **CE task**: take the task id from `.scannerwork/report-task.txt` and poll `GET /api/ce/task?id=` until `SUCCESS` or `FAILED`. Timeout (5 minutes by default) → treat it as unfinished rather than failed; report the task id and the last status and ask the user to re-check later, instead of re-running to paper over it.
   - **Quality Gate**: query it with `mcp__sonarqube__get_project_quality_gate_status`. `ERROR` → list every failing condition's name, actual value, and threshold, then stop and hand the choice — fix the code and rescan, or accept it as is — back to the user; do not touch production code, Quality Gate settings, or exclusions without consent.
   - **Wrap-up**: add `.scannerwork/` and coverage artifacts to the ignore rules, then confirm with `git diff --check` and `git status --short` that only the expected configuration and documentation changes remain. Report the project key/name, the analysis result, the Quality Gate status, which report types were actually imported, and the dashboard URL.
   - Debug aid: `sonar.scanner.internal.dumpToFile=<path>` dumps all resolved properties; equivalent is `Project Settings > Background Tasks > Show SonarScanner Context`.

## Failure recovery

| Trigger | First-line fix | If that still fails |
|---|---|---|
| `GET /api/system/status` ≠ `UP` | Check Docker container `docker ps`, restart SonarQube, re-check URL | Report server unreachable, stop — do not edit config to hide it |
| `git rev-parse --is-shallow-repository` = `true` | `git fetch --unshallow` then re-run analysis | Report shallow clone and its blame impact, keep analysis warning in summary |
| `java -version` < 21 and auto-provisioning off | Upgrade to 21 or enable auto-provisioning (CLI 6.0+) | Report Java mismatch, stop — do not downgrade scanner |
| `SONAR_TOKEN` not visible in process | Check Machine/User scope booleans, reload env or reopen shell (`reference/troubleshooting.md`) | Ask user to generate token in UI |
| HTTP 401 | Walk 401 checklist in `reference/troubleshooting.md` (validity → token type → scanner version → host → whitespace) | Ask user to regenerate token; never put token in CLI args |
| HTTP 403 | Report missing `Create Projects` / `Execute Analysis` permission | Ask user to create project / grant in UI, stop |
| Project key format rejected | Sanitize whitespace → `-`, confirm with user | Ask user to choose key explicitly |
| Coverage report missing/empty | Run native coverage command, verify path non-empty (`reference/coverage.md`) | State no coverage provided, scan without it — never create placeholder |
| Analyzer / report format error | Confirm property name vs analyzer docs (canonical `analyzing-source-code`) | Keep non-sensitive error summary, fix property, rescan |
| CE task `PENDING` / timeout | Extend polling, check `api/ce/activity` and container memory | Report taskId + last status, ask user to re-check later |
| Quality Gate `ERROR` | List each condition `name: actual vs threshold` | Hand choice back — fix code or accept as-is, no silent `Accepted` |

## Never do these

| Never do this | How to catch yourself | Do this instead |
|---|---|---|
| Put `SONAR_TOKEN` in `-Dsonar.token=xxx` CLI args, URLs, logs, or `sonar-project.properties` | Command line contains token value or its prefix/length | Use `SONAR_TOKEN` env var in same process; pass `-Dsonar.token=$env:SONAR_TOKEN` by reference or let scanner inherit env |
| Degrade JVM analysis by using CLI for Maven/Gradle/.NET projects | `pom.xml` / `build.gradle` exists but you run `sonar-scanner` | Use `mvn verify sonar:sonar` / `gradle sonar` / `dotnet sonarscanner` |
| Guess a coverage property name | Property not found in `reference/coverage.md` or official `test-coverage/*` | Look up the exact `sonar.*` key for that language/version |
| Exclude an entire language dir / test dir for convenience | Exclusion contains `src/**` or `tests/**` | Exclude only build/dependency/binary artifacts you confirmed |
| Fake success with `Accepted` / `False positive` / disabling rules | Quality Gate `ERROR` but you change server state | List failing conditions, hand choice back, fix source and rescan |
| Overwrite `sonar-project.properties` wholesale | Diff shows unrelated keys removed | Merge minimally, show diff, wait for checkpoint |
| Treat `Quality Gate = NONE` as error | Project has no prior analysis | Confirm CE `SUCCESS`, re-query; if still `NONE` query measures |

## References

- Official docs — Analyzing source code (SonarQube Community Build): https://docs.sonarsource.com/sonarqube-community-build/analyzing-source-code — property 名稱、報告格式與掃描器行為以此為準，版本差異以官方文件為權威依據。
- Read `reference/commands.md` before entering step 2: PowerShell commands, the `sonar-project.properties` template, scanner selection table, parameter hierarchy, and MCP tool table.
- Read `reference/coverage.md` before entering step 5: language-specific coverage property table and report paths (B 選項落地).
- Read `reference/troubleshooting.md` only when a step fails: 401/403/PKIX/OOM/locale/WAF diagnosis.
