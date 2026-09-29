# RimTest Redux Integrate

**English** | [繁體中文](rimtest-redux-integrate.zh.md)

> This document lives in `docs/`. The skill itself is at [`rimtest-redux-integrate/SKILL.md`](../rimtest-redux-integrate/SKILL.md).

A skill for testing RimWorld mods inside the running game with [RimTest Redux](https://steamcommunity.com/sharedfiles/filedetails/?id=3762405308), and for avoiding the timing and Harmony traps that make such tests pass or fail for the wrong reason.

Headless unit tests run with Unity stubbed out, so they never see whether a Harmony patch was actually applied, when deferred startup work finishes, or what atlases and injected translations end up looking like. In-game tests cover exactly that gap — but only if they wait for the right moment and compare against the right baseline.

## When It Applies

Whenever you write or debug tests for a RimWorld mod, including checking that Harmony patches really apply and chasing startup-timing failures. The request does not have to mention RimTest Redux.

The skill first **asks** whether to use RimTest Redux, and skips the question when the repository already has a companion test mod depending on it. If you pick another approach, the rest of the skill stays out of the way.

## What It Covers

1. **Project layout** — tests live in a separate, development-only companion mod that loads before the mod under test, references its built DLL, and never ships with it.
2. **Writing tests** — `[TestSuite]` / `[Test]` classes, failures collected and reported together; when a precondition (a map, a compatible mod) is absent, the test logs a skip reason and returns early.
3. **Vanilla baseline** — a Harmony reverse patch recovers the unmodified vanilla method, and the mod's result is compared item by item, content and order — limited to objects created through the vanilla entry point, since other mods write cached fields directly.
4. **Probes** — `[HarmonyPatch]` classes that record state, cover every overload of their target, and disable themselves through `Prepare()` when no target is found.
5. **Timing** — RimTest Redux's run-at-startup waits for queued long events but not for work on Tasks or threads or spread across frames, so for such mods a custom driver waits for a completion signal the mod under test provides.
6. **Reporting** — one run per settings combination with passed, failed, and skipped counts each, and every failure classified as the mod's bug, vanilla behavior, or RimTest Redux's own behavior.

The skill also carries [`references/rimtest-redux-api.md`](../rimtest-redux-integrate/references/rimtest-redux-api.md): RimTest Redux's framework rules, attributes, and assertion API adapted from its README, the internal members a custom driver calls through reflection, and three examples — a basic suite, collected failures with logged skips, and a custom driver.

## Harmony Pitfalls

| Pitfall | Remedy |
| --- | --- |
| A method containing a `catch … when` filter cannot be patched ("Incorrect code generation for exception block") | Use separate plain `catch` blocks in any method that must be patched |
| `Harmony.PatchCategory(string)` uses the calling assembly, so calling it from a test crashes Mono | Pass the target assembly explicitly |

## Requirements

Running the tests needs RimWorld 1.6 with the `brrainz.harmony`, `ilyvion.Laboratory`, and `ilyvion.rimtestredux` mods installed; the test assembly targets net481.

## Install

From the repository root, let the `skills` CLI discover supported agents and install this skill:

```bash
npx skills add . --skill rimtest-redux-integrate
```

Add `--global` for personal scope; without it, the CLI installs at project scope. For a manual installation, copy `rimtest-redux-integrate/` to a skills directory documented by the host instead of assuming a runtime-specific path.

> [!NOTE]
> The first `npx` invocation may download the CLI. Reload or restart the host when it only discovers skills at session start.
