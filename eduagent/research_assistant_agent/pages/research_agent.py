"""EDU Deep Research Agent - main research page."""
import streamlit as st
from datetime import datetime
import base64


def get_base64_image(image_path):
    """Convert image to base64 string."""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        print(f"Error loading image: {e}")
        return ""


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

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        overflow-y: auto !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        overflow-y: auto !important;
        max-height: 100vh !important;
        padding-top: 0 !important;
    }
    [data-testid="stSidebar"] .block-container {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0 !important;
        padding-top: 0 !important;
    }
    [data-testid="stSidebar"] > div > div {
        padding-top: 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:first-child {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    [data-testid="stSidebar"] .element-container:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    .logo-container {
        text-align: center;
        padding: 0 0 0.75rem 0;
        border-bottom: 1px solid #e5e7eb;
        margin: 0 0 1rem 0;
    }
    .logo-container img {
        max-width: 85%;
        height: auto;
    }
    [data-testid="stSidebar"] button[kind="secondary"] {
        height: auto;
        min-height: 60px;
        white-space: normal;
        word-wrap: break-word;
        text-align: left;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 8px 12px;
        transition: all 0.2s ease;
    }
    [data-testid="stSidebar"] button[kind="secondary"]:hover {
        background-color: rgba(240, 242, 246, 0.5) !important;
        opacity: 1;
    }
    [data-testid="stSidebar"] button[key="sessions_toggle"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0.5rem !important;
        text-align: left !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        color: #6b7280 !important;
        height: auto !important;
        min-height: auto !important;
    }
    [data-testid="stSidebar"] button[key="sessions_toggle"]:hover {
        background: #f9fafb !important;
        color: #6b7280 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Logo
    logo_base64 = get_base64_image("/Users/alymoosa/Documents/A-Moosa-Dev/AI-EDU-Dev/GF PRIMARY WEATHERED SLATE LOGO.png")
    if logo_base64:
        st.markdown(f"""
        <div class="logo-container">
            <img src="data:image/png;base64,{logo_base64}" alt="Gates Foundation">
        </div>
        """, unsafe_allow_html=True)

    if not st.session_state.db_initialized:
        st.warning("Could not connect to Neo4j database. Research features will be limited.")

    st.divider()

    # Session history
    caret_icon = "▼" if st.session_state.sessions_expanded else "▶"
    if st.button(f"{caret_icon}  RESEARCH SESSIONS", key="sessions_toggle", use_container_width=True, type="secondary"):
        st.session_state.sessions_expanded = not st.session_state.sessions_expanded
        st.rerun()

    try:
        sessions = st.session_state.session_manager.list_sessions(limit=20)
    except Exception:
        st.warning("Unable to connect to Neo4j database. Session history unavailable.")
        sessions = []

    if st.session_state.sessions_expanded and sessions:
        for session in sessions:
            created_date = datetime.fromisoformat(session.created_at).strftime('%b %d, %I:%M %p')
            display_query = session.query if len(session.query) <= 70 else session.query[:70] + "..."

            col1, col2 = st.columns([9, 1])
            with col1:
                if st.button(
                    display_query,
                    key=f"load_{session.session_id}",
                    use_container_width=True,
                    type="secondary"
                ):
                    st.session_state.current_session_id = session.session_id
                    full_session = st.session_state.session_manager.get_session(session.session_id)
                    graph_data = st.session_state.session_manager.get_session_graph(session.session_id)
                    papers = st.session_state.session_manager.get_session_papers(session.session_id)
                    research_summary = (
                        full_session.research_report
                        if full_session and full_session.research_report
                        else f"## Session: {session.query}\n\nLoaded {session.paper_count} papers from this research session."
                    )
                    st.session_state.research_results = {
                        "session": session.to_dict(),
                        "research_summary": research_summary,
                        "papers_added": session.paper_count,
                        "structured_papers": [
                            {
                                "title": p.get("title", "Unknown"),
                                "url": p.get("url", ""),
                                "objective": p.get("objective", ""),
                                "outcome": p.get("outcome", ""),
                                "finding_direction": p.get("finding_direction", ""),
                                "finding_summary": p.get("finding_summary", ""),
                                "measure": p.get("measure", ""),
                                "study_size": p.get("study_size"),
                                "effect_size": p.get("effect_size")
                            }
                            for p in papers
                        ],
                        "graph_data": graph_data
                    }
                    st.rerun()

            with col2:
                if st.button("×", key=f"delete_{session.session_id}", help="Delete session", use_container_width=True):
                    st.session_state.session_manager.delete_session(session.session_id)
                    if st.session_state.current_session_id == session.session_id:
                        st.session_state.current_session_id = None
                        st.session_state.research_results = None
                    st.rerun()

    elif st.session_state.sessions_expanded and not sessions:
        st.markdown(
            '<p style="text-align: center; color: #6b7280; font-size: 0.875rem; padding: 2rem 0;">'
            'No sessions yet. Start your first research!</p>',
            unsafe_allow_html=True
        )

# ── Main content ──────────────────────────────────────────────────────────────
st.title("📚 EDU Deep Research Agent")
st.info("ℹ️ This is an MVP of the deep research agent, synthesizing literature across credible and publication sources. If your query has no results, try reframing your question(s).")

st.divider()

st.markdown("""
<style>
button[kind="primary"] {
    background: #667eea !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px 0 rgba(102, 126, 234, 0.4) !important;
}
button[kind="primary"]:hover {
    background: #5568d3 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px 0 rgba(102, 126, 234, 0.6) !important;
}
button[kind="primary"]:active {
    transform: translateY(0px) !important;
}
div[data-baseweb="select"] {
    border-radius: 10px !important;
}
textarea {
    border-radius: 10px !important;
    border: 2px solid #e5e7eb !important;
    transition: border-color 0.2s ease !important;
}
textarea:focus {
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
}
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 3])
with col1:
    selected_model = st.selectbox(
        "Model",
        options=list(AVAILABLE_MODELS.keys()),
        index=3,
        help="Select the AI model for research"
    )
    model_provider = AVAILABLE_MODELS[selected_model]

with col2:
    search_depth = st.selectbox(
        "Search Depth",
        options=[
            "standard (~3-5 min)",
            "deep (~5-7 min)",
            "comprehensive (~7-10 min)"
        ],
        index=0,
        help="Control the depth and thoroughness of research"
    )
    search_depth = search_depth.split()[0]

focus_area = "all"

st.divider()

selected_preset = st.selectbox(
    "Select a preset query or enter your own below:",
    options=["Custom Query"] + list(PRESET_QUERIES.keys()),
    key="preset_selector",
    help="Choose a preset research question or write your own"
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
    help="Ask any research question about AI in education"
)

col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    if st.button("Start Research", type="primary", use_container_width=True):
        if not query.strip():
            st.error("⚠️ Please enter a research question")
        else:
            with st.spinner(f"🔬 Conducting research with {selected_model}... This may take 3-7 minutes..."):
                try:
                    results = st.session_state.pipeline.conduct_research(
                        query=query,
                        model_provider=model_provider,
                        search_depth=search_depth,
                        focus_area=focus_area
                    )
                    st.session_state.research_results = results
                    st.session_state.current_session_id = results['session']['session_id']
                    st.session_state.just_completed = True
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

st.divider()

# Results
if st.session_state.research_results:
    results = st.session_state.research_results

    if st.session_state.just_completed:
        st.session_state.just_completed = False

    st.subheader("Research Summary")
    st.markdown(results['research_summary'])

    if 'structured_papers' in results and results['structured_papers']:
        st.divider()
        with st.expander("Paper Extraction", expanded=False):
            for i, paper in enumerate(results['structured_papers'], 1):
                finding_items = []
                if paper.get('finding_direction'):
                    finding_items.append(f"  - **Direction:** {paper['finding_direction']}")
                if paper.get('finding_summary'):
                    finding_items.append(f"  - **Summary:** {paper['finding_summary']}")
                if paper.get('measure'):
                    finding_items.append(f"  - **Measure:** {paper['measure']}")
                if paper.get('study_size'):
                    finding_items.append(f"  - **Study Size:** {paper['study_size']}")
                if paper.get('effect_size'):
                    finding_items.append(f"  - **Effect Size:** {paper['effect_size']}")

                finding_section = "\n".join(finding_items) if finding_items else "  - No finding details available"

                st.markdown(f"""
**{i}. {paper['title']}**
- **Objective:** {paper['objective'] or 'Not specified'}
- **Outcome:** {paper['outcome'] or 'Not specified'}
- **Empirical Finding:**
{finding_section}
- [View Source]({paper['url']})
                """)
