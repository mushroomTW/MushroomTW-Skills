# 🐺 狼人殺 — 智慧 AI 補位多人連線版

[![Python](https://img.shields.io/badge/Python-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Gemini API](https://img.shields.io/badge/Gemini%20API-4285F4.svg?logo=google&logoColor=white)](https://ai.google.dev/)

在瀏覽器裡開一場[狼人殺](https://zh.wikipedia.org/wiki/%E7%8B%BC%E4%BA%BA%E6%AE%BA%E6%B8%B8%E6%88%8F)：湊不齊人的座位全部交給 Google Gemini 扮演的 AI 玩家。你可以單人與 AI 對戰、開房間和朋友連線（不足人數自動 AI 補位），或用上帝模式旁觀一整場全 AI 的心理戰。

## 目錄

- [專案簡介](#專案簡介)
- [遊戲特色](#遊戲特色)
- [快速開始](#快速開始)
- [遊戲模式](#遊戲模式)
- [遊戲流程與規則](#遊戲流程與規則)
- [設定](#設定)
- [架構與專案結構](#架構與專案結構)
- [已知限制](#已知限制)
- [授權](#授權)

## 專案簡介

這是一個自架的狼人殺網頁遊戲：後端以 FastAPI + WebSocket 推進劇本，前端是免建置的原生 HTML/CSS/JS 單頁介面。所有非真人座位都由 [Gemini API](https://ai.google.dev/) 驅動的 AI 玩家接手——它們會依隨機抽到的性格用口語化的方式發言、帶風向、悍跳、投票，甚至在狼人頻道裡和你密謀今晚刀誰。

適合的使用情境：

- 一個人想練狼人殺：單人模式直接開局，與一桌 AI 對戰。
- 朋友不夠開一局：多人房間開局時，空位自動由 AI 補齊。
- 想看 AI 互相演戲：上帝模式旁觀全 AI 對局，所有身分公開。

設計定位是本機或區域網路的自架同樂工具：沒有帳號系統、沒有資料庫，房間狀態只存在伺服器記憶體中。

## 遊戲特色

- 三種玩法：單人對 AI、多人房間（4 碼房號、房間列表、AI 補位）、上帝模式旁觀。
- AI 玩家隨機擁有 7 種性格（謹慎分析、直覺情緒、質問挑釁、沉穩高冷、跟風附和、激進帶風向、隱藏摸魚），發言口語化、有情緒，而不是死板的推理報告。
- 完整標準局劇本：狼人夜襲與陣營密聊（AI 狼同伴會回話）、預言家查驗、女巫解藥與毒藥、白天輪流發言、投票放逐與遺言。
- 發言接力機制：首位發言者隨機，之後由每位發言者指定下一位發言的人。
- 真人斷線時 AI 無縫接管座位，對局不中斷；真人行動逾時 60 秒自動採用預設行動。
- LLM 容錯：呼叫逾時、429 限流、500 錯誤時自動退避重試，主用模型失敗會切換備用模型。

## 快速開始

### 前置需求

- Python 3（`backend/requirements.txt` 未固定套件版本，建議使用近期的 Python 3 版本）
- Google Gemini API 金鑰（可在 [Google AI Studio](https://aistudio.google.com/apikey) 申請）
- 可連上 Gemini API 的網路（對局中所有 AI 發言與決策都是即時呼叫）

### 安裝與啟動

```bash
cd wk_fable/backend

# （建議）建立虛擬環境
python -m venv .venv
.venv\Scripts\activate        # Windows；macOS / Linux 改用 source .venv/bin/activate

pip install -r requirements.txt
```

接著編輯 [`backend/config.py`](backend/config.py)，把 `API_KEY` 換成你的 Gemini API 金鑰：

```python
API_KEY = "你的 Gemini API 金鑰"
```

啟動伺服器：

```bash
python main.py
```

伺服器會在 `0.0.0.0:8765` 啟動並直接供應前端頁面。打開瀏覽器進入 <http://localhost:8765> 就能開始遊戲。也可以先確認服務狀態：

```bash
curl http://localhost:8765/health
# {"status":"ok"}
```

> [!WARNING]
> API 金鑰是直接寫在 `backend/config.py` 原始碼裡的，而且 `.gitignore` 並未排除這個檔案。若要公開或提交此專案，請先移除真實金鑰，以免外洩。

> [!NOTE]
> 使用免費額度時若觸發 429 限流，程式會自動等待並重試（必要時切換備用模型），對局節奏會明顯變慢，這是正常現象。

> [!TIP]
> 區域網路同樂：伺服器綁定 `0.0.0.0`，朋友可直接用 `http://<你的內網 IP>:8765` 連入；前端會自動以同一主機名稱連接 WebSocket。請確認防火牆放行 8765 連接埠。

## 遊戲模式

| 模式 | 說明 |
| --- | --- |
| 單人模式 | 立即開局，你以隨機座位、隨機身分加入，其餘座位皆為 AI。 |
| 多人大廳 | 建立房間（自動產生 4 碼房號）或輸入房號加入好友的房間；大廳會列出等待中的房間。房主按下開始後，不足的人數由 AI 補位。 |
| 上帝模式 | 全部座位皆為 AI，你以旁觀者視角觀戰，所有玩家身分公開（含狼人夜間密聊），房主可隨時暫停／繼續對局。 |

## 遊戲流程與規則

支援 6–12 人局，職業配置如下（來自 `backend/config.py` 的 `ROLE_DISTS`）：

| 人數 | 🐺 狼人 | 👤 村民 | 🔮 預言家 | 🧪 女巫 |
| :-: | :-: | :-: | :-: | :-: |
| 6 | 2 | 2 | 1 | 1 |
| 7 | 2 | 3 | 1 | 1 |
| 8 | 2 | 4 | 1 | 1 |
| 9 | 3 | 4 | 1 | 1 |
| 10 | 3 | 5 | 1 | 1 |
| 11 | 3 | 6 | 1 | 1 |
| 12 | 3 | 7 | 1 | 1 |

每一天依序進行：

1. **夜晚**：狼人在專屬頻道密談並選定襲擊目標（真人狼可打字，AI 狼會即時回話）→ 預言家查驗一名玩家（得知好人或狼人）→ 女巫決定是否用解藥救人、是否用毒藥（各一瓶，整場限用一次）。
2. **白天**：公布昨夜死訊後輪流發言。首位發言者隨機，之後由發言者指定下一位；被淘汰者可留遺言，遺言也會納入 AI 的推理素材。
3. **投票**：全員投票，最高票者出局並發表遺言；平票時當日無人出局，直接入夜。
4. **勝負判定**：狼人全數出局則好人陣營獲勝；存活狼人數量大於等於其他存活者時狼人陣營獲勝。

其他規則：

- 真人每次行動（發言、投票、夜間技能）限時 60 秒，逾時自動採用預設行動（例如發言「我還在觀察...」、隨機投票、女巫不用藥）。
- 真人中途斷線時，該座位立即由 AI 接管並廣播提示，遊戲繼續進行。

## 設定

所有設定集中在 [`backend/config.py`](backend/config.py)：

| 設定 | 預設值 | 說明 |
| --- | --- | --- |
| `API_KEY` | `"API"`（占位字串） | Gemini API 金鑰，執行前必須換成有效金鑰。 |
| `PRIMARY_MODEL` | `gemma-4-26b-a4b-it` | 主用模型；依檔內註解，可與備用模型互換以追求速度。 |
| `FALLBACK_MODEL` | `gemini-3.1-flash-lite` | 主用模型重試仍失敗時自動切換的備用模型。 |
| `LLM_TIMEOUT` | `60` | 單次 LLM 呼叫的逾時秒數。 |
| `LLM_MAX_RETRIES` | `5` | 單一模型的重試次數上限。 |
| `MIN_PLAYERS` / `MAX_PLAYERS` | `6` / `12` | 允許的對局人數範圍。 |
| `ROLE_DISTS` | 見上方配置表 | 各人數對應的職業配置。 |

> [!IMPORTANT]
> 連接埠 `8765` 分別寫死在 [`backend/main.py`](backend/main.py)（`uvicorn.run` 的 `port`）與 [`frontend/js/websocket.js`](frontend/js/websocket.js)（WebSocket 連線網址）兩處，更改時必須一併修改。

## 架構與專案結構

前端是單頁應用，載入後透過單一 WebSocket（`/ws`）與後端交換 JSON 訊息（建房、加入、發言、投票、夜間技能等）。後端 FastAPI 同時負責供應靜態檔案、`/health` 健康檢查與遊戲邏輯；每個房間對應一個 `GameEngine`，以 asyncio 背景任務推進劇本——輪到真人時等待其輸入（60 秒逾時），輪到 AI 時組裝提示詞呼叫 Gemini 並解析 JSON 回應。

```text
wk_fable/
├── backend/
│   ├── main.py            # FastAPI 入口：WebSocket 訊息路由與靜態檔案供應
│   ├── game.py            # 遊戲引擎（夜晚／白天／投票）、房間與大廳管理
│   ├── llm.py             # Gemini 呼叫、重試與容錯、各角色提示詞、回應解析
│   ├── config.py          # API 金鑰、模型與遊戲參數
│   └── requirements.txt
└── frontend/
    ├── index.html         # 單頁介面：大廳、房間等待、對局畫面
    ├── css/style.css
    └── js/
        ├── app.js         # 大廳與設定頁邏輯（模式切換、房間列表輪詢）
        ├── game.js        # 對局事件處理與畫面渲染
        └── websocket.js   # WebSocket 用戶端封裝與自動重連
```

## 已知限制

- 房間與對局狀態只存在記憶體中，伺服器重啟後全部消失；沒有資料庫或持久化。
- 真人斷線後由 AI 永久接管，重新整理頁面無法回到原座位（房間只在等待階段接受加入）。
- 內建伺服器僅提供 HTTP，沒有 TLS 與任何身分驗證；建議只在信任的區域網路使用，或自行架設反向代理。
- AI 的回應品質與速度取決於所設定的 Gemini 模型與 API 額度；限流時對局會變慢。
- 目前沒有自動化測試與 CI。

## 授權

TODO：本專案目前未包含 LICENSE 檔案，授權條款未定。在取得作者確認前，請勿假設可自由散布或商用。
