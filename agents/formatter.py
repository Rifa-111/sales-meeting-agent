import json
from agents.state import AgentState


def format_brief(state: AgentState) -> AgentState:
    """Assemble the final markdown brief from all agent outputs."""
    company = state["company_name"]
    context = state["meeting_context"]

    def safe_parse(s):
        try:
            return json.loads(s)
        except Exception:
            return {}

    research = safe_parse(state.get("research_output", "{}"))
    insights = safe_parse(state.get("insights", "{}"))
    presentation = safe_parse(state.get("presentation", "{}"))

    lines = []
    lines.append(f"# 📊 Sales Meeting Brief: {company}")
    lines.append(f"**Meeting context:** {context}\n")

    lines.append("---")
    lines.append("## 🏢 Company Overview")
    lines.append(research.get("company_overview", "_No overview available._"))
    lines.append("")

    news = research.get("recent_news", [])
    if news:
        lines.append("## 📰 Recent News & Signals")
        for item in news:
            lines.append(f"- {item}")
        lines.append("")

    priorities = research.get("strategic_priorities", [])
    if priorities:
        lines.append("## 🎯 Strategic Priorities")
        for item in priorities:
            lines.append(f"- {item}")
        lines.append("")

    lines.append("---")
    lines.append("## 💡 Strategic Insights")
    if insights.get("headline_opportunity"):
        lines.append(f"**Headline opportunity:** {insights['headline_opportunity']}\n")
    if insights.get("core_pain"):
        lines.append(f"**Core pain:** {insights['core_pain']}\n")
    if insights.get("emotional_hook"):
        lines.append(f"**Emotional hook:** {insights['emotional_hook']}\n")
    if insights.get("competitive_angle"):
        lines.append(f"**Competitive angle:** {insights['competitive_angle']}\n")

    stakeholders = insights.get("stakeholder_angles", [])
    if stakeholders:
        lines.append("### Stakeholder Angles")
        for s in stakeholders:
            lines.append(f"- **{s.get('role', 'Unknown')}** — {s.get('motivation', '')} → _{s.get('message', '')}_")
        lines.append("")

    lines.append("---")
    lines.append("## 🗣️ Meeting Playbook")
    if presentation.get("opening_line"):
        lines.append(f"**Opening line:** _{presentation['opening_line']}_\n")

    talk_track = presentation.get("talk_track", [])
    if talk_track:
        lines.append("### Talk Track")
        for i, point in enumerate(talk_track, 1):
            lines.append(f"{i}. {point}")
        lines.append("")

    questions = presentation.get("discovery_questions", [])
    if questions:
        lines.append("### Discovery Questions")
        for q in questions:
            lines.append(f"- {q}")
        lines.append("")

    demo_focus = presentation.get("demo_focus", [])
    if demo_focus:
        lines.append("### Demo Focus Areas")
        for d in demo_focus:
            lines.append(f"- {d}")
        lines.append("")

    proof_points = presentation.get("value_proof_points", [])
    if proof_points:
        lines.append("### Value Proof Points")
        for p in proof_points:
            lines.append(f"- {p}")
        lines.append("")

    lines.append("---")
    lines.append("## 🛡️ Objection Handlers")
    objections = insights.get("top_objections", [])
    for obj in objections:
        lines.append(f"**❓ {obj.get('objection', '')}**")
        lines.append(f"> {obj.get('response', '')}\n")

    red_flags = presentation.get("red_flags", [])
    if red_flags:
        lines.append("## ⚠️ Red Flags to Watch")
        for r in red_flags:
            lines.append(f"- {r}")
        lines.append("")

    if insights.get("deal_risk"):
        lines.append(f"**Deal risk:** {insights['deal_risk']}\n")

    lines.append("---")
    lines.append("## ✅ Recommended Next Step")
    cta = presentation.get("call_to_action", "_Propose a follow-up discovery call._")
    lines.append(cta)

    final_brief = "\n".join(lines)

    log = state.get("status_log", [])
    log.append("✅ Final brief assembled and ready.")

    return {**state, "final_brief": final_brief, "status_log": log}
