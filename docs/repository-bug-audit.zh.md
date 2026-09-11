# Repository Bug Audit

[English](repository-bug-audit.md) | **繁體中文**

> 本文件位於 `docs/`。文中的相對路徑與指令以專案目錄 `repository-bug-audit/` 為基準。

一個以佐證為導向的 agent skill，針對整個儲存庫進行缺陷探勘與工程風險評估。它先找出實質缺陷，再於 Comprehensive 模式下評估更廣泛的工程品質，並產出一個風險加權的 0–100 分數。

這個 skill 對「什麼才算一項發現」刻意嚴格。掃描器命中、TODO、複雜度指標或搜尋結果都只是**訊號**，不是發現。任何內容被發表之前，都必須先讀過實作本身、它的主要呼叫端與被呼叫端、相關設定與測試。每一項發現都必須具備明確位置、直接佐證、影響、信心度、修復方向與驗證方式，整份紀錄在交付前還會經過機器檢查。

以一般 skill 資料夾形式提供，適用於任何相容的 host（Claude Code、Codex、OpenCode、Claude Apps 等）。

## 產出內容

每次執行只會在被稽核的儲存庫中留下一個檔案：

- 一份給人閱讀的**精簡 Markdown 報告** —— 這是唯一交付的產出。

報告背後，技能仍會建立一份機器可讀的佐證紀錄（檔案清冊、已追蹤流程、實際執行的檢查、所有發現、限制，以及 Comprehensive 模式的各構面分數），驗證器在交付前用它反向核對報告。那份佐證檔是驗證的輸入而非產出：跑完即刪，Markdown 也不會把它當附錄再抄一遍。

## 稽核模式

| | Rapid（快速） | Comprehensive（完整） |
| --- | --- | --- |
| 覆蓋範圍 | 對整個儲存庫建立地圖，讀取核心與最高風險路徑 | 讀取每一個納入範圍的檔案 |
| 清冊狀態 | `read`、`mapped`、`excluded`、`unreadable` | 僅 Provisional 報告可用 `mapped` |
| 發現類型 | `defect`、`risk` | `defect`、`risk`、`quality-debt` |
| 品質分數 | 不評分 | 七個構面、0–100 分並附評級 |
| 信心度上限 | Medium | High |

Rapid 回答的是「快速看一下，有沒有我該知道的缺陷？」；Comprehensive 回答的是「這個程式碼庫的健康程度如何，分數是多少？」。Rapid 永遠不評分 —— 用不完整的覆蓋率給出分數，會誤導別人以為檢查得比實際更徹底。

Comprehensive 模式會依納入範圍的檔案數與執行預算估算閱讀成本；當整個範圍無法在預算內讀完時，它必須選擇以多代理分工，或縮小到核心與最高風險路徑、將報告標記為 Provisional，並把每一個未讀檔案以 `mapped` 狀態連同原因記入清冊。清冊本身就是未讀檔案清單，覆蓋率會自動下降，`limitations` 則負責說明後果，而不是列出檔名。

## 執行模式

- **Standard（單一代理）** —— 由主代理獨立完成整份稽核。
- **Multi-agent partitioned（多代理分工）** —— 主代理切分範圍交給獨立審查者，再自行整合佐證並驗證跨邊界結論。每一項候選 High 發現都會交給**未被告知原始結論**的代理進行交叉審查，讓確認來自獨立判斷，而不是對既有結論的附和。

多代理模式不會放寬覆蓋率、隱私、驗證或唯讀要求。若目前平台無法提供獨立代理，skill 會明確說明並請你改用 Standard，而不是默默降級 —— 佐證 JSON 中的 `execution.review_mode` 是對「稽核實際如何執行」的事實陳述。

## 安裝

請在倉庫根目錄讓 `skills` CLI 自動偵測相容 agent，並安裝此 skill：

```bash
npx skills add . --skill repository-bug-audit
```

若要安裝到個人層級，請加上 `--global`；未加時為專案層級。若採手動安裝，請把 `repository-bug-audit/` 複製到 host 文件指定的 skills 目錄，不要假設特定 runtime 路徑。

Claude Apps：上傳本倉庫（或壓縮檔）作為 skill。Claude Apps 無子代理機制，Multi-agent 分工不可用，skill 會請你改選 Standard。

> [!NOTE]
> 第一次執行 `npx` 可能會下載 CLI。若 host 只在 session 啟動時偵測 skill，安裝後請重新載入或重啟。

## 使用方式

請以名稱明確叫用 —— 此 skill 僅限手動觸發，即使請求聽起來相似也不會自動觸發。它在 frontmatter 聲明 `disable-model-invocation: true`，host 不會自行啟動它：

```text
/repository-bug-audit
```

這個 skill 是為整個儲存庫設計的，不適用於單一檔案、PR diff 或某個已知缺陷：

接著 skill 會請你選擇稽核模式與執行模式。在 Claude Code 上，兩個問題會合併在同一次選擇介面中提出。若你在需求裡已經先講明其中一項，它就會跳過該問題。

之後它會建立儲存庫地圖、追蹤核心與高風險流程、只執行儲存庫既有設定的檢查、寫出兩份產出、執行驗證器，最後在對話中回覆可點擊的連結與極簡摘要，而不會把產出內容整篇貼進對話。

## 產出檔案

| 模式 | 報告 |
| --- | --- |
| Rapid | `.docs/repository-bug-audit-rapid-report.md` |
| Comprehensive | `.docs/repository-bug-audit-report.md` |

報告會寫入被稽核儲存庫的 `.docs/` 目錄；若該目錄不存在則會建立。佐證檔只在驗證器執行期間以 `<report-stem>.evidence.json` 的形式放在報告旁邊——驗證器要求這個檔名與 `.docs/` 上層目錄——跑完就移除。

若預設路徑已存在，報告會加上本地時間戳記，例如 `repository-bug-audit-report-20260806-153000.md`。既有檔案永遠不會被覆寫，因此重新稽核不會摧毀先前的報告。

兩種報告版型都固定四個章節。Rapid 為：執行摘要、審查覆蓋與缺陷面、優先發現、限制；Comprehensive 則把第二節換成「風險加權品質分數」。High 與 Medium 發現會有詳細區塊，Low 發現只留在表格中。每一列都標示佐證種類，執行摘要另外列出佐證組成，讓讀者能分辨哪些發現有實際執行的檢查背書、哪些只是讀出來的。詳見 [`audit-protocol.md`](../repository-bug-audit/references/audit-protocol.md)。

## 佐證模型

### 發現類型

| 類型 | 必須達到的門檻 |
| --- | --- |
| `defect`（缺陷） | 已證明行為違反可見契約或產生錯誤結果。必須具備 `expected_behavior`、`actual_behavior`、`observed` 或 `reproduced` 佐證、信心度 ≥ 7，且狀態為 `confirmed`／`cross-confirmed`。 |
| `risk`（風險） | 已直接支持存在控制缺口或具體失效條件，但錯誤結果尚未被完整觸發驗證。必須具備非空的前提條件與驗證方式。 |
| `quality-debt`（品質債） | 尚未證明會造成執行期行為錯誤的工程問題。僅限 Comprehensive 模式。 |

### 佐證種類

- `observed` —— 直接由目前工作目錄中的程式碼與資料流確認。
- `reproduced` —— 由儲存庫既有設定的檢查**實際執行**後確認。
- `inferred` —— 多項事實彼此吻合，但仍有一個具名的執行期條件未經驗證。`defect` 永不適用。
- `cross-confirmed` —— 這是 `status` 值而非佐證種類：由兩個獨立來源確認，其中至少一個必須來自審查代理之外（實際執行的檢查、測試、外部規格）。兩個代理讀同一棵原始碼樹共用同一組先驗，不算獨立來源；只有前一類來源才能把信心度提高，且最多一分。

### 信心度分級

嚴重度表達的是影響，信心度表達的是佐證確定性，兩者絕不可互相代換。

| 信心度 | 處理方式 |
| --- | --- |
| 9–10、7–8 | 可發表 |
| 5–6 | 僅能以 `needs-verification` 發表 |
| 3–4 | 只留在佐證檔中，不發表也不計分 |
| 1–2 | 直接捨棄 |

發現以「根本原因與修復方式」去重，而非以行號去重。因此同一個底層缺陷即使出現在六個檔案中，仍算一項發現；除非每次扣分都有各自獨立且已證明的影響，否則不會重複扣分。

完整協定：[`audit-protocol.md`](../repository-bug-audit/references/audit-protocol.md)。欄位層級的權威定義：[`bug-audit-evidence.schema.json`](../repository-bug-audit/references/bug-audit-evidence.schema.json)。

## 評分機制（Comprehensive 模式）

每個構面先給 0–5 的成熟度等級，再換算成加權貢獻。

| 構面 | ID | 權重 |
| --- | --- | ---: |
| 正確性與可靠性 | `correctness` | 30 |
| 安全性與資料處理 | `security` | 25 |
| 效能與可運維性 | `performance_operability` | 15 |
| 測試與驗證 | `testing` | 10 |
| 架構與可維護性 | `architecture` | 10 |
| 可讀性與一致性 | `readability` | 5 |
| 死碼整潔度 | `dead_code` | 5 |

沒有 N/A 構面時，`總分 = Σ(權重 × 等級 ÷ 5)`。若有 N/A 構面，則重新正規化為 `100 × Σ(適用構面分數) ÷ Σ(適用構面權重)`，最後以 half-up 方式四捨五入。

只有在專案客觀上不存在相關行為或風險時，構面才可標記為 N/A。缺少實作、測試或文件屬於「等級低」，不是豁免理由。

| 等級 | 成熟度錨點 |
| ---: | --- |
| 5 | 可驗證的控制措施一致涵蓋核心風險，未發現實質缺口 |
| 4 | 大致健全，僅有局部性的 Low 問題 |
| 3 | 堪用，但有明確的控制或覆蓋缺口需近期處理 |
| 2 | 多處缺口，或一項已確認的 High，構成實質風險 |
| 1 | 系統性弱點，使運作或修改難以信任 |
| 0 | 已確認重大失效、資料或安全危害，或該構面實質缺席 |

已確認的發現會對其構面設上限：一項已確認 High 將該構面上限壓到等級 2，多項已確認 High 壓到等級 1，核心流程上的已確認 Medium 則壓到等級 3。這些上限由驗證器強制執行 —— 這正是防止「明知有嚴重缺陷卻寫出漂亮分數」的機制。

| 分數 | 評級 |
| --- | --- |
| 90–100 | 工程品質優良 |
| 75–89 | 大致良好 |
| 60–74 | 存在實質技術債 |
| 40–59 | 工程風險偏高 |
| 0–39 | 重大工程風險 |

完整評分準則：[`audit-protocol.md`](../repository-bug-audit/references/audit-protocol.md) §3。

## 驗證

隨附的驗證器會在交付前拿佐證紀錄反向核對報告。它讀寫檔案時都明確指定 UTF-8；`-X utf8` 只是讓主控台輸出中的非 ASCII 文字顯示正常。

```bash
python -X utf8 scripts/validate_bug_audit.py --evidence <evidence.json> --report <report.md>
```

| 結束代碼 | 意義 |
| ---: | --- |
| `0` | 報告與佐證通過所有結構與政策檢查 |
| `1` | 存在內容違規，必須修正 |
| `2` | 引數或檔案無法讀取 |

它會檢查 schema 一致性、檔名配對政策、由清冊重新計算的覆蓋率算術、發現類型與信心度規則、去重、標準排序、構面上限、分數與評級的計算、模式專屬禁令、公開 Markdown 發現與佐證的完全一致，以及本地連結是否可解析。

覆蓋率會被算兩次：一次涵蓋所有納入範圍的檔案，一次只算 `core` 與 `high` 風險層級。信心度要高於 Low，第二個數字必須是 100% —— 讀再多瑣碎檔案都無法抵銷一個未讀的核心檔案，而且摘要必須把這個數字寫出來。

它同時會把報告所在目錄的上層（即 `.docs/` 的父目錄）視為受稽核的程式樹，並拒絕任何沒有實際檔案支撐的 `inventory` 路徑或發現 `location` —— 這是結構驗證器唯一能直接抓到的捏造。當產出是在與其描述對象不同的位置驗證時，請加上 `--repo-root <path>`。

它**不會**證明某項發現為真，只證明這份紀錄內部一致。要排除其他可能的解釋，仍然得回去讀程式碼。

## 防護邊界

除了那兩份產出之外，此 skill 全程唯讀。它不會修改程式碼、設定、測試或外部系統；不會安裝分析器或相依套件；也不會在任何位置（包含暫存目錄）撰寫重現程式或測試探針。只有儲存庫既有設定的檢查才能產生 `reproduced` 佐證。

它以整個目前工作目錄為範圍，絕不使用 `git diff`、歷史紀錄或變更檔案清單 —— 因為只看近期變更的「儲存庫稽核」，其實只是掛錯名字的 diff 審查。祕密憑證、完整原始碼檔案、個人資料與非必要的原始指令輸出，都不會被寫進佐證檔。

## 目錄結構

```text
repository-bug-audit/                         # 本倉庫即 skill 本體
├── README.md                                 # 英文版說明
├── README_zh.md                              # 本文件（繁體中文版）
├── SKILL.md                                  # Skill 定義與稽核流程
├── agents/
│   └── openai.yaml                           # Codex skill 選單中繼資料
├── references/
│   ├── platform-adapters.md                  # 各平台能力對照
│   ├── audit-protocol.md                     # 佐證、評分與報告協定
│   └── bug-audit-evidence.schema.json        # 權威佐證 schema（v3.0）
├── scripts/
│   └── validate_bug_audit.py                 # 產出配對驗證器
└── tests/
    └── test_validate_bug_audit.py            # 驗證器測試
```

本倉庫根目錄即 skill — 直接複製整個資料夾即可安裝。

## 開發

驗證器需 `jsonschema`（`pip install jsonschema`）。已在 CPython 3.14 上驗證。

```bash
pip install jsonschema
python -X utf8 -m unittest discover -s tests -v
```

修改規則時，請讓三個真實來源保持同步：`references/bug-audit-evidence.schema.json` 定義欄位與列舉、`references/audit-protocol.md` 定義人類可讀的協定與評分算式、`scripts/validate_bug_audit.py` 強制執行前兩者，`tests/test_validate_bug_audit.py` 則把行為釘死。只寫在文字敘述、卻沒有被驗證器強制執行的規則，遲早會漂移。
