---
name: rimworld-devtools
description: Integrate and use SmashPhil DevTools for in-game RimWorld mod tests, result interpretation, and benchmarks. Use when DevTools is explicitly selected or already used by the project; not for browser developer tools.
---

# RimWorld Mod Testing

SmashPhil DevTools is an SDK embedded in a host mod. Both `DevTools.dll` and the test DLL must be loaded by an active mod; DevTools has no standalone packageId.

## Workflow

Reuse the project's existing DevTools references, assembly output, and loading configuration. Read the relevant reference:

- Integration, fixtures, assertions, parameters, coroutines, and cleanup: [references/testing.md](references/testing.md).
- UI/CLI execution, configuration, results, and troubleshooting: [references/running.md](references/running.md). Read before running tests.
- Test plans, smoke tests, and benchmarks: [references/advanced.md](references/advanced.md).

Use this skill and local DevTools sources/DLLs for routine work, including API checks. Fetch `SmashPhil/DevTools` from GitHub only during initial integration when it is missing locally. Do not routinely access the network to check documentation or versions.

Rebuild and restart the game before running the relevant fixtures. Save progress first: tests switch scenes and return to the main menu.

Report the filter, passed/failed/skipped/not-run counts, and result file paths. Report zero-test runs and interrupted runs separately; neither counts as a pass.
