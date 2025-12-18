"""Streamlit UI for AI Education Research Assistant."""
import streamlit as st
from datetime import datetime
import streamlit.components.v1 as components
import math
import plotly.graph_objects as go
from dotenv import load_dotenv
from src.research_pipeline import SyncResearchPipeline
load_dotenv()

# Load Streamlit secrets to environment variables for Streamlit Cloud compatibility
from src.env_config import load_env_config
load_env_config()

from src.session_manager import SessionManager
from src.neo4j_config import initialize_database


def create_d3_visualization(graph_data):
    """Create D3.js force-directed graph visualization using actual extracted data.

    Args:
        graph_data: Dictionary with 'nodes' and 'edges' keys containing actual data

    Returns:
        HTML component with embedded D3.js visualization
    """
    import json

    # Convert graph_data to D3 format with actual extracted values
    nodes = []
    for node in graph_data['nodes']:
        # Get the display name based on node type
        if node['label'] == 'Paper':
            name = node['properties'].get('title', 'Untitled Paper')
        elif node['label'] == 'EmpiricalFinding':
            # For empirical findings, use direction as the name
            name = node['properties'].get('direction') or 'Empirical Finding'
        else:
            # For taxonomy nodes, use the 'id' property which contains the actual value
            name = node['properties'].get('id') or node['properties'].get('name') or 'Unknown'

        nodes.append({
            "id": node['id'],
            "name": name,
            "type": node['label'],
            "properties": node['properties']
        })

    links = []
    for edge in graph_data['edges']:
        links.append({
            "source": edge['source'],
            "target": edge['target'],
            "relation": edge['type']
        })

    graph_json = json.dumps({"nodes": nodes, "links": links})

    # Node colors by type
    node_colors = {
        "Paper": "#3b82f6",
        "Population": "#10b981",
        "UserType": "#f59e0b",
        "StudyDesign": "#8b5cf6",
        "ImplementationObjective": "#ef4444",
        "Outcome": "#ec4899",
        "EmpiricalFinding": "#06b6d4"
    }

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <style>
            body {{
                margin: 0;
                padding: 0;
                background: #ffffff;
                overflow: hidden;
            }}
            #graph-container {{
                width: 100%;
                height: 700px;
                background: #ffffff;
            }}
            .tooltip {{
                position: absolute;
                background: rgba(255, 255, 255, 0.95);
                border: 2px solid #334155;
                border-radius: 6px;
                padding: 10px;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.2s;
                color: #1e293b;
                font-size: 0.9rem;
                max-width: 300px;
                z-index: 1000;
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            }}
            .legend {{
                position: absolute;
                top: 20px;
                right: 20px;
                background: rgba(255, 255, 255, 0.95);
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                padding: 15px;
                font-family: system-ui, -apple-system, sans-serif;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                max-height: 600px;
                overflow-y: auto;
                min-width: 220px;
                transition: all 0.3s ease;
            }}
            .legend.collapsed {{
                min-width: auto;
                padding: 10px;
            }}
            .legend-header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 10px;
            }}
            .legend-title {{
                font-weight: 600;
                font-size: 14px;
                color: #1e293b;
            }}
            .legend-toggle {{
                cursor: pointer;
                font-size: 16px;
                padding: 4px;
                user-select: none;
                transition: transform 0.3s ease;
            }}
            .legend-toggle:hover {{
                transform: scale(1.1);
            }}
            .legend-content {{
                overflow: hidden;
                transition: max-height 0.3s ease, opacity 0.3s ease;
                max-height: 600px;
                opacity: 1;
            }}
            .legend-content.collapsed {{
                max-height: 0;
                opacity: 0;
            }}
            .legend-item {{
                display: flex;
                flex-direction: column;
                align-items: flex-start;
                margin-bottom: 18px;
                font-size: 12px;
                color: #475569;
                padding: 0;
            }}
            .legend-item-header {{
                display: flex;
                align-items: center;
                width: 100%;
                margin-bottom: 6px;
            }}
            .legend-color {{
                width: 16px;
                height: 16px;
                border-radius: 50%;
                margin-right: 8px;
                border: 2px solid #ffffff;
                box-shadow: 0 1px 3px rgba(0,0,0,0.2);
                flex-shrink: 0;
            }}
            .legend-eye {{
                margin-left: auto;
                cursor: pointer;
                font-size: 16px;
                user-select: none;
                flex-shrink: 0;
            }}
            .legend-size-control {{
                display: flex;
                align-items: center;
                width: 100%;
                gap: 8px;
                font-size: 11px;
                margin-top: 2px;
            }}
            .legend-size-control label {{
                flex-shrink: 0;
            }}
            .legend-size-control input {{
                width: 60px;
                padding: 3px 6px;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                font-size: 11px;
            }}
            .zoom-controls {{
                position: absolute;
                bottom: 20px;
                right: 20px;
                display: flex;
                gap: 5px;
                background: rgba(255, 255, 255, 0.95);
                border: 2px solid #e5e7eb;
                border-radius: 6px;
                padding: 6px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            .zoom-btn {{
                background: #f3f4f6;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: 500;
                color: #374151;
                cursor: pointer;
                transition: all 0.2s;
            }}
            .zoom-btn:hover {{
                background: #e5e7eb;
                border-color: #9ca3af;
            }}
            .zoom-btn:active {{
                transform: scale(0.95);
            }}
        </style>
    </head>
    <body>
        <div id="graph-container"></div>
        <div class="tooltip" id="tooltip"></div>
        <div class="zoom-controls">
            <button class="zoom-btn" id="zoom-in">+</button>
            <button class="zoom-btn" id="zoom-out">-</button>
            <button class="zoom-btn" id="zoom-reset">Reset</button>
        </div>
        <div class="legend" id="legend">
            <div class="legend-header">
                <div class="legend-title">Node Types</div>
                <span class="legend-toggle" id="legend-toggle">▼</span>
            </div>
            <div class="legend-content" id="legend-content">
            <div class="legend-item" data-type="Paper">
                <div class="legend-item-header">
                    <div class="legend-color" style="background-color: #3b82f6;"></div>
                    <span>Paper</span>
                    <span class="legend-eye" data-type="Paper" data-visible="true">👁️</span>
                </div>
                <div class="legend-size-control">
                    <label>Size:</label>
                    <input type="number" class="size-input" data-type="Paper" value="20" min="5" max="50">
                </div>
            </div>
            <div class="legend-item" data-type="Population">
                <div class="legend-item-header">
                    <div class="legend-color" style="background-color: #10b981;"></div>
                    <span>Population</span>
                    <span class="legend-eye" data-type="Population" data-visible="true">👁️</span>
                </div>
                <div class="legend-size-control">
                    <label>Size:</label>
                    <input type="number" class="size-input" data-type="Population" value="16" min="5" max="50">
                </div>
            </div>
            <div class="legend-item" data-type="UserType">
                <div class="legend-item-header">
                    <div class="legend-color" style="background-color: #f59e0b;"></div>
                    <span>User Type</span>
                    <span class="legend-eye" data-type="UserType" data-visible="true">👁️</span>
                </div>
                <div class="legend-size-control">
                    <label>Size:</label>
                    <input type="number" class="size-input" data-type="UserType" value="16" min="5" max="50">
                </div>
            </div>
            <div class="legend-item" data-type="StudyDesign">
                <div class="legend-item-header">
                    <div class="legend-color" style="background-color: #8b5cf6;"></div>
                    <span>Study Design</span>
                    <span class="legend-eye" data-type="StudyDesign" data-visible="true">👁️</span>
                </div>
                <div class="legend-size-control">
                    <label>Size:</label>
                    <input type="number" class="size-input" data-type="StudyDesign" value="16" min="5" max="50">
                </div>
            </div>
            <div class="legend-item" data-type="ImplementationObjective">
                <div class="legend-item-header">
                    <div class="legend-color" style="background-color: #ef4444;"></div>
                    <span>Implementation Objective</span>
                    <span class="legend-eye" data-type="ImplementationObjective" data-visible="true">👁️</span>
                </div>
                <div class="legend-size-control">
                    <label>Size:</label>
                    <input type="number" class="size-input" data-type="ImplementationObjective" value="16" min="5" max="50">
                </div>
            </div>
            <div class="legend-item" data-type="Outcome">
                <div class="legend-item-header">
                    <div class="legend-color" style="background-color: #ec4899;"></div>
                    <span>Outcome</span>
                    <span class="legend-eye" data-type="Outcome" data-visible="true">👁️</span>
                </div>
                <div class="legend-size-control">
                    <label>Size:</label>
                    <input type="number" class="size-input" data-type="Outcome" value="16" min="5" max="50">
                </div>
            </div>
            <div class="legend-item" data-type="EmpiricalFinding">
                <div class="legend-item-header">
                    <div class="legend-color" style="background-color: #06b6d4;"></div>
                    <span>Empirical Finding</span>
                    <span class="legend-eye" data-type="EmpiricalFinding" data-visible="true">👁️</span>
                </div>
                <div class="legend-size-control">
                    <label>Size:</label>
                    <input type="number" class="size-input" data-type="EmpiricalFinding" value="16" min="5" max="50">
                </div>
            </div>
            </div>
        </div>
        <script>
            const graphData = {graph_json};
            const width = window.innerWidth;
            const height = 700;
            const nodeColors = {json.dumps(node_colors)};

            // Track node visibility and sizes
            const nodeVisibility = {{
                "Paper": true,
                "Population": true,
                "UserType": true,
                "StudyDesign": true,
                "ImplementationObjective": true,
                "Outcome": true,
                "EmpiricalFinding": true
            }};

            const nodeSizes = {{
                "Paper": 20,
                "Population": 16,
                "UserType": 16,
                "StudyDesign": 16,
                "ImplementationObjective": 16,
                "Outcome": 16,
                "EmpiricalFinding": 16
            }};

            const svg = d3.select("#graph-container")
                .append("svg")
                .attr("width", width)
                .attr("height", height);

            // Create container for zoom
            const container = svg.append("g");

            // Add zoom behavior
            const zoom = d3.zoom()
                .scaleExtent([0.1, 4])
                .on("zoom", (event) => {{
                    container.attr("transform", event.transform);
                }});

            svg.call(zoom);

            const simulation = d3.forceSimulation(graphData.nodes)
                .force("link", d3.forceLink(graphData.links).id(d => d.id).distance(120))
                .force("charge", d3.forceManyBody().strength(-600))
                .force("center", d3.forceCenter(width / 2, height / 2))
                .force("collision", d3.forceCollide().radius(40));

            const linkGroup = container.append("g");
            const nodeGroup = container.append("g");

            let link, node;

            function updateVisualization() {{
                // Filter nodes based on visibility
                const visibleNodes = graphData.nodes.filter(d => nodeVisibility[d.type]);
                const visibleNodeIds = new Set(visibleNodes.map(d => d.id));

                // Filter links to only show those connecting visible nodes
                const visibleLinks = graphData.links.filter(l =>
                    visibleNodeIds.has(l.source.id || l.source) &&
                    visibleNodeIds.has(l.target.id || l.target)
                );

                // Update links
                link = linkGroup.selectAll("line")
                    .data(visibleLinks, d => `${{d.source.id || d.source}}-${{d.target.id || d.target}}`);

                link.exit().remove();

                link = link.enter().append("line")
                    .attr("stroke", "#cbd5e1")
                    .attr("stroke-width", 3)
                    .attr("stroke-opacity", 0.6)
                    .merge(link);

                // Update nodes
                node = nodeGroup.selectAll("g")
                    .data(visibleNodes, d => d.id);

                node.exit().remove();

                const nodeEnter = node.enter().append("g")
                    .call(d3.drag()
                        .on("start", dragstarted)
                        .on("drag", dragged)
                        .on("end", dragended));

                nodeEnter.append("circle");
                nodeEnter.append("text");

                node = nodeEnter.merge(node);

                // Update circle sizes and styles
                node.select("circle")
                    .attr("r", d => nodeSizes[d.type])
                    .attr("fill", d => nodeColors[d.type] || "#64748b")
                    .attr("stroke", "#ffffff")
                    .attr("stroke-width", 3);

                node.select("text")
                    .text(d => d.name.length > 50 ? d.name.substring(0, 50) + "..." : d.name)
                    .attr("dx", d => nodeSizes[d.type] + 5)
                    .attr("dy", 5)
                    .attr("fill", "#1e293b")
                    .attr("font-size", "12px")
                    .attr("font-weight", "500");

                // Update simulation
                simulation.nodes(visibleNodes);
                simulation.force("link").links(visibleLinks);
                simulation.alpha(0.3).restart();
            }}

            // Initial visualization
            updateVisualization();

            // Setup tooltips on node (need to be reapplied after update)
            function setupTooltips() {{
                const tooltip = d3.select("#tooltip");

                nodeGroup.selectAll("g").on("mouseover", function(event, d) {{
                    d3.select(this).select("circle")
                        .transition()
                        .duration(200)
                        .attr("stroke-width", 5);

                    // Build tooltip content based on node type
                    let tooltipContent = `<strong>${{d.name}}</strong><br/>Type: ${{d.type}}`;

                    if (d.type === "EmpiricalFinding" && d.properties) {{
                        tooltipContent = `<strong>${{d.name}}</strong><br/>Type: Empirical Finding<br/>`;
                        if (d.properties.summary) tooltipContent += `Summary: ${{d.properties.summary}}<br/>`;
                        if (d.properties.measure) tooltipContent += `Measure: ${{d.properties.measure}}<br/>`;
                        if (d.properties.study_size) tooltipContent += `Study Size: ${{d.properties.study_size}}<br/>`;
                        if (d.properties.effect_size) tooltipContent += `Effect Size: ${{d.properties.effect_size}}`;
                    }}

                    tooltip.transition()
                        .duration(200)
                        .style("opacity", 1);
                    tooltip.html(tooltipContent)
                        .style("left", (event.pageX + 10) + "px")
                        .style("top", (event.pageY - 10) + "px");
                }})
                .on("mouseout", function() {{
                    d3.select(this).select("circle")
                        .transition()
                        .duration(200)
                        .attr("stroke-width", 3);

                    d3.select("#tooltip").transition()
                        .duration(200)
                        .style("opacity", 0);
                }});
            }}

            setupTooltips();

            simulation.on("tick", () => {{
                link
                    .attr("x1", d => d.source.x)
                    .attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x)
                    .attr("y2", d => d.target.y);

                node
                    .attr("transform", d => `translate(${{d.x}},${{d.y}})`);
            }});

            function dragstarted(event) {{
                if (!event.active) simulation.alphaTarget(0.3).restart();
                event.subject.fx = event.subject.x;
                event.subject.fy = event.subject.y;
            }}

            function dragged(event) {{
                event.subject.fx = event.x;
                event.subject.fy = event.y;
            }}

            function dragended(event) {{
                if (!event.active) simulation.alphaTarget(0);
                event.subject.fx = null;
                event.subject.fy = null;
            }}

            // Event listeners for visibility eye icons
            d3.selectAll(".legend-eye").on("click", function() {{
                const nodeType = this.getAttribute("data-type");
                const isVisible = this.getAttribute("data-visible") === "true";

                // Toggle visibility
                nodeVisibility[nodeType] = !isVisible;
                this.setAttribute("data-visible", !isVisible);

                // Update icon
                this.textContent = !isVisible ? "👁️" : "🙈";

                updateVisualization();
                setupTooltips();
            }});

            // Event listeners for size inputs
            d3.selectAll(".size-input").on("input", function() {{
                const nodeType = this.getAttribute("data-type");
                nodeSizes[nodeType] = parseInt(this.value);
                updateVisualization();
                setupTooltips();
            }});

            // Zoom controls
            d3.select("#zoom-in").on("click", () => {{
                svg.transition().duration(300).call(zoom.scaleBy, 1.3);
            }});

            d3.select("#zoom-out").on("click", () => {{
                svg.transition().duration(300).call(zoom.scaleBy, 0.7);
            }});

            d3.select("#zoom-reset").on("click", () => {{
                svg.transition().duration(300).call(
                    zoom.transform,
                    d3.zoomIdentity.translate(0, 0).scale(1)
                );
            }});

            // Legend collapse/expand toggle
            const legendToggle = document.getElementById("legend-toggle");
            const legendContent = document.getElementById("legend-content");
            const legend = document.getElementById("legend");
            let isCollapsed = false;

            legendToggle.addEventListener("click", () => {{
                isCollapsed = !isCollapsed;

                if (isCollapsed) {{
                    legendContent.classList.add("collapsed");
                    legend.classList.add("collapsed");
                    legendToggle.textContent = "▶";
                }} else {{
                    legendContent.classList.remove("collapsed");
                    legend.classList.remove("collapsed");
                    legendToggle.textContent = "▼";
                }}
            }});
        </script>
    </body>
    </html>
    """

    return html_content


# Page configuration
st.set_page_config(
    page_title="AI in Education Research Agent",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'current_session_id' not in st.session_state:
    st.session_state.current_session_id = None
if 'research_results' not in st.session_state:
    st.session_state.research_results = None
if 'pipeline' not in st.session_state:
    st.session_state.pipeline = SyncResearchPipeline()
if 'session_manager' not in st.session_state:
    st.session_state.session_manager = SessionManager()

# Preset queries (from your HTML frontend)
PRESET_QUERIES = {
    "ITS Effectiveness": "What is the effectiveness of Intelligent Tutoring Systems (ITS) on student learning outcomes like mathematics, reading comprehension, and writing ability?",
    "Adaptive Feedback": "What does research show about the effectiveness of immediate feedback versus delayed feedback in tutoring? How does adaptive feedback timing impact student learning gains, retention, and problem-solving ability?",
    "Scaffolding Techniques": "How effective are scaffolding techniques in tutoring? Research on step-by-step problem solving, graduated guidance, hint systems, and fading support. What are the optimal levels of scaffolding for different student populations?",
    "Metacognitive Strategies": "What is the evidence for teaching metacognitive strategies in tutoring? How do self-explanation prompts, reflection activities, and thinking-about-thinking approaches impact learning outcomes, self-efficacy, and transfer?",
    "One-on-One Tutoring": "How does one-on-one human tutoring compare to computer-based tutoring systems? What are the unique benefits of each approach? ",
    "Peer Tutoring": "What does the research say about peer tutoring effectiveness? How does student-to-student tutoring impact both the tutor and tutee? Include outcomes on learning gains, engagement, and social-emotional benefits.",
}

# Sidebar
with st.sidebar:
    # Custom CSS for minimal text-only buttons and proper scrolling
    st.markdown("""
    <style>
    /* Enable scrollbar in sidebar with proper overflow */
    [data-testid="stSidebar"] {
        overflow-y: auto !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        overflow-y: auto !important;
        max-height: 100vh !important;
        padding-top: 0.5rem !important;
    }

    /* Reduce space at top of sidebar content */
    [data-testid="stSidebar"] .block-container {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* Remove extra spacing from sidebar elements */
    [data-testid="stSidebar"] .element-container {
        margin-top: 0 !important;
    }

    /* Reduce margin on the heading */
    [data-testid="stSidebar"] h2 {
        margin-top: 0 !important;
        margin-bottom: 1rem !important;
    }

    /* Make session buttons minimal - no background */
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

    /* Hover effect - subtle background */
    [data-testid="stSidebar"] button[kind="secondary"]:hover {
        background-color: rgba(240, 242, 246, 0.5) !important;
        opacity: 1;
    }

    /* Remove background from delete button */
    [data-testid="stSidebar"] button[kind="secondary"]:has([data-testid]) {
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Session History header
    st.markdown("<h2 style='text-align: center; margin-top: 0; font-size: 1.5rem;'>Research Sessions</h2>", unsafe_allow_html=True)

    sessions = st.session_state.session_manager.list_sessions(limit=20)

    if sessions:
        for session in sessions:
            created_date = datetime.fromisoformat(session.created_at).strftime('%m/%d %I:%M %p')

            # Truncate query to 80 characters for display
            display_query = session.query if len(session.query) <= 80 else session.query[:80] + "..."

            # Check if this is the active session
            is_active = st.session_state.current_session_id == session.session_id

            # Bold the text if it's the active session
            if is_active:
                button_text = f"**{display_query}**  \n{created_date} • {session.paper_count} papers"
            else:
                button_text = f"{display_query}  \n{created_date} • {session.paper_count} papers"

            # Create columns with better spacing to prevent overlap
            col1, col2 = st.columns([8.5, 1.5])

            with col1:
                if st.button(
                    button_text,
                    key=f"load_{session.session_id}",
                    use_container_width=True,
                    type="secondary"
                ):
                    st.session_state.current_session_id = session.session_id

                    # Load full session data
                    full_session = st.session_state.session_manager.get_session(session.session_id)

                    # Load session graph and papers
                    graph_data = st.session_state.session_manager.get_session_graph(session.session_id)
                    papers = st.session_state.session_manager.get_session_papers(session.session_id)

                    # Use the stored research report or create a fallback summary
                    research_summary = full_session.research_report if full_session and full_session.research_report else f"## Session: {session.query}\n\nLoaded {session.paper_count} papers from this research session."

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
                if st.button("✕", key=f"delete_{session.session_id}", help="Delete", use_container_width=True):
                    st.session_state.session_manager.delete_session(session.session_id)
                    if st.session_state.current_session_id == session.session_id:
                        st.session_state.current_session_id = None
                        st.session_state.research_results = None
                    st.rerun()
    else:
        st.caption("No sessions yet. Start your first research!")

# Tabs at the top
tab1, tab2 = st.tabs(["AI in Education Research Agent", "Research Evidence Map"])

# Add JavaScript to handle tab persistence
components.html("""
<script>
(function() {
    function setupTabPersistence() {
        const tabs = window.parent.document.querySelectorAll('button[role="tab"]');

        // Add click listeners to all tabs to save selection
        tabs.forEach((tab, index) => {
            tab.addEventListener('click', function() {
                // Store the tab index in localStorage
                localStorage.setItem('activeTab', index);
            });
        });

        // Restore previously selected tab on page load
        const savedTab = localStorage.getItem('activeTab');
        if (savedTab && tabs[savedTab]) {
            tabs[savedTab].click();
        }
    }

    setTimeout(setupTabPersistence, 300);
})();
</script>
""", height=0)

# Tab 1: Research Agent
with tab1:
    # Show sidebar on Research Agent tab using JavaScript
    components.html("""
    <script>
    (function() {
        function ensureSidebarVisible() {
            const activeTab = window.parent.document.querySelector('button[role="tab"][aria-selected="true"]');
            const sidebar = window.parent.document.querySelector('[data-testid="stSidebar"]');

            if (activeTab && sidebar) {
                // Show sidebar if Research Agent tab is active
                if (activeTab.textContent.includes('AI in Education Research Agent')) {
                    sidebar.style.display = 'block';
                }
            }
        }

        // Wait for page to be fully loaded before checking
        setTimeout(ensureSidebarVisible, 200);
    })();
    </script>
    """, height=0)

    st.caption("Powered by Open Deep Research & Neo4j | Quality, Impact, and Body of Evidence Maturity scores calculated using the K-12 Rubric for Evaluating Evidence")
    st.info("ℹ️ This is an MVP of the deep research agent, synthesizing literature across credible and publication sources. If your query has no results, try reframing your question(s).")

    st.divider()

    # Control dropdowns - smaller size
    # Model fixed to ChatGPT 4.1
    model_provider = "gpt-4.1"

    col1, col2 = st.columns([2, 3])

    with col1:
        st.selectbox(
            "Model",
            options=["ChatGPT 4.1"],
            index=0,
            disabled=True
        )

    with col2:
        search_depth = st.selectbox(
            "Search Depth",
            options=[
                "standard (~3-5 min)",
                "deep (~5-7 min)",
                "comprehensive (~7-10 min)"
            ],
            index=0
        )
        # Extract just the depth value
        search_depth = search_depth.split()[0]

    # Remove focus_area - not needed
    focus_area = "all"

    st.divider()

    # Preset queries dropdown
    selected_preset = st.selectbox(
        "Select a preset query or enter your own below:",
        options=["Custom Query"] + list(PRESET_QUERIES.keys()),
        key="preset_selector"
    )

    if selected_preset != "Custom Query":
        st.session_state.query_text = PRESET_QUERIES[selected_preset]
    else:
        # Clear the text when switching back to Custom Query
        st.session_state.query_text = ""

    # Query input
    if 'query_text' not in st.session_state:
        st.session_state.query_text = ""

    query = st.text_area(
        "Enter your research question:",
        value=st.session_state.query_text,
        height=100,
        placeholder="e.g., What is the effectiveness of intelligent tutoring systems on student learning outcomes in mathematics?"
    )

    # Start Research button
    if st.button("Start Research", type="primary", use_container_width=True):
        if not query.strip():
            st.error("Please enter a research question")
        else:
            with st.spinner("Conducting research... This may take 3-7 minutes..."):
                try:
                    # Run research pipeline
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
                    st.error(f"Error: {str(e)}")

    st.divider()

    # Display results
    if st.session_state.research_results:
        results = st.session_state.research_results

        # Show success message if research just completed
        if st.session_state.get('just_completed', False):
            st.session_state.just_completed = False

        # Research Summary
        st.subheader("Research Summary")
        st.markdown(results['research_summary'])

        # Knowledge Graph Visualization
        st.divider()
        with st.expander("Knowledge Graph Visualization", expanded=True):
            # Use current session graph data
            graph_data = results['graph_data']

            if not graph_data['nodes']:
                st.info("No graph data available yet. Run a research query to populate the knowledge graph.")
            else:
                # Create D3.js force-directed graph with actual extracted data
                d3_html = create_d3_visualization(graph_data)
                components.html(d3_html, height=700, scrolling=False)

            # Show graph info
            st.caption(f"📊 {len(graph_data['nodes'])} nodes, {len(graph_data['edges'])} edges")

        # Paper Extraction (moved below visualization)
        if 'structured_papers' in results and results['structured_papers']:
            st.divider()
            with st.expander("Paper Extraction", expanded=False):
                for i, paper in enumerate(results['structured_papers'], 1):
                    # Build finding details as indented bullet points
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

# Tab 2: Evidence Map
with tab2:
    from src.evidence_map import create_full_matrix

    # Hide sidebar on Evidence Map tab using JavaScript - only if this tab is active
    components.html("""
    <script>
    (function() {
        function toggleSidebarForTab() {
            const activeTab = window.parent.document.querySelector('button[role="tab"][aria-selected="true"]');
            const sidebar = window.parent.document.querySelector('[data-testid="stSidebar"]');

            if (activeTab && sidebar) {
                // Only hide if Evidence Map tab is actually active
                if (activeTab.textContent.includes('Research Evidence Map')) {
                    sidebar.style.display = 'none';
                } else {
                    sidebar.style.display = 'block';
                }
            }
        }

        // Wait for page to be fully loaded before checking
        setTimeout(toggleSidebarForTab, 200);

        // Listen for tab changes
        const observer = new MutationObserver(toggleSidebarForTab);
        const tabsContainer = window.parent.document.querySelector('[role="tablist"]');
        if (tabsContainer) {
            observer.observe(tabsContainer, { attributes: true, subtree: true });
        }
    })();
    </script>
    """, height=0)

    # Get data
    df = create_full_matrix()

    if df.empty or df['count'].sum() == 0:
        st.warning("No research papers in database yet. Conduct some research first!")
    else:
        # Implementation Objective names (uppercase)
        io_short_names = {
            "Intelligent Tutoring and Instruction": "INTELLIGENT TUTORING AND INSTRUCTION",
            "AI-Enable Personalized Advising": "AI-ENABLED PERSONALIZED ADVISING",
            "Institutional Decision-making": "INSTITUTIONAL DECISION-MAKING",
            "AI-Enabled Learner Mobility": "AI-ENABLED LEARNER MOBILITY"
        }

        # Clean outcome names (remove prefixes, uppercase)
        def clean_outcome(outcome):
            cleaned = outcome.replace('Cognitive - ', '').replace('Behavioral - ', '').replace('Affective - ', '')
            return cleaned.upper()

        df['outcome_clean'] = df['outcome'].apply(clean_outcome)
        df['io_short'] = df['implementation_objective'].map(io_short_names)

        # Get unique Implementation Objectives (columns)
        ios = list(io_short_names.values())

        # Get unique Outcomes (rows) in the correct order with categories
        outcomes_with_categories = [
            ("Cognitive", "CRITICAL THINKING/METACOGNITIVE SKILLS"),
            ("Cognitive", "READING AND WRITING LITERACY"),
            ("Cognitive", "SPEAKING, LISTENING, AND LANGUAGE FLUENCY"),
            ("Cognitive", "MATHEMATICAL NUMERACY"),
            ("Cognitive", "SCIENTIFIC REASONING"),
            ("Behavioral", "TASK AND ASSIGNMENT EFFICIENCY"),
            ("Behavioral", "STUDY HABITS, CONCENTRATION"),
            ("Behavioral", "PARTICIPATION AND SOCIAL ENGAGEMENT"),
            ("Behavioral", "PRODUCTIVITY"),
            ("Affective", "MOTIVATION"),
            ("Affective", "ENGAGEMENT"),
            ("Affective", "PERSISTENCE")
        ]

        # Create a lookup dictionary for counts
        count_dict = {}
        for _, row in df.iterrows():
            key = (row['io_short'], row['outcome_clean'])
            count_dict[key] = int(row['count'])

        # Import OUTCOMES for mapping
        from src.neo4j_config import OUTCOMES

        # Create Plotly bubble chart instead of HTML table
        # Prepare data for Plotly
        plot_data = []

        # Map outcomes to y-axis positions
        outcome_to_y = {outcome: idx for idx, (_, outcome) in enumerate(outcomes_with_categories)}
        io_to_x = {io: idx for idx, io in enumerate(ios)}

        for (io_display, outcome), count in count_dict.items():
            if count > 0:
                # Get database values
                io_db = list(io_short_names.keys())[list(io_short_names.values()).index(io_display)]
                outcome_db = None
                for orig in OUTCOMES:
                    if orig.replace('Cognitive - ', '').replace('Behavioral - ', '').replace('Affective - ', '').upper() == outcome:
                        outcome_db = orig
                        break

                plot_data.append({
                    'x': io_to_x[io_display],
                    'y': outcome_to_y[outcome],
                    'size': count,
                    'io_display': io_display,
                    'outcome_display': outcome,
                    'io_db': io_db,
                    'outcome_db': outcome_db,
                    'count': count
                })

        # Create Plotly figure
        fig = go.Figure()

        # Add scatter plot with bubbles
        fig.add_trace(go.Scatter(
            x=[d['x'] for d in plot_data],
            y=[d['y'] for d in plot_data],
            mode='markers',
            marker=dict(
                size=[math.sqrt(d['size']) * 12 for d in plot_data],  # Larger bubbles to fit numbers
                color='#dc2626',
                line=dict(color='#b91c1c', width=1)
            ),
            customdata=[[d['io_db'], d['outcome_db'], d['count']] for d in plot_data],
            hovertemplate='<b>%{customdata[0]}</b><br>%{customdata[1]}<br>%{customdata[2]} papers<extra></extra>',
            showlegend=False
        ))

        # Add header row background (red bar at top) - matches grid width exactly
        fig.add_shape(
            type="rect",
            x0=-0.5,
            y0=-1.05,
            x1=len(ios) - 0.5,
            y1=-0.55,
            line=dict(color='#b91c1c', width=1),
            fillcolor='#dc2626',
            layer='below'
        )

        # Add column header labels as annotations
        for idx, io in enumerate(ios):
            fig.add_annotation(
                x=idx,
                y=-0.8,
                text=f"<b>{io}</b>",
                showarrow=False,
                font=dict(size=10, color='white', family='Arial, sans-serif'),
                xanchor='center',
                yanchor='middle'
            )

        # Add grid cells and outcome labels
        for y_idx, (category, outcome) in enumerate(outcomes_with_categories):
            # Add cells for this row
            for x_idx in range(len(ios)):
                fig.add_shape(
                    type="rect",
                    x0=x_idx - 0.5,
                    y0=y_idx - 0.5,
                    x1=x_idx + 0.5,
                    y1=y_idx + 0.5,
                    line=dict(color='#d1d5db', width=0.8),
                    fillcolor='#ffffff',
                    layer='below'
                )

            # Add outcome label for this row
            fig.add_annotation(
                x=-0.65,
                y=y_idx,
                text=f"<b>{outcome}</b>",
                showarrow=False,
                font=dict(size=12, color='#374151', family='Arial, sans-serif'),
                xanchor='right',
                yanchor='middle',
                xref='x',
                yref='y'
            )


        # Add category labels on the left
        for idx, (category, outcome) in enumerate(outcomes_with_categories):
            if idx == 0 or outcomes_with_categories[idx][0] != outcomes_with_categories[idx-1][0]:
                # Find the span of this category
                cat_start = idx
                cat_end = idx
                for j in range(idx + 1, len(outcomes_with_categories)):
                    if outcomes_with_categories[j][0] == category:
                        cat_end = j
                    else:
                        break

                # Add category header rectangle
                fig.add_shape(
                    type="rect",
                    x0=-0.95,
                    y0=cat_start - 0.45,
                    x1=-0.88,
                    y1=cat_end + 0.45,
                    line=dict(color='#9ca3af', width=1),
                    fillcolor='#f3f4f6',
                    layer='below'
                )

                # Add category label
                fig.add_annotation(
                    x=-0.915,
                    y=(cat_start + cat_end) / 2,
                    text=f"<b>{category.upper()}</b>",
                    showarrow=False,
                    textangle=-90,
                    font=dict(size=11, color='#1f2937', family='Arial, sans-serif'),
                    xanchor='center',
                    yanchor='middle'
                )

        # Update layout with cleaner styling
        fig.update_layout(
            xaxis=dict(
                showticklabels=False,  # Hide default tick labels since we're using annotations
                showgrid=False,
                zeroline=False,
                range=[-0.7, len(ios) - 0.5],
                fixedrange=True
            ),
            yaxis=dict(
                showticklabels=False,  # Hide default tick labels since we're using annotations
                showgrid=False,
                zeroline=False,
                autorange='reversed',
                range=[-1.15, len(outcomes_with_categories) - 0.4],
                fixedrange=True
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=1600,
            margin=dict(l=350, r=0, t=50, b=20),
            hovermode='closest',
            showlegend=False,
            dragmode=False
        )

        # Show total stats at top - centered with larger text and spacing
        total_papers = df['count'].sum()
        cells_with_papers = (df['count'] > 0).sum()
        total_cells = len(df)

        # Add custom CSS for larger metrics
        st.markdown("""
            <style>
            [data-testid="stMetricValue"] {
                font-size: 48px !important;
                font-weight: bold;
            }
            [data-testid="stMetricLabel"] {
                font-size: 20px !important;
            }
            </style>
        """, unsafe_allow_html=True)

        # Center the metrics with more spacing between them - shifted right
        col_left, col1, spacer1, col2, spacer2, col3, col_right = st.columns([3, 1, 1, 1, 1, 1, 1])
        with col1:
            st.metric("Total Papers", int(total_papers))
        with col2:
            st.metric("Cells with Evidence", f"{cells_with_papers}/{total_cells}")
        with col3:
            coverage = (cells_with_papers / total_cells * 100) if total_cells > 0 else 0
            st.metric("Coverage", f"{coverage:.1f}%")

        # Display with click events - disable all interactions except clicking
        clicked_point = st.plotly_chart(
            fig,
            use_container_width=True,
            key="evidence_map_chart",
            on_select="rerun",
            config={
                'displayModeBar': False,  # Hide the toolbar
                'doubleClick': False,  # Disable double click
                'scrollZoom': False,  # Disable scroll zoom
                'displaylogo': False,  # Hide Plotly logo
                'modeBarButtonsToRemove': ['zoom', 'pan', 'select', 'lasso2d', 'zoomIn', 'zoomOut', 'autoScale', 'resetScale'],
            }
        )

        # Handle click event - always process clicks to ensure proper state
        if clicked_point and clicked_point.get('selection') and clicked_point['selection'].get('points'):
            points = clicked_point['selection']['points']
            if points:
                # Get the first clicked point
                point = points[0]
                customdata = point.get('customdata')
                if customdata and len(customdata) >= 2:
                    new_io = customdata[0]
                    new_outcome = customdata[1]
                    new_cell = f"{new_io}_{new_outcome}"

                    # Check if this is a different cell or modal was closed
                    current_modal_key = st.session_state.get('modal_key', '')
                    modal_open = st.session_state.get('show_modal', False)

                    # Process click only if modal is closed OR clicking a different cell
                    if not modal_open or current_modal_key != new_cell:
                        # Always clear ALL modal-related data first
                        for key in list(st.session_state.keys()):
                            if key.startswith('modal_') or key == 'selected_paper_idx':
                                st.session_state.pop(key, None)

                        # Set new selection
                        st.session_state.selected_io = new_io
                        st.session_state.selected_outcome = new_outcome
                        st.session_state.show_modal = True
                        st.session_state.modal_key = new_cell

                        st.rerun()

        # Pre-fetch data if modal should be shown but data not loaded
        if st.session_state.get('show_modal') and st.session_state.get('selected_io') and st.session_state.get('selected_outcome'):
            from src.evidence_map import get_paper_details_for_cell, synthesize_papers_for_cell

            io = st.session_state.selected_io
            outcome = st.session_state.selected_outcome

            # Fetch papers if not already loaded
            if 'modal_papers' not in st.session_state:
                st.session_state.modal_papers = get_paper_details_for_cell(io, outcome)
                st.rerun()

            @st.dialog(f"Paper Analysis - {io} × {outcome}", width="large")
            def show_cell_modal():
                # Check if we're showing the correct modal for current selection
                current_key = f"{io}_{outcome}"
                if st.session_state.get('modal_key') != current_key:
                    # Wrong modal is open, close it
                    st.session_state.show_modal = False
                    st.rerun()
                    return

                papers = st.session_state.modal_papers

                if not papers:
                    st.warning("No papers found for this combination.")
                    return

                # Initialize selected paper - default to first paper instead of overview
                if 'selected_paper_idx' not in st.session_state:
                    st.session_state.selected_paper_idx = 0

                # Check if synthesis is loaded
                synthesis = st.session_state.get('modal_synthesis', None)

                # Create two columns: Papers (left) and Content (right)
                col_papers, col_content = st.columns([1, 3])

                with col_papers:
                    st.markdown(f"**{len(papers)} papers**")
                    st.markdown("")

                    # CSS for email-like rows and scrollable container
                    st.markdown("""
                        <style>
                        .paper-row {
                            padding: 12px;
                            margin: 8px 0;
                            border: 1px solid #e0e0e0;
                            border-radius: 4px;
                            cursor: pointer;
                            background-color: white;
                        }
                        .paper-row:hover {
                            background-color: #f5f5f5;
                        }
                        .paper-row-selected {
                            padding: 12px;
                            margin: 8px 0;
                            border: 2px solid #dc2626;
                            border-radius: 4px;
                            cursor: pointer;
                            background-color: #fef2f2;
                        }
                        .paper-title {
                            font-size: 14px;
                            font-weight: 600;
                            color: #1f2937;
                            overflow: hidden;
                            text-overflow: ellipsis;
                            display: -webkit-box;
                            -webkit-line-clamp: 2;
                            -webkit-box-orient: vertical;
                        }
                        .paper-tags {
                            margin-top: 8px;
                            display: flex;
                            flex-wrap: wrap;
                            gap: 4px;
                        }
                        .tag-pill {
                            display: inline-block;
                            padding: 2px 8px;
                            font-size: 11px;
                            border-radius: 12px;
                            background-color: #e5e7eb;
                            color: #374151;
                        }
                        </style>
                    """, unsafe_allow_html=True)

                    # Overview row
                    if st.button("Overview", key="overview_row", use_container_width=True,
                                type="primary" if st.session_state.selected_paper_idx is None else "secondary"):
                        st.session_state.selected_paper_idx = None
                        st.rerun()

                    st.markdown("---")

                    # Scrollable container for papers
                    with st.container(height=600):
                        # Paper rows (email-like) - numbered starting from 1
                        for idx, paper in enumerate(papers):
                            paper_num = idx + 1
                            paper_title = paper.get('title', 'Untitled')

                            # Create clickable row using button with paper number
                            if st.button(f"Paper {paper_num}: {paper_title[:50]}{'...' if len(paper_title) > 50 else ''}",
                                        key=f"paper_row_{idx}",
                                        use_container_width=True,
                                        type="primary" if st.session_state.selected_paper_idx == idx else "secondary"):
                                st.session_state.selected_paper_idx = idx
                                st.rerun()

                with col_content:
                    # Show overview or selected paper
                    if st.session_state.selected_paper_idx is None:
                        # Show overview
                        st.markdown("#### Overview")

                        if synthesis is None:
                            # Show placeholder and generate button
                            st.info("Click the button below to generate an AI synthesis of these papers.")
                            if st.button("Generate Overview", key="gen_overview", type="primary"):
                                with st.spinner("Generating overview..."):
                                    synthesis = synthesize_papers_for_cell(io, outcome, papers)
                                    st.session_state.modal_synthesis = synthesis
                                    st.rerun()
                        else:
                            st.caption("Note: Paper numbers (e.g., Paper 1, Paper 2) refer to papers listed in the left panel")
                            st.markdown("")
                            st.markdown(synthesis['overview'])

                            st.markdown("#### Evidence Gaps")
                            st.markdown(synthesis['gaps'])
                    else:
                        # Show selected paper details
                        paper = papers[st.session_state.selected_paper_idx]
                        paper_num = st.session_state.selected_paper_idx + 1

                        # Title with paper number and year
                        title = paper.get('title', 'Untitled')
                        year = paper.get('year', '')
                        if year:
                            st.markdown(f"## Paper {paper_num}: {title} ({year})")
                        else:
                            st.markdown(f"## Paper {paper_num}: {title}")

                        # Authors (not available in current schema)
                        st.caption("Authors: N/A")

                        # Venue
                        venue = paper.get('venue', 'N/A')
                        st.caption(f"{venue}")

                        # Read paper link
                        if paper.get('url'):
                            st.markdown(f"[Read Paper]({paper['url']})")

                        st.markdown("---")

                        # Metadata fields
                        st.write(f"**User Type:** {paper.get('user_type', 'N/A')}")
                        st.write(f"**Population:** {paper.get('population', 'N/A')}")
                        st.write(f"**Study Design:** {paper.get('study_design', 'N/A')}")

                        st.markdown("")

                        # Empirical Finding
                        st.markdown("### Empirical Finding")
                        if paper.get('results_summary'):
                            st.write(paper['results_summary'])
                        else:
                            st.write("No summary available")

                        st.markdown("")

                        # Other metrics in single column
                        if paper.get('finding_direction'):
                            st.write(f"**Direction:** {paper['finding_direction']}")
                        if paper.get('measure'):
                            st.write(f"**Measure:** {paper['measure']}")
                        if paper.get('study_size'):
                            st.write(f"**Study Size:** {paper['study_size']}")
                        if paper.get('effect_size'):
                            st.write(f"**Effect Size:** {paper['effect_size']}")

            show_cell_modal()

# Initialize database on first run
if 'db_initialized' not in st.session_state:
    with st.spinner("Initializing database..."):
        initialize_database()
        st.session_state.db_initialized = True
