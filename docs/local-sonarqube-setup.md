# Local SonarQube Setup

**English** | [繁體中文](local-sonarqube-setup.zh.md)

> This document lives in `docs/`. The skill itself is at [`local-sonarqube-setup/SKILL.md`](../local-sonarqube-setup/SKILL.md).

Connect any code project to a **local Docker SonarQube** instance (default `http://127.0.0.1:9000`): create the project, produce reports, run the analysis, and verify the Quality Gate.

This skill only gets a project connected and analyzed. To batch-fix the issues SonarQube reports, use [sonarqube-fix-all](sonarqube-fix-all.md) instead.

## When It Applies

When the user asks to set up, configure, run, or troubleshoot a local SonarQube analysis.

## Assumptions

- The host is the current Windows machine; commands run in PowerShell
- SonarQube defaults to `http://127.0.0.1:9000`, overridden only when explicitly specified
- A directly runnable `sonar-scanner` is already installed — **this skill does not install, download, or replace the scanner**
- Credentials come from the `SONARQUBE_TOKEN` system environment variable
- Language, build system, and coverage generation are always discovered from the repository's actual contents; no default language assumptions are applied

## Hard Rules (Excerpt)

- The token exists only in process memory. It must never reach a command-line argument, URL, log, `sonar-project.properties`, or any reply; externally it is described only as "set" or "not set"
- Do not add SonarQube or database services, modify CI or compose files, commit, or push (unless explicitly asked)
- Do not change runtime behaviour, public APIs, production code, or build semantics just to make a scan work
- Never fake completion via `Accepted`, `False positive`, or by disabling rules
- Preserve the user's existing uncommitted changes

The full set is in the Hard rules section of SKILL.md.

## Workflow

| # | Step | Key points |
| --- | --- | --- |
| 1 | Discover | Read `AGENTS.md`, README, build docs, and existing sonar config; run `git status --short`; derive language and test layout from the manifest |
| 2 | Confirm service and scanner | `GET /api/system/status` must be `UP`; record the scanner version |
| 3 | Find or create the project | Query via MCP first; only `POST /api/projects/create` if absent, then record the dashboard URL |
| 4 | Scan configuration | Merge minimally into existing config rather than overwriting; exclude build artifacts and caches, never an entire language directory or the test directory |
| 5 | Produce reports | Run the project's own checks and tests first, then generate coverage with its native tooling; confirm report paths exist and are non-empty |
| 6 | Run the scan | Set `SONAR_HOST_URL` / `SONAR_TOKEN` within a single process; require `EXECUTION SUCCESS` and exit code 0 |
| 7 | Verify and wrap up | Take the CE task from `.scannerwork/report-task.txt` and poll to completion, check the Quality Gate, add artifacts to ignore rules |

## References

- [`reference/commands.md`](../local-sonarqube-setup/reference/commands.md) — PowerShell commands, a `sonar-project.properties` template, and the MCP tool mapping. Required reading before step 2.
- [`reference/troubleshooting.md`](../local-sonarqube-setup/reference/troubleshooting.md) — read only when a step fails.

## Install

This directory is the skill itself. Copy it into the host's skills directory:

| Host | Personal scope | Project scope |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/` | `<repo>/.claude/skills/` |
| Codex | `~/.codex/skills/` | — |

```bash
cp -r local-sonarqube-setup ~/.claude/skills/local-sonarqube-setup
```

> [!NOTE]
> Both hosts read their skills directories when a session starts, so start a new session after copying.
