# 🐺 狼人殺 — 智慧 AI 補位多人連線版

<!-- badge 來源：backend/requirements.txt（僅標示依賴名稱，不標版本，因此不會過期） -->
[![Backend: FastAPI](https://img.shields.io/badge/backend-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![LLM: Google Gemini API](https://img.shields.io/badge/LLM-Google%20Gemini%20API-4285F4.svg?logo=googlegemini&logoColor=white)](https://ai.google.dev/)
[![Frontend: Vanilla JS](https://img.shields.io/badge/frontend-Vanilla%20JS-f7df1e.svg?logo=javascript&logoColor=black)](https://developer.mozilla.org/docs/Web/JavaScript)

一個可以在自己電腦上跑起來的 6–12 人狼人殺，人數不足的座位由大型語言模型驅動的 AI 玩家補上。適合想跟三五好友在區域網路開一局、或單純想旁觀 AI 互相欺騙的人。

> [!IMPORTANT]
> 啟動前必須先把 `backend/config.py` 裡的 `API_KEY` 換成你自己的 [Google Gemini API 金鑰](https://ai.google.dev/gemini-api/docs/api-key)。倉庫內的值是佔位字串 `"API"`，不是可用金鑰。

> [!WARNING]
> 金鑰是以明碼寫在 `backend/config.py` 這個原始碼檔中，而 `.gitignore` 只忽略了 `.env`、不會忽略 `config.py`。若要把這份專案推上公開倉庫，請先確認金鑰沒有被一起提交。

## 目錄

- [這是什麼](#這是什麼)
- [快速開始](#快速開始)
- [遊戲模式](#遊戲模式)
- [主要功能](#主要功能)
- [遊戲規則](#遊戲規則)
- [設定](#設定)
- [專案結構](#專案結構)
- [運作方式](#運作方式)
- [已知限制](#已知限制)
- [授權與貢獻](#授權與貢獻)

## 這是什麼

狼人殺是一款社交推理桌遊：狼人在夜裡祕密擊殺，好人在白天靠發言和投票把狼人找出來。這個專案把它做成一個網頁版，並解決「湊不到人」這個最大障礙——你有幾個真人就開幾個座位，剩下的全部由 AI 頂上。

AI 玩家不是只會亂投票的機器人：每位 AI 開局時會隨機拿到一種口語化的說話人格（謹慎分析型、質問型、跟風型等七種），發言、指定下一位發言者、投票、遺言都由模型即時生成。給狼人 AI 的 prompt 還會要求牠假扮身份、必要時悍跳搶神職，實際演得像不像則取決於模型。

適合的情況：想在本機或區域網路快速開一局、想觀察 LLM 在社交推理場景的表現、想拿它當 FastAPI + WebSocket 的參考實作。

不適合的情況：這不是可公開上線的服務——沒有帳號系統、沒有存檔、沒有測試，房間狀態全在記憶體裡（詳見[已知限制](#已知限制)）。

## 快速開始

### 前置需求

- Python 3 與 pip。倉庫沒有 `pyproject.toml` 或版本鎖檔，`requirements.txt` 也未鎖定套件版本，因此最低可用版本未定義。
- 一組 [Google Gemini API 金鑰](https://ai.google.dev/gemini-api/docs/api-key)。
- 一個現代瀏覽器。前端沒有任何建置步驟，也不需要 Node.js。

### 安裝與啟動

```bash
cd backend
pip install -r requirements.txt
```

打開 `backend/config.py`，把第一行的 `API_KEY` 換成你的金鑰：

```python
API_KEY = "你的-gemini-api-金鑰"
```

啟動伺服器（後端同時負責提供前端靜態檔案，不需要另外開一個 web server）：

```bash
python main.py
```

終端機會出現類似這樣的訊息：

```
INFO:     Uvicorn running on http://0.0.0.0:8765 (Press CTRL+C to quit)
```

確認服務活著：

```bash
curl http://localhost:8765/health
```

```json
{"status":"ok"}
```

接著用瀏覽器打開 <http://localhost:8765>，在「單人模式」分頁選好人數後按「開始遊戲」，第一局就開始了。

> [!TIP]
> 要和同一個區域網路的朋友一起玩，把 `http://<你的區域網路 IP>:8765` 給他們即可。後端綁定 `0.0.0.0`，前端則用瀏覽器當下的 `location.hostname` 組出 WebSocket 位址，所以不必改任何設定。

## 遊戲模式

| 模式 | 怎麼進入 | 你的角色 |
| --- | --- | --- |
| 單人模式 | 首頁「單人模式」分頁，選人數後直接開始 | 你被隨機安排到其中一個座位，其餘座位全部由 AI 擔任 |
| 多人大廳 | 「多人大廳」分頁，建立房間或輸入 4 碼房號加入 | 房內每位真人各佔一個座位，剩下的空位在開局時由 AI 補滿 |
| 上帝模式 | 兩個分頁都有勾選框可切換 | 你不參戰，純旁觀全 AI 對局；所有玩家身份公開，並可暫停／繼續 |

多人房的房號是 4 位英數字（例如 `W7KF`），開局前可以在大廳看到所有等待中的房間，列表每 5 秒自動刷新。

## 主要功能

- **AI 補位**：真人不足時自動補滿座位；真人中途斷線，該座位立刻交由 AI 接管，並在聊天區廣播一則系統訊息，牌局不會中斷。
- **視角隔離**：伺服器針對每個觀看者分別決定哪些身份可見——你只看得到自己的牌、狼人互相看得到隊友、預言家看得到已查驗過的人、死者身份公開。上帝模式才會全部亮牌。
- **真人與 AI 混合的狼人夜聊**：夜晚狼人有獨立聊天室；真人發話後，會隨機挑一位 AI 狼人用模型生成一句回覆一起討論刀口。
- **指定下一位發言者**：發言結束後可以點名下一位，AI 也會依自己的懷疑對象點人，發言順序因此每局都不同。
- **逾時保護**：真人行動有 60 秒上限，逾時自動套用預設動作，不會有人卡住整局。
- **雙模型容錯**：主模型失敗時自動改用備用模型；遇到 429 額度超限或 500 伺服器錯誤會退避重試。

## 遊戲規則

### 角色

| 角色 | 能力 |
| --- | --- |
| 🐺 狼人 | 每晚共同選定一人擊殺；夜間可與狼同伴私聊。多名狼人各自選擇時取最高票 |
| 👤 村民 | 沒有特殊能力，只能靠發言與投票 |
| 🔮 預言家 | 每晚查驗一名尚未查驗過的存活玩家，得知對方是狼人或好人 |
| 🧪 女巫 | 全場一瓶解藥、一瓶毒藥，各只能用一次；同一晚不能同時使用兩瓶 |

### 職業配置

| 玩家人數 | 狼人 | 預言家 | 女巫 | 村民 |
| --- | --- | --- | --- | --- |
| 6–8 人 | 2 | 1 | 1 | 其餘 |
| 9–12 人 | 3 | 1 | 1 | 其餘 |

配置的權威來源是 `backend/config.py` 的 `ROLE_DISTS`。注意 `frontend/js/app.js` 另有一份相同的表，只用於首頁的配置預覽；修改規則時兩邊都要改。

### 一輪流程

每一輪依序經過夜晚、白天發言、投票三個階段，直到分出勝負為止。

**夜晚**

1. 狼人選擇今晚的擊殺目標。
2. 預言家查驗一名尚未查驗過的存活玩家。
3. 女巫得知今晚誰被殺，決定是否用解藥救人，或對某人使用毒藥。

**白天發言**

隨機一名存活玩家先發言，每位發言者可以指定下一位；若指定無效或未指定，則從尚未發言者中隨機挑一位，直到所有存活玩家都講過話。

**投票**

所有存活玩家投票，最高票者出局並發表遺言。若出現平票，本輪不淘汰任何人，直接進入下一個夜晚。

> [!NOTE]
> 真人玩家 60 秒未行動時的預設動作：發言送出「我還在觀察...」、投票隨機投給一名其他存活玩家、狼人刀口與預言家查驗改為隨機決定、女巫不使用任何藥水、遺言送出「...」。

### 勝負條件

- 狼人全部出局：好人陣營獲勝。
- 存活狼人數大於或等於存活非狼人數：狼人陣營獲勝。

## 設定

所有可調參數都集中在 `backend/config.py`，沒有環境變數或設定檔：

| 設定項 | 預設值 | 說明 |
| --- | --- | --- |
| `API_KEY` | `"API"`（佔位字串） | Google Gemini API 金鑰，**必須自行替換** |
| `PRIMARY_MODEL` | `gemma-4-26b-a4b-it` | 主要使用的模型 |
| `FALLBACK_MODEL` | `gemini-3.1-flash-lite` | 主模型失敗時改用，速度較快 |
| `LLM_TIMEOUT` | `60` | 單次模型請求的逾時秒數 |
| `LLM_MAX_RETRIES` | `5` | 每個模型的重試次數 |
| `MIN_PLAYERS` / `MAX_PLAYERS` | `6` / `12` | 允許的房間人數範圍 |
| `ROLE_NAMES` / `ROLE_DISTS` | 見檔案 | 角色顯示名稱與各人數的職業配置 |

兩個模型名稱請對照 [Gemini API 支援的模型清單](https://ai.google.dev/gemini-api/docs/models)確認在你的帳號下可用；模型名稱失效時，AI 的每一次行動都會走到備援路徑（見[已知限制](#已知限制)）。

> [!NOTE]
> 服務埠 `8765` 寫死在兩個地方：`backend/main.py` 結尾的 `uvicorn.run(...)`，以及 `frontend/js/websocket.js` 組 WebSocket 位址的那一行。要換埠必須兩邊一起改。

## 專案結構

```
.
├── backend/
│   ├── main.py           # FastAPI 進入點：WebSocket 路由、訊息分派、靜態檔案服務
│   ├── game.py           # Player / Room / LobbyManager / GameEngine，完整對局流程
│   ├── llm.py            # 模型呼叫與重試備援、各階段 prompt 組裝、回應解析
│   ├── config.py         # 金鑰、模型名稱、人數範圍、職業配置
│   └── requirements.txt
└── frontend/
    ├── index.html        # 首頁、房間等待頁、遊戲頁、結算彈窗（單頁切換）
    ├── css/style.css
    └── js/
        ├── websocket.js  # GameSocket：連線、斷線後自動重連、送出各類動作
        ├── game.js       # 遊戲畫面渲染與伺服器事件處理
        └── app.js        # 首頁、大廳、房間的 UI 與事件綁定
```

## 運作方式

後端是單一個 FastAPI 行程，所有房間與對局狀態都放在記憶體中的 `lobby_manager`。同一條 `/ws` 連線同時服務大廳和對局：`main.py` 依訊息的 `type` 欄位分派，實際流程由 `GameEngine.run()` 這個 async 迴圈驅動。所有非 `/health` 的 GET 請求都會落到 catch-all 路由，直接從 `frontend/` 讀檔回傳（找不到檔案時回退到 `index.html`，並擋掉跳出目錄的路徑）。

輪到真人行動時，引擎送出對應的 `your_*` 事件並 `await` 一個 `asyncio.Future`；瀏覽器回傳動作後 Future 被喚醒，逾時則套用預設動作。輪到 AI 時，同一個位置改成呼叫 `llm.ask_gemini()`。真人與 AI 因此走的是同一條流程，這也是斷線後能無縫換手的原因。

<details>
<summary>WebSocket 訊息一覽</summary>

**客戶端送出**（`frontend/js/websocket.js` → `backend/main.py`）

| `type` | 用途 |
| --- | --- |
| `get_room_list` | 取得等待中的房間列表 |
| `create_room` | 建立房間（`player_name`、`player_count`、`mode`） |
| `join_room` | 以房號加入房間（`room_id`、`player_name`） |
| `start_game` | 單人模式：建房並立即開始 |
| `start_room_game` | 多人模式：房主開始遊戲 |
| `speak_and_next` | 送出發言與指定的下一位發言者 |
| `vote` | 投票 |
| `wolf_target` | 狼人選擇刀口 |
| `wolf_chat` | 狼人夜間聊天 |
| `seer_target` | 預言家查驗目標 |
| `witch_decision` | 女巫用藥決定（`save`、`poison_target`） |
| `last_words` | 出局後的遺言 |
| `pause` / `resume` | 房主暫停或繼續（UI 只在上帝模式顯示此控制項） |

**伺服器送出**：`room_list`、`room_joined`、`room_members_update`、`host_promoted`、`error`、`init`、`phase`、`message`、`night_result`、`seer_result`、`ai_thinking`、`speech`、`vote`、`elimination`、`vote_tie`、`last_words`、`wolf_message`、`paused`、`game_over`，以及請求真人行動的 `your_turn`、`your_vote`、`your_wolf_target`、`your_seer_target`、`your_witch_decision`、`your_last_words`。各事件的欄位可在 `frontend/js/game.js` 的對應處理函式中查閱。

</details>

## 已知限制

- **狀態全在記憶體**：房間與對局狀態存在行程內的字典中，伺服器重啟就全部消失。房間只有在最後一名成員離開時才會被移除，已結束的房間不會自動清理。
- **無身分驗證**：任何連得到這個埠的人都能建立或加入房間，房號是 4 碼英數字。請只在信任的網路中使用，不要直接暴露到公開網路。
- **斷線無法重連回原座位**：真人斷線後座位交給 AI 接管，重新連線只會回到大廳，無法接管回原本的角色。
- **金鑰以明碼存放**：`config.py` 是原始碼檔而非被忽略的設定檔，`.gitignore` 不會保護它。
- **金鑰或模型無效時遊戲仍會進行**：模型呼叫全部失敗時 `llm.ask_gemini()` 會回傳固定的備援字串，AI 於是變成講罐頭台詞、隨機投票與隨機刀人，畫面上不會出現明顯錯誤提示，只有伺服器終端機會印出錯誤。
- **平票不重投**：出現平票時本輪直接沒有人出局，不會進行第二輪投票。
- **職業配置有兩份**：`backend/config.py` 與 `frontend/js/app.js` 各存一份，可能不同步。
- **未鎖定版本、無測試與 CI**：`requirements.txt` 沒有版本約束，倉庫內沒有任何測試或 CI 設定。

## 授權與貢獻

`TODO:` 倉庫中沒有 `LICENSE` 檔案，使用、修改與散布的條件目前未定義。

`TODO:` 倉庫中沒有 `CONTRIBUTING.md`，也沒有可指向的議題追蹤或討論區，提問與貢獻的管道尚未確立。
