# MushroomTW-Skills

**English** | [繁體中文](README.zh.md)

Five portable Agent Skills for README authoring, dependency decisions, repository auditing, and SonarQube quality workflows. They follow the open Agent Skills format and can be installed into Claude Code, Codex, Cursor, OpenCode, and other skills-compatible agents; workflows that need SonarQube or code-graph integrations still require those capabilities on the host.

Each skill is a self-contained skill folder at the root; its documentation lives in `docs/`.

## Skills

| Skill | What it does | Docs | Directory |
| --- | --- | --- | --- |
| `excellent-readme` | Writes, improves, audits, or re-syncs a `README.md` against what the repository actually contains. Claims it cannot trace to a file are reported as gaps rather than written as facts. | [EN](docs/excellent-readme.md) ・ [繁中](docs/excellent-readme.zh.md) | `excellent-readme/` |
| `library-first` | Before you hand-roll retry, validation, caching, auth, or date handling, forces one search of that language's own ecosystem and a stated reason for the build-or-adopt decision. | [EN](docs/library-first.md) ・ [繁中](docs/library-first.zh.md) | `library-first/` |
| `local-sonarqube-setup` | Points a project at a local Docker SonarQube (`127.0.0.1:9000`), generates coverage with the project's own tooling, scans, and checks the Quality Gate. Reads the token from `SONARQUBE_TOKEN` and keeps it out of files, logs, and replies. | [EN](docs/local-sonarqube-setup.md) ・ [繁中](docs/local-sonarqube-setup.zh.md) | `local-sonarqube-setup/` |
| `repository-bug-audit` | Reads the implementation, its callers, its config, and its tests before calling anything a bug. Delivers a Markdown report paired with a machine-checked evidence JSON, plus a 0–100 risk score in Comprehensive mode. | [EN](docs/repository-bug-audit.md) ・ [繁中](docs/repository-bug-audit.zh.md) | `repository-bug-audit/` |
| `sonarqube-fix-all` | Works through SonarQube findings in batches, verifying each batch against the build before moving on. Skips and reports bytecode-manipulating, reflection-driven, and timing-dependent code instead of rewriting it. | [EN](docs/sonarqube-fix-all.md) ・ [繁中](docs/sonarqube-fix-all.zh.md) | `sonarqube-fix-all/` |

`local-sonarqube-setup` and `sonarqube-fix-all` are meant to run in that order: the first connects a project and produces a first analysis, the second batch-fixes what it reports.

## Install

Every directory here is a plain skill folder. From the repository root, the [`skills` CLI](https://github.com/vercel-labs/skills) can discover supported agents and install all five. The first invocation of `npx` may use the network to download the CLI:

```bash
npx skills add . --list
npx skills add . --all --global
```

For a manual installation, copy one skill directory to a location supported by the host. These are common paths, not an exhaustive runtime registry:

| Route | Personal scope | Project scope |
| --- | --- | --- |
| Universal Agent Skills fallback | `~/.agents/skills/<skill-name>/` | `<repo>/.agents/skills/<skill-name>/` |
| Claude Code | `~/.claude/skills/` | `<repo>/.claude/skills/` |
| Codex | `~/.codex/skills/` | `<repo>/.agents/skills/` |
| Other compatible agents | Use CLI auto-discovery or the host's documented skills directory | Use CLI auto-discovery or the host's documented skills directory |

```bash
cp -r <skill-name> <host-skills-directory>/<skill-name>
```

> [!NOTE]
> Reload or restart the agent when its host requires a new session to discover installed skills. Use `npx skills list` to inspect the paths recognized by the CLI.

To use one skill as reference material without installing it:

```bash
npx skills use . --skill <skill-name>
```

`local-sonarqube-setup` additionally expects a `sonar-scanner` already on the host and a `SONARQUBE_TOKEN` environment variable; it does not install the scanner. `sonarqube-fix-all` expects an already-configured SonarQube MCP connection and reads `SONAR_TOKEN`.

All five ship an `agents/openai.yaml` for Codex; beyond that file, `library-first` is a single `SKILL.md` with no other supporting files.

## Repository layout

```
MushroomTW-Skills/
├── README.md / README.zh.md      ← this overview (EN / 繁中)
├── LICENSE                       (MIT)
│
├── docs/                         ← per-skill docs (EN default, .zh.md = 繁中)
│   ├── excellent-readme.md / .zh.md
│   ├── library-first.md / .zh.md
│   ├── local-sonarqube-setup.md / .zh.md
│   ├── repository-bug-audit.md / .zh.md
│   └── sonarqube-fix-all.md / .zh.md
│
├── excellent-readme/             SKILL.md + agents/ references/ scripts/
├── library-first/                SKILL.md + agents/
├── local-sonarqube-setup/        SKILL.md + agents/ reference/
├── repository-bug-audit/         SKILL.md + agents/ references/ scripts/
└── sonarqube-fix-all/            SKILL.md + agents/
```

Each skill directory holds only the skill itself. Development assets kept on disk — the `test-prompts.json` next to three of the skills, and `repository-bug-audit/tests/` — are excluded from version control by the single `.gitignore` at the root; a `cp -r` install still copies them along with the skill.

## Version control

The whole collection lives in a single git repository at the root; no skill directory carries a `.git` of its own any more. Each skill used to be a separate local repository, and those histories were merged in with `git subtree`, so every original commit is still reachable from `git log`. Note that the pre-merge commits recorded their paths at their own repository root, so `git log -- <skill>/` shows only the merge point — read the full `git log` to follow one skill's evolution.

The repository has no remote — this is a local-only copy.

No subproject contains a `README.md`; all documentation was consolidated into `docs/`.

## License

MIT — see [LICENSE](LICENSE). The file sits at the collection root and is not copied into a skill directory on install, so a skill installed on its own carries no license text with it.
