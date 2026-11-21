"""Accounts, storage and advisor logic for Futurepath AI (no web-framework imports)."""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import re
import secrets
import sqlite3
import time
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator

from data import CAREERS, SECTORS
from study import grade, modules_for, questions_for

log = logging.getLogger("futurepath")

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = os.getenv("FUTUREPATH_DB", str(BASE_DIR / "futurepath.db"))
MAX_ADVICE = 20  # each student keeps their 20 most recent pieces of advice
SESSION_DAYS = 30
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")

SECTOR_BY_ID = {s["id"]: s for s in SECTORS}
CAREER_BY_ID = {c["id"]: c for c in CAREERS}
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

try:  # dates shown to the student ("18 Nov") use this timezone
    from zoneinfo import ZoneInfo

    DISPLAY_TZ = ZoneInfo(os.getenv("APP_TZ", "Asia/Kolkata"))
except Exception:  # tzdata missing (e.g. some Windows installs)
    DISPLAY_TZ = timezone.utc


# --------------------------------------------------------------------------- #
# Database
# --------------------------------------------------------------------------- #
@contextmanager
def db() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def init_db() -> None:
    with db() as conn:
        # Version 1 of this app was single-user (profile.id = 1, no accounts). Its demo data
        # can't be attached to anyone, so drop those tables and recreate them per user.
        cols = [r["name"] for r in conn.execute("PRAGMA table_info(profile)")]
        if cols and "user_id" not in cols:
            conn.executescript("DROP TABLE IF EXISTS profile; DROP TABLE IF EXISTS saved; DROP TABLE IF EXISTS advice;")
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                email         TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                name          TEXT NOT NULL,
                created_at    TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token_hash TEXT PRIMARY KEY,
                user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                expires_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS profile (
                user_id   INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                name      TEXT NOT NULL,
                year      TEXT NOT NULL,
                subjects  TEXT NOT NULL DEFAULT '',
                location  TEXT NOT NULL DEFAULT '',
                interests TEXT NOT NULL DEFAULT '',
                sectors   TEXT NOT NULL DEFAULT '[]'
            );
            CREATE TABLE IF NOT EXISTS saved (
                user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                career_id  TEXT NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (user_id, career_id)
            );
            CREATE TABLE IF NOT EXISTS advice (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                text       TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_advice_user ON advice (user_id, id);
            CREATE TABLE IF NOT EXISTS module_done (
                user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                career_id  TEXT NOT NULL,
                module_id  TEXT NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (user_id, career_id, module_id)
            );
            CREATE TABLE IF NOT EXISTS test_attempts (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                career_id  TEXT NOT NULL,
                score      INTEGER NOT NULL,
                total      INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_attempts_user ON test_attempts (user_id, career_id, id);
            """
        )
        conn.execute("DELETE FROM sessions WHERE expires_at < ?", (_now(),))


# --------------------------------------------------------------------------- #
# Accounts: passwords, users, sessions
# --------------------------------------------------------------------------- #
class EmailTaken(Exception):
    pass


_SCRYPT = {"n": 2**14, "r": 8, "p": 1, "dklen": 32}


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, **_SCRYPT)
    return f"scrypt${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, salt_hex, digest_hex = stored.split("$")
        if scheme != "scrypt":
            return False
        digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex), **_SCRYPT)
        return hmac.compare_digest(digest, bytes.fromhex(digest_hex))
    except Exception:
        return False


_DUMMY_HASH = hash_password("not-a-real-password")  # so unknown emails take as long as wrong passwords


def normalize_email(email: str) -> str:
    return email.strip().lower()


def create_user(conn: sqlite3.Connection, email: str, password: str, name: str) -> dict:
    try:
        cur = conn.execute(
            "INSERT INTO users (email, password_hash, name, created_at) VALUES (?, ?, ?, ?)",
            (email, hash_password(password), name, _now()),
        )
    except sqlite3.IntegrityError:
        raise EmailTaken(email) from None
    uid = cur.lastrowid
    conn.execute(
        "INSERT INTO profile (user_id, name, year, subjects, location, interests, sectors) "
        "VALUES (?, ?, 'Class 12', '', '', '', '[]')",
        (uid, name),
    )
    return {"id": uid, "email": email, "name": name}


def authenticate(conn: sqlite3.Connection, email: str, password: str) -> dict | None:
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    ok = verify_password(password, row["password_hash"] if row else _DUMMY_HASH)
    if row is None or not ok:
        return None
    return {"id": row["id"], "email": row["email"], "name": row["name"]}


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()  # only the hash is stored, never the token


def create_session(conn: sqlite3.Connection, user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    expires = (datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS)).isoformat(timespec="seconds")
    conn.execute(
        "INSERT INTO sessions (token_hash, user_id, expires_at) VALUES (?, ?, ?)",
        (_token_hash(token), user_id, expires),
    )
    return token


def user_for_token(conn: sqlite3.Connection, token: str) -> dict | None:
    row = conn.execute(
        "SELECT u.id, u.email, u.name FROM sessions s JOIN users u ON u.id = s.user_id "
        "WHERE s.token_hash = ? AND s.expires_at > ?",
        (_token_hash(token), _now()),
    ).fetchone()
    return dict(row) if row else None


def end_session(conn: sqlite3.Connection, token: str) -> None:
    conn.execute("DELETE FROM sessions WHERE token_hash = ?", (_token_hash(token),))


_HITS: dict[str, list[float]] = {}


def allow(key: str, limit: int, window_seconds: int) -> bool:
    """Sliding-window rate limit kept in memory (resets when the server restarts)."""
    now = time.monotonic()
    hits = [t for t in _HITS.get(key, []) if now - t < window_seconds]
    if len(hits) >= limit:
        _HITS[key] = hits
        return False
    hits.append(now)
    _HITS[key] = hits
    return True


# --------------------------------------------------------------------------- #
# Profile
# --------------------------------------------------------------------------- #
def get_profile(conn: sqlite3.Connection, user_id: int) -> dict:
    row = conn.execute("SELECT * FROM profile WHERE user_id = ?", (user_id,)).fetchone()
    if row is None:  # should not happen, but never leave a logged-in student without a profile
        name = conn.execute("SELECT name FROM users WHERE id = ?", (user_id,)).fetchone()["name"]
        conn.execute(
            "INSERT INTO profile (user_id, name, year) VALUES (?, ?, 'Class 12')", (user_id, name)
        )
        row = conn.execute("SELECT * FROM profile WHERE user_id = ?", (user_id,)).fetchone()
    p = dict(row)
    p.pop("user_id")
    p["sectors"] = json.loads(p["sectors"])
    return p


def save_profile(conn: sqlite3.Connection, user_id: int, p: dict) -> dict:
    get_profile(conn, user_id)  # makes sure the row exists
    conn.execute(
        "UPDATE profile SET name=?, year=?, subjects=?, location=?, interests=?, sectors=? WHERE user_id = ?",
        (p["name"], p["year"], p["subjects"], p["location"], p["interests"], json.dumps(p["sectors"]), user_id),
    )
    return get_profile(conn, user_id)


def profile_completeness(p: dict) -> int:
    checks = [
        p["name"] and p["name"] != "Student",
        p["year"],
        p["subjects"].strip(),
        p["location"].strip(),
        p["interests"].strip(),
        p["sectors"],
    ]
    return round(100 * sum(bool(c) for c in checks) / len(checks))


# --------------------------------------------------------------------------- #
# Careers, saved careers, advice
# --------------------------------------------------------------------------- #
def saved_ids(conn: sqlite3.Connection, user_id: int) -> list[str]:
    rows = conn.execute(
        "SELECT career_id FROM saved WHERE user_id = ? ORDER BY created_at, rowid", (user_id,)
    ).fetchall()
    return [r["career_id"] for r in rows]


def save_career(conn: sqlite3.Connection, user_id: int, career_id: str) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO saved (user_id, career_id, created_at) VALUES (?, ?, ?)",
        (user_id, career_id, _now()),
    )


def unsave_career(conn: sqlite3.Connection, user_id: int, career_id: str) -> None:
    conn.execute("DELETE FROM saved WHERE user_id = ? AND career_id = ?", (user_id, career_id))


def career_out(c: dict, saved: set[str]) -> dict:
    return {**c, "sector_name": SECTOR_BY_ID[c["sector"]]["name"], "saved": c["id"] in saved}


def search_careers(sector: str | None, q: str | None) -> list[dict]:
    term = (q or "").strip().lower()
    out = []
    for c in CAREERS:
        if sector and sector != "all" and c["sector"] != sector:
            continue
        haystack = f"{c['title']}{c['exam']}{c['desc']}{SECTOR_BY_ID[c['sector']]['name']}".lower()
        if term and term not in haystack:
            continue
        out.append(c)
    return out


def recommendations(profile: dict, limit: int = 3) -> list[dict]:
    rec = [c for c in CAREERS if c["sector"] in profile["sectors"]][:limit]
    return rec or CAREERS[:limit]


def fmt_advice(row: sqlite3.Row) -> dict:
    dt = datetime.fromisoformat(row["created_at"]).astimezone(DISPLAY_TZ)
    return {
        "id": row["id"],
        "text": row["text"],
        "date": f"{dt.day} {dt.strftime('%b')}",  # e.g. "18 Nov", as the frontend displays it
        "created_at": row["created_at"],
    }


def list_advice(conn: sqlite3.Connection, user_id: int) -> list[dict]:
    rows = conn.execute("SELECT * FROM advice WHERE user_id = ? ORDER BY id DESC", (user_id,))
    return [fmt_advice(r) for r in rows]


def count_advice(conn: sqlite3.Connection, user_id: int) -> int:
    return conn.execute("SELECT COUNT(*) FROM advice WHERE user_id = ?", (user_id,)).fetchone()[0]


def add_advice(conn: sqlite3.Connection, user_id: int, text: str) -> dict:
    cur = conn.execute(
        "INSERT INTO advice (user_id, text, created_at) VALUES (?, ?, ?)", (user_id, text, _now())
    )
    conn.execute(
        "DELETE FROM advice WHERE user_id = ? AND id NOT IN "
        "(SELECT id FROM advice WHERE user_id = ? ORDER BY id DESC LIMIT ?)",
        (user_id, user_id, MAX_ADVICE),
    )
    return fmt_advice(conn.execute("SELECT * FROM advice WHERE id = ?", (cur.lastrowid,)).fetchone())


def delete_advice(conn: sqlite3.Connection, user_id: int, advice_id: int) -> bool:
    cur = conn.execute("DELETE FROM advice WHERE id = ? AND user_id = ?", (advice_id, user_id))
    return cur.rowcount > 0



# --------------------------------------------------------------------------- #
# Study modules and mock tests
# --------------------------------------------------------------------------- #
def done_modules(conn: sqlite3.Connection, user_id: int, career_id: str) -> set[str]:
    rows = conn.execute(
        "SELECT module_id FROM module_done WHERE user_id = ? AND career_id = ?", (user_id, career_id)
    ).fetchall()
    return {r["module_id"] for r in rows}


def set_module_done(conn: sqlite3.Connection, user_id: int, career_id: str, module_id: str, done: bool) -> None:
    if done:
        conn.execute(
            "INSERT OR IGNORE INTO module_done (user_id, career_id, module_id, created_at) VALUES (?, ?, ?, ?)",
            (user_id, career_id, module_id, _now()),
        )
    else:
        conn.execute(
            "DELETE FROM module_done WHERE user_id = ? AND career_id = ? AND module_id = ?",
            (user_id, career_id, module_id),
        )


def record_attempt(conn: sqlite3.Connection, user_id: int, career_id: str, score: int, total: int) -> None:
    conn.execute(
        "INSERT INTO test_attempts (user_id, career_id, score, total, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, career_id, score, total, _now()),
    )


def test_summary(conn: sqlite3.Connection, user_id: int, career_id: str) -> dict:
    rows = conn.execute(
        "SELECT score, total, created_at FROM test_attempts WHERE user_id = ? AND career_id = ? ORDER BY id DESC",
        (user_id, career_id),
    ).fetchall()
    attempts = [dict(r) for r in rows]
    best = max((a["score"] for a in attempts), default=None)
    return {
        "attempts": len(attempts),
        "best": best,
        "total": len(questions_for(career_id)),
        "last": attempts[0]["score"] if attempts else None,
        "history": [
            {"score": a["score"], "total": a["total"],
             "date": f"{(d := datetime.fromisoformat(a['created_at']).astimezone(DISPLAY_TZ)).day} {d.strftime('%b')}"}
            for a in attempts[:5]
        ],
    }


def study_plan(conn: sqlite3.Connection, user_id: int, career_id: str) -> dict:
    done = done_modules(conn, user_id, career_id)
    modules = [{**mod, "done": mod["id"] in done} for mod in modules_for(career_id)]
    return {
        "career": career_out(CAREER_BY_ID[career_id], set(saved_ids(conn, user_id))),
        "modules": modules,
        "modules_done": sum(m["done"] for m in modules),
        "test": test_summary(conn, user_id, career_id),
    }


def public_questions(career_id: str) -> list[dict]:
    """Questions without the answers, so the browser cannot read them before submitting."""
    return [{"text": q["text"], "options": q["options"]} for q in questions_for(career_id)]


# --------------------------------------------------------------------------- #
# Advisor
# --------------------------------------------------------------------------- #
# Extra words that point to a sector, beyond the first word of its name.
SECTOR_KEYWORDS = {
    "civil": ["upsc", "ias", "ifs", "irs", "administrat", "government", "policy", "diplomac", "collector"],
    "defence": ["army", "navy", "air force", "military", "nda", "officer", "soldier", "pilot"],
    "banking": ["bank", "finance", "economics", "economy", "rbi", "money", "accountan"],
    "science": ["scien", "space", "isro", "drdo", "research", "physics", "chemistry", "technology"],
    "engineering": ["engineer", "construction", "infrastructure", "mechanical", "civil engineering", "electrical"],
    "health": ["doctor", "medic", "neet", "hospital", "biology", "nurse"],
    "education": ["teach", "school", "ctet", "professor", "student learning"],
    "law": ["lawyer", "judge", "judicial", "court", "justice", "llb", "legal"],
}


def _sector_hits(text: str) -> set[str]:
    text = text.lower()
    hits = set()
    for s in SECTORS:
        words = [s["name"].lower().split()[0], *SECTOR_KEYWORDS.get(s["id"], [])]
        if any(re.search(r"\b" + re.escape(w), text) for w in words):
            hits.add(s["id"])
    return hits


def suggest_careers(message: str, profile: dict, limit: int = 3) -> list[dict]:
    """Careers that fit the question first, then the student's profile; best match first."""
    from_question = _sector_hits(message)
    from_profile = _sector_hits(f"{profile['interests']} {profile['subjects']}") | set(profile["sectors"])
    by_match = sorted(CAREERS, key=lambda c: -c["match"])
    ordered = [c for c in by_match if c["sector"] in from_question]
    ordered += [c for c in by_match if c["sector"] in from_profile and c["sector"] not in from_question]
    return (ordered or by_match)[:limit]


def rule_based_reply(message: str, profile: dict) -> str:
    matches = suggest_careers(message, profile)
    subjects = f" — especially your interest in {profile['subjects']}" if profile["subjects"] else ""
    items = "\n\n".join(
        f"• {c['title']} ({c['match']}% interest match)\n  {c['desc']}\n  Exam: {c['exam']}\n  Eligibility: {c['eligibility']}"
        for c in matches
    )
    return (
        f"From what you’ve shared{subjects} — here are a few paths worth exploring:\n\n{items}\n\n"
        "A good next step is to compare the subjects and preparation each path needs. "
        "Which one would you like to learn more about?"
    )


def llm_reply(message: str, history: list[dict], profile: dict) -> str | None:
    """Ask Claude for advice. Returns None if no API key / SDK, or on any error (caller falls back)."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        return None
    try:
        import anthropic
    except ImportError:
        log.warning("ANTHROPIC_API_KEY is set but the 'anthropic' package is not installed")
        return None

    catalogue = "\n".join(
        f"- {c['title']} [{SECTOR_BY_ID[c['sector']]['name']}] exam: {c['exam']}; eligibility: {c['eligibility']}"
        for c in CAREERS
    )
    system = (
        "You are the Futurepath Guide, a warm, practical career advisor for Indian students exploring "
        "government and public-service careers.\n"
        f"Student: {profile['name']}, {profile['year']}. Subjects: {profile['subjects'] or 'not shared'}. "
        f"Interests: {profile['interests'] or 'not shared'}. Location: {profile['location'] or 'not shared'}.\n\n"
        f"Careers in the app:\n{catalogue}\n\n"
        "Rules: reply in plain text only (no markdown), under 180 words. Prefer the careers above and be "
        "honest that exam patterns, age limits and eligibility change, so the student should confirm them on "
        "the official notification. End with one question that helps the student take a next step."
    )
    messages = [{"role": t["role"], "content": t["content"]} for t in history[-10:]]
    messages.append({"role": "user", "content": message})
    try:
        client = anthropic.Anthropic()
        resp = client.messages.create(
            model=ANTHROPIC_MODEL, max_tokens=700, system=system, messages=messages
        )
        text = "".join(b.text for b in resp.content if b.type == "text").strip()
        return text or None
    except Exception as exc:  # network, auth, bad history shape, ...
        log.warning("Claude call failed, using rule-based advisor: %s", exc)
        return None
