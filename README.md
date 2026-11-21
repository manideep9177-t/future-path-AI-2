# Futurepath AI — backend

FastAPI + SQLite, with email + password accounts. Every student has their own profile,
saved careers and advice. The login screen shows before the app opens.

## Run
    python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    python -m uvicorn main:app --reload
Open http://127.0.0.1:8000 (always use this address, not the file itself) or /docs for API docs.

## Optional: Claude-powered advisor
    export ANTHROPIC_API_KEY=sk-ant-...
    export ANTHROPIC_MODEL=claude-sonnet-5-5   # optional override
Without a key (or if the call fails) /api/chat uses the built-in rule-based advisor.

## Accounts
Passwords are hashed with scrypt; the browser holds only a random session token in an HttpOnly
cookie (30 days), and only its hash is stored. Login attempts, sign-ups and chat are rate limited.
Not included yet: "forgot password" emails and email verification (they need an email service).

## Endpoints (all except auth/health/sectors need a signed-in user)
| Method | Path | Purpose |
|---|---|---|
| POST | /api/auth/signup | `{name, email, password}` -> signs in |
| POST | /api/auth/login | `{email, password}` |
| POST | /api/auth/logout | |
| GET | /api/auth/me | Current user, or 401 |
| GET | /api/careers?sector=&q= | Explore / search (includes `saved` flag) |
| GET | /api/dashboard | Home stats + recommendations |
| GET / PUT | /api/profile | Read / save profile |
| PUT | /api/profile/sectors/{id} | Toggle a sector on the profile |
| GET | /api/saved | Saved careers |
| PUT / DELETE | /api/saved/{id} | Save / unsave |
| GET | /api/advice | Saved advice (newest first, max 20) |
| DELETE | /api/advice/{id} | Remove advice |
| POST | /api/chat | `{message, history?, save_advice?}` |

## Config (env vars)
FUTUREPATH_DB (sqlite path), APP_TZ (default Asia/Kolkata), ANTHROPIC_API_KEY, ANTHROPIC_MODEL,
CORS_ORIGINS (only if the frontend is hosted on a different address).

## Hosting note
On Render's free plan the SQLite file is wiped on restart, which would delete accounts. Use a paid
disk (set FUTUREPATH_DB=/data/futurepath.db) or move to Postgres before real users sign up.
