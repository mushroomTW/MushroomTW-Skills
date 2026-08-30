# Local SonarQube Setup

[English](local-sonarqube-setup.md) | **繁體中文**

> 本文件位於 `docs/`。skill 本體位於 [`local-sonarqube-setup/SKILL.md`](../local-sonarqube-setup/SKILL.md)。

把支援的程式碼專案接入**本機 Docker SonarQube**（預設 `http://127.0.0.1:9000`）：建立專案、產生報告、執行分析、驗證 Quality Gate。

這個 skill 只負責「接上去並跑起來」。要批次修掉 Sonar 回報的問題，請改用 [sonarqube-fix-all](sonarqube-fix-all.zh.md)。

## 觸發時機

要求導入、設定、執行或排查本機 SonarQube 分析時。

## 前提

- 執行環境為 Windows 主機，命令以 PowerShell 執行
- SonarQube 位址預設 `http://127.0.0.1:9000`，只有明確指定時才覆寫
- 主機已安裝可直接執行的 `sonar-scanner`——**本 skill 不含 scanner 的安裝、下載或替換流程**
- 認證由系統環境變數 `SONAR_TOKEN` 提供。目前 SonarScanner for .NET 不支援此路徑，因此 skill 會停止，不把 token 暴露於參數或檔案。
- 語言、建置系統與 coverage 產生方式一律從 repository 實際內容探勘，不套用預設語言假設

## 硬性規則（節錄）

- Token 只存在於目前程序記憶體，不得進入命令列參數、URL、log、`sonar-project.properties` 或任何回覆；對外只描述「已設定／未設定」
- 不新增 SonarQube 或資料庫服務、不修改 CI 或 compose、不 commit、不 push（明確要求除外）
- 不為了掃描改變 runtime 行為、公開 API、產品程式碼或建置語意
- 不得以 `Accepted`、`False positive` 或停用規則假裝完成
- 保留使用者既有未提交變更

完整規則見 SKILL.md 的 Hard rules 章節。

## 工作流程

| # | 步驟 | 重點 |
| --- | --- | --- |
| 1 | 探勘 | 讀 `AGENTS.md`、README、建置文件與既有 sonar 設定；跑 `git status --short`，從 manifest 推導語言與測試佈局 |
| 2 | 確認服務與掃描器 | `GET /api/system/status` 須為 `UP`，記錄 scanner 版本 |
| 3 | 專案查詢／建立 | 先用 MCP 查詢；不存在才 `POST /api/projects/create`，記下 dashboard URL |
| 4 | 掃描設定 | 已有設定最小幅度合併，不整份覆蓋；排除產物與快取，不得排除整個語言目錄或測試目錄 |
| 5 | 產生報告 | 先跑專案既有的檢查與測試，再以原生工具產生 coverage，確認報告路徑存在且非空 |
| 6 | 執行掃描 | 單一程序內設定 `SONAR_HOST_URL` / `SONAR_TOKEN`，須確認 `EXECUTION SUCCESS` 且 exit code 0 |
| 7 | 驗證與收尾 | 由 `.scannerwork/report-task.txt` 取 CE task 輪詢至完成，查 Quality Gate，把產物加入 ignore |

## 參考資料

- [`reference/commands.md`](../local-sonarqube-setup/reference/commands.md)——PowerShell 指令、`sonar-project.properties` 範本、MCP 工具對照表。進入步驟 2 前必讀。
- [`reference/troubleshooting.md`](../local-sonarqube-setup/reference/troubleshooting.md)——任何步驟失敗時才讀。

## 安裝

請在倉庫根目錄讓 `skills` CLI 自動偵測相容 agent，並安裝此 skill：

```bash
npx skills add . --skill local-sonarqube-setup
```

若要安裝到個人層級，請加上 `--global`；未加時為專案層級。若採手動安裝，請把 `local-sonarqube-setup/` 複製到 host 文件指定的 skills 目錄，不要假設特定 runtime 路徑。

> [!NOTE]
> 第一次執行 `npx` 可能會下載 CLI。若 host 只在 session 啟動時偵測 skill，安裝後請重新載入或重啟。
