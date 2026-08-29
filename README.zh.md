# MushroomTW-Skills

[English](README.md) | **繁體中文**

給 Claude Code 與 Codex 用的五個 agent skill，涵蓋 README 撰寫、相依決策、儲存庫稽核與 SonarQube 品質流程。

每個 skill 都是根目錄下一個獨立的 skill 資料夾，說明文件放在 `docs/`。

## Skill 一覽

| Skill | 做什麼 | 說明文件 | 目錄 |
| --- | --- | --- | --- |
| `excellent-readme` | 依照 repository 的實際內容撰寫、改善、稽核或同步 `README.md`。無法追溯到檔案的敘述會被列為待補資訊，而不是寫成事實。 | [繁中](docs/excellent-readme.zh.md) ・ [EN](docs/excellent-readme.md) | `excellent-readme/` |
| `library-first` | 在你動手寫重試、驗證、快取、認證或日期處理之前，先強制搜尋該語言自己的生態系，並要求把「用套件還是自己寫」的理由講出來。 | [繁中](docs/library-first.zh.md) ・ [EN](docs/library-first.md) | `library-first/` |
| `local-sonarqube-setup` | 把專案指向本機 Docker SonarQube（`127.0.0.1:9000`），用專案原生工具產生 coverage、執行掃描並檢查 Quality Gate。token 讀自 `SONARQUBE_TOKEN`，不進入檔案、log 或任何回覆。 | [繁中](docs/local-sonarqube-setup.zh.md) ・ [EN](docs/local-sonarqube-setup.md) | `local-sonarqube-setup/` |
| `repository-bug-audit` | 在把任何東西稱為缺陷之前，先讀過實作、它的呼叫端、設定與測試。交付一份 Markdown 報告搭配一份經機器檢查的佐證 JSON，Comprehensive 模式另有 0–100 風險分數。 | [繁中](docs/repository-bug-audit.zh.md) ・ [EN](docs/repository-bug-audit.md) | `repository-bug-audit/` |
| `sonarqube-fix-all` | 分批處理 SonarQube 的發現，每批都先對建置驗證過才往下走。碰到 bytecode 操作、反射驅動與時序相依的程式碼會跳過並回報，而不是動手改寫。 | [繁中](docs/sonarqube-fix-all.zh.md) ・ [EN](docs/sonarqube-fix-all.md) | `sonarqube-fix-all/` |

`local-sonarqube-setup` 與 `sonarqube-fix-all` 設計上是接續使用：前者把專案接上並跑出第一份分析，後者批次修掉它回報的問題。

## 安裝

這裡每個目錄都是標準的 skill 資料夾，複製到 host 的 skills 目錄即可：

| Host | 個人層級 | 專案層級 |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/` | `<repo>/.claude/skills/` |
| Codex | `~/.codex/skills/` | — |

```bash
cp -r excellent-readme       ~/.claude/skills/excellent-readme
cp -r library-first          ~/.claude/skills/library-first
cp -r local-sonarqube-setup  ~/.claude/skills/local-sonarqube-setup
cp -r repository-bug-audit   ~/.claude/skills/repository-bug-audit
cp -r sonarqube-fix-all      ~/.claude/skills/sonarqube-fix-all
```

> [!NOTE]
> 兩個 host 都在 session 啟動時讀取 skills 目錄，複製後請開啟新的 session。

`local-sonarqube-setup` 另外要求主機已有可執行的 `sonar-scanner` 與 `SONARQUBE_TOKEN` 環境變數，它不負責安裝 scanner。`sonarqube-fix-all` 需要一個已設定好的 SonarQube MCP 連線，並讀取 `SONAR_TOKEN`。

五個之中有四個附了給 Codex 用的 `agents/openai.yaml`；`library-first` 只有單一個 `SKILL.md`，沒有輔助檔案。

## 倉庫結構

```
MushroomTW-Skills/
├── README.md / README.zh.md      ← 本總覽（英 / 繁中）
├── LICENSE                       （MIT）
│
├── docs/                         ← 各 skill 說明文件（英文預設，.zh.md 為繁中）
│   ├── excellent-readme.md / .zh.md
│   ├── library-first.md / .zh.md
│   ├── local-sonarqube-setup.md / .zh.md
│   ├── repository-bug-audit.md / .zh.md
│   └── sonarqube-fix-all.md / .zh.md
│
├── excellent-readme/             SKILL.md + agents/ references/ scripts/
├── library-first/                SKILL.md
├── local-sonarqube-setup/        SKILL.md + agents/ reference/
├── repository-bug-audit/         SKILL.md + agents/ references/ scripts/
└── sonarqube-fix-all/            SKILL.md + agents/
```

各 skill 目錄只放 skill 本體。留在磁碟上的開發資產——三個 skill 旁的 `test-prompts.json` 與 `repository-bug-audit/tests/`——由根目錄唯一的 `.gitignore` 統一排除，不進版控；用 `cp -r` 安裝時它們仍會跟著 skill 一起被複製過去。

## 版控狀態

整個技能集由根目錄的單一 git repository 統一管理，各 skill 目錄不再各自帶 `.git`。原本每個 skill 都是獨立的本機 repository，這些歷史已用 `git subtree` 併入根倉庫，原始 commit 全數保留、仍可從 `git log` 查到。要注意併入前的 commit 記錄的是各子倉庫根目錄的路徑，所以 `git log -- <skill>/` 只會看到併入那一筆，要追某個 skill 的完整演進請看完整的 `git log`。

倉庫沒有設定 remote——這是只存在本機的副本。

各子專案內都沒有 `README.md`，說明文件已全數集中到 `docs/`。

## 授權

MIT，見 [LICENSE](LICENSE)。這個檔案放在集合根目錄，安裝時不會被複製進 skill 目錄，因此單獨安裝出去的 skill 本身不帶授權文字。
