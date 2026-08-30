---
name: local-sonarqube-setup
description: Connect a supported code project to a local Docker SonarQube (default http://127.0.0.1:9000), creating the project, running the analysis, and verifying the Quality Gate with the host's existing sonar-scanner or build-tool plugin. Use when the user asks to introduce, configure, run, or troubleshoot a local SonarQube analysis.
---

# Local SonarQube Setup

> Local Docker at `127.0.0.1:9000` · PowerShell on Windows · `SONAR_TOKEN` env only · no scanner install.

**TL;DR routing**

```
pom.xml / build.gradle[.kts] exists? → use mvn/gradle plugin, not CLI
*.csproj / .sln? → .NET scanner required; SONAR_TOKEN env unsupported → credential STOP
NPM / Python / Other? → sonar-scanner CLI (or Docker fallback)
shallow clone? → git fetch --unshallow before scan
Java <21 and auto-provisioning OFF? → upgrade or enable auto
```

## Invariants

1. Token only in process memory — never in args/URL/log/file; describe only as set/not set; if leaked → tell user to revoke; read once and do all steps in same process, no `setx`, clear only after verify.
2. Never fake Gate with `Accepted`/`False positive`/disabling rules/server-side threshold edits; never change production code/build semantics to pass.
3. Do not add services, modify CI/compose, commit or push unless explicitly asked; preserve uncommitted changes; do not overwrite unrelated files.
4. Output only non-sensitive summaries (status, key, CE, Gate, URL), never full logs; query issues/measures only on failure or request.
5. Discover language/build/coverage from repo, not defaults; Community Build loads only supported languages.

## Workflow — 4 phases, 7 steps

| Phase | Step | Action | Output | 🛑 Checkpoint |
|---|---|---|---|---|
| **A · Preflight** | 1 Discovery | Read `AGENTS.md`/README/build docs/sonar config; `git status --short`; derive language/sources/tests/reports. Shallow=`true`→`git fetch --unshallow`. Not git→note no rollback. | Evidence table (path→source) | — |
| | 2 Service+Scanner+Java | `GET /api/system/status`=`UP`; `sonar-scanner --version`; `java -version` 21+ (or 11+ if auto-provisioning ON — CLI 6.0+ default). Scanner per table: Maven `mvn verify sonar:sonar` · Gradle `gradle sonar` · .NET requires `dotnet sonarscanner`, but current scanner does not support env-only token transport · Other CLI. Docker CLI permission fail ≠ blocker. | `UP` + version + chosen scanner | 🔴 Scanner+Java if mixed toolchain; 🔴 .NET credential STOP |
| **B · Setup** | 3 Project | Key order: `sonar.projectKey` → `.sonarlint/connectedMode.json` → git remote → dir name; sanitize `[A-Za-z0-9-_.:]` not all digits; monorepo ambiguity→ask. Query `mcp__sonarqube__search_my_sonarqube_projects`; host mismatch→stop. Reuse or `POST /api/projects/create`. | `key / name / dashboard URL` | 🔴 Key/name before create (cannot delete) |
| | 4 Config | Minimal merge into `sonar-project.properties` (create only if none). Exclude only confirmed artifacts, never whole `src`/`tests`. Hierarchy Global < Project < file < CLI (file/CLI not persisted; Global Exclusions cannot override). `sonar.projectBaseDir`/`project.settings` in `reference/commands.md §5`. | Diff shown | 🔴 Diff before write |
| **C · Execute** | 5 Reports | Run repo checks/tests first (report failures). Then native coverage **before** scanner; format per `reference/coverage.md` (JaCoCo `jacoco.xml`→`sonar.coverage.jacoco.xmlReportPaths`, JS `lcov.info`→`sonar.javascript.lcov.reportPaths`, Python `coverage.xml`→`sonar.python.coverage.reportPaths`, .NET Coverlet/dotCover→`sonar.cs.*`, Generic→`sonar.coverageReportPaths`). Verify non-empty. None→state none. | `path (bytes, format)` list | — |
| | 6 Scan | Same process: `SONAR_HOST_URL` + `SONAR_TOKEN` → run chosen scanner. Need `EXECUTION SUCCESS` + exit 0 + key/URL match. Docker fallback: `sonar-scanner-cli` with `-v cache:/opt/sonar-scanner/.sonar/cache` (user 1000 RW, Windows→`host.docker.internal`). OOM→`SONAR_SCANNER_JAVA_OPTS="-Xmx512m"` (pre-6.0 `SONAR_SCANNER_OPTS`). | 3-line summary | — |
| **D · Verify** | 7 CE+Gate+Wrap | CE: parse `.scannerwork/report-task.txt` → poll `GET /api/ce/task?id=` to `SUCCESS/FAILED` (5m; timeout→report taskId+status). Gate: `mcp__sonarqube__get_project_quality_gate_status`; `ERROR`→list `name: actual vs threshold`, hand back. Wrap: add `.scannerwork/`/coverage to ignore, `git diff --check`+`git status --short`, report key/Gate/imported types/URL. Debug: `sonar.scanner.internal.dumpToFile` or `Background Tasks > Show SonarScanner Context`. | `CE / Gate / URL` | — |

Execution is one process; PowerShell dot values need quotes.

## Failure handling

| Phase | Trigger | First | Still fails |
|---|---|---|---|
| A | `status`≠`UP` | `docker ps`+restart | Stop, report unreachable |
| A | shallow=`true` | `git fetch --unshallow` | Warning in summary |
| A | Java <21 auto-off | Upgrade or enable auto | Report mismatch, stop |
| A | .NET scanner selected | Report that `SONAR_TOKEN` env is unsupported | Stop; never move the token to `/d:sonar.token`, a file, or output |
| A/B | `SONAR_TOKEN` invisible | Machine/User booleans, reload env | Ask UI generate |
| B | 401 | validity→type→version→host→whitespace (`troubleshooting.md`) | Regenerate, never CLI token |
| B | 403 | Report `Create Projects`/`Execute Analysis` | UI create/grant |
| B | key rejected | Sanitize →`-` confirm | Ask pick |
| C | coverage missing/empty | Run native cmd, verify non-empty | State none, scan without |
| C | analyzer/format error | Confirm `sonar.*` vs docs | Fix+rescan |
| D | CE `PENDING`/timeout | Extend poll, `api/ce/activity` | Report taskId+status |
| D | Gate `ERROR` | List `name: actual vs threshold` | Hand back, no `Accepted` |

## Never do these

| Never | Tell | Instead |
|---|---|---|
| Token in CLI/URL/log/file | Args contain token | Inherit `SONAR_TOKEN` unchanged; Docker uses `--env SONAR_TOKEN` with no `=value` |
| Guess coverage key | Not in `coverage.md` | Lookup exact `sonar.*` |
| Treat `NONE` as error | No prior analysis | Confirm CE `SUCCESS`, re-query |

## References

- Official — Analyzing source code: https://docs.sonarsource.com/sonarqube-community-build/analyzing-source-code — canonical.
- `reference/commands.md` — before step 2: commands, template, hierarchy, Docker, MCP.
- `reference/coverage.md` — before step 5: language table (B).
- `reference/troubleshooting.md` — on failure: PKIX/OOM/locale/WAF/401/403.
