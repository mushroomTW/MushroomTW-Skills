# Troubleshooting

Read this only when the matching failure occurs. Format: symptom → diagnosis → handling.

## `Unable to establish loopback connection`

Diagnosis: a local network or process restriction in the execution environment, not a project configuration problem.

Handling: re-run the same commands in an environment that allows local loopback connections (an ordinary user terminal, not a restricted sandbox). **Never** work around it by editing `sonar-project.properties`, switching to another host URL, or disabling functionality to hide it.

## `SONAR_TOKEN` is not visible in the current process

Diagnosis: the variable is set at Machine or User scope, but the current shell started before it was set and therefore did not inherit it.

Handling: first confirm which scope holds the variable (print booleans only, never the value):

```powershell
"machine=$(-not [string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable('SONAR_TOKEN','Machine')))"
"user=$(-not [string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable('SONAR_TOKEN','User')))"
```

If either is `True`, reopen the shell so the process inherits it, or load it inside the current process:

```powershell
$env:SONAR_TOKEN = [Environment]::GetEnvironmentVariable('SONAR_TOKEN','Machine')
```

Only when both are `False` is it genuinely unset — ask the user to generate a token and set the system environment variable.

## HTTP 401

Diagnosis: the scanner or API never received the token, or the token is invalid, of the wrong type, or aimed at a different server.

First fix: confirm `SONAR_TOKEN` is readable inside the same process (see section 2 of commands.md) and that the cleanup step has not run yet.

Still 401 — work through these in order, reporting only the conclusion of each and never printing the token:

1. **Is the token still valid**: `(Invoke-RestMethod -Headers $headers -Uri "$env:SONAR_HOST_URL/api/authentication/validate").valid`. `False` means it has expired or been revoked.
2. **Token type**: a Project Analysis Token can only scan the project it is bound to; using it for another project or a general API call returns 401. Cross-project work needs a Global Analysis Token or a user token.
3. **Scanner version**: scanners older than SonarQube 10 read `sonar.login` and do not recognize `sonar.token` / `SONAR_TOKEN`; a mismatched version is equivalent to sending no credentials. Compare against the scanner version recorded in step 2.
4. **Host address**: addresses differ inside and outside a container (`localhost` versus the service name or `host.docker.internal`), and hitting a different SonarQube also returns 401. Cross-check `$env:SONAR_HOST_URL` against the server URL in the scanner log.
5. **Whitespace or newlines in the value itself**: pasting a newline in when setting the environment variable is common. Print only the boolean result of `$env:SONAR_TOKEN -ne $env:SONAR_TOKEN.Trim()`.

Only once all of these are ruled out, ask the user to regenerate the token in the SonarQube UI and update the system environment variable. Never retry by moving the token into a command-line argument.

## HTTP 403

Diagnosis: the token is valid but lacks permissions — most often `Create Projects`, or `Execute Analysis` on that project.

Handling: report the name of the permission that is actually missing, or ask the user to create the project or grant access in the SonarQube UI before re-running. Never fake success, and never substitute some other existing project key.

## Project key format rejected

Diagnosis: SonarQube restricts project key characters — alphanumerics, `-`, `_`, `.`, `:` are allowed, and the key cannot be all digits.

Handling: derive it from the repository name (whitespace and other symbols become `-`) and confirm the converted key matches the user's intent before creating it. Check any non-obvious naming with the user first.

## Coverage report path missing or empty

Diagnosis: coverage was never produced, went to a different path, or the tests did not run at all.

Handling: find the project's native test/coverage command and its actual output path, regenerate the report, then scan again. **Never** create an empty placeholder report or point at a path that does not exist; when the project has no coverage tooling, state plainly that no coverage is provided and run the analysis without it.

## Analyzer or report format error

Diagnosis: the property name does not match that language's analyzer, the report format version does not match, or the paths inside the report do not line up with the scan root.

Handling: check the documentation for that SonarQube version and analyzer to confirm the correct property and the supported formats, then fix the cause. Keep a non-sensitive summary of the original error (rule key, file path, format name) rather than pasting the full log. Never fake completion with `Accepted`, `False positive`, or by disabling rules.

## Encoding or binary-file warnings

Diagnosis: source file encoding does not match `sonar.sourceEncoding`, or binary files were pulled into the scan scope.

Handling: do not treat this as a blocker while the analysis still succeeds, but explain it in the delivery summary. Only when these warnings make the analysis **fail** should you adjust the scan scope (excluding binary assets) or fix the file encoding.

## Quality Gate shows `NONE`

Diagnosis: the project exists but has no completed analysis yet — a normal state, not an error.

Handling: confirm the CE task reached `SUCCESS`, then query again. If the CE task succeeded and it is still `NONE`, query measures to confirm whether the data was actually uploaded.

## CE task stuck in `PENDING` or timing out

Diagnosis: the SonarQube Compute Engine is busy, short on memory, or the background task is queued.

Handling: extend the polling limit and re-check; if it stays `PENDING`, inspect the SonarQube container's resources and `api/ce/activity`. When the task is `FAILED`, take a non-sensitive summary of its `errorMessage` and address the cause rather than re-running to paper over it.
