# Sales Meeting Agent — multi-agent research prototype

An **experimental** LangGraph + Streamlit project for preparing structured sales-meeting briefs. The application chains a local ChromaDB retrieval step, optional Tavily web search, LLM-based research synthesis, insights and presentation drafting, a supervisor and final Markdown/PDF export.

**Status:** demonstration prototype, not independently validated production software. There is no supported evidence for a guaranteed 60-second turnaround, clinical or commercial outcomes, GDPR compliance or external adoption.

## Architecture

```text
Company + meeting context
           |
      ChromaDB retriever (requires local knowledge base + OpenAI API)
           |
      Optional Tavily search + LLM synthesis
           |
      Insight agent -> Presentation agent
           |
      Supervisor (heuristic score; bounded optional retry)
           |
      Formatter -> Markdown / PDF export
```

The supervisor uses a structured integer score from 1 to 10. A score below 4 can cause a second research pass, up to two total supervisor assessments. This is a **heuristic**, not independent quality validation. Search results and generated briefs must be fact-checked.

## Running locally

Use a Python environment and install dependencies:

```bash
git clone https://github.com/Rifa-111/sales-meeting-agent.git
cd sales-meeting-agent
python -m pip install -r requirements.txt
cp .env.example .env
# Edit .env: set your own OPENAI_API_KEY and optional TAVILY_API_KEY
python -m utils.ingest
streamlit run app.py
```

The ingest step embeds **eight synthetic demonstration documents** in a persistent `./chroma_db` directory. They are not actual client records. The demo includes fictional company information, invented sales results, product capabilities, ROI figures and case studies. **Do not quote these as established facts or use them as evidence of real customer outcomes.**

Tavily may be omitted, but retrieval and LLM generation still require a usable OpenAI API key. API calls can incur usage charges. You must review provider terms and policies.

## Verification

```bash
python -m pip install pytest
python -m pytest -q tests/
```

GitHub Actions checks offline supervisor routing and source syntax without contacting third-party APIs. An end-to-end execution requires credentials and is **not currently verified by CI**.

## Safety and limitations

- Never add production customer or sensitive information to the demo without a suitable privacy and security assessment.
- Company and meeting-context inputs go to OpenAI; Tavily queries are sent to Tavily when configured. ChromaDB persists the synthetic seed knowledge base on disk. Data handling also depends on third-party providers. **No claim of zero data retention or GDPR compliance is made.**
- Model outputs may be incorrect, stale, fabricated or unsupported. Verify cited sources and proof points before using a brief.
- The per-session counter is not a server-side rate limiter.
- The code currently has no verified top-level open-source licence. A public repository does not automatically grant permission to redistribute or reuse it. The owner should choose a licence before describing this as MIT-licensed or openly reusable.
- No independent GitHub adoption, community benefit or performance benchmark is currently demonstrated.

See [SECURITY.md](SECURITY.md) for responsible-use considerations and [CONTRIBUTING.md](CONTRIBUTING.md) for genuine code and reproducibility feedback.

## Project structure

- `graph.py`: stateful LangGraph orchestration
- `agents/`: retrieval, research, insights, presentation, review, formatting
- `utils/ingest.py`: seeded synthetic knowledge base
- `utils/pdf_export.py`: PDF helper
- `app.py`: Streamlit interface
- `tests/`: local offline tests

## Contributing

Technical reviews, reproductions, documented bug reports and code improvements are welcome. Public availability alone does not establish independent community adoption. Respect third-party data and content rights.
