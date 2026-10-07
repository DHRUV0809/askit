"""Sequential CrewAI pipeline: Researcher -> Writer -> Editor."""
import logging

from app.agents.editor import build_editor
from app.agents.researcher import build_researcher
from app.agents.writer import build_writer
from app.config import settings
from app.models.schemas import ServiceError, Source
from app.services.research_service import ResearchProvider, to_sources
from app.tools.web_search import make_search_tool

logger = logging.getLogger("askit.crew")


def run_crew(query: str, provider: ResearchProvider) -> tuple[str, list[Source]]:
    from crewai import Crew, LLM, Process, Task  # lazy import

    collected: list[dict] = []
    llm = LLM(model=f"openai/{settings.openai_model}", api_key=settings.openai_api_key, temperature=0.2)
    researcher = build_researcher(llm, [make_search_tool(provider, collected)])
    writer, editor = build_writer(llm), build_editor(llm)

    research = Task(
        description=(
            "Research this question using the web_search tool: {query}\n"
            "Extract key facts, compare sources where needed, and list the sources (title + URL) "
            "you actually used. Do not speculate and never invent URLs."
        ),
        expected_output="Structured research notes: key facts as bullets, then a list of sources (title + URL).",
        agent=researcher,
        callback=lambda _o: logger.info("Research completed; Writer started"),
    )
    draft = Task(
        description=(
            "Using ONLY the research notes, write a clear structured answer to: {query}\n"
            "Use headings and bullets where useful, simple language, no filler."
        ),
        expected_output="A concise, well-structured draft answer in Markdown.",
        agent=writer,
        context=[research],
        callback=lambda _o: logger.info("Draft completed; Editor started"),
    )
    final = Task(
        description=(
            "Review the research notes and draft for the question: {query}\n"
            "Remove unsupported claims, speculation and redundancy, fix contradictions, improve "
            "clarity. Return ONLY the final polished answer in Markdown (no commentary, no source list)."
        ),
        expected_output="The final polished answer in Markdown.",
        agent=editor,
        context=[research, draft],
    )
    logger.info("Research started")
    crew = Crew(
        agents=[researcher, writer, editor],
        tasks=[research, draft, final],
        process=Process.sequential,
        verbose=False,
    )
    result = crew.kickoff(inputs={"query": query})
    answer = str(getattr(result, "raw", result)).strip()
    if not answer:
        raise ServiceError("The research pipeline returned an empty answer. Please try again.")
    logger.info("Editor completed")
    return answer, to_sources(collected)
