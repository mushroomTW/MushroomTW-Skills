# Build and Release Integration

## Identify the Provider

First inspect project files, shared build properties, About.xml, LoadFolders.xml, and release scripts to verify the game version, existing SmashTools source/DLL, reference paths, and actual release locations. The completion criterion is the ability to pinpoint "which copy is used for compilation, which copy is loaded by the game, and who provides it."

| Approach | Build and Release Configuration |
| --- | --- |
| Provided by an existing dependency mod | Reference compatible assemblies from that provider and disable auto-copy; declare its actual packageId and load order in About.xml. Do not bundle another copy of SmashTools into the release package |
| Bundled with the target mod | Pin the source commit or binary source, produce release assemblies via project reference or controlled copying, and ensure the target mod's active load folder includes it |

`loadAfter` alone does not enforce installing a dependency. The provider's packageId is taken from its About.xml; the SmashTools assembly name is not the packageId of a standalone mod. When introducing a required prerequisite mod for players, or switching to merged assemblies, renaming, or maintaining a source fork, confirm the deployment choice with the user first.

## Project References

Framework, compiler, game, and Harmony references should follow the project file of the adopted source. Consumers using only DLLs do not need to replicate all upstream compiler options or development dependencies.

File references can provide paths using project properties, for example:

```xml
<Reference Include="SmashTools">
  <HintPath>$(SmashToolsAssemblyPath)</HintPath>
  <Private>false</Private>
</Reference>
```

`SmashToolsAssemblyPath` must be provided by the target project's build configuration; it is not a built-in SmashTools property. This example applies when a runtime provider already exists, or when a release script copies the DLL separately. `Private=false` only disables automatic reference copying; it does not provide the assembly to the game.

When using ProjectReference, inspect the referenced project's `OutDir`/`OutputPath` and imported shared props. Cross-repository builds may still write to the upstream mod directory; override output or explicitly copy artifacts according to existing build conventions when necessary. A clean checkout should be reproducible via fixed acquisition and build workflows, without relying on DLLs manually left in Assemblies.

Keep game, Unity, and externally provided Harmony assemblies as reference-only. Whether build support packages and analyzers need distribution depends on their actual runtime dependencies; do not indiscriminately mirror the entire upstream output folder.

## Loading and Updates

Check LoadFolders.xml for version/condition branching, shared Assemblies, version-specific directories, and release staging folders. Base verification on the files the game will actually load, rather than build outputs alone.

- Compare DLL paths, assembly names, versions, and sources; identical version strings may correspond to different commits—compare hashes when necessary.
- Remove old artifacts managed by this integration when updating. Excluding a file in a new build does not automatically delete leftover files in staging or archive sources.
- Renaming a file does not change assembly identity. When encountering multiple copies of SmashTools, inspect loading sources and binding results first before deciding whether types are shared, conflicting, or isolated; do not infer compatibility from filenames alone.
- Retain the full license and copyright notice of the adopted version when distributing its DLL, source, or substantial rewrites.

Upon completion, the final release package should contain only assemblies and licenses required by the deployment approach, with an explicit provider for every runtime dependency.
