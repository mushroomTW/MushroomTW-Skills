# MushroomTW-Skills

[English](README.md) | **繁體中文**

MushroomTW-Skills 是一組專為現代 AI Agent（Claude Code、Codex、Cursor、OpenCode 等相容開放 Agent Skills 規格的工具）打造的可攜式 Skill 集合，涵蓋**程式碼過度設計稽核**、**本機 SonarQube 品質流程自動化**以及 **RimWorld 模組開發與遊戲內測試**。

每個 Skill 均為獨立目錄，包含完整的提示詞規格、觸發規則與相關參考資料，詳細說明文件集中於 `docs/`。

---

## Skill 一覽

| Skill | 類別 | 觸發方式 | 核心摘要 | 說明文件 | 目錄 |
| --- | --- | --- | --- | --- | --- |
| `ponytail-audit-lite` | 通用稽核 | 手動叫用 (`/ponytail-audit-lite`) | 全專案過度設計掃描，列出可刪除、簡化或原生替代的程式碼清單，只回報不修改 | [繁中](docs/ponytail-audit-lite.zh.md) ・ [EN](docs/ponytail-audit-lite.md) | `ponytail-audit-lite/` |
| `local-sonarqube-setup` | 品質流程 | 自然語言描述自動觸發 | 指向本機 Docker SonarQube，自動產出覆蓋率、執行掃描並查驗 Quality Gate，嚴格防範 Token 外洩 | [繁中](docs/local-sonarqube-setup.zh.md) ・ [EN](docs/local-sonarqube-setup.md) | `local-sonarqube-setup/` |
| `rimtest-redux-integrate` | RimWorld 開發 | 自然語言描述自動觸發 | 建立 RimTest Redux 遊戲內整合測試，利用 Harmony reverse patch 作對照組並處理時序延遲 | [繁中](docs/rimtest-redux-integrate.zh.md) ・ [EN](docs/rimtest-redux-integrate.md) | `rimtest-redux-integrate/` |
| `rimworld-devtools` | RimWorld 開發 | 自然語言描述自動觸發 | 整合 SmashPhil DevTools 進行遊戲內即時測試、Test Plan 規劃、結果判讀與 Benchmark | [繁中](docs/rimworld-devtools.zh.md) ・ [EN](docs/rimworld-devtools.md) | `rimworld-devtools/` |
| `rimworld-smashtools` | RimWorld 開發 | 自然語言描述自動觸發 | SmashTools 工具庫整合指引，涵蓋尋路、物件池、事件、UI/渲染、生命週期與打包 | [繁中](docs/rimworld-smashtools.zh.md) ・ [EN](docs/rimworld-smashtools.md) | `rimworld-smashtools/` |

---

## Skill 詳細介紹

### 通用程式碼稽核

#### `ponytail-audit-lite` — 過度設計與 YAGNI 稽核

- **核心定位**：快速診斷整個程式碼庫中「不必要的複雜度」，找出過度設計、未使用的抽象層與未遵循 YAGNI 原則的部分。
- **主要特點**：
  - **只報告、不動手（Report-only）**：執行一次性全域掃描，僅產出建議清單，絕不擅自修改任何程式碼。
  - **量化排序表格**：產出以預估減少行數由大到小排序的 Markdown 表格，清晰標示 `delete`（死代碼/未使用的彈性）、`yagni`（單一實作的過度抽象/單純轉發的 wrapper）、`stdlib`（重造標準函式庫輪子）、`native`（平台已有現成功能）及 `shrink`（相同邏輯的精簡寫法）。
  - **排除雜訊**：略過第三方依賴（`node_modules`、`vendor` 等）、建置產物、自動生成程式碼與受 `.gitignore` 排除之項目；專注於複雜度稽核，不發散到一般 Bug、資安或效能問題。
- **叫用機制**：**僅限手動觸發**。聲明了 `disable-model-invocation: true`（Claude Code）與 `policy.allow_implicit_invocation: false`（Codex），避免 Agent 在一般對話中擅自執行，請於對話中主動輸入 `/ponytail-audit-lite` 叫用。
- **來源**：改寫自 [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)（MIT 授權）。

---

### 靜態分析與代碼品質

#### `local-sonarqube-setup` — 本機 Docker SonarQube 自動化與安全掃描

- **核心定位**：協助將本地專案無縫對接到本機 Docker 執行的 SonarQube，自動化執行覆蓋率分析、代碼掃描與 Quality Gate 門禁驗證。
- **主要特點**：
  - **全自動工作流**：探測專案語言與建置工具（Maven、Gradle、.NET、npm 等）、生成專案原生覆蓋率報告、執行 Scanner、追蹤分析任務並驗證 Quality Gate 狀態。
  - **最高安全原則（Strict Token Safety）**：認證 Token 僅能讀取自環境變數 `SONAR_TOKEN`，絕不寫入任何設定檔、命令列參數、日誌或模型回覆中；若專案或 Scanner 機制可能洩漏 Token（如 .NET Scanner 無法從安全環境變數讀取），Skill 會主動中斷流程防範洩漏。
  - **真實門禁驗證**：絕不透過設定排除或停用規則來「偽造通過」，如未達標一律回報真實失敗狀態。
- **環境先決條件**：
  - 目標為本機 Docker 運行的 SonarQube（預設 `http://127.0.0.1:9000` Community Build），叫用前需已預先啟動該容器（Skill 不負責啟動容器）。
  - 不支援 SonarCloud。
  - 主機需已安裝對應語言的 Scanner 工具與相容的 Java 執行環境。

---

### RimWorld 模組開發

#### `rimtest-redux-integrate` — 遊戲內整合測試與 Harmony 對照驗證

- **核心定位**：為 RimWorld 模組建立於真實遊戲環境內運行的整合測試，攻克 headless 單元測試無法驗證 Harmony Patch 實際注入、執行時序衝突與遊戲資料載入狀態的痛點。
- **主要特點**：
  - **雙軌防護先行確認**：進入測試流程前，會先詢問開發者是否要採用 RimTest Redux，不強加流程。
  - **Companion 獨立測試 Mod**：測試程式碼獨立建置於伴隨測試 Mod 中，絕不打包進發布用模組。
  - **Harmony 原版對照組（Reverse Patch）**：透過 Harmony reverse patch 動態取得未被修改的原版方法作為 baseline，直接比對原版行為與 Mod 修改後的實際輸出。
  - **啟動時序同步**：自動等待 RimWorld 啟動階段的長任務（LongEvent）與非同步工作完畢，避免時序競爭造成假性失敗。
  - **規避引擎地雷**：內建針對 Mono 運行環境與 Harmony 的常見陷阱防護（如處理 `catch ... when` 導致的異常程式碼產生錯誤、`PatchCategory` 的崩潰防範等）。
- **環境先決條件**：RimWorld 1.6，需安裝 `brrainz.harmony`、`ilyvion.Laboratory` 與 `ilyvion.rimtestredux` 三個前置模組；測試組件目標為 net481。

#### `rimworld-devtools` — SmashPhil DevTools 遊戲內測試與診斷

- **核心定位**：當模組已選用或接入 SmashPhil DevTools 時，提供遊戲內即時測試執行、測試結果解讀、測試計畫規劃與效能基準測試支援。
- **主要特點**：
  - **多維度測試支援**：涵蓋 Smoke Test（冒煙測試）、測試計畫（Test Plan）制定、組件測試與遊戲內非拋出式斷言。
  - **智慧結果判讀**：即時解析遊戲日誌與測試結果，自動過濾無關雜訊，將失敗項目精準歸類為 Mod 本身問題、原版行為或環境相容性問題。
  - **效能分析**：支援遊戲內效能基準測試（Benchmark），診斷執行瓶頸與記憶體狀況。
- **環境先決條件**：需要 SmashPhil DevTools 建置、RimWorld 遊戲參考組件與 SDK，實際執行測試需啟動遊戲。

#### `rimworld-smashtools` — SmashTools 框架架構整合

- **核心定位**：全面支援 RimWorld 知名高效能工具庫 SmashTools 的整合開發，提供完整 API 功能導引、相容性處理與模組發布流程。
- **主要特點**：
  - **全方位功能導引**：涵蓋 SmashTools 核心基礎設施，包含原生集合擴充、高效物件池（Object Pooling）、工作與執行緒調度（Job/Threading Dispatching）、多格大型實體尋路（Multi-cell Pathfinding）、遊戲事件、UI/視窗與自訂渲染、資料持久化（XML/Data）、動畫曲線、快取與 Profiling。
  - **生命週期與初始化**：確保模組在載入階段各階段（靜態建構子、Mod 實例化、遊戲啟動）的正確初始化順序與相容性檢查。
  - **打包與發布驗證**：指導多版本相容性建置、相依組件隔離、發布包裝與執行期依賴驗證。

---

## 倉庫結構

```txt
MushroomTW-Skills/
├── README.md / README.zh.md      ← 本總覽（英 / 繁中）
├── LICENSE                       （MIT）
│
├── docs/                         ← 各 skill 完整說明文件（.md 為英文，.zh.md 為繁中）
│   ├── ponytail-audit-lite.md / .zh.md
│   ├── local-sonarqube-setup.md / .zh.md
│   ├── rimtest-redux-integrate.md / .zh.md
│   ├── rimworld-devtools.md / .zh.md
│   └── rimworld-smashtools.md / .zh.md
│
├── ponytail-audit-lite/          SKILL.md + agents/ LICENSE（上游 MIT）
├── local-sonarqube-setup/        SKILL.md + agents/ reference/
├── rimtest-redux-integrate/      SKILL.md + agents/ references/ LICENSE（上游 MIT）
├── rimworld-devtools/            SKILL.md + agents/ references/
└── rimworld-smashtools/          SKILL.md + agents/ references/ LICENSE（上游 MIT）
```

各子專案內未重複放置 `README.md`，完整說明文件已全數統一集中於 `docs/`。

---

## 授權

專案採用 [MIT License](LICENSE)。

部分 Skill 包含源自上游專案的實作與獨立授權條款：

- `ponytail-audit-lite`：改編自 [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)（MIT License，包含於該目錄中）
- `rimtest-redux-integrate`：包含 RimTest Redux 相關參考與 API 改編（MIT License，包含於該目錄中）
- `rimworld-smashtools`：包含 SmashTools 相關參考與 API 規格（MIT License，包含於該目錄中）
