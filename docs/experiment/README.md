# 實驗：excellent-readme 在四個模型上的效果

同一個受測專案、同一句提示，讓 Claude 的四個模型各寫兩份 README——一份遵循本 skill、一份明確禁止讀取任何 skill 內容——共 8 份輸出，全部原封不動收錄在本目錄。實驗於 2026-08-25 執行。

## 受測專案

一個未公開的網頁狼人殺遊戲（FastAPI + WebSocket 後端、原生 JS 前端、Google Gemini 驅動 AI 玩家），約 1,300 行程式碼，**沒有 README、LICENSE、測試與 CI**。它天然帶有幾個文件陷阱：

| 檢驗點 | 程式碼中的正解 |
| --- | --- |
| 啟動方式 | `python backend/main.py`，port **8765**，後端直接伺服前端 |
| API 金鑰 | 硬編碼於 `backend/config.py`（佔位字串 `"API"`），**不是**環境變數；`.gitignore` 卻只排除 `.env` |
| LLM | `gemma-4-26b-a4b-it` 主用、`gemini-3.1-flash-lite` 備用，含重試與降級 |
| 遊戲事實 | 6–12 人；狼人／村民／預言家／女巫；上帝模式旁觀 |
| 誠實度 | 無 LICENSE、無測試——只能揭露，不能虛構 |
| 語言判斷 | UI 與註解全為繁體中文 |

> [!NOTE]
> 受測專案的原始碼不在本 repo 中，因此本實驗無法由讀者完整復現；收錄的 8 份輸出為逐字原件，其中的相對連結（如 `backend/config.py`）指向原專案，在本目錄中無法解析。

## 方法

- 兩組條件使用相同提示，唯一差異：skill 組被要求先讀 `SKILL.md` 並遵循（含 references）；對照組被明確禁止讀取任何 skill 內容。
- 對照組必須「明確禁止」是實驗過程的一個發現：初次試跑時，僅拿到「幫這個專案寫 README」的代理**自動觸發了本 skill**——觸發條件即是如此運作的。
- 每格僅運行一次（n=1），數字會受取樣波動影響；「檢查行為」以代理自述為準，但關鍵事實（port、config、授權段、validator 結果）由主持者實際讀檔核對。
- 事後逐一稽核了全部十個代理的完整工具呼叫紀錄：五個對照組讀取 skill 檔案的次數為 **0**、Skill 工具呼叫為 **0**；五個 skill 組都有實際讀取 `SKILL.md` 與 references 的紀錄（每組 3–10 次）。對照組的系統提示中仍含 skill 的一行描述（環境無法移除），但內容層面的汙染已由紀錄排除。

## 輸出一覽

| 模型 | 遵循 skill | 無 skill 對照 |
| --- | --- | --- |
| Haiku 4.5 | [haiku-skill.md](haiku-skill.md) | [haiku-baseline.md](haiku-baseline.md) |
| Sonnet 5 | [sonnet-skill.md](sonnet-skill.md) | [sonnet-baseline.md](sonnet-baseline.md) |
| Opus 5 | [opus-skill.md](opus-skill.md) | [opus-baseline.md](opus-baseline.md) |
| Fable 5 | [fable-skill.md](fable-skill.md) | [fable-baseline.md](fable-baseline.md) |

## 客觀結果

| 模型／條件 | 行數 | 耗時 | tokens | 工具呼叫 | 主動執行的檢查 |
| --- | --- | --- | --- | --- | --- |
| Haiku skill | 206 | 178s | 56k | 20 | validator、數值核對 |
| Haiku 對照 | 232 | 93s | 46k | 8 | 無 |
| Sonnet skill | 188 | 747s | 160k | 39 | py_compile、錨點逐一核對、validator×2、grep 證實無 .env 機制 |
| Sonnet 對照 | 165 | 390s | 116k | 16 | 無 |
| Opus skill | 236 | 508s | 117k | 29 | validator、錨點腳本、py_compile、badge URL 逐一驗證、config 七項比對 |
| Opus 對照 | 292 | 298s | 101k | 21 | 無 |
| Fable skill | 172 | 469s | 109k | 28 | validator×2、py_compile、終審自我修正一處過度宣稱 |
| Fable 對照 | 151 | 277s | 85k | 20 | 無 |

四個模型（含對照組）在語言判斷（繁中）、port 8765、`config.py` 金鑰位置與模型名稱上全數正確，顯示這一代模型的事實底子已經很強；差異出現在別處。

## 每個模型的縱向差異

**Haiku 4.5 — skill 影響最大，而且是雙向的。** 對照組的安裝指令 `pip install fastapi uvicorn` 漏了三個依賴（照做必定 ImportError）、把暫存目錄名當專案標題、開場是行銷語、快速開始排在第 11 個標題；skill 版全部修正（`pip install -r requirements.txt`、從 `index.html` 取得真實遊戲名、快速開始升至第 4 個標題），並跑了檢查。但 skill 治不了小模型的模板慣性：對照組對授權**沉默**，skill 版反而**虛構**了「授權條款請參考 LICENSE 檔案」——整場實驗唯一的虛構事實，來自「補完章節」的衝動。

**Sonnet 5 — 事實全對，skill 改變結構與交付紀律。** 對照組把技術架構排在快速開始之前（本 skill framework 明列的反模式）、「未附 LICENSE」一行帶過；skill 版是完整漏斗結構、獨立授權段＋`TODO:`＋SPDX 建議，並執行了四類檢查。代價也最大（+357 秒、+44k tokens）。

**Opus 5 — 底子最強，skill 增量最小但方向清楚。** 對照組本身就抓到了金鑰不受 `.gitignore` 保護與 port 雙處寫死，甚至比 skill 版長 56 行；skill 帶來的是紀律：授權與貢獻管道用明確 `TODO:`、badge 附來源註記防漂移、六類檢查，以及範圍紀律——對照組跑去建議把程式改成讀環境變數（改碼建議），skill 版守住「記錄現狀」。skill 版也因 right-sized 原則反而更短。

**Fable 5 — 與 Opus 同型。** 對照組事實全對、指令可跑，但無目錄、無 badge、授權隻字未提、零檢查；skill 版補上目錄與統一樣式 badge、授權 `TODO:` 加警語、規則細節（60 秒逾時、平票流局），並在終審自我修正了一處過度宣稱。

## 結論

1. **skill 對小模型修正的是硬錯誤**（裝不齊的依賴、錯誤標題、結構倒置），但無法根治其虛構慣性——甚至可能誘發模板式的「補完」虛構。
2. **skill 對前沿模型修正的不是事實**（它們自己就對），**而是交付紀律**：驗證行為、誠實揭露的格式化（`TODO:` 標記 vs 一行帶過 vs 沉默）、漏斗結構、badge 防漂移、右尺寸。
3. 全部 8 次運行中最穩定的訊號：**四個 skill 版全數主動執行了檢查；四個對照組一個檢查都沒跑。**
4. 成本：skill 平均多花約四到九成時間、約兩成 tokens。
5. 附帶發現一個 skill 檢查器的盲區：Haiku 那句純文字的「請參考 LICENSE 檔案」不是連結，`validate_readme.py` 的本機連結檢查抓不到。

## 限制

- 每格 n=1，無統計效力；模型輸出存在取樣波動。
- 受測專案不公開，讀者無法完整復現；能檢視的是輸出原件與本報告的核對紀錄。
- 「檢查行為」欄位以代理自述為主，主持者僅實測核對了關鍵事實與 validator 結果。
