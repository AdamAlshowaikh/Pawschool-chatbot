# Paws Chatbot (free, one-day build)

A small chatbot API with a chat page. It works with any OpenAI-compatible provider, so you can run it fully free and offline with Ollama, or use a free-tier API key from Gemini or Groq.

## Features

- `POST /chat` with per-session memory (last 10 exchanges)
- Chat page at `/` with thumbs up/down feedback
- Every chat logged to SQLite (question, reply, latency, feedback)
- `GET /stats` for total chats, average latency and feedback counts
- Editable personality in `system_prompt.txt`
- Keys kept in `.env`, never in code

## Run it

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # Windows: copy .env.example .env
```

**Option A, Ollama (no account, fully free):**
1. Install Ollama from ollama.com.
2. Run `ollama pull llama3.2` (a small model; needs roughly 2 GB of disk and 4 GB of RAM).
3. Leave `.env` as it is.

**Option B or C:** uncomment that block in `.env`, paste your free key, and comment out Option A.

Start the server:

```bash
uvicorn app:app --reload
```

Open http://localhost:8000.

## Suggested plan for the day

| Time | Task |
|---|---|
| Hour 1 | Install, run it, change the system prompt to your own topic |
| Hour 2 | Try 20 questions, note where answers are weak, improve the prompt |
| Hour 3 | Read `app.py` line by line until you can explain each part |
| Hour 4 | Add one test: call `/chat` with `pytest` and `fastapi.testclient` |
| Hour 5 | Push to GitHub (check that `.env` and `chat_logs.db` are in `.gitignore`) |
| Hour 6 | Write up what you built, what it can't do, and what you would add next |

## Free hosting (optional)

Ollama only runs on your own machine. To put the bot online for free, use Option B or C and deploy to a free tier such as Hugging Face Spaces (Docker) or Render. Free tiers change, so check their current limits.

## Known limits

- Memory lives in RAM and resets when the server restarts.
- Free API tiers have rate limits.
- Small local models make more mistakes than large hosted ones.
- No login, so do not expose it publicly without adding auth and rate limiting.

## Next steps (to make it job-relevant)

1. Add RAG: embed your own documents and answer only from them.
2. Add one tool call (for example a weather or booking lookup).
3. Build a 30 question test set and score answers automatically.
4. Dockerize it and add GitHub Actions CI.
