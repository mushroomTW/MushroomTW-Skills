# Excellent README

[English](excellent-readme.md) | **繁體中文**

> 本文件位於 `docs/`。skill 本體位於 [`excellent-readme/SKILL.md`](../excellent-readme/SKILL.md)。

一個可供 Codex 與 Claude Code 安裝的 skill，用 repository 事實建立、改善、稽核及同步 `README.md`。

它把 README 視為專案入口：先幫助讀者判斷專案是否適合自己，再提供可複製、可驗證的最小成功路徑。所有功能、命令、版本、設定與連結都必須能追溯至 repository 證據；無法確認的資訊會明確標記，而不是合理猜測。

## 快速使用

在 Codex 中明確指定 skill：

```text
$excellent-readme 請根據這個 repository 的實際內容改善 README，並驗證所有安裝與使用命令。
```

在 Claude Code 中執行 skill：

```text
/excellent-readme 請根據這個 repository 的實際內容改善 README，並驗證所有安裝與使用命令。
```

兩個產品也可以在任務符合 skill 描述時自動載入它。預期結果是一份適合專案規模的 README，以及已驗證項目、未執行檢查與資訊缺口的摘要。

## 功能

- 支援建立、改善、稽核與同步四種工作模式。
- 先從程式碼、manifest、測試、設定與現有文件建立證據清單。
- 依讀者採用專案的決策順序組織內容，不照實作順序堆疊章節。
- 驗證安裝、啟動、測試、範例、目錄與本機連結。
- 依 CLI、函式庫、服務、前端或研究工具調整 README 結構。
- 同步維護多語言 README 版本，無法同步時回報差異。
- 缺少證據時先詢問使用者或在交付報告回報缺口，不在 README 留下待辦佔位，也不虛構功能與相容性資訊。

## 工作方式

1. 確認 README 的語言、讀者、目的與輸出位置。
2. 從原始碼、manifest、測試、設定、範例及現有文件建立證據清單。
3. 依專案類型選擇必要章節，不套用固定的完整模板。
4. 由用途與最小範例開始，逐步補上安裝、設定、限制與維護資訊。
5. 檢查命令、連結、標題、資產與範例是否可追溯且可執行。
6. 從首次閱讀者角度進行最後複核，回報驗證結果與資訊缺口。

詳細規則位於 [`SKILL.md`](../excellent-readme/SKILL.md)。README 的設計原則、品質檢核表與風格範例位於同一個 skill 的 [`references/`](../excellent-readme/references/) 目錄。

## Skill 入口位置

唯一的 skill 入口是 [`SKILL.md`](../excellent-readme/SKILL.md)，其輔助檔案位於同一個目錄：

```text
excellent-readme/
├── SKILL.md
├── agents/openai.yaml
├── references/
└── scripts/validate_readme.py
```

請勿在 repository 內複製第二份 skill。安裝時只會複製這一個目錄，因此所有指示只有一個維護來源。

## 驗證

README 靜態檢查器僅依賴 Python 標準函式庫，可檢查未完成標記、空連結目標、本機連結，以及指向不存在授權檔的敘述，並略過程式碼區塊與行內程式碼。章節是否齊備、內容是否有用交由品質檢核表判斷，不以關鍵字比對代替：

```powershell
python scripts/validate_readme.py README.md --project .
```

成功時會輸出：

```text
README static checks passed.
```

> [!NOTE]
> README 腳本只做靜態檢查，不能取代命令實際執行、外部連結存取或人工閱讀複核。

## 專案結構

```text
excellent-readme/
├── SKILL.md                         # 核心指示與觸發範圍
├── agents/openai.yaml               # Codex 顯示資料與預設提示
├── references/                      # 設計框架、檢核表與範例
└── scripts/                         # README 靜態檢查器
```

## 限制

- 此 skill 不取代完整 API 文件、教學網站或一般文章的撰寫流程。
- 檢查品質受 repository 中可取得的程式碼、設定、文件與工具影響。
- 需要網路、憑證、付費服務或會改動資料的驗證，仍須取得適當授權後才能執行。
- repository 目前未提供授權條款；在加入 `LICENSE` 前，請勿假設可用的授權範圍。

## 安裝

本目錄即 skill 本體，複製到 host 的 skills 目錄：

| 平台 | 個人層級 | 專案層級 |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/` | `<repo>/.claude/skills/` |
| Codex | `~/.codex/skills/` | — |

```powershell
$dest = "$HOME/.claude/skills/excellent-readme"
Remove-Item -Recurse -Force $dest -ErrorAction SilentlyContinue
Copy-Item -Recurse excellent-readme $dest
```

```powershell
$dest = "$HOME/.codex/skills/excellent-readme"
Remove-Item -Recurse -Force $dest -ErrorAction SilentlyContinue
Copy-Item -Recurse excellent-readme $dest
```

先 `Remove-Item` 是為了讓重新安裝也能使用同一組命令；若不先刪除，`Copy-Item` 會把新版本嵌到現有 skill 目錄裡面。若只想安裝在單一 repository 而非整個帳號，請改用該 repository 的 `.claude/skills/`（Claude Code）作為目的地。

> [!NOTE]
> 兩個產品在 session 啟動時讀取 skill 目錄，複製後請開啟新的 session。

## 開發與貢獻

修改 skill 後，請用實際 repository 測試建立、改善與稽核情境，並對兩份 README 重新執行上方的靜態檢查。提交前確認新增的命令、功能與連結都有 repository 證據支持。
