# 實驗：excellent-readme 在四個模型上的效果

本目錄收錄兩場實驗。兩場的設計相同——同一個受測專案、同一句提示，讓模型各寫兩份 README，一份遵循本 skill、一份明確禁止讀取任何 skill 內容——差別在受測專案：第一場用的是不公開的專案，第二場改用收錄在本 repo 內、任何人都能重跑的陷阱專案。

> [!IMPORTANT]
> 第一場實驗（狼人殺專案）的展品對應 skill 1.7.0，未涵蓋其後新增的章節。1.8.0 新增的 `Failure recovery` 與 `Never do these` 由第二場實驗（陷阱專案）涵蓋。

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
> 受測專案的原始碼不在本 repo 中，因此本實驗無法由讀者完整復現；收錄的輸出為逐字原件，其中的相對連結（如 `backend/config.py`）指向原專案，在本目錄中無法解析。

## 方法

- 兩組條件使用相同提示，唯一差異：skill 組被要求先讀 `SKILL.md` 並遵循（含 references）；對照組被明確禁止讀取任何 skill 內容。
- 對照組必須「明確禁止」是實驗過程的一個發現：初次試跑時，僅拿到「幫這個專案寫 README」的代理**自動觸發了本 skill**——觸發條件即是如此運作的。
- 每格僅運行一次（n=1），數字會受取樣波動影響；「檢查行為」以代理自述為準，但關鍵事實（port、config、授權段、validator 結果）由主持者實際讀檔核對。
- 事後逐一稽核了全部代理的完整工具呼叫紀錄：對照組讀取 skill 檔案的次數為 **0**、Skill 工具呼叫為 **0**；skill 組都有實際讀取 `SKILL.md` 與 references 的紀錄（每組 3–10 次）。對照組的系統提示中仍含 skill 的一行描述（環境無法移除），但內容層面的汙染已由紀錄排除。
- 對照組從未讀取 skill，其輸出不隨 skill 版本變動，因此在 skill 改版後不需重跑。

## 展品

| 模型 | 遵循 skill（v1.7.0） | 無 skill 對照 |
| --- | --- | --- |
| Haiku 4.5 | [haiku-skill-v2.md](haiku-skill-v2.md) · 184 行 | [haiku-baseline.md](haiku-baseline.md) · 232 行 |
| Sonnet 5 | [sonnet-skill-v2.md](sonnet-skill-v2.md) · 126 行 | [sonnet-baseline.md](sonnet-baseline.md) · 165 行 |
| Opus 5 | [opus-skill-v2.md](opus-skill-v2.md) · 171 行 | [opus-baseline.md](opus-baseline.md) · 292 行 |
| Fable 5 | [fable-skill-v2.md](fable-skill-v2.md) · 108 行 | [fable-baseline.md](fable-baseline.md) · 151 行 |

檔名保留 `-v2` 後綴是因為這批是重測輸出；第一批（1.2.0 時代）的 skill 組展品已移除，理由見下方沿革。

## 結果

主持者實檔核對四份 skill 組輸出：

| 模型 | 核對結果 |
| --- | --- |
| Haiku 4.5 | 授權平述缺席、0 個 `TODO:` 佔位 |
| Sonnet 5 | 實跑快速開始全程：venv、安裝、啟動伺服器、`/health` 回應驗證 |
| Opus 5 | 受眾判斷引用證據；開放問題（授權／貢獻管道）列給使用者而非猜測 |
| Fable 5 | 明確聲明受眾假設與依據；0 個 badge（新判準：沒有 badge 需要回答的問題） |

四份共通：validator 全過、`TODO:` 出現 **0** 次、badge **0** 個、授權段全數誠實平述、無貢獻客套段。

四個模型（含對照組）在語言判斷（繁中）、port 8765、`config.py` 金鑰位置與模型名稱上全數正確，顯示這一代模型的事實底子已經很強；差異出現在別處：

1. **skill 對小模型修正的是硬錯誤。** Haiku 對照組的安裝指令 `pip install fastapi uvicorn` 漏了三個依賴（照做必定 ImportError）、把暫存目錄名當專案標題、快速開始排在第 11 個標題；skill 版全部修正。
2. **skill 對前沿模型修正的不是事實，而是交付紀律。** Opus 與 Fable 的對照組事實本來就對——Opus 對照組甚至自行抓到金鑰不受 `.gitignore` 保護。skill 帶來的是驗證行為、缺口的誠實處理方式、漏斗結構與右尺寸（skill 版反而比對照組短 41–121 行）。
3. **最穩定的訊號：skill 組全數主動執行了檢查；對照組一個檢查都沒跑。**
4. **範圍紀律。** Opus 對照組跑去建議把程式改成讀環境變數（改碼建議），skill 版守住「記錄現狀」。

殘餘觀察：Sonnet 在未事先取得授權下執行了需要網路的 `pip install`。這個越界後來成為 1.7.1 的修補依據（明定裝依賴＝網路動作、無人可授權＝視為未授權）。

## 追加實驗：可復現的陷阱專案（1.8.0）

前兩次實驗的最大限制是受測專案不公開。這次改用一個**收錄在本 repo 內**的最小專案 [`fixture/`](fixture/)：一個 48 行的 CSV 欄位計數 CLI，純標準函式庫、無需安裝、無需網路即可執行。

`fixture/README.seed.md` 是**故意寫錯的**起始 README，埋了九個陷阱。復現時先把它複製成 `README.md`：

```bash
cd docs/experiment/fixture && cp README.seed.md README.md
```

再讓代理處理「請改善這個專案的 README」，兩組條件與前次相同（skill 組讀 SKILL.md；對照組明確禁止讀取任何 skill 內容）。

### 九個陷阱

| # | 陷阱 | 程式碼中的正解 |
| --- | --- | --- |
| 1 | 「blazing-fast, powerful and seamless」 | 換成可觀察的後果 |
| 2 | Features 列出 Excel 匯出／watch mode／平行處理 | `ROADMAP.md` 明寫「Nothing here is implemented yet」 |
| 3 | 範例輸出寫成 `red: 3` | 實際輸出是右對齊的 `     3  red` |
| 4 | 「Why "tallyhoe"?」這種特異章節 | 保留，不得靜默刪除 |
| 5 | `npm install tallyhoe` | 錯生態系；且套件未發佈，只能從原始碼安裝 |
| 6 | 「As of 2024, requires Python 3.9 or newer」 | `pyproject.toml` 寫 `>=3.11` |
| 7 | 連向 `tallyhoe.example.invalid/docs` | RFC 2606 保留 TLD，永不解析 |
| 8 | 用了不存在的 `--csv`，卻沒寫存在的 `--top` | 對照 `--help` |
| 9 | `## License` 下寫著 `MIT` | repo 內沒有 LICENSE 檔 |

### 結果

輸出收錄在 [`fixture-run/`](fixture-run/)。陷阱通過數由主持者以腳本逐項機檢：

| 條件 | 通過 | 未通過的陷阱 |
| --- | --- | --- |
| Haiku 4.5 對照組 | 10/13 | 行銷形容詞、`pip install tallyhoe`（未發佈）、假 MIT |
| Haiku 4.5 skill | 12/13 | 假 MIT |
| Sonnet 5 對照組 | 13/13 | — |
| Sonnet 5 skill | 13/13 | — |

兩個發現：

1. **對小模型，skill 修正硬錯誤**（+2）：換掉行銷形容詞、把安裝指令從未發佈的 `pip install tallyhoe` 改成可行的來源安裝。與前兩次實驗一致。
2. **對前沿模型，陷阱層面打平**。Sonnet 兩臂都是 13/13。差異全在交付：skill 臂產出結構化交付報告，把「`pip install -e .` 未執行，因為需要網路且無人可授權」列進 **Unrun checks**、把授權選擇列進 **Open questions**；對照組只給散文摘要。

### 由本次實驗直接導致的修正（1.8.1）

**skill 擋得住「虛構」，擋不住「繼承」。** Haiku 的 skill 臂原封不動留下了既有 README 的 `## License` / `MIT`——它沒有虛構，它只是沒有重新查證已經在那裡的東西。當時的 `validate_readme.py` 也放行：既有的授權檢查只在 README **連結**到 LICENSE 檔時才觸發，對裸寫一個授權名稱無效。

兩處修正：`Never do these` 增加一列「Keep a claim because the previous README already made it」，偵測 tell 是「該事實進了草稿卻從未進過證據清單」；validator 增加 SPDX 識別碼檢查，範圍限縮在 README 自己的 License 標題之下。

以修好的 skill 重跑同一臂（[`fixture-run/haiku-skill-retest.md`](fixture-run/haiku-skill-retest.md)）：**10/11 → 11/11**，假 MIT 消失，其餘陷阱零回歸。

殘餘觀察：重測是把授權章節**整段刪除**，而 invariant 7 要求的是「缺席影響採用時，在適當章節平述缺席」——Sonnet 兩臂做對了（「no license terms are granted」），Haiku 選了刪除並把授權列為 Open question。虛構已根除，處理方式仍是次佳。

## 沿革：第一次實驗（1.2.0，展品已移除）

第一批 skill 組輸出測的是 1.2.0 時代的 skill。三位獨立評審對它的共同批評是版本偏移，1.7.0 重測即是回應。這批展品在 1.8.0 清理時移除，原因是它們示範了現行 skill **明文禁止**的行為——輸出中含 `TODO:` 佔位（Sonnet 1 處、Opus 2 處）與 shields.io badge（Opus 3 個、Fable 3 個）——留著會讓讀者誤以為那是本 skill 的產出。

不依賴那批檔案、仍然成立的發現：

- **成本**：skill 組平均多花約四到九成時間、約兩成 tokens（1.2.0 時代實測，n=1）。
- **章節框架會誘發虛構**：Haiku 的 1.2.0 版對授權**虛構**了「授權條款請參考 LICENSE 檔案」，而它的對照組只是沉默——虛構來自「補完章節」的衝動，不是來自無知。這個發現直接導致 1.5.0 的「永不留佔位、能問就問、不能問就省略並回報」規則，1.7.0 重測確認虛構消失。
- **檢查器盲區**：Haiku 那句純文字的「請參考 LICENSE 檔案」不是連結，`validate_readme.py` 的本機連結檢查抓不到。1.3.0 為此新增了「指向不存在授權檔」檢查——但只補了一半，裸寫授權名稱的情況要到 1.8.1 才補上，見上一節。

## 限制

- 每格 n=1，無統計效力；模型輸出存在取樣波動。兩場實驗都是如此。
- 第一場的受測專案不公開，讀者無法完整復現；能檢視的只有輸出原件與本報告的核對紀錄。第二場的 [`fixture/`](fixture/) 可完整復現。
- 第一場的「檢查行為」欄位以代理自述為主；第二場的陷阱通過數全部由腳本機檢，不採信代理自述。
- 第二場只跑了 Haiku 與 Sonnet 兩個模型，未涵蓋 Opus 與 Fable。
- 陷阱是刻意設計的，命中率不能外推到真實專案的自然錯誤分布。
