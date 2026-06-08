"""
Meeting Prep — public-facing Streamlit app.
Keys are server-side only. Users never configure credentials.
Rate limited per session. GDPR/privacy notice inline.
"""
import os
import time
import hashlib
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ── Constants ──────────────────────────────────────────────────────────────────
MAX_BRIEFS_PER_SESSION = 5
OPENAI_KEY  = os.getenv("OPENAI_API_KEY", "")
TAVILY_KEY  = os.getenv("TAVILY_API_KEY", "")

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Meeting Prep",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Design system ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stApp"] {
  background: #f5f5f7 !important;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", ui-sans-serif, system-ui, sans-serif !important;
  color: #1d1d1f;
  -webkit-font-smoothing: antialiased;
}

#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="collapsedControl"],
[data-testid="stSidebar"] { display: none !important; }

.main .block-container {
  max-width: 800px !important;
  padding: 56px 24px 96px !important;
  margin: 0 auto !important;
}

h1,h2,h3,h4 {
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", ui-sans-serif, sans-serif !important;
  letter-spacing: -0.022em;
  color: #1d1d1f;
}

/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
  background: #ffffff !important;
  border: 1px solid #d2d2d7 !important;
  border-radius: 10px !important;
  padding: 11px 14px !important;
  font-size: 15px !important;
  font-family: inherit !important;
  color: #1d1d1f !important;
  box-shadow: none !important;
  transition: border-color 0.15s, box-shadow 0.15s;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
  border-color: #0071e3 !important;
  box-shadow: 0 0 0 3px rgba(0,113,227,0.18) !important;
  outline: none !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder { color: #aeaeb2 !important; }
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label {
  font-size: 13px !important;
  font-weight: 500 !important;
  color: #6e6e73 !important;
  letter-spacing: 0.005em;
  margin-bottom: 5px !important;
}

/* ── Buttons ── */
[data-testid="stButton"] button[kind="primary"] {
  background: #0071e3 !important;
  color: #fff !important;
  border: none !important;
  border-radius: 980px !important;
  padding: 11px 22px !important;
  font-size: 15px !important;
  font-weight: 500 !important;
  font-family: inherit !important;
  letter-spacing: -0.01em;
  box-shadow: none !important;
  transition: background 0.15s, transform 0.1s;
}
[data-testid="stButton"] button[kind="primary"]:hover  { background: #0077ed !important; transform: scale(1.01); }
[data-testid="stButton"] button[kind="primary"]:active { background: #006edb !important; transform: scale(0.99); }
[data-testid="stButton"] button[kind="primary"]:disabled {
  background: #d2d2d7 !important; color: #aeaeb2 !important;
  cursor: not-allowed !important; transform: none !important;
}
[data-testid="stButton"] button[kind="secondary"] {
  background: #fff !important;
  color: #1d1d1f !important;
  border: 1px solid #d2d2d7 !important;
  border-radius: 980px !important;
  padding: 9px 18px !important;
  font-size: 14px !important;
  font-weight: 400 !important;
  font-family: inherit !important;
  box-shadow: none !important;
  transition: background 0.12s, border-color 0.12s;
}
[data-testid="stButton"] button[kind="secondary"]:hover { background: #f5f5f7 !important; border-color: #aeaeb2 !important; }

/* ── Download buttons ── */
[data-testid="stDownloadButton"] button {
  background: #fff !important;
  color: #0071e3 !important;
  border: 1px solid #d2d2d7 !important;
  border-radius: 980px !important;
  padding: 9px 18px !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  font-family: inherit !important;
  box-shadow: none !important;
  transition: background 0.12s, border-color 0.12s;
}
[data-testid="stDownloadButton"] button:hover { background: #f0f7ff !important; border-color: #0071e3 !important; }

/* ── Progress ── */
[data-testid="stProgressBar"] > div { background: #e8e8ed !important; border-radius: 4px !important; height: 4px !important; }
[data-testid="stProgressBar"] > div > div { background: #0071e3 !important; border-radius: 4px !important; }

/* ── Expander ── */
[data-testid="stExpander"] {
  border: 1px solid #d2d2d7 !important;
  border-radius: 12px !important;
  background: #fff !important;
  box-shadow: none !important;
}
[data-testid="stExpander"] summary {
  font-size: 14px !important; font-weight: 500 !important; color: #1d1d1f !important; padding: 14px 16px !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [data-baseweb="tab"] {
  font-size: 14px !important; font-weight: 400 !important; color: #6e6e73 !important;
}
[data-testid="stTabs"] [aria-selected="true"] { color: #1d1d1f !important; font-weight: 500 !important; }
[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background: #1d1d1f !important; }

hr { border: none; border-top: 1px solid #d2d2d7 !important; margin: 28px 0 !important; }

/* ── Custom blocks ── */
.nav {
  display: flex; align-items: center; justify-content: space-between;
  padding-bottom: 20px; margin-bottom: 52px;
  border-bottom: 1px solid #d2d2d7;
}
.nav-wordmark { font-size: 17px; font-weight: 600; color: #1d1d1f; letter-spacing: -0.022em; }
.nav-meta { font-size: 12px; color: #aeaeb2; }

.hero { margin-bottom: 44px; }
.hero-title { font-size: 38px; font-weight: 600; letter-spacing: -0.03em; color: #1d1d1f; line-height: 1.08; margin: 0 0 10px; }
.hero-sub   { font-size: 17px; color: #6e6e73; font-weight: 400; line-height: 1.5; margin: 0; }

.eyebrow {
  font-size: 11px; font-weight: 600; color: #aeaeb2;
  letter-spacing: 0.08em; text-transform: uppercase;
  display: block; margin-bottom: 14px;
}

.status-log {
  background: #f5f5f7; border-radius: 10px; padding: 14px 16px;
  font-family: "SF Mono", ui-monospace, "Menlo", monospace;
  font-size: 12px; color: #1d1d1f; line-height: 1.9;
  min-height: 64px; max-height: 200px; overflow-y: auto;
}
.log-row  { display: flex; gap: 10px; align-items: baseline; }
.log-time { color: #aeaeb2; min-width: 32px; }
.log-text { color: #1d1d1f; }

.pipeline-item { display: flex; align-items: flex-start; gap: 11px; padding: 9px 0; }
.pip-icon {
  width: 26px; height: 26px; border-radius: 7px;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; flex-shrink: 0; margin-top: 1px;
}
.ic-teal   { background:#e4f8f0; color:#00b37a; }
.ic-blue   { background:#e6f2ff; color:#0071e3; }
.ic-orange { background:#fff3e6; color:#ff6b00; }
.ic-purple { background:#f0eaff; color:#8b5cf6; }
.ic-indigo { background:#e8eaff; color:#4f5ce3; }
.pip-name  { font-size: 14px; font-weight: 500; color: #1d1d1f; }
.pip-desc  { font-size: 12px; color: #aeaeb2; margin-top: 1px; }

.dot-row   { display: flex; align-items: center; gap: 8px; padding: 11px 0; border-bottom: 1px solid #f5f5f7; }
.dot-row:last-child { border-bottom: none; }
.dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.dot-g { background: #34c759; }
.dot-a { background: #aeaeb2; }
.dot-label { font-size: 14px; color: #1d1d1f; flex: 1; }
.dot-val   { font-size: 13px; color: #aeaeb2; }
.dot-val.ok { color: #34c759; }

.privacy-notice {
  background: #fff; border: 1px solid #d2d2d7; border-radius: 12px;
  padding: 16px 18px; margin-top: 20px;
}
.privacy-title { font-size: 13px; font-weight: 600; color: #1d1d1f; margin-bottom: 5px; }
.privacy-body  { font-size: 12px; color: #6e6e73; line-height: 1.6; }

.usage-pill {
  display: inline-flex; align-items: center; gap: 5px;
  background: #f5f5f7; border: 1px solid #e8e8ed;
  border-radius: 6px; padding: 4px 10px;
  font-size: 12px; color: #6e6e73;
}
.usage-pill.warn { background:#fff3e6; border-color:#ffd09b; color:#b45309; }
.usage-pill.full { background:#ffe8e8; border-color:#ffb3b3; color:#c0392b; }

.brief-header {
  padding: 0 0 20px;
  border-bottom: 1px solid #d2d2d7;
  margin-bottom: 28px;
}
.brief-company { font-size: 26px; font-weight: 600; letter-spacing: -0.022em; color: #1d1d1f; margin: 0; }
.brief-meta    { font-size: 14px; color: #aeaeb2; margin: 4px 0 0; }
</style>
""", unsafe_allow_html=True)

# ── Session state init ─────────────────────────────────────────────────────────
if "briefs_used" not in st.session_state:
    st.session_state.briefs_used = 0
if "ingested" not in st.session_state:
    st.session_state.ingested = os.path.exists("./chroma_db")

# ── Server-side key check ──────────────────────────────────────────────────────
server_ready = bool(OPENAI_KEY)
if OPENAI_KEY:
    os.environ["OPENAI_API_KEY"] = OPENAI_KEY
if TAVILY_KEY:
    os.environ["TAVILY_API_KEY"] = TAVILY_KEY

# ── Nav ────────────────────────────────────────────────────────────────────────
remaining = MAX_BRIEFS_PER_SESSION - st.session_state.briefs_used
pill_cls = "usage-pill full" if remaining == 0 else ("usage-pill warn" if remaining <= 2 else "usage-pill")
st.markdown(f"""
<div class="nav">
  <span class="nav-wordmark">Meeting Prep</span>
  <span class="{pill_cls}">{remaining} of {MAX_BRIEFS_PER_SESSION} briefs remaining</span>
</div>
""", unsafe_allow_html=True)

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <p class="hero-title">Walk in prepared.</p>
  <p class="hero-sub">Enter a company name and your meeting goal.<br>AI agents research, analyse, and write your brief.</p>
</div>
""", unsafe_allow_html=True)

# ── Layout ─────────────────────────────────────────────────────────────────────
left, right = st.columns([3, 2], gap="large")

# ── Right column ───────────────────────────────────────────────────────────────
with right:
    # Service status
    st.markdown('<span class="eyebrow">Service status</span>', unsafe_allow_html=True)

    web_search = bool(TAVILY_KEY)
    kb_ready   = st.session_state.ingested
    st.markdown(f"""
    <div style="background:#fff;border:1px solid #d2d2d7;border-radius:12px;padding:4px 16px;margin-bottom:20px">
      <div class="dot-row">
        <div class="dot {'dot-g' if server_ready else 'dot-a'}"></div>
        <span class="dot-label">AI service</span>
        <span class="dot-val {'ok' if server_ready else ''}">{'Online' if server_ready else 'Unavailable'}</span>
      </div>
      <div class="dot-row">
        <div class="dot {'dot-g' if web_search else 'dot-a'}"></div>
        <span class="dot-label">Web research</span>
        <span class="dot-val {'ok' if web_search else ''}">{'Online' if web_search else 'Offline'}</span>
      </div>
      <div class="dot-row">
        <div class="dot {'dot-g' if kb_ready else 'dot-a'}"></div>
        <span class="dot-label">Knowledge base</span>
        <span class="dot-val {'ok' if kb_ready else ''}">{'Ready' if kb_ready else 'Not loaded'}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Load KB button — only show if not yet loaded
    if not kb_ready:
        if st.button("Load knowledge base", use_container_width=True):
            if not server_ready:
                st.error("Service is unavailable right now.")
            else:
                with st.spinner("Loading…"):
                    try:
                        from utils.ingest import ingest
                        ingest()
                        st.session_state.ingested = True
                        st.rerun()
                    except Exception:
                        st.error("Could not load knowledge base. Please try again.")

    # Pipeline overview
    st.markdown('<span class="eyebrow" style="margin-top:24px;display:block">How it works</span>', unsafe_allow_html=True)
    st.markdown("""
    <div>
      <div class="pipeline-item">
        <div class="pip-icon ic-teal">↗</div>
        <div><div class="pip-name">Retrieve</div><div class="pip-desc">Searches internal knowledge base</div></div>
      </div>
      <div class="pipeline-item">
        <div class="pip-icon ic-blue">◎</div>
        <div><div class="pip-name">Research</div><div class="pip-desc">Finds recent news and signals</div></div>
      </div>
      <div class="pipeline-item">
        <div class="pip-icon ic-orange">◈</div>
        <div><div class="pip-name">Analyse</div><div class="pip-desc">Extracts pain points and angles</div></div>
      </div>
      <div class="pipeline-item">
        <div class="pip-icon ic-purple">▦</div>
        <div><div class="pip-name">Write</div><div class="pip-desc">Drafts talk track and questions</div></div>
      </div>
      <div class="pipeline-item">
        <div class="pip-icon ic-indigo">⟳</div>
        <div><div class="pip-name">Review</div><div class="pip-desc">Quality-checks and retries if needed</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Privacy notice
    st.markdown("""
    <div class="privacy-notice">
      <div class="privacy-title">Data & privacy</div>
      <div class="privacy-body">
        The company name and meeting context you enter are sent to OpenAI to generate your brief.
        No data is stored after your session ends. Do not enter personal data, confidential client
        information, or anything you would not share with a third-party AI provider.
        <a href="https://openai.com/policies/privacy-policy" target="_blank"
           style="color:#0071e3;text-decoration:none"> OpenAI privacy policy.</a>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Left column ────────────────────────────────────────────────────────────────
with left:
    st.markdown('<span class="eyebrow">Your meeting</span>', unsafe_allow_html=True)

    default_company = st.session_state.get("prefill_company", "")
    default_context = st.session_state.get("prefill_context", "")

    company_name = st.text_input(
        "Company name",
        value=default_company,
        placeholder="e.g. Beacon Health",
    )
    meeting_context = st.text_area(
        "Meeting context",
        value=default_context,
        placeholder="Who are you meeting? What is the goal? Any known pain points or signals?",
        height=110,
    )

    # Example chips
    ec1, ec2, ec3 = st.columns(3)
    with ec1:
        if st.button("Beacon Health", key="ex1"):
            st.session_state.prefill_company = "Beacon Health"
            st.session_state.prefill_context = "First discovery call with new CFO. Legacy vendor contract ends June 2025. Goal: qualify budget and book a demo."
            st.rerun()
    with ec2:
        if st.button("Nova Fintech", key="ex2"):
            st.session_state.prefill_company = "Nova Fintech"
            st.session_state.prefill_context = "Second meeting with CTO after they read our LLM underwriting post. Goal: technical deep-dive and POC proposal."
            st.rerun()
    with ec3:
        if st.button("Stellar Retail", key="ex3"):
            st.session_state.prefill_company = "Stellar Retail"
            st.session_state.prefill_context = "First call with CMO. 28% return rate problem flagged on LinkedIn. Goal: surface our returns-reduction case study."
            st.rerun()

    # Clear prefill after pick-up
    if "prefill_company" in st.session_state and company_name == st.session_state.get("prefill_company"):
        st.session_state.pop("prefill_company", None)
        st.session_state.pop("prefill_context", None)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    at_limit = st.session_state.briefs_used >= MAX_BRIEFS_PER_SESSION
    ready    = bool(company_name and meeting_context and server_ready and not at_limit)

    generate = st.button(
        "Generate brief",
        type="primary",
        disabled=not ready,
        use_container_width=True,
    )

    # Contextual hint under button
    if at_limit:
        st.markdown("<p style='font-size:13px;color:#aeaeb2;margin-top:8px'>Session limit reached. Refresh to start a new session.</p>", unsafe_allow_html=True)
    elif not server_ready:
        st.markdown("<p style='font-size:13px;color:#aeaeb2;margin-top:8px'>Service is currently unavailable.</p>", unsafe_allow_html=True)

    # Status log
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown('<span class="eyebrow">Status</span>', unsafe_allow_html=True)
    status_slot = st.empty()
    status_slot.markdown('<div class="status-log"><span style="color:#aeaeb2">Waiting</span></div>', unsafe_allow_html=True)

# ── Pipeline run ───────────────────────────────────────────────────────────────
if generate and ready:
    from graph import run_pipeline
    from utils.pdf_export import brief_to_pdf

    t0        = time.time()
    log_lines: list[str] = []
    start_ts  = time.time()

    def render_log(lines: list[str]) -> None:
        rows = "".join(
            f'<div class="log-row"><span class="log-time">{round(time.time()-start_ts):02d}s</span>'
            f'<span class="log-text">{l}</span></div>'
            for l in lines[-10:]
        )
        status_slot.markdown(f'<div class="status-log">{rows}</div>', unsafe_allow_html=True)

    log_lines.append("Starting")
    render_log(log_lines)
    prog = st.progress(0)

    try:
        prog.progress(8)
        result = run_pipeline(company_name, meeting_context)

        # Strip emoji from internal log entries for clean display
        import re
        for entry in result.get("status_log", []):
            clean = re.sub(r"[^\x00-\x7F]+", "", entry).strip(" :—-")
            if clean:
                log_lines.append(clean)
                render_log(log_lines)

        elapsed = round(time.time() - t0, 1)
        log_lines.append(f"Done in {elapsed}s")
        render_log(log_lines)
        prog.progress(100)

        st.session_state.briefs_used += 1

        final_brief = result.get("final_brief", "")

        if final_brief:
            st.markdown("---")

            st.markdown(f"""
            <div class="brief-header">
              <p class="brief-company">{company_name}</p>
              <p class="brief-meta">Meeting brief  ·  Generated in {elapsed}s</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(final_brief)

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            dl1, dl2, _ = st.columns([1, 1, 2])
            with dl1:
                st.download_button(
                    "Download Markdown",
                    data=final_brief,
                    file_name=f"{company_name.replace(' ', '_')}_brief.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
            with dl2:
                try:
                    pdf_bytes = brief_to_pdf(final_brief)
                    st.download_button(
                        "Download PDF",
                        data=pdf_bytes,
                        file_name=f"{company_name.replace(' ', '_')}_brief.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except Exception:
                    pass

            with st.expander("Raw agent outputs"):
                t1, t2, t3 = st.tabs(["Research", "Insights", "Presentation"])
                with t1: st.json(result.get("research_output", "{}"))
                with t2: st.json(result.get("insights", "{}"))
                with t3: st.json(result.get("presentation", "{}"))

        else:
            prog.empty()
            st.error("Something went wrong generating your brief. Please try again.")

    except Exception:
        prog.empty()
        st.error("Something went wrong. Please try again in a moment.")

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:64px;padding-top:20px;border-top:1px solid #d2d2d7;
            display:flex;justify-content:space-between;align-items:center">
  <span style="font-size:12px;color:#aeaeb2">
    Built with LangGraph, OpenAI, ChromaDB
  </span>
  <span style="font-size:12px;color:#aeaeb2">
    Your data is not stored after this session
  </span>
</div>
""", unsafe_allow_html=True)
