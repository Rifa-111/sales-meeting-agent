# Sales Meeting Preparation Agent

A production-style **multi-agent LLM system** built with LangGraph, OpenAI, ChromaDB, and Streamlit.
Given a company name and meeting context, it autonomously researches the prospect, extracts strategic insights,
and generates a complete, actionable meeting brief in under 60 seconds.

---

## Architecture

```
Customer data
     ↓
ChromaDB RAG       ← Embed query, retrieve internal docs
     ↓
Research Agent     ← ReAct loop with Tavily web search
     ↓
Insight Agent      ← LLM reasoning: pain points, objections, stakeholder angles
     ↓
Presentation Agent ← Talk track, discovery questions, demo focus, CTA
     ↓
Supervisor         ← Quality check; retry Research agent if score < 4/10
     ↓
Final Brief        ← Formatted markdown + PDF export
```

Built with **LangGraph StateGraph** for orchestration, conditional edges for the retry loop,
and a shared typed state object passed through all nodes.

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API keys

```bash
cp .env.example .env
# Edit .env and fill in:
# OPENAI_API_KEY=sk-...
# TAVILY_API_KEY=tvly-...   (optional — enables live web search)
```

Get a free Tavily key at [tavily.com](https://tavily.com) (1,000 free searches/month).

### 3. Ingest the knowledge base

```bash
python -m utils.ingest
```

This loads 8 synthetic documents (company profiles, product overview, objection handlers,
competitive intel) into a local ChromaDB instance at `./chroma_db/`.

### 4. Run the app

```bash
streamlit run app.py
```

---

## Features

- **LangGraph orchestration** — typed `AgentState`, `StateGraph`, conditional edges
- **RAG** — ChromaDB with OpenAI `text-embedding-3-small` embeddings; retrieves relevant internal docs
- **Agentic research** — Research agent uses Tavily for live web search (news, signals, context)
- **Supervisor loop** — LLM quality scoring with automatic retry (max 2 iterations)
- **Structured outputs** — all agents return validated JSON parsed into clean markdown
- **PDF + Markdown export** — downloadable brief from the Streamlit UI
- **Streamlit UI** — real-time agent status log, example prefills, API key management in sidebar

---

## Design Decisions

**Why LangGraph over simple LLM chaining?**
LangGraph provides a compiled graph with typed state, enabling conditional routing (the supervisor
retry loop), clear separation of concerns per node, and easy extension (add a new node without
touching existing ones). Plain chaining would require manual state threading and no retry logic.

**Why ChromaDB local?**
Zero infrastructure setup — persistent client writes to `./chroma_db/`. In production, swap for
a hosted Chroma instance or Pinecone. The embedding function interface is identical.

**Why structured JSON outputs from agents?**
Each agent returns JSON that the formatter assembles deterministically. This makes each agent's
output testable and the pipeline debuggable — raw JSON is visible in the "View raw outputs" expander.

---

## Project Structure

```
sales_meeting_agent/
├── app.py                  # Streamlit UI
├── graph.py                # LangGraph graph definition
├── requirements.txt
├── .env.example
├── agents/
│   ├── state.py            # Shared AgentState TypedDict
│   ├── retriever.py        # ChromaDB RAG node
│   ├── researcher.py       # ReAct web search node
│   ├── insight.py          # Strategic insight node
│   ├── presentation.py     # Meeting brief node
│   ├── supervisor.py       # Quality check + routing
│   └── formatter.py        # Markdown assembly
└── utils/
    ├── ingest.py           # ChromaDB ingestion script
    └── pdf_export.py       # Markdown → PDF utility
```

---

## Extending the Project

- **Add a CRM connector** — replace ChromaDB retrieval with a Salesforce/HubSpot API call
- **Add memory** — persist past meeting briefs back into ChromaDB for learning over time
- **Add a human-in-the-loop node** — pause before the Supervisor for manual review
- **Deploy** — wrap `graph.py` as a FastAPI endpoint; deploy Streamlit to Streamlit Cloud

---

## CV / Portfolio Narrative

> "Built a production-style multi-agent LLM system using LangGraph to automate pre-meeting
> sales intelligence. The system orchestrates four specialised agents (retrieval, research,
> insight, presentation) with a quality-checking supervisor node that implements a conditional
> retry loop. Demonstrates agentic orchestration, RAG with ChromaDB, ReAct tool use via Tavily,
> structured LLM outputs, and a full Streamlit deployment."

---

## Deploying for public use

### Environment variables (server-side only)

Set these on your server or hosting platform. Users never see or enter API keys.

```bash
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...   # optional
```

On **Streamlit Cloud**: Settings → Secrets → paste as TOML:
```toml
OPENAI_API_KEY = "sk-..."
TAVILY_API_KEY = "tvly-..."
```

On **Railway / Render / Fly.io**: add as environment variables in the dashboard.

### Rate limiting

The app limits each session to 5 briefs (`MAX_BRIEFS_PER_SESSION` in `app.py`).
Change that constant to suit your expected traffic and API budget.
For production, replace with server-side IP-based rate limiting (e.g. Redis + a middleware layer).

### Privacy compliance (GDPR / UK GDPR)

The app already:
- Shows users an inline data notice before they submit anything
- States clearly that company names and meeting context are sent to OpenAI
- Links to OpenAI's privacy policy
- Tells users no data is stored after the session
- Never asks for or stores personal data

If you're deploying commercially, also add a privacy policy page and cookie notice.

### What users never see

- API keys (server env only)
- Stack traces (all exceptions are caught and shown as generic messages)
- Internal agent logs (status log strips emoji and internal markers)
