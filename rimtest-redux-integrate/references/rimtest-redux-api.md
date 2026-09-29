# RimTest Redux API

Adapted from the [RimTest Redux README](https://github.com/ilyvion/rimtest-redux) (mod 0.2.0, RimWorld 1.6); internals and examples 2–3 checked against its source.

## Framework rules

- Every assembly loaded into the game is scanned for `[TestSuite]` classes; no registration step.
- Suite classes are `static`; `[Test]`, `[BeforeEach]`, `[AfterEach]` methods are `static void` with no parameters; at most one `[BeforeEach]` and one `[AfterEach]` per suite.
- Status **SKIP** means only that a suite or test breaks these rules; there is no run-time skip API.
- An assembly referencing `RimTestRedux` types fails to load entirely without `RimTestRedux.dll` — hence the separate companion mod.
- **Run at startup** is toggled in Mod Options → RimTest Redux.

## Attributes (namespace `RimTestRedux`)

| Attribute | Effect |
| --- | --- |
| `[TestSuite]` | Registers a static class as a suite |
| `[Test]` | Registers a test |
| `[BeforeEach]` / `[AfterEach]` | Run around every test; `[AfterEach]` runs in `finally`, even when the test throws |
| `[ShouldThrow]` / `[ShouldThrow(typeof(T))]` | Passes only if the test throws (a `T`, when given) |

## Assertions

`Assert.That…` entry point, optional grammar links (`.To` `.Is` `.Be` `.Do` `.Does` `.Has` `.Have` `.The`, no effect), then a check; `.Not` negates the next check.

| Entry point | Checks |
| --- | --- |
| `Assert.That(IComparable)` | `EqualTo`, `LessThan`, `GreaterThan`, `BetweenInclusive(min, max)`, `BetweenExclusive(min, max)`, `SameValueAs`, `SameReferenceAs`, `Null()`, `True()`, `False()` |
| `Assert.ThatCollection(IEnumerable)` | `Contain(item)`, `Empty()`, `Count(n)` |
| `Assert.ThatFunc(Func<dynamic>)` / `Assert.ThatFunc(Action)` | `Throw()` |

A failed check throws the public `RimTestRedux.AssertionException(string)`; throw it yourself for a custom assertion.

## Internals a custom driver needs

`internal`, so reach them through reflection:

| Member | Purpose |
| --- | --- |
| `RimTestRedux.Testing.Runner:RunAllRegisteredTests` | Runs every registered assembly; repeatable, each call overwrites prior statuses |
| `RimTestRedux.Testing.StatusExplorer:UpdateAllStatusCounts` | Refreshes the runner window's counts |
| `RimTestRedux.Testing.Viewer:LogTestsResults` | Writes results to the game log |

Built-in run-at-startup is a `Root.Update` postfix: once `PlayDataLoader.Loaded && !LongEventHandler.AnyEventNowOrWaiting && Find.UIRoot != null`, it calls those three through `LongEventHandler.ExecuteWhenFinished`.

## Example 1: basic suite

Abridged from the upstream README.

```csharp
using System;
using RimTestRedux;

namespace MyMod.Tests;

[TestSuite]
internal static class InventoryTests
{
    private static Pawn testPawn = null!;

    [BeforeEach]
    public static void SetUp() => testPawn = CreateTestPawn();

    [AfterEach]
    public static void TearDown() => testPawn.Destroy();

    [Test]
    public static void PawnStartsWithNoWeapons() =>
        Assert.ThatCollection(testPawn.equipment.AllEquipmentListForReading).Is.Empty();

    [Test]
    [ShouldThrow(typeof(ArgumentNullException))]
    public static void EquipNullWeaponThrows() => testPawn.equipment.AddEquipment(null!);

    [Test]
    public static void HealthPercentIsWithinExpectedRange() =>
        Assert.That(testPawn.health.summaryHealth.SummaryHealthPercent).Is.BetweenInclusive(0.0, 1.0);

    private static Pawn CreateTestPawn() => /* ... */ null!;
}
```

## Example 2: collected failures and logged skips

```csharp
using System.Collections.Generic;
using System.Linq;
using RimTestRedux;
using Verse;

namespace MyMod.InGameTests;

[TestSuite]
internal static class MapTests
{
    [Test]
    public static void EveryPawnHasMyComp()
    {
        if (Find.CurrentMap == null)
        {
            Log.Message("[MyMod.InGameTests] skipped: EveryPawnHasMyComp needs a map");
            return;
        }
        var failures = Find.CurrentMap.mapPawns.AllPawnsSpawned
            .Where(p => p.GetComp<MyComp>() == null)
            .Select(p => p.LabelShort)
            .ToList();
        TestHelpers.AssertNone(failures, "pawns without MyComp");
    }
}

internal static class TestHelpers
{
    public static void AssertNone(List<string> failures, string message)
    {
        if (failures.Count > 0)
            throw new AssertionException($"{message} ({failures.Count}):\n{string.Join("\n", failures)}");
    }
}
```

## Example 3: custom driver

Applied by the test mod's own `Harmony.PatchAll()`. `MyMod.Startup.Finished` stands for the completion signal the mod under test exposes.

```csharp
using System;
using HarmonyLib;
using Verse;

namespace MyMod.InGameTests;

[HarmonyPatch(typeof(Root), nameof(Root.Update))]
internal static class TestDriver
{
    private static readonly Action RunAll = Internal("Runner:RunAllRegisteredTests");
    private static readonly Action UpdateCounts = Internal("StatusExplorer:UpdateAllStatusCounts");
    private static readonly Action LogResults = Internal("Viewer:LogTestsResults");

    private static bool hasRun;

    public static void Postfix()
    {
        if (hasRun || !Ready())
            return;
        hasRun = true;
        RunAll();
        UpdateCounts();
        LogResults();
    }

    private static bool Ready() =>
        PlayDataLoader.Loaded
        && !LongEventHandler.AnyEventNowOrWaiting
        && Find.UIRoot != null
        && MyMod.Startup.Finished;

    private static Action Internal(string typeColonMethod) =>
        AccessTools.MethodDelegate<Action>(AccessTools.Method("RimTestRedux.Testing." + typeColonMethod));
}
```
