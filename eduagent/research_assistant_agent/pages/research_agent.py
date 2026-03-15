"""EDU Deep Research Agent — main research page."""
import base64
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as _components

from src.exports import export_report_as_docx, export_session_as_json
from src.audit_writer import load_session_audit

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
    "Claude Sonnet 4.6": "anthropic:claude-sonnet-4-6",
    "Claude Opus 4.6": "anthropic:claude-opus-4-6",
    "Claude Haiku 4.5": "anthropic:claude-haiku-4-5-20251001",
    "Claude Sonnet 4.5": "anthropic:claude-sonnet-4-5",
    "Claude Opus 4.5": "anthropic:claude-opus-4-5",
    "GPT 4o": "openai:gpt-4o",
    "GPT 4.1": "openai:gpt-4.1",
    "GPT 5.4": "openai:gpt-5.4-2026-03-05",
    "GPT 5.2": "openai:gpt-5.2-2025-12-11",
    "GPT 5 Mini": "openai:gpt-5-mini-2025-08-07",
}

ALL_COLUMNS = [
    {"key": "title",               "label": "Title"},
    {"key": "year",                "label": "Year"},
    {"key": "study_design",        "label": "Study Design"},
    {"key": "population",          "label": "Population"},
    {"key": "outcome",             "label": "Outcome"},
    {"key": "measure",             "label": "Study Measure"},
    {"key": "finding_direction",   "label": "Finding Direction"},
    {"key": "effect_size",         "label": "Effect Size"},
    {"key": "confidence_interval", "label": "Confidence Interval"},
    {"key": "std_deviation",       "label": "Std. Deviation"},
    {"key": "study_size",          "label": "Study Size"},
]
DEFAULT_COLUMN_LABELS = [c["label"] for c in ALL_COLUMNS]

# Maps column key → lambda that extracts the value from a paper dict
_COL_EXTRACTORS = {
    "title":               lambda p: p.get("title", ""),
    "year":                lambda p: p.get("year", ""),
    "study_design":        lambda p: p.get("study_design", ""),
    "population":          lambda p: p.get("population", ""),
    "outcome":             lambda p: p.get("outcome", ""),
    "measure":             lambda p: p.get("measure", ""),
    "finding_direction":   lambda p: p.get("finding_direction", ""),
    "effect_size":         lambda p: p.get("effect_size", ""),
    "confidence_interval": lambda p: p.get("confidence_interval", ""),
    "std_deviation":       lambda p: p.get("std_deviation", ""),
    "study_size":          lambda p: p.get("study_size", ""),
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_base64_image(path: str) -> str:
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""


def render_progress_tracker(step: int):
    """Render a 3-step inline progress tracker. step = 1..3."""
    labels = ["Query", "Report Construction", "Final View"]
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

        if not st.session_state.get("db_initialized"):
            st.warning("Could not connect to Neo4j database. Research features will be limited.")

        if st.button("+ New Chat", use_container_width=True, type="primary"):
            st.session_state.current_session_id = None
            st.session_state.research_results = None
            st.session_state.query_text = ""
            st.session_state.just_completed = False
            st.session_state.construction_screen = None
            st.session_state.selected_columns = None
            st.session_state.report_outline = ""
            st.session_state.stream_event_log = []
            st.rerun()

        st.write("\n\n&nbsp;\n\n", unsafe_allow_html=True)

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
                        # Try to restore QA fields from local audit file
                        audit = load_session_audit(session.session_id)

                        st.session_state.current_session_id = session.session_id
                        st.session_state.research_results = {
                            "session": session.to_dict(),
                            "research_summary": research_summary,
                            "papers_added": session.paper_count,
                            "structured_papers": (
                                audit.get("structured_papers")
                                or [
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
                                ]
                            ),
                            "graph_data": graph_data,
                            # Quality Assessment fields — present for sessions that have audit files
                            "qa_assessment": audit.get("qa_assessment"),
                            "extraction_table": audit.get("extraction_table"),
                            "swanson_hypotheses": audit.get("swanson_hypotheses"),
                            "causality_diagram": audit.get("causality_diagram"),
                            "sub_researcher_notes": audit.get("sub_researcher_notes") or [],
                        }
                        st.session_state.stream_event_log = audit.get("event_log", [])
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

    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        selected_model = st.selectbox("Model", options=list(AVAILABLE_MODELS.keys()), index=8)
        model_provider = AVAILABLE_MODELS[selected_model]
    with col2:
        search_depth_label = st.selectbox(
            "Search Depth",
            options=["standard (~3-5 min)", "deep (~5-7 min)", "comprehensive (~7-10 min)"],
            index=0,
        )
        search_depth = search_depth_label.split()[0]
    with col3:
        max_sources = st.slider("Citation Cap", min_value=20, max_value=50, value=30, step=1)
        st.caption("Upper limit — cite what the evidence warrants, not a target.")

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

    keywords = st.text_input(
        "Keywords *(separate by comma)*",
        placeholder="e.g., intelligent tutoring, formative assessment, randomized controlled trial",
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
                st.session_state.pending_max_sources = max_sources
                st.session_state.pending_clarification_context = (
                    f"Keywords to search: {keywords}" if keywords.strip() else ""
                )
                st.session_state.construction_screen = "loading"
                st.rerun()

    st.divider()



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

    st.markdown("**Custom Columns** *(optional)*")
    st.caption("Add a column the standard set doesn't cover. Be specific in the extraction instruction so the model knows what to look for.")

    # Render existing custom columns with remove buttons
    for idx, col in enumerate(st.session_state.pending_custom_columns):
        c1, c2, c3 = st.columns([3, 5, 1])
        with c1:
            st.markdown(f"**{col['label']}**")
        with c2:
            st.caption(col["instruction"])
        with c3:
            if st.button("✕", key=f"rm_col_{idx}"):
                st.session_state.pending_custom_columns.pop(idx)
                st.rerun()

    with st.expander("+ Add custom column"):
        ca, cb = st.columns([2, 4])
        with ca:
            new_col_label = st.text_input("Column name", placeholder="e.g. Implementation Cost", key="new_col_label")
        with cb:
            new_col_instruction = st.text_input(
                "Extraction instruction",
                placeholder="e.g. What does the paper say about cost or resource requirements?",
                key="new_col_instruction",
            )
        if st.button("+ Add", key="add_custom_col"):
            if new_col_label.strip() and new_col_instruction.strip():
                st.session_state.pending_custom_columns.append({
                    "label": new_col_label.strip(),
                    "instruction": new_col_instruction.strip(),
                })
                st.rerun()

    st.markdown("---")
    col_l, col_btn, col_r = st.columns([1, 2, 1])
    with col_btn:
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

            # Append custom column instructions so the pipeline knows what to extract
            if st.session_state.pending_custom_columns:
                custom_block = "\n\nCustom data extraction columns:\n" + "\n".join(
                    f"- {c['label']}: {c['instruction']}"
                    for c in st.session_state.pending_custom_columns
                )
                clarification_answer = (clarification_answer or "") + custom_block

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

    # sub_researchers: [{topic, done}]  — thoughts are in the flat log, not per-researcher
    sub_researchers: list = []
    done_researcher_count: int = 0  # tracks compress_research ends

    # flat_thoughts: unified log across all researchers
    # each entry: {"label": str, "content": str, "is_critique": bool}
    flat_thoughts: list = []

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

            # ── Sub-researchers — topic pills only, no individual thought lists ──
            if sub_researchers:
                for i, r in enumerate(sub_researchers):
                    is_active = not r["done"]
                    icon = "⏳" if is_active else "✅"
                    status_text = "Searching and synthesizing..." if is_active else "Research complete"
                    st.markdown(
                        f"<div style='display:flex;align-items:flex-start;gap:0.5rem;"
                        f"padding:0.5rem 0.75rem;margin-bottom:0.4rem;"
                        f"border-radius:6px;background:{'#f0fdf4' if not is_active else '#f0f4ff'};"
                        f"border:1px solid {'#bbf7d0' if not is_active else '#bfdbfe'}'>"
                        f"<span style='font-size:0.85rem;margin-top:0.05rem'>{icon}</span>"
                        f"<div style='flex:1'>"
                        f"<div style='font-size:0.8rem;font-weight:600;color:#111827;"
                        f"white-space:normal;word-break:break-word'>{r['topic']}</div>"
                        f"<div style='font-size:0.7rem;color:#6b7280'>{status_text}</div>"
                        f"</div></div>",
                        unsafe_allow_html=True,
                    )

            # ── Flat research thought log ─────────────────────────────────
            if flat_thoughts or sub_researchers:
                thoughts_label = "⏳ Research Thoughts" if any(not r["done"] for r in sub_researchers) else "✅ Research Thoughts"
                with st.expander(thoughts_label, expanded=True):
                    if not flat_thoughts:
                        st.caption("Thoughts will appear here as researchers work...")
                    for entry in flat_thoughts:
                        if entry.get("is_critique"):
                            st.markdown(
                                f"<div style='color:#7c3aed;font-style:italic;font-size:0.82rem;"
                                f"border-left:2px solid #a78bfa;padding-left:0.75rem;"
                                f"margin-bottom:0.4rem'>"
                                f"<strong>Critique [{entry['label']}]:</strong> {entry['content']}</div>",
                                unsafe_allow_html=True,
                            )
                        else:
                            label_html = (
                                f"<span style='font-size:0.7rem;font-weight:600;color:#6b7280;"
                                f"text-transform:uppercase;letter-spacing:0.04em'>{entry['label']}</span><br>"
                                if entry.get("label") else ""
                            )
                            st.markdown(
                                f"<div style='color:#374151;font-style:italic;font-size:0.82rem;"
                                f"border-left:2px solid #d1d5db;padding-left:0.75rem;"
                                f"margin-bottom:0.4rem'>{label_html}{entry['content']}</div>",
                                unsafe_allow_html=True,
                            )

            # ── Final report ──────────────────────────────────────────────
            if current_section == "final" or final_tokens or final_status:
                if final_status:
                    fin_label = "⏳ Saving to database..."
                elif final_done:
                    fin_label = "⏳ Finalizing..."
                else:
                    fin_label = "⏳ Writing Final Report"
                with st.expander(fin_label, expanded=True):
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
        max_sources=st.session_state.get("pending_max_sources", 20),
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
            research_topic = (event.get("metadata") or {}).get("research_topic", "")
            # Determine label: researcher topic if known, else "Supervisor"
            if research_topic:
                short = research_topic[:60] + "..." if len(research_topic) > 60 else research_topic
                label = short
            elif sub_researchers:
                label = "Supervisor"
            else:
                label = "Supervisor"
                system_setup.append(event["content"])
            flat_thoughts.append({"label": label, "content": event["content"], "is_critique": False})
            _redraw()

        elif etype == "critique":
            research_topic = (event.get("metadata") or {}).get("research_topic", "")
            short = research_topic[:60] + "..." if len(research_topic) > 60 else research_topic
            flat_thoughts.append({"label": short or "Researcher", "content": event["content"], "is_critique": True})
            _redraw()

        elif etype == "sub_researcher_start":
            system_done = True
            topic = event["content"]
            if not any(r["topic"] == topic for r in sub_researchers):
                sub_researchers.append({"topic": topic, "done": False})
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
            audit_data=final_result_metadata,
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


# ── Quality Assessment helpers ────────────────────────────────────────────────

def _confidence_badge(confidence: str) -> str:
    color = {"Strong": "#16a34a", "Moderate": "#d97706", "Speculative": "#6b7280"}.get(confidence, "#6b7280")
    return (
        f"<span style='background:{color};color:#fff;font-size:0.7rem;font-weight:600;"
        f"padding:2px 8px;border-radius:999px;letter-spacing:0.05em'>{confidence}</span>"
    )


def _render_hypothesis_card(h: dict, index: int):
    confidence = h.get("confidence", "Speculative")
    badge = _confidence_badge(confidence)
    a, b, c = h.get("A", ""), h.get("B", ""), h.get("C", "")
    # Handle both naming conventions the LLM might output
    mech_ab = h.get("mechanism_AB") or h.get("A_to_B_mechanism") or ""
    mech_bc = h.get("mechanism_BC") or h.get("B_to_C_mechanism") or ""
    cites_ab = h.get("citations_AB") or h.get("A_to_B_citations") or []
    cites_bc = h.get("citations_BC") or h.get("B_to_C_citations") or []
    rationale = h.get("rationale", "")

    cite_ab_str = "; ".join(str(c) for c in cites_ab) if cites_ab else "—"
    cite_bc_str = "; ".join(str(c) for c in cites_bc) if cites_bc else "—"

    chain_html = f"<strong>{a}</strong> → <strong>{b}</strong> → <strong>{c}</strong>"
    legs_html = ""
    if mech_ab or mech_bc:
        legs_html = (
            f"<div style='font-size:0.8rem;color:#6b7280;margin-top:0.4rem'>"
            f"<em>A→B:</em> {mech_ab} <span style='color:#9ca3af'>({cite_ab_str})</span><br>"
            f"<em>B→C:</em> {mech_bc} <span style='color:#9ca3af'>({cite_bc_str})</span>"
            f"</div>"
        )
    else:
        legs_html = (
            f"<div style='font-size:0.8rem;color:#6b7280;margin-top:0.4rem'>"
            f"<em>A→B citations:</em> {cite_ab_str}<br>"
            f"<em>B→C citations:</em> {cite_bc_str}"
            f"</div>"
        )
    rationale_html = (
        f"<div style='font-size:0.78rem;color:#9ca3af;margin-top:0.4rem;font-style:italic'>{rationale}</div>"
        if rationale else ""
    )

    st.markdown(
        f"<div style='border:1px solid #e5e7eb;border-radius:8px;padding:1rem;"
        f"margin-bottom:0.75rem;background:#fafafa'>"
        f"<div style='display:flex;align-items:center;gap:0.5rem;margin-bottom:0.5rem'>"
        f"<span style='font-weight:600;color:#111827'>Hypothesis {index + 1}</span>"
        f"{badge}</div>"
        f"<div style='font-size:0.9rem;color:#374151;margin-bottom:0.25rem'>{chain_html}</div>"
        f"{legs_html}{rationale_html}"
        f"</div>",
        unsafe_allow_html=True,
    )


def _parse_note_section(note: str, header: str, stop_headers: list) -> str:
    """Extract the content of a named section from a structured note string."""
    if header not in note:
        return ""
    after = note.split(header, 1)[1]
    for stop in stop_headers:
        if stop in after:
            after = after.split(stop, 1)[0]
    return after.strip()


def _render_source_log(notes: list):
    if not notes:
        st.info("No source log available — this session predates the structured note format.")
        return

    included_all = []
    excluded_all = []

    for note in notes:
        inc = _parse_note_section(note, "### SOURCES USED", ["### SOURCES EXCLUDED", "### MECHANISMS"])
        exc = _parse_note_section(note, "### SOURCES EXCLUDED", ["### MECHANISMS"])
        if inc:
            included_all.append(inc)
        if exc:
            excluded_all.append(exc)

    st.markdown(
        "<div style='font-weight:600;color:#16a34a;margin-bottom:0.5rem'>"
        "✓ Included Sources</div>",
        unsafe_allow_html=True,
    )
    if included_all:
        for block in included_all:
            st.markdown(block)
    else:
        st.caption("No inclusion data available.")

    st.markdown("---")

    st.markdown(
        "<div style='font-weight:600;color:#dc2626;margin-bottom:0.5rem'>"
        "✗ Excluded Sources</div>",
        unsafe_allow_html=True,
    )
    if excluded_all:
        for block in excluded_all:
            st.markdown(block)
    else:
        st.caption("No exclusion data available.")


def _render_quality_assessment_tab(results: dict):
    qa_assessment = results.get("qa_assessment")
    notes = results.get("sub_researcher_notes") or []

    # ── Coverage Assessment ───────────────────────────────────────────────
    st.markdown("### Coverage Assessment")
    if qa_assessment:
        st.markdown(qa_assessment)
    else:
        st.info("No coverage assessment available for this session.")

    st.divider()

    # ── Source Inclusion / Exclusion Log ─────────────────────────────────
    st.markdown("### Source Inclusion Log")
    st.caption("Compiled from sub-researcher structured outputs. Included = passed relevance and quality gates. Excluded = filtered out with reason.")
    _render_source_log(notes)


# ── Results view (Final View) ─────────────────────────────────────────────────

def _render_report_section2(results: dict):
    """Render Section 2 as side-by-side hypothesis cards + interactive Mermaid diagram."""
    swanson_hypotheses = results.get("swanson_hypotheses") or []
    causality_diagram = results.get("causality_diagram") or ""

    col_hyp, col_diag = st.columns([1, 1])

    with col_hyp:
        st.markdown("### Novel Hypotheses")
        st.caption("Surfaced via Swanson ABC chaining — novel A→C connections not explicitly stated in any single source.")
        if swanson_hypotheses:
            for idx, h in enumerate(swanson_hypotheses):
                _render_hypothesis_card(h, idx)
        else:
            st.info("No novel hypotheses were identified for this session.")

    with col_diag:
        st.markdown("### Causality Diagram")
        st.caption("Copy the block below and paste into [mermaid.live](https://mermaid.live) to render interactively.")
        if causality_diagram and "graph" in causality_diagram:
            raw = causality_diagram
            if "```mermaid" in raw:
                raw = raw.split("```mermaid", 1)[1].rsplit("```", 1)[0].strip()
            # Fix single-% comment lines → %% (LLM sometimes outputs invalid syntax)
            fixed_lines = []
            for line in raw.splitlines():
                stripped = line.lstrip()
                if stripped.startswith("%") and not stripped.startswith("%%"):
                    line = line.replace("%", "%%", 1)
                fixed_lines.append(line)
            raw = "\n".join(fixed_lines)
            mermaid_html = f"""
<div style="background:#fff;padding:1rem;border-radius:8px;border:1px solid #e5e7eb;overflow:auto">
  <div class="mermaid">{raw}</div>
</div>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>mermaid.initialize({{startOnLoad:true,theme:'default',securityLevel:'loose'}});</script>
"""
            _components.html(mermaid_html, height=480, scrolling=True)
        else:
            st.info("No causality diagram was generated for this session.")


def _render_results(results: dict):
    import re as _re

    tab_report, tab_qa = st.tabs(["Report", "Quality Assessment"])

    with tab_report:
        report_text = results["research_summary"]

        query_title = results.get("session", {}).get("query", "")
        if query_title:
            st.markdown(f"# {query_title}")

        # Split report at Section 2 so we can replace the raw Mermaid block
        # with the interactive hypothesis cards + rendered diagram
        sec2_match = _re.search(r"##\s*Section\s*2", report_text)
        sec3_match = _re.search(r"##\s*Section\s*3", report_text)

        if sec2_match and sec3_match:
            st.markdown(report_text[: sec2_match.start()])
            st.markdown("## Section 2 — Causality Diagram")
            _render_report_section2(results)
            st.markdown(report_text[sec3_match.start() :])
            st.markdown("""
<div style='background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:1rem 1.25rem;margin-top:1rem;font-size:0.82rem;color:#374151'>
<strong>Source scoring uses the K-12 Evidence Framework</strong><br><br>
<strong>Quality</strong> — evaluates research design, credibility, and relevance to U.S. K-12 contexts:<br>
🔵 <strong>Blue</strong> — Highest quality: meta-analysis or well-designed RCT, peer-reviewed, disaggregated by race/income, representative of priority populations (Black, Latino, poverty)<br>
🟢 <strong>Green</strong> — Moderate to strong: quasi-experimental or correlational, credible source, somewhat relevant population<br>
🟡 <strong>Yellow</strong> — Limited or weaker: opinion/descriptive/case study, limited peer review, general or non-representative population<br>
🔴 <strong>Red</strong> — Low or unacceptable: no credible evidence, anecdotal, conflicts of interest<br><br>
<strong>Impact</strong> — evaluates effect size and reach for priority populations:<br>
🔵 <strong>Blue</strong> — Medium or large impact on priority populations (Black, Latino, students in poverty)<br>
🟢 <strong>Green</strong> — Modest impact on priority populations OR medium/large impact on general population<br>
🟡 <strong>Yellow</strong> — Modest impact on general population, not priority populations<br>
🔴 <strong>Red</strong> — No impact or negative impact<br><br>
<strong>Body of Evidence Maturity:</strong>
🔵 Mature — 🟢 Limited — 🟡 Emerging — 🔴 Early
</div>
""", unsafe_allow_html=True)
        else:
            st.markdown(report_text)

        papers = results.get("structured_papers", [])

        # ── Download buttons ─────────────────────────────────────────────
        st.markdown("---")
        col_dl1, col_dl2 = st.columns(2)

        docx_bytes = export_report_as_docx(
            research_summary=results["research_summary"],
            session_query=results.get("session", {}).get("query", "Research Report"),
            structured_papers=papers or None,
            selected_columns=st.session_state.get("selected_columns") or None,
            results=results,
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
        session_json = export_session_as_json(results=results, event_log=event_log)
        with col_dl2:
            st.download_button(
                "⬇ Session Export (.json)",
                data=session_json,
                file_name="research_session.json",
                mime="application/json",
                use_container_width=True,
            )

    with tab_qa:
        _render_quality_assessment_tab(results)


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

st.title("📚 EduAgent")

st.info(
    "Enter your research question below. Parallel sub-researchers will mine academic databases "
    "and peer-reviewed literature, then synthesize findings into an evidence-graded report."
)

if st.session_state.get("construction_screen") in ("loading", "showing"):
    _cur_step = 2
elif st.session_state.get("research_screen") == "streaming" or st.session_state.get("research_results"):
    _cur_step = 3
else:
    _cur_step = 1
render_progress_tracker(_cur_step)

st.divider()

if st.session_state.construction_screen == "loading":
    run_construction_loading()
elif st.session_state.construction_screen == "showing":
    render_construction_screen()
elif st.session_state.research_screen == "streaming":
    render_streaming_screen()
elif st.session_state.research_results:
    _render_results(st.session_state.research_results)
else:
    render_query_screen()
