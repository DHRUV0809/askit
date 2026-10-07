# Architecture

```
USER -> React frontend -> n8n webhook -> FastAPI /api/ask -> CrewAI (sequential)
                                                              Researcher <-> Tavily
                                                              Writer -> Editor -> final answer
USER <- audio <- FastAPI /api/tts <- ElevenLabs <- (answer)
```

1. **Frontend** (React + Vite, plain CSS): question box, simulated agent pipeline, Markdown answer, sources, audio player. Calls n8n if `VITE_N8N_WEBHOOK_URL` is set, otherwise FastAPI directly. Holds no secrets.
2. **n8n**: Webhook → `/api/ask` → `/api/tts` → Respond. Orchestration/automation layer; also the entry point for future Telegram/voice channels.
3. **FastAPI**: validation (400 on bad input), CORS, logging, timeout, friendly errors (`ServiceError`), Pydantic response models. Runs the blocking crew in a worker thread.
4. **CrewAI**: `Process.sequential`; task 2 receives task 1 output and task 3 receives both via `context`.
5. **Researcher**: uses `web_search` tool through a `ResearchProvider`. Sources are collected only from URLs the tool returned (deduplicated).
6. **Tavily**: REST call, max 5 results, handles invalid key / rate limit / network / empty results.
7. **Writer**: turns notes into a structured draft using only the research.
8. **Editor**: fact-checks research vs draft, strips unsupported claims, returns the final answer.
9. **ElevenLabs**: `tts_service` strips Markdown, truncates to ~4500 chars, returns MP3 bytes (no files written, so Windows-safe).
10. **Future RAG (Phase 2, not implemented)**: add `DocumentResearchProvider(ResearchProvider)` (PDF → loader → splitter → embeddings → Chroma → retriever) and register it as an extra tool; the pipeline is unchanged.

```
Query --+--> DocumentResearchProvider (Phase 2) --+
        +--> WebResearchProvider (Tavily) --------+--> Researcher -> Writer -> Editor
```
Future channels: Voice input (Vapi / ElevenLabs STT) → n8n → AskIt → TTS; Telegram → n8n → FastAPI → ElevenLabs → Telegram; WhatsApp via a Business API provider.
