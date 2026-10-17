# UI, Windows, Rendering, and Animation

Verify API signatures and prerequisites against the locally adopted version; see [Feature Index](features.md) for other categories.

## UI Components, Multi-Column Layouts, and Window System (UI & Windows)

- **Purpose**: Enhances vanilla UI layout capabilities, providing advanced window base classes, multi-column layouts, and common dialogs.
- **Representative Types**:
  - Window Base Classes:
    - `SmashTools.SingleWindow`: Ensures only a single instance of that type exists in the `WindowStack`.
    - `SmashTools.SubWindow`: Floating sub-window attached to a parent window.
    - `SmashTools.MovingWindow`: Window supporting dragging, moving, and boundary clamping.
  - Common Dialogs: `Dialog_FilePicker` (in-game file/folder picker), `Dialog_ActionList`, `Dialog_ItemDropdown`, `Dialog_RadioButtonMenu`, `Dialog_ToggleMenu`, `EditWindow_TweakFields` (real-time tweaking for fields marked with `[TweakField]`), `Dialog_Graph` / `Dialog_GraphEditor` (curve viewer and editor).
  - Layout and Widgets:
    - `SmashTools.Listing_SplitColumns`: List drawer supporting automatic multi-column wrapping and custom spacing.
    - `SmashTools.WidgetRowButBetter`: Advanced widget row supporting wrapping and multiple growth directions (`UIDirection`).
    - `SmashTools.UIElements`: Provides headers with background highlights, custom textured checkboxes, hex color conversions, and slider drag controls.
    - `SmashTools.UndoManager`: State manager supporting undo/redo operations.
- **Source Locations**: `SmashTools/SmashTools/UI/`

## GUI State and RAII Scopes (Scopes)

- **Purpose**: Uses `using` blocks to guarantee safe restoration of GUI states, matrices, and clipping areas even when exceptions occur.
- **Representative Types and Methods**:
  - `SmashTools.GUIState`: `using (GUIState.DisableIf(bool disable))` conditionally disables GUI and applies greyscale tinting.
  - `SmashTools.GUIClipScope`: `using (new GUIClipScope(Rect rect))` regional clipping.
  - `SmashTools.GUIMatrixScope`: `using (new GUIMatrixScope(Matrix4x4 matrix))` temporarily saves and restores GUI transformation matrix.
  - `SmashTools.WidgetGroupScope`: `using (new WidgetGroupScope(Rect rect))` grouped drawing.
  - `SmashTools.ScrollViewScope`: `using (new ScrollViewScope(Rect outRect, ref Vector2 scrollPosition, Rect viewRect))` scroll view.
  - `SmashTools.RandStateBlock`: `using (new RandStateBlock(int seed))` random state push/pop guard.
- **Source Locations**: `SmashTools/SmashTools/Utility/Scopes/`, `SmashTools/SmashTools/UI/ScrollViewScope.cs`

## Off-Screen Texture Drawing and Overlay Rendering (Rendering)

- **Purpose**: Supports batch drawing objects, pawns, or meshes to RenderTextures, as well as drawing pawn overlays in containers/buildings.
- **Representative Types**:
  - `SmashTools.Rendering.RenderTextureDrawer`: Off-screen texture drawer providing `Init(texture)`, `Add(renderData)`, `Draw(rect)`; executes only during `Repaint` events, supporting centering and scaling.
  - `SmashTools.Rendering.RenderTextureBuffered`, `RenderTextureIdler`: High-performance texture management with double-buffering and idle sleep (skips repainting when unchanged).
  - `SmashTools.PawnOverlayRenderer`, `SmashTools.IThingHolderPawnOverlayer`: Pawn orientation and custom overlay rendering control inside containers (`ThingHolder`).
  - `SmashTools.Rendering.IParallelRenderer`, `ParallelRenderer.SetDirty()`: Interface for marking parallel rendering dirty state.
- **Source Locations**: `SmashTools/SmashTools/Rendering/`

## Animation Timelines and Curve Simulation (Animating & Graphing)

- **Purpose**: Frame-by-frame animation driving, event triggers, playback speed adjustment, and keyframe curve simulation.
- **Representative Types**:
  - `SmashTools.AnimationDriver`: Defines animation labels, durations, update callbacks, and draw position/rotation calculations.
  - `SmashTools.AnimationSimulator`: In-game simulator supporting pause, step, and variable speed (`PlaybackSpeed`).
  - `SmashTools.AnimatorObject`: Animation target bound to entity field curves.
  - `SmashTools.LinearCurve`, `BezierCurve`, `LagrangeCurve`, `StaircaseCurve`: Mathematical data structures for Bezier, Lagrange, and staircase curves.
- **Source Locations**: `SmashTools/SmashTools/Animating/`, `SmashTools/SmashTools/DataTypes/Graphing/`

## SmashTools.Rendering Native Window Hosting (`SmashTools.Rendering/`)

- **Purpose**: Renders RimWorld `Verse.Window` contents into standalone native GLFW / Vulkan windows for multi-window displays or external debug panels.
- **Representative Types and Methods**:
  - `SmashTools.Rendering.WindowFrame`: Window hosting frame implementing `IDisposable`.
    - `public WindowFrame([NotNull] Window window, in WindowContext context)`
    - `public void Run()`: Creates and displays a standalone native window.
  - `SmashTools.Rendering.WindowContext`: Window appearance configuration struct (`title`, `size`, `color`, `drawTitleBar`).
- **Usage Example**:

  ```csharp
  var context = new WindowContext
  {
      title = "Standalone Tool Window",
      size = new Brutal.Numerics.int2(800, 600),
      drawTitleBar = true
  };
  using WindowFrame frame = new WindowFrame(myVerseWindow, in context);
  frame.Run();
  ```

- **Prerequisites and Constraints**:
  - Must be created and run on the main thread (`UnityData.IsInMainThread`).
  - Runtime dependency on Waylith graphics environment (`EngineApplication.Instance != null && !app.Headless`); unavailable in pure vanilla Unity environments without Waylith.
  - Internal classes (`Backend`, `BehaviourGui`, `Host`, `WindowGui`, `WindowInput`, `WindowStackContext`) handle Vulkan/ImGui and input forwarding, and are internal implementation details.
- **Source Locations**: `SmashTools.Rendering/`
