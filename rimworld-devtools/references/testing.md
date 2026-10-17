# Integration and Test Authoring

## Build and Assembly Loading

| Item | Configuration / behavior |
| --- | --- |
| Framework | `Directory.Build.props` sets `net10.0`, `LangVersion=preview`, and warnings as errors; use an SDK supporting the required language features |
| Game references | `UseKrafsPackageRef=false` loads game DLLs from `RefDir`, including Waylith/Brutal assemblies. The `true` branch still specifies `Krafs.Rimworld.Ref 1.6.*`; this does not establish compatibility with RimWorld 1.6 |
| Output | `DevTools.csproj` uses `$(ModDir)\1.7\Assemblies\`; check or override output for cross-repository ProjectReferences to avoid writing into another mod |
| Discovery | `DevHarmony` scans active mods' `loadedAssemblies` during `[StaticConstructorOnStartup]` and registers tools for matching types |
| Host | Both DevTools and test DLLs must be loaded by an active ModContentPack; creating a test project alone does not enable discovery |
| packageId | The CLI targets the mod containing the test assemblies; use the companion mod's packageId when tests live there |

For initial integration:

1. Prefer existing local SmashPhil DevTools sources/DLLs. Download `SmashPhil/DevTools` from GitHub only when missing, and retain it locally. Prepare the .NET 10 SDK, game assemblies, and Harmony references.
2. Reference the DevTools project/DLL from the test project or development-only companion mod, along with the required Verse/RimWorld/Unity assemblies.
3. Set the ProjectReference's `OutDir`/`OutputPath` or copy DLLs explicitly into the game's loading path. `Private=false` only prevents automatic reference copying; one DevTools DLL must still be loaded by the game.
4. Check `LoadFolders.xml` and actual assembly paths. Do not invent a DevTools packageId or use `IfModActive="DevTools"`. Avoid loading multiple DevTools versions.
5. Check the release archive/staging directory for DevTools/test DLLs and development configuration, including leftovers from earlier builds. Excluding a project from Release does not remove existing DLLs.

## Fixtures and Lifecycle

```csharp
using DevTools.Testing;
using Verse;

namespace MyMod.Tests;

[TestFixture(TestType.MainMenu)]
internal sealed class ThingStateTests
{
    [Test]
    public void KeepsAssignedStackCount()
    {
        var thing = new Thing { stackCount = 7 };
        Expect.AreEqual(7, thing.stackCount);
    }
}
```

- Fixtures must be non-static, non-abstract classes with exactly one public instance constructor. An internal class's implicit default constructor works. Static fixture classes are silently excluded.
- One instance is created per fixture run; all methods share its fields. `[SetUp]`/`[TearDown]` run around each test; `[OneTimeSetUp]`/`[OneTimeTearDown]` run around the fixture. These methods must return `void`. Per-test TearDown runs through a `finally` path; fixture initialization failures do not guarantee full recovery.
- `MainMenu` requires no live map. `Playing` generates a world and map first. `PostGameExit` enters a game and then returns to the main menu for testing.
- Consecutive fixtures can share a map when their scene and settings remain unchanged. `IWorldGeneration`, `IMapGeneration`, `IScenario`, and `IStoryteller` customize the fixture environment. Use `[LoadSave]` for a saved game; avoid combining it with custom generation settings.
- Higher `[ExecutionPriority]` values run first. Each test should establish its own prerequisites rather than depend on previous results.

## Common APIs

| Need | Usage / restriction |
| --- | --- |
| Synchronous / multi-frame tests | `[Test] void` / `[Test] IEnumerator` |
| Inline cases | `[TestCase(2, 3, ExpectedResult = 5)]` on a method returning the result; it inherits `[Test]`, so do not add another `[Test]` |
| Parameter sources | `[Parameters(...)]`, `[ParametersSource(...)]`, or `[DefParameters(...)]` on method/constructor parameters; at most one source-based parameter, unlike TestCase arguments |
| External sources | ParametersSource supports static array fields or static methods returning `IEnumerable` |
| Categories / disabling | `[TestCategory("integration")]` / `[Disabled]`; cases excluded during registration by disabling or missing mods are not executed skips |
| Mod / DLC requirements | `[LoadIfModsActive(...)]`, `[LoadIfAnyModsActive(...)]`, and DLC-specific attributes |
| Retries | `[Retry(n)]`; record retries and investigate leaked state or waiting conditions rather than masking instability |
| Expected logs | `[WarningsAllowed("narrow regex")]` / `[ErrorsAllowed(...)]`, preferably on the method producing that message |

`Expect` does not throw or support fluent chains. `Test.Fail`, `Test.Skip`, and `Test.Cancel` also only set status; explicitly `return`/`yield break` when execution must stop:

```csharp
Expect.IsNotNull(value);
if (value == null)
    return;
Expect.AreEqual(expected, value.Count);
```

Common assertions: `IsTrue/IsFalse`, `IsNull/IsNotNull` (class types), `AreEqual/AreNotEqual` (expected first), `AreApproximatelyEqual` (float), `ReferencesAreEqual`, comparisons such as `GreaterThan/LessThan`, `IsEmpty/IsNotEmpty`, `All/Any/None`, `Throws<T>(Action)`, and `DoesNotThrow(Action)`.

For element-wise sequence equality, use `Expect.That(() => expected.SequenceEqual(actual))` with `System.Linq`; `AreEqual` does not compare two Lists element by element. Prefer `Expect` over `UnityEngine.Assertions.Assert`, whose calls can depend on the `UNITY_ASSERTIONS` compilation symbol.

## Maps, Coroutines, and Cleanup

Create game objects with vanilla APIs such as `ThingMaker.MakeThing`, `PawnGenerator.GeneratePawn`, and `GenSpawn.Spawn`. To verify patches, exercise the actual player-facing entry point rather than calling postfixes or writing fields directly.

Tests run on the main thread; the runner does not await `Task`/`async void`. Use `IEnumerator` across frames and bound waits by ticks or real time. `yield return null` advances one frame; `WaitTicks`/`WaitUntilTimeout` depend on game ticks and do not advance while paused. For controlled simulation, pause and call `DoSingleTick()` in batches, yield frames, check a bounded condition, and restore speed afterward. Startup work spread across Tasks or update loops needs an explicit completion signal; finishing long events alone is insufficient.

Consecutive Playing fixtures may share a map. Use `TearDown`/`finally`/`IDisposable` to restore settings, defs, static fields, and speed. Remove only pawns, items, quests, letters, windows, and other objects created by the test. Destroyed containers/pawns can drop contents; clean those up too. Use `ScopedMethodHook` for temporary Harmony patches.

When importing Harmony, `DevTools.Testing.MethodType` can cause ambiguity. Add `using MethodType = HarmonyLib.MethodType;` if needed.
