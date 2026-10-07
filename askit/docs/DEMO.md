# Demo script

Main question: **"What are the advantages and disadvantages of electric vehicles?"**

1. Show the architecture (docs/ARCHITECTURE.md), then the n8n workflow canvas.
2. Ask the question in the UI. Point out Researcher → Writer → Editor status, the answer, clickable sources, then play the audio.
3. Show the backend log lines (research started/completed, editor, TTS).
4. No keys / flaky Wi-Fi? Set `DEMO_MODE=true` and restart the backend: same flow, deterministic answer (EV question gets an EV answer), real Wikipedia source links, silent audio. Say clearly it is demo mode.
5. Mention Phase 2: RAG, voice input, Telegram/WhatsApp.
