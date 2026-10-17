# Logging, Performance, and Development Tools

Verify API signatures and prerequisites against the locally adopted version; see [Feature Index](features.md) for other categories.

## Core Logging and Trace (Logging & Trace)

- **Purpose**: Low-level console logging output and debug assertion tracing independent of RimWorld UI.
- **Representative Types**:
  - `CoreLib.Logger`: Low-level static logger (`Message`, `Warning`, `Error`).
  - `SmashTools.Trace`: Assertions and error tracing (`Trace.Fail(string message)`).
- **Source Locations**: `Core/Logging/`

## Caching and Profiling (Performance & Profiling)

- **Purpose**: Map component caching and method-level Harmony performance profiling.
- **Representative Types and Methods**:
  - `SmashTools.ComponentCache`:
    - `map.GetCachedMapComponent<T>()`: Replaces vanilla RimWorld linear traversal queries on the map component list with dictionary and type-indexed caching.
    - `map.GetDetachedMapComponent<T>()`: Accesses detached-lifecycle `DetachedMapComponent`.
  - `SmashTools.Performance.Profiler`:
    - `Profiler.Begin(string label)` / `Profiler.End(Timer timer)`
    - `using (new ProfilerScope("Label"))` scope execution time recording.
    - Annotate with `[Profile]` or `[NoProfiling]` attributes to automatically inject Harmony profiling hooks.
  - `SmashTools.Performance.GlobalObjectPool`: Global object pool.
- **Source Locations**: `SmashTools/SmashTools/Performance/`

## Semantic Tag Logging (Logging)

- **Purpose**: Rich-text logging utility supporting custom semantic tags to output colored console messages.
- **Representative Types and Methods**:
  - `SmashTools.SmashLog`:
    - `Message(string text)`, `Warning(string text)`, `Error(string text)`, `ErrorLabel(string label, string text)`: Supports colored output by parsing tags like `<field>`, `<property>`, `<method>`, `<struct>`, `<class>`, `<type>`, `<success>`, `<error>`, `<warning>`, `<mod>`, `<attribute>`, `<xml>`.
    - Semantic tags are registered internally by `SmashLog`; `RegisterRichTextBracket` is private, consumers use existing tags.
- **Constraints**: Relies on Unity GUI rich-text parsing and `Verse.Log`; `QuickMessage` is marked `[Obsolete]` for development testing only and must not be used in production code.
- **Source Locations**: `SmashTools/SmashTools/Logging/`

## Development, Debugging, and Attributes (Debugging & Attributes)

- **Purpose**: Rapid debugging entry points, camera tracking, and dynamic field tweaking during mod development.
- **Representative Types**:
  - Attributes: `[TweakField]` (marks fields adjustable in the tweak window), `[StartupAction]` (game startup test task), `[StaticConstructorOnModInit]` (executes immediately upon Mod instantiation), `[StaticConstructorOnGameInit]` (executes immediately upon entering game), `[GraphEditable]`.
  - Debuggers: `CameraAttacher`, `CameraController`, `QuickStartMenu`, `MainMenuKeyBindHandler`, `GameState`.
- **Source Locations**: `SmashTools/SmashTools/Debugging/`, `SmashTools/SmashTools/Attributes/`

## SmashTools.Analyzer Compile-Time Analysis Rules (`SmashTools.Analyzer/`)

- **Purpose**: Roslyn static code analyzers and warning suppressors preventing common RimWorld modding mistakes at build time.
- **Representative Rules**:
  - `VF0001` (`UsedWithReflectionAnalyzer`): Emits a warning when a member annotated with `[UsedWithReflection]` is referenced directly in code rather than invoked via reflection.
  - `VF0002` (`DisposableWindow`): Emits an error when a class inherits `Verse.Window` and implements `IDisposable` (RimWorld does not call `Dispose()` when closing windows, leading to resource leaks).
  - `VF0003` (`AccessToolsConstructorAnalyzer`): Enforces using `AccessTools.DeclaredConstructor` instead of `AccessTools.Constructor` to avoid resolving to a base class constructor.
  - `VFSPR0001` (`AssignedFromXmlSuppressor`): Automatically suppresses CS0649 (unassigned field) compiler warnings for fields annotated with `[UsedWithReflection]` or `[AssignedFromXml]`.
- **Prerequisites and Constraints**: A compile-time analyzer project included via `<Analyzer Include="..." />` in project files; contains no runtime callable APIs.
- **Source Locations**: `SmashTools.Analyzer/`
