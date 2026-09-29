---
name: rimtest-redux-integrate
description: Use when writing or debugging tests for a RimWorld mod — including checking that Harmony patches really apply and startup-timing failures — even if RimTest Redux is never mentioned.
---

# RimWorld Mod Testing (RimTest Redux)

[RimTest Redux](https://github.com/ilyvion/rimtest-redux) (`ilyvion.rimtestredux`, RimWorld 1.6 only) runs `[TestSuite]` / `[Test]` classes inside the live game. Before writing the first test, read [references/rimtest-redux-api.md](references/rimtest-redux-api.md): framework rules, assertions, internals, and examples.

## 1. Ask first

If the repository already has a companion test mod depending on `ilyvion.rimtestredux`, skip to section 3.

Otherwise ask the user whether this mod should get in-game integration tests with RimTest Redux, naming what headless tests miss with Unity stubbed: patches actually applied, load timing, atlases, translation injection. If they decline, follow their choice and leave this skill.

## 2. Project layout

- Tests live in a development-only companion mod (e.g. `Source/<Mod>.InGameTests/`, About and Assemblies under `Mod/`), outside the `.sln` and never shipped with the mod under test.
- The test DLL builds into its own `Mod/Assemblies/` and references the target's `Assemblies/*.dll`; building tests never rebuilds the target, so Release-build it yourself after changing it.
- Dependencies: `brrainz.harmony`, `ilyvion.Laboratory`, `ilyvion.rimtestredux` (Workshop 3762405308, net481).
- The test mod's `About.xml` lists the target in `<loadBefore>`, so probes are in place before the target's constructor runs.

## 3. Writing tests

- Collect failures and throw once (a custom `AssertNone(failures, msg)`), so one run shows every failure.
- When a precondition is absent (no map, compatible mod missing), log `skipped: <reason>` and `return`. The runner counts such a test as passed, so section 6 counts skips from these log lines.
- **Vanilla baseline**: get the unmodified method through a Harmony reverse patch and compare the mod's result item by item — content and order, not just count; when that is too expensive, recompute from one vanilla list. Compare only objects created through the vanilla entry point (e.g. `GraphicData.Init`), tagged by a probe — other mods write fields directly (e.g. Bionic Icons writes `cachedGraphic`).
- **Probes**: a `[HarmonyPatch]` class records state. Enumerate every overload of the target; `Prepare()` returns false when none is found.
- For a path the game never reaches naturally, rebuild the scenario by hand, call the postfix, and restore state in `finally` or `[AfterEach]`.

## 4. Timing

Built-in **Run at startup** waits for queued long events, not for work on Tasks, threads, or spread across frames by the mod's own update loop. Search the mod under test for such work; if any exists, turn Run at startup off and use a custom driver (reference, Example 3):

- The mod under test exposes the completion signal (e.g. counters `Started >= round && LastFinished == Started`, updated in `finally`), counted per round; `Runner.RunAllRegisteredTests` can rerun each round.
- The signal check lives in one shared helper class used by every suite. Map tests also wait for `ProgramState.Playing` and a current map.

## 5. Harmony pitfalls

| Pitfall | Remedy |
|---|---|
| A method with a `catch … when` filter cannot be patched ("Incorrect code generation for exception block", on the net9 test host and in Mono) | Use separate plain `catch` blocks, and no filters or finalizers, in any method that must be patched |
| `Harmony.PatchCategory(string)` uses the **calling** assembly; called from a test it scans the test assembly and crashes Mono | `PatchCategory(typeof(Mod).Assembly, "Category")` |

## 6. Running and reporting

- Run once per settings combination (defaults, everything enabled, map-requiring quicktest, compatible-mod set); record passed, failed, and skipped counts for each.
- Classify every failure as a bug in the mod under test, vanilla behavior, or RimTest Redux's own behavior; name any combination not rerun.
