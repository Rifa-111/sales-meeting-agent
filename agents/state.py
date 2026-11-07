from typing import TypedDict


class AgentState(TypedDict, total=False):
    company_name: str
    meeting_context: str
    retrieved_docs: list[str]
    research_output: str
    insights: str
    presentation: str
    final_brief: str
    iteration: int
    quality_score: int | None
    status_log: list[str]
