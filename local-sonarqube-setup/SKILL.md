---
name: local-sonarqube-setup
description: Connect a supported code project to a local Docker SonarQube (default http://127.0.0.1:9000), creating the project, running the analysis, and verifying the Quality Gate with the host's existing sonar-scanner or build-tool plugin. Use when the user asks to introduce, configure, run, or troubleshoot a local SonarQube analysis.
---

# Local SonarQube Setup

> Local Docker at `127.0.0.1:9000` · PowerShell on Windows · `SONAR_TOKEN` env only · no scanner install.

**TL;DR routing**

```
main language unsupported by Community Build (C/C++, Swift, Dart…)? → STOP, report (reference/languages.md §1)
pom.xml / build.gradle[.kts] exists? → use mvn/gradle plugin, not CLI
*.csproj / .sln[x]? → dotnet sonarscanner begin/build/end; token via in-process SONARQUBE_SCANNER_PARAMS (commands.md §6.1)
Java via CLI? → build first, sonar.java.binaries required
NPM / Python / Other? → sonar-scanner CLI (or Docker fallback)
shallow clone? → git fetch --unshallow before scan
Java <21 and auto-provisioning OFF? → upgrade or enable auto
```

## Invariants

1. Token only in process memory — never in args/URL/log/file; describe it only as set or not set; if it leaks, tell the user to revoke it. Read it once and run every step in the same process; no `setx`; remove it (and any `SONARQUBE_SCANNER_PARAMS` built from it) from the process only after step 7 has finished.
2. Server-side project settings (Quality Profile, Quality Gate assignment, main branch, New Code definition, visibility, tags, permissions) stay at the server defaults; change them only when the user asks.
3. Never fake Gate with `Accepted`/`False positive`/disabling rules/server-side threshold edits; never change production code/build semantics to pass.
4. Do not add services, modify CI/compose, commit or push unless explicitly asked; preserve uncommitted changes; do not overwrite unrelated files.
5. Output only non-sensitive summaries (status, key, CE, Gate, URL), never full logs; query issues/measures only on failure or request.
6. Discover language/build/coverage from repo, not defaults; Community Build loads only supported languages.

## Workflow — 4 phases, 7 steps

| Phase | Step | Action | Output | 🛑 Checkpoint |
|---|---|---|---|---|
| **A · Preflight** | 1 Discovery | Read `AGENTS.md`/README/build docs/sonar config; `git status --short`; derive language/sources/tests/reports, then run the support check in `reference/languages.md §1`. Shallow=`true`→`git fetch --unshallow`. Not git→note no rollback. | Evidence table (path→source) + supported/skipped languages | 🔴 Main language unsupported or needs a community plugin → stop and report |
| | 2 Service+Scanner+Java | `GET /api/system/status`=`UP`; `sonar-scanner --version`; `java -version` 21+ (or 11+ if auto-provisioning ON — CLI 6.0+ default). Scanner per table: Maven `mvn verify sonar:sonar` · Gradle `gradle sonar` · .NET `dotnet sonarscanner` begin→build→end, token via in-process `SONARQUBE_SCANNER_PARAMS` (`reference/commands.md §6.1`) · Other CLI. Docker CLI permission fail ≠ blocker. | `UP` + version + chosen scanner | 🔴 Confirm scanner and Java with the user when the repo mixes toolchains |
| **B · Setup** | 3 Project | Key order: `sonar.projectKey` → `.sonarlint/connectedMode.json` → git remote → dir name; sanitize `[A-Za-z0-9-_.:]` not all digits; monorepo ambiguity→ask. Name = the project's own name: existing `sonar.projectName` → name declared by the project (solution/`.csproj`, `package.json` `name`, `pyproject.toml`, `pom.xml`, `Cargo.toml`, About/manifest) → repo dir name; keep it as written, no prefixes or suffixes. Look it up with the SonarQube MCP project search when the host has one, otherwise `GET /api/projects/search` (`reference/commands.md §4`); host mismatch→stop. Reuse or `POST /api/projects/create`. | `key / name / dashboard URL` | 🔴 Key/name before create (this skill never deletes a project) |
| | 4 Config | Minimal merge into `sonar-project.properties` (create only if none). Add the language-specific keys from `reference/languages.md` (e.g. `sonar.java.binaries`, `sonar.python.version`). Exclude only confirmed artifacts, never whole `src`/`tests`. Hierarchy Global < Project < file < CLI (file/CLI not persisted; Global Exclusions cannot override). `sonar.projectBaseDir`/`project.settings` in `reference/commands.md §5`. | Diff shown | 🔴 Diff before write |
| **C · Execute** | 5 Reports | Run repo checks/tests first (report failures). Then native coverage **before** scanner; format and exact `sonar.*` key per `reference/coverage.md` (e.g. JaCoCo→`sonar.coverage.jacoco.xmlReportPaths`, LCOV→`sonar.javascript.lcov.reportPaths`, Coverlet in opencover format→`sonar.cs.opencover.reportsPaths`). Verify non-empty. None→state none. | `path (bytes, format)` list | — |
| | 6 Scan | Same process: `SONAR_HOST_URL` + `SONAR_TOKEN` → run chosen scanner. Need `EXECUTION SUCCESS` + exit 0 + key/URL match. Docker fallback: `sonar-scanner-cli` (runs as user 1000, which needs RW on every mount) with the named volume `-v sonar-cache:/opt/sonar-scanner/.sonar/cache` and `host.docker.internal` as the host (Linux also needs `--add-host=host.docker.internal:host-gateway`); see `reference/commands.md §8`. OOM→`SONAR_SCANNER_JAVA_OPTS="-Xmx512m"` (pre-6.0 `SONAR_SCANNER_OPTS`). | 3-line summary | — |
| **D · Verify** | 7 CE+Gate+Wrap | CE: parse `.scannerwork/report-task.txt` (.NET: `.sonarqube/out/.sonar/report-task.txt`) → poll `GET /api/ce/task?id=` to `SUCCESS/FAILED` (5m; timeout→report taskId+status). Gate: the SonarQube MCP Quality Gate tool when the host has one, otherwise `GET /api/qualitygates/project_status` (`reference/commands.md §7`); `ERROR`→list `name: actual vs threshold`, hand back. Confirm `ncloc` > 0; zero means nothing was analyzed, so report failure. Wrap: add `.scannerwork/`/coverage to ignore, `git diff --check`+`git status --short`, report key/Gate/imported types/URL. Debug: `sonar.scanner.internal.dumpToFile` or `Background Tasks > Show SonarScanner Context`. | `CE / Gate / URL` | — |

Execution is one process; PowerShell dot values need quotes.

## Failure handling

| Phase | Trigger | First | Still fails |
|---|---|---|---|
| A | `status`≠`UP` | `docker ps`+restart | Stop, report unreachable |
| A | shallow=`true` | `git fetch --unshallow` | Warning in summary |
| A | Java <21 auto-off | Upgrade or enable auto | Report mismatch, stop |
| C | .NET `begin`/`end` Not authorized | Confirm `SONARQUBE_SCANNER_PARAMS` was built in this same process (`commands.md §6.1`) | Follow the 401 row; never move the token to `/d:sonar.token`, a file, or output |
| C | .NET build fails between `begin` and `end` | Set the repo's documented path variables, rebuild | Report the build error; do not edit project files to force it |
| A/B | `SONAR_TOKEN` invisible | Check whether the Machine or User scope holds it (print booleans only), then load it into this process | Ask the user to generate a token in the SonarQube UI and set the system variable |
| B | 401 | Check validity → token type → scanner version → host → whitespace (`troubleshooting.md`) | Ask the user to regenerate it; never retry with the token on the command line |
| B | 403 | Report the missing `Create Projects` or `Execute Analysis` permission | Ask the user to create the project or grant it in the UI |
| B | key rejected | Replace invalid characters with `-` and confirm the result | Ask the user to pick a key |
| C | coverage missing/empty | Run native cmd, verify non-empty | State none, scan without |
| C | analyzer/format error (e.g. missing `sonar.java.binaries`) | Confirm `sonar.*` against `languages.md`/`coverage.md`/docs | Fix+rescan; never exclude the language's files to pass |
| D | CE `PENDING`/timeout | Extend poll, `api/ce/activity` | Report taskId+status |
| D | Gate `ERROR` | List `name: actual vs threshold` | Hand back, no `Accepted` |

## Never do these

| Never | Tell | Instead |
|---|---|---|
| Token in CLI/URL/log/file | Args contain token | Inherit `SONAR_TOKEN` unchanged; .NET builds `SONARQUBE_SCANNER_PARAMS` in-process; Docker uses `--env SONAR_TOKEN` with no `=value` |
| Guess coverage key | Not in `coverage.md` | Lookup exact `sonar.*` |
| Treat `NONE` as error | No prior analysis | Confirm CE `SUCCESS`, re-query |

## References

- Official — Analyzing source code: https://docs.sonarsource.com/sonarqube-community-build/analyzing-source-code — canonical.
- `reference/languages.md` — step 1 onward: supported languages, scanner per ecosystem, per-language keys and pitfalls.
- `reference/commands.md` — before step 2: commands, template, hierarchy, Docker, MCP.
- `reference/coverage.md` — before step 5: language table (B).
- `reference/troubleshooting.md` — on failure: PKIX/OOM/locale/WAF/401/403.
