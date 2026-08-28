---
name: local-sonarqube-setup
description: 將任意程式碼專案接入本機 Docker SonarQube（預設 http://127.0.0.1:9000），以主機既有 sonar-scanner 或建置工具 sonar plugin 建立專案、執行分析並驗證 Quality Gate。當使用者要求導入、設定、執行或排查本機 SonarQube 分析時使用。
---

# Local SonarQube Setup

## Assumptions

- 執行環境為目前的 Windows 主機，命令以 PowerShell 執行。
- SonarQube 位址預設 `http://127.0.0.1:9000`；只有使用者或既有設定明確指定時才覆寫。
- 主機已安裝可直接執行的 `sonar-scanner`；JVM 專案改走建置工具的 sonar plugin（見步驟 2）。本 Skill 不含安裝、下載或替換 scanner 的流程。
- 認證由系統環境變數 `SONAR_TOKEN` 提供。語言、建置系統與 coverage 產生方式一律從 repository 實際內容探勘，不套用預設語言假設。

## Hard rules

- Token 只存在於目前程序記憶體。不得進入命令列參數、URL、log、`sonar-project.properties` 或任何回覆；對外只以「已設定／未設定」描述，不提長度、前綴或部分內容。
- 只讀取 `SONAR_TOKEN` 一次，在同一程序內完成查詢、建立、掃描與驗證。不使用 `setx`；全部步驟結束後才清除 `SONAR_TOKEN` 程序變數。
- Token 若曾出現在聊天、commit、log 或其他不受控位置，完成後提醒使用者撤銷重發；「本地 token」不是省略理由。
- 不新增 SonarQube 或資料庫服務、不修改 CI 或 compose、不 commit、不 push（使用者明確要求除外）。
- 不為了掃描改變 runtime 行為、公開 API、產品程式碼或建置語意。
- 不得以 `Accepted`、`False positive` 或停用規則假裝完成；不偽造成功。
- 保留使用者既有未提交變更，不覆蓋、重置或刪除與本任務無關的檔案。
- 輸出只保留 HTTP 狀態、project key、CE task 狀態、Quality Gate 與 dashboard URL 等非敏感摘要，不回傳完整 scanner log 或 API response。
- Issues、measures 與詳細日誌只在驗證失敗或使用者要求時查詢；初次探勘後只讀必要的設定區塊與報告摘要，不重複載入整個 repository、完整 scanner log 或完整 API 回應。

## Workflow

1. **探勘**：讀 `AGENTS.md`、README、建置/測試文件與既有 sonar 設定；執行 `git status --short`。從文件或 manifest 推導語言、來源目錄、測試佈局與報告格式，不靠猜測。`git rev-parse` 失敗（非 git repo）→ 跳過步驟 1 與 7 的所有 git 檢查，並在交付摘要標明「無版控保護，改動未留可回滾紀錄」。
2. **確認服務與掃描器**：`GET /api/system/status` 需為 `UP`，並記錄 scanner 版本。HTTP 可用但 Docker CLI 權限不足不算阻擋條件。偵測到 `pom.xml` 或 `build.gradle[.kts]` → 改用該建置工具的 sonar plugin（`mvn verify sonar:sonar`、`gradle sonar`），不用 CLI `sonar-scanner`：CLI 掃 JVM 專案讀不到 bytecode，分析會靜默降級成純文字規則。兩者並存時以專案實際建置指令為準。
3. **專案查詢／建立**：
   - **決定 key**：依序取既有 `sonar-project.properties` 的 `sonar.projectKey` → `.sonarlint/connectedMode.json` → git remote 的 repo 名 → 目錄名。空白與非法字元改 `-`（只允許英數與 `-`、`_`、`.`、`:`，不可全為數字）。monorepo 子專案或轉換結果不明確 → 先問使用者。
   - **查詢**：用 `mcp__sonarqube__search_my_sonarqube_projects`。MCP 與 scanner 必須指向同一台 server；回傳結果與 `SONAR_HOST_URL` 不一致 → 停止並回報，不混用兩邊資料。
   - **重用或建立**：已存在則驗證 key/name 後重用；不存在才 `POST /api/projects/create`。🔴 **CHECKPOINT — 建立前把 key 與 name 給使用者確認並等待回覆**：專案建立後本流程無法刪除。建立後再查一次並記下 dashboard URL。權限不足 → 回報所需權限，請使用者在 UI 建立。
4. **掃描設定**：已有設定就最小幅度合併，不整份覆蓋；沒有才建立根目錄 `sonar-project.properties`。🔴 **CHECKPOINT — 寫入前把完整內容或合併 diff 給使用者確認**：這會動到使用者的 repo。排除產物、依賴快取、coverage 輸出、scanner 工作目錄、VCS 目錄與二進位資產，不得排除整個語言目錄、測試目錄或未知原始碼。範本見 `reference/commands.md`。
5. **產生報告**：先跑 repository 已定義的格式檢查、靜態分析與測試（失敗先回報，不把 SonarQube 問題冒充成測試修復），再以專案原生工具產生 coverage。確認報告路徑存在、非空檔，且暫存產物落在 ignore 範圍內。
6. **執行掃描**：在單一程序內設定 `SONAR_HOST_URL`、確認 `SONAR_TOKEN` 已生效後執行 `sonar-scanner`。必須確認輸出含 `EXECUTION SUCCESS`、exit code 為 0，且 project key 與 server URL 符合預期。
7. **驗證與收尾**：
   - **CE task**：由 `.scannerwork/report-task.txt` 取 task id，輪詢 `GET /api/ce/task?id=` 至 `SUCCESS` 或 `FAILED`。逾時（預設 5 分鐘）→ 判定為「未完成」而非失敗，回報 task id 與最後狀態請使用者稍後重查，不重跑掩蓋。
   - **Quality Gate**：用 `mcp__sonarqube__get_project_quality_gate_status` 查詢。`ERROR` → 🛑 **STOP**：列出每個未通過條件的名稱、實際值與門檻後停下，把「修程式碼再重掃」或「接受現狀」交回使用者決定；未經同意不改產品程式碼、不動 Quality Gate 設定、不排除檔案。
   - **收尾**：`.scannerwork/` 與 coverage 產物加入 ignore，以 `git diff --check` 與 `git status --short` 確認只留下預期的設定/文件變更。回報 project key/name、分析結果、Quality Gate 狀態、實際匯入的報告類型與 dashboard URL。

## References

- 進入步驟 2 前讀 `reference/commands.md`：PowerShell 指令、`sonar-project.properties` 範本、MCP 工具對照表。
- 任何步驟失敗才讀 `reference/troubleshooting.md`。
