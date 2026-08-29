---
name: library-first
description: Use before hand-rolling a general mechanism such as retry, backoff, validation, date/time handling, state management, authentication/authorization, caching, serialization, CLI argument parsing, or cryptographic hashing, to evaluate existing library solutions before deciding to write it yourself. Triggers on hand-roll retry, custom validation, date handling, state management, auth, caching, serialization, CLI parsing, hashing, or any general mechanism someone else has already solved. Does not apply to domain-specific business logic.
---

# Library-First

> 通用機制先搜尋再手寫；每行自寫程式碼都是負債。

## Invariants

1. 必須顯式決策：`Decision: used X because Y` 或 `wrote manually because Z`。
2. 未過 Quality Gate 視為不存在。
3. 不確定必查證，不可猜測。

## Workflow

| Step | Action | Input | Output | Format |
|------|--------|-------|--------|--------|
| 1 | 命名問題 | 變數名 | 領域詞 | 例 `exponential backoff retry` 非 `callApiAgain` |
| 2 | 搜尋生態 | 領域詞+語言 | 候選 1-3 個 | 含標準庫 + npm/PyPI/NuGet/pkg.go.dev/crates.io |
| 3 | 評估候選 | 候選 | 採用/排除 | 第三方套件套用 Quality Gate；標準庫確認適用性與版本支援 |
| 4 | 決策陳述 | 判定結果 | 一句決策語 | 見模板 |

🔴 CHECKPOINT 1 · 🛑 STOP — Step 2 後暫停：確認含標準庫、主流套件、用領域詞而非變數名檢索。

### Quality Gate（第三方套件五項全過才採用）

| # | 檢查 | 條件 | 不通過 |
|---|------|------|--------|
| 1 | 維護 | 12月內 commit、未 deprecated | 排除 |
| 2 | 依賴樹 | 不為小功能引入數十依賴 | 排除 |
| 3 | License | 與專案相容（閉源 GPL 硬停） | 排除 |
| 4 | 體積 | 僅在前端 bundle size 重要時，200KB 替 20 行不划算 | 排除 |
| 5 | API | 不需重構周邊 | 排除 |

> 不確定 → 查 repo/registry/License 檔。

> 標準庫不新增依賴，不套用第三方套件的維護 commit、依賴樹與 bundle 體積門檻；改確認目標版本可用、授權相容且 API 適合。

### 決策語模板

```
Decision: used <pkg>@<ver> because gate 1-5 pass, <理由>.
Decision: used standard library <API> because target version <ver> supports it and API fits.
Decision: wrote manually because domain-specific business logic.
Decision: wrote manually because performance-critical, measured <metric> shows library overhead is unacceptable.
Decision: wrote manually because security-sensitive, full auditability is required and opaque dependencies are unacceptable.
Decision: wrote manually because evaluated <pkg> failed gate #<n>.
Decision: wrote manually because no suitable candidate exists after checking <來源>.
Decision: wrote manually because this is a one-off three-line helper with no edge cases, state, or growth.
```

## 四種應手寫

- **領域邏輯** — 折扣、保費、遊戲規則。
- **效能關鍵** — 有實測數據證明抽象開銷不可接受。
- **安全敏感** — 需完全可審計。
- **已評估不足** — *evaluated* 非假設。

## 不要手寫這些

| Need | 不要自己寫 |
|---|---|
| Retry / circuit breaker | `cockatiel` (TS), `Polly` (C#), `tenacity` (Py) |
| Auth | Auth0, Supabase, Keycloak, ASP.NET Identity |
| 前端狀態 | Zustand, Redux, Jotai |
| Schema 驗證 | Zod, Pydantic, FluentValidation |
| Date/time | `date-fns`, Temporal, NodaTime |
| Cache/序列化/CLI/hashing | 先搜尋對應生態主流方案 |

> 三行 helper 例外：只用一次、沒有邊界案例或狀態、且不會成長的三行 helper 可直接手寫。

🔴 CHECKPOINT 2 — Step 4 提交前自檢：決策語含 because、對應評估結果或手寫理由、無軟化措辭。

## Failure Handling

| 觸發 | 一線修復 | 仍失敗兜底 |
|---|---|---|
| 找不到候選 | 換領域詞重搜 + 查標準庫 | 手寫並記已查來源與「no suitable candidate」 |
| 任一 gate 不通過 | 換次優候選 | 全不通過 → 手寫並記失敗 gate # |
| License 不確定 | 讀 LICENSE/registry 欄位 | 仍不確定 → 視為不相容 |
| 候選過多 | 按 gate 篩至 1-3 個深查 | 決策語列已排除原因 |
| 手寫後邊界爆炸 | 重跑 Step 2-3 評替換 | 封裝為內部模組，不在業務中膨脹 |

## Never Do

1. 用變數名檢索 — 搜 `callApiAgain` 找不到 `exponential backoff`。
2. 靜默決策 — 無 `Decision: ... because ...` 視為未完成。
3. 猜測 — 「應該/大概」改為查 commit/License/體積。
4. 因有名就採用 — 未過 gate 高星也不用。
5. 為三行 helper 引套件。
6. 用軟化措辭 — 禁「可以考慮/視情況/靈活把握」，必須 pass/fail。

## Examples

| 場景 | Step 1 命名 | Step 2 候選 | Gate 結果 | Decision |
|---|---|---|---|---|
| 指數退避重試 (Node) | `exponential backoff retry` | `cockatiel`/`p-retry` + 標準庫 | `cockatiel` 1-5 pass | `Decision: used cockatiel@<ver> because gate 1-5 pass, API不侵入且依賴輕` |
| 訂單滿千折百 | `order discount rule (domain)` | 不適用（業務規則） | 不需搜尋 | `Decision: wrote manually because domain-specific business logic` |
| Schema 驗證 | `schema validation` | `Zod` vs 手寫 regex | Zod 1-5 pass | `Decision: used zod@<ver> because gate 1-5 pass, License MIT、體積可接受、API可組合` |

## References

- 來源：`npm` / `PyPI` / `NuGet` / `pkg.go.dev` / `crates.io` + 標準庫
- 代理：`agents/openai.yaml`（與 SKILL.md 同目錄）
