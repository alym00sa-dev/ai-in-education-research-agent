"""Per-question exhaustive KG explorer using Claude tool use.

QuestionExplorer takes a list of research questions and for each one:
- Runs multiple Cypher queries via Claude tool use (outcomes, objectives, populations, empirical findings)
- Deduplicates papers across all queries for that question
- Synthesizes: coverage level, evidence gaps, replication candidates, direct summary

This is designed for the Strategic Canvas mode to generate per-question coverage cards.
"""
import json
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

import anthropic

from src.neo4j_config import IMPLEMENTATION_OBJECTIVES, OUTCOMES, POPULATIONS, STUDY_DESIGNS
from src.kg_agent.queries import (
    get_papers_by_taxonomy,
    query_by_empirical_findings,
)


@dataclass
class QuestionExploration:
    question: str
    papers: List[Dict[str, Any]] = field(default_factory=list)
    coverage_level: str = "limited"  # "strong" | "partial" | "limited"
    evidence_gaps: List[str] = field(default_factory=list)
    replication_candidates: List[Dict[str, Any]] = field(default_factory=list)
    synthesis: str = ""

    @property
    def paper_count(self) -> int:
        return len(self.papers)


def _infer_coverage(count: int) -> str:
    if count >= 10:
        return "strong"
    elif count >= 3:
        return "partial"
    return "limited"


_TOOLS = [
    {
        "name": "query_by_outcomes",
        "description": "Search for papers in the knowledge base targeting specific educational outcomes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "outcomes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Outcome terms to search. Must be chosen from the available taxonomy. "
                        "Call get_available_taxonomy first if unsure."
                    ),
                }
            },
            "required": ["outcomes"],
        },
    },
    {
        "name": "query_by_objectives",
        "description": "Search for papers by implementation objective — what kind of intervention or approach the paper is studying.",
        "input_schema": {
            "type": "object",
            "properties": {
                "objectives": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Implementation objective terms from the available taxonomy.",
                }
            },
            "required": ["objectives"],
        },
    },
    {
        "name": "query_by_population",
        "description": "Search for papers focused on a specific student population or grade level.",
        "input_schema": {
            "type": "object",
            "properties": {
                "populations": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Population terms from the available taxonomy.",
                }
            },
            "required": ["populations"],
        },
    },
    {
        "name": "query_by_empirical_findings",
        "description": (
            "Search for papers by study design and/or finding direction. "
            "Use this to find RCTs, causal studies, quasi-experimental work, or papers with specific finding directions. "
            "Critical for identifying replication candidates and evidence gaps."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "study_designs": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Study design types from the available taxonomy.",
                },
                "finding_directions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Finding direction values, e.g. ['positive', 'negative', 'mixed', 'null']",
                },
            },
        },
    },
    {
        "name": "get_available_taxonomy",
        "description": "Returns all available taxonomy terms so you know exactly what to search with.",
        "input_schema": {"type": "object", "properties": {}},
    },
]

_SYSTEM_PROMPT = """You are an exhaustive knowledge graph explorer for an education research database.

Given a research question, search the database thoroughly by trying multiple angles:
- Outcomes: what outcomes does the research measure
- Implementation objectives: what kind of intervention or approach
- Population: who the research focuses on
- Empirical findings: study design (especially RCTs and causal studies), finding directions

Be systematic. Try at least 3 different tool calls using different angles before synthesizing. If one query returns few results, try different terms or angles. Call get_available_taxonomy if you are unsure what terms exist.

After exhaustively searching, output ONLY this JSON (no markdown, no extra text):
{
  "coverage_level": "strong|partial|limited",
  "evidence_gaps": ["specific gap 1", "specific gap 2"],
  "replication_candidates": [
    {"title": "paper title here", "why": "one sentence — strong finding but narrow context, could be replicated in X"}
  ],
  "synthesis": "2-3 direct sentences: what exists, what study designs are represented, what is clearly missing"
}

coverage_level:
- "strong": 10+ papers with meaningful study designs
- "partial": 3-9 papers, or mostly indirect/weak designs
- "limited": fewer than 3 papers, or very indirect evidence

Be pointed. Do not hedge. If coverage is thin, say so directly."""


class QuestionExplorer:
    """Exhaustively explores the Neo4j KG for each research question using Claude tool use."""

    def __init__(self):
        self._client = anthropic.Anthropic()

    def _execute_tool(
        self, name: str, inputs: dict, accumulated: Dict[str, Dict]
    ) -> str:
        """Run a tool and add new papers to the deduplicated accumulator."""
        try:
            if name == "get_available_taxonomy":
                return json.dumps({
                    "objectives": IMPLEMENTATION_OBJECTIVES,
                    "outcomes": OUTCOMES,
                    "populations": POPULATIONS,
                    "study_designs": STUDY_DESIGNS,
                })

            papers: List[Dict] = []
            if name == "query_by_outcomes":
                papers = get_papers_by_taxonomy(
                    objectives=[], outcomes=inputs.get("outcomes", []), populations=[]
                )
            elif name == "query_by_objectives":
                papers = get_papers_by_taxonomy(
                    objectives=inputs.get("objectives", []), outcomes=[], populations=[]
                )
            elif name == "query_by_population":
                papers = get_papers_by_taxonomy(
                    objectives=[], outcomes=[], populations=inputs.get("populations", [])
                )
            elif name == "query_by_empirical_findings":
                papers = query_by_empirical_findings(
                    study_designs=inputs.get("study_designs") or None,
                    finding_directions=inputs.get("finding_directions") or None,
                )
            else:
                return json.dumps({"error": f"Unknown tool: {name}"})

            new_count = 0
            for p in papers:
                key = (p.get("title") or "").strip()
                if key and key not in accumulated:
                    accumulated[key] = p
                    new_count += 1

            return json.dumps({
                "papers_found": len(papers),
                "new_papers_added": new_count,
                "total_accumulated": len(accumulated),
                "sample_titles": [p.get("title", "") for p in papers[:5]],
            })
        except Exception as e:
            return json.dumps({"error": str(e)})

    def explore_question(self, question: str) -> QuestionExploration:
        """Run the agentic exploration loop for a single research question."""
        accumulated: Dict[str, Dict] = {}

        messages = [
            {
                "role": "user",
                "content": (
                    f"Research question to explore exhaustively:\n\n{question}\n\n"
                    "Search the knowledge base using multiple angles, then synthesize what you found."
                ),
            }
        ]

        max_rounds = 8
        for _ in range(max_rounds):
            response = self._client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                system=_SYSTEM_PROMPT,
                tools=_TOOLS,
                messages=messages,
            )

            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                final_text = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        final_text = block.text.strip()
                        break

                synthesis_data: Dict[str, Any] = {}
                try:
                    synthesis_data = json.loads(final_text)
                except (json.JSONDecodeError, ValueError):
                    # Model may have wrapped JSON in markdown or added preamble text —
                    # extract the outermost {...} object regardless of surrounding content.
                    match = re.search(r'\{.*\}', final_text, re.DOTALL)
                    if match:
                        try:
                            synthesis_data = json.loads(match.group())
                        except (json.JSONDecodeError, ValueError):
                            pass

                papers = list(accumulated.values())
                fallback_synthesis = (
                    f"Found {len(papers)} paper(s) across this question. "
                    + (final_text[:300] if final_text and not synthesis_data else "")
                ).strip()
                return QuestionExploration(
                    question=question,
                    papers=papers,
                    coverage_level=synthesis_data.get(
                        "coverage_level", _infer_coverage(len(papers))
                    ),
                    evidence_gaps=synthesis_data.get("evidence_gaps", []),
                    replication_candidates=synthesis_data.get("replication_candidates", []),
                    synthesis=synthesis_data.get("synthesis", "") or fallback_synthesis,
                )

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = self._execute_tool(block.name, block.input, accumulated)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        })
                messages.append({"role": "user", "content": tool_results})

        # Fallback if max rounds exceeded
        papers = list(accumulated.values())
        return QuestionExploration(
            question=question,
            papers=papers,
            coverage_level=_infer_coverage(len(papers)),
            synthesis=f"Found {len(papers)} papers after exhaustive search.",
        )

    def explore_questions(
        self, questions: List[str]
    ) -> Dict[str, QuestionExploration]:
        """Explore a list of research questions. Returns {question: QuestionExploration}."""
        results = {}
        for q in questions:
            try:
                results[q] = self.explore_question(q)
            except Exception as e:
                results[q] = QuestionExploration(
                    question=q,
                    synthesis=f"Exploration failed: {e}",
                )
        return results
