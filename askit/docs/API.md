# AskIt API

Base URL: `http://localhost:8000` · Errors always look like `{"success": false, "error": "friendly message"}`.

## GET /
`{"status":"online","service":"AskIt","version":"1.0.0"}`

## GET /health
`{"status":"healthy"}`

## POST /api/ask
Request: `{"query": "What is retrieval augmented generation?"}` (trimmed, 1–5000 chars)

Response 200:
```json
{"success": true, "query": "...", "answer": "...", "sources": [{"title": "...", "url": "https://..."}], "processing_time": 10.2}
```
Errors: `400` empty/too long/invalid body · `429` provider rate limit · `503` missing/invalid key or provider down · `504` timeout (`REQUEST_TIMEOUT_SECONDS`).
```bash
curl -X POST http://localhost:8000/api/ask -H "Content-Type: application/json" -d '{"query":"What is artificial intelligence?"}'
```

## POST /api/tts
Request: `{"text": "Hello from AskIt"}` → Response 200 `audio/mpeg` (binary MP3). In `DEMO_MODE` it returns ~1.5 s of silence.
Errors: `400` empty/too long · `503` ElevenLabs not configured/invalid key · `504` timeout.
```bash
curl -X POST http://localhost:8000/api/tts -H "Content-Type: application/json" -d '{"text":"Hello from AskIt"}' --output out.mp3
```
