# Troubleshooting

Read only when a step fails. Never print the token while diagnosing, and never get past a failure by faking success, excluding source, or moving the token into arguments.

## `SONAR_TOKEN` not visible in this process

The variable was set after the shell started. Check which scope holds it, printing booleans only:

```powershell
"user=$(-not [string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable('SONAR_TOKEN','User')))"
"machine=$(-not [string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable('SONAR_TOKEN','Machine')))"
$env:SONAR_TOKEN = [Environment]::GetEnvironmentVariable('SONAR_TOKEN','User')
if ([string]::IsNullOrWhiteSpace($env:SONAR_TOKEN)) { $env:SONAR_TOKEN = [Environment]::GetEnvironmentVariable('SONAR_TOKEN','Machine') }
```

Both `False` → ask the user to generate a token in SonarQube and set the system environment variable.

## HTTP 401 / `Not authorized`

Check in order, reporting only each conclusion:

1. The token is still in this process and cleanup has not run yet.
2. `(Invoke-RestMethod -Headers $headers "$env:SONAR_HOST_URL/api/authentication/validate").valid` is `True`; `False` means expired or revoked.
3. Token type: a Project Analysis Token works only for its own project. Use a Global Analysis Token or a user token for setup.
4. Host: the URL in the scanner log is the expected server (`localhost` vs `host.docker.internal` inside Docker).
5. .NET: `SONARQUBE_SCANNER_PARAMS` was built in this same process (`commands.md §4.3`).
6. Stray whitespace: `$env:SONAR_TOKEN -ne $env:SONAR_TOKEN.Trim()` is `False`.

Still failing → ask the user to regenerate the token.

## Other failures

| Symptom | Cause | Handling |
| --- | --- | --- |
| `status` is not `UP` / connection refused | Server down | `docker ps`, restart the container; still down → stop and report |
| `Unable to establish loopback connection` | Sandbox blocks local network | Re-run in a normal user terminal; do not change the host URL or config |
| HTTP 403 | Missing `Create Projects` or `Execute Analysis` | Name the missing permission; ask the user to grant it or create the project in the UI |
| Project key rejected | Invalid characters or all digits | Replace invalid characters with `-`, confirm with the user |
| `please provide compiled classes with sonar.java.binaries` | Java scanned by the CLI without a build | Build first and set `sonar.java.binaries` (`languages.md` Java) |
| Other analyzer or property error | Wrong key or format for that language | Check the key in `languages.md` and the docs, fix, rescan |
| Coverage report missing, empty, or `coverage=0.0` | Tests not run, wrong path, or no symbols (.NET) | Re-run the repo's own coverage command, check content (`languages.md` Coverage checks); no tool → scan without it |
| `ncloc` is 0 after success | Only unsupported languages, or sources excluded | Recheck the support check and `sonar.sources` / exclusions |
| .NET build fails between `begin` and `end` | Missing local paths or SDK | Set the repo's documented environment variables; do not edit project files |
| CE stays `PENDING` past 5 minutes | Server busy or low memory | Poll longer, check `api/ce/activity`; report the task id and status |
| CE `FAILED` | Server-side processing error | Summarize the task's `errorMessage`, fix the cause, rescan |
| `PKIX path building failed` | HTTPS with a self-signed certificate | Import the certificate into the scanner's truststore (`scanners/scanner-environment/manage-tls-certificates.md`); never disable TLS checks |
| `Malformed input` on non-ASCII paths | Locale not UTF-8 | `$env:LC_ALL = 'en_US.UTF-8'; $env:LANG = 'en_US.UTF-8'`, rescan |
| Scanner fails when the Windows user name has `!` or similar | User home path breaks the scanner | `sonar-scanner '-Dsonar.userHome=C:\sonar-cache'` |
| `OutOfMemoryError` | Scanner heap too small | `$env:SONAR_SCANNER_JAVA_OPTS = '-Xmx1024m'` (CLI before 6.0: `SONAR_SCANNER_OPTS`) |
| Gate shows `NONE` | No completed analysis yet | Normal before the first scan; confirm CE `SUCCESS`, then query again |
