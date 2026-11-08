# RimWorld DevTools — In-Game Testing & Profiling

**English** | [繁體中文](rimworld-devtools.zh.md)

> This document lives in `docs/`. The skill itself is at [`rimworld-devtools/SKILL.md`](../rimworld-devtools/SKILL.md).

Integrates the SmashPhil DevTools test suite into RimWorld mod projects, enabling in-game automated test execution, multi-process test plans, smoke testing, intelligent log analysis, and precision micro-benchmarking directly within the running game engine.

Headless unit tests cannot capture Unity engine states, graphic rendering contexts, or complex multi-mod load dependencies. SmashPhil DevTools provides an in-game execution environment that tests mod behavior in real gameplay conditions without crashing the host process when assertions fail.

## When It Applies

Applies when setting up, authoring, running, or troubleshooting in-game tests and performance benchmarks for RimWorld mods utilizing SmashPhil DevTools.

The skill triggers automatically when a project references or configures DevTools, or via direct agent invocation:

```text
Use $rimworld-devtools to add map-based tests to this mod, run the relevant fixture, and report results.
```

## Core Capabilities

1. **In-Game Test Fixtures & Assertions**:
   - Implements structured test fixtures using non-throwing assertions (`Test.Assert`), allowing entire test suites to complete and report all failures rather than aborting on the first error.
   - Supports test parameterization, Unity coroutines (`IEnumerator`), and rigorous post-test state cleanup to prevent leaking modified game state across runs.

2. **Automated Smoke Testing**:
   - Executes `--smoke-test` via `SmokeTestManager` to monitor startup, scene transitions, and initialization logs without requiring explicit assertions.
   - Configured through `Configs/SmokeTestConfig.xml` to immediately flag initialization warnings and fatal errors.

3. **Multi-Process Test Plans**:
   - Coordinates child-process matrix testing across distinct mod configurations using `--test-plan <name>`.
   - Protects player environments by automatically backing up `ModsConfig.xml` prior to execution and restoring it after child processes terminate.

4. **Intelligent Log Analysis & Failure Classification**:
   - Parses `Test.log` and runtime console output, filters out ambient engine noise and harmless vanilla warnings, and classifies issues into:
     - **Mod Bugs**: Logic defects originating from the mod under test.
     - **Vanilla Quirks**: Unmodified base game behaviors or known engine limits.
     - **Environment Issues**: Missing test fixtures, corrupted configurations, or missing assemblies.

5. **Performance Micro-Benchmarking**:
   - Uses `DevTools.Benchmarking` (`[BenchmarkClass]`, `[Benchmark]`) to measure execution times, memory usage, and frame latency.
   - Configures statistical tables (mean, median, standard deviation, sample counts) and implements defenses against JIT compiler dead-code elimination and constant folding.

## References

- [`references/testing.md`](../rimworld-devtools/references/testing.md) — Assembly loading mechanisms, test fixtures, non-throwing assertions, parameterization, coroutines, and clean state restoration.
- [`references/running.md`](../rimworld-devtools/references/running.md) — UI and CLI invocation, runtime configuration, log freshness verification, completion indicators, and troubleshooting.
- [`references/advanced.md`](../rimworld-devtools/references/advanced.md) — Smoke test hosts, test-plan state recovery, and benchmark constraints.

## Prerequisites

- **RimWorld Engine**: RimWorld 1.6+ running instance for test execution.
- **Tooling**: .NET SDK and RimWorld game reference assemblies.
- **DevTools Assemblies**: Compatible SmashPhil DevTools assemblies (`DevTools.dll`). Local sources are prioritized; external repositories (`SmashPhil/DevTools`) are consulted only upon initial setup if missing locally.

## Install

From the repository root, use the `skills` CLI to discover supported agent hosts and install this skill:

```bash
npx skills add . --skill rimworld-devtools
```

Add `--global` for personal user scope; omitting it installs at project scope. For manual installation, copy `rimworld-devtools/` directly into your agent host's configured skills directory.

> [!NOTE]
> The initial `npx` invocation may download the CLI. Reload or restart your agent host if it only discovers skills during session startup.
