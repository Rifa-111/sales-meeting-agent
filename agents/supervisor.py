import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from agents.state import AgentState
from langgraph.graph import END

MAX_ITERATIONS = 2


def supervisor_node(state: AgentState) -> AgentState:
    """Checks output quality. Increments iteration counter."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=os.environ["OPENAI_API_KEY"])

    research = state.get("research_output", "")
    iteration = state.get("iteration", 0)

    # Quick quality check via LLM
    check_prompt = f"""Rate the quality of this sales research output for '{state["company_name"]}' on a scale 1–10.
Return JSON: {{"score": <int>, "reason": "<one sentence>"}}

Research output:
{research[:1500]}

Output ONLY valid JSON."""

    messages = [
        SystemMessage(content="You are a quality evaluator. Return only JSON."),
        HumanMessage(content=check_prompt),
    ]
    response = llm.invoke(messages)
    try:
        result = json.loads(response.content.strip())
        score = result.get("score", 5)
        reason = result.get("reason", "")
    except Exception:
        score = 5
        reason = "Could not parse quality score."

    log = state.get("status_log", [])
    log.append(f"🎯 Supervisor: quality score {score}/10 — {reason}")

    new_iteration = iteration + 1
    return {**state, "iteration": new_iteration, "status_log": log}


def should_retry(state: AgentState) -> str:
    """Routing function: retry research if score is low, else finish."""
    log = state.get("status_log", [])
    iteration = state.get("iteration", 1)

    # Check last supervisor log entry for score
    supervisor_entry = next((l for l in reversed(log) if l.startswith("🎯 Supervisor")), "")
    low_quality = "score 1" in supervisor_entry or "score 2" in supervisor_entry or "score 3" in supervisor_entry

    if low_quality and iteration < MAX_ITERATIONS:
        return "researcher"
    return END
