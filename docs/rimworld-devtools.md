# RimWorld Mod Testing

**English** | [繁體中文](rimworld-devtools.zh.md)

This skill helps agents integrate SmashPhil DevTools, write and run in-game RimWorld mod tests, and interpret results. It also covers smoke tests, child-process test plans, and benchmarks.

Entry point: [`rimworld-devtools/SKILL.md`](../rimworld-devtools/SKILL.md).

## Usage

After installing `rimworld-devtools/` in your skills host:

```text
Use $rimworld-devtools to add map-based tests to this mod, run the relevant fixture, and report results.
```

Other uses include investigating missing fixtures, configuring Test.log and reports, or comparing method performance. Automatic selection is enabled for projects that explicitly select or already use DevTools.

Integration needs DevTools sources/DLLs, the .NET 10 SDK, and game reference assemblies. Tests run inside RimWorld.

Prefer local DevTools sources. Download `SmashPhil/DevTools` from GitHub only during initial integration when missing locally. Routine work and API checks do not require network access.

## Contents

- `references/testing.md`: Assembly loading, fixtures, non-throwing assertions, parameters, coroutines, and cleanup.
- `references/running.md`: UI/CLI, configuration, fresh logs, completion evidence, counts, and troubleshooting.
- `references/advanced.md`: Smoke-test hosts, test-plan recovery, and benchmark restrictions.
