def build_editor(llm) :
    from crewai import Agent  # lazy: tests/demo mode don't need crewai

    return Agent(
        role="Senior Fact-Checking Editor",
        goal="Review the research and the draft and produce the final, polished response.",
        backstory=(
            "You are a meticulous editor. You check factual consistency against the research, "
            "remove unsupported claims, speculation and redundancy, fix contradictions, preserve "
            "useful source information and return only the final answer."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )
