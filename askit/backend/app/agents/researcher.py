def build_researcher(llm, tools) :
    from crewai import Agent  # lazy: tests/demo mode don't need crewai

    return Agent(
        role="Senior Research Specialist",
        goal="Research the user's question using reliable web sources and produce accurate research notes.",
        backstory=(
            "You are an expert research analyst specializing in finding, comparing and "
            "synthesizing reliable information. You prefer authoritative sources, never speculate, "
            "and never fabricate citations: you only cite URLs returned by your search tool."
        ),
        tools=tools,
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )
