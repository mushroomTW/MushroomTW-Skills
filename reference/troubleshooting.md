# 故障排除

只在對應失敗發生時閱讀。格式：症狀 → 判定 → 處置。

## `Unable to establish loopback connection`

判定：執行環境的本機網路/程序限制，不是專案設定問題。

處置：改在允許本機 loopback 連線的環境（一般使用者終端機、非受限沙箱）重跑同一組指令。**不得**為了規避而修改 `sonar-project.properties`、改用其他 host URL 或關閉功能來掩蓋。

## `SONAR_TOKEN` 在目前程序讀不到

判定：變數設在 Machine 或 User 範圍，但目前 shell 早於設定時間啟動，因此沒有繼承。

處置：先確認變數存在於哪個範圍（只印布林值，不印內容）：

```powershell
"machine=$(-not [string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable('SONAR_TOKEN','Machine')))"
"user=$(-not [string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable('SONAR_TOKEN','User')))"
```

任一為 `True` 時，重開 shell 讓程序繼承，或在目前程序內載入：

```powershell
$env:SONAR_TOKEN = [Environment]::GetEnvironmentVariable('SONAR_TOKEN','Machine')
```

兩者皆為 `False` 才是真的未設定，請使用者產生 token 後設定系統環境變數。

## HTTP 401

判定：token 未被 scanner/API 讀到，或 token 本身失效、型別不符、打到別台 server。

一線修復：確認同一程序內 `SONAR_TOKEN` 讀得到（見 commands.md 第 2 節），且清除步驟尚未執行。

仍為 401 時依序排查，每項只回報結論，不印 token 內容：

1. **token 是否仍有效**：`(Invoke-RestMethod -Headers $headers -Uri "$env:SONAR_HOST_URL/api/authentication/validate").valid`。`False` 代表已失效或被撤銷。
2. **token 型別**：Project Analysis Token 只能掃它綁定的那個專案，用來掃別的專案或呼叫一般 API 會 401；跨專案需 Global Analysis Token 或 user token。
3. **scanner 版本**：SonarQube 10 之前的 scanner 讀 `sonar.login`，不認 `sonar.token`／`SONAR_TOKEN`；版本不符時等同沒帶憑證。以步驟 2 記錄的 scanner 版本比對。
4. **host 位址**：容器內外位址不同（`localhost` 對服務名／`host.docker.internal`），打到另一台 SonarQube 也會 401。核對 `$env:SONAR_HOST_URL` 與 scanner log 中的 server URL。
5. **值本身夾帶空白或換行**：設定環境變數時貼入換行很常見。只印 `$env:SONAR_TOKEN -ne $env:SONAR_TOKEN.Trim()` 的布林結果。

以上皆排除才請使用者在 SonarQube UI 重新產生 token 並更新系統環境變數。不得把 token 改成命令列參數重試。

## HTTP 403

判定：token 有效但權限不足，最常見是缺 `Create Projects` 或該專案的 `Execute Analysis`。

處置：回報實際缺少的權限名稱，或請使用者在 SonarQube UI 先建立專案／授權後再重跑。不得偽造成功，也不得改用其他既有專案 key 頂替。

## Project key 格式被拒

判定：SonarQube 對 project key 有字元限制——允許英數字、`-`、`_`、`.`、`:`，且不可全為數字。

處置：由 repository 名稱轉換（空白與其他符號改為 `-`），確認轉換後的 key 與使用者意圖一致再建立。非顯而易見的命名先向使用者確認。

## Coverage 報告路徑不存在或為空檔

判定：coverage 未產生、輸出到別的路徑，或測試根本沒跑起來。

處置：先查專案原生的測試/coverage 指令與其實際輸出路徑，重跑產生報告後再掃描。**不得**建立空白假報告或指向不存在的路徑；專案沒有 coverage 工具時，明確標示「未提供 coverage」並執行不含 coverage 的分析。

## Analyzer 或 report 格式錯誤

判定：property 名稱不符該語言 analyzer、報告格式版本不符，或報告內容路徑與掃描根目錄對不上。

處置：查該 SonarQube 版本與 analyzer 的文件確認正確 property 與支援格式，修正原因。保留原始錯誤的非敏感摘要（規則 key、檔案路徑、格式名稱），不貼完整 log。不得以 `Accepted`、`False positive` 或停用規則假裝完成。

## 編碼或二進位檔警告

判定：來源檔編碼與 `sonar.sourceEncoding` 不符，或二進位檔被納入掃描範圍。

處置：分析仍成功時不阻擋，但要在交付摘要中說明。只有在這些警告造成分析**失敗**時，才調整掃描範圍（排除二進位資產）或修正檔案編碼。

## Quality Gate 顯示 `NONE`

判定：專案已建立但尚未有任何完成的分析，屬正常狀態而非錯誤。

處置：確認 CE task 已到 `SUCCESS` 後重查。若 CE task 已成功但仍為 `NONE`，改查 measures 確認資料是否真的上傳。

## CE task 停在 `PENDING` 或逾時

判定：SonarQube Compute Engine 忙碌、記憶體不足，或背景任務排隊。

處置：延長輪詢上限後重查；持續 `PENDING` 時檢查 SonarQube 容器資源與 `api/ce/activity`。task 為 `FAILED` 時取其 `errorMessage` 的非敏感摘要處理原因，不重跑掩蓋。

## 反模式對照

這節與其他節不同，**進入步驟 3 前先讀一次**。左欄任一動作出現在你的計畫裡，換成右欄再往下走。

| 不得這樣做 | 改為 |
| --- | --- |
| `-Dsonar.token=xxx`，或把 token 寫進 properties、URL、log | 只用程序環境變數 `SONAR_TOKEN` |
| 用 `setx` 或寫檔保存 token | 只留在目前程序記憶體，收尾時 `Remove-Item Env:SONAR_TOKEN` |
| 標 `Accepted`／`False positive`、停用規則、調鬆 Quality Gate 讓它過 | 列出未通過條件的名稱、實際值與門檻，交回使用者決定 |
| 用 `sonar.exclusions` 把有問題的原始碼排掉 | 只排除產物、依賴快取、coverage 輸出與二進位資產 |
| coverage 產不出來就指向不存在的路徑或建空報告 | 標示「未提供 coverage」，執行不含 coverage 的分析 |
| Maven／Gradle 專案直接跑 CLI `sonar-scanner` | 改用 `mvn verify sonar:sonar`／`gradle sonar` |
| 服務不通就自己 `docker run` 起一台 SonarQube | 狀態非 `UP` 即停止並回報，不新增服務 |
| 整份覆蓋既有 `sonar-project.properties` | 最小幅度合併，寫入前給使用者確認 |
| CE task 逾時就重跑一次當作沒事 | 判為「未完成」，回報 task id 請使用者稍後重查 |
| 專案名不確定就自己挑一個 key 建下去 | key 依步驟 3 的四層順序決定，不明確先問使用者 |
