# Excellent Project Docs

[English](excellent-project-docs.md) | **繁體中文**

> 本文件位於 `docs/`。skill 本體位於 [`excellent-project-docs/SKILL.md`](../excellent-project-docs/SKILL.md)。

一個可供 Codex 與 Claude Code 安裝的 skill，用 repository 事實建立、改善、稽核及同步整個 repository 層級的文件集——`README.md`，加上 GitHub 會從根目錄或 `.github/` 讀取的標準隨附文件（`CONTRIBUTING.md`、`CODE_OF_CONDUCT.md`、`SECURITY.md`、`SUPPORT.md`、`CHANGELOG.md`、`ARCHITECTURE.md`、`ROADMAP.md`、`GOVERNANCE.md`、issue 與 pull request 範本）。

它把 README 視為樞紐、隨附文件視為衛星：README 先幫助讀者判斷專案是否適合自己，再提供可複製、可驗證的最小成功路徑；每個衛星文件只負責一個會讓 README 膨脹的主題，並由 README 連結過去。所有功能、命令、版本、設定、聯絡方式與連結都必須能追溯至 repository 證據；無法確認的資訊會明確標記，而不是合理猜測。

## 快速使用

在 Codex 中明確指定 skill：

```text
$excellent-project-docs 請根據這個 repository 的實際內容改善 README，驗證所有安裝與使用命令，並告訴我證據支持哪些隨附文件。
```

在 Claude Code 中執行 skill：

```text
/excellent-project-docs 請根據這個 repository 的實際內容改善 README，驗證所有安裝與使用命令，並告訴我證據支持哪些隨附文件。
```

兩個產品也可以在任務符合 skill 描述時自動載入它。預期結果是一份適合專案規模的 README、你在提案確認點同意建立的隨附文件，以及已驗證項目、未執行檢查與資訊缺口的摘要。

## 功能

- 支援建立、改善、稽核與同步四種工作模式，涵蓋整個文件集。
- 先從程式碼、manifest、測試、設定、發布歷史與現有文件建立證據清單。
- 依讀者採用專案的決策順序組織內容，不照實作順序堆疊章節。
- 依證據判斷哪些隨附文件值得存在，先提案、經你同意才建立；你點名的文件則直接處理。
- 每個事實只有一個擁有者：README 摘要並連結，衛星文件不重述 README，文件之間的矛盾會被解決或回報。
- 呈現方式由你決定：詢問文件集要涵蓋哪些語言、要放哪些徽章／logo／截圖與採用哪種風格、多種安裝管道時以哪一條為主，以及建立新 README 時從兩三個標語中挑選開頭那一句。
- 提供兩種呈現層級：plain（預設）或 showcase——後者把同一組事實做成統一色盤的設計頁面：置中標頭區與 skill 依專案設計的 SVG banner（編輯海報、終端機 mockup、圖為主、分割面板四種方向）、事實列、每個概念一張圖（套主題的 Mermaid 或手繪 SVG）、功能卡片格、摺疊的參考表格——每個形狀、數字與輸出行都來自證據。
- 授權交給 `LICENSE` 檔，GitHub 會在側欄自動顯示：README 不放 License 章節或徽章，除非授權需要說明（雙授權、非 OSI 授權、依版本不同），且只寫一行 SPDX 識別碼加連結。
- 驗證每份經手文件中的安裝、啟動、測試、範例、目錄與本機連結。
- 依 CLI、函式庫、服務、前端或研究工具調整 README 結構。
- 同步維護多語言版本，無法同步時回報差異。
- 缺少證據時先詢問使用者或在交付報告回報缺口，不留下待辦佔位，也不虛構貢獻規則、安全聯絡方式或發布歷史。

## 工作方式

1. 確認語言、讀者、目的、目標文件與輸出位置。
2. 從原始碼、manifest、測試、設定、範例、發布歷史及每一份現有隨附文件建立證據清單。
3. 選擇 README 章節與證據支持的隨附文件；對任何新的隨附文件先提案，並詢問呈現方式（plain 或 showcase 層級、徽章與圖片、徽章風格、主要安裝管道、標語），等待同意。
4. 逐份起草：由用途與最小範例開始，逐步補上安裝、設定、限制與維護資訊，並讓 README 連到每個衛星文件。
5. 檢查命令、連結、標題、資產與範例是否可追溯且可執行，並確認沒有任何事實同時由兩份文件擁有。
6. 以各文件的首次閱讀者角度進行最後複核，回報驗證結果、已提案但未建立的檔案與資訊缺口。

詳細規則位於 [`SKILL.md`](../excellent-project-docs/SKILL.md)。README 的設計原則、showcase 食譜、隨附文件規則、品質檢核表與風格範例位於同一個 skill 的 [`references/`](../excellent-project-docs/references/) 目錄。

## 範圍

納入：`README.md` 與上述隨附文件，位置以 GitHub 會讀取的地方為準（`.github/`、根目錄或 `docs/`）。`LICENSE` 只回報、不撰寫——選擇授權是你的決定。

不納入：完整 API 參考、文件網站、`docs/` 底下的頁面，以及與 repository 無關的文章。skill 會把 `docs/` 當作證據來讀並連結過去，但不撰寫它。

## Skill 入口位置

唯一的 skill 入口是 [`SKILL.md`](../excellent-project-docs/SKILL.md)，其輔助檔案位於同一個目錄：

```text
excellent-project-docs/
├── SKILL.md
├── agents/openai.yaml
├── references/
└── scripts/validate_docs.py
```

請勿在 repository 內複製第二份 skill。安裝時只會複製這一個目錄，因此所有指示只有一個維護來源。

## 驗證

靜態檢查器僅依賴 Python 標準函式庫，可一次接受多份 Markdown 文件，逐份檢查未完成標記、空連結目標、本機連結，以及指向不存在授權檔的敘述，並略過程式碼區塊與行內程式碼。章節或隨附文件是否齊備、內容是否有用交由品質檢核表判斷，不以關鍵字比對代替：

```powershell
python scripts/validate_docs.py README.md CONTRIBUTING.md SECURITY.md --project .
```

成功時每份文件輸出一行：

```text
README.md: static checks passed.
CONTRIBUTING.md: static checks passed.
SECURITY.md: static checks passed.
```

> [!NOTE]
> 腳本只做靜態檢查，不能取代命令實際執行、外部連結存取、「每個衛星文件都有從 README 連過去」的確認，或人工逐份閱讀複核。

## 專案結構

```text
excellent-project-docs/
├── SKILL.md                         # 核心指示與觸發範圍
├── agents/openai.yaml               # Codex 顯示資料與預設提示
├── references/                      # README 設計框架、showcase 食譜、隨附文件規則、檢核表與範例
└── scripts/                         # 可一次檢查多份文件的靜態檢查器
```

## 限制

- 此 skill 不取代完整 API 文件、教學網站或一般文章的撰寫流程。
- 它不撰寫 `LICENSE`，也不會虛構只有你能提供的內容：安全聯絡方式、貢獻政策、行為準則標準、路線圖。
- 檢查品質受 repository 中可取得的程式碼、設定、文件與工具影響。
- 需要網路、憑證、付費服務或會改動資料的驗證，仍須取得適當授權後才能執行。

## 安裝

請在倉庫根目錄讓 `skills` CLI 自動偵測相容 agent，並安裝此 skill：

```bash
npx skills add . --skill excellent-project-docs
```

若要安裝到個人層級，請加上 `--global`；未加時為專案層級。若採手動安裝，請把 `excellent-project-docs/` 複製到 host 文件指定的 skills 目錄，不要假設特定 runtime 路徑。

> [!NOTE]
> 第一次執行 `npx` 可能會下載 CLI。若 host 只在 session 啟動時偵測 skill，安裝後請重新載入或重啟。

## 開發與貢獻

修改 skill 後，請用實際 repository 測試建立、改善與稽核情境——包含至少一個證據支持隨附文件的 repository——並對兩份 README 重新執行上方的靜態檢查。提交前確認新增的命令、功能與連結都有 repository 證據支持。
