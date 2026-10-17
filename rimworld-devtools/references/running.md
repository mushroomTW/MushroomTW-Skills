# Execution, Results, and Troubleshooting

## Before Launch

Save game progress and confirm the host packageId and loaded test DLLs. Reuse the project's existing launcher.

Rebuild, stop the previous test process, and restart. Preserve needed results and distinguish the current log using a fresh directory, timestamps, or archiving. A previous run's completion line must not satisfy the current wait.

## UI and CLI

UI: enable developer mode, open the DevTools icon in the debug-windows row, select the host mod/tool, and open Test Explorer. Run all/selected tests, rerun failures, or use Open Log. The runner switches scenes and returns to the main menu afterward.

| Argument | Meaning |
| --- | --- |
| `--pid <packageId>` | Matches the host's `PackageIdPlayerFacing`, case-insensitively; missing/incorrect IDs do not run the intended tests |
| `--test` / `-t` | Unit test manager |
| `--where <expr>` / `-w <expr>` | Test filter; `--filter` / `-f` are not supported |
| `--exit` / `-e` | Exit after normal completion; the manager returns 0/1 depending on whether any fixture failed |
| `--smoke-test` / `-s` | Smoke Test; see host restrictions in advanced.md |
| `--test-plan <name>` / `-p <name>` | Child-process test plan; read advanced.md first |
| `--test-list <file>` | One function.FullName per line, not fixture names |

PowerShell launch example; replace the executable path and packageId:

```powershell
& 'C:\Games\RimWorld\RimWorld.exe' --pid 'example.my-mod.tests' --test --where 'class == ThingStateTests' --exit
```

When using a launcher, pass these arguments through it.

`-NoWindow` enables hide-window compatibility handling and exit. The `-Headless` parser sets headless to false; the flag does not establish headless support.

## Filter Syntax

- `key op value`; keys include `class`, `method`, `namespace`, `type`, `category`, `status`, and metadata keys.
- Operators: `==`, `!=`, `=~`, `!~`. `=~` means substring matching, not regex.
- Join with `&&`/`||` or `and`/`or`. Evaluation is left to right, without parentheses or normal operator precedence.
- Single `|`/`&` tokens are discarded and can cause parsing errors. Quote the entire expression for the shell; do not quote individual values inside it because the parser retains those quotes.

Example: `--where 'namespace =~ MyMod.Tests && type == MainMenu'`. If filtering across assemblies raises an `IComparable` sorting exception, restrict execution to a single test assembly.

## Result Files and Configuration

Results go to **`Test.log`**; `Player.log` contains game and discovery errors. The default folder is `Application.persistentDataPath`; do not assume `-savedatafolder` changes it. Set a writable folder in the host root's `Configs/UnitTestConfig.xml` and confirm where the file appears.

```xml
<TestConfig>
  <log>
    <folder>C:/RimWorld-TestRuns/current</folder>
    <verboseLogging>true</verboseLogging>
    <report>DevTools.Testing.MarkdownReport</report>
  </log>
  <failOnWarnings>true</failOnWarnings>
  <failOnErrors>true</failOnErrors>
  <randSeed>12345</randSeed>
</TestConfig>
```

Replace folder with the actual output directory, create it, and ensure the game can write to it. Merge settings into existing configuration.

- `verboseLogging=true` by default logs Passed/Skipped and other statuses. When disabled, missing passing lines do not mean zero passes.
- `maxFileSize` defaults to 10 MiB; further messages are dropped. The logger also drops messages when its file does not exist; custom writers must account for this.
- The first TextLogWriter owner creates/truncates the log; other instances may append. Avoid sharing output locations between unrelated runs.
- The unit test manager can generate `test-report.md` through `MarkdownReport`. Use `ILogWriter` for custom output and `ITestReport` for a custom report receiving the result tree.

## Completion and Counts

The runner writes `Tests finished in ... ms with ...` statistics. With **`--exit`**, the unit/smoke manager also writes:

```text
Test runner finished. Result: Passed
```

Failures use `Failed`. Without `--exit`, Test Explorer opens and this manager completion line is absent. Use the UI, current runner statistics, `OnTestRunnerStateChange(false)`, or a generated report. Test Plan has no `Test plan finished. Result:` line; check parent-process completion and all job results.

Cross-check completion evidence, process status, and expected cases. Exit 0 can occur without executing the intended tests; setup/scene failures can leave incomplete statistics. Report cases excluded by missing prerequisites or disabling separately.

In `Test.log`, fixture lines start with `[Status]`; case lines start with `--` followed by TAB and `[Status]`. A failure appears at both fixture and case levels, so do not count all `[Failed]` occurrences. TestGenerator creates one TestFunction per argument set, producing separate parameterized case lines. Compare counts against discovery and reports, not method declarations.

Locate case lines and failure context with PowerShell:

```powershell
Select-String -LiteralPath 'C:\RimWorld-TestRuns\current\Test.log' -Pattern '^--\t\[(Passed|Failed|Skipped|Canceled|NotRun|Pending)\]'
Select-String -LiteralPath 'C:\RimWorld-TestRuns\current\Test.log' -Pattern '\[Failed\]' -Context 0,8
```

Set a deadline when waiting for completion. On timeout, inspect process status and Player.log and report an interrupted run.

## Troubleshooting

| Symptom | Check first |
| --- | --- |
| Game starts normally but tests do not run | packageId, active host mod, assembly paths, registered manager |
| Fixture missing | Static/abstract class, public constructor count, Disabled/mod gates, parameter sources |
| No Test.log | Initialization/CLI errors in Player.log, writable folder, zero fixtures, assembly type-loading errors |
| Completion never arrives | Stale/wrong log, missing exit flag, stalled test, constructor/scene exception, log size limit, nonexistent completion marker |
| Unexpected warning/error failure | Read full messages in Player.log; allow only expected messages with narrow patterns |
| Only the second run fails | Shared map, fixture fields, static fields, settings, defs, speed, or patches not restored |
