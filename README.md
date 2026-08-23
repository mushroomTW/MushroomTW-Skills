# Excellent README

一個可供 Codex 與 Claude Code 安裝的 skill，用 repository 事實建立、改善、稽核及同步 `README.md`。

它把 README 視為專案入口：先幫助讀者判斷專案是否適合自己，再提供可複製、可驗證的最小成功路徑。所有功能、命令、版本、設定與連結都必須能追溯至 repository 證據；無法確認的資訊會明確標記，而不是合理猜測。

## 快速使用（Usage）

在 Codex 中明確指定 skill：

```text
$excellent-readme 請根據這個 repository 的實際內容改善 README，並驗證所有安裝與使用命令。
```

在 Claude Code 中執行 namespaced skill：

```text
/excellent-readme:excellent-readme 請根據這個 repository 的實際內容改善 README，並驗證所有安裝與使用命令。
```

兩個產品也可以在任務符合 skill 描述時自動載入它。預期結果是一份適合專案規模的 README，以及已驗證項目、未執行檢查與資訊缺口的摘要。

## 功能

- 支援建立、改善、稽核與同步四種工作模式。
- 先從程式碼、manifest、測試、設定與現有文件建立證據清單。
- 依讀者採用專案的決策順序組織內容，不照實作順序堆疊章節。
- 驗證安裝、啟動、測試、範例、目錄與本機連結。
- 依 CLI、函式庫、服務、前端或研究工具調整 README 結構。
- 缺少證據時保留明確待辦或回報缺口，不虛構功能與相容性資訊。

## 從 Marketplace 安裝

此 repository 同時提供 Codex 與 Claude Code 的自架 marketplace catalog。以下命令會先加入 GitHub marketplace，再安裝 `excellent-readme` plugin。

### Codex

```powershell
codex plugin marketplace add mushroomTW/excellent-readme
codex plugin add excellent-readme@mushroomtw-skills
```

### Claude Code

```powershell
claude plugin marketplace add mushroomTW/excellent-readme
claude plugin install excellent-readme@mushroomtw-skills
```

> [!IMPORTANT]
> GitHub repository 必須可供安裝端讀取。若是 private repository，請先設定對應的 Git credential。

Codex 與 Claude Code 會從各自的 catalog 安裝同一份 plugin 內容，因此 skill 指示、參考資料與檢查腳本不會分叉。格式依據 [OpenAI Build plugins](https://learn.chatgpt.com/docs/build-plugins) 與 [Claude Code plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces) 官方文件。

## 工作方式

1. 確認 README 的語言、讀者、目的與輸出位置。
2. 從 knowledge graph、原始碼、manifest、測試、設定、範例及現有文件建立證據清單。
3. 依專案類型選擇必要章節，不套用固定的完整模板。
4. 由用途與最小範例開始，逐步補上安裝、設定、限制與維護資訊。
5. 檢查命令、連結、標題、資產與範例是否可追溯且可執行。
6. 從首次閱讀者角度進行最後複核，回報驗證結果與資訊缺口。

詳細規則位於 [`SKILL.md`](.agents/plugins/plugins/excellent-readme/skills/excellent-readme/SKILL.md)。README 的設計原則、品質檢核表與風格範例位於同一個 skill 的 [`references/`](.agents/plugins/plugins/excellent-readme/skills/excellent-readme/references/) 目錄。

## 驗證

README 靜態檢查器僅依賴 Python 標準函式庫，可檢查必要內容提示、未完成標記與本機連結：

```powershell
python .agents/plugins/plugins/excellent-readme/skills/excellent-readme/scripts/validate_readme.py README.md --project .
```

成功時會輸出：

```text
README static checks passed.
```

驗證兩個 plugin manifest 與 marketplace catalog：

```powershell
claude plugin validate .
python C:/Users/<user>/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .agents/plugins/plugins/excellent-readme
```

> [!NOTE]
> README 腳本只做靜態檢查，不能取代命令實際執行、外部連結存取或人工閱讀複核。Codex 驗證器的實際路徑取決於本機 Codex 安裝位置。

## 專案結構

```text
excellent-readme/
├── .claude-plugin/
│   └── marketplace.json                 # Claude Code marketplace catalog
├── .agents/plugins/
│   ├── marketplace.json                 # Codex marketplace catalog
│   └── plugins/excellent-readme/
│       ├── .claude-plugin/plugin.json   # Claude Code plugin manifest
│       ├── .codex-plugin/plugin.json    # Codex plugin manifest
│       └── skills/excellent-readme/
│           ├── SKILL.md                 # 核心指示與觸發範圍
│           ├── agents/openai.yaml       # Codex 顯示資料與預設提示
│           ├── references/              # 設計框架、檢核表與範例
│           └── scripts/                 # README 靜態檢查器
└── README.md
```

## 限制

- 此 skill 不取代完整 API 文件、教學網站或一般文章的撰寫流程。
- 檢查品質受 repository 中可取得的程式碼、設定、文件與工具影響。
- 需要網路、憑證、付費服務或會改動資料的驗證，仍須取得適當授權後才能執行。
- repository 目前未提供授權條款；在加入 `LICENSE` 前，請勿假設可用的授權範圍。
- 此 repository 提供可直接加入的自架 marketplace；若要出現在 OpenAI 或 Anthropic 的官方公開 marketplace，仍須分別提交並通過平台審查。

## 開發與貢獻

修改 skill 或 manifest 後，請用實際 repository 測試建立、改善與稽核情境，並重新執行上方三項驗證。提交前確認新增的命令、功能與連結都有 repository 證據支持。
