# Ponytail Audit Lite

[English](ponytail-audit-lite.md) | **繁體中文**

> 本文件位於 `docs/`。skill 本體位於 [`ponytail-audit-lite/SKILL.md`](../ponytail-audit-lite/SKILL.md)。

一次性的稽核：掃描整個倉庫找出過度設計，回傳一張依刪減量排序的表格，列出可以刪除、簡化，或改用標準函式庫／平台原生功能取代的地方。只回報，不動手改。

## 來源

改寫自 [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) 的 `ponytail-audit` skill（MIT，Copyright (c) 2026 DietrichGebert）。上游授權檔放在 skill 目錄內的 [`ponytail-audit-lite/LICENSE`](../ponytail-audit-lite/LICENSE)，安裝時會一併帶走。

與上游的差異：

- **僅限手動觸發。** frontmatter 聲明 `disable-model-invocation: true`，並從 `description` 拿掉觸發詞，host 不會自行啟動。請以名稱叫用（`/ponytail-audit-lite`）。
- **可獨立使用。** 移除對姊妹 skill `ponytail-review` 的引用與「stop ponytail-audit」模式切換，標籤清單完整寫在本檔內。
- **表格輸出。** 結果改為 Markdown 表格，而不是每項一行。

## 觸發時機

只在你叫用時執行。對象是整個程式碼庫，不是 diff。正確性 bug、安全漏洞與效能問題不在範圍內，請交給一般的 code review。

## 找什麼

標準函式庫或平台已內建的依賴、只有一個實作的介面、只產出一種東西的 factory、只做轉呼叫的 wrapper、只匯出一個東西的檔案、沒人用的 flag 與設定、手刻的標準函式庫功能。

每項發現帶一個標籤：

| 標籤 | 意義 |
| --- | --- |
| `delete:` | 死程式碼、沒用到的彈性、臆測性功能。取代方案：無。 |
| `stdlib:` | 手刻了標準函式庫已提供的東西；會寫出函式名稱。 |
| `native:` | 依賴或程式碼在做平台本來就會做的事；會寫出功能名稱。 |
| `yagni:` | 只有一個實作的抽象、沒人設定的設定、只有一個呼叫者的層。 |
| `shrink:` | 邏輯相同但可以更短；較短的寫法附在表格下方。 |

## 輸出

一張依刪減量由大到小排序的 Markdown 表格，下方附估計總量：

```md
| # | Tag | Cut | Replacement | Path |
|---|-----|-----|-------------|------|
| 1 | `yagni:` | <what to cut> | <replacement> | `<path>` |
| 2 | `shrink:` | <what to cut> | shorter form in #2 | `<path>` |

#2
<shorter form, as a fenced code block>

net: -<N> lines, -<M> deps possible.
```

每一格都保持單行。程式碼放不進表格儲存格，所以 `shrink:` 那一列只寫編號，較短的寫法以對應編號的程式碼區塊放在表格後面。

沒有可刪的東西時不出表格，只輸出 `Lean already. Ship.`

## 安裝

請在倉庫根目錄讓 `skills` CLI 自動偵測相容 agent，並安裝此 skill：

```bash
npx skills add . --skill ponytail-audit-lite
```

若要安裝到個人層級，請加上 `--global`；未加時為專案層級。若採手動安裝，請把 `ponytail-audit-lite/`（含其中的 `LICENSE`）複製到 host 文件指定的 skills 目錄。

> [!NOTE]
> 第一次執行 `npx` 可能會下載 CLI。若 host 只在 session 啟動時偵測 skill，安裝後請重新載入或重啟。
