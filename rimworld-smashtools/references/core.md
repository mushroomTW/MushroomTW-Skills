# Collections, Threading, and Core Utilities

Verify API signatures and prerequisites against the locally adopted version; see [Feature Index](features.md) for other categories.

## Native and Unmanaged Collections (Collections & Geometry)

- **Purpose**: Unmanaged memory collections and entity geometry designed for high-frequency algorithms, Burst Jobs, or zero-GC allocation scenarios.
- **Representative Types**:
  - `CoreLib.Collections.NativeArrayList<T>`: Dynamic array based on unmanaged memory.
  - `CoreLib.Collections.NativeBitArraySlim`: Compact unmanaged bit array.
  - `CoreLib.Collections.NativeFixedList<T>`, `NativeMinHeap<T>`: Fixed-capacity list and min-heap priority queue.
  - `CoreLib.Collections.ReadOnlyArray<T>`, `ReadOnlyList<T>`: Lightweight read-only wrappers.
  - `CoreLib.EntityRect`, `CoreLib.Octant`, `CoreLib.Orientation`: Entity rectangular geometry operations and 8-way orientation definitions.
- **Constraints and Ownership Contracts**: Not all containers require disposal. Managed read-only wrappers (such as `ReadOnlyArray<T>`, `ReadOnlyList<T>`) do not need manual release; native unmanaged collections (such as `NativeArrayList<T>`, `NativeBitArraySlim`, `NativeFixedList<T>`, `NativeMinHeap<T>`) allocate unmanaged memory and must follow Allocator ownership contracts, calling `Dispose()` or using temporary allocators at the end of their lifecycle.
- **Source Locations**: `Core/Collections/`, `Core/Entity/`, `Core/Extensions/`

## Threading, Main Thread Dispatch, and Job Management (Threading & Jobs)

- **Purpose**: Cross-thread scheduling helpers, main thread sync/async callbacks, background long-running tasks, and debouncing.
- **Representative Types and Methods**:
  - `CoreLib.Performance.UnityThread`:
    - `ExecuteOnMainThreadAndWait(Action action, int waitTimeout = 0)`: Block and wait for execution on the main thread.
    - `ExecuteOnMainThreadAsync(Action action)`: Asynchronously dispatch to the main thread queue.
    - `IsInMainThread`: Check whether the current thread is the Unity main thread.
  - `CoreLib.Performance.Debouncer`: `Debounce(Action action, int delayMs)` action debouncing.
  - `CoreLib.Performance.DedicatedThread`, `TaskManager`, `ThreadManager`: Dedicated background worker threads and task lifecycle management.
  - `CoreLib.Jobs.JobDispatchManager`, `IJobDispatcher`: Unity Job pumping manager.
- **Usage Example**:

  ```csharp
  // Switch from background thread back to main thread to call game APIs
  UnityThread.ExecuteOnMainThreadAndWait(() =>
  {
      Find.LetterStack.ReceiveLetter("Title", "Message", LetterDefOf.NeutralEvent);
  });
  ```

- **Constraints**: Most core Unity and RimWorld states (maps, UI, DefDatabase) cannot be accessed directly from background threads.
- **Source Locations**: `Core/Performance/Multithreading/`, `Core/Performance/UnityThread.cs`, `Core/Jobs/`

## Pooling and Caching Infrastructure (Caching & Pooling)

- **Purpose**: Reduce GC allocation overhead caused by frequent creation of short-lived objects.
- **Representative Types**:
  - `CoreLib.Performance.ObjectPool<T>`: Generic instance object pool supporting dynamic resizing (`Resizable`). When a returned object (`Return`) implements `IPoolable`, automatically calls `Reset()` and flags `InPool = true`; when retrieved, flags `InPool = false`.
  - `CoreLib.Performance.AsyncPool<T>`: Static thread-safe object pool (`public static class AsyncPool<T> where T : class, new()`), stored internally with `ConcurrentBag<T>`; does **not** support `IPoolable` automatic reset, so callers must clean up object state before returning. Use `Get()` and `Return(item)` in pairs, or manage returns via `AsyncPool<T>.Scope(out item)`.
  - `CoreLib.Performance.MapObjectPool<T>`: Manages object pools keyed by 2D map dimensions `(width, height)` with internal reference counting (`RefCount`). Acquire or create pool instances via `Get(int width, int height, int poolSize, Func<T> factory = null)`, and decrement reference count via `Release(int width, int height)`; automatically clears the pool for that dimension when the count drops to zero. Callers must invoke `Get` and `Release` in pairs.
- **Source Locations**: `Core/Performance/Caching/`

## Dynamic Invocation, Expression Evaluation, and RAII Guards (Invocation & Utils)

- **Purpose**: High-efficiency runtime reflection invocation, string expression parsing, and automatic scope restoration.
- **Representative Types**:
  - `CoreLib.Performance.MethodBuilder`: Dynamic IL method generator for accelerated reflection delegate invocation.
  - `CoreLib.ShuntingYard`: Shunting-yard algorithm implementation supporting mathematical expression string evaluation.
  - `CoreLib.ClearOnDispose<T>`, `DestroyOnDispose`, `ScopedRollback<T>`: RAII-style structs that automatically clear collections or restore variable values when exiting a `using` scope.
- **Source Locations**: `Core/Performance/Invocation/`, `Core/Utils/`
