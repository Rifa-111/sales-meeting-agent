import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from agents.state import AgentState


PRESENTATION_SYSTEM = """You are a world-class sales coach. Given research and strategic insights about a prospect,
produce a polished, ready-to-use meeting brief that a salesperson can review in 5 minutes before walking in.

The brief must be practical and immediately actionable — no fluff, no vague advice.

Return structured JSON with these keys:
- opening_line: A specific, attention-grabbing opening sentence for the meeting
- talk_track: list of 4–5 talk track bullet strings (what to say, in order)
- discovery_questions: list of 5 killer questions to uncover need and budget
- demo_focus: list of 2–3 specific features/capabilities to demo based on their pain
- value_proof_points: list of 2–3 specific ROI or case study references to cite
- call_to_action: the specific next step to propose at the end of the meeting
- red_flags: list of 2–3 warning signs to watch for during the meeting

Output ONLY valid JSON, no markdown fences."""


def presentation_node(state: AgentState) -> AgentState:
    """Converts insights into a polished, actionable meeting brief."""
    llm = ChatOpenAI(model="gpt-4o", temperature=0.4, api_key=os.environ["OPENAI_API_KEY"])

    research = state.get("research_output", "")
    insights = state.get("insights", "")
    company = state["company_name"]
    context = state["meeting_context"]

    user_prompt = f"""Company: {company}
Meeting context: {context}

Research:
{research}

Strategic insights:
{insights}

Now produce the meeting brief."""

    messages = [
        SystemMessage(content=PRESENTATION_SYSTEM),
        HumanMessage(content=user_prompt),
    ]
    response = llm.invoke(messages)
    raw = response.content.strip()

    try:
        parsed = json.loads(raw)
        presentation = json.dumps(parsed, indent=2)
    except json.JSONDecodeError:
        presentation = raw

    log = state.get("status_log", [])
    log.append(f"📋 Presentation agent: meeting brief drafted.")

    return {**state, "presentation": presentation, "status_log": log}
