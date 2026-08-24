# wkb_haiku

一款功能豐富的多人在線人狼遊戲平台，搭載 AI 玩家與即時 WebSocket 通訊機制。支援 6-12 人遊戲，提供沉浸式的策略性推理體驗。

## 功能特性

### 核心遊戲機制
- **多人實時遊戲**：支援 6-12 名玩家同時進行，透過 WebSocket 實現毫秒級同步
- **多元角色設定**：
  - 🐺 狼人（Werewolf）：夜間狩獵，掩藏身份
  - 👤 村民（Villager）：與狼人對抗
  - 🔮 預言家（Seer）：夜間預言身份
  - 🧪 女巫（Witch）：擁有解藥與毒藥

### AI 與 LLM 整合
- **智能 AI 玩家**：由大型語言模型驅動，具備天然語言理解能力
- **個性化發言風格**：7 種不同性格設定
  - 謹慎分析型
  - 直覺型（情緒派）
  - 質問型（挑釁／逼問）
  - 沉穩型（高冷）
  - 跟風型（附和／牆頭草）
  - 激進型（暴躁帶風向）
  - 隱藏型（摸魚打太極）
- **多模型支援**：主用 Gemma 4，備用 Gemini Flash，確保穩定性

### 遊戲管理
- **房間系統**：支援創建與加入房間，房主可控制遊戲進程
- **暫停與恢復**：房主可在遊戲中隨時暫停與恢復
- **觀察者模式**（God Mode）：無限容納觀眾，不影響遊戲進行
- **自動 AI 接管**：玩家掉線時，AI 無縫接管其操作
- **動態房主轉移**：房主離開時自動提升新房主

### 遊戲流程
- **白天階段**：所有玩家公開討論，投票決定處死對象
- **夜間階段**：狼人狩獵、預言家預言、女巫作用決定
- **投票機制**：實時投票統計，多數決機制
- **遺言系統**：被執行者可發表最後遺言

## 技術架構

### 後端（Backend）
- **框架**：FastAPI + Uvicorn
- **通訊**：WebSocket 雙向實時傳輸
- **遊戲引擎**：GameEngine 處理核心邏輯
- **大型語言模型**：Anthropic Gemma 與 Google Gemini 整合

### 前端（Frontend）
- **技術棧**：Vanilla JavaScript + HTML5 + CSS3
- **實時通訊**：WebSocket 客戶端
- **互動方式**：實時投票、發言、角色操作

### 專案結構
```
wkb_haiku/
├── backend/
│   ├── main.py           # FastAPI 主應用與 WebSocket 端點
│   ├── game.py           # 遊戲引擎與房間管理
│   ├── config.py         # 配置文件（角色分配、玩家數限制等）
│   ├── llm.py            # LLM 整合模組
│   └── __pycache__/
├── frontend/
│   ├── index.html        # 主頁面
│   ├── css/
│   │   └── style.css     # 樣式表
│   └── js/
│       ├── app.js        # 主應用邏輯
│       ├── game.js       # 遊戲邏輯
│       └── websocket.js  # WebSocket 通訊
├── .gitignore            # Git 忽略規則
└── README.md             # 本文件
```

## 快速開始

### 環境需求
- Python 3.9+
- 現代化網頁瀏覽器（支援 WebSocket）

### 安裝與執行

1. **複製專案**
   ```bash
   git clone <repository>
   cd wkb_haiku
   ```

2. **安裝 Python 依賴**
   ```bash
   pip install fastapi uvicorn
   ```

3. **配置 LLM API**
   編輯 `backend/config.py`，設定 API 金鑰與偏好的模型：
   ```python
   API_KEY = "your-api-key"
   PRIMARY_MODEL = "gemma-4-26b-a4b-it"
   FALLBACK_MODEL = "gemini-3.1-flash-lite"
   ```

4. **啟動伺服器**
   ```bash
   cd backend
   python main.py
   ```
   伺服器運行於 `http://0.0.0.0:8765`

5. **開啟瀏覽器**
   訪問 `http://localhost:8765` 開始遊戲

## 遊戲玩法

### 基本流程
1. **創建房間**：輸入暱稱與目標人數，生成房間代碼
2. **邀請玩家**：分享房間代碼，其他玩家加入
3. **開始遊戲**：房主點擊「開始遊戲」，系統自動分配角色
4. **白天討論**：玩家輪流發言，討論誰是狼人
5. **投票**：進行投票，票數最多的玩家被處死
6. **夜間行動**：狼人狩獵、預言家預言、女巫決定
7. **勝負判定**：狼人全滅→村民勝；狼人等於或超過村民→狼人勝

### 角色說明
- **狼人**：掩蓋身份，夜間協力狩獵一名村民
- **村民**：普通玩家，無特殊能力
- **預言家**：夜間可預言一人的身份
- **女巫**：擁有一份解藥（救人）與一份毒藥（殺人）

## API 端點

### 健康檢查
- `GET /health` - 檢查伺服器狀態

### WebSocket
- `WS /ws` - 主遊戲通訊端點

### 訊息類型

#### 客戶端 → 伺服器
| 訊息類型 | 參數 | 說明 |
|---------|------|------|
| `create_room` | `player_name`, `player_count`, `mode` | 創建房間 |
| `join_room` | `room_id`, `player_name` | 加入房間 |
| `get_room_list` | - | 取得活動房間列表 |
| `start_room_game` | - | 開始遊戲（房主專用） |
| `start_game` | `player_count`, `mode` | 快速開始遊戲 |
| `speak_and_next` | `text`, `next_speaker_id` | 發言並指定下一發言者 |
| `vote` | `target_id` | 投票 |
| `wolf_target` | `target_id` | 狼人選擇狩獵目標 |
| `seer_target` | `target_id` | 預言家選擇預言對象 |
| `witch_decision` | `save`, `poison_target` | 女巫決定（救人／毒人） |
| `wolf_chat` | `text` | 狼人夜間聊天 |
| `last_words` | `text` | 遺言 |
| `pause` | - | 暫停遊戲（房主專用） |
| `resume` | - | 恢復遊戲（房主專用） |

#### 伺服器 → 客戶端
| 訊息類型 | 說明 |
|---------|------|
| `room_joined` | 成功加入房間 |
| `room_members_update` | 房間成員更新 |
| `room_list` | 活動房間列表 |
| `message` | 遊戲消息 |
| `error` | 錯誤訊息 |
| `host_promoted` | 被提升為房主 |

## 配置選項

編輯 `backend/config.py` 調整以下參數：

```python
MIN_PLAYERS = 6          # 最少玩家數
MAX_PLAYERS = 12         # 最多玩家數
LLM_TIMEOUT = 60         # LLM 響應超時（秒）
LLM_MAX_RETRIES = 5      # LLM 最大重試次數

ROLE_DISTS = {           # 各人數下的角色分配
    6:  {"werewolf": 2, "villager": 2, "seer": 1, "witch": 1},
    # ... 其他配置
}
```

## 開發指南

### 目錄結構與職責
- **backend/main.py**：FastAPI 應用與 WebSocket 端點管理
- **backend/game.py**：遊戲邏輯、房間管理、玩家狀態
- **backend/llm.py**：LLM 整合與 AI 玩家回應生成
- **frontend/js/websocket.js**：WebSocket 通訊層
- **frontend/js/game.js**：遊戲 UI 邏輯
- **frontend/js/app.js**：應用程序初始化

### 添加新功能
1. 在 `backend/main.py` 的 WebSocket 端點添加新訊息類型
2. 在 `frontend/js/websocket.js` 實現客戶端處理
3. 編寫相應的 UI 邏輯到 `frontend/js/game.js` 或 `app.js`

### 自訂 AI 性格
編輯 `backend/game.py` 中 `Player.__init__` 的 `personality` 列表，修改 AI 發言特徵。

## 故障排除

### 連線問題
- 檢查防火牆是否允許 8765 埠
- 確認 WebSocket 未被代理攔截
- 瀏覽器控制台查看連線錯誤

### 遊戲卡頓
- 檢查 LLM API 響應時間
- 確認 `LLM_TIMEOUT` 設置足夠
- 考慮調整 `PRIMARY_MODEL` 為更快的備用模型

### AI 回應異常
- 驗證 API 金鑰有效性
- 檢查 `backend/llm.py` 中的模型配置
- 查看伺服器日誌確認 LLM 呼叫狀態

## 許可證

本專案遵循相應開源許可證（如有）。

## 貢獻

歡迎提交問題回報與改進建議！

## 聯繫方式

如有問題，請透過 GitHub Issues 聯繫或提交 Pull Request。

---

**版本**：1.0.0  
**最後更新**：2026 年 8 月
