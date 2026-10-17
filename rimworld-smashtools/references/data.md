# Persistence, XML, and Data Utilities

Verify API signatures and prerequisites against the locally adopted version; see [Feature Index](features.md) for other categories.

## Scribe Serialization Extensions and Delayed XML Parsing (Saving & Xml)

- **Purpose**: Resolves the issue where vanilla RimWorld Scribe cannot directly handle multi-dimensional arrays, boxed polymorphic objects, or nested dictionaries, and supports resolving delayed Def cross-references loaded in early phases.
- **Representative Types and Methods**:
  - `SmashTools.Scribe_NestedCollections`:
    - `Look<K, K2, V>(ref Dictionary<K, Dictionary<K2, V>> dict, string label, LookMode keyMode, LookMode innerKeyMode, LookMode innerValueMode)`
  - `SmashTools.Scribe_Array`: Serialization for 1D and 2D arrays (`T[]`, `T[,]`).
  - `SmashTools.Scribe_ObjectValue`: Serialization for polymorphic and boxed types (`ref object obj`), automatically recording `InnerType` and `SavingType`.
  - `SmashTools.Scribe_ObjectCollection`: Polymorphic serialization for object lists.
  - `SmashTools.Xml.DelayedCrossRefResolver`: Registers Def cross-references specifically for XML loaded before the Def loading stage (e.g., animation curve configurations), resolved collectively by the startup pipeline once `DefDatabase` is ready.
  - `SmashTools.Xml.XmlExporter`: Serializes entities or Defs back into XML nodes.
- **Source Locations**: `SmashTools/SmashTools/Saving/`, `SmashTools/SmashTools/Xml/`

## Common Data Structures and Collections (Collections & DataTypes)

- **Purpose**: Supplements specific needs not covered by RimWorld and .NET native data structures.
- **Representative Types**:
  - `SmashTools.RingBuffer<T>`: Fixed-capacity ring buffer.
  - `SmashTools.DropOutStack<T>`: Fixed-size stack that automatically drops items from the bottom when capacity is exceeded.
  - `SmashTools.RotatingList<T>`, `SelfOrderingList<T>`, `FlatQueue<T>`, `ConcurrentSet<T>`, `SimpleDictionary<TKey, TValue>`, `ThingDefCountList`.
  - `SmashTools.Rot8`: 8-way rotation struct (North, NorthEast, East, etc.), providing conversions between angles and vectors.
  - `SmashTools.RimWorldTime`: Precise conversion between ticks and game hours, days, quadrums, and years.
  - `SmashTools.DetachedMapComponent`: Self-managed component base class independent of the vanilla map components list.
- **Source Locations**: `SmashTools/SmashTools/Collections/`, `SmashTools/SmashTools/DataTypes/`

## Extension Method Libraries (Extensions)

- **Purpose**: Encapsulates common null-checks, collection operations, and convenient RimWorld API calls.
- **Representative Types**:
  - Game Extensions (`SmashTools`): `Ext_Pawn`, `Ext_Map`, `Ext_CellRect`, `Ext_Color`, `Ext_Comp`, `Ext_PathFinding`, `Ext_Rect`, `Ext_Texture`, `Ext_Mods`, `Ext_World`.
  - System Extensions (`SmashTools`): `Ext_Array`, `Ext_IEnumerable`, `Ext_IList`, `Ext_IDictionary`, `Ext_String`, `Ext_IntVec`, `Ext_Math`, `Ext_Numeric`, `Ext_Type`, `CellRectOverlap`.
  - Project Extensions (`SmashTools`): `DefIndexManager` (Def integer index cache), `Ext_Animation`, `Ext_EventManager`, `Ext_Profiler`.
- **Source Locations**: `SmashTools/SmashTools/Utility/Extensions/`

## Enum Types, Extension Interfaces, and External Annotations (Enums, Interfaces & ExternalAnnotations)

- **Enum Types (`SmashTools/SmashTools/Enums/`)**:
  - `SmashTools.MathOp`: Basic arithmetic operators (Add, Subtract, Multiply, Divide).
  - `SmashTools.UISettingsType`: UI tweak setting types (Checkbox, Slider, NumericBox, Text, Dropdown, etc.), used by `[TweakField]` to specify control rendering form.
- **Extension Interfaces (`SmashTools/SmashTools/Interfaces/`)**:
  - `SmashTools.IAnimationTarget`: Interface for animation-driven targets.
  - `SmashTools.IDefaultValue`: Object interface providing default values.
  - `SmashTools.IDefIndex`: Interface providing Def integer index caching.
  - `SmashTools.IInspectable`: Object interface for dynamic inspection via `Dialog_InspectWindow`.
  - `SmashTools.INestedType`: Helper interface for reflection nested type resolution.
  - `SmashTools.IThingHolderPawnOverlayer`: Interface for pawn orientation and overlay display within a container.
  - `SmashTools.ITransformable`: Entity interface exposing a `Transform` property.
  - `SmashTools.ITweakFields`: Object interface for tweaking fields via `EditWindow_TweakFields`.
- **External Annotations (`SmashTools/SmashTools/ExternalAnnotations/`)**:
  - `Assembly-CSharp.xml`: ReSharper / Rider external metadata annotations file for IDEs and static analysis tools to infer nullability and contracts of vanilla RimWorld assemblies; not involved in runtime compilation.
