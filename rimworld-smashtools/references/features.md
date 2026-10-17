# SmashTools Feature Index

Read the relevant category based on your task without loading all documents at once.

| Purpose | Reference Document |
| --- | --- |
| Native collections and geometry, main thread dispatch, background jobs, object pooling, dynamic delegates, and scope restoration | [Collections, Threading, and Core Utilities](core.md) |
| BFS, Dijkstra, Hungarian algorithm, Burst multi-cell pathfinding, and grid costs | [Search, Assignment, and Multi-Cell Pathfinding](pathfinding.md) |
| UI components, GUI scopes, off-screen rendering, animation curves, and native windows | [UI, Windows, Rendering, and Animation](ui-rendering.md) |
| Scribe, XML, game data structures, extension methods, enums, and supporting interfaces | [Persistence, XML, and Data Utilities](data.md) |
| Map/world targeters, event broadcasting and suppression, phased and conditional patching | [Targeting, Events, and Patch Contracts](events-patching.md) |
| Logging, component caching, profiling, tweak and debug entry points, Roslyn analyzers | [Logging, Performance, and Development Tools](diagnostics.md) |
| Dependency sources, project references, and packaging | [Build and Release Integration](integration.md) |
| Initialization, internal mechanics, runtime verification, and troubleshooting | [Lifecycle](lifecycle.md) |

## Module and Assembly Architecture

SmashTools consists of 5 concrete functional projects:

- `CoreLib` (`Core/`): Low-level high-performance utility library independent of RimWorld game logic, covering unmanaged collections, thread scheduling, object pooling, dynamic delegates, logging, and geometric operations.
- `SmashTools` (`SmashTools/SmashTools/`): Main RimWorld extension SDK, covering targeting, events, custom UI/windows, off-screen rendering, Scribe extensions, animations, logging, patch contracts, and component caching.
- `SmashTools.PathFinder` (`SmashTools.PathFinder/`): Parallel multi-cell pathfinding engine based on Unity Burst and Job systems.
- `SmashTools.Rendering` (`SmashTools.Rendering/`): Rendering bridge module that hosts game windows into standalone native windows via Waylith / Vulkan / GLFW.
- `SmashTools.Analyzer` (`SmashTools.Analyzer/`): Compile-time Roslyn code analyzer and warning suppressor.
