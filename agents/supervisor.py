"""Supervisor scoring and bounded retry routing for the research prototype."""
import json
import os

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import END

from agents.state import AgentState

MAX_ITERATIONS = 2
RETRY_BELOW_SCORE = 4


def parse_quality_score(content: str):
    """Return an integer from 1 to 10 or None for invalid model output."""
    try:
        payload = json.loads(content.strip())
        score = payload.get("score")
        if isinstance(score, bool) or not isinstance(score, int) or not 1 <= score <= 10:
            return None
        return score
    except (ValueError, TypeError, AttributeError):
        return None


def supervisor_node(state: AgentState) -> AgentState:
    """Evaluate current draft and store a structured score for routing."""
    llm = ChatOpenAI(
        model="gpt-4o-mini", temperature=0,
        api_key=os.environ["OPENAI_API_KEY"],
    )
    company = state.get("company_name", "")
    research = state.get("research_output", "")
    prompt = (
        f"Rate the relevance and factual grounding of this sales research for {company!r} "
        "from 1 to 10. Return only JSON with integer score and a brief reason.\n"
        "This score is heuristic and not an independently validated assessment.\n"
        f"Research:\n{research[:1500]}"
    )
    response = llm.invoke([
        SystemMessage(content="You assess research quality. Return only JSON."),
        HumanMessage(content=prompt),
    ])
    score = parse_quality_score(response.content)
    try:
        details = json.loads(response.content)
        reason = str(details.get("reason", ""))[:250] if isinstance(details, dict) else ""
    except (ValueError, TypeError):
        reason = "Unparseable response."
    status = list(state.get("status_log", []))
    status.append(
        f"Supervisor: score {score}/10 — {reason}" if score is not None
        else "Supervisor: quality score unavailable; stopping automated retries."
    )
    return {
        **state,
        "iteration": int(state.get("iteration", 0)) + 1,
        "quality_score": score,
        "status_log": status,
    }


def should_retry(state: AgentState) -> str:
    """Retry when an explicit low score is recorded and budget remains."""
    score = state.get("quality_score")
    iteration = int(state.get("iteration", 0))
    if (
        isinstance(score, int)
        and not isinstance(score, bool)
        and score < RETRY_BELOW_SCORE
        and iteration < MAX_ITERATIONS
    ):
        return "researcher"
    return END
