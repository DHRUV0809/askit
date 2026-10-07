"""Research providers (RAG-ready) and the main research entry point."""
import logging
from abc import ABC, abstractmethod

from app.config import settings
from app.models.schemas import ServiceError, Source
from app.tools.web_search import tavily_search

logger = logging.getLogger("askit.research")


class ResearchProvider(ABC):
    """Anything that can return evidence for a query: [{title, url, content}]."""

    @abstractmethod
    def search(self, query: str) -> list[dict]: ...


class WebResearchProvider(ResearchProvider):
    def search(self, query: str) -> list[dict]:
        return tavily_search(query, max_results=5)


# Phase 2: class DocumentResearchProvider(ResearchProvider) backed by Chroma.
# The Researcher only depends on ResearchProvider, so adding it needs no pipeline rewrite.


def to_sources(results: list[dict]) -> list[Source]:
    seen, out = set(), []
    for r in results:
        url = r.get("url", "")
        key = url.rstrip("/").lower()
        if url.startswith(("http://", "https://")) and key not in seen:
            seen.add(key)
            out.append(Source(title=r.get("title") or url, url=url))
    return out


_DEMO_RAG = (
    "## What is Retrieval-Augmented Generation (RAG)?\n\n"
    "Retrieval-Augmented Generation (RAG) combines language models with external knowledge retrieval.\n\n"
    "- **Retrieve**: relevant documents are found for the question.\n"
    "- **Augment**: those documents are added to the model's prompt.\n"
    "- **Generate**: the model answers using the retrieved evidence.\n\n"
    "This reduces hallucinations and keeps answers up to date without retraining.\n\n"
    "*(Demo mode: this is a deterministic mock answer.)*"
)
_DEMO_EV = (
    "## Electric vehicles: advantages and disadvantages\n\n"
    "### Advantages\n"
    "- **Lower running costs**: electricity is usually cheaper per km than fuel, and servicing is simpler.\n"
    "- **No tailpipe emissions**: better local air quality.\n"
    "- **Smooth, quiet driving** with instant torque.\n\n"
    "### Disadvantages\n"
    "- **Higher purchase price** in many markets.\n"
    "- **Charging time and infrastructure** can be limiting on long trips.\n"
    "- **Battery production and recycling** have environmental costs.\n\n"
    "*(Demo mode: this is a deterministic mock answer.)*"
)
_DEMO_SOURCES = {
    "ev": [Source(title="Wikipedia: Electric vehicle", url="https://en.wikipedia.org/wiki/Electric_vehicle")],
    "rag": [
        Source(
            title="Wikipedia: Retrieval-augmented generation",
            url="https://en.wikipedia.org/wiki/Retrieval-augmented_generation",
        )
    ],
}


def demo_research(query: str) -> tuple[str, list[Source]]:
    if "electric" in query.lower():
        return _DEMO_EV, list(_DEMO_SOURCES["ev"])
    return _DEMO_RAG, list(_DEMO_SOURCES["rag"])


def run_research(query: str) -> tuple[str, list[Source]]:
    """Run Researcher -> Writer -> Editor. Returns (final_answer, sources)."""
    if settings.demo_mode:
        logger.info("DEMO_MODE active: returning mock research")
        return demo_research(query)
    if not settings.openai_api_key:
        raise ServiceError("AI service is not configured (missing OPENAI_API_KEY).")
    from app.crew.askit_crew import run_crew  # lazy import keeps startup light

    try:
        return run_crew(query, WebResearchProvider())
    except ServiceError:
        raise
    except Exception as exc:  # CrewAI / OpenAI failures
        logger.exception("Crew failed")
        text = str(exc).lower()
        if "api key" in text or "authentication" in text or "401" in text:
            raise ServiceError("The AI service API key appears to be invalid.")
        if "rate limit" in text or "429" in text:
            raise ServiceError("The AI service is rate limited. Please try again shortly.", 429)
        raise ServiceError("Research service is temporarily unavailable. Please try again.")
