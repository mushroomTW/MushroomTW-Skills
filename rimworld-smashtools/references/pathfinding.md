# Search, Assignment, and Multi-Cell Pathfinding

Verify API signatures and prerequisites against the locally adopted version; see [Feature Index](features.md) for other categories.

## Core Algorithms Library (Algorithms)

- **Purpose**: Graph search, shortest path, and optimal assignment algorithms.
- **Representative Types and Methods**:
  - `SmashTools.Algorithms.BreadthFirstSearch<T>`: Generic breadth-first search and FloodFill.
    - `FloodFill(T start, Func<T, IEnumerable<T>> neighbors, Action<T> processor, Func<T, bool> canEnter = null)`
  - `SmashTools.Algorithms.Dijkstra<T>`: Shortest-path pathfinder based on priority queues, supporting custom neighbors, cost functions, and entry restrictions.
  - `SmashTools.Algorithms.KuhnMunkres`: Hungarian algorithm calculating optimal bipartite matching for an $N \times N$ cost matrix in $O(N^3)$ time.
- **Usage Example**:

  ```csharp
  var bfs = new BreadthFirstSearch<IntVec3>();
  bfs.FloodFill(rootCell, cell => cell.AdjacentCells8Way(), cell => Process(cell), cell => cell.Standable(map));
  ```

- **Source Locations**: `SmashTools/SmashTools/Algorithms/`

## SmashTools.PathFinder Parallel Multi-Cell Pathfinding (`SmashTools.PathFinder/`)

- **Purpose**: Burst parallel-accelerated pathfinder designed for large entities or pawns/vehicles occupying multiple cells (Hitbox > 1x1). Uses 2D Summed-Area Tables to query regional traversal costs in $O(1)$ time.
- **Representative Types and Methods**:
  - `SmashTools.PathFinder.PathFinder`: Main pathfinder implementing `IJobDispatcher`, `IDisposable`, `IPathGridSync`. Constructor requires `PathFinder.Settings`.
    - `Path FindPath(in PathRequest request)`: Computes and returns the path immediately on the main thread.
    - `PathReceipt RequestPath(in PathRequest request)`: Schedules a Burst Job for asynchronous pathfinding, returning a `PathReceipt` handle.
    - `NotifyWritingToGrid()`: Invalidates pathfinder snapshots when map traversal costs or obstacles change.
  - `SmashTools.PathFinder.SumAreaTable`: Summed-area table core supporting Cardinal (cross) and Diagonal layouts.
  - `SmashTools.PathFinder.PathRequest`, `EntityConfig`: Defines pathfinding start, goal, size dimensions, and rotation settings.
  - `SmashTools.PathFinder.ModifierGrid`, `PathGridMask`, `PathGridScalar`, `PathOffsetGrid`: Spatial masks and dynamic cost modifier grids.
  - `SmashTools.PathFinder.HeuristicGrid`, `NormalHeuristic`, `WeightedHeuristic`: Heuristic distance weight grids.
  - `SmashTools.PathFinder.TurnCost`, `TurnData`, `Rotation`: Orientation and turning cost configurations.
- **Invocation and Lifecycle Contracts**:
  - The main thread can initiate immediate synchronous pathfinding via `FindPath(in PathRequest request)`, or schedule an asynchronous Job returning a `PathReceipt` via `RequestPath(in PathRequest request)`.
  - **Ownership and Lifecycle Management**: The caller must maintain ownership of the `PathFinder` instance and input grid (`pathGrid`) throughout async execution; do not dispose prematurely before work completes.
  - **Receipt and Disposal**: `PathReceipt` implements `IPathPromise`. `IsCompleted` checks completion status, `GetPath()` waits for completion and copies the resulting path. `Cancel()` does not abort the Job; it waits for completion and calls `Dispose()`. Disposal must align with scheduler ownership: check the adopted version for whether the caller or scheduler recycles resources to avoid double-free after cancellation or double-returning pooled `PathData`.
- **Prerequisites and Constraints**:
  - All pathfinding requests must be initiated from the main thread (`All requests must be made from the main thread`).
  - Asynchronous scheduling relies on `JobDispatchManager` pumping completion during the main game loop.
  - Internal Burst jobs (`SumCardinalJob`, `SumDiagonalJob`, `Snapshot*Job`, `BurstUtils`) are internal scheduling details and must not be called manually.
- **Source Locations**: `SmashTools.PathFinder/PathFinding/`, `SmashTools.PathFinder/Algorithms/`, `SmashTools.PathFinder/Snapshot/`, `SmashTools.PathFinder/Utilities/`
