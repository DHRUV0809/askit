import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import ServiceError, Source

client = TestClient(app, raise_server_exceptions=False)


class FakeResp:
    def __init__(self, status=200, payload=None, content=b""):
        self.status_code, self._p, self.content = status, payload or {}, content

    def json(self):
        return self._p


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json() == {"status": "online", "service": "AskIt", "version": "1.0.0"}


def test_health():
    assert client.get("/health").json() == {"status": "healthy"}


@pytest.mark.parametrize("body", [{"query": ""}, {"query": "   "}, {}, {"query": "x" * 5001}])
def test_invalid_queries_rejected(body):
    r = client.post("/api/ask", json=body)
    assert r.status_code == 400
    assert r.json()["success"] is False


def test_ask_mocked_crew(monkeypatch):
    monkeypatch.setattr(
        "app.api.routes.run_research", lambda q: ("Mock answer", [Source(title="T", url="https://example.com")])
    )
    r = client.post("/api/ask", json={"query": "  What is AI?  "})
    body = r.json()
    assert r.status_code == 200 and body["success"] is True
    assert body["query"] == "What is AI?" and body["answer"] == "Mock answer"
    assert body["sources"] == [{"title": "T", "url": "https://example.com"}]
    assert isinstance(body["processing_time"], float)


def test_ask_service_error_is_friendly(monkeypatch):
    def boom(q):
        raise ServiceError("Research service is temporarily unavailable. Please try again.")

    monkeypatch.setattr("app.api.routes.run_research", boom)
    r = client.post("/api/ask", json={"query": "hi"})
    assert r.status_code == 503 and "Traceback" not in r.text


def test_ask_demo_mode(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "true")
    r = client.post("/api/ask", json={"query": "What are the advantages and disadvantages of electric vehicles?"})
    assert r.status_code == 200 and r.json()["sources"]


def test_tts_demo_mode(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "true")
    r = client.post("/api/tts", json={"text": "Hello from AskIt"})
    assert r.status_code == 200 and r.headers["content-type"] == "audio/mpeg" and r.content


def test_tts_not_configured(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "false")
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    assert client.post("/api/tts", json={"text": "hi"}).status_code == 503


def test_tts_mocked_elevenlabs(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "false")
    monkeypatch.setenv("ELEVENLABS_API_KEY", "k")
    monkeypatch.setenv("ELEVENLABS_VOICE_ID", "v")
    monkeypatch.setattr("app.services.tts_service.httpx.post", lambda *a, **k: FakeResp(200, content=b"MP3DATA"))
    r = client.post("/api/tts", json={"text": "# Title\n\nSome **bold** text."})
    assert r.status_code == 200 and r.content == b"MP3DATA"


def test_tts_empty_rejected():
    assert client.post("/api/tts", json={"text": " "}).status_code == 400
