# Audit Protocol — Evidence, Scoring & Reporting

> 單一協定文件，合併原 `evidence-and-reporting.md` + `scoring-rubric.md` + `report-template.md`。
> `SKILL.md` 只作骨架引用，此文件為人類可讀的完整規則；權威欄位仍以 `bug-audit-evidence.schema.json` 與 `validate_bug_audit.py` 為準。

## 目錄

- [1. 佐證模型](#1-佐證模型)
- [2. 去重與衝突](#2-去重與衝突)
- [3. 評分與校準](#3-評分與校準)
- [4. 報告版型](#4-報告版型)
- [5. 完成關卡](#5-完成關卡)

---

## 1. 佐證模型

### 1.1 Finding 類型

| 類型 | 門檻 |
|---|---|
| `defect` | 行為已證明違反可見契約或產生錯誤結果。必須具備 `expected_behavior` / `actual_behavior`、佐證 `observed` 或 `reproduced`、信心度 ≥7、狀態 `confirmed` / `cross-confirmed` |
| `risk` | 已直接證明存在控制缺口或具體失效條件，但錯誤結果尚未完整觸發。必須具備非空 `preconditions` 與 `verification`；有重大替代解釋時用 `needs-verification` |
| `quality-debt` | 尚未證明會造成執行期錯誤的工程問題。僅 Comprehensive 允許；Rapid 禁止 |

掃描器命中、TODO、複雜度、搜尋結果、code smell 僅為候選訊號，建 finding 前必須讀實作、主要呼叫端與被呼叫端、設定與測試。

### 1.2 佐證種類與信心度

| 佐證 | 意義 |
|---|---|
| `observed` | 由目前工作樹的程式碼與資料流直接確認 |
| `reproduced` | 由儲存庫既有設定的測試/建置/lint/analyzer 實際執行後確認 |
| `inferred` | 多項事實吻合但仍有具名執行期條件未驗證；`defect` 永不適用 |
| `cross-confirmed` | 兩個獨立來源確認；獨立審查最多將信心度 +1 |

| 信心度 | 處理 |
|---|---|
| 9–10、7–8 | 可發表 |
| 5–6 | 僅能以 `needs-verification` 發表 |
| 3–4 | 只留於 evidence，不發表不計分 |
| 1–2 | 直接捨棄 |

嚴重度（`High/Medium/Low`）表達影響，信心度表達確定性，兩者不可互換。Evidence 存 `High/Medium/Low`，報告渲染為 `🔴 High / 🟡 Medium / 🟢 Low`。

公開 findings 排序：`defect → risk → quality-debt`；同類型內 `High → Medium → Low`；再依信心度遞減、ID 排序。

---

## 2. 去重與衝突

- 以 **根本原因與修復方式** 去重，非行號。指紋正規化為小寫英文 `category|root-cause|primary-symbol`。
- 同一根因即使出現在多檔，算一項；除非每次扣分有獨立且已證明的影響，否則不重複扣分。
- 每個 finding 僅扣一個維度（由 `category` 決定，見 §3.3），validator 強制執行。
- Multi-agent：主代理讀相關原始碼與測試解決分歧；仍有衝突則降信心度並用 `needs-verification`，永不平均分數。

---

## 3. 評分與校準

### 3.1 模式差異

|  | Rapid | Comprehensive |
|---|---|---|
| 分數/評級/維度 | 無 | 有，7 維度 0–100 |
| 信心度上限 | Medium | High |

Rapid 風險校準：
- **High**：存在至少一項已確認 High `defect`/`risk`，或多項已確認 Medium 形成系統性重大風險
- **Medium**：無已確認 High，但存在公開 High/Medium `defect`/`risk`，或重大未知需升級
- **Low**：無公開 High/Medium `defect`/`risk`，選定核心/高風險流程已追蹤，無重大未知

Rapid 信心度永不為 High；`provisional` 的 Rapid 必須為 Low。

### 3.2 七維度與權重

| 維度 | ID | 權重 |
|---|---|---:|
| 正確性與可靠性 | `correctness` | 30 |
| 安全性與資料處理 | `security` | 25 |
| 效能與可運維性 | `performance_operability` | 15 |
| 測試與驗證 | `testing` | 10 |
| 架構與可維護性 | `architecture` | 10 |
| 可讀性與一致性 | `readability` | 5 |
| 死碼整潔度 | `dead_code` | 5 |

成熟度 0–5：

| 等級 | 錨點 |
|---:|---|
| 5 | 可驗證控制一致涵蓋核心風險，無實質缺口 |
| 4 | 大致健全，僅局部 Low 問題 |
| 3 | 堪用，但有明確控制/覆蓋缺口需近期處理 |
| 2 | 多處缺口或一項已確認 High 構成實質風險 |
| 1 | 系統性弱點使運作或修改難以信任 |
| 0 | 已確認重大失效/資料或安全危害，或該維度實質缺席 |

算式：無 N/A 時 `total = Σ(weight × level ÷ 5)`；有 N/A 時 `total = 100 × Σ(適用分數) ÷ Σ(適用權重)`，half-up 四捨五入。N/A 僅當專案客觀上無相關行為或風險，缺實作/測試/文件屬低分非豁免。

### 3.3  caps 與歸屬

- 一項已確認 High → 該維度上限 level 2；多項已確認 High → 上限 1；核心流程上已確認 Medium → 上限 3（`validate_bug_audit.py` 強制）。
- 為避免 double-deduct，`category → dimension` 映射固定：`correctness→correctness`、`security→security`、`testing→testing`、`architecture→architecture`、`readability→readability`、`dead-code→dead_code`、`performance/operability→performance_operability`。

### 3.4 總分與評級

| 分數 | 評級 |
|---|---|
| 90–100 | Strong engineering quality |
| 75–89 | Generally good |
| 60–74 | Material technical debt |
| 40–59 | Elevated engineering risk |
| 0–39 | Major engineering risk |

分數為兩個位數的判斷結果，非量測值；跨儲存庫不可比，跨次執行約一個帶寬內的波動屬雜訊。 caps 使「嚴重度判定」最牽動總分，應以影響校準而非以預期總分反推。

Confidence 要求（Comprehensive）：
- **High**：100% coverage、所有核心/高風險流程 traced、至少一項既有檢查 passed、非 provisional、無結論級不可見邊界
- **Medium**：≥90% coverage 且核心流程 traced，或 100% 但有不可驗證的外部/執行期邊界
- **High/Medium 皆額外要求** 100% core-path coverage（所有 `core`/`high` 檔案為 `read`）

### 3.5 維度檢查清單

- **Correctness**：契約、邊界、部分失效、逾時/重試/取消、狀態轉換/交易/一致性/併發、資源釋放
- **Security**：外部輸入、路徑/查詢/序列化、授權、憑證/個資/日誌、injection/SSRF/反序列化/加解密/預設值
- **Performance & Operability**：無界工作、N+1、阻塞 I/O、熱路徑配置、資源限制/背壓、可觀測性/啟動/部署韌性
- **Testing**：核心/失效/邊界/安全行為的可觀測斷言、mock、風險適配的整合證據
- **Architecture**：責任邊界、依賴方向/循環、重複、全域狀態、錯誤契約、單一真實來源
- **Readability**：命名/組織/控制流/註解/魔術值/專案慣例（不把純格式偏好膨脹為 finding）
- **Dead code**：不可達碼、未用符號/依賴、過時路徑/旗標/遷移/相容層（搜尋不到僅為候選訊號）

---

## 4. 報告版型

### 4.1 共通規則

- 兩種模式皆 **恰好四個二級標題**；`execution.provisional == true` 時標題下緊接 `**Provisional report**`。
- Executive Summary 必須包含 `Core-path coverage` 行：`critical_read_files / critical_in_scope_files` 與百分比。
- Finding 以 `severity` 存 `High/Medium/Low`，報告渲染為 `🔴 High / 🟡 Medium / 🟢 Low`，validator 校驗一致。
- 不含逐檔清冊、指紋、完整 evidence、原始指令輸出或附錄；不把 evidence JSON 當附錄重抄。
- 本地 Markdown 連結須可解析；報告位於 `.docs/`，指向根檔用 `../`，例如 `[src/main.py](../src/main.py:1)`。

### 4.2 Finding 表格與詳情

章節 3 開頭為單一表格：

```markdown
| ID | Type | Severity / confidence | Location | Problem and impact | Recommendation |
| --- | --- | --- | --- | --- | --- |
```

排序規則見 §1.2。**每個公開 finding 恰出現一次**；High/Medium 追加 `### FINDING-ID: Summary` 詳情塊（含 Location、≤3 條 Evidence、Impact、Recommendation、Verification），Low 不展開。無公開 findings 時寫 `No reportable findings were identified within the reviewed scope.`。

### 4.3 Rapid 版型

```markdown
# Repository Bug Audit — Rapid
## 1. Executive Summary
| Metric | Result |
| --- | --- |
| Risk signal | High / Medium / Low |
| Assessment confidence | Medium / Low + 原因 |
| Review coverage | 已讀 / 非排除、百分比與邊界 |
| Core-path coverage | 核心+高風險 已讀 / 範圍內、百分比 |
| Verification summary | 主要 passed/failed/not_run/unavailable |
明確聲明 Rapid 不評分。
## 2. Review Coverage and Bug Surfaces
## 3. Prioritized Findings
## 4. Limitations（≤5 條結論級缺口） 
```

### 4.4 Comprehensive 版型

```markdown
# Repository Bug Audit
## 1. Executive Summary
| Metric | Result |
| --- | --- |
| Total score | 0–100 + rating；有 N/A 時揭露重正規化 |
| Overall risk | High / Medium / Low |
| Assessment confidence | High / Medium / Low + 原因 |
| File coverage | 已讀 / 範圍內、百分比 |
| Core-path coverage | 核心+高風險 已讀 / 範圍內、百分比 |
| Verification summary | 主要 passed/failed/not_run/unavailable |
## 2. Risk-Weighted Quality Scores
| Dimension | Weight | Level | Score | Primary rationale |
| --- | ---: | ---: | ---: | --- |
每維度 rationale ≤2 句，僅引用相關 finding IDs，不輸出 Compliance 表。
## 3. Prioritized Findings
## 4. Limitations（≤5 條）
```

---

## 5. 完成關卡

### 5.1 共通

- inventory 路徑唯一、相對路徑、檔案存在；`coverage` 與 `critical_*` 可由 inventory 重算
- 每個 finding `location` 指向實際存在檔案
- 至少一項在範圍內項目為 `core` 或 `high`
- 信心度 > Low 需 100% core-path coverage
- 每個已知核心/高風險流程有 trace 狀態
- finding 滿足類型/信心度/去重/排序；公開 Markdown 與 evidence 完全一致
- `limitations` 揭露結論級未知；報告與 evidence 檔名成對且不覆蓋；validator exit 0

### 5.2 Rapid 專屬

- 允許 `mapped`；不得輸出 `dimensions/total_score/rating`；信心度不超過 Medium；地圖/選定流程/最低 evidence 不完整時標 `provisional`

### 5.3 Comprehensive 專屬

- 非 provisional 時無 `mapped`（每項 `read` 或 `unreadable`）；所有已知核心/高風險流程 traced；完成 7 維度與總分；結論級邊界不完整時標 `provisional`
- 超預算時：**要麼** 切 Multi-agent 分工，**要麼** 縮至核心/最高風險路徑並標 `provisional`，每項未讀以 `mapped` + `reason` 記於 inventory，`limitations` 僅述後果不列檔名
- High 信心度需 100% coverage + traced + 非 provisional + 至少一項驗證 passed；Medium 需 ≥90% 且 traced

