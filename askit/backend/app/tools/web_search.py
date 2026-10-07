"""Tavily web search (REST) + the CrewAI tool wrapper."""
import logging

import httpx

from app.config import settings
from app.models.schemas import ServiceError

logger = logging.getLogger("askit.search")
TAVILY_URL = "https://api.tavily.com/search"


def tavily_search(query: str, max_results: int = 5) -> list[dict]:
    """Return [{title, url, content}]. Raises ServiceError with a friendly message."""
    if not settings.tavily_api_key:
        raise ServiceError("Web search is not configured (missing TAVILY_API_KEY).")
    try:
        resp = httpx.post(
            TAVILY_URL,
            json={"query": query[:400], "max_results": max_results, "search_depth": "basic"},
            headers={"Authorization": f"Bearer {settings.tavily_api_key}"},
            timeout=30,
        )
    except httpx.TimeoutException:
        raise ServiceError("Web search timed out.", 504)
    except httpx.HTTPError:
        raise ServiceError("Could not reach the web search service.")
    if resp.status_code in (401, 403):
        raise ServiceError("Web search API key is invalid.")
    if resp.status_code == 429:
        raise ServiceError("Web search rate limit reached. Please try again shortly.", 429)
    if resp.status_code >= 400:
        logger.error("Tavily returned HTTP %s", resp.status_code)
        raise ServiceError("Web search is temporarily unavailable.")
    try:
        items = resp.json().get("results", [])
    except ValueError:
        raise ServiceError("Web search returned an unreadable response.")
    results = []
    for item in items[:max_results]:
        url = str(item.get("url", ""))
        if url.startswith(("http://", "https://")):  # only real, valid URLs
            results.append(
                {"title": item.get("title") or url, "url": url, "content": item.get("content", "")}
            )
    return results


def make_search_tool(provider, collector: list):
    """Build a CrewAI tool bound to a ResearchProvider; found results go into `collector`."""
    from crewai.tools import BaseTool  # lazy: demo mode/tests don't need crewai

    class WebSearchTool(BaseTool):
        name: str = "web_search"
        description: str = (
            "Search the web for current, reliable information. "
            "Input: a search query string. Returns titles, URLs and snippets."
        )

        def _run(self, query: str) -> str:
            try:
                results = provider.search(query)
            except ServiceError as exc:
                return f"SEARCH_ERROR: {exc.message} Do not invent sources; say that search failed."
            if not results:
                return "No results found. Do not invent sources."
            collector.extend(results)
            return "\n\n".join(
                f"Title: {r['title']}\nURL: {r['url']}\nContent: {r['content']}" for r in results
            )

    return WebSearchTool()
