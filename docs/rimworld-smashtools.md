# RimWorld SmashTools — Architecture & Feature Integration

**English** | [繁體中文](rimworld-smashtools.zh.md)

> This document lives in `docs/`. The skill itself is at [`rimworld-smashtools/SKILL.md`](../rimworld-smashtools/SKILL.md).

A comprehensive architectural and integration guide for [SmashTools](https://github.com/SmashPhil/SmashTools), a high-performance foundational C# framework for RimWorld mod development. This skill assists AI agents and developers in adopting existing SmashTools subsystems, structuring mod architecture, and resolving complex lifecycle, loading, and packaging challenges.

SmashTools provides battle-tested infrastructure for complex mods — including multi-cell pathfinding, thread-safe object pooling, custom UI rendering pipelines, and XML persistence. This skill eliminates redundant reinvention by mapping mod requirements directly to SmashTools' optimized native APIs.

## When It Applies

Applies when designing, implementing, optimizing, or packaging RimWorld mods that integrate SmashTools.

The skill triggers automatically when a project references or configures SmashTools, or can be invoked directly:

```text
Use $rimworld-smashtools to integrate SmashTools into this RimWorld mod.
```

For projects with an existing integration:

```text
Use $rimworld-smashtools to identify relevant features, then implement this mod's UI and data persistence logic.
```

## Architectural Modules

SmashTools is organized into specialized subsystems covered by dedicated reference guides:

| Subsystem | Reference | Scope & Core Capabilities |
| --- | --- | --- |
| **Core Infrastructure** | [`core.md`](../rimworld-smashtools/references/core.md) | High-performance native collections, 2D/3D geometry calculations, thread-safe object pooling, background job dispatchers, and dynamic delegates. |
| **Multi-Cell Pathfinding** | [`pathfinding.md`](../rimworld-smashtools/references/pathfinding.md) | Navigation algorithms for multi-tile entities, spatial search heuristics, and Hungarian optimal assignment solvers. |
| **UI & Custom Rendering** | [`ui-rendering.md`](../rimworld-smashtools/references/ui-rendering.md) | Window management frameworks, GUI state caching, custom mesh and shader rendering, and animation curve evaluation. |
| **Data & XML Persistence** | [`data.md`](../rimworld-smashtools/references/data.md) | Deep XML serialization, structured save-game persistence, collection extensions, and serialization contracts. |
| **Events & Patching** | [`events-patching.md`](../rimworld-smashtools/references/events-patching.md) | Custom entity targeting handlers, high-throughput event bus systems, and patch extension contracts. |
| **Diagnostics & Profiling** | [`diagnostics.md`](../rimworld-smashtools/references/diagnostics.md) | High-throughput logging, LRU memory caching, execution profiling, and compile-time code analyzers. |
| **Build & Packaging** | [`integration.md`](../rimworld-smashtools/references/integration.md) | Multi-version compilation matrices, dependency providers, assembly identity validation, release packaging, and artifact hygiene. |
| **Mod Lifecycle** | [`lifecycle.md`](../rimworld-smashtools/references/lifecycle.md) | Safe execution sequencing across static constructors, `Mod` instantiation, and game start hooks; patch ownership isolation, background thread shutdown, and startup debugging. |
| **Feature Index** | [`features.md`](../rimworld-smashtools/references/features.md) | High-level index mapping functional requirements to specific reference documents. |

## Key Integration Guidelines

- **Local-First Resolution**: Prioritizes local SmashTools source trees and compiled DLLs over remote downloads. Routine code navigation and API checks run completely offline.
- **Strict Lifecycle Sequencing**: Ensures code respects RimWorld's loading boundaries (e.g., preventing premature access to `DefDatabase` during early static constructors).
- **Graceful Thread Teardown**: Guarantees background workers, thread pools, and job dispatchers cleanly terminate on map transitions or game shutdown to avoid memory leaks.
- **Assembly Identity Hygiene**: Enforces clean separation between mod assemblies and shared SmashTools dependencies to prevent multiple-definition type clashes.

## Prerequisites

- **RimWorld Engine**: RimWorld 1.6+ runtime environment.
- **Tooling**: .NET SDK and RimWorld game reference assemblies.
- **SmashTools Assemblies**: Target version of `SmashTools.dll` and its supporting libraries.

## Install

From the repository root, use the `skills` CLI to discover supported agent hosts and install this skill:

```bash
npx skills add . --skill rimworld-smashtools
```

Add `--global` for personal user scope; omitting it installs at project scope. For manual installation, copy `rimworld-smashtools/` directly into your agent host's configured skills directory.

> [!NOTE]
> The initial `npx` invocation may download the CLI. Reload or restart your agent host if it only discovers skills during session startup.
