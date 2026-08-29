# Coverage report mapping

> 依官方 `analyzing-source-code/test-coverage/*` 整理。SonarQube 不產生 coverage，只**匯入**你在掃描前用原生工具產生的報告。格式與屬性名需對照當前 SonarQube 版本確認，本表為常用對照（B 選項）。

## 流程（必做順序）

1. coverage 工具作為 build pipeline 一環在 **scanner 之前**執行
2. 調整工具輸出，使路徑與格式符合 scanner 預期
3. 在 `sonar-project.properties` 或 CLI 參數設定對應 `sonar.*` 屬性，讓 scanner 匯入

`test execution`（哪些測試被執行）與 `test coverage`（覆蓋率）是兩個不同功能，參數不同。

## 語言別對照表

| 語言 / 生態 | 產生工具（例） | 報告格式 | SonarQube 屬性（對照官方確認） | 備註 |
|---|---|---|---|---|
| Java | JaCoCo | `jacoco.xml` | `sonar.coverage.jacoco.xmlReportPaths` | 舊版 `sonar.jacoco.reportPaths` 已棄用；需先 `mvn verify` 產生 |
| JavaScript / TypeScript | Jest, Vitest, nyc, c8 | `lcov.info` | `sonar.javascript.lcov.reportPaths` | CSS 亦有額外要求見 `languages/javascript-typescript-css.md` |
| .NET | dotCover, VS Coverage, Coverlet | `*.xml` / `*.coveragexml` | `sonar.cs.dotcover.reportsPaths` / `sonar.cs.vscoveragexml.reportsPaths` / `sonar.cs.opencover.reportsPaths` | 必須用 SonarScanner for .NET，CLI 無法分析 C# |
| Python | coverage.py | `coverage.xml` | `sonar.python.coverage.reportPaths` | 需 `coverage xml` 產生 Cobertura 相容格式 |
| PHP | PHPUnit, phpcov | `clover.xml` | `sonar.php.coverage.reportPaths` |  |
| Generic | 任意工具轉換 | `generic` XML | `sonar.coverageReportPaths` | 用於不直接支援的工具，需先轉為 generic 格式（見 `generic-test-data.md`） |

> 屬性名大小寫敏感；PowerShell 中含 `.` 的值需用引號包裹。

## 檢查清單（掃描前）

```powershell
Test-Path coverage/lcov.info          # 存在且非空
Test-Path target/site/jacoco/jacoco.xml
(Get-Item coverage/lcov.info).Length -gt 0
# 報告內路徑與 sonar.projectBaseDir 對齊，否則分析時對不上
```

- 報告為空或不存在 → 依 `troubleshooting.md#Coverage report path missing` 處理，**絕不**建立空占位檔
- 無 coverage 工具的專案 → 明確聲明「無覆蓋率」，不帶屬性掃描
- 多模組 / monorepo → 每個模組各自的 `sonar.*` 需分別指向該模組報告

## 官方深讀

- Overview: `test-coverage/overview.md`
- Parameters: `test-coverage/test-coverage-parameters.md` / `test-execution-parameters.md`
- 各語言: `java-test-coverage.md`, `javascript-typescript-test-coverage.md`, `dotnet-test-coverage.md`, `python-test-coverage.md`, `php-test-coverage.md`, `generic-test-data.md`
- Canonical 入口: https://docs.sonarsource.com/sonarqube-community-build/analyzing-source-code/test-coverage
