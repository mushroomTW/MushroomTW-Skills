# Ponytail Audit Lite

[English](ponytail-audit-lite.md) | **繁體中文**

> 本文件位於 `docs/`。Skill 本體位於 [`ponytail-audit-lite/SKILL.md`](../ponytail-audit-lite/SKILL.md)。

一次性的輕量化程式碼稽核：掃描整個儲存庫找出過度設計（Over-engineering），產出一張依預估刪減行數由大到小排序的建議表格，具體列出可刪除、簡化或改用標準函式庫／平台原生功能取代的項目。始終堅持「只產出報告、絕不擅自修改程式碼」。

## 來源背景

本 Skill 改編自 [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) 之 `ponytail-audit` skill（MIT 授權，Copyright (c) 2026 DietrichGebert）。上游授權條款收錄於目錄內的 [`ponytail-audit-lite/LICENSE`](../ponytail-audit-lite/LICENSE)，每次安裝皆會完整隨附。

與上游版本的主要差異：

- **僅限手動觸發**：Frontmatter 為 Claude Code 設定 `disable-model-invocation: true`，`agents/openai.yaml` 為 Codex 設定 `policy.allow_implicit_invocation: false`，並自描述中移除了自動觸發詞。兩者皆不會在一般交談中自行啟動，請手動輸入 `/ponytail-audit-lite` 叫用。
- **嚴謹證據驗證**：標註 `delete:` 或 `yagni:` 之前，必須在整個專案中執行全面引用檢索。凡經由反射（Reflection）、依賴注入（DI）、框架慣例、程式進入點或已發布之公開 API 所使用的程式碼，一律不予標記。自動排除編譯生成、vendored 與第三方依賴目錄。
- **完全獨立運作**：移除對姊妹 skill `ponytail-review` 的依賴與模式切換指令，標籤規範與分類原則完整自包含於本 Skill 內。
- **結構化表格輸出**：將稽核結果收攏為清晰的 Markdown 評估表格，而非單行零散條列。

## 觸發時機

僅在使用者主動叫用時執行。適用於整體程式碼庫的架構精簡，而非 PR 增量審查（Diff Review）。常規程式錯誤（Bugs）、資安漏洞與底層效能問題不在本 Skill 範圍內，應循常規 Code Review 流程處理。

## 稽核標的

- 標準函式庫或平台原生環境已具備的外部依賴
- 僅有單一實作的介面（Interface）與單一產物的工廠模式（Factory）
- 單純轉發呼叫而無實質邏輯的中介包裝層（Wrapper）
- 僅匯出單一簡易輔助函式的零碎原始檔
- 無人使用的 Feature Flag、無效設定選項與死邏輯分支
- 自行手刻造輪子的標準函式庫功能

每項發現僅會賦予一個最相符的標籤：

| 標籤 | 分類 | 意義與說明 |
| --- | --- | --- |
| `delete:` | 無用程式碼 | 死碼、未使用的擴充彈性或臆測性功能。建議方案：直接刪除。 |
| `stdlib:` | 標準函式庫 | 手刻了標準函式庫現成的功能；會具體指名建議替換的標準函式。 |
| `native:` | 平台原生功能 | 依賴或自寫程式碼重複了執行期平台原生已有的能力；會具體指名平台功能名稱。 |
| `yagni:` | 臆測性抽象 | 僅有單一實作的抽象層、無人指派的設定參數、或僅有單一呼叫者的過度分層。 |
| `shrink:` | 程式碼精簡 | 相同業務邏輯但具備顯著更精簡的寫法；將於表格下方展示簡化前後的程式碼對比。 |

## 輸出格式

產出一張依預估刪減行數由大到小排序的 Markdown 表格，並於末尾附上整體預估減量指標：

```md
| # | Tag | Cut | Replacement | Path |
|---|-----|-----|-------------|------|
| 1 | `yagni:` | <what to cut> | <replacement> | `<path>` |
| 2 | `shrink:` | <what to cut> | shorter form in #2 | `<path>` |

#2
<shorter form, as a fenced code block>

net: -<N> lines, -<M> deps possible.
```

- `N` 為所有標記項目（包含超過 20 項而未完整排入表格者）加總的預估刪除行數，由檔案實際行數精算得出。
- `M` 為可移除的第三方套件／依賴數量。
- 若發現項目超過 20 筆，表格將保留刪減效益最高的前 20 項，並註明後續省略的項目數量。
- 表格每一儲存格皆維持單行呈現。因多行程式碼無法直接容納於表格中，`shrink:` 項目於表格內僅記錄編號，並於表格下方以標註 `#<n>` 的獨立程式碼區塊展示精簡寫法。
- 若程式碼庫已相當精煉、無過度設計之處，將不輸出表格，僅回傳：`Lean already. Ship.`

## 安裝方式

請於儲存庫根目錄下，透過 `skills` CLI 自動偵測相容 Agent 並安裝本 Skill：

```bash
npx skills add . --skill ponytail-audit-lite
```

加上 `--global` 可安裝至個人使用者層級；未加時預設為專案層級。若採用手動安裝，請將 `ponytail-audit-lite/` 目錄（包含其 `LICENSE`）複製至 Agent 主機所指定的 Skills 目錄中。

> [!NOTE]
> 首次執行 `npx` 可能需要下載 CLI。若 Agent 主機僅在啟動對話階段載入 Skills，安裝完成後請重新載入或重啟主機環境。
