"""
D3.js force-directed knowledge graph visualization.

Archived from research_assistant_agent/app.py during Session 2 refactor.
Was used to render Paper/Outcome/Population nodes as an interactive graph.
Not currently used in the app — kept for reference.
"""
import json


def create_d3_visualization(graph_data):
    """Create D3.js force-directed graph visualization using actual extracted data.

    Args:
        graph_data: Dictionary with 'nodes' and 'edges' keys containing actual data

    Returns:
        HTML string with embedded D3.js visualization (pass to st.components.v1.html)
    """
    # Convert graph_data to D3 format with actual extracted values
    nodes = []
    for node in graph_data['nodes']:
        if node['label'] == 'Paper':
            name = node['properties'].get('title', 'Untitled Paper')
        elif node['label'] == 'EmpiricalFinding':
            name = node['properties'].get('direction') or 'Empirical Finding'
        else:
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

            const container = svg.append("g");

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
                const visibleNodes = graphData.nodes.filter(d => nodeVisibility[d.type]);
                const visibleNodeIds = new Set(visibleNodes.map(d => d.id));
                const visibleLinks = graphData.links.filter(l =>
                    visibleNodeIds.has(l.source.id || l.source) &&
                    visibleNodeIds.has(l.target.id || l.target)
                );

                link = linkGroup.selectAll("line")
                    .data(visibleLinks, d => `${{d.source.id || d.source}}-${{d.target.id || d.target}}`);
                link.exit().remove();
                link = link.enter().append("line")
                    .attr("stroke", "#cbd5e1")
                    .attr("stroke-width", 3)
                    .attr("stroke-opacity", 0.6)
                    .merge(link);

                node = nodeGroup.selectAll("g").data(visibleNodes, d => d.id);
                node.exit().remove();

                const nodeEnter = node.enter().append("g")
                    .call(d3.drag()
                        .on("start", dragstarted)
                        .on("drag", dragged)
                        .on("end", dragended));

                nodeEnter.append("circle");
                nodeEnter.append("text");
                node = nodeEnter.merge(node);

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

                simulation.nodes(visibleNodes);
                simulation.force("link").links(visibleLinks);
                simulation.alpha(0.3).restart();
            }}

            updateVisualization();

            function setupTooltips() {{
                const tooltip = d3.select("#tooltip");
                nodeGroup.selectAll("g").on("mouseover", function(event, d) {{
                    d3.select(this).select("circle").transition().duration(200).attr("stroke-width", 5);
                    let tooltipContent = `<strong>${{d.name}}</strong><br/>Type: ${{d.type}}`;
                    if (d.type === "EmpiricalFinding" && d.properties) {{
                        tooltipContent = `<strong>${{d.name}}</strong><br/>Type: Empirical Finding<br/>`;
                        if (d.properties.summary) tooltipContent += `Summary: ${{d.properties.summary}}<br/>`;
                        if (d.properties.measure) tooltipContent += `Measure: ${{d.properties.measure}}<br/>`;
                        if (d.properties.study_size) tooltipContent += `Study Size: ${{d.properties.study_size}}<br/>`;
                        if (d.properties.effect_size) tooltipContent += `Effect Size: ${{d.properties.effect_size}}`;
                    }}
                    tooltip.transition().duration(200).style("opacity", 1);
                    tooltip.html(tooltipContent)
                        .style("left", (event.pageX + 10) + "px")
                        .style("top", (event.pageY - 10) + "px");
                }})
                .on("mouseout", function() {{
                    d3.select(this).select("circle").transition().duration(200).attr("stroke-width", 3);
                    d3.select("#tooltip").transition().duration(200).style("opacity", 0);
                }});
            }}

            setupTooltips();

            simulation.on("tick", () => {{
                link
                    .attr("x1", d => d.source.x).attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
                node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
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

            d3.selectAll(".legend-eye").on("click", function() {{
                const nodeType = this.getAttribute("data-type");
                const isVisible = this.getAttribute("data-visible") === "true";
                nodeVisibility[nodeType] = !isVisible;
                this.setAttribute("data-visible", !isVisible);
                this.textContent = !isVisible ? "👁️" : "🙈";
                updateVisualization();
                setupTooltips();
            }});

            d3.selectAll(".size-input").on("input", function() {{
                const nodeType = this.getAttribute("data-type");
                nodeSizes[nodeType] = parseInt(this.value);
                updateVisualization();
                setupTooltips();
            }});

            d3.select("#zoom-in").on("click", () => {{ svg.transition().duration(300).call(zoom.scaleBy, 1.3); }});
            d3.select("#zoom-out").on("click", () => {{ svg.transition().duration(300).call(zoom.scaleBy, 0.7); }});
            d3.select("#zoom-reset").on("click", () => {{
                svg.transition().duration(300).call(zoom.transform, d3.zoomIdentity.translate(0, 0).scale(1));
            }});

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
