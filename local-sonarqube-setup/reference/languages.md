# Per-language handling

> Compiled from the official `analyzing-source-code/languages/*` and `scanners/*` pages for SonarQube Community Build (checked November 2026). Read this in step 1 once the repo's languages are known, and again in steps 2, 4 and 5 for the language you are scanning. Confirm against the docs when the server version changes.

## Contents

1. Support check (do this first)
2. Scanner per ecosystem
3. Language notes: Java · Kotlin · JS/TS/CSS · Python · Go · C#/VB.NET · PHP · IaC/Docker · Secrets/HTML/XML/Flex
4. Languages that need a community plugin
5. Languages Community Build cannot analyze

## 1. Support check

Community Build analyzes only these languages: Java, Kotlin, JavaScript, TypeScript, CSS, HTML, XML, Python, Go, PHP, C#, VB.NET, Flex, Docker, Terraform, CloudFormation, Kubernetes/Helm, Azure Resource Manager, and Secrets.

Files of any other language are skipped silently. The scan still ends with `EXECUTION SUCCESS`, so a "successful" scan of an unsupported repo can contain zero lines of code. That is why the support check comes before anything else:

- Every main language is supported → continue.
- Some are supported and some are not → continue, and name the skipped languages in the summary.
- The main language is unsupported → stop before creating the project, and tell the user which language it is and what it would need (section 4 or 5).

After the scan, check that the lines-of-code measure (`ncloc`) is above zero. Zero lines means nothing was analyzed. In that case, report it as a failure, not a success.

## 2. Scanner per ecosystem

| Ecosystem | Scanner | Invocation | Reads `SONAR_TOKEN` env |
|---|---|---|---|
| Maven | SonarScanner for Maven | `mvn verify sonar:sonar` | yes |
| Gradle | SonarScanner for Gradle | `gradle sonar` (plugin `org.sonarqube`) | yes |
| MSBuild / .NET CLI | SonarScanner for .NET | `dotnet sonarscanner begin/build/end` | `begin`: **no**, so pass the token through an in-process `SONARQUBE_SCANNER_PARAMS` (`commands.md §6.1`) |
| npm project | SonarScanner for NPM (`@sonar/scan`) | `npx @sonar/scan` (5.x needs Node.js 22.12+) | yes |
| Python | SonarScanner for Python (`pysonar`, Python 3.10+) | `pysonar`; also reads `[tool.sonar]` in `pyproject.toml` | yes |
| Rust / Cargo | SonarScanner for Cargo | `cargo sonar-scanner`; config in `[package.metadata.sonar]` of `Cargo.toml` (`host-url` is required, or it targets SonarQube Cloud; never put the token there) | yes |
| Everything else | SonarScanner CLI | `sonar-scanner` (or the Docker image) | yes |

This skill does not install scanners. If the ecosystem's own scanner is missing, the SonarScanner CLI (on the host or through Docker) can scan npm and Python projects with the same `sonar-project.properties`. That fallback does not work for C#/VB.NET, which only the .NET scanner can analyze. For Java without Maven/Gradle, see the `sonar.java.binaries` rule below.

With JRE auto-provisioning enabled, the .NET, NPM and Python scanners need no Java on the host. Maven and Gradle need Java 11+, and the CLI needs 11+ from 7.2 (17+ before 7.2). When auto-provisioning is off, every scanner needs Java 21+.

## 3. Language notes

### Java

- **Through Maven/Gradle**: the plugin supplies binaries, libraries and `sonar.java.source` automatically. Prefer this path.
- **Through the CLI**: if the project has more than one `.java` file, `sonar.java.binaries` (the compiled `.class` directories) is **required**. Without it the analysis fails with `please provide compiled classes with sonar.java.binaries`. Build the project first and point the property at the real output directory, such as `target/classes` or `build/classes/java/main`. Add `sonar.java.libraries` (dependency jars, wildcards allowed) for accuracy, and `sonar.java.test.binaries` / `sonar.java.test.libraries` when tests are in scope. Never exclude `.java` files to get past this error.
- Set `sonar.java.source` (for example `21`) when the scanner does not set it. If it is missing, rules for Java 9+ are skipped.
- If the project is built with a different JDK from the one running the scanner, set `sonar.java.jdkHome` to the project's JDK.
- Coverage: JaCoCo XML → `sonar.coverage.jacoco.xmlReportPaths`.

### Kotlin

- Prefer the Maven or Gradle scanner. With the CLI, provide the dependency binaries (`sonar.java.binaries` / `sonar.java.libraries`) for better accuracy.
- Optional: `sonar.kotlin.source.version` (format `X.Y`).
- Coverage: JaCoCo XML → `sonar.coverage.jacoco.xmlReportPaths`.

### JavaScript / TypeScript / CSS

- These analyzers run on Node.js. The scanner uses the first match among (1) `sonar.nodejs.executable`, (2) the embedded Node.js it downloads on Linux x64, Windows x64 or Apple ARM64, and (3) `node` on `PATH`. A Node.js you supply must be 22.12+ (v22) or 24.0+ (v24). On any other architecture you must supply one.
- If the embedded Node.js fails to deploy because of permissions, set `sonar.nodejs.executable` instead of excluding files.
- Source files must be read as UTF-8. Keep `sonar.sourceEncoding=UTF-8`.
- Keep `node_modules` excluded. TypeScript projects need their `tsconfig.json` inside the scan scope.
- Coverage: LCOV → `sonar.javascript.lcov.reportPaths` (Jest, Vitest, nyc, c8).
- Remove any community CSS plugin from the server, because it conflicts with the built-in CSS analysis.

### Python

- Set `sonar.python.version` (for example `3.12`, or a list such as `3.11, 3.12`) from `pyproject.toml`, `.python-version`, `setup.cfg` or CI config. Without it the analyzer assumes 2 and 3 compatibility and silences some issues.
- Exclude virtual environments (`.venv`, `venv`).
- Coverage: Cobertura XML from `coverage xml` → `sonar.python.coverage.reportPaths`. The default is `coverage-reports/*coverage-*.xml`.

### Go

- Keep `go.mod` inside `sonar.sources`, because results are less precise without it. `vendor` is excluded by default through `sonar.go.exclusions`. Leave that default alone.
- Coverage: `go test -coverprofile=coverage.out ./...` → `sonar.go.coverage.reportPaths`.

### C# / VB.NET

- These need SonarScanner for .NET 5.x or later (`dotnet sonarscanner`). The CLI cannot analyze them. Run `begin` → the repo's own build → `end` as shown in `commands.md §6.1`. That section also covers the token, which must never go into `/d:sonar.token`.
- `sonar-project.properties` is ignored by this scanner. Pass settings to `begin` with `/d:`.
- The build between `begin` and `end` must succeed. If it needs local paths, set the environment variables the repo documents rather than editing project files.
- Coverage (wildcards allowed):
  - C#: `sonar.cs.opencover.reportsPaths` (OpenCover, and Coverlet in **opencover** format) · `sonar.cs.vscoveragexml.reportsPaths` (VS Coverage, `dotnet-coverage`) · `sonar.cs.dotcover.reportsPaths` · `sonar.cs.cobertura.reportsPaths`
  - VB.NET: the same four with the `sonar.vbnet.*` prefix

### PHP

- Keep `vendor` excluded. `php.ini` files are analyzed only when they are inside the project.
- Coverage: PHPUnit Clover XML → `sonar.php.coverage.reportPaths`.

### IaC and Docker

- Terraform, CloudFormation, Kubernetes/Helm, ARM templates and Dockerfiles are picked up automatically when they are in `sonar.sources`. Do not exclude infra directories unless the user asks.
- Terraform: optionally set `sonar.terraform.provider.aws.version` / `sonar.terraform.provider.azure.version` (and other providers) so rules match the provider version actually in use.
- Docker: the default patterns are `Dockerfile`, `Dockerfile.*` and `*.dockerfile`. Add others through `sonar.docker.file.patterns`. Dockerfiles do not support `NOSONAR`.

### Secrets, HTML, XML, Flex

- Secrets detection runs on all analyzed files except documentation and template suffixes (such as `.md`). Tune it with `sonar.secrets.excluded.file.suffixes`; `sonar.text.excluded.file.suffixes` is deprecated. Never widen exclusions to hide a finding.
- HTML and XML need no setup.
- Flex coverage: Cobertura XML → `sonar.flex.cobertura.reportPaths`.

## 4. Languages that need a community plugin

From Community Build 26.11, **Ruby, Scala and Rust** are analyzed only after an administrator installs the community-maintained plugin (`sonar-ruby-plugin`, `sonar-scala-plugin`, `sonar-rust-plugin`). Installing a server plugin is outside this skill's scope. Check `GET /api/plugins/installed` (or ask the user). If the plugin is missing, stop and tell the user. Once it is installed:

- Ruby: SimpleCov JSON → `sonar.ruby.coverage.reportPaths` (for example `coverage/coverage.json`); `vendor` is excluded by default.
- Scala: Scoverage `scoverage.xml` → `sonar.scala.coverage.reportPaths`.
- Rust: use SonarScanner for Cargo. It needs Clippy (`rustup component add clippy`), which the analyzer runs by default. `sonar.rust.cargo.manifestPaths` points at extra `Cargo.toml` files.

## 5. Languages Community Build cannot analyze

C, C++, Objective-C, Swift, Dart, Groovy, Shell, PowerShell, JSON, YAML, PL/SQL, T-SQL, GitHub Actions, Azure Pipelines, Ansible, and the enterprise languages (ABAP, Apex, COBOL, Gosu, JCL, PL/I, RPG, R, VB6, MuleSoft DataWeave) need a commercial SonarQube Server edition or SonarQube Cloud. Do not try to work around this with build wrappers, other scanners or generic reports. Report it as unsupported on this server.
