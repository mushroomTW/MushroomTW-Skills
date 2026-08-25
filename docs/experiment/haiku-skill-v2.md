# 🐺 狼人殺 — AI 補位多人連線版

A real-time Werewolf (Mafia) game with AI player support, playable solo or with friends. One or more AI players can substitute for absent players, powered by large language models for natural gameplay.

## Table of Contents

- [About](#about)
- [Features](#features)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Limitations](#limitations)
- [License](#license)

## About

**狼人殺** (Werewolf) is a classic social deduction game where players are secretly assigned roles: werewolves (enemies), villagers (neutral), special roles like seer (investigator) and witch (support). During the day, players vote to eliminate one player; at night, werewolves eliminate a villager. The game ends when all werewolves or all villagers are eliminated.

This version adds two innovations:

1. **AI Supplementation**: Games automatically proceed even if players join mid-game or disconnect—AI players seamlessly take over absent roles with distinct personalities and reasoning.
2. **Social Modes**: Play solo to test strategies, watch AI-only games as an observer ("god mode"), or host a room for friends to join online.

Ideal for:
- Players learning Werewolf strategy
- Groups unable to gather a full table
- Understanding how LLMs handle social reasoning

## Features

- **Single-player mode**: Configure player count and roles, then play against AI opponents
- **Multiplayer rooms**: Create or join 4-digit room codes; public room browser for fast discovery
- **God mode (observation)**: Watch AI-only games with all roles visible
- **Live AI substitution**: Disconnect mid-game; AI takes your role instantly with continuity
- **Diverse AI personalities**: Werewolves and villagers adopt distinct speaking styles—cautious analysts, impulsive players, provocateurs, and more
- **Real-time gameplay**: WebSocket-based chat and actions with no polling delays
- **Role assignment**: Configurable player counts (6–12) automatically adjust role distribution

## Getting Started

### Prerequisites

- Python 3.8 or later
- pip (Python package manager)

### Installation

1. **Clone the repository** (or extract the project directory):
   ```bash
   cd wk2_haiku
   ```

2. **Install backend dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Set up API credentials** (required):
   - Edit `backend/config.py`
   - Set `API_KEY` to your Google Generative AI API key (free tier available at [Google AI Studio](https://aistudio.google.com/apikey))
   - Optionally adjust `PRIMARY_MODEL` and `FALLBACK_MODEL` (Gemini models are free)

### Running the Game

1. **Start the backend server**:
   ```bash
   cd backend
   python main.py
   ```
   The server starts at `http://localhost:8765`

2. **Open the frontend**:
   - Navigate to `http://localhost:8765` in your browser
   - The frontend is served statically from the backend

3. **Play**:
   - **Single player**: Select player count, adjust god mode toggle, then start
   - **Multiplayer**: Create a room, share the 4-digit code with friends, then start when everyone joins
   - **AI only**: Enable god mode to watch AI players run a full game

## Usage

### Gameplay Flow

1. **Setup Phase**: Select roles and player count. Real players set a nickname; AI fills remaining slots automatically.
2. **Night Phase**: Werewolves choose a target to eliminate; seer investigates a player; witch can save or poison.
3. **Day Phase**: All players discuss and vote to eliminate one player.
4. **Game End**: Werewolves win if they equal or outnumber villagers; villagers win if all werewolves are dead.

### Role Descriptions

| Role | Count | Ability |
|------|-------|---------|
| 🐺 Werewolf | 2–3 | Eliminate a villager each night; see other werewolves |
| 👤 Villager | 2–7 | No special power; vote and discuss |
| 🔮 Seer | 1 | Learn one player's role each night |
| 🧪 Witch | 1 | Each night, save one player OR poison one player (not both) |

### Commands and Controls

- **Create Room**: Enter a nickname, select player count, then click "建立房間" (Create Room)
- **Join Room**: Enter a 4-digit room code, then click "加入房間" (Join Room)
- **Speech Phase**: Type your argument in the text area; select the next speaker from the dropdown; click "發言" (Speak)
- **Vote Phase**: Select a target player from the dropdown; click "投票" (Vote)
- **Night Actions** (for special roles):
  - Werewolves: select a target villager to eliminate
  - Seer: select a player to investigate
  - Witch: check a box to save the seer's target OR select a target to poison

## Architecture

### Backend (FastAPI)

The backend manages game state, WebSocket connections, and AI calls:

- **`main.py`**: FastAPI server and WebSocket endpoint. Handles room creation, player joining, game actions (vote, speak, night actions), and static file serving.
- **`game.py`**: Core game engine (`GameEngine` class). Manages phases, role distribution, player elimination, AI action callbacks, and event broadcasting.
- **`llm.py`**: Interface to Google Generative AI models. Handles model calls, fallback logic, and prompt engineering for player personalities.
- **`config.py`**: Configuration for API key, model names, player count limits, role distributions, and role display names.

### Frontend (Vanilla JavaScript)

- **`index.html`**: Three-page layout—setup (single/multi tabs), room waiting area, game board.
- **`js/websocket.js`**: WebSocket connection and message handling.
- **`js/game.js`**: Game state, UI updates, role-specific input areas.
- **`js/app.js`**: Page transitions, event listeners, formatting.

### Data Flow

1. Player opens browser → backend serves `index.html`
2. Player clicks "Start" → WebSocket connects to `/ws` endpoint
3. Player sends `start_game` or `create_room` → backend creates `GameEngine` instance
4. `GameEngine.run()` orchestrates phases asynchronously
5. For AI turns, `GameEngine` calls LLM via `llm.py`; LLM returns text (move description, speech, vote reasoning)
6. Backend broadcasts events to all connected clients via WebSocket
7. Frontend updates UI based on event type (phase change, message, role reveal, game end)

## Configuration

Edit `backend/config.py` to adjust:

| Setting | Default | Purpose |
|---------|---------|---------|
| `API_KEY` | `"API"` | Google Generative AI API key (required) |
| `PRIMARY_MODEL` | `"gemma-4-26b-a4b-it"` | Main model for AI players (free tier) |
| `FALLBACK_MODEL` | `"gemini-3.1-flash-lite"` | Fallback model if primary fails (faster, lighter) |
| `LLM_TIMEOUT` | `60` | Max seconds to wait for LLM response |
| `LLM_MAX_RETRIES` | `5` | Max retry attempts on LLM failure |
| `MIN_PLAYERS` | `6` | Minimum player count (including AI) |
| `MAX_PLAYERS` | `12` | Maximum player count |
| `ROLE_DISTS` | Dict | Role counts per player count (e.g., 8 players → 2 werewolves, 4 villagers, 1 seer, 1 witch) |

### Example: Change the Primary Model

If you want to use a different Gemini model for better speed or cost:

```python
PRIMARY_MODEL = "gemini-3.1-flash"  # Faster, smaller model
FALLBACK_MODEL = "gemini-3.1-flash-lite"  # Even lighter fallback
```

See [Google AI Model Garden](https://ai.google.dev/models) for available models.

## Limitations

> [!IMPORTANT]
> This project requires a Google Generative AI API key. Free tier access is available but has rate limits. High-concurrency games may hit rate limits; commercial deployments should use paid tiers.

- **LLM Dependency**: All AI reasoning relies on LLM quality. Poor prompts or model limitations can result in illogical decisions.
- **Latency**: AI responses add 1–10 seconds per turn depending on model and load. Games are slower than face-to-face play.
- **Personalities Static**: AI personalities are predefined in `Player.__init__()`. They do not adapt to game state or learn.
- **No Persistence**: Game records are not saved. Closing the browser loses chat history and game state.
- **Chinese-Only UI**: Frontend is entirely in Traditional Chinese; multi-language support is not planned.
- **Single Server**: The project is designed for local deployment. Scaling to multiple servers requires refactoring room storage and WebSocket routing.

## License

No license file is present in this repository. The project status and licensing terms are not specified.

---

**Play thoughtfully.** Werewolf is a game of language and psychology. Use the chat to read players, catch contradictions, and build trust. Don't worry about winning—focus on the deduction.
