"""ResearchPipeline — async orchestrator for the full research workflow."""
import os
import re
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage

from src.pipeline.prompts import OUTLINE_PROMPT, CLARIFY_PROMPT
from src.pipeline.langgraph_client import call_open_deep_research
from src.session_manager import SessionManager
from src.kg_extractor import KGExtractor, StructuredPaper
from src.audit_writer import write_session_audit


def _build_graph_data(structured_papers: List[StructuredPaper]) -> Dict[str, Any]:
    nodes, edges = [], []
    node_id_map: Dict[str, str] = {}

    def get_or_create(label: str, value: str):
        if not value:
            return None
        key = f"{label}:{value}"
        if key not in node_id_map:
            nid = f"{label.lower()}_{len(node_id_map)}"
            node_id_map[key] = nid
            nodes.append({"id": nid, "label": label, "properties": {"id": value, "name": value}})
        return node_id_map[key]

    for idx, p in enumerate(structured_papers):
        pid = f"paper_{idx}"
        nodes.append({"id": pid, "label": "Paper", "properties": {
            "title": p.title, "url": p.url, "year": p.year, "venue": p.venue,
        }})
        for label, val in [
            ("Population", p.population), ("UserType", p.user_type),
            ("StudyDesign", p.study_design),
            ("ImplementationObjective", p.implementation_objective), ("Outcome", p.outcome),
        ]:
            nid = get_or_create(label, val)
            if nid:
                edges.append({"source": pid, "target": nid, "type": f"HAS_{label.upper()}"})

        if p.empirical_finding:
            direction = p.empirical_finding.get("direction", "")
            if direction:
                fid = f"finding_{idx}"
                nodes.append({"id": fid, "label": "EmpiricalFinding", "properties": {
                    "id": direction, "direction": direction,
                    "summary": p.empirical_finding.get("results_summary", ""),
                    "measure": p.empirical_finding.get("measure", ""),
                    "study_size": p.empirical_finding.get("study_size", ""),
                    "effect_size": p.empirical_finding.get("effect_size", ""),
                }})
                edges.append({"source": pid, "target": fid, "type": "REPORTS_FINDING"})
                if p.outcome:
                    oid = get_or_create("Outcome", p.outcome)
                    if oid:
                        edges.append({"source": oid, "target": fid, "type": "HAS_FINDING"})

        if p.implementation_objective and p.outcome:
            oid2 = get_or_create("ImplementationObjective", p.implementation_objective)
            oid3 = get_or_create("Outcome", p.outcome)
            if oid2 and oid3:
                edges.append({"source": oid2, "target": oid3, "type": "LEADS_TO"})

    return {"nodes": nodes, "edges": edges}


class ResearchPipeline:
    """Async orchestrator: research → extract → persist → return results."""

    def __init__(self):
        self.session_manager = SessionManager()
        self.kg_extractor = KGExtractor()
        self.langgraph_url = os.getenv("LANGGRAPH_API_URL", "http://127.0.0.1:2024")

    # ── Fast LLM helpers ──────────────────────────────────────────────────────

    async def get_clarification(self, query: str, model_provider: str) -> Dict[str, Any]:
        model = init_chat_model(model=model_provider, max_tokens=512)
        today = datetime.now().strftime("%B %d, %Y")
        response = await model.ainvoke([HumanMessage(content=CLARIFY_PROMPT.format(query=query, date=today))])
        content = response.content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(l for l in lines if not l.strip().startswith("```")).strip()
        result = json.loads(content)
        return {k: result.get(k, "") for k in ("who", "what", "where", "when")}

    async def get_report_structure(self, query: str, context: str, model_provider: str) -> str:
        model = init_chat_model(model=model_provider, max_tokens=512)
        response = await model.ainvoke([HumanMessage(content=OUTLINE_PROMPT.format(
            query=query, context=context or "No additional context provided.",
        ))])
        return response.content.strip()

    # ── Main research flow ────────────────────────────────────────────────────

    async def conduct_research(
        self,
        query: str,
        model_provider: str = "openai:gpt-4.1",
        search_depth: str = "standard",
        focus_area: str = "all",
        clarification_answer: Optional[str] = None,
        skip_clarification: bool = False,
        _prefetched_summary: Optional[str] = None,
        _prefetched_sources: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        session = self.session_manager.create_session(
            query=query, model_provider=model_provider,
            search_depth=search_depth, focus_area=focus_area,
        )
        try:
            if _prefetched_summary is not None:
                research_summary = _prefetched_summary
                sources = _prefetched_sources or []
            else:
                research_results = await call_open_deep_research(
                    query=query, model_provider=model_provider,
                    search_depth=search_depth, langgraph_url=self.langgraph_url,
                    clarification_answer=clarification_answer,
                    skip_clarification=skip_clarification,
                )
                research_summary = research_results["summary"]
                sources = research_results["sources"]

            return await self._finalize(session, research_summary, sources)
        except Exception:
            raise

    async def finalize_streamed_research(
        self,
        session,
        research_summary: str,
        sources: List[Dict],
        audit_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Post-processing after streaming completes (extract, persist, return)."""
        return await self._finalize(session, research_summary, sources, audit_data=audit_data)

    async def _finalize(
        self,
        session,
        research_summary: str,
        sources: List[Dict],
        audit_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        # Always save the report text first so sidebar reloads work even if paper extraction fails.
        if research_summary:
            self.session_manager.update_session_report(session_id=session.session_id, research_report=research_summary)

        papers = self.kg_extractor.extract_papers_from_sources(sources)
        if not papers:
            return self._empty_result(session, research_summary)

        structured_papers = self.kg_extractor.extract_structured_info(papers)
        if not structured_papers:
            return self._empty_result(session, research_summary)

        added_count = self.kg_extractor.add_to_neo4j(papers=structured_papers, session_id=session.session_id)
        self.session_manager.update_session_paper_count(session_id=session.session_id, count=added_count)

        graph_data = _build_graph_data(structured_papers)
        self.session_manager.update_session_graph_data(session_id=session.session_id, graph_data=graph_data)

        structured_papers_dicts = [
            {
                "title": p.title,
                "url": p.url,
                "year": p.year,
                "venue": p.venue,
                "population": p.population,
                "user_type": p.user_type,
                "study_design": p.study_design,
                "objective": p.implementation_objective,
                "outcome": p.outcome,
                "finding_direction": (p.empirical_finding or {}).get("direction", ""),
                "finding_summary": (p.empirical_finding or {}).get("results_summary", ""),
                "measure": (p.empirical_finding or {}).get("measure", ""),
                "study_size": (p.empirical_finding or {}).get("study_size"),
                "effect_size": (p.empirical_finding or {}).get("effect_size"),
                "confidence_interval": (p.empirical_finding or {}).get("confidence_interval", ""),
                "std_deviation": (p.empirical_finding or {}).get("std_deviation", ""),
            }
            for p in structured_papers
        ]

        # Write session audit JSON
        try:
            query = getattr(session, "query", "") or (session.to_dict() or {}).get("query", "")
            write_session_audit(
                session_id=session.session_id,
                query=query,
                research_summary=research_summary,
                sources=sources,
                structured_papers=structured_papers_dicts,
                audit_data=audit_data,
            )
        except Exception:
            pass  # Audit write failure must never block the main result

        _ad = audit_data or {}
        return {
            "session": session.to_dict(),
            "research_summary": research_summary,
            "papers_added": added_count,
            "structured_papers": structured_papers_dicts,
            "graph_data": graph_data,
            # Quality assessment fields from LangGraph nodes
            "qa_assessment": _ad.get("qa_assessment"),
            "extraction_table": _ad.get("extraction_table"),
            "swanson_hypotheses": _ad.get("swanson_hypotheses"),
            "causality_diagram": _ad.get("causality_diagram"),
            "sub_researcher_notes": _ad.get("notes", []),
        }

    def _empty_result(self, session, research_summary: str) -> Dict[str, Any]:
        return {
            "session": session.to_dict(),
            "research_summary": research_summary,
            "papers_added": 0,
            "graph_data": {"nodes": [], "edges": []},
        }

    def create_session(self, query, model_provider, search_depth, focus_area):
        return self.session_manager.create_session(
            query=query, model_provider=model_provider,
            search_depth=search_depth, focus_area=focus_area,
        )
