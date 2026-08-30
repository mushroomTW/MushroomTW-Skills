# Commands and configuration templates

PowerShell first, with the Bash equivalent where one is needed. Every snippet is expected to run in order **inside a single process**, so the token stays in that process's memory.

## 1. Service and scanner check

```powershell
$env:SONAR_HOST_URL = 'http://127.0.0.1:9000'   # override only when the user or existing configuration specifies another address
(Invoke-RestMethod "$env:SONAR_HOST_URL/api/system/status").status   # must be UP
sonar-scanner --version
```

Stop when `status` is not `UP` and deal with the server first; HTTP being reachable while the Docker CLI lacks permissions is not a blocker.

### 1.5 SCM checkout check (shallow clone)

```powershell
git rev-parse --is-shallow-repository  # true → shallow, blame will be skipped
# fix
git fetch --unshallow
# verify
git rev-parse --is-shallow-repository  # must be false
```

Official prerequisite: `analyzing-source-code/overview.md` — full clone required.

### 1.6 Scanner selection and Java runtime

**Selection table** — from `scanners/scanner-environment/general-requirements.md`:

| Build system | Scanner | Command |
|---|---|---|
| Maven | SonarScanner for Maven | `mvn verify sonar:sonar` |
| Gradle | SonarScanner for Gradle | `gradle sonar` |
| .NET / MSBuild | SonarScanner for .NET | Credential STOP: current scanner requires a token property and does not support `SONAR_TOKEN` |
| NPM | SonarScanner for NPM | `sonar-scanner` via npm |
| Python | SonarScanner for Python | `sonar-scanner` / `pysonar` |
| Other | SonarScanner CLI | `sonar-scanner` |

> CLI cannot analyze C# / VB.NET — must use Scanner for .NET.

**Java runtime**:

```powershell
java -version
sonar-scanner --version  # check embedded JRE / auto-provisioning notes
```

| Scanner | Auto-provisioning ON | Auto-provisioning OFF |
|---|---|---|
| Maven / Gradle | Java 11+ (auto) | Java 21+ (17 removed) |
| CLI 7.2+ | Java 11+ (auto) | Java 21+ |
| CLI <7.2 | Java 17+ (auto) | Java 21+ |
| .NET / NPM / Python | n/a | Java 21+ |

Auto-provisioning downloads scanner engine + analyzers at analysis time from the server (see `analysis-overview.md#scanner-engine-and-analyzers-download`). When ON, no manual upgrade is needed. When OFF, ensure `JAVA_HOME` points to 21+.

```powershell
# when build needs different Java than scanner
$env:JAVA_HOME = "C:\Program Files\Java\jdk-21"
```

Troubleshoot with `SONAR_SCANNER_JAVA_OPTS` vs `SONAR_SCANNER_OPTS` distinction in §6.

## 2. Authentication check and cleanup

`SONAR_TOKEN` is the standard variable name SonarScanner reads, supplied directly by the system environment; no extra mapping is needed.

> [!CAUTION]
> SonarScanner for .NET currently does not support `SONAR_TOKEN` and documents `/d:sonar.token=...`. That would expose the expanded secret in process arguments, so this skill stops on .NET instead of using the documented argument or writing a token file.

```powershell
if ([string]::IsNullOrWhiteSpace($env:SONAR_TOKEN)) {
    throw 'Environment variable SONAR_TOKEN is not set. Generate a user token in SonarQube, set SONAR_TOKEN as a system environment variable, then reopen the shell.'
}
```

Bash equivalent:

```bash
[ -n "$SONAR_TOKEN" ] || { echo 'SONAR_TOKEN is not set'; exit 1; }
```

Clear it only after every step (verification included) has finished — clearing it too early makes the later API calls fail:

```powershell
Remove-Item Env:SONAR_TOKEN -ErrorAction SilentlyContinue
```

Do not use `setx`; do not write it to any file.

## 3. Web API authentication header

Use this only where no MCP tool covers the need (creating a project, for example).

```powershell
$pair    = "$($env:SONAR_TOKEN):"
$basic   = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($pair))
$headers = @{ Authorization = "Basic $basic" }
```

SonarQube 10 and later also accepts `@{ Authorization = "Bearer $($env:SONAR_TOKEN)" }`.

Never `echo $headers`, `$pair`, or `$basic`, and never put `$headers` into an error message or a delivery summary.

## 4. Project lookup and creation

Prefer MCP for the lookup: `mcp__sonarqube__search_my_sonarqube_projects`. Fallback when it is unavailable:

```powershell
(Invoke-RestMethod -Headers $headers `
    -Uri "$env:SONAR_HOST_URL/api/projects/search?projects=$projectKey").components
```

Create it only when it does not exist and the token holds the `Create Projects` permission (no MCP tool covers this):

```powershell
$projectKey  = 'my-project-key'
$projectName = 'My Project'
Invoke-RestMethod -Method Post -Headers $headers `
    -Uri "$env:SONAR_HOST_URL/api/projects/create" `
    -Body @{ project = $projectKey; name = $projectName }
```

Query again after creating to confirm, and note the dashboard URL: `$env:SONAR_HOST_URL/dashboard?id=$projectKey`. A Quality Gate of `NONE` before the first analysis is normal.

## 5. `sonar-project.properties` template

Merge minimally into existing configuration instead of overwriting the whole file. Put it in the repository root and write it with a file-editing tool, not shell redirection.

```properties
sonar.projectKey=my-project-key
sonar.projectName=My Project
sonar.sourceEncoding=UTF-8

# source scope confirmed against the actual files
sonar.sources=.

# build output, dependency caches, coverage output, scanner work directory, VCS directories, binary assets
sonar.exclusions=**/bin/**,**/obj/**,**/dist/**,**/build/**,**/out/**,**/target/**,\
  **/node_modules/**,**/vendor/**,**/.venv/**,**/venv/**,\
  **/coverage/**,**/*.lcov,**/.scannerwork/**,**/.git/**,\
  **/*.dll,**/*.exe,**/*.so,**/*.dylib,**/*.jar,**/*.png,**/*.jpg,**/*.pdf,**/*.zip
```

### 5.1 Parameter hierarchy (from `analysis-parameters/configuration-overview.md`)

Precedence low → high: **Global (UI)** < **Project (UI)** < **Scanner config file** (`sonar-project.properties`, `pom.xml`, `build.gradle`, `.csproj`) < **Scanner CLI args** (`-Dsonar.*`). Env vars are overridden by CLI args. Notes:

- CLI/file values are **not persisted** to DB — only UI values are. Next analysis without the same args reverts.
- `Global Source File Exclusions` / `Global Test File Exclusions` cannot be overridden at project level.
- Property keys are case-sensitive.
- In PowerShell, quote any value containing a dot: `'-Dsonar.projectKey=my-key'`.

### 5.2 Alternative locations

- CLI args: `sonar-scanner -Dsonar.projectKey=myproject -Dsonar.sources=src1`
- Alternate base dir: `sonar.projectBaseDir=/path/to/subproject` (then `sonar.sources` is relative to it)
- Alternate config file: `sonar-scanner -Dproject.settings=../myproject.properties` (resolved relative to **launch dir**, not `projectBaseDir`)
- `sonar.projectKey` is mandatory either in file or CLI

### 5.3 Language-specific reports

Never guess a property name. Use `reference/coverage.md` table and confirm against `analyzing-source-code/test-coverage/*` for your SonarQube version. Common keys (verify!):

- Java: `sonar.coverage.jacoco.xmlReportPaths`
- JS/TS: `sonar.javascript.lcov.reportPaths`
- Python: `sonar.python.coverage.reportPaths`
- .NET: `sonar.cs.dotcover.reportsPaths` / `sonar.cs.vscoveragexml.reportsPaths`
- PHP: `sonar.php.coverage.reportPaths`
- Generic: `sonar.coverageReportPaths`

When there is no report to import, state plainly that none is provided.

### 5.4 Scope notes

- `sonar.host.url` can come from `SONAR_HOST_URL` env; writing it into the file is not required, token never goes in this file.
- Exclusions cover only artifacts you can confirm; never exclude an entire language directory, the test directory, or unknown source code.
- Add `sonar.tests` only when test directory and classification are confirmed.
- Community Build loads only files for supported languages — unrecognized extensions are silently ignored.

## 6. Run the scan

```powershell
sonar-scanner
if ($LASTEXITCODE -ne 0) { throw "sonar-scanner failed with exit code $LASTEXITCODE" }
```

The output must satisfy all of: it contains `EXECUTION SUCCESS`, the exit code is 0, and the project key and server URL in the log match what you expect. Keep only the success/failure summary; do not return the full scanner log.

**Out-of-memory**: increase heap via `SONAR_SCANNER_JAVA_OPTS` (CLI 6.0+) or `SONAR_SCANNER_OPTS` (older):

```powershell
$env:SONAR_SCANNER_JAVA_OPTS = "-Xmx512m"   # Windows: no double quotes
# or
$env:SONAR_SCANNER_JAVA_OPTS = "-Xmx1024m"
```

Debug dump: `sonar-scanner -Dsonar.scanner.internal.dumpToFile=dump.properties` (also in UI `Background Tasks > Show SonarScanner Context`).

## 7. Verify the CE task and the Quality Gate

Parse `report-task.txt` for the CE task id:

```powershell
$report = @{}
Get-Content .scannerwork\report-task.txt | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') { $report[$Matches[1]] = $Matches[2] }
}
$ceTaskId = $report['ceTaskId']
```

Poll until a terminal state or the timeout:

```powershell
$deadline = (Get-Date).AddMinutes(5)
do {
    $status = (Invoke-RestMethod -Headers $headers `
        -Uri "$env:SONAR_HOST_URL/api/ce/task?id=$ceTaskId").task.status
    if ($status -in 'SUCCESS','FAILED','CANCELED') { break }
    Start-Sleep -Seconds 5
} while ((Get-Date) -lt $deadline)
$status
```

Prefer MCP for the Quality Gate: `mcp__sonarqube__get_project_quality_gate_status`. Fallback when it is unavailable:

```powershell
(Invoke-RestMethod -Headers $headers `
    -Uri "$env:SONAR_HOST_URL/api/qualitygates/project_status?projectKey=$projectKey").projectStatus.status
```

On `ERROR`, list the name and value of each failing condition; do not change the Quality Gate rules yourself.

## 8. Docker fallback

When host `sonar-scanner` is unavailable, use the Docker image (no install needed):

```powershell
docker run --rm `
  -e SONAR_HOST_URL="http://host.docker.internal:9000" `
  --env SONAR_TOKEN `
  -v "${PWD}:/usr/src" `
  sonarsource/sonar-scanner-cli
```

Cache to avoid re-downloading analyzers each run:

```powershell
docker run --rm `
  -v "${PWD}/.sonar-cache:/opt/sonar-scanner/.sonar/cache" `
  -v "${PWD}:/usr/src" `
  -e SONAR_HOST_URL="http://host.docker.internal:9000" `
  --env SONAR_TOKEN `
  sonarsource/sonar-scanner-cli
# also via SONAR_USER_HOME
$env:SONAR_USER_HOME = "C:/cache/sonar"
```

> Ensure user 1000 has RW on mounted dirs; otherwise permission errors. On Windows use `host.docker.internal` not `localhost` when SonarQube runs in Docker.

## 9. Preferred MCP tools

| Need | Tool |
| --- | --- |
| Find projects | `mcp__sonarqube__search_my_sonarqube_projects` |
| Quality Gate status | `mcp__sonarqube__get_project_quality_gate_status` |
| Issues | `mcp__sonarqube__search_sonar_issues_in_projects` |
| Measures | `mcp__sonarqube__get_component_measures` |
| Branches | `mcp__sonarqube__list_branches` |
| Create a project | No MCP tool; only `POST /api/projects/create` |

Query issues and measures only when verification fails or the user asks.

## 10. Working-tree wrap-up

```powershell
git diff --check
git status --short
```

Add `.scannerwork/`, coverage output, and any other scan artifacts to the appropriate ignore rules. Do not run `git commit` or `git push` unless the user explicitly asks.
