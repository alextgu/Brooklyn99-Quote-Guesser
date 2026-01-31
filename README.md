# 🦾 Holt Bot

A formal, high-efficiency bot for Brooklyn Nine-Nine enthusiasts. Delivers daily dispatches, quote challenges, and stoic wisdom in the style of Captain Raymond Holt.

---

## 📋 Feature Checklist

| Feature | Tech Stack | Description | Status |
|---------|------------|-------------|--------|
| Minimalist Landing Page | HTML5 / Tailwind CSS | A formal, high-efficiency UI for user enrollment | ✅ |
| Double Opt-In System | FastAPI / Resend API | Sends a formal "Invitation" email; users must click to confirm | ✅ |
| "Who Said It?" Game | JavaScript / B99 API | Interactive quote challenge with character autocomplete | ✅ |
| The Efficiency Sweep | Python / Supabase | Self-cleaning background task that deletes unconfirmed records >48hrs | ✅ |
| Daily Dispatch Engine | Python / Resend API | Constructs and sends "Daily Challenge" email (Quote + Holt Compliment) | ✅ |
| Anti-Duplicate Guard | Supabase (PostgreSQL) | Tracks `last_notified_at` to ensure exactly one dispatch per 24 hours | ✅ |
| The "Morning Alarm" | GitHub Actions (CRON) | Automated schedule that triggers dispatch at 08:00 daily | ✅ |

---

## 🗂️ Project Structure

```
holt/
├── .github/
│   └── workflows/
│       └── daily_dispatch.yml    # CRON job: 08:00 daily
├── api/
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry point
│   └── routes/
│       ├── __init__.py
│       ├── auth.py               # Signup, email confirmation
│       └── game.py               # "Who Said It?" game endpoints
├── core/
│   ├── __init__.py
│   ├── config.py                 # Centralized environment config
│   ├── database.py               # Supabase operations
│   ├── mailer.py                 # Resend email functions
│   ├── bot_logic.py              # Holt message generation
│   └── quotes.py                 # B99 API client
├── scripts/
│   ├── run_daily.py              # Daily dispatch script
│   └── run_purge.py              # Efficiency sweep script
├── static/
│   ├── css/
│   │   └── styles.css            # Custom styles
│   └── js/
│       └── game.js               # Game logic
├── templates/
│   ├── base.html                 # Base template (Tailwind)
│   ├── index.html                # Landing page
│   ├── signup_success.html       # Post-signup confirmation
│   ├── signup_error.html         # Signup error page
│   ├── confirm_success.html      # Email confirmed
│   ├── confirm_error.html        # Confirmation error
│   └── game.html                 # "Who Said It?" game
├── .env.example                  # Environment template
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
cd holt
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Set Up Supabase

Create a `users` table in Supabase with this schema:

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    confirmed BOOLEAN DEFAULT FALSE,
    signup_date TIMESTAMPTZ DEFAULT NOW(),
    last_notified_at TIMESTAMPTZ
);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Allow inserts from anon key
CREATE POLICY "Allow public signup" ON users
    FOR INSERT WITH CHECK (true);

-- Allow updates for confirmation
CREATE POLICY "Allow confirmation update" ON users
    FOR UPDATE USING (true);
```

### 4. Run Locally

```bash
uvicorn api.main:app --reload
```

Visit: http://localhost:8000

---

## 📡 API Endpoints

### Authentication
- `GET /` - Landing page
- `POST /signup` - Register new user
- `GET /confirm?email=...` - Confirm email address

### Game
- `GET /game` - Game page
- `GET /game/quote` - Get random masked quote
- `GET /game/characters` - List characters for autocomplete
- `POST /game/verify` - Verify answer
- `GET /game/search` - Search quote database

### Utility
- `GET /health` - Service health check

---

## ⚙️ GitHub Actions Secrets

For the daily CRON to work, add these secrets to your repository:

| Secret | Description |
|--------|-------------|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_ANON_KEY` | Supabase anon/public key |
| `SUPABASE_SERVICE_KEY` | Supabase service role key |
| `RESEND_API_KEY` | Resend API key |
| `BASE_URL` | Your deployed app URL |
| `B99_API_URL` | (Optional) B99 API URL override |

---

## 🧪 Manual Script Execution

### Run Daily Dispatch
```bash
python scripts/run_daily.py
```

### Run Efficiency Sweep
```bash
python scripts/run_purge.py
```

---

## 🌐 Deployment

### Render
1. Connect your GitHub repository
2. Set environment variables
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

### Vercel
Deploy as a Python serverless function or use the FastAPI adapter.

---

## 📝 License

MIT

---

*"Every problem has a solution. You just need to be smart enough to find it."*
— Captain Raymond Holt
