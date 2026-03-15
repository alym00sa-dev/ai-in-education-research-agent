"""Strategic Canvas advisor agent."""
import asyncio
import json
import re
from typing import List, Dict, Optional

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from src.strategic_canvas.prompts import STRATEGIC_CANVAS_SYSTEM_PROMPT, KG_CONTEXT_INJECTION


def _run(coro):
    """Run an async coroutine from a sync context (same pattern as goal_agent.py)."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


class StrategicCanvasAgent:

    async def _chat_turn(
        self,
        history: List[Dict[str, str]],
        user_message: str,
        model_provider: str,
        context_text: str = "",
        kg_injection: str = "",
    ) -> str:
        system = STRATEGIC_CANVAS_SYSTEM_PROMPT
        if context_text:
            system += f"\n\n## Uploaded Context Files\n{context_text[:6000]}"

        model = init_chat_model(model=model_provider, max_tokens=2048)
        messages = [SystemMessage(content=system)]
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))

        # If KG results are being injected, append them to the user message
        final_message = user_message
        if kg_injection:
            final_message = f"{user_message}\n\n{kg_injection}"

        messages.append(HumanMessage(content=final_message))
        response = await model.ainvoke(messages)
        return response.content.strip()

    def chat_turn(
        self,
        history: List[Dict[str, str]],
        user_message: str,
        model_provider: str,
        context_text: str = "",
        kg_injection: str = "",
    ) -> str:
        return _run(self._chat_turn(history, user_message, model_provider, context_text, kg_injection))

    def has_draft_questions(self, response: str) -> bool:
        """True if the agent has proposed draft questions for user approval."""
        return "---DRAFT QUESTIONS---" in response

    def parse_draft_questions(self, response: str) -> Dict:
        """Extract draft questions from ---DRAFT QUESTIONS--- JSON block."""
        match = re.search(
            r"---DRAFT QUESTIONS---(.*?)---END DRAFT---",
            response, re.DOTALL,
        )
        if not match:
            return {}
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            return {}

    def parse_proposed_research(self, response: str) -> List[str]:
        """Extract research questions from ---PROPOSE RESEARCH--- block."""
        match = re.search(
            r"---PROPOSE RESEARCH---(.*?)---END RESEARCH---",
            response, re.DOTALL,
        )
        if not match:
            return []
        return [line.strip() for line in match.group(1).strip().splitlines() if line.strip()]

    def ready_for_export(self, response: str) -> bool:
        return "---READY FOR EXPORT---" in response
