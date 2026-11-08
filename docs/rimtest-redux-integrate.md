# RimTest Redux Integrate

**English** | [繁體中文](rimtest-redux-integrate.zh.md)

> This document lives in `docs/`. The skill itself is at [`rimtest-redux-integrate/SKILL.md`](../rimtest-redux-integrate/SKILL.md).

A specialized skill for building and running in-game integration tests for RimWorld mods with [RimTest Redux](https://steamcommunity.com/sharedfiles/filedetails/?id=3762405308), while steering clear of startup timing race conditions and Harmony engine pitfalls that cause tests to spuriously pass or fail.

Headless unit tests run with Unity and game subsystems stubbed out, meaning they cannot verify whether a Harmony patch actually injected, when deferred game startup operations complete, or how graphics atlases and dynamically injected translations resolve in the live engine. In-game tests bridge this critical gap — provided they synchronize with the correct lifecycle timing and compare against an untainted baseline.

## When It Applies

Applies whenever writing or debugging integration tests for RimWorld mods, including validating that Harmony patches inject successfully and diagnosing startup timing failures. The user's request does not need to mention RimTest Redux explicitly.

The skill begins by **asking** whether to introduce RimTest Redux into the project. It automatically skips this prompt if the repository already contains a companion test mod depending on RimTest Redux. If the user prefers an alternative approach, the remainder of this skill steps aside.

## What It Covers

1. **Companion Mod Architecture**: Tests are isolated within a dedicated, development-only companion test mod that loads before the target mod, references its compiled DLL, and is strictly excluded from release packages.
2. **Writing In-Game Tests**: Structured `[TestSuite]` and `[Test]` classes that batch failure reports for collective inspection. When environmental prerequisites (such as an active map or compatible third-party mod) are missing, tests log explicit skip rationale and exit early.
3. **Harmony Baseline Comparison**: Employs Harmony Reverse Patching to dynamically reconstruct unmodified vanilla methods, comparing mod output item-by-item (content and ordering). Comparisons are scoped to objects instantiated through vanilla entry points to avoid cross-contamination from third-party mods writing directly to cached fields.
4. **State Probes**: `[HarmonyPatch]` classes that inspect and record internal state across all overloads of their target, using `Prepare()` to safely deactivate themselves when target methods are absent.
5. **Lifecycle & Timing Safeguards**: RimTest Redux automatically awaits queued `LongEvent` tasks at startup, but does not inherently await asynchronous `Task` instances, worker threads, or multi-frame coroutines. For such mods, a custom test driver monitors explicit completion signals dispatched by the mod under test.
6. **Granular Reporting**: Executes suites across distinct mod setting combinations, reporting passed, failed, and skipped metrics. Every failure is accurately classified as a bug in the mod under test, vanilla behavior, or RimTest Redux framework behavior.

The skill also includes [`references/rimtest-redux-api.md`](../rimtest-redux-integrate/references/rimtest-redux-api.md), containing framework rules, attribute definitions, assertion APIs, internal reflection hooks for custom drivers, and complete code examples (basic test suite, collected assertions with skip logging, and a custom test driver).

## Harmony & Mono Pitfalls

| Pitfall | Root Cause & Diagnostic | Solution |
| --- | --- | --- |
| **`catch … when` Exception Filter** | Mono compiler failure: "Incorrect code generation for exception block" when patching methods containing exception filters. | Replace `catch … when` constructs with standard sequential `catch` blocks in any method targeted by a patch. |
| **`Harmony.PatchCategory(string)`** | `PatchCategory` resolves using the calling assembly. Invoking it directly from test assemblies causes Mono runtime crashes. | Always supply the target mod assembly explicitly when calling category patches. |

## Prerequisites

Running in-game tests requires RimWorld 1.6 with the following mods installed in the load order:
- `brrainz.harmony` (Harmony library)
- `ilyvion.Laboratory` (Test framework prerequisite)
- `ilyvion.rimtestredux` (RimTest Redux test runner)

The companion test project must target `.NET Framework 4.8.1` (`net481`).

## Install

From the repository root, use the `skills` CLI to discover supported agent hosts and install this skill:

```bash
npx skills add . --skill rimtest-redux-integrate
```

Add `--global` for personal user scope; omitting it installs at project scope. For manual installation, copy `rimtest-redux-integrate/` directly into your agent host's configured skills directory.

> [!NOTE]
> The initial `npx` invocation may download the CLI. Reload or restart your agent host if it only discovers skills during session startup.
