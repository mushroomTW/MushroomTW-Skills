# Targeting, Events, and Patch Contracts

Verify API signatures and prerequisites against the locally adopted version; see [Feature Index](features.md) for other categories.

## Targeting Dispatch System (Targeting)

- **Purpose**: Replaces or extends vanilla RimWorld `Targeter`, supporting layered targeter stacks, custom target updates, and callbacks.
- **Representative Types and Methods**:
  - `SmashTools.Targeting.Targeter<T>`: Base targeter class.
  - `SmashTools.Targeting.MapTargeter`: Abstract map targeter class.
  - `SmashTools.Targeting.WorldTargeter`: Abstract world map targeter class.
  - `SmashTools.Targeting.TargeterDispatcher`: Static targeter dispatcher providing extension methods `targeter.Start()` and `targeter.Stop()`.
  - `SmashTools.Targeting.TargetValidation`, `ITargetOption`: Target validity validation and confirmation menu options.
- **Constraints**: Initiation and operations must be executed on the main thread.
- **Source Locations**: `SmashTools/SmashTools/Targeting/`

## Game Events and Scoped Control (Events)

- **Purpose**: Extends game lifecycle event broadcasting and provides keyed event managers with scoped suppression capabilities.
- **Representative Types and Methods**:
  - `SmashTools.GameEvent`: Global static events covering `OnNewGame`, `OnLoadGame`, `OnMainMenu`, `OnGameDisposing`, `OnWorldUnloading`, `OnWorldRemoved`, `OnGenerateImpliedDefs` (provides the timing to inject dynamic Defs before DefDatabase resolution).
  - `SmashTools.EventManager<T>`: Generic keyed event manager accessing `EventTrigger` via `manager[key]`.
  - `SmashTools.EventDisabler`: RAII struct that temporarily disables event broadcasting for a specified `IEventControl`.
- **Usage Example**:

  ```csharp
  // Pause event firing during batch data updates; automatically resume upon exiting using
  using (new EventDisabler(myEventManager))
  {
      PerformBatchUpdates();
  }
  ```

- **Source Locations**: `SmashTools/SmashTools/Events/`

## Harmony Patching Extension Contracts (Patching Contracts)

- **Purpose**: Public extension interfaces for mods to declare phased patching and conditional patching for dependent mods.
- **Representative Types**:
  - `SmashTools.Patching.IPatchCategory`: Patch grouping interface declaring execution timing phase via `PatchSequence PatchAt { get; }` (e.g., `Mod`, `PostDefDatabase`, `Async`), implementing `PatchMethods()` to execute patches for that phase.
  - `SmashTools.Patching.IConditionalPatch`: Conditional patch interface declaring `string PackageId` and `PatchSequence PatchAt`; when the target mod is present and active, the framework invokes `PatchAll(ModMetaData mod)` to execute compatibility patches.
- **Lifecycle Specifications**: See [lifecycle.md](lifecycle.md) for registration timing, Harmony owner, and scan scope.
- **Source Locations**: `SmashTools/SmashTools/Patching/Harmony/`
