import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

from agents.state import AgentState
from agents.retriever import retriever_node
from agents.researcher import research_node
from agents.insight import insight_node
from agents.presentation import presentation_node
from agents.supervisor import supervisor_node, should_retry
from agents.formatter import format_brief

load_dotenv()


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("retriever", retriever_node)
    graph.add_node("researcher", research_node)
    graph.add_node("insight", insight_node)
    graph.add_node("presentation", presentation_node)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("formatter", format_brief)

    graph.set_entry_point("retriever")
    graph.add_edge("retriever", "researcher")
    graph.add_edge("researcher", "insight")
    graph.add_edge("insight", "presentation")
    graph.add_edge("presentation", "supervisor")

    # Conditional: retry research if quality is poor, else format and finish
    graph.add_conditional_edges(
        "supervisor",
        should_retry,
        {"researcher": "researcher", END: "formatter"},
    )
    graph.add_edge("formatter", END)

    return graph.compile()


# Module-level compiled graph (cached)
compiled_graph = build_graph()


def run_pipeline(company_name: str, meeting_context: str) -> AgentState:
    initial_state: AgentState = {
        "company_name": company_name,
        "meeting_context": meeting_context,
        "retrieved_docs": [],
        "research_output": "",
        "insights": "",
        "presentation": "",
        "final_brief": "",
        "iteration": 0,
        "status_log": [],
    }
    return compiled_graph.invoke(initial_state)
