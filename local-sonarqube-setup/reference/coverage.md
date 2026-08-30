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
| Java | JaCoCo | `jacoco.xml` | `sonar.coverage.jacoco.xmlReportPaths` | the older `sonar.jacoco.reportPaths` is deprecated; run `mvn verify` first to produce it |
| JavaScript / TypeScript | Jest, Vitest, nyc, c8 | `lcov.info` | `sonar.javascript.lcov.reportPaths` | CSS has extra requirements — see `languages/javascript-typescript-css.md` |
| .NET | dotCover, VS Coverage, Coverlet | `*.xml` / `*.coveragexml` | `sonar.cs.dotcover.reportsPaths` / `sonar.cs.vscoveragexml.reportsPaths` / `sonar.cs.opencover.reportsPaths` | requires SonarScanner for .NET; the CLI cannot analyze C# |
| Python | coverage.py | `coverage.xml` | `sonar.python.coverage.reportPaths` | run `coverage xml` to produce the Cobertura-compatible format |
| PHP | PHPUnit, phpcov | `clover.xml` | `sonar.php.coverage.reportPaths` |  |
| Generic | any tool, converted | `generic` XML | `sonar.coverageReportPaths` | for unsupported tools; convert to the generic format first (see `generic-test-data.md`) |

> Property names are case-sensitive; in PowerShell, quote any value containing a `.`.

## Pre-scan checklist

```powershell
Test-Path coverage/lcov.info          # exists and is non-empty
Test-Path target/site/jacoco/jacoco.xml
(Get-Item coverage/lcov.info).Length -gt 0
# paths inside the report must line up with sonar.projectBaseDir, or the analysis will not match them
```

- Report empty or missing → follow `troubleshooting.md#Coverage report path missing`; **never** create an empty placeholder file
- Project with no coverage tool → state "no coverage" explicitly and scan without the property
- Multi-module / monorepo → each module's `sonar.*` must point at that module's own report

## Official deep reading

- Overview: `test-coverage/overview.md`
- Parameters: `test-coverage/test-coverage-parameters.md` / `test-execution-parameters.md`
- Per language: `java-test-coverage.md`, `javascript-typescript-test-coverage.md`, `dotnet-test-coverage.md`, `python-test-coverage.md`, `php-test-coverage.md`, `generic-test-data.md`
- Canonical entry point: https://docs.sonarsource.com/sonarqube-community-build/analyzing-source-code/test-coverage
