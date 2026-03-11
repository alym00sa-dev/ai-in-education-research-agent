"""Entry point for the EDU Deep Research Agent Streamlit app.

To add a future page, create a file in pages/ and add it to st.navigation:

    st.navigation([
        st.Page("pages/research_agent.py", title="EDU Research Agent", icon="📚"),
        st.Page("pages/admin.py", title="Admin", icon="⚙️"),  # <- new page
    ])
"""
import streamlit as st
from dotenv import load_dotenv
from src.research_pipeline import SyncResearchPipeline

load_dotenv()

from src.env_config import load_env_config
load_env_config()

from src.session_manager import SessionManager
from src.neo4j_config import initialize_database

# Page configuration
st.set_page_config(
    page_title="EDU Deep Research Agent",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize all session state here so it's shared across all pages
if 'current_session_id' not in st.session_state:
    st.session_state.current_session_id = None
if 'research_results' not in st.session_state:
    st.session_state.research_results = None
if 'pipeline' not in st.session_state:
    st.session_state.pipeline = SyncResearchPipeline()
if 'session_manager' not in st.session_state:
    st.session_state.session_manager = SessionManager()
if 'sessions_expanded' not in st.session_state:
    st.session_state.sessions_expanded = True
if 'query_text' not in st.session_state:
    st.session_state.query_text = ""
if 'just_completed' not in st.session_state:
    st.session_state.just_completed = False
if 'selected_mode' not in st.session_state:
    st.session_state.selected_mode = "Default"
if 'clarification_screen' not in st.session_state:
    st.session_state.clarification_screen = None  # None | "loading" | "showing"
if 'clarification_who' not in st.session_state:
    st.session_state.clarification_who = ""
if 'clarification_what' not in st.session_state:
    st.session_state.clarification_what = ""
if 'clarification_where' not in st.session_state:
    st.session_state.clarification_where = ""
if 'clarification_when' not in st.session_state:
    st.session_state.clarification_when = ""
if 'pending_query' not in st.session_state:
    st.session_state.pending_query = ""
if 'pending_model' not in st.session_state:
    st.session_state.pending_model = "openai:gpt-4.1"
if 'pending_search_depth' not in st.session_state:
    st.session_state.pending_search_depth = "standard"
if 'pending_clarification_context' not in st.session_state:
    st.session_state.pending_clarification_context = ""
if 'construction_screen' not in st.session_state:
    st.session_state.construction_screen = None  # None | "loading" | "showing"
if 'report_outline' not in st.session_state:
    st.session_state.report_outline = ""
if 'selected_columns' not in st.session_state:
    st.session_state.selected_columns = None
if 'db_initialized' not in st.session_state:
    st.session_state.db_initialized = None  # None = not yet attempted

# Initialize database once on first load
if st.session_state.db_initialized is None:
    try:
        initialize_database()
        st.session_state.db_initialized = True
    except Exception:
        st.session_state.db_initialized = False

# Navigation
page = st.navigation([
    st.Page("pages/research_agent.py", title="EDU Research Agent", icon="📚"),
    st.Page("pages/placeholder.py", title="Extra Page - Ignore", icon="🚧"),
])
page.run()
