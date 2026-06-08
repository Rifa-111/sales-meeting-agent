import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from agents.state import AgentState


INSIGHT_SYSTEM = """You are a senior B2B sales strategist with 15 years experience closing enterprise deals.
Given research about a prospect company, your job is to extract sharp, actionable insights 
that will help a salesperson win the deal.

Think deeply about:
- The real underlying pain (not just stated problems)
- Political dynamics (who wins/loses from a change)
- The strongest emotional hook for this buyer
- What success looks like for each stakeholder
- The most dangerous objection and how to neutralise it

Return structured JSON with these keys:
- headline_opportunity: 1 sentence — the single biggest opening
- core_pain: 2–3 sentences on the true underlying problem
- top_objections: list of 3 objects each with "objection" and "response" keys
- stakeholder_angles: list of objects with "role", "motivation", "message" 
- emotional_hook: 1–2 sentences — the narrative that resonates emotionally
- competitive_angle: 1–2 sentences on how to position vs likely alternatives
- deal_risk: 1–2 sentences on the biggest risk to this deal

Output ONLY valid JSON, no markdown fences."""


def insight_node(state: AgentState) -> AgentState:
    """Pure LLM reasoning to extract deep insights from research."""
    llm = ChatOpenAI(model="gpt-4o", temperature=0.3, api_key=os.environ["OPENAI_API_KEY"])

    research = state.get("research_output", "")
    company = state["company_name"]
    context = state["meeting_context"]
    retrieved = "\n\n".join(state.get("retrieved_docs", []))

    user_prompt = f"""Company: {company}
Meeting context: {context}

Research findings:
{research}

Internal product/competitive knowledge:
{retrieved if retrieved else "Use general best-practice knowledge."}

Now produce the deep insight analysis."""

    messages = [
        SystemMessage(content=INSIGHT_SYSTEM),
        HumanMessage(content=user_prompt),
    ]
    response = llm.invoke(messages)
    raw = response.content.strip()

    try:
        parsed = json.loads(raw)
        insights = json.dumps(parsed, indent=2)
    except json.JSONDecodeError:
        insights = raw

    log = state.get("status_log", [])
    log.append(f"💡 Insight agent: extracted strategic insights and objection handlers.")

    return {**state, "insights": insights, "status_log": log}
