# B99 Quote Guesser

A "Who Said It?" game for Brooklyn Nine-Nine fans. Guess the character and episode from each quote and build your streak.

---

## Features

- **Quote Challenge**: Identify the character and episode from masked B99 quotes
- **Streak Tracking**: Streak persists in browser localStorage (no account needed)

---

## Project Structure

```
holt/
├── api/
│   ├── main.py              # FastAPI app
│   └── routes/
│       └── game.py          # Game endpoints
├── core/
│   ├── config.py            # Environment config
│   ├── episodes.py          # Episode metadata
│   └── quotes.py            # B99 quotes loader
├── data/
│   └── quotes.json            # Full B99 quotes dataset
├── static/
│   ├── css/styles.css
│   └── js/game.js           # Game logic
├── templates/
│   ├── base.html
│   ├── index.html           # Landing page
│   └── game.html            # Game page
└── requirements.txt
```

---

## Quick Start

### 1. Clone & Install

```bash
cd holt
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Locally

```bash
uvicorn api.main:app --reload
```

Visit: http://localhost:8000

The app uses `data/quotes.json` by default. Override with `B99_QUOTES_JSON=path/to/quotes.json` if needed.

---

## API Endpoints

- `GET /` - Landing page
- `GET /game` - Game page
- `GET /game/quote` - Get random masked quote
- `GET /game/characters` - Character list for autocomplete
- `GET /game/episodes` - Episodes grouped by season
- `POST /game/verify` - Verify guess
- `GET /health` - Health check

---

*"Every problem has a solution. You just need to be smart enough to find it."* — Captain Raymond Holt
