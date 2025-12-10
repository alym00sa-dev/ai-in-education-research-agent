"""Streamlit UI for AI Education Research Assistant."""
import streamlit as st
from datetime import datetime
import streamlit.components.v1 as components
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
    "ITS Effectiveness": "What is the effectiveness of Intelligent Tutoring Systems (ITS) on student learning outcomes? Include meta-analyses, effect sizes, and comparisons with traditional tutoring methods. Focus on concepts like adaptive difficulty, immediate feedback, and scaffolding.",
    "Adaptive Feedback": "What does research show about the effectiveness of immediate feedback versus delayed feedback in tutoring? How does adaptive feedback timing impact student learning gains, retention, and problem-solving ability?",
    "Math Tutoring": "What are the most effective tutoring methods and concepts for mathematics instruction? Include research on cognitive tutors, worked examples, step-by-step problem solving, and error correction strategies in math tutoring.",
    "Scaffolding Techniques": "How effective are scaffolding techniques in tutoring? Research on step-by-step problem solving, graduated guidance, hint systems, and fading support. What are the optimal levels of scaffolding for different student populations?",
    "Metacognitive Strategies": "What is the evidence for teaching metacognitive strategies in tutoring? How do self-explanation prompts, reflection activities, and thinking-about-thinking approaches impact learning outcomes, self-efficacy, and transfer?",
    "One-on-One Tutoring": "How does one-on-one human tutoring compare to computer-based tutoring systems? What are the unique benefits of each approach? Include effect sizes and research on hybrid human-AI tutoring models.",
    "Peer Tutoring": "What does the research say about peer tutoring effectiveness? How does student-to-student tutoring impact both the tutor and tutee? Include outcomes on learning gains, engagement, and social-emotional benefits.",
    "Cognitive Tutor": "What is the effectiveness of Cognitive Tutor systems based on cognitive models of problem-solving? Include research on their impact on learning gains, problem-solving ability, and knowledge transfer. Compare with other ITS approaches."
}

# Sidebar
with st.sidebar:
    # Custom CSS for minimal text-only buttons
    st.markdown("""
    <style>
    /* Make sidebar static */
    [data-testid="stSidebar"] > div:first-child {
        overflow-y: hidden;
    }

    /* Style primary button (New Research Chat) - softer white/light grey background, black text */
    [data-testid="stSidebar"] button[kind="primary"] {
        background-color: #d0d0d0 !important;
        color: #000000 !important;
        border: none !important;
    }

    [data-testid="stSidebar"] button[kind="primary"]:hover {
        background-color: #c0c0c0 !important;
        color: #000000 !important;
    }

    /* Make session buttons minimal - no background (only secondary buttons, not primary) */
    [data-testid="stSidebar"] button[kind="secondary"] {
        height: auto;
        min-height: 60px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        text-align: left;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 8px 12px;
    }

    /* Hover effect - subtle opacity change */
    [data-testid="stSidebar"] button[kind="secondary"]:hover {
        background-color: transparent !important;
        opacity: 0.7;
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

    # New Research Button at top with background
    if st.button("New Research Chat +", use_container_width=True, type="primary"):
        st.session_state.current_session_id = None
        st.session_state.research_results = None
        st.rerun()

    # Session History
    st.markdown("<h3 style='text-align: center;'>Research Sessions</h3>", unsafe_allow_html=True)

    sessions = st.session_state.session_manager.list_sessions(limit=10)

    if sessions:
        for session in sessions:
            created_date = datetime.fromisoformat(session.created_at).strftime('%m/%d %I:%M %p')

            # Create columns with better spacing to prevent overlap
            col1, col2 = st.columns([8.5, 1.5])

            with col1:
                if st.button(
                    f"{session.query}  \n{created_date} • {session.paper_count} papers",
                    key=f"load_{session.session_id}",
                    use_container_width=True
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

# Main content
st.title("📚 AI in Education Research Agent")
st.caption("Powered by Open Deep Research & Neo4j Knowledge Graph")


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

# Initialize database on first run
if 'db_initialized' not in st.session_state:
    with st.spinner("Initializing database..."):
        initialize_database()
        st.session_state.db_initialized = True
