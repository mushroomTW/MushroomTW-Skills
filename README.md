# MushroomTW-Skills

**English** | [繁體中文](README.zh.md)

Five portable Agent Skills for project documentation, dependency decisions, over-engineering audits, and SonarQube quality workflows. They follow the open Agent Skills format and can be installed into Claude Code, Codex, Cursor, OpenCode, and other skills-compatible agents; workflows that need SonarQube still require that capability on the host.

Each skill is a self-contained skill folder at the root; its documentation lives in `docs/`.

## Skills

### General

| Skill | What it does | Docs | Directory |
| --- | --- | --- | --- |
| `excellent-project-docs` | Writes, improves, audits, or re-syncs a repository's `README.md` and the companion files GitHub reads (`CONTRIBUTING`, `SECURITY`, `ARCHITECTURE`, `CHANGELOG`, …) against what the repository actually contains. Proposes companion files before creating them; claims it cannot trace to a file are reported as gaps rather than written as facts. | [EN](docs/excellent-project-docs.md) ・ [繁中](docs/excellent-project-docs.zh.md) | `excellent-project-docs/` |
| `library-first` | Before you hand-roll retry, validation, caching, auth, or date handling, forces one search of that language's own ecosystem and a stated reason for the build-or-adopt decision. | [EN](docs/library-first.md) ・ [繁中](docs/library-first.zh.md) | `library-first/` |
| `ponytail-audit-lite` | Scans a whole repository for over-engineering and returns a ranked table of what to delete, simplify, or replace with a standard-library or platform equivalent. Reports only; applies nothing. Adapted from [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) (MIT). | [EN](docs/ponytail-audit-lite.md) ・ [繁中](docs/ponytail-audit-lite.zh.md) | `ponytail-audit-lite/` |

### SonarQube workflow

| Skill | What it does | Docs | Directory |
| --- | --- | --- | --- |
| `local-sonarqube-setup` | Points a project at a local Docker SonarQube (`127.0.0.1:9000`), generates coverage with the project's own tooling, scans, and checks the Quality Gate. Reads the token from `SONAR_TOKEN` and keeps it out of files, arguments, logs, and replies. | [EN](docs/local-sonarqube-setup.md) ・ [繁中](docs/local-sonarqube-setup.zh.md) | `local-sonarqube-setup/` |
| `sonarqube-fix-all` | Works through SonarQube findings in batches, verifying each batch against the build before moving on. Skips and reports bytecode-manipulating, reflection-driven, and timing-dependent code instead of rewriting it. | [EN](docs/sonarqube-fix-all.md) ・ [繁中](docs/sonarqube-fix-all.zh.md) | `sonarqube-fix-all/` |

Both skills target a **self-hosted SonarQube running in Docker** on the same machine (default `http://127.0.0.1:9000`, Community Build). They connect to it; they do not start it — bring the container up before invoking either skill. SonarCloud is not supported.

`local-sonarqube-setup` and `sonarqube-fix-all` are meant to run in that order: the first connects a project and produces a first analysis, the second batch-fixes what it reports.

`sonarqube-fix-all` and `ponytail-audit-lite` are manual-trigger-only: they declare `disable-model-invocation: true`, so the host never fires them on their own. Invoke them by name (`/sonarqube-fix-all`, `/ponytail-audit-lite`). The other three trigger from their `description`.

## Design rationale

The references below back two design decisions, not the effectiveness of the skills themselves — no published study evaluates them.

| Design decision | Skills | Evidence |
| --- | --- | --- |
| Never state a fact the repository cannot back | `excellent-project-docs` | F. Liu et al., [Exploring and Evaluating Hallucinations in LLM-Powered Code Generation](https://arxiv.org/abs/2404.00971), preprint 2024 — taxonomy of code-generation hallucinations and the HalluCode benchmark |
| Search the ecosystem instead of recalling a package name | `library-first` | Spracklen et al., [We Have a Package for You!](https://www.usenix.org/conference/usenixsecurity25/presentation/spracklen), USENIX Security 2025 — 19.7% of packages referenced across 576,000 generated samples do not exist |

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

`local-sonarqube-setup` additionally expects a compatible scanner already on the host and a `SONAR_TOKEN` environment variable; it does not install the scanner. SonarScanner for .NET currently lacks this environment-variable path, so the skill stops instead of exposing the token in arguments or files. `sonarqube-fix-all` expects an already-configured SonarQube MCP connection and also reads `SONAR_TOKEN`.

All five ship an `agents/openai.yaml` for Codex; beyond that file, `library-first` is a single `SKILL.md` with no other supporting files. `ponytail-audit-lite` also carries its upstream `LICENSE`, which travels with the install.

## Repository layout

```txt
MushroomTW-Skills/
├── README.md / README.zh.md      ← this overview (EN / 繁中)
├── LICENSE                       (MIT)
│
├── docs/                         ← per-skill docs (EN default, .zh.md = 繁中)
│   ├── excellent-project-docs.md / .zh.md
│   ├── library-first.md / .zh.md
│   ├── ponytail-audit-lite.md / .zh.md
│   ├── local-sonarqube-setup.md / .zh.md
│   └── sonarqube-fix-all.md / .zh.md
│
├── excellent-project-docs/       SKILL.md + agents/ references/ scripts/
├── library-first/                SKILL.md + agents/
├── ponytail-audit-lite/          SKILL.md + agents/ LICENSE (upstream MIT)
├── local-sonarqube-setup/        SKILL.md + agents/ reference/
└── sonarqube-fix-all/            SKILL.md + agents/
```

No subproject contains a `README.md`; all documentation was consolidated into `docs/`.

## License

MIT — see [LICENSE](LICENSE). The file sits at the collection root and is not copied into a skill directory on install, so a skill installed on its own carries no license text with it.
