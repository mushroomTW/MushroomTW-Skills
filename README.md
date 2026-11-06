# MushroomTW-Skills

**English** | [繁體中文](README.zh.md)

Five portable Agent Skills for over-engineering audits, SonarQube quality workflows, and RimWorld mod development. They follow the open Agent Skills format and can be installed into Claude Code, Codex, Cursor, OpenCode, and other skills-compatible agents; workflows that need SonarQube still require that capability on the host.

Each skill is a self-contained skill folder at the root; its documentation lives in `docs/`.

## Skills

### General

| Skill | What it does | Docs | Directory |
| --- | --- | --- | --- |
| `ponytail-audit-lite` | Scans a whole repository for over-engineering and returns a ranked table of what to delete, simplify, or replace with a standard-library or platform equivalent. Reports only; applies nothing. Adapted from [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) (MIT). | [EN](docs/ponytail-audit-lite.md) ・ [繁中](docs/ponytail-audit-lite.zh.md) | `ponytail-audit-lite/` |

### SonarQube workflow

| Skill | What it does | Docs | Directory |
| --- | --- | --- | --- |
| `local-sonarqube-setup` | Points a project at a local Docker SonarQube (`127.0.0.1:9000`), generates coverage with the project's own tooling, scans, and checks the Quality Gate. Reads the token from `SONAR_TOKEN` and keeps it out of files, arguments, logs, and replies. | [EN](docs/local-sonarqube-setup.md) ・ [繁中](docs/local-sonarqube-setup.zh.md) | `local-sonarqube-setup/` |

`local-sonarqube-setup` targets a **self-hosted SonarQube running in Docker** on the same machine (default `http://127.0.0.1:9000`, Community Build). It connects to the service; it does not start it — bring the container up before invoking the skill. SonarCloud is not supported.

`ponytail-audit-lite` is manual-trigger-only: it declares `disable-model-invocation: true` for Claude Code and `policy.allow_implicit_invocation: false` in `agents/openai.yaml` for Codex; other hosts apply their own rules. Invoke it by name (`/ponytail-audit-lite`). The other four trigger from their `description`.

### RimWorld modding

| Skill | What it does | Docs | Directory |
| --- | --- | --- | --- |
| `rimtest-redux-integrate` | When you write or debug tests for a RimWorld mod, asks whether to add in-game integration tests with RimTest Redux, then sets up a companion test mod, compares results against a vanilla baseline recovered by Harmony reverse patch, and waits for deferred startup work before running. | [EN](docs/rimtest-redux-integrate.md) ・ [繁中](docs/rimtest-redux-integrate.zh.md) | `rimtest-redux-integrate/` |
| `rimworld-devtools` | Uses SmashPhil DevTools for in-game tests, result interpretation, test plans, and benchmarks when DevTools is selected or already in use. | [EN](docs/rimworld-devtools.md) ・ [繁中](docs/rimworld-devtools.zh.md) | `rimworld-devtools/` |
| `rimworld-smashtools` | Selects and uses SmashTools features for RimWorld mods, and handles integration, packaging, initialization, and verification. | [EN](docs/rimworld-smashtools.md) ・ [繁中](docs/rimworld-smashtools.zh.md) | `rimworld-smashtools/` |

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

`local-sonarqube-setup` additionally expects a compatible scanner already on the host and a `SONAR_TOKEN` environment variable; it does not install the scanner. SonarScanner for .NET currently lacks this environment-variable path, so the skill stops instead of exposing the token in arguments or files. Tests written with `rimtest-redux-integrate` run inside RimWorld and need RimWorld 1.6 with the `brrainz.harmony`, `ilyvion.Laboratory`, and `ilyvion.rimtestredux` mods installed.

`rimworld-devtools` requires a compatible SmashPhil/DevTools build, game assemblies, SDK, and a running game for execution.

All five ship an `agents/openai.yaml` for Codex. `ponytail-audit-lite`, `rimtest-redux-integrate`, and `rimworld-smashtools` also carry their upstream `LICENSE`, which travels with the install.

## Repository layout

```txt
MushroomTW-Skills/
├── README.md / README.zh.md      ← this overview (EN / 繁中)
├── LICENSE                       (MIT)
│
├── docs/                         ← per-skill docs (EN default, .zh.md = 繁中)
│   ├── ponytail-audit-lite.md / .zh.md
│   ├── local-sonarqube-setup.md / .zh.md
│   ├── rimtest-redux-integrate.md / .zh.md
│   ├── rimworld-devtools.md / .zh.md
│   └── rimworld-smashtools.md / .zh.md
│
├── ponytail-audit-lite/          SKILL.md + agents/ LICENSE (upstream MIT)
├── local-sonarqube-setup/        SKILL.md + agents/ reference/
├── rimtest-redux-integrate/      SKILL.md + agents/ references/ LICENSE (upstream MIT)
├── rimworld-devtools/            SKILL.md + agents/ references/
└── rimworld-smashtools/          SKILL.md + agents/ references/ LICENSE (upstream MIT)
```

No subproject contains a `README.md`; all documentation was consolidated into `docs/`.

## License

MIT — see [LICENSE](LICENSE). The file sits at the collection root and is not copied into a skill directory on install, so a skill installed on its own carries no license text with it.
