# Commands

PowerShell snippets for each step. Run them in order **inside one process** so the token stays in that process's memory.

## 1. Token and auth header

```powershell
if ([string]::IsNullOrWhiteSpace($env:SONAR_TOKEN)) { throw 'SONAR_TOKEN is not set' }
$env:SONAR_HOST_URL = 'http://127.0.0.1:9000'   # change only when the user or existing config says so
$pair    = "$($env:SONAR_TOKEN):"
$headers = @{ Authorization = "Basic $([Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($pair)))" }
```

Never print `$pair` or `$headers`, and never put them in an error message. Do not use `setx` or write the token anywhere.

## 2. Server and scanner check

```powershell
(Invoke-RestMethod "$env:SONAR_HOST_URL/api/system/status").status   # must be UP
sonar-scanner --version            # or: mvn -v / gradle -v / dotnet sonarscanner --version
git rev-parse --is-shallow-repository   # true → git fetch --unshallow
```

The Docker CLI lacking permissions is not a blocker while HTTP reaches the server.

## 3. Project lookup and creation

Use the SonarQube MCP project search when the host has it. Otherwise:

```powershell
(Invoke-RestMethod -Headers $headers -Uri "$env:SONAR_HOST_URL/api/projects/search?projects=$projectKey").components
```

Create it only when it does not exist, after the user confirmed key and name:

```powershell
Invoke-RestMethod -Method Post -Headers $headers -Uri "$env:SONAR_HOST_URL/api/projects/create" `
    -Body @{ project = $projectKey; name = $projectName }
```

Dashboard: `$env:SONAR_HOST_URL/dashboard?id=$projectKey`. A Gate of `NONE` before the first analysis is normal.

## 4. Configuration and first analysis

### 4.1 `sonar-project.properties` (CLI, NPM, Python)

Put it in the repo root, merge into an existing file instead of overwriting, and write it with a file-editing tool:

```properties
sonar.projectKey=my-project-key
sonar.projectName=My Project
sonar.sourceEncoding=UTF-8
sonar.sources=.
# only confirmed build output, caches and binaries
sonar.exclusions=**/bin/**,**/obj/**,**/dist/**,**/build/**,**/target/**,**/node_modules/**,**/.venv/**,**/coverage/**,**/.scannerwork/**
# language and coverage keys from languages.md §3
```

Add `sonar.tests` only when the test directory is confirmed. The token and host URL never go in this file. Maven and Gradle read these settings from the build file or `-D` options instead.

### 4.2 SonarScanner CLI

```powershell
sonar-scanner
if ($LASTEXITCODE -ne 0) { throw "sonar-scanner failed: $LASTEXITCODE" }
```

Success means exit code 0, `EXECUTION SUCCESS`, and the expected key and server URL in the log.

Docker fallback when no host scanner exists:

```powershell
docker run --rm -e SONAR_HOST_URL="http://host.docker.internal:9000" --env SONAR_TOKEN `
  -v "${PWD}:/usr/src" sonarsource/sonar-scanner-cli
```

`--env SONAR_TOKEN` has no `=value`, so the token is inherited, not typed. Inside the container `localhost` is the container itself; on Linux add `--add-host=host.docker.internal:host-gateway`.

### 4.3 SonarScanner for .NET (C# / VB.NET)

`begin` does not read `SONAR_TOKEN`, and the documented `/d:sonar.token=...` would expose it in process arguments, so never use that form. Build `SONARQUBE_SCANNER_PARAMS` in the same process instead. Tested with scanner 12.1.0 and Community Build 26.11: `begin` authenticates through it, `end` accepts it, and the token is not written to disk. Re-test when the scanner's major version changes.

```powershell
$params = @{}
if ($env:SONARQUBE_SCANNER_PARAMS) {
    ($env:SONARQUBE_SCANNER_PARAMS | ConvertFrom-Json).PSObject.Properties | ForEach-Object { $params[$_.Name] = $_.Value }
}
$params['sonar.token'] = $env:SONAR_TOKEN
$env:SONARQUBE_SCANNER_PARAMS = $params | ConvertTo-Json -Compress

dotnet sonarscanner begin /k:$projectKey "/n:$projectName" "/d:sonar.host.url=$env:SONAR_HOST_URL" `
    "/d:sonar.cs.opencover.reportsPaths=**/coverage.opencover.xml"   # only when coverage exists
if ($LASTEXITCODE -ne 0) { throw "begin failed: $LASTEXITCODE" }
dotnet build <solution-or-project>                                    # the repo's own build
if ($LASTEXITCODE -ne 0) { throw "build failed: $LASTEXITCODE" }
dotnet test <test-project> --no-build --settings <repo-runsettings>   # coverage, when the repo has tests
if ($LASTEXITCODE -ne 0) { throw "tests failed: $LASTEXITCODE" }
dotnet sonarscanner end
if ($LASTEXITCODE -ne 0) { throw "end failed: $LASTEXITCODE" }
```

- `sonar-project.properties` is ignored; pass settings to `begin` with `/d:`. Run `begin` and `end` from the same directory.
- Coverlet needs PDBs. A configuration with `DebugType=none` (often `Release`) gives a report with no modules, so use one that emits symbols (usually the default `Debug`).
- If the build needs local paths, set the environment variables the repo documents instead of editing project files.

## 5. Confirm and wrap up

```powershell
$reportTask = if (Test-Path .sonarqube\out\.sonar\report-task.txt) { '.sonarqube\out\.sonar\report-task.txt' } else { '.scannerwork\report-task.txt' }
$report = @{}
Get-Content $reportTask | ForEach-Object { if ($_ -match '^([^=]+)=(.*)$') { $report[$Matches[1]] = $Matches[2] } }

$deadline = (Get-Date).AddMinutes(5)
do {
    $status = (Invoke-RestMethod -Headers $headers -Uri "$env:SONAR_HOST_URL/api/ce/task?id=$($report['ceTaskId'])").task.status
    if ($status -in 'SUCCESS','FAILED','CANCELED') { break }
    Start-Sleep -Seconds 5
} while ((Get-Date) -lt $deadline)

(Invoke-RestMethod -Headers $headers -Uri "$env:SONAR_HOST_URL/api/measures/component?component=$projectKey&metricKeys=ncloc,coverage").component.measures
(Invoke-RestMethod -Headers $headers -Uri "$env:SONAR_HOST_URL/api/qualitygates/project_status?projectKey=$projectKey").projectStatus.status
```

The SonarQube MCP tools (measures, Quality Gate status) can replace the last two calls. Report the Gate as-is, even `ERROR`; fixing it is not part of setup.

Finally, add `.scannerwork/`, `.sonarqube/` and coverage output to the ignore rules, then clean up:

```powershell
git diff --check; git status --short
Remove-Item Env:SONAR_TOKEN, Env:SONARQUBE_SCANNER_PARAMS -ErrorAction SilentlyContinue
```
