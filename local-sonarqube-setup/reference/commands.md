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
| .NET / MSBuild | SonarScanner for .NET | `dotnet sonarscanner begin` → build → `end`, token via `SONARQUBE_SCANNER_PARAMS` (§6.1) |
| NPM | SonarScanner for NPM (`@sonar/scan`) | `npx @sonar/scan` |
| Python | SonarScanner for Python (`pysonar`) | `pysonar` |
| Rust / Cargo | SonarScanner for Cargo | `cargo sonar-scanner` (needs the community Rust plugin) |
| Other | SonarScanner CLI | `sonar-scanner` |

> CLI cannot analyze C# / VB.NET — must use Scanner for .NET. Per-language requirements (Java binaries, Node.js, Python version, unsupported languages) are in `reference/languages.md`.

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
| .NET / NPM / Python | none (no host Java needed) | Java 21+ |

Auto-provisioning downloads scanner engine + analyzers at analysis time from the server (see `analysis-overview.md#scanner-engine-and-analyzers-download`). When ON, no manual upgrade is needed. When OFF, ensure `JAVA_HOME` points to 21+.

```powershell
# when build needs different Java than scanner
$env:JAVA_HOME = "C:\Program Files\Java\jdk-21"
```

Troubleshoot with `SONAR_SCANNER_JAVA_OPTS` vs `SONAR_SCANNER_OPTS` distinction in §6.

## 2. Authentication check and cleanup

`SONAR_TOKEN` is the standard variable name SonarScanner reads, supplied directly by the system environment; no extra mapping is needed.

> [!CAUTION]
> SonarScanner for .NET's `begin` step does not read `SONAR_TOKEN`, and the docs show `/d:sonar.token=...`, which would expose the secret in process arguments. Never use that form. Use the env-only path in §6.1 instead: build `SONARQUBE_SCANNER_PARAMS` inside the same process from `SONAR_TOKEN`. Tested November 2026 with scanner 12.1.0 against Community Build 26.11 with forced authentication: `begin` authenticates only through `SONARQUBE_SCANNER_PARAMS`; `end` accepts either variable and fails with neither; no file under the working tree contains the token afterwards. Re-test when the scanner's major version changes.

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
Remove-Item Env:SONARQUBE_SCANNER_PARAMS -ErrorAction SilentlyContinue   # only if §6.1 built it
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

Never guess a property name. Coverage keys are listed only in `reference/coverage.md`; analysis keys such as `sonar.java.binaries`, `sonar.python.version` and `sonar.nodejs.executable` are in `reference/languages.md`. Confirm against `analyzing-source-code/test-coverage/*` for your SonarQube version.

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

### 6.1 SonarScanner for .NET (C# / VB.NET)

`sonar-project.properties` is not read here. Project settings go to `begin` as `/k:`, `/n:` and `/d:sonar.*=` arguments; credentials never do. Build the JSON variable inside the same process so the token never appears in arguments, files or output, and merge any existing value instead of overwriting it:

```powershell
$params = @{}
if ($env:SONARQUBE_SCANNER_PARAMS) {
    ($env:SONARQUBE_SCANNER_PARAMS | ConvertFrom-Json).PSObject.Properties | ForEach-Object { $params[$_.Name] = $_.Value }
}
$params['sonar.token'] = $env:SONAR_TOKEN
$env:SONARQUBE_SCANNER_PARAMS = $params | ConvertTo-Json -Compress

dotnet sonarscanner begin /k:$projectKey "/n:$projectName" "/d:sonar.host.url=$env:SONAR_HOST_URL" `
    "/d:sonar.cs.opencover.reportsPaths=**/coverage.opencover.xml"   # only when coverage exists (coverage.md)
if ($LASTEXITCODE -ne 0) { throw "begin failed: $LASTEXITCODE" }
dotnet build <solution-or-project>    # the repo's own build command and configuration
if ($LASTEXITCODE -ne 0) { throw "build failed: $LASTEXITCODE" }
dotnet test <test-project> --no-build --settings <repo-runsettings>   # only when the repo has tests; produces coverage
if ($LASTEXITCODE -ne 0) { throw "tests failed: $LASTEXITCODE" }
dotnet sonarscanner end
if ($LASTEXITCODE -ne 0) { throw "end failed: $LASTEXITCODE" }
```

- Success means all three exit codes are 0 and `end` logs `ANALYSIS SUCCESSFUL` with the expected dashboard URL.
- `begin` and `end` must run from the same directory. `.sonarqube/` is the scanner work directory; add it to the ignore rules at wrap-up.
- Collect coverage between `begin` and `end`. Prefer the repo's own runsettings. Without one, use `dotnet test --collect "XPlat Code Coverage" -- DataCollectionRunSettings.DataCollectors.DataCollector.Configuration.Format=opencover`.
- Coverlet needs PDBs. A configuration with `DebugType=none` (often `Release`) yields a report with no modules, so build and test in a configuration that emits symbols (usually the default `Debug`). Do not edit the project to add them.
- If the build needs local paths (game installs, SDK locations), set the environment variables the repo documents (e.g. in `Directory.Build.props`) instead of editing project files.

## 7. Verify the CE task and the Quality Gate

Parse `report-task.txt` for the CE task id:

```powershell
$report = @{}
$reportTask = if (Test-Path .sonarqube\out\.sonar\report-task.txt) { '.sonarqube\out\.sonar\report-task.txt' } else { '.scannerwork\report-task.txt' }   # .NET vs other scanners
Get-Content $reportTask | ForEach-Object {
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

Cache to avoid re-downloading analyzers each run. A named volume keeps the cache out of the working tree:

```powershell
docker run --rm `
  -v "sonar-cache:/opt/sonar-scanner/.sonar/cache" `
  -v "${PWD}:/usr/src" `
  -e SONAR_HOST_URL="http://host.docker.internal:9000" `
  --env SONAR_TOKEN `
  sonarsource/sonar-scanner-cli
# also via SONAR_USER_HOME
$env:SONAR_USER_HOME = "C:/cache/sonar"
```

> The container runs as user 1000, which needs RW on the mounted source directory and on the cache volume; otherwise permission errors. If the first run fails writing the cache, fix the volume's ownership once: `docker run --rm -u 0 -v sonar-cache:/c alpine chown -R 1000:1000 /c`. Inside the container `localhost` is the container itself, so use `host.docker.internal`. Docker Desktop (Windows, macOS) resolves it by default; on Linux add `--add-host=host.docker.internal:host-gateway` to the `docker run` line.

## 9. Preferred MCP tools

The names below are how Claude Code exposes the SonarQube MCP server; other hosts name the same tools differently. Without an MCP connection, use the REST fallbacks in §4 and §7.

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
