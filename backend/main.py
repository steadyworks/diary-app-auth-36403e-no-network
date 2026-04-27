from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
from passlib.context import CryptContext
import sqlite3
import os
from datetime import datetime, timezone

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
DB_PATH = os.environ.get("DB_PATH", "/app/backend/diary.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            mood TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()


init_db()


def require_auth(request: Request) -> int:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user_id


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


@app.post("/api/auth/signup", status_code=201)
async def signup(request: Request):
    data = await request.json()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")
    conn = get_db()
    try:
        hashed = pwd_context.hash(password)
        cursor = conn.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            (email, hashed),
        )
        user_id = cursor.lastrowid
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already registered")
    finally:
        conn.close()
    request.session["user_id"] = user_id
    return {"id": user_id, "email": email}


@app.post("/api/auth/login")
async def login(request: Request):
    data = await request.json()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")
    conn = get_db()
    try:
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
    finally:
        conn.close()
    if not user or not pwd_context.verify(password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    request.session["user_id"] = user["id"]
    return {"id": user["id"], "email": user["email"]}


@app.post("/api/auth/logout")
async def logout(request: Request):
    request.session.clear()
    return {"ok": True}


@app.get("/api/auth/me")
async def me(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    conn = get_db()
    try:
        user = conn.execute(
            "SELECT id, email FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    finally:
        conn.close()
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"id": user["id"], "email": user["email"]}


@app.get("/api/entries")
async def list_entries(request: Request):
    user_id = require_auth(request)
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT * FROM entries WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
    finally:
        conn.close()
    return [dict(row) for row in rows]


@app.post("/api/entries", status_code=201)
async def create_entry(request: Request):
    user_id = require_auth(request)
    data = await request.json()
    title = data.get("title", "").strip()
    body = data.get("body", "").strip()
    mood = data.get("mood", "")
    if not title or not body or mood not in ("happy", "neutral", "sad"):
        raise HTTPException(status_code=400, detail="title, body, and valid mood required")
    now = now_utc()
    conn = get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO entries (user_id, title, body, mood, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, title, body, mood, now, now),
        )
        entry_id = cursor.lastrowid
        conn.commit()
        entry = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
    finally:
        conn.close()
    return dict(entry)


@app.get("/api/entries/{entry_id}")
async def get_entry(entry_id: int, request: Request):
    user_id = require_auth(request)
    conn = get_db()
    try:
        entry = conn.execute(
            "SELECT * FROM entries WHERE id = ? AND user_id = ?",
            (entry_id, user_id),
        ).fetchone()
    finally:
        conn.close()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return dict(entry)


@app.put("/api/entries/{entry_id}")
async def update_entry(entry_id: int, request: Request):
    user_id = require_auth(request)
    data = await request.json()
    title = data.get("title", "").strip()
    body = data.get("body", "").strip()
    mood = data.get("mood", "")
    if not title or not body or mood not in ("happy", "neutral", "sad"):
        raise HTTPException(status_code=400, detail="title, body, and valid mood required")
    now = now_utc()
    conn = get_db()
    try:
        result = conn.execute(
            "UPDATE entries SET title=?, body=?, mood=?, updated_at=? WHERE id=? AND user_id=?",
            (title, body, mood, now, entry_id, user_id),
        )
        conn.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Entry not found")
        entry = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
    finally:
        conn.close()
    return dict(entry)


@app.delete("/api/entries/{entry_id}", status_code=204)
async def delete_entry(entry_id: int, request: Request):
    user_id = require_auth(request)
    conn = get_db()
    try:
        result = conn.execute(
            "DELETE FROM entries WHERE id = ? AND user_id = ?",
            (entry_id, user_id),
        )
        conn.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Entry not found")
    finally:
        conn.close()
    return Response(status_code=204)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)
