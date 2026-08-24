# 🐺 狼人殺 — 智慧 AI 補位多人連線版

一款以 **FastAPI + WebSocket** 打造的即時多人狼人殺遊戲，內建 **Google Gemini** 驅動的 AI 玩家。房間人數不足時由 AI 自動補位，真人玩家中途斷線也會無縫交由 AI 接手，遊戲隨時能開局、不會因人數不足而卡關。

## 特色功能

- 🎮 **雙模式遊玩**：單人模式（獨自帶一整桌 AI 開局）與多人連線大廳（建立／加入房間，最多 12 人同場）
- 🤖 **AI 智慧補位**：房間座位不足時自動由 Gemini AI 補齊角色，AI 會依角色與人格進行發言、投票、使用技能
- 🔌 **斷線無縫接管**：真人玩家中途斷線時，該角色立即轉由 AI 接管，遊戲不中斷、其他玩家不受影響
- 👁️ **上帝模式（旁觀模式）**：整桌皆為 AI 對戰，旁觀者可看到所有人身份，並可暫停／繼續觀戰
- 🗣️ **七種 AI 人格**：每個 AI 角色隨機套用「謹慎分析型」「直覺型」「質問型」「沉穩型」「跟風型」「激進型」「隱藏型」等七種說話風格，發言口語化、會回應其他玩家的發言
- 🐺 **狼人夜間悄悄話**：狼人陣營（不論真人或 AI）可在夜晚即時討論今晚要刀誰，真人發言時 AI 狼人也會即時回應
- 🏠 **多人連線大廳**：建立房間（4 碼房號）／輸入房號加入、房間列表即時刷新、房主離線時自動轉移房主
- ⏸️ **暫停／繼續控制**：房主可隨時暫停或繼續遊戲進行
- 🌐 **零建置前端**：純 HTML5 / CSS3 / JavaScript，不需任何前端建置工具，由後端直接靜態伺服

## 技術架構

| 分類 | 技術 |
| --- | --- |
| 後端框架 | [FastAPI](https://fastapi.tiangolo.com/)（WebSocket + 靜態檔案伺服） |
| ASGI Server | [Uvicorn](https://www.uvicorn.org/) |
| AI 模型 | Google Gemini（透過 [`google-genai`](https://pypi.org/project/google-genai/) SDK） |
| 前端 | 原生 HTML5 / CSS3 / JavaScript（無框架、無建置流程） |
| 即時通訊 | 單一 WebSocket 連線（`/ws`），以 JSON 訊息傳遞大廳與遊戲事件 |

## 專案結構

```
backend/
├── main.py           # FastAPI 入口：WebSocket 路由、大廳／遊戲訊息分派、前端靜態檔案伺服
├── game.py           # 遊戲核心：Player / Room / LobbyManager / GameEngine（夜晚、白天、投票流程）
├── llm.py            # 封裝 Gemini API 呼叫、Prompt 組裝、429/500 自動重試與備援模型切換、JSON 回應解析
├── config.py          # API 金鑰、主／備援模型、逾時與重試次數、人數上限、角色配置
└── requirements.txt  # Python 依賴套件

frontend/
├── index.html         # 單頁應用（大廳／房間等待／遊戲畫面／結算彈窗）
├── css/style.css       # 深色奇幻風格介面樣式
└── js/
    ├── websocket.js    # WebSocket 連線封裝與事件收發
    ├── game.js          # 遊戲畫面渲染、玩家操作互動
    └── app.js           # 大廳與房間頁面邏輯（建立/加入房間、人數與模式切換）
```

## 快速開始

### 1. 環境需求

- Python 3.9 以上（建議；專案大量使用 `asyncio` 與型別註記）
- 一組 Google Gemini API 金鑰（可至 [Google AI Studio](https://aistudio.google.com/apikey) 免費申請）

### 2. 安裝依賴

```bash
cd backend
pip install -r requirements.txt
```

依賴套件：`fastapi`、`uvicorn`、`websockets`、`google-genai`、`pydantic`

### 3. 設定 API 金鑰

編輯 `backend/config.py`，將 `API_KEY` 換成你自己的 Gemini API 金鑰：

```python
API_KEY = "你的 Gemini API 金鑰"
```

> ⚠️ `config.py` 目前**沒有**被 `.gitignore` 排除，金鑰是直接寫在程式碼中。若要將專案推上公開 repo，請自行改用環境變數或另外拆出設定檔，避免金鑰外洩。

### 4. 啟動伺服器

```bash
cd backend
python main.py
```

（也可等效使用 `uvicorn main:app --host 0.0.0.0 --port 8765`，但需在 `backend/` 目錄下執行，因為 `main.py`／`game.py`／`llm.py` 是以相對於該目錄的方式互相 import。）

伺服器預設會在連接埠 `8765` 啟動，並同時提供：

- 前端頁面：`http://localhost:8765/`
- WebSocket：`ws://localhost:8765/ws`
- 健康檢查：`http://localhost:8765/health`

啟動後直接用瀏覽器開啟 `http://localhost:8765` 即可開始遊戲，不需要另外啟動前端伺服器。

> 若要更換連接埠，除了 `backend/main.py` 內 `uvicorn.run(..., port=8765)`，也要同步修改 `frontend/js/websocket.js` 中寫死的 `8765`，這兩處目前並未共用同一份設定。

## 如何遊玩

### 單人模式
1. 選擇玩家人數（6～12 人）與是否開啟「上帝模式」
2. 按下「開始遊戲」，其餘座位立即由 AI 補滿並直接開局
3. 上帝模式下你僅為旁觀者，可看到所有人身份，並能暫停／繼續整場 AI 對戰

### 多人連線模式
1. 切換到「多人大廳」分頁，輸入暱稱
2. **建立房間**：設定人數與是否為上帝模式旁觀房，取得 4 碼房號分享給朋友
3. 或**加入房間**：從現有房間列表點選加入，或直接輸入房號（同房間內暱稱不可重複）
4. 房主可在等待畫面按「開始遊戲」；未坐滿的座位會自動由 AI 補齊
5. 遊戲進行中若有真人斷線，該座位立即轉由 AI 接管，其他玩家不受影響；房主離線則自動轉移給房內其他成員

### 遊戲內操作
- **發言**：輪到你時可輸入發言內容，並指定下一位發言者（不指定則從尚未發言的玩家中隨機挑選）
- **投票**：白天發言結束後，對存活玩家投票表決放逐對象
- **技能**：預言家查驗身份、女巫使用解藥／毒藥、狼人選擇襲擊目標——輪到你時介面會彈出對應操作區
- **狼人悄悄話**：若你是狼人，夜晚可與同伴（含 AI 狼人）即時聊天討論目標

## 遊戲規則

### 角色配置（依人數自動配置）

| 玩家人數 | 🐺 狼人 | 👤 村民 | 🔮 預言家 | 🧪 女巫 |
| :---: | :---: | :---: | :---: | :---: |
| 6  | 2 | 2 | 1 | 1 |
| 7  | 2 | 3 | 1 | 1 |
| 8  | 2 | 4 | 1 | 1 |
| 9  | 3 | 4 | 1 | 1 |
| 10 | 3 | 5 | 1 | 1 |
| 11 | 3 | 6 | 1 | 1 |
| 12 | 3 | 7 | 1 | 1 |

### 回合流程

1. **夜晚**
   - 狼人共同選擇一名襲擊目標（人類與 AI 狼人可透過悄悄話討論）
   - 預言家查驗一名未查驗過的存活玩家陣營
   - 女巫得知狼人今晚選定的目標後，可選擇用解藥搭救，或改用毒藥殺死另一名玩家；**解藥與毒藥皆為一局限用一次，且同一晚只能擇一使用**（使用解藥後，當晚毒藥不會生效）
2. **白天**：存活玩家依序發言（可指定下一位發言者），發言內容會作為所有 AI 玩家後續推理與投票的依據
3. **投票**：全員對存活玩家投票，最高票者被放逐並可留下遺言；若最高票數者不只一人，本輪無人出局，直接進入下一個夜晚
4. **勝負判定**：狼人全滅 → 好人陣營獲勝；狼人數 ≥ 好人數 → 狼人陣營獲勝；否則重複夜晚／白天／投票流程直到分出勝負，結束後公開所有玩家真實身份

## 設定選項（`backend/config.py`）

| 設定 | 說明 | 預設值 |
| --- | --- | --- |
| `API_KEY` | Google Gemini API 金鑰 | `"API"`（需自行替換） |
| `PRIMARY_MODEL` | 主要使用的 Gemini 模型 | `"gemma-4-26b-a4b-it"` |
| `FALLBACK_MODEL` | 主模型逾時／錯誤／額度超限時的備援模型 | `"gemini-3.1-flash-lite"` |
| `LLM_TIMEOUT` | 單次 LLM 請求逾時秒數 | `60` |
| `LLM_MAX_RETRIES` | 每個模型的最大重試次數 | `5` |
| `MIN_PLAYERS` / `MAX_PLAYERS` | 房間人數上下限 | `6` / `12` |
| `ROLE_NAMES` | 角色代碼對應的顯示名稱（含 emoji） | 見原始檔 |
| `ROLE_DISTS` | 各人數對應的職業配置 | 見上方角色配置表 |

`backend/llm.py` 內建對 Gemini 免費額度限制（`429 RESOURCE_EXHAUSTED`）與伺服器暫時性錯誤（`500`）的自動退避重試機制；單一模型重試多次仍失敗時會切換到備援模型，兩個模型皆失敗則以預設安全回應（如「我保持沉默」）代替，避免整場遊戲卡死。

## 架構重點與已知限制

- **單一伺服器、單一連接埠**：`backend/main.py` 用同一個 FastAPI app 同時處理 WebSocket（`/ws`）與前端靜態檔案（其餘所有路徑皆會嘗試對應 `frontend/` 內的檔案，找不到則回退到 `index.html`），開發或部署時不需要額外的跨來源設定。
- **狀態全存在記憶體中**：房間（`LobbyManager`）與對局（`GameEngine`）都只是程序內的物件，重啟伺服器會清空所有房間與進行中的對局，目前也未支援多進程／多機水平擴展。
- **WebSocket 訊息協定**：前後端所有溝通都在同一條 `/ws` 連線上以 JSON 訊息進行，並以 `type` 欄位區分：

  | 方向 | 常見 `type` |
  | --- | --- |
  | 前端 → 後端 | `get_room_list`、`create_room`、`join_room`、`start_room_game`、`start_game`、`speak_and_next`、`vote`、`wolf_target`、`wolf_chat`、`seer_target`、`witch_decision`、`last_words`、`pause`、`resume` |
  | 後端 → 前端 | `room_list`、`room_joined`、`room_members_update`、`host_promoted`、`init`、`phase`、`message`、`night_result`、`seer_result`、`speech`、`your_turn`、`vote`、`elimination`、`vote_tie`、`last_words`、`wolf_message`、`your_wolf_target`、`your_seer_target`、`your_witch_decision`、`game_over`、`error` |

## 其他注意事項

- 專案目前未附上 LICENSE 檔案，沒有明確的授權條款；若要對外開源發佈，建議自行加上授權宣告。
- 呼叫 Gemini API 會依 Google 當下的方案計費／計入免費額度，AI 玩家愈多、對局愈長，呼叫次數也愈多，請留意用量與額度。
- `config.py` 內含明文 API 金鑰且未被 `.gitignore` 排除，公開分享或推送 repo 前請自行妥善處理，避免金鑰外流。
