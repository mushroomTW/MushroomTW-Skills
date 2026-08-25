# 🐺 狼人殺 — 智慧 AI 補位多人連線版

在瀏覽器裡玩的狼人殺網頁遊戲：由 [Google Gemini](https://ai.google.dev/) 模型扮演 AI 玩家，支援單人對戰全 AI、旁觀全 AI 對局，以及多人連線房間（缺額由 AI 自動補位）。後端為 FastAPI + WebSocket，前端為免建置的原生 HTML/CSS/JavaScript。

## 遊戲特色

- **三種玩法**：單人模式（你 + AI 玩家）、上帝視角（全 AI 對局旁觀，可隨時暫停/繼續）、多人大廳（建房取得房號，親友加入後由 AI 補足空位）。
- **6～12 人局**：依人數自動套用職業配置，包含 🐺 狼人、👤 村民、🔮 預言家、🧪 女巫四種職業。
- **AI 玩家有個性**：每名 AI 依人物風格發言，會回應場上已發言玩家的觀點、投票、留遺言；發言者可指定下一位發言者。
- **完整夜晚流程**：狼人刀人 → 預言家查驗 → 女巫用解藥/毒藥；真人玩家擔任特殊職業時，透過網頁介面執行對應行動。
- **穩定性設計**：主模型逾時或額度用盡（429）時自動退避重試並切換備用模型；前端斷線後每 3 秒自動重連。

## 快速開始

前置需求：

- Python 3 與 pip
- Google Gemini API 金鑰（可在 [Google AI Studio](https://aistudio.google.com/apikey) 免費申請；預設模型皆有免費額度）

```bash
# 1. 安裝後端依賴
pip install -r backend/requirements.txt

# 2. 設定 API 金鑰：編輯 backend/config.py，將 API_KEY 換成你的金鑰
#    API_KEY = "你的 Gemini API 金鑰"

# 3. 啟動伺服器（同時供應前端頁面）
python backend/main.py
```

啟動後以瀏覽器開啟 <http://localhost:8765>，選擇人數與模式即可開局。伺服器是否正常可用健康檢查確認：

```bash
curl http://localhost:8765/health
# {"status":"ok"}
```

> [!IMPORTANT]
> `backend/config.py` 內建的 `API_KEY = "API"` 只是佔位值，不是有效金鑰。未替換前所有 LLM 呼叫都會失敗，AI 玩家只會重複「我保持沉默。」等固定台詞。

> [!WARNING]
> 金鑰以明文寫在 `backend/config.py`，且該檔**未**列入 `.gitignore`。若要公開這份程式碼，請先移除金鑰，避免將它提交進版本庫。

## 遊戲流程

每一天依序進行：

1. **夜晚**：狼人選擇擊殺目標 → 預言家查驗一名玩家身分 → 女巫決定是否用解藥救人或用毒藥殺人。
2. **白天發言**：玩家輪流發言（1～2 句），發言者可指定下一位發言者；出局者可留遺言。
3. **投票**：全體存活玩家投票，得票最高者出局。
4. **勝負判定**：狼人全數出局則好人陣營獲勝；狼人數量大於等於其他存活玩家時狼人陣營獲勝。

各人數的職業配置（定義於 `backend/config.py` 的 `ROLE_DISTS`）：

| 玩家人數 | 🐺 狼人 | 👤 村民 | 🔮 預言家 | 🧪 女巫 |
| :---: | :---: | :---: | :---: | :---: |
| 6 | 2 | 2 | 1 | 1 |
| 7 | 2 | 3 | 1 | 1 |
| 8 | 2 | 4 | 1 | 1 |
| 9 | 3 | 4 | 1 | 1 |
| 10 | 3 | 5 | 1 | 1 |
| 11 | 3 | 6 | 1 | 1 |
| 12 | 3 | 7 | 1 | 1 |

## 設定

所有設定都是 `backend/config.py` 中的 Python 常數，修改後重啟伺服器生效。程式**不會**讀取環境變數或 `.env` 檔（`.gitignore` 裡的 `.env` 只是預防性排除，程式沒有載入它）。

| 常數 | 預設值 | 說明 |
| --- | --- | --- |
| `API_KEY` | `"API"`（佔位值） | Gemini API 金鑰，必須替換 |
| `PRIMARY_MODEL` | `gemma-4-26b-a4b-it` | 主用模型；註解建議追求速度可與備用模型互換 |
| `FALLBACK_MODEL` | `gemini-3.1-flash-lite` | 備用模型，主模型連續失敗時啟用 |
| `LLM_TIMEOUT` | `60` | 單次 LLM 呼叫逾時秒數 |
| `LLM_MAX_RETRIES` | `5` | 每個模型的最大重試次數 |
| `MIN_PLAYERS` / `MAX_PLAYERS` | `6` / `12` | 允許的玩家人數範圍 |
| `ROLE_NAMES` / `ROLE_DISTS` | 見上表 | 職業名稱與各人數的職業配置 |

> [!NOTE]
> 伺服器埠號 `8765` 分別寫死在 `backend/main.py`（`uvicorn.run`）與 `frontend/js/websocket.js`（WebSocket 連線位址）兩處，如需更換必須同時修改。

## 專案結構

```text
wk2_fable/
├── backend/
│   ├── main.py      # FastAPI 入口：WebSocket 端點 /ws、健康檢查 /health、前端靜態檔服務
│   ├── game.py      # 遊戲引擎與大廳/房間管理（夜晚、發言、投票、勝負判定）
│   ├── llm.py       # Gemini 呼叫、重試/降級策略與各職業提示詞
│   ├── config.py    # 金鑰、模型與遊戲參數
│   └── requirements.txt
└── frontend/        # 原生 HTML/CSS/JS，由後端直接供應，無需建置
    ├── index.html
    ├── css/style.css
    └── js/           # websocket.js（連線）、game.js（遊戲畫面）、app.js（大廳與設定）
```

前後端以單一 WebSocket（`ws://<host>:8765/ws`）溝通，訊息為 JSON；後端同時擔任前端靜態檔伺服器，因此只需啟動一個行程。

## 已知限制

- 房間與對局狀態只存在記憶體中，伺服器重啟後全部消失，沒有資料庫或存檔。
- AI 回應速度與品質取決於 Gemini API 額度：免費額度吃緊時會因 429 退避重試而變慢，兩個模型都失敗時 AI 以固定台詞帶過該回合。
- 伺服器預設監聽 `0.0.0.0`，區網內其他裝置可直接連入；如不希望對外開放，請自行調整 `backend/main.py` 的監聽位址。

## 授權

本專案目前未附 LICENSE 檔案，尚未指定授權條款。
