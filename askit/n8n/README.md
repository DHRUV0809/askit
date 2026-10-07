# n8n workflow

`askit_workflow.json`: **Webhook** (`POST /webhook/askit`) → **HTTP Request** `POST {BACKEND}/api/ask` → **HTTP Request** `POST {BACKEND}/api/tts` (audio kept as binary, failures tolerated) → **Respond to Webhook**.

## Import
1. Start n8n (`npx n8n` or Docker: `docker run -it --rm -p 5678:5678 -e BACKEND_URL=http://host.docker.internal:8000 n8nio/n8n`).
2. Workflows → **Import from file** → `askit_workflow.json`.
3. Set the backend URL: the workflow reads `$env.BACKEND_URL` and falls back to `http://host.docker.internal:8000`. If your n8n blocks env access, set `N8N_BLOCK_ENV_ACCESS_IN_NODE=false`, or just edit the two URLs in the HTTP nodes (use `http://localhost:8000` when n8n runs on the host).
4. **Activate** the workflow (production URL `http://localhost:5678/webhook/askit`; test URL is `/webhook-test/askit`).

## Test
```bash
curl -X POST http://localhost:5678/webhook/askit -H "Content-Type: application/json" -d '{"query":"Explain machine learning"}'
```
Response: `{ "success": true, "answer": "...", "sources": [...], "processing_time": 12.4, "audio_available": true }`. The audio itself is fetched by the frontend from the backend `/api/tts` (the key never reaches the browser).
To use n8n from the UI set `VITE_N8N_WEBHOOK_URL=http://localhost:5678/webhook/askit` in `frontend/.env`.
