# ASKIT Frontend (React + Vite)

```bash
cp .env.example .env     # optional; defaults to http://localhost:8000
npm install
npm run dev              # http://localhost:5173
npm run build            # production build
```

- `VITE_API_URL` – FastAPI backend URL.
- `VITE_N8N_WEBHOOK_URL` – optional. If set, questions go through the n8n webhook (`/webhook/askit`) instead of calling `/api/ask` directly. Audio is always fetched from the backend `/api/tts`.
- No API keys exist in the frontend. Agent status is simulated from timing while the single synchronous request runs.
