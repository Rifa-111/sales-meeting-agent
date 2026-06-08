import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from agents.state import AgentState

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False


def _tavily_search(query: str, max_results: int = 3) -> str:
    """Run a Tavily web search and return formatted results."""
    if not TAVILY_AVAILABLE:
        return "Tavily not installed — skipping live search."
    api_key = os.getenv("TAVILY_API_KEY", "")
    if not api_key:
        return "TAVILY_API_KEY not set — skipping live search."
    client = TavilyClient(api_key=api_key)
    response = client.search(query=query, max_results=max_results, search_depth="advanced")
    results = response.get("results", [])
    if not results:
        return "No results found."
    formatted = []
    for r in results:
        formatted.append(f"**{r.get('title', 'No title')}**\n{r.get('content', '')}\nSource: {r.get('url', '')}")
    return "\n\n---\n\n".join(formatted)


RESEARCH_SYSTEM = """You are an expert B2B sales researcher. Given a company name, meeting context, 
and retrieved internal knowledge, your job is to produce structured research that helps a salesperson 
walk into a meeting fully prepared.

You have access to a web search tool. Use it to find:
1. Recent company news (funding, leadership changes, product launches, layoffs)
2. Industry trends relevant to their pain points
3. Any signals of buying intent or strategic initiatives

Return your output as structured JSON with these keys:
- company_overview: 2–3 sentence summary
- recent_news: list of up to 4 bullet strings
- strategic_priorities: list of up to 4 bullet strings  
- buying_signals: list of up to 3 bullet strings
- risks: list of up to 3 potential risks or objections
- search_sources: list of URLs found

Output ONLY valid JSON, no markdown fences."""


def research_node(state: AgentState) -> AgentState:
    """ReAct-style research agent: searches the web then synthesises findings."""
    llm = ChatOpenAI(model="gpt-4o", temperature=0.2, api_key=os.environ["OPENAI_API_KEY"])

    retrieved_context = "\n\n".join(state.get("retrieved_docs", []))
    company = state["company_name"]
    context = state["meeting_context"]

    # Step 1: Run web searches
    search_q1 = f"{company} company news 2024 2025"
    search_q2 = f"{company} strategic initiatives technology investment"
    web_results_1 = _tavily_search(search_q1)
    web_results_2 = _tavily_search(search_q2)
    web_context = f"=== Search 1: {search_q1} ===\n{web_results_1}\n\n=== Search 2: {search_q2} ===\n{web_results_2}"

    # Step 2: Synthesise
    user_prompt = f"""Company: {company}
Meeting context: {context}

Internal knowledge base context:
{retrieved_context if retrieved_context else "No internal records found."}

Live web research:
{web_context}

Now produce the structured JSON research report."""

    messages = [
        SystemMessage(content=RESEARCH_SYSTEM),
        HumanMessage(content=user_prompt),
    ]
    response = llm.invoke(messages)
    raw = response.content.strip()

    # Safely parse JSON — fall back to raw string
    try:
        parsed = json.loads(raw)
        research_output = json.dumps(parsed, indent=2)
    except json.JSONDecodeError:
        research_output = raw

    log = state.get("status_log", [])
    log.append(f"🔍 Research agent: completed web research and synthesis for {company}.")

    return {**state, "research_output": research_output, "status_log": log}
