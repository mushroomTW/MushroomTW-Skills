# MushroomTW-Skills

**English** | [繁體中文](README.zh.md)

MushroomTW-Skills is a curated collection of portable Agent Skills designed for modern AI coding assistants (such as Claude Code, Codex, Cursor, OpenCode, and any agent supporting the open Agent Skills specification). It covers **codebase over-engineering audits**, **local SonarQube quality workflow automation**, and **RimWorld mod development & in-game testing**.

Each skill is an independent directory containing its prompt specification, trigger rules, and technical reference materials. In-depth documentation is consolidated in `docs/`.

---

## Skills Overview

| Skill | Category | Trigger | Summary | Docs | Directory |
| --- | --- | --- | --- | --- | --- |
| `ponytail-audit-lite` | General Audit | Manual (`/ponytail-audit-lite`) | Repo-wide over-engineering audit; returns a ranked table of code to delete, simplify, or replace with stdlib/platform native. Strictly report-only. | [EN](docs/ponytail-audit-lite.md) ・ [繁中](docs/ponytail-audit-lite.zh.md) | `ponytail-audit-lite/` |
| `local-sonarqube-setup` | Quality Workflow | Auto (Natural Language) | Connects a project to a local Docker SonarQube instance, generates coverage, runs scans, and verifies the Quality Gate. Strict token protection. | [EN](docs/local-sonarqube-setup.md) ・ [繁中](docs/local-sonarqube-setup.zh.md) | `local-sonarqube-setup/` |
| `rimtest-redux-integrate` | RimWorld Modding | Auto (Natural Language) | Sets up RimTest Redux in-game integration tests with a companion test mod, Harmony reverse-patch vanilla baselines, and startup timing protection. | [EN](docs/rimtest-redux-integrate.md) ・ [繁中](docs/rimtest-redux-integrate.zh.md) | `rimtest-redux-integrate/` |
| `rimworld-devtools` | RimWorld Modding | Auto (Natural Language) | Integrates SmashPhil DevTools for in-game testing, Test Plan management, result interpretation, and performance benchmarks. | [EN](docs/rimworld-devtools.md) ・ [繁中](docs/rimworld-devtools.zh.md) | `rimworld-devtools/` |
| `rimworld-smashtools` | RimWorld Modding | Auto (Natural Language) | Architecture & feature integration guide for the SmashTools framework (pathfinding, object pooling, UI, rendering, lifecycle, packaging). | [EN](docs/rimworld-smashtools.md) ・ [繁中](docs/rimworld-smashtools.zh.md) | `rimworld-smashtools/` |

---

## Featured Skills

### General Codebase Audit

#### `ponytail-audit-lite` — Over-Engineering & YAGNI Audit

- **Purpose**: Quickly diagnose unnecessary complexity across an entire repository, identifying speculative features, redundant abstractions, and YAGNI violations.
- **Key Features**:
  - **Report-Only**: Performs a one-shot scan across the whole project and outputs actionable recommendations without modifying any files.
  - **Ranked Findings Table**: Generates a Markdown table sorted by estimated lines removed, categorized by `delete` (dead code / unused flexibility), `yagni` (single-implementation abstractions, forwarding wrappers), `stdlib` (reinventing standard library functionality), `native` (platform-provided capabilities), and `shrink` (equivalent shorter implementations).
  - **Noise Filtering**: Automatically skips vendored code (`node_modules`, `vendor`), build outputs, generated files, and `.gitignore` matches. Focuses strictly on simplicity rather than standard bugs, security vulnerabilities, or performance tuning.
- **Invocation**: **Manual trigger only**. Configured with `disable-model-invocation: true` (Claude Code) and `policy.allow_implicit_invocation: false` (Codex) to prevent accidental execution during normal conversations. Invoke explicitly via `/ponytail-audit-lite`.
- **Origin**: Adapted from [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) (MIT License).

---

### Static Analysis & Quality Gate

#### `local-sonarqube-setup` — Local Docker SonarQube Workflow & Safe Analysis

- **Purpose**: Connect a project to a local Docker SonarQube instance, automatically handling coverage generation, scanner execution, and Quality Gate verification.
- **Key Features**:
  - **End-to-End Workflow**: Discovers build tools (Maven, Gradle, .NET, npm, etc.), produces native coverage reports, runs the appropriate scanner, tracks the analysis background task, and checks the Quality Gate status.
  - **Strict Token Safety**: Reads credentials exclusively from the `SONAR_TOKEN` environment variable. Never exposes tokens in files, command-line arguments, logs, or model responses. Aborts safely if a scanner (such as current SonarScanner for .NET) cannot accept tokens securely without exposure.
  - **Uncompromised Quality Gate**: Never fabricates a passing status by relaxing rules or marking issues as `Accepted` / `False positive`; always reports actual Gate metrics and failures.
- **Prerequisites & Limitations**:
  - Targets a self-hosted SonarQube instance running in Docker on the local machine (default `http://127.0.0.1:9000`, Community Build). The container must be running prior to invoking the skill.
  - SonarCloud is not supported.
  - Requires a compatible scanner and Java environment pre-installed on the host.

---

### RimWorld Mod Development

#### `rimtest-redux-integrate` — In-Game Integration Testing & Harmony Baseline

- **Purpose**: Build and run integration tests inside the actual RimWorld game engine, catching Harmony patch conflicts, execution timing issues, and asset loading states that headless unit tests miss.
- **Key Features**:
  - **Opt-in Confirmation**: Explicitly asks whether to introduce RimTest Redux before proceeding, keeping test workflows developer-driven (skips confirmation if a companion test mod already exists).
  - **Isolated Companion Test Mod**: Houses all test fixtures and assertions in a separate companion mod that is never packaged into release builds.
  - **Harmony Baseline Comparison**: Uses Harmony reverse patching to extract unmodified vanilla methods, comparing mod behavior directly against vanilla baselines.
  - **Startup Timing Protection**: Delays test execution until RimWorld's deferred initialization (`LongEvent`, background tasks) completes to eliminate race conditions.
  - **Mono & Harmony Pitfall Defenses**: Built-in safeguards against Mono and Harmony runtime pitfalls (e.g., Mono compiler issues with `catch ... when`, and `PatchCategory` crashes).
- **Prerequisites**: RimWorld 1.6 with `brrainz.harmony`, `ilyvion.Laboratory`, and `ilyvion.rimtestredux` installed; test assembly targets `net481`.

#### `rimworld-devtools` — SmashPhil DevTools In-Game Testing & Profiling

- **Purpose**: Leverage the SmashPhil DevTools suite for in-game test execution, test plan management, result analysis, and performance benchmarking.
- **Key Features**:
  - **Comprehensive Test Support**: Covers smoke tests, test plans, fixture assemblies, and non-throwing in-game assertions.
  - **Intelligent Log Interpretation**: Analyzes game test logs, filters irrelevant background messages, and categorizes failures (mod bug, vanilla behavior, or test environment issue).
  - **Performance Benchmarking**: Runs in-game performance benchmarks to detect execution bottlenecks and track frame times.
- **Prerequisites**: Requires compatible SmashPhil DevTools assemblies, RimWorld game assemblies, .NET SDK, and an active running game instance for execution.

#### `rimworld-smashtools` — SmashTools Architecture & Feature Integration

- **Purpose**: Comprehensive integration and feature reference guide for the high-performance SmashTools library in RimWorld mod development.
- **Key Features**:
  - **Broad Architecture Coverage**: Guides adoption of core utilities, native collections, high-efficiency object pooling, background job/thread dispatching, multi-cell pathfinding, event systems, UI/custom rendering, XML/data persistence, animation curves, and caching/profiling.
  - **Lifecycle & Initialization**: Manages proper execution hooks across mod lifecycle stages (static constructors, mod initialization, and game loading) while avoiding cross-assembly loading pitfalls.
  - **Packaging & Compatibility Verification**: Assists with multi-version build setups, dependency isolation, release packaging, and runtime coexistence validation.

---

## Repository Layout

```txt
MushroomTW-Skills/
├── README.md / README.zh.md      ← This overview (EN / 繁中)
├── LICENSE                       (MIT)
│
├── docs/                         ← Per-skill documentation (.md = EN, .zh.md = 繁中)
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

No subproject contains a standalone `README.md`; all in-depth documentation is consolidated in `docs/`.

---

## License

This collection is licensed under the [MIT License](LICENSE).

Individual skills may include upstream components and licenses:

- `ponytail-audit-lite`: Adapted from [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) (MIT License, included in directory)
- `rimtest-redux-integrate`: Contains references and API adaptations from RimTest Redux (MIT License, included in directory)
- `rimworld-smashtools`: Contains references and API specifications for SmashTools (MIT License, included in directory)
