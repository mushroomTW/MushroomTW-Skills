# Local SonarQube Setup

[English](local-sonarqube-setup.md) | **繁體中文**

> 本文件位於 `docs/`。Skill 本體位於 [`local-sonarqube-setup/SKILL.md`](../local-sonarqube-setup/SKILL.md)。

在**本機 Docker SonarQube**（預設 `http://127.0.0.1:9000`）完成專案的初始設置：建立專案、寫好掃描設定、以原生工具產生涵蓋率報告，並跑一次分析確認可用。

首次分析成功即完成。Quality Gate 只如實回報狀態，修正問題或讓未通過的 Gate 通過不在本 Skill 範圍內。

## 觸發時機

當使用者要把儲存庫接上本機 SonarQube、進行初始設置，或初始設置失敗需要排解時。

## 前提假設

- 執行環境為本機 Windows 主機，命令皆以 PowerShell 執行。
- SonarQube 位址預設為 `http://127.0.0.1:9000`，僅在使用者明確指定時覆寫。
- 主機環境需預先安裝可直接執行的 `sonar-scanner` 於 PATH 中——**本 Skill 不包含 Scanner 的下載、安裝或版本替換**。
- 認證金鑰必須由系統環境變數 `SONAR_TOKEN` 提供。SonarScanner for .NET 的 `begin` 步驟不讀 `SONAR_TOKEN`，因此 Skill 會在同一程序內組出 `SONARQUBE_SCANNER_PARAMS` JSON 環境變數，Token 絕不出現在命令列參數或檔案中。
- 程式語言、建置工具與涵蓋率生成方式一律從儲存庫實際內容動態探勘，不預設立場或套用假設。
- SonarQube 上的專案名稱採用專案本身的名稱（依序取自既有 Sonar 設定、建置檔或儲存庫名稱）；Quality Profile、Quality Gate、主分支、New Code 定義等伺服器端設定一律沿用預設，使用者要求才修改。

## 硬性規則（節錄）

- **嚴格 Token 防護**：Token 僅允許留存於當前程序記憶體中，嚴禁進入命令列參數、URL、日誌輸出、`sonar-project.properties` 或任何對話回覆；對外僅能描述為「已設定」或「未設定」。
- **零額外更動**：不擅自啟動 SonarQube 或資料庫服務、不改動 CI/CD 管線或 Compose 設定檔、不主動 commit 或 push（除非使用者明確要求）。
- **維持產品程式碼純潔性**：絕不為了迎合掃描工具而修改 Runtime 行為、公開 API、產品程式碼或建置語意。
- **伺服器設定維持預設**：Quality Profile、Quality Gate 等伺服器端設定一律沿用預設，使用者要求才修改；絕不刪除專案。
- **保留工作區未提交變更**：始終保留使用者現有之未提交變更。

完整規則請參閱 [`SKILL.md`](../local-sonarqube-setup/SKILL.md) 的 Rules 章節。

## 工作流程

| # | 步驟 | 重點摘要 |
| --- | --- | --- |
| 1 | **探勘** | 研讀 `AGENTS.md`、README、建置檔與既有 Sonar 設定；列出語言，主要語言不受 Community Build 支援就停止。 |
| 2 | **確認服務與掃描器** | `GET /api/system/status` 回傳 `UP`；依生態系選定 Scanner 並確認可執行。 |
| 3 | **建立專案** | 推導 key 與專案本身的名稱；已存在就沿用，否則先與使用者確認再建立。 |
| 4 | **寫入設定** | 對 `sonar-project.properties`（.NET 則為 `begin` 參數）做最小幅度合併，加入語言參數，寫入前先展示 diff。 |
| 5 | **產生涵蓋率** | 執行專案原生的測試與涵蓋率工具，確認報告有實際內容。 |
| 6 | **首次分析** | 在持有 Token 的同一程序內執行 Scanner；結束碼需為 0 且回報成功。 |
| 7 | **確認** | CE 任務達到 `SUCCESS`、`ncloc` 大於 0，如實回報 Quality Gate 狀態；將掃描產物加入忽略規則。 |

## 參考資料

- [`reference/languages.md`](../local-sonarqube-setup/reference/languages.md)——Community Build 支援的語言、各生態系對應的 scanner，以及各語言的必要參數、涵蓋率參數與常見陷阱（從步驟 1 起參考）。
- [`reference/commands.md`](../local-sonarqube-setup/reference/commands.md)——各步驟的 PowerShell 指令，含 `sonar-project.properties` 範本與 .NET 流程。
- [`reference/troubleshooting.md`](../local-sonarqube-setup/reference/troubleshooting.md)——各步驟遭遇失敗時的診斷與排查指引。

## 安裝方式

請於儲存庫根目錄下，透過 `skills` CLI 自動偵測相容 Agent 並安裝本 Skill：

```bash
npx skills add . --skill local-sonarqube-setup
```

加上 `--global` 可安裝至個人使用者層級；未加時預設為專案層級。若採用手動安裝，請將 `local-sonarqube-setup/` 目錄複製至 Agent 主機所指定的 Skills 目錄中。

> [!NOTE]
> 首次執行 `npx` 可能需要下載 CLI。若 Agent 主機僅在啟動對話階段載入 Skills，安裝完成後請重新載入或重啟主機環境。
