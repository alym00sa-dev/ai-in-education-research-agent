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
])
page.run()
