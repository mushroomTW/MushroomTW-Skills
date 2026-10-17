---
name: rimworld-smashtools
description: Integrate and use SmashTools to develop RimWorld mods, adopt built-in features, or troubleshoot compilation, packaging, and loading issues. Use when SmashTools is explicitly selected or already used by the project.
---

# RimWorld SmashTools Integration and Usage

SmashTools provides utility classes as well as mod initialization, event, and patching infrastructure. Integration must address compile-time references, game loading, and runtime initialization simultaneously; having a DLL available for compilation does not mean it is ready at runtime.

Features cover native collections, object pooling, threading and job dispatching, search and multi-cell pathfinding, targeting, game events, UI and windows, rendering, persistence and XML, animation curves, caching and profiling, logging, and compile-time analyzers. See the feature guide for component distribution, prerequisites, and usage of each feature.

## Workflow

Reuse the project's existing SmashTools sources, build, and release configuration. Read the relevant reference based on the task:

- Find built-in features, select APIs, or write consumer code: start with [Feature Index](references/features.md), read only the required category, and check local signatures, callers, and constraints.
- Initial integration, dependency updates, or release adjustments: [references/integration.md](references/integration.md). Covers provider selection, project references, output, and assembly identity.
- Hook into startup workflows, use patchers, or troubleshoot game loading issues: [references/lifecycle.md](references/lifecycle.md). Covers initialization ownership, timing, verification, and troubleshooting; read before running in-game verification.

Use the source code or DLL metadata of the locally adopted version for routine API and contract checks. Fetch upstream `SmashPhil/SmashTools` only during initial adoption when artifacts are missing locally, when the user requests an update, or when local sources are insufficient to resolve a specific issue, and retain the source for subsequent use. Routine integration does not require network access to check documentation or latest versions.

For projects with an existing integration, implement the required features directly; enter the integration workflow only when dependencies, initialization, or release configurations are missing.

Rebuild according to the project release configuration and inspect the final release package; restart the game after modifying loaded assemblies before verifying integrated features.

Deliver the adopted source, runtime provider, modified locations, and verification results. List build, game loading, feature, and coexistence verification separately; mark unexecuted items as unverified.
