# Coverage report mapping

> Compiled from the official `analyzing-source-code/test-coverage/*` pages. SonarQube does not produce coverage; it only **imports** the report your native tool produced before the scan. Confirm formats and property names against your current SonarQube version — this table is the common mapping (option B).

## Order of operations (mandatory)

1. Run the coverage tool as part of the build pipeline, **before** the scanner
2. Adjust the tool's output so paths and format match what the scanner expects
3. Set the matching `sonar.*` property in `sonar-project.properties` or as a CLI argument so the scanner imports it

`test execution` (which tests ran) and `test coverage` (how much code is covered) are two different features with different parameters.

## Language mapping

| Language / ecosystem | Producing tool (example) | Report format | SonarQube property (confirm against the docs) | Notes |
|---|---|---|---|---|
| Java / Kotlin | JaCoCo | `jacoco.xml` | `sonar.coverage.jacoco.xmlReportPaths` | the older `sonar.jacoco.reportPaths` is deprecated; run `mvn verify` first to produce it |
| JavaScript / TypeScript | Jest, Vitest, nyc, c8 | `lcov.info` | `sonar.javascript.lcov.reportPaths` | Node.js and encoding requirements are in `languages.md` |
| C# | OpenCover / Coverlet (opencover format) | `*.opencover.xml` | `sonar.cs.opencover.reportsPaths` | Coverlet must emit the **opencover** format; requires SonarScanner for .NET, since the CLI cannot analyze C# |
| C# | VS Coverage, `dotnet-coverage` | `*.coveragexml` | `sonar.cs.vscoveragexml.reportsPaths` | same scanner requirement |
| C# | dotCover | `*.html` / `*.xml` | `sonar.cs.dotcover.reportsPaths` | same scanner requirement |
| C# | any Cobertura producer | Cobertura XML | `sonar.cs.cobertura.reportsPaths` | same scanner requirement |
| VB.NET | same tools as C# | same formats | `sonar.vbnet.opencover.reportsPaths` / `sonar.vbnet.vscoveragexml.reportsPaths` / `sonar.vbnet.dotcover.reportsPaths` / `sonar.vbnet.cobertura.reportsPaths` | same scanner requirement |
| Python | coverage.py | `coverage.xml` | `sonar.python.coverage.reportPaths` | run `coverage xml` to produce the Cobertura-compatible format |
| Go | `go test -coverprofile` | `coverage.out` | `sonar.go.coverage.reportPaths` |  |
| PHP | PHPUnit, phpcov | `clover.xml` | `sonar.php.coverage.reportPaths` |  |
| Flex | any Cobertura producer | Cobertura XML | `sonar.flex.cobertura.reportPaths` |  |
| Ruby | SimpleCov 0.20+ JSON formatter | `coverage/coverage.json` | `sonar.ruby.coverage.reportPaths` | only with the community Ruby plugin (26.11+) |
| Scala | Scoverage | `scoverage.xml` | `sonar.scala.coverage.reportPaths` | only with the community Scala plugin (26.11+) |
| Generic | any tool, converted | `generic` XML | `sonar.coverageReportPaths` | for unsupported tools; convert to the generic format first (see `generic-test-data.md`) |

> Property names are case-sensitive; in PowerShell, quote any value containing a `.`.

## Pre-scan checklist

```powershell
Test-Path coverage/lcov.info          # exists and is non-empty
Test-Path target/site/jacoco/jacoco.xml
(Get-Item coverage/lcov.info).Length -gt 0
# paths inside the report must line up with sonar.projectBaseDir, or the analysis will not match them
# a non-empty file can still be an empty report: check it lists real content
Get-ChildItem -Recurse -Filter coverage.opencover.xml | Select-String -Pattern '<Module ' -List   # OpenCover/Coverlet: at least one module
Select-String -Path coverage/lcov.info -Pattern '^SF:' -List             # LCOV: at least one source file
```

- Report empty or missing → follow `troubleshooting.md#Coverage report path missing`; **never** create an empty placeholder file
- Report present but with no modules/files (e.g. .NET built without PDBs) → treat as missing; after the scan, a `coverage` measure of `0.0` with passing tests usually means this
- Project with no coverage tool → state "no coverage" explicitly and scan without the property
- Multi-module / monorepo → each module's `sonar.*` must point at that module's own report

## Official deep reading

- Overview: `test-coverage/overview.md`
- Parameters: `test-coverage/test-coverage-parameters.md` / `test-execution-parameters.md`
- Per language: `java-test-coverage.md`, `javascript-typescript-test-coverage.md`, `dotnet-test-coverage.md`, `python-test-coverage.md`, `php-test-coverage.md`, `generic-test-data.md`
- Analysis requirements beyond coverage (binaries, runtimes, versions): `reference/languages.md`
- Canonical entry point: https://docs.sonarsource.com/sonarqube-community-build/analyzing-source-code/test-coverage
