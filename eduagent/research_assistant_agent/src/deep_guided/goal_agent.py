"""Goal discovery agent and codebook generator for Deep Guided mode."""
import asyncio
import json
import re
from typing import List, Dict, Optional

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from src.deep_guided.config_schema import ResearchGoal, TechConfig, Codebook
from src.deep_guided.prompts import (
    GOAL_CHAT_SYSTEM_PROMPT,
    CODEBOOK_GENERATION_SYSTEM_PROMPT,
    PDF_ANNOTATION_PROMPT,
)


def _run(coro):
    """Run an async coroutine from a sync context."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


class GoalAgent:
    """Handles goal discovery chat and codebook generation."""

    # ── Goal discovery chat ───────────────────────────────────────────────────

    async def _chat_turn(
        self,
        history: List[Dict[str, str]],
        user_message: str,
        model_provider: str,
    ) -> str:
        model = init_chat_model(model=model_provider, max_tokens=1024)
        messages = [SystemMessage(content=GOAL_CHAT_SYSTEM_PROMPT)]
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))
        messages.append(HumanMessage(content=user_message))
        response = await model.ainvoke(messages)
        return response.content.strip()

    def chat_turn(self, history, user_message, model_provider) -> str:
        return _run(self._chat_turn(history, user_message, model_provider))

    def parse_proposed_goals(self, agent_response: str) -> List[str]:
        """Extract goals from ---PROPOSED GOALS--- block if present."""
        match = re.search(
            r"---PROPOSED GOALS---(.*?)---END GOALS---", agent_response, re.DOTALL
        )
        if not match:
            return []
        block = match.group(1).strip()
        goals = []
        for line in block.splitlines():
            m = re.match(r"^\d+\.\s+(.+)", line.strip())
            if m:
                goals.append(m.group(1).strip())
        return goals

    # ── Codebook generation ───────────────────────────────────────────────────

    async def _generate_codebook(
        self,
        goals: List[ResearchGoal],
        tech_config: TechConfig,
        model_provider: str,
        extra_context: Optional[str] = None,
    ) -> Codebook:
        model = init_chat_model(model=model_provider, max_tokens=2048)

        goals_text = "\n".join(
            f"goal_{i+1} [{g.goal_id}]: {g.statement}"
            for i, g in enumerate(goals)
        )
        config_text = (
            f"Evidence hierarchy (strongest first): {', '.join(tech_config.evidence_hierarchy)}\n"
            f"Citation scoring weights: {tech_config.citation_scoring}\n"
            f"Source domains: {', '.join(tech_config.source_domains)}\n"
            f"Search depth: {tech_config.search_depth}"
        )

        prompt = f"Research Goals:\n{goals_text}\n\nConfiguration:\n{config_text}"
        if extra_context:
            prompt += f"\n\nAdditional guidance: {extra_context}"

        content = ""
        response = await model.ainvoke([
            SystemMessage(content=CODEBOOK_GENERATION_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])
        content = response.content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(l for l in lines if not l.strip().startswith("```")).strip()

        data = json.loads(content)
        raw_directions = data.get("research_directions", {})

        # Map numbered keys (goal_1, goal_2...) back to goal IDs
        directions: Dict[str, str] = {}
        for i, goal in enumerate(goals):
            key = f"goal_{i+1}"
            directions[goal.goal_id] = raw_directions.get(key, "")

        return Codebook(
            scoring_rubric=data.get("scoring_rubric", ""),
            research_directions=directions,
        )

    def generate_codebook(
        self,
        goals: List[ResearchGoal],
        tech_config: TechConfig,
        model_provider: str,
        extra_context: Optional[str] = None,
    ) -> Codebook:
        return _run(self._generate_codebook(goals, tech_config, model_provider, extra_context))

    # ── PDF annotation ────────────────────────────────────────────────────────

    async def _annotate_pdf(
        self,
        pdf_text: str,
        user_note: str,
        goals: List[ResearchGoal],
        model_provider: str,
    ) -> str:
        model = init_chat_model(model=model_provider, max_tokens=512)
        goals_text = "\n".join(f"- {g.statement}" for g in goals)
        prompt = (
            f"Research goals:\n{goals_text}\n\n"
            f"User's note: {user_note or 'None provided.'}\n\n"
            f"Study excerpt (first 3000 chars):\n{pdf_text[:3000]}"
        )
        response = await model.ainvoke([
            SystemMessage(content=PDF_ANNOTATION_PROMPT),
            HumanMessage(content=prompt),
        ])
        return response.content.strip()

    def annotate_pdf(self, pdf_text, user_note, goals, model_provider) -> str:
        return _run(self._annotate_pdf(pdf_text, user_note, goals, model_provider))
