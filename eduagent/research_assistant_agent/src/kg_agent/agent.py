"""KG Agent — queries the Neo4j knowledge graph and proposes grounded research questions.

Designed to be reusable across all EDU Agent modes:
  - Strategic Canvas: map challenge → query KG → propose questions with sub-questions
  - Default mode (future): pre-check KG coverage before deep research
  - Deep Guided (future): check coverage per goal after codebook generation
"""
import asyncio
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage

from src.neo4j_config import OUTCOMES, POPULATIONS
from src.kg_agent.queries import (
    get_papers_by_taxonomy,
    get_outcome_coverage,
    get_total_paper_count,
)


# ── Data classes ───────────────────────────────────────────────────────────────

@dataclass
class TaxonomyMapping:
    outcomes: List[str] = field(default_factory=list)
    populations: List[str] = field(default_factory=list)
    reasoning: str = ""


@dataclass
class KGCoverage:
    total_papers: int = 0
    relevant_papers: List[Dict[str, Any]] = field(default_factory=list)
    outcome_counts: Dict[str, int] = field(default_factory=dict)
    matched_outcomes: List[str] = field(default_factory=list)
    matched_populations: List[str] = field(default_factory=list)

    def coverage_summary(self) -> str:
        """Format a concise summary string for injection into an LLM prompt."""
        lines = [
            f"Total papers in knowledge base: {self.total_papers}",
            f"Papers relevant to this challenge: {len(self.relevant_papers)}",
        ]
        if self.outcome_counts:
            lines.append("\nOutcome coverage (papers per outcome):")
            for outcome, count in sorted(self.outcome_counts.items(), key=lambda x: -x[1]):
                lines.append(f"  - {outcome}: {count} paper(s)")
        if self.relevant_papers:
            lines.append("\nSample relevant papers:")
            for p in self.relevant_papers[:8]:
                title = p.get("title", "Untitled")
                year = p.get("year") or "n/d"
                design = p.get("study_design") or ""
                direction = p.get("finding_direction") or ""
                lines.append(f"  - {title} ({year}){' — ' + design if design else ''}{' [' + direction + ']' if direction else ''}")
        return "\n".join(lines)


# ── Async bridge ───────────────────────────────────────────────────────────────

def _run(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


# ── Prompts ────────────────────────────────────────────────────────────────────

_TAXONOMY_MAPPING_PROMPT = f"""You are mapping a strategic education challenge to a research taxonomy.

Available taxonomy terms:

OUTCOMES (choose any that apply):
{chr(10).join(f'  - {o}' for o in OUTCOMES)}

POPULATIONS (choose any that apply):
{chr(10).join(f'  - {p}' for p in POPULATIONS)}

Return valid JSON only — no markdown, no explanation:
{{
  "outcomes": ["exact strings from OUTCOMES"],
  "populations": ["exact strings from POPULATIONS"],
  "reasoning": "one sentence explaining the mapping"
}}

Use only exact strings from the lists above. Return empty arrays if nothing fits.
"""

_QUESTION_PROPOSAL_PROMPT = """You are a strategic research coach specializing in education.
Your job is to propose focused research questions grounded in what a knowledge base actually contains.

You will receive:
1. A strategic challenge from the user
2. A summary of what's in the knowledge base (papers, outcomes covered, gaps)

Propose 3–5 core research questions that:
- Are directly relevant to the strategic challenge
- Are specific enough to be answerable by education research
- Reflect what's actually in the knowledge base (don't invent coverage)
- Surface genuine gaps where deep research would add value

For each question, also provide 2–3 sub-questions — variations or more specific angles.

Return valid JSON only:
{
  "questions": [
    {
      "core_question": "The main research question",
      "sub_questions": ["Variation 1", "Variation 2"],
      "kg_coverage": "strong|partial|none",
      "gap_description": "What's missing — be specific about populations, designs, contexts"
    }
  ],
  "overall_assessment": "2–3 sentences on the overall evidence landscape for this challenge"
}

kg_coverage guidance:
- "strong": 3+ relevant papers in the KG with decent study designs
- "partial": 1–2 papers, or papers that are adjacent but not directly on this question
- "none": no relevant papers found in the KG
"""


# ── KGAgent ────────────────────────────────────────────────────────────────────

class KGAgent:
    """Queries the Neo4j knowledge graph and proposes research questions grounded in real data.

    Usage:
        agent = KGAgent()
        coverage = agent.query_coverage(challenge, model_provider)
        questions = agent.propose_questions(challenge, coverage, model_provider)
    """

    # ── Taxonomy mapping ──────────────────────────────────────────────────────

    async def _map_to_taxonomy(self, challenge: str, model_provider: str) -> TaxonomyMapping:
        model = init_chat_model(model=model_provider, max_tokens=512)
        response = await model.ainvoke([
            SystemMessage(content=_TAXONOMY_MAPPING_PROMPT),
            HumanMessage(content=f"Strategic challenge:\n{challenge}"),
        ])
        content = response.content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(l for l in lines if not l.strip().startswith("```")).strip()
        data = json.loads(content)
        return TaxonomyMapping(
            outcomes=data.get("outcomes", []),
            populations=data.get("populations", []),
            reasoning=data.get("reasoning", ""),
        )

    def map_to_taxonomy(self, challenge: str, model_provider: str) -> TaxonomyMapping:
        return _run(self._map_to_taxonomy(challenge, model_provider))

    # ── KG query ──────────────────────────────────────────────────────────────

    def query_coverage(self, challenge: str, model_provider: str) -> KGCoverage:
        """Map challenge to taxonomy, query Neo4j, return structured coverage."""
        try:
            mapping = self.map_to_taxonomy(challenge, model_provider)
        except Exception:
            mapping = TaxonomyMapping()

        try:
            relevant = get_papers_by_taxonomy(
                outcomes=mapping.outcomes,
                populations=mapping.populations,
            )
        except Exception:
            relevant = []

        try:
            outcome_rows = get_outcome_coverage()
            outcome_counts = {r["outcome"]: r["paper_count"] for r in outcome_rows if r["outcome"]}
        except Exception:
            outcome_counts = {}

        try:
            total = get_total_paper_count()
        except Exception:
            total = 0

        return KGCoverage(
            total_papers=total,
            relevant_papers=relevant,
            outcome_counts=outcome_counts,
            matched_outcomes=mapping.outcomes,
            matched_populations=mapping.populations,
        )

    # ── Question proposal ─────────────────────────────────────────────────────

    async def _propose_questions(
        self,
        challenge: str,
        coverage: KGCoverage,
        model_provider: str,
    ) -> Dict[str, Any]:
        model = init_chat_model(model=model_provider, max_tokens=2048)
        prompt = (
            f"Strategic challenge:\n{challenge}\n\n"
            f"Knowledge base summary:\n{coverage.coverage_summary()}"
        )
        response = await model.ainvoke([
            SystemMessage(content=_QUESTION_PROPOSAL_PROMPT),
            HumanMessage(content=prompt),
        ])
        content = response.content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(l for l in lines if not l.strip().startswith("```")).strip()
        return json.loads(content)

    def propose_questions(
        self,
        challenge: str,
        coverage: KGCoverage,
        model_provider: str,
    ) -> Dict[str, Any]:
        """Returns {"questions": [...], "overall_assessment": "..."}"""
        return _run(self._propose_questions(challenge, coverage, model_provider))
