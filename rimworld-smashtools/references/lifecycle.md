# Initialization, Verification, and Troubleshooting

## Verify the Actual Startup Path

Locate `ProjectSetup`, `ProjectStartup`, `HarmonyPatcher`, and their callers in local SmashTools sources; names and signatures follow the adopted version. When only DLLs are available, determine visibility and call relationships via metadata or decompilation.

| Checkpoint | Contract to Verify |
| --- | --- |
| `Verse.Mod` subclass and constructor | Which mod instantiates the entry point, which `ModContentPack` is passed, and how existing mod entry points coexist with it |
| Startup static constructor | When it is triggered by the game, and whether it depends on prior registration, Def loading, or delayed cross-reference resolution |
| Patcher initialization | The source of the Harmony owner, and whether patch classes scan the provider, consumer, or other assemblies |
| Events and background jobs | Subscription and cleanup for scene/world events, completion signals and wait sites for asynchronous patches |

The completion criterion is tracing the exact sequence: "game loads assembly → initialization owner → registration → integrated feature usage," ensuring every required initialization runs exactly once. Confirming that the DLL merely appears in loaded assemblies is insufficient to prove this path is sound.

## Integration Principles

Place necessary wiring within existing lifecycle entry points, preserving initialization ownership to the correct `ModContentPack`. Avoid repeatedly creating Mod instances at caller sites or manually re-running startup static constructors just to obtain utility classes; event subscriptions and patch registrations may accumulate as a result.

If a patcher only scans assemblies of the passed mod, external provider initialization will not automatically discover consumer patches. Consumers should retain their own Harmony entry point and owner for general patches; when using SmashTools patch categorization mechanisms, verify their registration scope, execution phase, and public APIs first. `internal` initialization methods are not interfaces for consumers to call directly.

Confirm the owner using the Harmony instance actually created by the initializer; constant names do not guarantee runtime values. When verifying patches, inspect target method patch metadata to distinguish between multiple expected patches and duplicate registration of the same patch.

If background work spans Tasks, update loops, or multiple frames, await its actual completion signal before using features dependent on results. After scene or world unloading, confirm that events, threads, and caches used in this run are cleaned up per source contracts.

## Minimal Verification

1. Build in release configuration, confirm artifacts are the exact files the game is about to load, and complete release checks in [integration.md](integration.md).
2. Restart the game, record the mod list for this run, and confirm initialization order and load logs; Release builds do not necessarily output Debug-only reports, so missing such messages alone does not indicate failure.
3. Operate integrated APIs from actual feature entry points. Verify UI state restoration, saving/loading, background task completion, or world unloading cleanup according to feature specifications; do not exhaustively test unused utility classes.
4. When intended to coexist with other SmashTools providers, rerun loading and integrated features with that mod combination to verify actual assembly sources and patch owners.

Existing in-game test frameworks can be used for these checks; integrating SmashTools itself does not require installing additional test frameworks. When game execution conditions are unavailable, deliver build and release verification results, marking load, feature, and coexistence checks as unverified.

## Troubleshooting

| Symptom | Primary Checkpoint |
| --- | --- |
| Build succeeds, but game cannot find assembly | `Private`/copy steps, whether provider is enabled, LoadFolders.xml active directory, and release package contents |
| `MissingMethodException` / `TypeLoadException` | Whether loaded DLL matches compilation references, game API compatibility, stale artifacts, or duplicate assemblies |
| Class is callable, but patch does not take effect | Initialization entry point, registration scan scope, execution phase, and target method patch metadata |
| Duplicate callbacks or duplicate patches | Whether Mod entry point was instantiated manually again, multiple providers, event subscriptions, and initialization invocation counts |
| Same-name type cast failure | Actual assembly identity and loading source of the type, rather than namespace/class name alone |
| Intermittent error on startup or unload | Async task completion conditions, event timing, background work, and cache cleanup |

## Internal Maintenance and Lifecycle Implementation Directory Notice

The following source directories are internal mechanisms of the SmashTools framework, managed collectively by mod startup workflows or patching pipelines. **Mod developers should not directly invoke their internal types manually**:

- `SmashTools/SmashTools/Patching/`: Contains internal auto-install patchers `Patch_Components`, `Patch_Events`, `Patch_Rendering`, `Patch_XmlParsing`, and `HarmonyPatcher`. These patch classes are responsible for hooking core SmashTools features and are automatically injected sequentially by the framework at startup without requiring manual caller invocation. (For public extension contracts `IPatchCategory` / `IConditionalPatch`, refer to [Patching Contracts](events-patching.md) and [lifecycle.md](lifecycle.md)).
- `SmashTools/SmashTools/Jobs/`: Contains `BurstAssemblyLoader` and `JobDispatch`, responsible for loading Burst binary assemblies and scheduling Jobs into the game heartbeat.
- `SmashTools/SmashTools/` root directory: Contains `ProjectSetup`, `ProjectStartup`, `DllInjector`, and `TestWatcher`, serving as mod loading and DLL injection entry points.
- `SmashTools.PathFinder/Snapshot/`: Contains `Snapshot*Job`, internal grid data snapshot Burst jobs.
- `SmashTools.Rendering/` internal types: `Backend`, `BehaviourGui`, `Host`, `WindowGui`, `WindowInput`, and `WindowStackContext`, implementing Waylith / Vulkan low-level window message forwarding.
