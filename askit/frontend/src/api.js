// All calls go to the backend (or n8n). No API keys ever live in the frontend.
const API = import.meta.env.VITE_API_URL || "http://localhost:8000";
const N8N = import.meta.env.VITE_N8N_WEBHOOK_URL || "";
const FRIENDLY = "Research service is temporarily unavailable. Please try again.";

async function request(url, body) {
  let res;
  try {
    res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    throw new Error("Cannot reach the service. Check your connection and that the backend is running.");
  }
  return res;
}

async function failure(res) {
  let msg = FRIENDLY;
  try {
    const data = await res.json();
    if (data?.error) msg = data.error;
  } catch { /* keep friendly default */ }
  return new Error(msg);
}

export async function ask(query) {
  const res = await request(N8N || `${API}/api/ask`, { query });
  if (!res.ok) throw await failure(res);
  const data = await res.json();
  if (data.success === false) throw new Error(data.error || FRIENDLY);
  return data;
}

export async function tts(text) {
  const res = await request(`${API}/api/tts`, { text });
  if (!res.ok) throw await failure(res);
  return URL.createObjectURL(await res.blob());
}
