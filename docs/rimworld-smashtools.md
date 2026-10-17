# RimWorld SmashTools Integration and Usage

**English** | [繁體中文](rimworld-smashtools.zh.md)

Helps select existing SmashTools features for RimWorld mod development, and handles integration, packaging, initialization, and loading problems. Entry point: [`rimworld-smashtools/SKILL.md`](../rimworld-smashtools/SKILL.md).

The feature guide covers CoreLib native collections, threading and pools; search and multi-cell pathfinding; targeting and events; UI, windows and rendering; persistence and XML; animation curves; caching, profiling, logging, extensions and compile-time analyzers. Find representative APIs, constraints and source locations by purpose.

Automatic selection is enabled, or invoke it directly:

```text
Use $rimworld-smashtools to integrate SmashTools into this RimWorld mod.
```

For an existing integration:

```text
Use $rimworld-smashtools to find existing features, then implement this mod's UI and data persistence logic.
```

Prefers local sources and DLLs. Building requires compatible tools and game reference assemblies; runtime verification requires the game.

## Contents

- `references/features.md`: Feature index for selecting the relevant reference.
- `references/core.md`: Collections, geometry, threading, jobs, pools and dynamic delegates.
- `references/pathfinding.md`: Search, optimal assignment and multi-cell pathfinding.
- `references/ui-rendering.md`: UI, windows, GUI state, rendering and animation curves.
- `references/data.md`: Persistence, XML, data structures, extensions and supporting interfaces.
- `references/events-patching.md`: Targeting, events and patch extension contracts.
- `references/diagnostics.md`: Logging, caching, profiling, debugging and compile-time analyzers.
- `references/integration.md`: Dependency providers, project references, output and packaging, assembly identity, and stale artifacts.
- `references/lifecycle.md`: Initialization, patch ownership, background work, runtime verification, and troubleshooting.
