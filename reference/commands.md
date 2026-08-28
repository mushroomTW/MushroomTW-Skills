# 指令與設定範本

Windows PowerShell 為主，Bash 對應寫法附在需要處。所有片段預期在**同一個程序**內依序執行，token 只存在該程序記憶體。

## 1. 服務與掃描器檢查

```powershell
$env:SONAR_HOST_URL = 'http://127.0.0.1:9000'   # 使用者或既有設定指定其他位址時才覆寫
(Invoke-RestMethod "$env:SONAR_HOST_URL/api/system/status").status   # 需為 UP
sonar-scanner --version
```

`status` 非 `UP` 時停止，先處理伺服器；HTTP 可用但 Docker CLI 權限不足不算阻擋條件。

## 2. 認證檢查與清除

`SONAR_TOKEN` 即 SonarScanner 讀取的標準變數名，由系統環境變數直接提供，不需另行映射。

```powershell
if ([string]::IsNullOrWhiteSpace($env:SONAR_TOKEN)) {
    throw '環境變數 SONAR_TOKEN 未設定。請在 SonarQube 產生 user token 後，於系統環境變數設定 SONAR_TOKEN 並重開 shell。'
}
```

Bash 對應：

```bash
[ -n "$SONAR_TOKEN" ] || { echo 'SONAR_TOKEN 未設定'; exit 1; }
```

全部步驟（含驗證）完成後才清除，清除過早會讓後續 API 呼叫失敗：

```powershell
Remove-Item Env:SONAR_TOKEN -ErrorAction SilentlyContinue
```

不使用 `setx`；不寫入任何檔案。

## 3. Web API 認證 header

只在 MCP 工具沒有對應功能時使用（例如建立專案）。

```powershell
$pair    = "$($env:SONAR_TOKEN):"
$basic   = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($pair))
$headers = @{ Authorization = "Basic $basic" }
```

SonarQube 10 以上亦接受 `@{ Authorization = "Bearer $($env:SONAR_TOKEN)" }`。

不得 `echo $headers`、`$pair`、`$basic`，也不得把 `$headers` 放進錯誤訊息或交付摘要。

## 4. 專案查詢與建立

查詢優先走 MCP：`mcp__sonarqube__search_my_sonarqube_projects`。無法使用時 fallback：

```powershell
(Invoke-RestMethod -Headers $headers `
    -Uri "$env:SONAR_HOST_URL/api/projects/search?projects=$projectKey").components
```

不存在且 token 具 `Create Projects` 權限時才建立（無對應 MCP 工具）：

```powershell
$projectKey  = 'my-project-key'
$projectName = 'My Project'
Invoke-RestMethod -Method Post -Headers $headers `
    -Uri "$env:SONAR_HOST_URL/api/projects/create" `
    -Body @{ project = $projectKey; name = $projectName }
```

建立後再查詢一次確認，並記下 dashboard URL：`$env:SONAR_HOST_URL/dashboard?id=$projectKey`。首次分析前 Quality Gate 為 `NONE` 屬正常。

## 5. `sonar-project.properties` 範本

已有設定時最小幅度合併，不整份覆蓋。放在 repository 根目錄，使用檔案編輯工具寫入，不用 shell 重導向。

```properties
sonar.projectKey=my-project-key
sonar.projectName=My Project
sonar.sourceEncoding=UTF-8

# 依實際檔案確認的來源範圍
sonar.sources=.

# 產物、依賴快取、coverage 輸出、scanner 工作目錄、VCS 目錄、二進位資產
sonar.exclusions=**/bin/**,**/obj/**,**/dist/**,**/build/**,**/out/**,**/target/**,\
  **/node_modules/**,**/vendor/**,**/.venv/**,**/venv/**,\
  **/coverage/**,**/*.lcov,**/.scannerwork/**,**/.git/**,\
  **/*.dll,**/*.exe,**/*.so,**/*.dylib,**/*.jar,**/*.png,**/*.jpg,**/*.pdf,**/*.zip
```

規則：

- `sonar.host.url` 由環境變數 `SONAR_HOST_URL` 提供即可，寫進檔案並非必要；token 絕不寫入此檔。
- 排除清單只針對能確認的產物；不得為了方便排除整個語言目錄、測試目錄或未知的原始碼。
- 只有在能確認測試目錄與測試分類規則時才加 `sonar.tests`；嵌入原始碼的測試保留既有分析方式。
- 語言專屬的 report 參數（coverage、既有 linter 報告）必須查該 SonarQube 版本與 analyzer 的文件確認正確 property 名稱，不得猜測。沒有可匯入的報告就明確標示「未提供」。

## 6. 執行掃描

```powershell
sonar-scanner
if ($LASTEXITCODE -ne 0) { throw "sonar-scanner 失敗，exit code $LASTEXITCODE" }
```

輸出需同時滿足：包含 `EXECUTION SUCCESS`、exit code 為 0、log 中的 project key 與 server URL 與預期一致。只保留成功/失敗摘要，不回傳完整 scanner log。

## 7. 驗證 CE task 與 Quality Gate

解析 `report-task.txt` 取得 CE task id：

```powershell
$report = @{}
Get-Content .scannerwork\report-task.txt | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') { $report[$Matches[1]] = $Matches[2] }
}
$ceTaskId = $report['ceTaskId']
```

輪詢至終態或逾時：

```powershell
$deadline = (Get-Date).AddMinutes(5)
do {
    $status = (Invoke-RestMethod -Headers $headers `
        -Uri "$env:SONAR_HOST_URL/api/ce/task?id=$ceTaskId").task.status
    if ($status -in 'SUCCESS','FAILED','CANCELED') { break }
    Start-Sleep -Seconds 5
} while ((Get-Date) -lt $deadline)
$status
```

Quality Gate 優先走 MCP：`mcp__sonarqube__get_project_quality_gate_status`。無法使用時 fallback：

```powershell
(Invoke-RestMethod -Headers $headers `
    -Uri "$env:SONAR_HOST_URL/api/qualitygates/project_status?projectKey=$projectKey").projectStatus.status
```

`ERROR` 時列出未通過條件的名稱與數值，不自行修改 Quality Gate 規則。

## 8. MCP 工具優先路徑

| 需求 | 工具 |
| --- | --- |
| 查專案 | `mcp__sonarqube__search_my_sonarqube_projects` |
| Quality Gate 狀態 | `mcp__sonarqube__get_project_quality_gate_status` |
| Issues | `mcp__sonarqube__search_sonar_issues_in_projects` |
| Measures | `mcp__sonarqube__get_component_measures` |
| 分支 | `mcp__sonarqube__list_branches` |
| 建立專案 | 無 MCP 工具，只能用 `POST /api/projects/create` |

Issues 與 measures 只在驗證失敗或使用者要求時查詢。

## 9. 工作樹收尾

```powershell
git diff --check
git status --short
```

`.scannerwork/`、coverage 輸出與其他掃描產物加入適當 ignore 規則。除非使用者明確要求，不執行 `git commit` 或 `git push`。
