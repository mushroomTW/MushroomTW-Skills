# Commands and configuration templates

PowerShell first, with the Bash equivalent where one is needed. Every snippet is expected to run in order **inside a single process**, so the token stays in that process's memory.

## 1. Service and scanner check

```powershell
$env:SONAR_HOST_URL = 'http://127.0.0.1:9000'   # override only when the user or existing configuration specifies another address
(Invoke-RestMethod "$env:SONAR_HOST_URL/api/system/status").status   # must be UP
sonar-scanner --version
```

Stop when `status` is not `UP` and deal with the server first; HTTP being reachable while the Docker CLI lacks permissions is not a blocker.

## 2. Authentication check and cleanup

`SONAR_TOKEN` is the standard variable name SonarScanner reads, supplied directly by the system environment; no extra mapping is needed.

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

Rules:

- `sonar.host.url` can come from the `SONAR_HOST_URL` environment variable; writing it into the file is not required, and the token never goes in this file.
- Exclusions cover only artifacts you can confirm; never exclude an entire language directory, the test directory, or unknown source code for convenience.
- Add `sonar.tests` only when the test directory and the test classification rules are confirmed; tests embedded in source keep their existing analysis treatment.
- Language-specific report parameters (coverage, existing linter reports) must be confirmed against the documentation for that SonarQube version and analyzer — never guess a property name. When there is no report to import, state plainly that none is provided.

## 6. Run the scan

```powershell
sonar-scanner
if ($LASTEXITCODE -ne 0) { throw "sonar-scanner failed with exit code $LASTEXITCODE" }
```

The output must satisfy all of: it contains `EXECUTION SUCCESS`, the exit code is 0, and the project key and server URL in the log match what you expect. Keep only the success/failure summary; do not return the full scanner log.

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

## 8. Preferred MCP tools

| Need | Tool |
| --- | --- |
| Find projects | `mcp__sonarqube__search_my_sonarqube_projects` |
| Quality Gate status | `mcp__sonarqube__get_project_quality_gate_status` |
| Issues | `mcp__sonarqube__search_sonar_issues_in_projects` |
| Measures | `mcp__sonarqube__get_component_measures` |
| Branches | `mcp__sonarqube__list_branches` |
| Create a project | No MCP tool; only `POST /api/projects/create` |

Query issues and measures only when verification fails or the user asks.

## 9. Working-tree wrap-up

```powershell
git diff --check
git status --short
```

Add `.scannerwork/`, coverage output, and any other scan artifacts to the appropriate ignore rules. Do not run `git commit` or `git push` unless the user explicitly asks.
