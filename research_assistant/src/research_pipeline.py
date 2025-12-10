"""Research pipeline integrating Open Deep Research with Knowledge Graph extraction."""
import os
import json
import httpx
from typing import Dict, Any, List
from dotenv import load_dotenv

from src.session_manager import SessionManager, ResearchSession
from src.kg_extractor import KGExtractor, StructuredPaper

load_dotenv()


def build_graph_data_from_papers(structured_papers: List[StructuredPaper]) -> Dict[str, Any]:
    """Build graph visualization data directly from structured papers.

    Args:
        structured_papers: List of StructuredPaper objects

    Returns:
        Dictionary with 'nodes' and 'edges' lists
    """
    nodes = []
    edges = []
    node_id_map = {}  # Track unique nodes by their label+value

    def get_or_create_node(label: str, value: str, paper_idx: int) -> str:
        """Get existing node ID or create new node."""
        if not value or value == "":
            return None

        key = f"{label}:{value}"
        if key not in node_id_map:
            node_id = f"{label.lower()}_{len(node_id_map)}"
            node_id_map[key] = node_id
            nodes.append({
                "id": node_id,
                "label": label,
                "properties": {"id": value, "name": value}
            })
        return node_id_map[key]

    # Build nodes and edges from each paper
    for idx, paper in enumerate(structured_papers):
        # Create paper node
        paper_id = f"paper_{idx}"
        nodes.append({
            "id": paper_id,
            "label": "Paper",
            "properties": {
                "title": paper.title,
                "url": paper.url,
                "year": paper.year,
                "venue": paper.venue
            }
        })

        # Create edges to taxonomy nodes
        taxonomy_fields = [
            ("Population", paper.population),
            ("UserType", paper.user_type),
            ("StudyDesign", paper.study_design),
            ("ImplementationObjective", paper.implementation_objective),
            ("Outcome", paper.outcome)
        ]

        for label, value in taxonomy_fields:
            node_id = get_or_create_node(label, value, idx)
            if node_id:
                edges.append({
                    "source": paper_id,
                    "target": node_id,
                    "type": f"HAS_{label.upper()}"
                })

        # Create empirical finding node if present
        if paper.empirical_finding:
            finding_direction = paper.empirical_finding.get("direction", "")
            if finding_direction:
                finding_id = f"finding_{idx}"
                nodes.append({
                    "id": finding_id,
                    "label": "EmpiricalFinding",
                    "properties": {
                        "id": finding_direction,
                        "direction": finding_direction,
                        "summary": paper.empirical_finding.get("results_summary", ""),
                        "measure": paper.empirical_finding.get("measure", ""),
                        "study_size": paper.empirical_finding.get("study_size", ""),
                        "effect_size": paper.empirical_finding.get("effect_size", "")
                    }
                })
                # Paper -> Finding edge
                edges.append({
                    "source": paper_id,
                    "target": finding_id,
                    "type": "REPORTS_FINDING"
                })

                # Outcome -> Finding edge if outcome exists
                if paper.outcome:
                    out_id = get_or_create_node("Outcome", paper.outcome, idx)
                    if out_id:
                        edges.append({
                            "source": out_id,
                            "target": finding_id,
                            "type": "HAS_FINDING"
                        })

        # Create Objective -> Outcome edge if both exist
        if paper.implementation_objective and paper.outcome:
            obj_id = get_or_create_node("ImplementationObjective", paper.implementation_objective, idx)
            out_id = get_or_create_node("Outcome", paper.outcome, idx)
            if obj_id and out_id:
                edges.append({
                    "source": obj_id,
                    "target": out_id,
                    "type": "LEADS_TO"
                })

    return {
        "nodes": nodes,
        "edges": edges
    }


class ResearchPipeline:
    """Orchestrates the complete research workflow."""

    def __init__(self):
        """Initialize the research pipeline."""
        self.session_manager = SessionManager()
        self.kg_extractor = KGExtractor()
        self.langgraph_url = os.getenv("LANGGRAPH_API_URL", "http://127.0.0.1:2024")

    async def conduct_research(
        self,
        query: str,
        model_provider: str = "openai:gpt-4.1",
        search_depth: str = "standard",
        focus_area: str = "all"
    ) -> Dict[str, Any]:
        """Conduct full research workflow: research → extract → add to KG.

        Args:
            query: The research question
            model_provider: LLM model to use
            search_depth: standard, deep, or comprehensive
            focus_area: Research focus area

        Returns:
            Dictionary with research results and graph data
        """
        print(f"\n{'='*60}")
        print(f"🔬 STARTING RESEARCH: {query[:80]}...")
        print(f"{'='*60}\n")

        # Step 1: Create session
        print("📝 Step 1: Creating research session...")
        session = self.session_manager.create_session(
            query=query,
            model_provider=model_provider,
            search_depth=search_depth,
            focus_area=focus_area
        )

        try:
            # Step 2: Run Open Deep Research
            print("\n🔍 Step 2: Running Open Deep Research...")
            research_results = await self._call_open_deep_research(
                query=query,
                model_provider=model_provider,
                search_depth=search_depth
            )

            research_summary = research_results.get("summary", "No summary available")
            sources = research_results.get("sources", [])

            print(f"  ✅ Research complete! Found {len(sources)} sources")

            # Step 3: Extract papers from sources
            print(f"\n📚 Step 3: Extracting papers from {len(sources)} sources...")
            papers = self.kg_extractor.extract_papers_from_sources(sources)

            if not papers:
                print("  ⚠️  No papers extracted. Returning research summary only.")
                return {
                    "session": session.to_dict(),
                    "research_summary": research_summary,
                    "papers_added": 0,
                    "graph_data": {"nodes": [], "edges": []}
                }

            # Step 4: Extract structured info using LLM
            print(f"\n🧠 Step 4: Extracting structured information from {len(papers)} papers...")
            structured_papers = self.kg_extractor.extract_structured_info(papers)

            if not structured_papers:
                print("  ⚠️  No structured data extracted. Returning research summary only.")
                return {
                    "session": session.to_dict(),
                    "research_summary": research_summary,
                    "papers_added": 0,
                    "graph_data": {"nodes": [], "edges": []}
                }

            # Step 5: Add to Neo4j
            print(f"\n💾 Step 5: Adding {len(structured_papers)} papers to Neo4j...")
            added_count = self.kg_extractor.add_to_neo4j(
                papers=structured_papers,
                session_id=session.session_id
            )

            # Update session paper count
            self.session_manager.update_session_paper_count(
                session_id=session.session_id,
                count=added_count
            )

            # Save research report to session
            self.session_manager.update_session_report(
                session_id=session.session_id,
                research_report=research_summary
            )

            # Step 6: Build graph data from extracted papers
            print("\n📊 Step 6: Building knowledge graph visualization...")
            graph_data = build_graph_data_from_papers(structured_papers)

            # Save graph data to session
            self.session_manager.update_session_graph_data(
                session_id=session.session_id,
                graph_data=graph_data
            )

            print(f"\n{'='*60}")
            print(f"✅ RESEARCH COMPLETE!")
            print(f"  • Papers added: {added_count}")
            print(f"  • Graph nodes: {len(graph_data['nodes'])}")
            print(f"  • Graph edges: {len(graph_data['edges'])}")
            print(f"{'='*60}\n")

            return {
                "session": session.to_dict(),
                "research_summary": research_summary,
                "papers_added": added_count,
                "structured_papers": [
                    {
                        "title": p.title,
                        "url": p.url,
                        "objective": p.implementation_objective,
                        "outcome": p.outcome,
                        "finding_direction": (p.empirical_finding or {}).get("direction", ""),
                        "finding_summary": (p.empirical_finding or {}).get("results_summary", ""),
                        "measure": (p.empirical_finding or {}).get("measure", ""),
                        "study_size": (p.empirical_finding or {}).get("study_size"),
                        "effect_size": (p.empirical_finding or {}).get("effect_size")
                    }
                    for p in structured_papers
                ],
                "graph_data": graph_data
            }

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            raise

    async def _call_open_deep_research(
        self,
        query: str,
        model_provider: str,
        search_depth: str
    ) -> Dict[str, Any]:
        """Call the Open Deep Research LangGraph API.

        Args:
            query: The research question
            model_provider: LLM model to use
            search_depth: standard, deep, or comprehensive

        Returns:
            Dictionary with research summary and sources
        """
        # Map search depth to researcher iterations
        iterations_map = {
            "standard": 4,
            "deep": 6,
            "comprehensive": 8
        }

        async with httpx.AsyncClient(timeout=600.0) as client:
            # Create thread
            thread_response = await client.post(
                f"{self.langgraph_url}/threads",
                json={}
            )
            thread_response.raise_for_status()
            thread_id = thread_response.json()["thread_id"]

            # Run research
            payload = {
                "assistant_id": "Deep Researcher",
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": query
                        }
                    ]
                },
                "config": {
                    "configurable": {
                        "research_model": model_provider,
                        "max_researcher_iterations": iterations_map.get(search_depth, 6)
                    }
                },
                "stream_mode": "values"
            }

            response = await client.post(
                f"{self.langgraph_url}/threads/{thread_id}/runs/stream",
                json=payload
            )
            response.raise_for_status()

            # Parse streaming response
            final_state = None
            for line in response.text.strip().split('\n'):
                if line.startswith('data: '):
                    data_str = line[6:]  # Remove "data: " prefix

                    # Skip [DONE] signal
                    if data_str == "[DONE]":
                        continue

                    # Parse JSON
                    try:
                        data = json.loads(data_str)
                        if data:
                            final_state = data
                    except json.JSONDecodeError:
                        # Skip invalid JSON lines
                        continue

            if not final_state:
                raise Exception("No response from LangGraph server")

            # Extract final report and sources
            final_report = final_state.get('final_report', '')
            sources = self._extract_sources_from_report(final_report, final_state)

            return {
                "summary": final_report,
                "sources": sources
            }

    def _extract_sources_from_report(self, report: str, state: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract source URLs and titles from the research report.

        Args:
            report: The research report text
            state: The final state from LangGraph

        Returns:
            List of source dictionaries with 'url' and 'title'
        """
        sources = []

        # Try to extract from raw_notes in state (this contains search results)
        raw_notes = state.get('raw_notes', [])
        for note in raw_notes:
            if isinstance(note, str):
                # Look for URLs in notes
                import re
                urls = re.findall(r'https?://[^\s\)"\]>]+', note)
                for url in urls:
                    sources.append({
                        "url": url,
                        "title": url.split('/')[-1]  # Fallback title
                    })

        # Also extract URLs directly from report
        import re
        urls = re.findall(r'https?://[^\s\)"\]>]+', report)
        for url in urls:
            if not any(s['url'] == url for s in sources):
                sources.append({
                    "url": url,
                    "title": url.split('/')[-1]
                })

        # Deduplicate
        seen = set()
        unique_sources = []
        for source in sources:
            if source['url'] not in seen:
                seen.add(source['url'])
                unique_sources.append(source)

        return unique_sources[:18]  # Limit to 18 sources (matches typical report citations)


# Synchronous wrapper for use in Streamlit
class SyncResearchPipeline:
    """Synchronous wrapper for the research pipeline."""

    def __init__(self):
        """Initialize the sync research pipeline."""
        self.pipeline = ResearchPipeline()

    def conduct_research(
        self,
        query: str,
        model_provider: str = "openai:gpt-4.1",
        search_depth: str = "standard",
        focus_area: str = "all"
    ) -> Dict[str, Any]:
        """Synchronous version of conduct_research for Streamlit.

        Args:
            query: The research question
            model_provider: LLM model to use
            search_depth: standard, deep, or comprehensive
            focus_area: Research focus area

        Returns:
            Dictionary with research results and graph data
        """
        import asyncio

        # Run async function in event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(
            self.pipeline.conduct_research(
                query=query,
                model_provider=model_provider,
                search_depth=search_depth,
                focus_area=focus_area
            )
        )
