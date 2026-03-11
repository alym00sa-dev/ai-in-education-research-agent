"""EDU Deep Research Agent — main research page."""
import base64
from datetime import datetime

import streamlit as st

from src.exports import export_audit_log_as_json, export_report_as_docx
from src.deep_guided.ui import render_deep_guided, render_dg_progress

# ── Constants ─────────────────────────────────────────────────────────────────

PRESET_QUERIES = {
    "ITS Effectiveness": "What is the effectiveness of Intelligent Tutoring Systems (ITS) on student learning outcomes like mathematics, reading comprehension, and writing ability?",
    "Adaptive Feedback": "What does research show about the effectiveness of immediate feedback versus delayed feedback in tutoring? How does adaptive feedback timing impact student learning gains, retention, and problem-solving ability?",
    "Scaffolding Techniques": "How effective are scaffolding techniques in tutoring? Research on step-by-step problem solving, graduated guidance, hint systems, and fading support. What are the optimal levels of scaffolding for different student populations?",
    "Metacognitive Strategies": "What is the evidence for teaching metacognitive strategies in tutoring? How do self-explanation prompts, reflection activities, and thinking-about-thinking approaches impact learning outcomes, self-efficacy, and transfer?",
    "One-on-One Tutoring": "How does one-on-one human tutoring compare to computer-based tutoring systems? What are the unique benefits of each approach?",
    "Peer Tutoring": "What does the research say about peer tutoring effectiveness? How does student-to-student tutoring impact both the tutor and tutee? Include outcomes on learning gains, engagement, and social-emotional benefits.",
}

AVAILABLE_MODELS = {
    "Claude Sonnet 4.5": "anthropic:claude-sonnet-4-5",
    "Claude Opus 4.5": "anthropic:claude-opus-4-5",
    "GPT 4o": "openai:gpt-4o",
    "GPT 4.1": "openai:gpt-4.1",
    "GPT 5.2": "openai:gpt-5.2-2025-12-11",
    "GPT 5 Mini": "openai:gpt-5-mini-2025-08-07",
}

ALL_COLUMNS = [
    {"key": "title",             "label": "Title"},
    {"key": "year",              "label": "Year"},
    {"key": "study_design",      "label": "Study Design"},
    {"key": "population",        "label": "Population"},
    {"key": "outcome",           "label": "Outcome"},
    {"key": "measure",           "label": "Study Measure"},
    {"key": "finding_direction", "label": "Finding Direction"},
    {"key": "effect_size",       "label": "Effect Size"},
    {"key": "study_size",        "label": "Study Size"},
]
DEFAULT_COLUMN_LABELS = [c["label"] for c in ALL_COLUMNS]

# Maps column key → lambda that extracts the value from a paper dict
_COL_EXTRACTORS = {
    "title":             lambda p: p.get("title", ""),
    "year":              lambda p: p.get("year", ""),
    "study_design":      lambda p: p.get("study_design", ""),
    "population":        lambda p: p.get("population", ""),
    "outcome":           lambda p: p.get("outcome", ""),
    "measure":           lambda p: p.get("measure", ""),
    "finding_direction": lambda p: p.get("finding_direction", ""),
    "effect_size":       lambda p: p.get("effect_size", ""),
    "study_size":        lambda p: p.get("study_size", ""),
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_base64_image(path: str) -> str:
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""


def render_progress_tracker(step: int):
    """Render a 4-step inline progress tracker. step = 1..4."""
    labels = ["Query", "Clarification", "Report Construction", "Final View"]
    parts = []
    for i, label in enumerate(labels):
        n = i + 1
        if n < step:
            parts.append(f"<span style='color:#2563eb;font-weight:600'>✓ {label}</span>")
        elif n == step:
            parts.append(
                f"<span style='color:#2563eb;font-weight:700;"
                f"border-bottom:2px solid #2563eb;padding-bottom:2px'>● {label}</span>"
            )
        else:
            parts.append(f"<span style='color:#9ca3af'>○ {label}</span>")
    arrow = "<span style='color:#d1d5db;margin:0 10px'>→</span>"
    st.markdown(
        f"<div style='margin-bottom:0.25rem'>{arrow.join(parts)}</div>",
        unsafe_allow_html=True,
    )


# ── Sidebar ───────────────────────────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <style>
        [data-testid="stSidebar"] { overflow-y: auto !important; }
        [data-testid="stSidebar"] > div:first-child {
            overflow-y: auto !important; max-height: 100vh !important; padding-top: 0 !important;
        }
        [data-testid="stSidebar"] .block-container { padding-top: 0 !important; margin-top: 0 !important; }
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 0 !important; padding-top: 0 !important; }
        [data-testid="stSidebar"] > div > div { padding-top: 0 !important; }
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:first-child { padding-top: 0 !important; margin-top: 0 !important; }
        [data-testid="stSidebar"] .element-container:first-child { margin-top: 0 !important; padding-top: 0 !important; }
        .logo-container { text-align: center; padding: 0 0 0.75rem 0; border-bottom: 1px solid #e5e7eb; margin: 0 0 1rem 0; }
        .logo-container img { max-width: 85%; height: auto; }
        [data-testid="stSidebar"] button[kind="secondary"] {
            height: auto; min-height: 60px; white-space: normal; word-wrap: break-word;
            text-align: left; background-color: transparent !important; border: none !important;
            box-shadow: none !important; padding: 8px 12px; transition: all 0.2s ease;
        }
        [data-testid="stSidebar"] button[kind="secondary"]:hover { background-color: rgba(240,242,246,0.5) !important; opacity: 1; }
        [data-testid="stSidebar"] button[key="sessions_toggle"] {
            background: transparent !important; border: none !important; box-shadow: none !important;
            padding: 0.5rem !important; text-align: left !important; font-size: 0.75rem !important;
            font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.05em !important;
            color: #6b7280 !important; height: auto !important; min-height: auto !important;
        }
        [data-testid="stSidebar"] button[key="sessions_toggle"]:hover { background: #f9fafb !important; color: #6b7280 !important; }
        </style>
        """, unsafe_allow_html=True)

        logo_b64 = _get_base64_image(
            "/Users/alymoosa/Documents/A-Moosa-Dev/AI-EDU-Dev/GF PRIMARY WEATHERED SLATE LOGO.png"
        )
        if logo_b64:
            st.markdown(
                f'<div class="logo-container"><img src="data:image/png;base64,{logo_b64}" alt="Gates Foundation"></div>',
                unsafe_allow_html=True,
            )

        if not st.session_state.db_initialized:
            st.warning("Could not connect to Neo4j database. Research features will be limited.")

        if st.button("+ New Chat", use_container_width=True, type="primary"):
            st.session_state.current_session_id = None
            st.session_state.research_results = None
            st.session_state.query_text = ""
            st.session_state.just_completed = False
            st.session_state.clarification_screen = None
            st.session_state.construction_screen = None
            st.session_state.selected_columns = None
            st.session_state.report_outline = ""
            st.session_state.stream_event_log = []
            st.rerun()

        st.write("\n\n&nbsp;\n\n", unsafe_allow_html=True)

        st.session_state.selected_mode = st.selectbox(
            "Mode",
            options=["Default", "Deep Guided (BETA)", "Strategic Canvas (BETA)"],
            index=["Default", "Deep Guided (BETA)", "Strategic Canvas (BETA)"].index(
                st.session_state.selected_mode
            ),
        )

        st.info(
            "🔧 This tool is actively under development and tuning. "
            "Results are improving continuously — if a query returns limited findings, "
            "try reframing or narrowing your question."
        )
        st.markdown("<div style='margin-bottom:0.5rem'></div>", unsafe_allow_html=True)

        st.divider()

        caret = "▼" if st.session_state.sessions_expanded else "▶"
        if st.button(f"{caret}  RESEARCH SESSIONS", key="sessions_toggle", use_container_width=True, type="secondary"):
            st.session_state.sessions_expanded = not st.session_state.sessions_expanded
            st.rerun()

        try:
            sessions = st.session_state.session_manager.list_sessions(limit=20)
        except Exception:
            st.warning("Unable to connect to Neo4j database. Session history unavailable.")
            sessions = []

        if st.session_state.sessions_expanded and sessions:
            for session in sessions:
                datetime.fromisoformat(session.created_at).strftime("%b %d, %I:%M %p")
                display_query = session.query if len(session.query) <= 70 else session.query[:70] + "..."

                col1, col2 = st.columns([9, 1])
                with col1:
                    if st.button(display_query, key=f"load_{session.session_id}",
                                 use_container_width=True, type="secondary"):
                        full_session = st.session_state.session_manager.get_session(session.session_id)
                        papers = st.session_state.session_manager.get_session_papers(session.session_id)
                        graph_data = st.session_state.session_manager.get_session_graph(session.session_id)
                        research_summary = (
                            full_session.research_report
                            if full_session and full_session.research_report
                            else f"## Session: {session.query}\n\nLoaded {session.paper_count} papers."
                        )
                        st.session_state.current_session_id = session.session_id
                        st.session_state.research_results = {
                            "session": session.to_dict(),
                            "research_summary": research_summary,
                            "papers_added": session.paper_count,
                            "structured_papers": [
                                {
                                    "title": p.get("title", ""), "url": p.get("url", ""),
                                    "year": p.get("year"), "venue": p.get("venue", ""),
                                    "population": p.get("population", ""),
                                    "user_type": p.get("user_type", ""),
                                    "study_design": p.get("study_design", ""),
                                    "objective": p.get("objective", ""), "outcome": p.get("outcome", ""),
                                    "finding_direction": p.get("finding_direction", ""),
                                    "finding_summary": p.get("finding_summary", ""),
                                    "measure": p.get("measure", ""),
                                    "study_size": p.get("study_size"),
                                    "effect_size": p.get("effect_size"),
                                }
                                for p in papers
                            ],
                            "graph_data": graph_data,
                        }
                        st.session_state.stream_event_log = []
                        st.rerun()
                with col2:
                    if st.button("×", key=f"delete_{session.session_id}",
                                 help="Delete session", use_container_width=True):
                        st.session_state.session_manager.delete_session(session.session_id)
                        if st.session_state.current_session_id == session.session_id:
                            st.session_state.current_session_id = None
                            st.session_state.research_results = None
                        st.rerun()

        elif st.session_state.sessions_expanded and not sessions:
            st.markdown(
                '<p style="text-align:center;color:#6b7280;font-size:0.875rem;padding:2rem 0">'
                "No sessions yet. Start your first research!</p>",
                unsafe_allow_html=True,
            )


# ── Screen: query ─────────────────────────────────────────────────────────────

def render_query_screen():

    col1, col2 = st.columns([2, 3])
    with col1:
        selected_model = st.selectbox("Model", options=list(AVAILABLE_MODELS.keys()), index=3)
        model_provider = AVAILABLE_MODELS[selected_model]
    with col2:
        search_depth_label = st.selectbox(
            "Search Depth",
            options=["standard (~3-5 min)", "deep (~5-7 min)", "comprehensive (~7-10 min)"],
            index=0,
        )
        search_depth = search_depth_label.split()[0]

    st.divider()

    selected_preset = st.selectbox(
        "Select a preset query or enter your own below:",
        options=["Custom Query"] + list(PRESET_QUERIES.keys()),
        key="preset_selector",
    )
    if selected_preset != "Custom Query":
        st.session_state.query_text = PRESET_QUERIES[selected_preset]
    else:
        st.session_state.query_text = ""

    query = st.text_area(
        "Enter your research question:",
        value=st.session_state.query_text,
        height=120,
        placeholder="e.g., What is the effectiveness of intelligent tutoring systems on student learning outcomes in mathematics?",
    )

    _, col_btn2, __ = st.columns([1, 2, 1])
    with col_btn2:
        if st.button("Start Research", type="primary", use_container_width=True):
            if not query.strip():
                st.error("⚠️ Please enter a research question")
            else:
                st.session_state.pending_query = query
                st.session_state.pending_model = model_provider
                st.session_state.pending_search_depth = search_depth
                st.session_state.clarification_screen = "loading"
                st.rerun()

    st.divider()



# ── Screen: clarification loading ─────────────────────────────────────────────

def run_clarification_loading():
    with st.spinner("Analyzing your research question..."):
        result = st.session_state.pipeline.get_clarification(
            query=st.session_state.pending_query,
            model_provider=st.session_state.pending_model,
        )
    st.session_state.clarification_who   = result.get("who", "")
    st.session_state.clarification_what  = result.get("what", "")
    st.session_state.clarification_where = result.get("where", "")
    st.session_state.clarification_when  = result.get("when", "")
    st.session_state.clarification_screen = "showing"
    st.rerun()


# ── Screen: clarification showing ─────────────────────────────────────────────

def render_clarification_screen():
    st.caption("Fill in any details to sharpen your research. Leave fields blank to keep them open-ended.")
    st.divider()

    st.markdown("**Your research question:**")
    st.info(st.session_state.pending_query)
    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        who = st.text_input("Who", value=st.session_state.clarification_who,
                            placeholder="e.g. K-12 students, classroom teachers")
        where = st.text_input("Where", value=st.session_state.clarification_where,
                              placeholder="e.g. U.S. public schools, rural districts")
    with col_b:
        what = st.text_input("What", value=st.session_state.clarification_what,
                             placeholder="e.g. ITS effectiveness on math outcomes")
        when = st.text_input("When", value=st.session_state.clarification_when,
                             placeholder="e.g. last 10 years, 2015–2025")

    st.markdown("---")
    keywords = st.text_input(
        "Keywords *(separate by comma)*",
        placeholder="e.g. intelligent tutoring, formative assessment, randomized controlled trial",
    )
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Skip & Start Research", use_container_width=True, type="secondary"):
            st.session_state.pending_clarification_context = ""
            st.session_state.construction_screen = "loading"
            st.session_state.clarification_screen = None
            st.rerun()
    with col2:
        if st.button("Continue →", use_container_width=True, type="primary"):
            parts = []
            if who:      parts.append(f"Population/Who: {who}")
            if what:     parts.append(f"Focus/What: {what}")
            if where:    parts.append(f"Context/Where: {where}")
            if when:     parts.append(f"Time period/When: {when}")
            if keywords: parts.append(f"Keywords to search: {keywords}")
            st.session_state.pending_clarification_context = "\n".join(parts)
            st.session_state.clarification_screen = None
            st.session_state.construction_screen = "loading"
            st.rerun()


# ── Screen: construction loading ──────────────────────────────────────────────

def run_construction_loading():
    with st.spinner("Generating report structure..."):
        outline = st.session_state.pipeline.get_report_structure(
            query=st.session_state.pending_query,
            context=st.session_state.pending_clarification_context,
            model_provider=st.session_state.pending_model,
        )
    st.session_state.report_outline = outline
    st.session_state.construction_screen = "showing"
    st.rerun()


# ── Screen: construction showing ──────────────────────────────────────────────

def render_construction_screen():
    st.caption("Review and edit the suggested report outline, then choose which data to extract.")
    st.divider()

    st.markdown("**Report Outline**")
    st.caption("Edit the structure below to guide how your final report is organized.")
    outline = st.text_area("outline", value=st.session_state.report_outline,
                           height=300, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("**Data Extraction Columns**")
    st.caption("Choose which fields to include in the data extraction table.")
    selected_labels = st.multiselect(
        "columns", options=DEFAULT_COLUMN_LABELS,
        default=DEFAULT_COLUMN_LABELS, label_visibility="collapsed",
    )

    st.markdown("---")
    _, col2 = st.columns(2)
    with col2:
        if st.button("Start Research →", use_container_width=True, type="primary"):
            st.session_state.report_outline = outline
            st.session_state.selected_columns = [c for c in ALL_COLUMNS if c["label"] in selected_labels]

            clarification_answer = st.session_state.pending_clarification_context
            if outline.strip():
                clarification_answer = (
                    clarification_answer + "\n\nReport outline:\n" + outline.strip()
                    if clarification_answer
                    else "Report outline:\n" + outline.strip()
                )

            # Create session up front so we can reference it during streaming
            session = st.session_state.pipeline.create_session(
                query=st.session_state.pending_query,
                model_provider=st.session_state.pending_model,
                search_depth=st.session_state.pending_search_depth,
            )
            st.session_state.pending_session = session
            st.session_state.pending_clarification_answer = clarification_answer
            st.session_state.construction_screen = None
            st.session_state.research_screen = "streaming"
            st.rerun()


# ── Screen: streaming research ────────────────────────────────────────────────

def render_streaming_screen():
    # Single st.empty() + fillers to atomically clear the construction screen
    content = st.empty()
    _clear = [st.empty() for _ in range(11)]  # noqa: F841

    # ── Streaming state ───────────────────────────────────────────────────────
    query = st.session_state.pending_query

    # system_setup: list of first-person thought strings (supervisor think_tool)
    system_setup: list = []
    system_done: bool = False

    # sub_researchers: [{topic, thoughts, done}]
    # thoughts = first-person reflections from think_tool during research
    sub_researchers: list = []
    done_researcher_count: int = 0  # tracks compress_research ends

    # final report
    final_tokens: str = ""
    final_status: str = ""  # shown inside final expander
    final_done: bool = False

    current_section: str = "system"

    event_log: list = []
    accumulated_report: str = ""
    final_result_metadata = None

    def _thought_block(text: str) -> str:
        return (
            f"<div style='color:#374151;font-style:italic;"
            f"border-left:2px solid #d1d5db;padding-left:0.75rem;"
            f"margin-bottom:0.5rem'>{text}</div>"
        )

    def _redraw():
        with content.container():
            # ── User query bubble ─────────────────────────────────────────
            st.markdown(
                f"<div style='background:#f0f4ff;border-left:3px solid #2563eb;"
                f"padding:0.75rem 1rem;border-radius:4px;margin-bottom:1rem'>"
                f"<span style='color:#6b7280;font-size:0.75rem;font-weight:600;"
                f"text-transform:uppercase;letter-spacing:0.05em'>Your Query</span><br>"
                f"<span style='color:#111827'>{query}</span></div>",
                unsafe_allow_html=True,
            )

            # ── System setup ──────────────────────────────────────────────
            sys_label = "✅ System Setup" if system_done else "⏳ System Setup"
            with st.expander(sys_label, expanded=not system_done):
                st.markdown(
                    _thought_block("I'm analyzing your research question and preparing the research framework."),
                    unsafe_allow_html=True,
                )
                for thought in system_setup:
                    st.markdown(_thought_block(thought), unsafe_allow_html=True)
                if not system_done:
                    st.caption("Planning research strategy...")

            # ── Sub-researchers ───────────────────────────────────────────
            for i, r in enumerate(sub_researchers):
                is_active = not r["done"]
                icon = "⏳" if is_active else "✅"
                short_topic = r["topic"][:80] + "..." if len(r["topic"]) > 80 else r["topic"]
                with st.expander(f"{icon} Deep Research: {short_topic}", expanded=is_active):
                    st.markdown(
                        _thought_block(f"I'm investigating: <em>{r['topic']}</em>"),
                        unsafe_allow_html=True,
                    )
                    for t in r["thoughts"]:
                        st.markdown(_thought_block(t), unsafe_allow_html=True)
                    if is_active:
                        st.caption("Searching and synthesizing sources...")
                    else:
                        st.caption("✓ Research complete.")

            # ── Final report ──────────────────────────────────────────────
            if current_section == "final" or final_tokens or final_status:
                fin_label = "✅ Report Complete" if final_done else "⏳ Writing Final Report"
                with st.expander(fin_label, expanded=not final_done):
                    st.markdown(
                        _thought_block("I'm synthesizing all findings into a comprehensive report."),
                        unsafe_allow_html=True,
                    )
                    if final_tokens:
                        st.markdown(final_tokens)
                    if final_status:
                        st.caption(final_status)
                    elif not final_done:
                        st.caption("Writing...")

    # Initial clean render (white screen)
    _redraw()

    for event in st.session_state.pipeline.stream_research(
        query=query,
        model_provider=st.session_state.pending_model,
        search_depth=st.session_state.pending_search_depth,
        clarification_answer=st.session_state.pending_clarification_answer,
        skip_clarification=True,
    ):
        event_log.append(event)
        etype = event["type"]

        if etype == "section_start":
            current_section = event["content"]
            if current_section == "final":
                system_done = True
                for r in sub_researchers:
                    r["done"] = True
            _redraw()

        elif etype == "section_end" and event["content"] == "final":
            final_done = True
            _redraw()

        elif etype == "thought":
            # Route to system_setup or to the last active sub-researcher
            active = next((r for r in reversed(sub_researchers) if not r["done"]), None)
            if active is not None:
                active["thoughts"].append(event["content"])
            else:
                system_setup.append(event["content"])
            _redraw()

        elif etype == "sub_researcher_start":
            system_done = True
            sub_researchers.append({
                "topic": event["content"],
                "thoughts": [],
                "done": False,
            })
            _redraw()

        elif etype == "sub_researcher_done":
            done_researcher_count += 1
            # Mark the oldest undone researcher as done (parallel dispatch order)
            for r in sub_researchers:
                if not r["done"]:
                    r["done"] = True
                    break
            _redraw()

        elif etype == "token":
            accumulated_report += event["content"]
            final_tokens += event["content"]
            if len(final_tokens) % 300 < 5:
                _redraw()

        elif etype == "result":
            final_result_metadata = event["metadata"]

        elif etype == "error":
            content.error(f"Error during research: {event['content']}")
            st.session_state.research_screen = None
            return

        elif etype == "done":
            final_done = True
            final_status = "Extracting structured data and saving to database..."
            _redraw()
            break

    # Post-processing (shown inside the Final Report expander via final_status)
    if final_result_metadata:
        results = st.session_state.pipeline.finalize_streamed_research(
            session=st.session_state.pending_session,
            research_summary=final_result_metadata.get("summary", accumulated_report),
            sources=final_result_metadata.get("sources", []),
        )
        if accumulated_report:
            results["research_summary"] = accumulated_report

        st.session_state.research_results = results
        st.session_state.current_session_id = results["session"]["session_id"]
        st.session_state.just_completed = True
        st.session_state.stream_event_log = event_log
        st.session_state.research_screen = None
        st.rerun()
    else:
        content.error("Research completed but no results were returned.")
        st.session_state.research_screen = None


# ── Results view (Final View) ─────────────────────────────────────────────────

def _render_results(results: dict):
    tab_report, tab_thoughts = st.tabs(["Report", "Thought Log"])

    with tab_report:
        st.markdown(results["research_summary"])

        # ── Summary table ────────────────────────────────────────────────
        papers = results.get("structured_papers", [])
        if papers:
            st.markdown("---")
            st.markdown("### Summary Table")
            columns = st.session_state.selected_columns or ALL_COLUMNS
            rows = [
                {c["label"]: _COL_EXTRACTORS.get(c["key"], lambda _p: "")(_p) for c in columns}
                for _p in papers
            ]
            st.dataframe(rows, use_container_width=True)

        # ── Download buttons ─────────────────────────────────────────────
        st.markdown("---")
        col_dl1, col_dl2 = st.columns(2)

        docx_bytes = export_report_as_docx(
            research_summary=results["research_summary"],
            session_query=results.get("session", {}).get("query", "Research Report"),
            structured_papers=papers or None,
        )
        with col_dl1:
            st.download_button(
                "⬇ Export Report (.docx)",
                data=docx_bytes,
                file_name="research_report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )

        event_log = st.session_state.get("stream_event_log", [])
        audit_json = export_audit_log_as_json(event_log)
        with col_dl2:
            st.download_button(
                "⬇ Audit Trail (.json)",
                data=audit_json,
                file_name="audit_trail.json",
                mime="application/json",
                use_container_width=True,
            )

    with tab_thoughts:
        event_log = st.session_state.get("stream_event_log", [])
        if not event_log:
            st.info("No thought log available for sessions loaded from history.")
        else:
            def _tblock(text):
                return (
                    f"<div style='color:#374151;font-style:italic;"
                    f"border-left:2px solid #d1d5db;padding-left:0.75rem;"
                    f"margin-bottom:0.5rem'>{text}</div>"
                )

            # Rebuild sections from event log
            system_thoughts = []
            researchers = []   # [{topic, thoughts}]
            final_tokens_replay = ""

            for e in event_log:
                if e["type"] == "sub_researcher_start":
                    researchers.append({"topic": e["content"], "thoughts": []})
                elif e["type"] == "thought":
                    # Assign to last undone researcher, or system if none started
                    if researchers:
                        researchers[-1]["thoughts"].append(e["content"])
                    else:
                        system_thoughts.append(e["content"])
                elif e["type"] == "token":
                    final_tokens_replay += e["content"]

            # ── System Setup ──────────────────────────────────────────────
            with st.expander("✅ System Setup", expanded=True):
                st.markdown(
                    _tblock("I analyzed your research question and prepared the research framework."),
                    unsafe_allow_html=True,
                )
                for t in system_thoughts:
                    st.markdown(_tblock(t), unsafe_allow_html=True)

            # ── Deep Research sections ────────────────────────────────────
            for i, r in enumerate(researchers):
                short = r["topic"][:80] + "..." if len(r["topic"]) > 80 else r["topic"]
                with st.expander(f"✅ Deep Research: {short}", expanded=False):
                    st.markdown(
                        _tblock(f"I investigated: <em>{r['topic']}</em>"),
                        unsafe_allow_html=True,
                    )
                    for t in r["thoughts"]:
                        st.markdown(_tblock(t), unsafe_allow_html=True)

            # ── Final Report ──────────────────────────────────────────────
            if final_tokens_replay:
                with st.expander("✅ Final Report Written", expanded=False):
                    st.markdown(
                        _tblock("I synthesized all findings into a comprehensive report."),
                        unsafe_allow_html=True,
                    )
                    st.markdown(final_tokens_replay)


# ── Global styles ─────────────────────────────────────────────────────────────

st.markdown("""
<style>
button[kind="primary"] {
    background: #2563eb !important;
    border: none !important;
    transition: background 0.2s ease !important;
}
button[kind="primary"]:hover { background: #1d4ed8 !important; }
</style>
""", unsafe_allow_html=True)

# ── Init extra session state keys used only in this page ─────────────────────

if "stream_event_log" not in st.session_state:
    st.session_state.stream_event_log = []
if "research_screen" not in st.session_state:
    st.session_state.research_screen = None
if "pending_clarification_answer" not in st.session_state:
    st.session_state.pending_clarification_answer = ""
if "pending_session" not in st.session_state:
    st.session_state.pending_session = None

# ── Dispatch ──────────────────────────────────────────────────────────────────

render_sidebar()

mode = st.session_state.get("selected_mode", "Default")

# ── Shared header (always visible) ────────────────────────────────────────────

st.title("📚 EDU Deep Research Agent")

_main_callouts = {
    "Default": (
        "Enter your research question below. The agent will clarify your scope, build a report "
        "outline, then synthesize evidence from academic and credible sources into a structured report."
    ),
    "Deep Guided (BETA)": (
        "Start by describing your broad research intent in the chat below. The advisor will ask "
        "clarifying questions and help you develop a precise set of research goals — no research "
        "begins until your goals are confirmed and configured."
    ),
    "Strategic Canvas (BETA)": (
        "Describe a strategic challenge or goal. The agent will help you identify the research "
        "questions that need answering and map the evidence landscape — built for discovery, "
        "not just answers."
    ),
}
st.info(_main_callouts.get(mode, ""))

# Mode-appropriate progress tracker
if mode == "Deep Guided (BETA)":
    render_dg_progress(st.session_state.get("dg_step", 1))
elif mode == "Strategic Canvas (BETA)":
    pass  # tracker TBD
else:
    if st.session_state.get("clarification_screen") in ("loading", "showing"):
        _cur_step = 2
    elif st.session_state.get("construction_screen") in ("loading", "showing"):
        _cur_step = 3
    elif st.session_state.get("research_screen") == "streaming" or st.session_state.get("research_results"):
        _cur_step = 4
    else:
        _cur_step = 1
    render_progress_tracker(_cur_step)

st.divider()

# ── Mode content ───────────────────────────────────────────────────────────────

if mode == "Deep Guided (BETA)":
    render_deep_guided()
elif mode == "Strategic Canvas (BETA)":
    st.info("Strategic Canvas mode is coming soon.")
else:
    # Default mode
    if st.session_state.clarification_screen == "loading":
        run_clarification_loading()
    elif st.session_state.clarification_screen == "showing":
        render_clarification_screen()
    elif st.session_state.construction_screen == "loading":
        run_construction_loading()
    elif st.session_state.construction_screen == "showing":
        render_construction_screen()
    elif st.session_state.research_screen == "streaming":
        render_streaming_screen()
    elif st.session_state.research_results:
        _render_results(st.session_state.research_results)
    else:
        render_query_screen()
