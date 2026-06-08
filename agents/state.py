from typing import TypedDict, Optional


class AgentState(TypedDict):
    company_name: str
    meeting_context: str
    retrieved_docs: list[str]
    research_output: str
    insights: str
    presentation: str
    final_brief: str
    iteration: int
    status_log: list[str]
