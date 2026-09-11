# Fix All SonarQube Issues

[English](sonarqube-fix-all.md) | **繁體中文**

> 本文件位於 `docs/`。skill 本體位於 [`sonarqube-fix-all/SKILL.md`](../sonarqube-fix-all/SKILL.md)。

透過已設定好的 SonarQube MCP 連線，批次修正自架 SonarQube 回報的品質與安全問題，逐批驗證後重新掃描，並誠實回報「修了什麼、抑制了什麼、放著沒動什麼」。

語言無關；能處理沒有自動化測試的專案，並且會保護語意敏感的程式碼（bytecode／IL 操作、runtime patching、反射驅動）不被亂改。

要先把專案接上本機 SonarQube，請用 [local-sonarqube-setup](local-sonarqube-setup.zh.md)。

## 觸發時機

請以名稱明確叫用 —— 此 skill 僅限手動觸發，即使請求提到 SonarQube 問題或 quality gate 沒過也不會自動觸發。它在 frontmatter 聲明 `disable-model-invocation: true`，host 不會自行啟動它：

```text
/sonarqube-fix-all
```

## 限制

- 分析伺服器是 **Docker 自架的 SonarQube，絕不是 SonarCloud**
- 絕不要求使用者提供、建立、顯示或修改 SonarQube 憑證。查詢走 MCP，掃描 token 讀系統環境變數 `SONAR_TOKEN`，其值絕不印出或寫入 log
- **絕不更改伺服器上的 issue 狀態**。`Accepted`、`False positive`、`Won't fix`、檔案排除、停用 quality profile 規則全部禁止，除非使用者明確要求該項重分類
- 絕不重設、還原或丟棄使用者既有變更。絕不 push
- 輸出精簡：只給摘要與相關片段，不倒完整 payload、issue 清單或原始 log

## 流程

| # | 階段 | 重點 |
| --- | --- | --- |
| 1 | 偵測工具鏈 | 不假設語言、建置工具或測試框架，從 manifest 與 lockfile 判定；monorepo 逐模組解析，批次不跨模組 |
| 2 | 前置檢查 | 工作樹乾淨、**變更前建置必須是綠的**、在專屬分支上工作。任一項不成立就停下回報 |
| 3 | 解析環境 | 從對話、repo 設定、建置 manifest 與 Docker 設定推導 workspace root、MCP 連線、server URL、project key。**絕不猜 project key** |
| 4 | 抓取與分類 | 依嚴重度→規則→檔案分組，Blocker/Critical/High 優先，同檔案的相容修正合併成一批 |
| 5 | 敏感區域辨識 | 見下節 |
| 6 | 修正或說明理由 | 預設在源頭修。就地抑制與保留開啟各有明確條件 |
| 7 | 逐批驗證 | 每批跑該模組的 formatter、linter、build；有測試就跑測試，沒有就以「build 乾淨、無新增警告、未動敏感區」為準。每批通過後 commit 一個檢查點 |
| 8 | 重新掃描 | 全量 build＋測試後跑 SonarScanner，以 **issue key 集合差異**比對，不看總數。最多三輪自動掃描 |
| 9 | 回報 | 分節列出：變更檔案、源頭修正、待人工冒煙測試、抑制項及理由、保留開啟項及理由、驗證命令與 Quality Gate 狀態。關閉問題一律不得寫成缺陷減少 |

## 敏感區域——不重寫

有些程式碼的正確性建立在靜態分析器看不見的結構上。下列一律視為敏感：

- **Bytecode／IL 操作**或對非自有程式碼的 runtime patching——指令序列比對、程式碼生成、攔截 hook
- **反射或 metaprogramming 驅動**——以字串名稱解析成員，或行為由 annotation／decorator／慣例掛上
- **順序或時序相依**——初始化順序、生命週期 hook、並行原語
- **原生、FFI 或序列化邊界**——欄位順序、記憶體佈局或精確命名屬於契約的一部分
- **生成、vendored 或第三方**來源

敏感區域只允許**保持語意**的修改（補 null／邊界檢查、釋放資源、修真正的競態）。任何控制流、簽章、宣告順序或指令序列的更動一律**跳過並回報**給人工審查——這裡的靜默語意變更會建置成功，只在使用者環境的 runtime 才爆。

## 抑制的判準

就地抑制只在規則與該段程式碼的設計意圖真正衝突時使用，並且用該語言最小範圍的機制、綁定特定規則、附上書面理由：

```txt
<local suppression directive> <rule id>  // reason: 為什麼這條規則不適用於此
```

典型案例是「單一線性敘事」函式（指令比對器、協定狀態機、parser dispatch）上的 cognitive complexity。判準是：**抽出來的單元若能取一個誠實描述其行為的名字，就抽出來；若最好的名字只能叫 `part2`，就改用抑制。**

## 安裝

請在倉庫根目錄讓 `skills` CLI 自動偵測相容 agent，並安裝此 skill：

```bash
npx skills add . --skill sonarqube-fix-all
```

若要安裝到個人層級，請加上 `--global`；未加時為專案層級。若採手動安裝，請把 `sonarqube-fix-all/` 複製到 host 文件指定的 skills 目錄，不要假設特定 runtime 路徑。

> [!NOTE]
> 第一次執行 `npx` 可能會下載 CLI。若 host 只在 session 啟動時偵測 skill，安裝後請重新載入或重啟。此 skill 需要已設定好的 SonarQube MCP 連線。
