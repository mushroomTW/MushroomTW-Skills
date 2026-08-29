---
name: local-sonarqube-setup
description: Connect any code project to a local Docker SonarQube (default http://127.0.0.1:9000), creating the project, running the analysis, and verifying the Quality Gate with the host's existing sonar-scanner or the build tool's sonar plugin. Use when the user asks to introduce, configure, run, or troubleshoot a local SonarQube analysis.
---

# Local SonarQube Setup

## Assumptions

- Execution is on Windows host, PowerShell.
- SonarQube at `http://127.0.0.1:9000` unless config says otherwise.
- Host already has runnable `sonar-scanner`; JVM projects use build-tool plugin (step 2). No scanner install/replacement.
- Auth via `SONAR_TOKEN` env. Language/build/coverage inferred from repo, no defaults.
- SCM is full clone: `git rev-parse --is-shallow-repository`=`true` → `git fetch --unshallow`, else blame skipped.
- Java 21+ (or 11+ with JRE auto-provisioning). Verified in step 2.

## Hard rules

- Token lives only in current process memory; never in args, URLs, logs, `sonar-project.properties`, or replies. Describe only as set/not set.
- Read `SONAR_TOKEN` once, do query/create/scan/verify in same process. No `setx`; clear only after all steps done.
- If token ever leaked to chat/log/commit, tell user to revoke and reissue.
- Do not add services, modify CI/compose, commit or push unless user explicitly asks.
- Do not change runtime behavior, public APIs, production code, or build semantics for the scan.
- Never fake with `Accepted`/`False positive`/disabling rules.
- Preserve uncommitted changes; do not overwrite unrelated files.
- Output only non-sensitive summaries (HTTP status, key, CE, Gate, URL), never full logs.
- Query issues/measures only on failure or request; otherwise read only config blocks and summaries.

## Workflow

1. **Discovery**: read `AGENTS.md`, README, build/test docs, existing sonar config; `git status --short`. Derive language/sources/tests/reports from manifests, not guesswork. Shallow → `git fetch --unshallow`. Not a git repo → skip git checks and note no rollback trail.
2. **Confirm service and scanner**: `GET /api/system/status` must be `UP`; `sonar-scanner --version` (needed for 401). Docker CLI no permission ≠ blocker.
   - Java: `java -version` 21+; auto-provisioning ON (CLI 6.0+ default, 7.2+ needs 11+) → auto, else require 21+. See `reference/commands.md §1.6`.
   - Scanner table: Maven→`mvn verify sonar:sonar`, Gradle→`gradle sonar`, .NET→Scanner for .NET, NPM/Python/Other→CLI. CLI cannot read bytecode → degrades JVM analysis. Follow actual build command.
   - 🔴 **CHECKPOINT — scanner + Java**: report variant + Java, confirm if mixed toolchain.
3. **Find or create project**: key order `sonar.projectKey` → `.sonarlint/connectedMode.json` → git remote → dir name; sanitize to `[A-Za-z0-9-_.:]`, not all digits; monorepo ambiguity → ask. Query via `mcp__sonarqube__search_my_sonarqube_projects`; host mismatch → stop. Reuse if exists; else `POST /api/projects/create`. 🔴 **CHECKPOINT — key/name before create**: cannot delete; verify dashboard `.../dashboard?id=$key`; 403 → report permission.
4. **Scan configuration**: minimally merge into `sonar-project.properties`; create only if none. 🔴 **CHECKPOINT — show diff before write**. Exclude only confirmed artifacts (build/dependency/coverage/`.scannerwork`/`.git`/binaries); never whole language/test dir. Hierarchy: Global < Project < file < CLI args (file/CLI not persisted; Global Exclusions cannot be overridden). See `reference/commands.md §5` for template + `sonar.projectBaseDir`/`project.settings`. Community Build loads only supported languages.
5. **Produce reports**: run repo's own checks/tests first (report failures), then native coverage **before** scanner. Coverage format must match `reference/coverage.md` per language (canonical `test-coverage/*`); verify paths exist and non-empty. No report → state none, never placeholder.
6. **Run scan**: in same process set `SONAR_HOST_URL`, confirm `SONAR_TOKEN`, run chosen scanner. Must see `EXECUTION SUCCESS`, exit 0, key/URL match. Docker fallback `sonar-scanner-cli` with cache `-v cache:/opt/sonar-scanner/.sonar/cache` (user 1000 RW, `host.docker.internal` on Windows). OOM → `SONAR_SCANNER_JAVA_OPTS="-Xmx512m"` (pre-6.0 `SONAR_SCANNER_OPTS`).
7. **Verify and wrap up**: CE from `.scannerwork/report-task.txt` poll `GET /api/ce/task?id=` to `SUCCESS/FAILED` (5m timeout → report taskId + status, re-check later). Gate via `mcp__sonarqube__get_project_quality_gate_status`; `ERROR` → list `name: actual vs threshold`, hand back choice. Wrap: add `.scannerwork/`/coverage to ignore, `git diff --check` + `git status --short`, report key/name, Gate, imported report types, dashboard URL. Debug: `sonar.scanner.internal.dumpToFile` or `Background Tasks > Show SonarScanner Context`.

## Failure recovery

| Trigger | Fix | Still fails |
|---|---|---|
| `status`≠`UP` | `docker ps` + restart | Report unreachable, stop |
| shallow=`true` | `git fetch --unshallow` | Keep warning in summary |
| Java <21 auto-off | Upgrade 21 or enable auto | Report mismatch, stop |
| `SONAR_TOKEN` invisible | Check Machine/User booleans, reload env | Ask to generate token |
| 401 | Checklist validity→type→version→host→whitespace (`troubleshooting.md`) | Regenerate token, never CLI args |
| 403 | Report `Create Projects`/`Execute Analysis` | Ask UI create/grant |
| key rejected | Sanitize →`-`, confirm | Ask user to pick |
| coverage missing/empty | Run native cmd, verify non-empty (`coverage.md`) | State none, scan without |
| analyzer/format error | Confirm `sonar.*` vs docs | Fix property, rescan |
| CE `PENDING`/timeout | Extend poll, `api/ce/activity` | Report taskId+status |
| Gate `ERROR` | List `name: actual vs threshold` | Hand back, no `Accepted` |

## Never do these

| Never | Tell | Instead |
|---|---|---|
| Token in CLI/URL/log/file | Args contain token | Env var in same process, `-Dsonar.token=$env:SONAR_TOKEN` or inherit |
| CLI for Maven/Gradle/.NET | `pom.xml` exists but `sonar-scanner` | `mvn sonar:sonar` / `gradle sonar` / `dotnet sonarscanner` |
| Guess coverage key | Not in `coverage.md` | Lookup exact `sonar.*` |
| Exclude whole `src`/`tests` | Exclusion=`src/**` | Only confirmed artifacts |
| Fake Gate with `Accepted` | Gate `ERROR` → server edit | List conditions, fix source |
| Overwrite properties wholesale | Diff removes keys | Minimal merge + checkpoint |
| Treat `NONE` as error | No prior analysis | Confirm CE `SUCCESS`, re-query |

## References

- Official — Analyzing source code: https://docs.sonarsource.com/sonarqube-community-build/analyzing-source-code — property/format/behavior canonical.
- `reference/commands.md` — before step 2: commands, template, selection table, hierarchy, MCP list.
- `reference/coverage.md` — before step 5: language coverage table (B).
- `reference/troubleshooting.md` — on failure: 401/403/PKIX/OOM/locale/WAF.
