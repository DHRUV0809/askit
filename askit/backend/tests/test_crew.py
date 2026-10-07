import httpx
import pytest

from app.models.schemas import ServiceError, Source
from app.services import research_service as rs
from app.tools import web_search as ws


class FakeResp:
    def __init__(self, status=200, payload=None):
        self.status_code, self._p = status, payload or {}

    def json(self):
        return self._p


def test_to_sources_dedupes_and_validates():
    out = rs.to_sources(
        [
            {"title": "A", "url": "https://a.com/"},
            {"title": "A again", "url": "https://a.com"},
            {"title": "Bad", "url": "javascript:alert(1)"},
        ]
    )
    assert [s.url for s in out] == ["https://a.com/"]


def test_demo_research(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "true")
    answer, sources = rs.run_research("What is RAG?")
    assert "Retrieval-Augmented Generation" in answer and sources


def test_missing_openai_key(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "false")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ServiceError):
        rs.run_research("q")


def test_run_research_uses_mocked_crew(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "false")
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    monkeypatch.setattr(
        "app.crew.askit_crew.run_crew", lambda q, p: ("final", [Source(title="S", url="https://s.com")])
    )
    assert rs.run_research("q")[0] == "final"


def test_crew_failure_becomes_friendly_error(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "false")
    monkeypatch.setenv("OPENAI_API_KEY", "k")

    def boom(q, p):
        raise RuntimeError("boom with secrets")

    monkeypatch.setattr("app.crew.askit_crew.run_crew", boom)
    with pytest.raises(ServiceError) as e:
        rs.run_research("q")
    assert "secrets" not in e.value.message


def test_tavily_success_filters_bad_urls(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "k")
    payload = {"results": [{"title": "T", "url": "https://x.com", "content": "c"}, {"title": "n", "url": "ftp://x"}]}
    monkeypatch.setattr(ws.httpx, "post", lambda *a, **k: FakeResp(200, payload))
    assert rs.WebResearchProvider().search("q") == [{"title": "T", "url": "https://x.com", "content": "c"}]


def test_tavily_empty_results(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "k")
    monkeypatch.setattr(ws.httpx, "post", lambda *a, **k: FakeResp(200, {"results": []}))
    assert ws.tavily_search("q") == []


@pytest.mark.parametrize("status,status_out", [(401, 503), (429, 429), (500, 503)])
def test_tavily_errors(monkeypatch, status, status_out):
    monkeypatch.setenv("TAVILY_API_KEY", "k")
    monkeypatch.setattr(ws.httpx, "post", lambda *a, **k: FakeResp(status))
    with pytest.raises(ServiceError) as e:
        ws.tavily_search("q")
    assert e.value.status == status_out


def test_tavily_network_error(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "k")

    def fail(*a, **k):
        raise httpx.ConnectError("down")

    monkeypatch.setattr(ws.httpx, "post", fail)
    with pytest.raises(ServiceError):
        ws.tavily_search("q")


def test_tavily_missing_key(monkeypatch):
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    with pytest.raises(ServiceError):
        ws.tavily_search("q")
