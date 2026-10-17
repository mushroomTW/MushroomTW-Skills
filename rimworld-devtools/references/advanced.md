# Smoke Tests, Test Plans, and Benchmarks

## Smoke Tests

`--pid <host> --smoke-test --exit` selects SmokeTestManager to check startup and subsequent scene logs, rather than assert mod behavior. Configure it through `Configs/SmokeTestConfig.xml`; warnings/errors fail by default.

`SmokeTestAttribute` is internal and unavailable directly to external test projects. Discovery scans each mod's loaded assemblies. Built-in `DefaultSmokeTests` resides in DevTools.dll, so select a host that loads that DLL and registers the smoke manager. A companion containing ordinary TestFixtures does not necessarily have a smoke manager.

## Test Plans

Use plans for different mod lists or separate processes. Ordinary fixtures can use the unit runner.

- Plan files live in the host's `TestPlans/**/*.xml`. A `TestPlan` contains `name` and `jobs`; job fields are `name`, `commandLineArgs`, `loadWithMods`, and `timeOut`. The CLI matches the XML name, not necessarily the filename.
- `--pid <host> --test-plan <name> --exit` runs the parent, and each job starts a child game process. `loadWithMods` is a complete list, not additions; include required game/DLC/dependency mods and the plan host.
- Back up ModsConfig.xml first. The runner writes each job's mod list and restores it only when the parent manager finishes normally. After a crash/forced stop, check and restore it manually.
- Children launch through `Environment.ProcessPath` with `--pid`, `-e`, and `-ColdBoot`. Parent savedatafolder, logfile, and bridge-port arguments are not automatically forwarded. Check child arguments/configuration before using custom folders to avoid modifying default player data.
- `timeOut` is compared with `Time.realtimeSinceStartup`, in seconds. The default constant is 600000 despite a comment saying ten minutes. Set an explicit value in seconds and check the local implementation instead of relying on that comment.
- The parent judges results by child exit codes. There is no `Test plan finished. Result:` line. A child's unit completion line may appear in shared Test.log before the plan finishes; wait for parent completion/exit and all job results, with an external deadline.
- Check for leftover child processes and restored mod lists. Record parent/child results and their logs. Unknown names or zero jobs do not count as success.

## Benchmarks

Use `DevTools.Benchmarking`. Mark a class with `[BenchmarkClass]` and static measurement methods with `[Benchmark]`. Run them through the developer DevTools > Benchmark menu.

- Methods take no parameters or one `ref T` context parameter, where T is an ordinary struct. A `[Context]` static field/readable property can supply the context.
- `[Prepare]`/`[OnFinish]` methods are also static and run before/after the whole measurement group, not each sample. OnFinish is not protected by finally; provide another recovery path for modified game state.
- `[BenchmarkClass(RunAsync = false)]` disables background execution; RunAsync defaults to true. Use the main thread when calling game/Unity APIs and restrict required scenes through AllowedGameStates.
- `[Measurement(Benchmark.Measurement.Milliseconds)]` and related values control display units; `[Table]` selects statistics. The default table shows mean, median, standard deviation, and samples; without table statistics, output goes to the game log. Graph display is not implemented.
- Return actual computation results to reduce dead-code elimination. Use real input data to avoid constant folding. Compare equal workloads, states, and build modes without an attached debugger; record the environment and statistics.
- Operations close to the cost of a single method call are not measured reliably; display units do not imply measurement precision.

Report sample counts, units, statistics, and comparison results.
