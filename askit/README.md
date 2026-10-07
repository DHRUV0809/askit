# ASKIT — Voice-Enabled Multi-Agent Research Assistant

*Ask anything. Research everything.*

A user asks a question in a React UI → (optionally) an **n8n** webhook → **FastAPI** → a sequential **CrewAI** crew (**Researcher** with Tavily web search → **Writer** → **Editor**) → final answer + sources → **ElevenLabs** voice.

## Features
- 3-agent sequential CrewAI pipeline with tool calling (Tavily) and source de-duplication (only URLs the search tool returned)
- Structured Pydantic JSON responses, input validation (HTTP 400), friendly errors, logging, timeout
- ElevenLabs TTS through the backend (key never reaches the browser; MP3 returned as binary, Windows-safe)
- n8n importable workflow, dark React UI with agent status and audio player
- `DEMO_MODE=true` works with **no API keys**
- RAG-ready (`ResearchProvider` interface). **RAG is not implemented yet** (Phase 2); voice input and Telegram/WhatsApp are documented future phases only.

## Stack
Python 3.11–3.12, FastAPI, Uvicorn, Pydantic, CrewAI, OpenAI, Tavily, ElevenLabs, n8n, React + Vite (plain CSS), pytest, Docker (optional).

## Structure
```
askit/
├── backend/app/{main.py,config.py,api/,agents/,crew/,tools/,services/,models/}
├── backend/tests/        ├── frontend/src/{App.jsx,api.js,components/}
├── n8n/askit_workflow.json  ├── docs/{ARCHITECTURE,API,DEMO}.md
└── .env.example  .gitignore  docker-compose.yml
```

## Prerequisites
Python 3.11 or 3.12 (CrewAI does not support very new Python versions), Node 18+, optionally Docker and n8n. Keys: OpenAI, Tavily, ElevenLabs (+ a voice ID) — not needed for demo mode.

## Environment variables
Copy `.env.example` to `.env` (project root **or** `backend/`). Never commit it.

| Variable | Purpose |
|---|---|
| `OPENAI_API_KEY`, `OPENAI_MODEL` | LLM (default model `gpt-4o-mini`) |
| `TAVILY_API_KEY` | web search |
| `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID` | text-to-speech |
| `DEMO_MODE` | `true` = mock answers/audio, no external calls (default `false`) |
| `REQUEST_TIMEOUT_SECONDS` | `/api/ask` timeout (default 240) |
| `N8N_WEBHOOK_URL`, `BACKEND_URL`, `FRONTEND_URL` | integration URLs / CORS |

## Option A — local setup
Backend:
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows   (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env         # macOS/Linux: cp .env.example .env  -> fill in keys or set DEMO_MODE=true
uvicorn app.main:app --reload --port 8000
```
Frontend:
```bash
cd frontend
npm install
npm run dev                    # http://localhost:5173
```
## Option B — Docker
```bash
cp .env.example .env           # edit keys
docker compose up --build      # backend :8000, frontend :5173 (n8n is run separately)
```

## n8n
See `n8n/README.md`: import `n8n/askit_workflow.json`, activate, test with
`curl -X POST http://localhost:5678/webhook/askit -H "Content-Type: application/json" -d '{"query":"Explain machine learning"}'`.
Set `VITE_N8N_WEBHOOK_URL` in `frontend/.env` to route the UI through n8n.

## Testing
```bash
cd backend && pytest          # all external services mocked; no keys needed
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/ask -H "Content-Type: application/json" -d '{"query":"What is artificial intelligence?"}'
```
End to end: start backend (try `DEMO_MODE=true` first) → start frontend → ask "What are the advantages and disadvantages of electric vehicles?" → see agent status, answer, sources, audio. See `docs/DEMO.md`, `docs/API.md`.

## Troubleshooting
- **`pip install crewai` fails**: use Python 3.11/3.12 in a fresh venv.
- **503 "not configured"**: a key is missing in `.env`; or use `DEMO_MODE=true`. Restart uvicorn after editing `.env`.
- **CORS error in browser**: set `FRONTEND_URL` to the exact frontend origin.
- **n8n cannot reach backend**: use `http://host.docker.internal:8000` (n8n in Docker) or `http://localhost:8000` (n8n on host); `$env` access may need `N8N_BLOCK_ENV_ACCESS_IN_NODE=false`.
- **No audio**: check `ELEVENLABS_VOICE_ID`; the text answer still works without audio.

## Known limitations
Synchronous request (typically 10–60 s); agent status in the UI is simulated from timing; a timed-out crew may keep running in its thread until it finishes; TTS truncates at ~4500 characters; real Tavily/OpenAI/ElevenLabs/n8n flows need your keys and were verified here only through mocked tests and demo mode.

## Future improvements (Phase 2+)
RAG: PDF → loader → splitter → embeddings → Chroma → retriever as a `DocumentResearchProvider`. Voice input (Vapi / ElevenLabs STT) → n8n. Telegram via n8n; WhatsApp via a Business API provider. Streaming agent status, caching, auth.
