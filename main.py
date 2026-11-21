"""Futurepath AI — backend API with email + password accounts.

Run:  uvicorn main:app --reload
Docs: http://127.0.0.1:8000/docs
"""
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator

import core
from data import SECTORS

COOKIE = "fp_session"


@asynccontextmanager
async def lifespan(_: FastAPI):
    core.init_db()
    yield


app = FastAPI(title="Futurepath AI", version="2.0.0", lifespan=lifespan)

# The app is served from this same server, so no CORS is needed. Only set CORS_ORIGINS if you
# host the frontend on a different address (then also expect cookie limits across sites).
_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
if _origins:
    app.add_middleware(CORSMiddleware, allow_origins=_origins, allow_credentials=True,
                       allow_methods=["*"], allow_headers=["*"])


# --------------------------------------------------------------------------- #
# Login helpers
# --------------------------------------------------------------------------- #
def current_user(request: Request) -> dict:
    """The signed-in student, from the session cookie. Raises 401 if there isn't one."""
    token = request.cookies.get(COOKIE)
    if token:
        with core.db() as conn:
            user = core.user_for_token(conn, token)
        if user:
            return user
    raise HTTPException(401, "Please sign in")


def _set_session_cookie(request: Request, response: Response, token: str) -> None:
    proto = request.headers.get("x-forwarded-proto", request.url.scheme).split(",")[0].strip()
    response.set_cookie(
        COOKIE, token, max_age=core.SESSION_DAYS * 86400, path="/",
        httponly=True, samesite="lax", secure=(proto == "https"),
    )


def _limit(key: str, limit: int, window: int, message: str) -> None:
    if not core.allow(key, limit, window):
        raise HTTPException(429, message)


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


# --------------------------------------------------------------------------- #
# Request models
# --------------------------------------------------------------------------- #
class SignupIn(BaseModel):
    name: str = Field("", max_length=200)
    email: str = Field("", max_length=320)
    password: str = Field("", max_length=500)


class LoginIn(BaseModel):
    email: str = Field("", max_length=320)
    password: str = Field("", max_length=500)


class ProfileIn(BaseModel):
    name: str = Field("Student", max_length=100)
    year: str = Field("Class 12", max_length=40)
    subjects: str = Field("", max_length=300)
    location: str = Field("", max_length=100)
    interests: str = Field("", max_length=1000)
    sectors: list[str] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def _name(cls, v: str) -> str:
        return v.strip() or "Student"

    @field_validator("subjects", "location", "interests", "year")
    @classmethod
    def _strip(cls, v: str) -> str:
        return v.strip()

    @field_validator("sectors")
    @classmethod
    def _sectors(cls, v: list[str]) -> list[str]:
        unknown = [s for s in v if s not in core.SECTOR_BY_ID]
        if unknown:
            raise ValueError(f"Unknown sector id(s): {', '.join(unknown)}")
        return list(dict.fromkeys(v))


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., max_length=4000)


class ChatIn(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: list[ChatTurn] = Field(default_factory=list)
    save_advice: bool = True

    @field_validator("message")
    @classmethod
    def _msg(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("message must not be blank")
        return v


# --------------------------------------------------------------------------- #
# Accounts
# --------------------------------------------------------------------------- #
@app.post("/api/auth/signup")
def signup(body: SignupIn, request: Request, response: Response):
    name = body.name.strip()
    email = core.normalize_email(body.email)
    if not name:
        raise HTTPException(400, "Please tell us your name.")
    if len(name) > 100:
        raise HTTPException(400, "That name is too long.")
    if not core.EMAIL_RE.match(email) or len(email) > 254:
        raise HTTPException(400, "Please enter a valid email address.")
    if len(body.password) < 8:
        raise HTTPException(400, "Your password needs at least 8 characters.")
    if len(body.password) > 128:
        raise HTTPException(400, "That password is too long (maximum 128 characters).")
    _limit(f"signup:{_client_ip(request)}", 10, 3600, "Too many sign-ups from this network. Please try again later.")

    with core.db() as conn:
        try:
            user = core.create_user(conn, email, body.password, name)
        except core.EmailTaken:
            raise HTTPException(409, "An account with this email already exists. Try signing in.") from None
        token = core.create_session(conn, user["id"])
    _set_session_cookie(request, response, token)
    return user


@app.post("/api/auth/login")
def login(body: LoginIn, request: Request, response: Response):
    email = core.normalize_email(body.email)
    _limit(f"login:{_client_ip(request)}|{email}", 10, 600,
           "Too many attempts. Please wait a few minutes and try again.")
    with core.db() as conn:
        user = core.authenticate(conn, email, body.password)
        if user is None:
            raise HTTPException(401, "Incorrect email or password.")
        token = core.create_session(conn, user["id"])
    _set_session_cookie(request, response, token)
    return user


@app.post("/api/auth/logout")
def logout(request: Request, response: Response):
    token = request.cookies.get(COOKIE)
    if token:
        with core.db() as conn:
            core.end_session(conn, token)
    response.delete_cookie(COOKIE, path="/")
    return {"ok": True}


@app.get("/api/auth/me")
def me(user: dict = Depends(current_user)):
    return user


# --------------------------------------------------------------------------- #
# Catalogue
# --------------------------------------------------------------------------- #
@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/sectors")
def list_sectors():
    return SECTORS


@app.get("/api/careers")
def list_careers(
    sector: str | None = Query(None, description="Sector id, or 'all'"),
    q: str | None = Query(None, description="Search title, exam, description or sector name"),
    user: dict = Depends(current_user),
):
    if sector and sector != "all" and sector not in core.SECTOR_BY_ID:
        raise HTTPException(404, f"Unknown sector '{sector}'")
    with core.db() as conn:
        saved = set(core.saved_ids(conn, user["id"]))
    return [core.career_out(c, saved) for c in core.search_careers(sector, q)]


@app.get("/api/careers/{career_id}")
def get_career(career_id: str, user: dict = Depends(current_user)):
    career = core.CAREER_BY_ID.get(career_id)
    if not career:
        raise HTTPException(404, "Career not found")
    with core.db() as conn:
        saved = set(core.saved_ids(conn, user["id"]))
    return core.career_out(career, saved)


# --------------------------------------------------------------------------- #
# Home dashboard and profile
# --------------------------------------------------------------------------- #
@app.get("/api/dashboard")
def dashboard(user: dict = Depends(current_user)):
    with core.db() as conn:
        profile = core.get_profile(conn, user["id"])
        saved = core.saved_ids(conn, user["id"])
        advice_count = core.count_advice(conn, user["id"])
    words = profile["name"].split()
    first_name = words[0] if words else "Student"
    return {
        "name": profile["name"],
        "first_name": first_name,
        "initial": first_name[0].upper(),
        "saved_count": len(saved),
        "advice_count": advice_count,
        "profile_completeness": core.profile_completeness(profile),
        "recommendations": [core.career_out(c, set(saved)) for c in core.recommendations(profile)],
    }


@app.get("/api/profile")
def read_profile(user: dict = Depends(current_user)):
    with core.db() as conn:
        profile = core.get_profile(conn, user["id"])
        return {
            **profile,
            "email": user["email"],
            "saved_count": len(core.saved_ids(conn, user["id"])),
            "advice_count": core.count_advice(conn, user["id"]),
            "completeness": core.profile_completeness(profile),
        }


@app.put("/api/profile")
def update_profile(body: ProfileIn, user: dict = Depends(current_user)):
    with core.db() as conn:
        profile = core.save_profile(conn, user["id"], body.model_dump())
        return {**profile, "completeness": core.profile_completeness(profile)}


@app.put("/api/profile/sectors/{sector_id}")
def toggle_profile_sector(sector_id: str, user: dict = Depends(current_user)):
    """Add the sector to the student's interests, or remove it if already there."""
    if sector_id not in core.SECTOR_BY_ID:
        raise HTTPException(404, "Unknown sector")
    with core.db() as conn:
        profile = core.get_profile(conn, user["id"])
        sectors = profile["sectors"]
        profile["sectors"] = [s for s in sectors if s != sector_id] if sector_id in sectors else [*sectors, sector_id]
        profile = core.save_profile(conn, user["id"], profile)
        saved = set(core.saved_ids(conn, user["id"]))
        return {**profile, "recommendations": [core.career_out(c, saved) for c in core.recommendations(profile)]}


# --------------------------------------------------------------------------- #
# Saved careers
# --------------------------------------------------------------------------- #
@app.get("/api/saved")
def list_saved(user: dict = Depends(current_user)):
    with core.db() as conn:
        ids = core.saved_ids(conn, user["id"])
    return [core.career_out(core.CAREER_BY_ID[i], set(ids)) for i in ids if i in core.CAREER_BY_ID]


@app.put("/api/saved/{career_id}")
def save_career(career_id: str, user: dict = Depends(current_user)):
    if career_id not in core.CAREER_BY_ID:
        raise HTTPException(404, "Career not found")
    with core.db() as conn:
        core.save_career(conn, user["id"], career_id)
        return {"career_id": career_id, "saved": True, "saved_count": len(core.saved_ids(conn, user["id"]))}


@app.delete("/api/saved/{career_id}")
def unsave_career(career_id: str, user: dict = Depends(current_user)):
    with core.db() as conn:
        core.unsave_career(conn, user["id"], career_id)
        return {"career_id": career_id, "saved": False, "saved_count": len(core.saved_ids(conn, user["id"]))}


# --------------------------------------------------------------------------- #
# Advice history + AI advisor
# --------------------------------------------------------------------------- #
@app.get("/api/advice")
def list_advice(user: dict = Depends(current_user)):
    with core.db() as conn:
        return core.list_advice(conn, user["id"])


@app.delete("/api/advice/{advice_id}")
def delete_advice(advice_id: int, user: dict = Depends(current_user)):
    with core.db() as conn:
        if not core.delete_advice(conn, user["id"], advice_id):
            raise HTTPException(404, "Advice not found")
        return {"deleted": advice_id}


@app.post("/api/chat")
def chat(body: ChatIn, user: dict = Depends(current_user)):
    """Career advisor. Uses Claude when ANTHROPIC_API_KEY is set, otherwise the built-in rules."""
    _limit(f"chat:{user['id']}", 30, 3600, "You’ve asked a lot of questions this hour. Please try again a little later.")
    with core.db() as conn:
        profile = core.get_profile(conn, user["id"])

    history = [t.model_dump() for t in body.history]
    reply = core.llm_reply(body.message, history, profile)
    source = "ai"
    if reply is None:
        reply, source = core.rule_based_reply(body.message, profile), "rules"

    advice = None
    with core.db() as conn:
        if body.save_advice:
            advice = core.add_advice(conn, user["id"], reply)
        advice_count = core.count_advice(conn, user["id"])
    return {"reply": reply, "source": source, "advice": advice, "advice_count": advice_count}



# --------------------------------------------------------------------------- #
# Study modules, YouTube videos and mock tests
# --------------------------------------------------------------------------- #
class SubmitIn(BaseModel):
    answers: list[int | None] = Field(default_factory=list, max_length=50)


def _career_or_404(career_id: str) -> dict:
    career = core.CAREER_BY_ID.get(career_id)
    if not career:
        raise HTTPException(404, "Career not found")
    return career


@app.get("/api/study/{career_id}")
def study_plan(career_id: str, user: dict = Depends(current_user)):
    _career_or_404(career_id)
    with core.db() as conn:
        return core.study_plan(conn, user["id"], career_id)


@app.put("/api/study/{career_id}/modules/{module_id}")
def complete_module(career_id: str, module_id: str, user: dict = Depends(current_user)):
    _career_or_404(career_id)
    if module_id not in {m["id"] for m in core.modules_for(career_id)}:
        raise HTTPException(404, "Module not found")
    with core.db() as conn:
        core.set_module_done(conn, user["id"], career_id, module_id, True)
        return core.study_plan(conn, user["id"], career_id)


@app.delete("/api/study/{career_id}/modules/{module_id}")
def uncomplete_module(career_id: str, module_id: str, user: dict = Depends(current_user)):
    _career_or_404(career_id)
    with core.db() as conn:
        core.set_module_done(conn, user["id"], career_id, module_id, False)
        return core.study_plan(conn, user["id"], career_id)


@app.get("/api/mocktest/{career_id}")
def mock_test(career_id: str, user: dict = Depends(current_user)):
    _career_or_404(career_id)
    return {"career_id": career_id, "questions": core.public_questions(career_id)}


@app.post("/api/mocktest/{career_id}/submit")
def submit_mock_test(career_id: str, body: SubmitIn, user: dict = Depends(current_user)):
    _career_or_404(career_id)
    _limit(f"mock:{user['id']}", 60, 3600, "You’ve submitted many tests this hour. Please take a short break.")
    outcome = core.grade(career_id, body.answers)
    with core.db() as conn:
        core.record_attempt(conn, user["id"], career_id, outcome["score"], outcome["total"])
        outcome["summary"] = core.test_summary(conn, user["id"], career_id)
    return outcome


# --------------------------------------------------------------------------- #
# Frontend
# --------------------------------------------------------------------------- #
@app.get("/", include_in_schema=False)
def index():
    page = core.BASE_DIR / "index.html"
    if page.exists():
        return FileResponse(page)
    return {"message": "Futurepath AI API is running. Visit /docs. Put index.html next to main.py to serve the UI."}
