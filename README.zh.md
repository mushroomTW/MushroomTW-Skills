# MushroomTW-Skills

[English](README.md) | **繁體中文**

四個可攜式 Agent Skill，涵蓋專案文件撰寫、相依決策與 SonarQube 品質流程。它們遵循開放的 Agent Skills 格式，可安裝到 Claude Code、Codex、Cursor、OpenCode 與其他相容的 agent；需要 SonarQube 的流程，仍要求 host 提供對應能力。

每個 skill 都是根目錄下一個獨立的 skill 資料夾，說明文件放在 `docs/`。

## Skill 一覽

### 通用

| Skill | 做什麼 | 說明文件 | 目錄 |
| --- | --- | --- | --- |
| `excellent-project-docs` | 依照 repository 的實際內容撰寫、改善、稽核或同步 `README.md` 與 GitHub 會讀取的隨附文件（`CONTRIBUTING`、`SECURITY`、`ARCHITECTURE`、`CHANGELOG`……）。隨附文件先提案再建立；無法追溯到檔案的敘述會被列為待補資訊，而不是寫成事實。 | [繁中](docs/excellent-project-docs.zh.md) ・ [EN](docs/excellent-project-docs.md) | `excellent-project-docs/` |
| `library-first` | 在你動手寫重試、驗證、快取、認證或日期處理之前，先強制搜尋該語言自己的生態系，並要求把「用套件還是自己寫」的理由講出來。 | [繁中](docs/library-first.zh.md) ・ [EN](docs/library-first.md) | `library-first/` |

### SonarQube 流程

| Skill | 做什麼 | 說明文件 | 目錄 |
| --- | --- | --- | --- |
| `local-sonarqube-setup` | 把專案指向本機 Docker SonarQube（`127.0.0.1:9000`），用專案原生工具產生 coverage、執行掃描並檢查 Quality Gate。token 讀自 `SONAR_TOKEN`，不進入檔案、參數、log 或任何回覆。 | [繁中](docs/local-sonarqube-setup.zh.md) ・ [EN](docs/local-sonarqube-setup.md) | `local-sonarqube-setup/` |
| `sonarqube-fix-all` | 分批處理 SonarQube 的發現，每批都先對建置驗證過才往下走。碰到 bytecode 操作、反射驅動與時序相依的程式碼會跳過並回報，而不是動手改寫。 | [繁中](docs/sonarqube-fix-all.zh.md) ・ [EN](docs/sonarqube-fix-all.md) | `sonarqube-fix-all/` |

這兩個 skill 都以**同一台機器上、用 Docker 建置的自架 SonarQube** 為目標（預設 `http://127.0.0.1:9000`，Community Build）。它們只負責連線，不負責啟動——叫用任一 skill 前請先把容器跑起來。不支援 SonarCloud。

`local-sonarqube-setup` 與 `sonarqube-fix-all` 設計上是接續使用：前者把專案接上並跑出第一份分析，後者批次修掉它回報的問題。

`sonarqube-fix-all` 僅限手動觸發：它在 frontmatter 聲明 `disable-model-invocation: true`，host 不會自行啟動。請以名稱叫用（`/sonarqube-fix-all`）。其餘三個依各自的 `description` 自動觸發。

## 設計依據

下列文獻支撐的是兩項設計決策，不是這四個 skill 的效果——後者沒有任何已發表的研究評估過。

| 設計決策 | 對應 Skill | 依據 |
| --- | --- | --- |
| 不寫任何無法由倉庫佐證的事實 | `excellent-project-docs` | F. Liu et al.，[Exploring and Evaluating Hallucinations in LLM-Powered Code Generation](https://arxiv.org/abs/2404.00971)，2024 preprint — 程式碼生成幻覺的分類法與 HalluCode 基準 |
| 實際搜尋生態系，而不是憑印象講出套件名 | `library-first` | Spracklen et al.，[We Have a Package for You!](https://www.usenix.org/conference/usenixsecurity25/presentation/spracklen)，USENIX Security 2025 — 57.6 萬份生成樣本中，19.7% 被引用的套件根本不存在 |

## 安裝

這裡每個目錄都是標準的 skill 資料夾。在倉庫根目錄可用 [`skills` CLI](https://github.com/vercel-labs/skills) 自動偵測相容 agent 並安裝全部四個 skill。第一次執行 `npx` 時可能需要連網下載 CLI：

```bash
npx skills add . --list
npx skills add . --all --global
```

若採手動安裝，請把單一 skill 目錄複製到 host 支援的位置。下表是常見路徑，不是所有 runtime 的完整清單：

| 路徑 | 個人層級 | 專案層級 |
| --- | --- | --- |
| 通用 Agent Skills fallback | `~/.agents/skills/<skill-name>/` | `<repo>/.agents/skills/<skill-name>/` |
| Claude Code | `~/.claude/skills/` | `<repo>/.claude/skills/` |
| Codex | `~/.codex/skills/` | `<repo>/.agents/skills/` |
| 其他相容 agent | 使用 CLI 自動偵測，或查閱 host 的 skills 目錄文件 | 使用 CLI 自動偵測，或查閱 host 的 skills 目錄文件 |

```bash
cp -r <skill-name> <host-skills-directory>/<skill-name>
```

> [!NOTE]
> 若 host 只在 session 啟動時載入 skill，安裝後請重新載入或開啟新 session。可用 `npx skills list` 檢查 CLI 辨識到的安裝路徑。

若只想把單一 skill 當成參考資料使用，不安裝到 host：

```bash
npx skills use . --skill <skill-name>
```

`local-sonarqube-setup` 另外要求主機已有相容 scanner 與 `SONAR_TOKEN` 環境變數，它不負責安裝 scanner。目前 SonarScanner for .NET 不支援此環境變數路徑，因此 skill 會停止，不把 token 暴露於參數或檔案。`sonarqube-fix-all` 需要已設定好的 SonarQube MCP 連線，同樣讀取 `SONAR_TOKEN`。

四個都附了給 Codex 用的 `agents/openai.yaml`；除了這個檔案之外，`library-first` 只有單一個 `SKILL.md`，沒有其他輔助檔案。

## 倉庫結構

```txt
MushroomTW-Skills/
├── README.md / README.zh.md      ← 本總覽（英 / 繁中）
├── LICENSE                       （MIT）
│
├── docs/                         ← 各 skill 說明文件（英文預設，.zh.md 為繁中）
│   ├── excellent-project-docs.md / .zh.md
│   ├── library-first.md / .zh.md
│   ├── local-sonarqube-setup.md / .zh.md
│   └── sonarqube-fix-all.md / .zh.md
│
├── excellent-project-docs/       SKILL.md + agents/ references/ scripts/
├── library-first/                SKILL.md + agents/
├── local-sonarqube-setup/        SKILL.md + agents/ reference/
└── sonarqube-fix-all/            SKILL.md + agents/
```

各子專案內都沒有 `README.md`，說明文件已全數集中到 `docs/`。

## 授權

MIT，見 [LICENSE](LICENSE)。這個檔案放在集合根目錄，安裝時不會被複製進 skill 目錄，因此單獨安裝出去的 skill 本身不帶授權文字。
