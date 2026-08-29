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

1. **Discovery**: read `AGENTS.md`, the README, build/test docs, and any existing sonar configuration; run `git status --short`. Derive language, source directories, test layout, and report formats from those docs or manifests, not from guesswork. `git rev-parse` fails (not a git repository) → skip every git check in steps 1 and 7, and state in the delivery summary that there is no version-control safety net, so the changes leave no rollback trail.
2. **Confirm the service and the scanner**: `GET /api/system/status` must return `UP`, and record the scanner version with `sonar-scanner --version` (401 troubleshooting needs it). HTTP being reachable while the Docker CLI lacks permissions is not a blocker. `pom.xml` or `build.gradle[.kts]` detected → use that build tool's sonar plugin (`mvn verify sonar:sonar`, `gradle sonar`) rather than the CLI `sonar-scanner`: the CLI cannot read bytecode for a JVM project, and the analysis silently degrades to text-only rules. When both are present, follow the project's actual build command.
3. **Find or create the project**:
   - **Decide the key**: take, in order, `sonar.projectKey` from an existing `sonar-project.properties` → `.sonarlint/connectedMode.json` → the repo name from the git remote → the directory name. Replace whitespace and illegal characters with `-` (only alphanumerics plus `-`, `_`, `.`, `:` are allowed, and the key cannot be all digits). A monorepo subproject, or an ambiguous conversion → ask the user first.
   - **Query**: use `mcp__sonarqube__search_my_sonarqube_projects`. The MCP connection and the scanner must point at the same server; a result that disagrees with `SONAR_HOST_URL` → stop and report, never mix data from the two.
   - **Reuse or create**: if the project exists, verify its key/name and reuse it; only call `POST /api/projects/create` when it does not. 🔴 **CHECKPOINT — give the user the key and name and wait for a reply before creating**: this workflow cannot delete a project once it exists. After creating, query again and note the dashboard URL. Insufficient permissions → report which permission is missing and ask the user to create the project in the UI.
4. **Scan configuration**: merge minimally into existing configuration instead of overwriting the whole file; create a root `sonar-project.properties` only when there is none. 🔴 **CHECKPOINT — show the user the full content or the merge diff and wait before writing**: this touches the user's repo. Exclude build output, dependency caches, coverage output, the scanner work directory, VCS directories, and binary assets; never exclude an entire language directory, the test directory, or unknown source code. Template in `reference/commands.md`.
5. **Produce the reports**: first run the repository's own format checks, static analysis, and tests (report failures first, and do not pass SonarQube findings off as test fixes), then produce coverage with the project's native tooling. Confirm the report paths exist, the files are non-empty, and temporary artifacts fall within the ignore rules.
6. **Run the scan**: inside a single process, set `SONAR_HOST_URL`, confirm `SONAR_TOKEN` is in effect, then run `sonar-scanner`. You must confirm the output contains `EXECUTION SUCCESS`, the exit code is 0, and the project key and server URL match what you expect.
7. **Verify and wrap up**:
   - **CE task**: take the task id from `.scannerwork/report-task.txt` and poll `GET /api/ce/task?id=` until `SUCCESS` or `FAILED`. Timeout (5 minutes by default) → treat it as unfinished rather than failed; report the task id and the last status and ask the user to re-check later, instead of re-running to paper over it.
   - **Quality Gate**: query it with `mcp__sonarqube__get_project_quality_gate_status`. `ERROR` → list every failing condition's name, actual value, and threshold, then stop and hand the choice — fix the code and rescan, or accept it as is — back to the user; do not touch production code, Quality Gate settings, or exclusions without consent.
   - **Wrap-up**: add `.scannerwork/` and coverage artifacts to the ignore rules, then confirm with `git diff --check` and `git status --short` that only the expected configuration and documentation changes remain. Report the project key/name, the analysis result, the Quality Gate status, which report types were actually imported, and the dashboard URL.

## References

- Read `reference/commands.md` before entering step 2: PowerShell commands, the `sonar-project.properties` template, and the MCP tool table.
- Read `reference/troubleshooting.md` only when a step fails.
