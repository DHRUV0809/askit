def build_writer(llm) :
    from crewai import Agent  # lazy: tests/demo mode don't need crewai

    return Agent(
        role="Expert Research Writer",
        goal="Transform research notes into a clear, useful and structured answer.",
        backstory=(
            "You write clear, concise explanations in simple language. You use headings and bullet "
            "points when useful, rely only on information supported by the research, and never "
            "fabricate information."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )
