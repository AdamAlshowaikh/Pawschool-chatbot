# Paws Chatbot 

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



## Free hosting (optional)

Ollama only runs on your own machine. To put the bot online for free, use Option B or C and deploy to a free tier such as Hugging Face Spaces (Docker) or Render. Free tiers change, so check their current limits.

## Known limits

- Memory lives in RAM and resets when the server restarts.
- Free API tiers have rate limits.
- Small local models make more mistakes than large hosted ones.
- No login, so do not expose it publicly without adding auth and rate limiting.


