# 🐺 狼人殺 — 智慧 AI 補位多人連線版

一個具有先進 AI 玩家的即時多人狼人殺（Werewolf/Mafia）遊戲，採用 FastAPI 後端與 WebSocket 實時通訊。由 Google Gemini/Gemma 模型驅動的 AI 玩家提供自然逼真的遊戲體驗。

## 目錄

- [特色](#特色)
- [快速開始](#快速開始)
- [遊戲玩法](#遊戲玩法)
- [技術棧](#技術棧)
- [專案結構](#專案結構)
- [配置](#配置)
- [開發](#開發)

## 特色

- **智慧 AI 玩家**：採用 Google Gemini/Gemma 模型，AI 玩家具備多種人格特徵（謹慎分析型、直覺情緒型、沉穩高冷型等），提供富有變化的遊戲體驗
- **即時多人遊戲**：基於 WebSocket 的實時通訊，支援 6-12 人同時進行
- **靈活的遊戲模式**：
  - 單人模式：觀看 AI 玩家之間的對戰（上帝模式）
  - 多人模式：與真人及 AI 玩家混合遊戲
- **無縫 AI 補位**：人類玩家斷線時，AI 自動接管該玩家，遊戲繼續進行
- **房間管理**：創建房間、加入現有房間、自動房主轉移等功能
- **動態角色配置**：根據玩家人數自動調配職業（狼人、村民、預言家、女巫）

## 快速開始

### 需求

- Python 3.9+
- Node.js（可選，不需要構建前端）
- Google AI API 金鑰（用於 Gemini/Gemma）

### 安裝與運行

1. **克隆或下載專案**

   ```bash
   git clone <repository-url>
   cd wk_haiku
   ```

2. **配置 API 金鑰**

   編輯 `backend/config.py`，設定你的 Google AI API 金鑰：

   ```python
   API_KEY = "your-google-ai-api-key"
   ```

3. **安裝後端依賴**

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **啟動伺服器**

   ```bash
   python main.py
   ```

   伺服器將在 `http://localhost:8765` 啟動。在瀏覽器中打開此地址即可開始遊戲。

## 遊戲玩法

### 遊戲角色

| 角色 | 描述 |
| --- | --- |
| 🐺 狼人 | 在夜間秘密投票消滅村民，目標是消滅所有村民 |
| 👤 村民 | 好人一方，通過白天投票消滅狼人 |
| 🔮 預言家 | 每晚可查看一名玩家的身份 |
| 🧪 女巫 | 擁有救人藥水（可救被狼人選中的人）和毒藥（可毒死一人） |

### 職業配置

遊戲會根據玩家人數自動配置職業。例如：

- **6 人遊戲**：2 狼人 + 2 村民 + 1 預言家 + 1 女巫
- **8 人遊戲**：2 狼人 + 4 村民 + 1 預言家 + 1 女巫
- **12 人遊戲**：3 狼人 + 7 村民 + 1 預言家 + 1 女巫

### 遊戲流程

1. **配置階段**：選擇玩家人數和遊戲模式
2. **角色分配**：系統隨機分配角色給所有玩家
3. **夜間階段**：
   - 狼人投票選擇要消滅的村民
   - 預言家選擇要查看身份的玩家
   - 女巫決定是否救人或投毒
4. **白天階段**：所有活著的玩家討論並投票消滅可疑的狼人
5. **勝負判定**：
   - 所有狼人被消滅 → 村民方勝利
   - 狼人數量 ≥ 村民數量 → 狼人方勝利

## 技術棧

### 後端

- **FastAPI**：現代化的 Python Web 框架
- **Uvicorn**：ASGI Web 伺服器
- **WebSockets**：實時雙向通訊
- **google-genai**：Google 生成式 AI SDK（Gemini/Gemma 模型）
- **Pydantic**：資料驗證與設定管理

### 前端

- **HTML5**：網頁結構
- **CSS3**：樣式與響應式設計
- **JavaScript**：用戶交互與 WebSocket 客戶端

## 專案結構

```
wk_haiku/
├── backend/
│   ├── main.py            # FastAPI 應用程式入口點，WebSocket 端點定義
│   ├── config.py          # 配置文件（API 金鑰、玩家數量限制、角色配置等）
│   ├── game.py            # 遊戲邏輯（Player、Room、GameEngine、LobbyManager）
│   ├── llm.py             # Google Gemini API 調用與重試邏輯
│   └── requirements.txt    # Python 依賴清單
├── frontend/
│   ├── index.html         # 主 HTML 文件（遊戲 UI）
│   ├── css/
│   │   └── style.css      # 遊戲樣式
│   └── js/
│       ├── app.js         # 主應用邏輯
│       ├── game.js        # 遊戲狀態與流程控制
│       └── websocket.js   # WebSocket 連線管理
├── .gitignore             # Git 忽略文件
└── README.md              # 本文件
```

## 配置

所有配置都在 `backend/config.py` 中設定：

```python
# Google AI API 配置
API_KEY = "your-api-key"
PRIMARY_MODEL = "gemma-4-26b-a4b-it"      # 主用模型（追求速度可互換備用模型）
FALLBACK_MODEL = "gemini-3.1-flash-lite"  # 備用模型（速度較快）
LLM_TIMEOUT = 60                          # AI 回應超時（秒）
LLM_MAX_RETRIES = 5                       # AI 調用失敗重試次數

# 遊戲配置
MIN_PLAYERS = 6                           # 最少玩家數
MAX_PLAYERS = 12                          # 最多玩家數

# 角色配置
ROLE_DISTS = {
    6:  {"werewolf": 2, "villager": 2, "seer": 1, "witch": 1},
    7:  {"werewolf": 2, "villager": 3, "seer": 1, "witch": 1},
    # ... 更多配置
}
```

### 環境變數

> [!IMPORTANT]
> 編輯 `backend/config.py` 直接設定 API 金鑰。**不要在版本控制中提交 `.env` 檔案**。`.gitignore` 已配置忽略 `.env`。

## 開發

### 後端開發

1. 安裝開發依賴：

   ```bash
   pip install -r requirements.txt
   ```

2. 運行開發伺服器（支援熱重載）：

   ```bash
   cd backend
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8765
   ```

3. 查看伺服器日誌以調試 AI 呼叫和遊戲流程

### 前端開發

前端為靜態資源，由後端服務。編輯 `frontend/` 下的 HTML/CSS/JS 檔案後，直接刷新瀏覽器即可看到變更。

### 除錯技巧

- **WebSocket 訊息**：在瀏覽器開發者工具 → Networks 標籤中檢查 WebSocket 連線
- **API 金鑰問題**：檢查 `config.py` 中的 `API_KEY` 是否正確設定，控制台會輸出 AI 呼叫的重試日誌
- **超時問題**：調整 `config.py` 中的 `LLM_TIMEOUT` 和 `LLM_MAX_RETRIES`

## 限制與已知問題

- **AI 模型依賴**：遊戲依賴 Google Gemini/Gemma API 的可用性和額度。超過配額時會觸發重試機制
- **連線穩定性**：長時間遊戲可能因網路波動導致連線中斷，UI 會顯示玩家已斷線且由 AI 補位
- **模型成本**：每次 AI 玩家決策都會消耗 API 配額，請監控使用情況

## 貢獻

歡迎提交問題報告和改進建議。

## 授權

本專案的授權條款請參考 LICENSE 檔案。
