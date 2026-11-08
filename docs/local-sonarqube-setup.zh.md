# Local SonarQube Setup

[English](local-sonarqube-setup.md) | **繁體中文**

> 本文件位於 `docs/`。Skill 本體位於 [`local-sonarqube-setup/SKILL.md`](../local-sonarqube-setup/SKILL.md)。

將支援的專案對接至**本機 Docker SonarQube** 執行環境（預設 `http://127.0.0.1:9000`）：自動建立專案、生成原生測試涵蓋率報告、執行靜態代碼分析並驗證 Quality Gate 門禁狀態。

本 Skill 專注於設定連線與自動化執行分析流程，不會擅自修改專案程式碼以修正分析出的問題。

## 觸發時機

當使用者提出導入、設定、執行或疑難排解本機 SonarQube 靜態分析之需求時。

## 前提假設

- 執行環境為本機 Windows 主機，命令皆以 PowerShell 執行。
- SonarQube 位址預設為 `http://127.0.0.1:9000`，僅在使用者明確指定時覆寫。
- 主機環境需預先安裝可直接執行的 `sonar-scanner` 於 PATH 中——**本 Skill 不包含 Scanner 的下載、安裝或版本替換**。
- 認證金鑰必須由系統環境變數 `SONAR_TOKEN` 提供。由於目前 SonarScanner for .NET 尚無法安全地從環境變數讀取 Token，Skill 會主動中斷流程，絕不將 Token 暴露於命令列參數或檔案中。
- 程式語言、建置工具與涵蓋率生成方式一律從儲存庫實際內容動態探勘，不預設立場或套用假設。

## 硬性規則（節錄）

- **嚴格 Token 防護**：Token 僅允許留存於當前程序記憶體中，嚴禁進入命令列參數、URL、日誌輸出、`sonar-project.properties` 或任何對話回覆；對外僅能描述為「已設定」或「未設定」。
- **零額外更動**：不擅自啟動 SonarQube 或資料庫服務、不改動 CI/CD 管線或 Compose 設定檔、不主動 commit 或 push（除非使用者明確要求）。
- **維持產品程式碼純潔性**：絕不為了迎合掃描工具而修改 Runtime 行為、公開 API、產品程式碼或建置語意。
- **真實門禁驗證**：嚴禁以標記 `Accepted`、`False positive` 或停用檢查規則的方式「假裝通過門禁」，必須如實回報真實狀態。
- **保留工作區未提交變更**：始終保留使用者現有之未提交變更。

完整規則清單請參閱 [`SKILL.md`](../local-sonarqube-setup/SKILL.md) 的 Hard rules 章節。

## 工作流程

| # | 步驟 | 重點摘要 |
| --- | --- | --- |
| 1 | **探勘** | 研讀 `AGENTS.md`、README、建置文件與既有 Sonar 設定；執行 `git status --short`，從 Manifest 推導語言架構與測試配置。 |
| 2 | **確認服務與掃描器** | 驗證 `GET /api/system/status` 回傳為 `UP`，檢查並記錄 Scanner 版本。 |
| 3 | **專案查詢／建立** | 優先透過 MCP 查詢現有專案（無 MCP 則使用 REST API）；僅在專案不存在時發送 `POST /api/projects/create`，並記錄儀表板 URL。 |
| 4 | **掃描設定** | 對既有設定檔進行最小幅度合併，不覆蓋既有項目；排除建置產物與快取目錄，嚴禁排除整個語言目錄或測試目錄。 |
| 5 | **產生報告** | 優先執行專案原生的檢查與測試，接著以原生工具產生測試涵蓋率報告，確認報告檔案存在且非空。 |
| 6 | **執行掃描** | 於單一程序生命週期內注入 `SONAR_HOST_URL` 與 `SONAR_TOKEN`；確認掃描輸出 `EXECUTION SUCCESS` 且結束碼為 0。 |
| 7 | **驗證與收尾** | 自 `.scannerwork/report-task.txt` 取得 Compute Engine 任務 ID 並輪詢至處理完成，查驗 Quality Gate 指標，將掃描產物加入忽略規則。 |

## 參考資料

- [`reference/commands.md`](../local-sonarqube-setup/reference/commands.md)——PowerShell 常用指令範本、`sonar-project.properties` 設定範本與 MCP 工具對照表（進入步驟 2 前必讀）。
- [`reference/troubleshooting.md`](../local-sonarqube-setup/reference/troubleshooting.md)——各步驟遭遇失敗時的診斷與排查指引。

## 安裝方式

請於儲存庫根目錄下，透過 `skills` CLI 自動偵測相容 Agent 並安裝本 Skill：

```bash
npx skills add . --skill local-sonarqube-setup
```

加上 `--global` 可安裝至個人使用者層級；未加時預設為專案層級。若採用手動安裝，請將 `local-sonarqube-setup/` 目錄複製至 Agent 主機所指定的 Skills 目錄中。

> [!NOTE]
> 首次執行 `npx` 可能需要下載 CLI。若 Agent 主機僅在啟動對話階段載入 Skills，安裝完成後請重新載入或重啟主機環境。
