"""Simple chatbot API. Works with any OpenAI-compatible provider (Ollama, Gemini, Groq)."""
import os
import sqlite3
import time
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()

BASE_DIR = Path(__file__).parent
BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
API_KEY = os.getenv("LLM_API_KEY", "ollama")
MODEL = os.getenv("LLM_MODEL", "llama3.2")
MAX_TURNS = int(os.getenv("MAX_TURNS", "10"))
DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "chat_logs.db"))
SYSTEM_PROMPT = (BASE_DIR / "system_prompt.txt").read_text(encoding="utf-8").strip()

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
app = FastAPI(title="Free Chatbot")

# Mount static folder so images, CSS, and JS load properly
app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory conversation history, keyed by session id.
sessions: dict[str, list[dict]] = {}


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL,
            session_id TEXT,
            user_msg TEXT,
            reply TEXT,
            latency_ms INTEGER,
            feedback INTEGER
        )"""
    )
    return conn


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    session_id: str | None = None


class ChatOut(BaseModel):
    reply: str
    session_id: str
    chat_id: int
    latency_ms: int


class FeedbackIn(BaseModel):
    chat_id: int
    value: int = Field(ge=-1, le=1)  # 1 = thumbs up, -1 = thumbs down


@app.get("/")
def index():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL}


@app.post("/chat", response_model=ChatOut)
def chat(body: ChatIn):
    sid = body.session_id or str(uuid.uuid4())
    history = sessions.setdefault(sid, [])
    history.append({"role": "user", "content": body.message})
    # Keep only the last N exchanges so the prompt stays small.
    history[: max(0, len(history) - MAX_TURNS * 2)]

    messages = [{"role": "system", "content": SYSTEM_PROMPT}, *history]
    start = time.perf_counter()
    try:
        resp = client.chat.completions.create(model=MODEL, messages=messages)
        reply = (resp.choices[0].message.content or "").strip()
    except Exception as exc:  # network, auth, rate limit, model not found
        history.pop()  # do not keep a user message that got no answer
        raise HTTPException(status_code=502, detail=f"LLM call failed: {exc}")
    latency_ms = int((time.perf_counter() - start) * 1000)

    history.append({"role": "assistant", "content": reply})

    conn = db()
    cur = conn.execute(
        "INSERT INTO chats (ts, session_id, user_msg, reply, latency_ms) VALUES (?,?,?,?,?)",
        (time.time(), sid, body.message, reply, latency_ms),
    )
    conn.commit()
    chat_id = cur.lastrowid
    conn.close()

    return ChatOut(reply=reply, session_id=sid, chat_id=chat_id, latency_ms=latency_ms)


@app.post("/feedback")
def feedback(body: FeedbackIn):
    conn = db()
    cur = conn.execute(
        "UPDATE chats SET feedback = ? WHERE id = ?", (body.value, body.chat_id)
    )
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="chat_id not found")
    return {"ok": True}


@app.get("/stats")
def stats():
    conn = db()
    row = conn.execute(
        """SELECT COUNT(*), AVG(latency_ms),
                   SUM(CASE WHEN feedback = 1 THEN 1 ELSE 0 END),
                   SUM(CASE WHEN feedback = -1 THEN 1 ELSE 0 END)
            FROM chats"""
    ).fetchone()
    conn.close()
    total, avg_latency, ups, downs = row
    return {
        "total_chats": total or 0,
        "avg_latency_ms": round(avg_latency or 0),
        "thumbs_up": ups or 0,
        "thumbs_down": downs or 0,
    }