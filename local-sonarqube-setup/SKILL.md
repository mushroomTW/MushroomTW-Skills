---
name: local-sonarqube-setup
description: Initial setup of a code project on a local Docker SonarQube (default http://127.0.0.1:9000) — create the project, write the scan configuration, generate coverage, and run the first analysis to confirm it works, using the host's existing scanner. Use when the user asks to connect, onboard, or set up a repository with a local SonarQube, or when that first setup fails.
---

# Local SonarQube Setup

Goal: the repository has a SonarQube project, a working scan configuration, and one successful analysis. Fixing issues or a failing Quality Gate is out of scope — report the Gate status and stop.

Assumes PowerShell on Windows, the token in the `SONAR_TOKEN` environment variable, and a scanner already installed (this skill never installs one).

## Rules

1. **Token stays in process memory.** Never put it in arguments, URLs, files, or output; say only whether it is set. Run every step in one process, and remove `SONAR_TOKEN` (and any `SONARQUBE_SCANNER_PARAMS` built from it) from the process only at the end. If it leaks, tell the user to revoke it.
2. **Server settings stay at defaults.** Quality Profile, Quality Gate, main branch, New Code definition, visibility, tags and permissions are changed only when the user asks. Never delete a project.
3. **Touch only what setup needs.** Do not change production code, build semantics, CI or compose files; do not commit or push unless asked; preserve uncommitted changes.
4. **Derive everything from the repo** (languages, build, tests, coverage) instead of assuming defaults. Output short summaries, never full logs.

## Steps

1. **Discover.** Read `AGENTS.md`, README, build files and any existing Sonar config; run `git status --short`. List the languages and run the support check in `reference/languages.md §1`. Stop if the main language is unsupported. If `git rev-parse --is-shallow-repository` is `true`, run `git fetch --unshallow`.
2. **Check server and scanner.** `GET /api/system/status` must be `UP`. Pick the scanner from `reference/languages.md §2` (Maven/Gradle plugin, .NET scanner, or `sonar-scanner`; Docker image as fallback) and confirm it runs. Ask the user when the repo mixes toolchains.
3. **Create the project.** Key: `sonar.projectKey` → `.sonarlint/connectedMode.json` → git remote → folder name, using only `[A-Za-z0-9-_.:]` and not all digits. Name: the project's own name (existing `sonar.projectName` → name in the build manifest → repo name), unchanged. Look it up first and reuse it if it exists; otherwise **confirm key and name with the user**, then create it (`reference/commands.md §3`).
4. **Write the configuration.** Merge the minimum into `sonar-project.properties` (create it only if absent; .NET passes settings to `begin` instead). Add the language keys from `reference/languages.md §3`. Exclude only confirmed build output and caches. **Show the diff before writing.**
5. **Generate coverage.** Run the repo's own tests with its coverage tool, then point the matching `sonar.*` key at the report (`reference/languages.md §3`). The report must contain real content, not just exist. No coverage tool → say so and continue without it.
6. **Run the first analysis.** Set `SONAR_HOST_URL`, run the chosen scanner (`reference/commands.md §4`). It must exit 0 and report success for the expected key and URL.
7. **Confirm.** Poll the CE task to `SUCCESS`, then check that `ncloc` is above zero (zero means nothing was analyzed). Read the Quality Gate status and report it as-is. Add scanner work directories and coverage output to the ignore rules, then report key, name, dashboard URL, CE status, `ncloc`, coverage and Gate (`reference/commands.md §5`).

On any failure, see `reference/troubleshooting.md`.

## References

- `reference/languages.md` — supported languages, scanner per ecosystem, per-language keys and coverage.
- `reference/commands.md` — PowerShell snippets for each step.
- `reference/troubleshooting.md` — what to do when a step fails.
- Official docs: https://docs.sonarsource.com/sonarqube-community-build/analyzing-source-code
