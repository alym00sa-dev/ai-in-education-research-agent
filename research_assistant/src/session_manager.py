"""Session management for research chats."""
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from src.neo4j_config import get_neo4j_connection


@dataclass
class ResearchSession:
    """Represents a research chat session."""
    session_id: str
    query: str
    created_at: str
    model_provider: str
    search_depth: str
    focus_area: str
    paper_count: int = 0
    follow_up_count: int = 0
    status: str = "active"  # active, completed, archived
    research_report: str = ""  # Store the original research report
    graph_data_json: str = ""  # Store graph visualization data as JSON string

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class SessionManager:
    """Manages research session lifecycle."""

    def __init__(self):
        """Initialize session manager with Neo4j connection."""
        self.conn = get_neo4j_connection()

    def create_session(
        self,
        query: str,
        model_provider: str = "openai:gpt-4.1",
        search_depth: str = "standard",
        focus_area: str = "all"
    ) -> ResearchSession:
        """Create a new research session.

        Args:
            query: The research question
            model_provider: LLM model to use
            search_depth: standard, deep, or comprehensive
            focus_area: Research focus area

        Returns:
            ResearchSession object
        """
        session_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()

        session = ResearchSession(
            session_id=session_id,
            query=query,
            created_at=created_at,
            model_provider=model_provider,
            search_depth=search_depth,
            focus_area=focus_area,
            paper_count=0,
            follow_up_count=0,
            status="active"
        )

        # Store session in Neo4j
        with self.conn.driver.session(database=self.conn.database) as db_session:
            db_session.run(
                """
                CREATE (s:Session {
                    session_id: $session_id,
                    query: $query,
                    created_at: $created_at,
                    model_provider: $model_provider,
                    search_depth: $search_depth,
                    focus_area: $focus_area,
                    paper_count: $paper_count,
                    follow_up_count: $follow_up_count,
                    status: $status,
                    research_report: $research_report,
                    graph_data_json: $graph_data_json
                })
                """,
                session.to_dict()
            )

        print(f"✅ Created session: {session_id[:8]}...")
        return session

    def get_session(self, session_id: str) -> Optional[ResearchSession]:
        """Retrieve a session by ID."""
        with self.conn.driver.session(database=self.conn.database) as db_session:
            result = db_session.run(
                """
                MATCH (s:Session {session_id: $session_id})
                RETURN s
                """,
                {"session_id": session_id}
            )
            record = result.single()

            if record:
                data = dict(record["s"])
                return ResearchSession(**data)
            return None

    def list_sessions(self, limit: int = 50) -> List[ResearchSession]:
        """List all sessions, most recent first."""
        with self.conn.driver.session(database=self.conn.database) as db_session:
            result = db_session.run(
                """
                MATCH (s:Session)
                RETURN s
                ORDER BY s.created_at DESC
                LIMIT $limit
                """,
                {"limit": limit}
            )

            sessions = []
            for record in result:
                data = dict(record["s"])
                sessions.append(ResearchSession(**data))

            return sessions

    def update_session_paper_count(self, session_id: str, count: int):
        """Update the paper count for a session."""
        with self.conn.driver.session(database=self.conn.database) as db_session:
            db_session.run(
                """
                MATCH (s:Session {session_id: $session_id})
                SET s.paper_count = $count
                """,
                {"session_id": session_id, "count": count}
            )

    def update_session_report(self, session_id: str, research_report: str):
        """Update the research report for a session."""
        with self.conn.driver.session(database=self.conn.database) as db_session:
            db_session.run(
                """
                MATCH (s:Session {session_id: $session_id})
                SET s.research_report = $research_report
                """,
                {"session_id": session_id, "research_report": research_report}
            )

    def update_session_graph_data(self, session_id: str, graph_data: Dict[str, Any]):
        """Update the graph visualization data for a session."""
        import json
        graph_data_json = json.dumps(graph_data)
        with self.conn.driver.session(database=self.conn.database) as db_session:
            db_session.run(
                """
                MATCH (s:Session {session_id: $session_id})
                SET s.graph_data_json = $graph_data_json
                """,
                {"session_id": session_id, "graph_data_json": graph_data_json}
            )

    def delete_session(self, session_id: str):
        """Delete a session from the database.

        Note: This only deletes the Session node. Papers remain in the graph
        for cumulative learning but are no longer tagged with this session_id.
        """
        with self.conn.driver.session(database=self.conn.database) as db_session:
            db_session.run(
                """
                MATCH (s:Session {session_id: $session_id})
                DELETE s
                """,
                {"session_id": session_id}
            )

    def get_session_papers(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all papers associated with a session with full details."""
        with self.conn.driver.session(database=self.conn.database) as db_session:
            result = db_session.run(
                """
                MATCH (p:Paper {session_id: $session_id})
                OPTIONAL MATCH (p)-[:HAS_IMPLEMENTATION_OBJECTIVE]->(io:ImplementationObjective)
                OPTIONAL MATCH (p)-[:FOCUSES_ON_OUTCOME]->(out:Outcome)
                OPTIONAL MATCH (p)-[:REPORTS_FINDING]->(f:EmpiricalFinding)
                RETURN p, io.id as objective, out.id as outcome,
                       f.direction as finding_direction,
                       f.results_summary as finding_summary,
                       f.measure as measure,
                       f.study_size as study_size,
                       f.effect_size as effect_size
                ORDER BY p.added_date DESC
                """,
                {"session_id": session_id}
            )

            papers = []
            for record in result:
                paper_dict = dict(record["p"])
                paper_dict["objective"] = record["objective"] or ""
                paper_dict["outcome"] = record["outcome"] or ""
                paper_dict["finding_direction"] = record["finding_direction"] or ""
                paper_dict["finding_summary"] = record["finding_summary"] or ""
                paper_dict["measure"] = record["measure"] or ""
                paper_dict["study_size"] = record["study_size"]
                paper_dict["effect_size"] = record["effect_size"]
                papers.append(paper_dict)

            return papers

    def get_session_graph(self, session_id: str) -> Dict[str, Any]:
        """Get the complete knowledge graph for a session from stored graph_data."""
        import json
        with self.conn.driver.session(database=self.conn.database) as db_session:
            # Retrieve the stored graph_data_json from the Session node
            result = db_session.run(
                """
                MATCH (s:Session {session_id: $session_id})
                RETURN s.graph_data_json as graph_data_json
                """,
                {"session_id": session_id}
            ).single()

            if not result or not result["graph_data_json"]:
                print(f"⚠️  No stored graph data for session {session_id[:8]}.")
                print(f"   This is an old session. Attempting to rebuild from papers...")
                # Fallback: rebuild graph from papers
                papers = self.get_session_papers(session_id)
                if not papers:
                    print(f"   No papers found. Returning empty graph.")
                    return {"nodes": [], "edges": []}

                # Import the builder function
                from src.research_pipeline import build_graph_data_from_papers
                from src.kg_extractor import StructuredPaper

                # Convert paper dicts to StructuredPaper objects
                structured_papers = []
                for p in papers:
                    # Create a minimal StructuredPaper from stored data
                    paper = StructuredPaper(
                        title=p.get("title", ""),
                        url=p.get("url", ""),
                        year=None,
                        venue=None,
                        text_content="",
                        population=None,
                        user_type=None,
                        study_design=None,
                        implementation_objective=p.get("objective"),
                        outcome=p.get("outcome"),
                        empirical_finding={
                            "direction": p.get("finding_direction"),
                            "results_summary": p.get("finding_summary"),
                            "measure": p.get("measure"),
                            "study_size": p.get("study_size"),
                            "effect_size": p.get("effect_size")
                        } if p.get("finding_direction") else None
                    )
                    structured_papers.append(paper)

                graph_data = build_graph_data_from_papers(structured_papers)
                print(f"   ✅ Rebuilt graph: {len(graph_data['nodes'])} nodes, {len(graph_data['edges'])} edges")

                # Save for next time
                self.update_session_graph_data(session_id, graph_data)

                return graph_data

            # Parse the stored JSON
            graph_data = json.loads(result["graph_data_json"])

            print(f"\n📊 Retrieved stored graph for session {session_id[:8]}:")
            print(f"   Nodes: {len(graph_data.get('nodes', []))} | Edges: {len(graph_data.get('edges', []))}")

            return graph_data
