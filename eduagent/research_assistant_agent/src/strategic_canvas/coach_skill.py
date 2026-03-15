"""Strategic research coach as a Claude skill using the Anthropic SDK.

The coach is pinned to claude-sonnet-4-6. Instead of emitting text markers,
it calls two tools:
  - propose_draft_questions: when ready to surface research questions
  - signal_export_ready: when synthesis is complete

The model selector in the Strategic Canvas UI controls the deep research runs only.
"""
import json
from dataclasses import dataclass, field
from typing import List, Dict

import anthropic

_CLIENT = anthropic.Anthropic()
_MODEL = "claude-sonnet-4-6"

_TOOLS = [
    {
        "name": "propose_draft_questions",
        "description": (
            "Call this when you genuinely understand the strategic challenge — usually after "
            "3 to 5 exchanges — and are ready to surface research questions for user review. "
            "Do not call this too early. Earn it through the conversation."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "narrative": {
                    "type": "string",
                    "description": "One or two plain sentences framing your thinking before the questions appear.",
                },
                "questions": {
                    "type": "array",
                    "description": "3 to 5 research questions grounded in the strategic logic you heard.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "core_question": {"type": "string"},
                            "sub_questions": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                        "required": ["core_question", "sub_questions"],
                    },
                },
            },
            "required": ["narrative", "questions"],
        },
    },
    {
        "name": "signal_export_ready",
        "description": "Call this when research synthesis is complete and the strategy document is ready for export.",
        "input_schema": {
            "type": "object",
            "properties": {
                "narrative": {
                    "type": "string",
                    "description": "Brief plain-text closing statement.",
                }
            },
            "required": ["narrative"],
        },
    },
]

_SYNTHESIS_SYSTEM = """You are writing a final strategic research report that synthesizes findings from multiple deep research runs, each addressing a specific research question within a broader strategic challenge.

Structure your report exactly as follows:

## Executive Summary
2–3 paragraphs. What does the overall body of evidence say about the strategic challenge? Where is coverage strong vs. thin? What are the highest-confidence takeaways?

## Findings by Research Question
For each question: key findings, evidence quality (study designs found, effect sizes if any), and the strategic implication.

## Cross-Cutting Themes
2–3 themes that emerge consistently across multiple questions.

## Strategic Recommendations
3–5 concrete, evidence-grounded recommendations. Note confidence level for each (strong / moderate / emerging evidence).

## Evidence Gaps & Future Research
What was NOT found that would materially change the strategic conclusions.

## Research Frontier
Keep this section tight — 2 parts only:

**Replication Candidates (2–3 max):** Studies with strong findings (RCT or quasi-experimental, clear effect) but narrow context (single site, specific population, short duration) that are worth replicating at scale or in different settings. For each: what was found, why it's promising, what replication would look like.

**Novel Hypotheses (1–2 max):** Use Swanson's ABC model — find cross-question chains where a shared bridging mechanism B connects an intervention A (from one question's findings) to an outcome C (from another question's findings) that has never been directly studied together. For each hypothesis use this structure:

- **A → B → C**: [Intervention] → [Bridging mechanism] → [Novel outcome/population]
- **A→B evidence**: [citation(s) supporting this leg] — confidence: Strong / Moderate / Speculative
- **B→C evidence**: [citation(s) supporting this leg] — confidence: Strong / Moderate / Speculative
- **Overall confidence**: Strong (both legs ≥2 sources, at least one experimental) / Moderate (both legs supported but correlational) / Speculative (one leg has only 1 source or observational)
- **Why novel**: One sentence — what makes this A→C connection untested and worth investigating.

Only include if both legs are explicitly grounded in the research summaries. Do not infer.

Write concretely. Cite specific studies and findings from the summaries. Acknowledge gaps honestly. Audience: sophisticated education investor or strategist.

<Citation Rules>
- Assign each unique URL a single citation number in your text
- End with ### Sources that lists each source with corresponding numbers
- Number sources sequentially without gaps (1, 2, 3...)
- Cite only sources that genuinely support a claim — do NOT pad the source list

For each source, evaluate using the K-12 Evidence Framework:

**QUALITY RATING (Blue/Green/Yellow/Red):**

🔵 BLUE (Highest Quality): Meta-analysis OR well-designed experimental study; credible third-party + peer reviewed + addresses positionality; disaggregated by race/income + representative of priority populations + timely (within 10 years) + relevant context.

🟢 GREEN (Moderate to Strong): Well-designed quasi-experimental; 2 of 3 credibility criteria; 3 of 4 relevance criteria.

🟡 YELLOW (Limited): Correlational or qualitative; 1 of 3 credibility criteria; 2 of 4 relevance criteria.

🔴 RED (Low): Does not meet quality standards; meets none of the credibility or relevance criteria.

**IMPACT RATING (Blue/Green/Yellow/Red):**

🔵 BLUE: Effect size ≥0.20 for priority populations (Black, Latino, poverty).
🟢 GREEN: Effect size 0.05–0.20 for priority populations OR ≥0.20 for general population.
🟡 YELLOW: Effect size <0.05 for general population.
🔴 RED: No measurable effect or harmful effects.

**FORMAT per source:**
[N] [Study Title](URL)
    **Quality:** 🔵 Blue - [Brief justification]
    **Impact:** 🟢 Green - [Brief justification]

After all sources, add:
### Body of Evidence Maturity: MATURE 🔵 / LIMITED 🟢 / EMERGING 🟡 / EARLY 🔴
**Justification**: [1–2 sentences]
</Citation Rules>"""


_SYSTEM_PROMPT = """You are a strategic research coach working at the intersection of education research and investment strategy. The people you work with are thinking about where to direct resources for maximum impact in education — they have investment theses, portfolio strategies, and theories of change they are pressure-testing. They are thinking upstream: what does the evidence say, what do we still not know, where does research support placing a bet?

You work exclusively in the education domain: K-12, higher ed, ed-tech, tutoring, learning science, teacher development, curriculum, policy, and adjacent areas.

How you talk:
- Plain prose only. No bold, no bullets, no headers. Just sentences.
- Short responses. One idea at a time.
- Ask one real question at a time — never a menu of options.
- Listen for the investment logic underneath what they say: the theory of change, the load-bearing assumption, what would have to be true for the strategy to work.
- Push back gently when the framing is too narrow (anchored on one product) or too vague (just restating a desired outcome without a mechanism).
- Help them articulate what mechanism they believe is doing the work, what conditions matter, and what outcomes would signal the strategy is working — at a level of abstraction that applies across a portfolio, not one tool.
- Don't rush. Stay in the conversation until you understand the strategic logic.

When you are ready to surface research questions, call propose_draft_questions. Not before — earn it through the conversation.
When synthesis is complete and the strategy document is ready, call signal_export_ready."""


# ── Response type ───────────────────────────────────────────────────────────────

@dataclass
class CoachResponse:
    type: str  # "text" | "propose_questions" | "export_ready"
    narrative: str = ""
    questions: List[Dict] = field(default_factory=list)

    def to_storage_string(self) -> str:
        """Encode for storage in sc_chat_history."""
        if self.type == "propose_questions":
            data = json.dumps({"questions": self.questions})
            return f"__QUESTIONS__\n{self.narrative}\n__JSON__\n{data}"
        if self.type == "export_ready":
            return f"__EXPORT_READY__\n{self.narrative}"
        return self.narrative

    @staticmethod
    def from_storage_string(s: str) -> "CoachResponse":
        """Decode a stored chat history string back into a CoachResponse."""
        if s.startswith("__QUESTIONS__\n"):
            parts = s.split("\n__JSON__\n", 1)
            narrative = parts[0][len("__QUESTIONS__\n"):]
            data = json.loads(parts[1]) if len(parts) > 1 else {}
            return CoachResponse(
                type="propose_questions",
                narrative=narrative,
                questions=data.get("questions", []),
            )
        if s.startswith("__EXPORT_READY__\n"):
            return CoachResponse(
                type="export_ready",
                narrative=s[len("__EXPORT_READY__\n"):],
            )
        return CoachResponse(type="text", narrative=s)


# ── CoachSkill ──────────────────────────────────────────────────────────────────

class CoachSkill:
    """Strategic research coach — Claude skill, pinned to claude-sonnet-4-6."""

    def _build_messages(
        self, history: List[Dict[str, str]], user_message: str, kg_injection: str
    ) -> list:
        messages = []
        for msg in history:
            content = msg["content"]
            if msg["role"] == "user":
                messages.append({"role": "user", "content": content})
            else:
                # Decode stored responses; send only the narrative text to the API
                decoded = CoachResponse.from_storage_string(content)
                narrative = decoded.narrative.split("\n\n---PROPOSE RESEARCH---")[0].strip()
                if narrative:
                    messages.append({"role": "assistant", "content": narrative})

        final = f"{user_message}\n\n{kg_injection}" if kg_injection else user_message
        messages.append({"role": "user", "content": final})
        return messages

    def chat_turn(
        self,
        history: List[Dict[str, str]],
        user_message: str,
        context_text: str = "",
        kg_injection: str = "",
    ) -> CoachResponse:
        system = _SYSTEM_PROMPT
        if context_text:
            system += f"\n\nContext files uploaded by user:\n{context_text[:4000]}"

        messages = self._build_messages(history, user_message, kg_injection)

        response = _CLIENT.messages.create(
            model=_MODEL,
            max_tokens=1024,
            system=system,
            tools=_TOOLS,
            messages=messages,
        )

        # Extract any text content
        narrative = ""
        for block in response.content:
            if hasattr(block, "text"):
                narrative += block.text

        if response.stop_reason == "tool_use":
            for block in response.content:
                if block.type == "tool_use":
                    args = block.input
                    if block.name == "propose_draft_questions":
                        return CoachResponse(
                            type="propose_questions",
                            narrative=args.get("narrative", narrative).strip(),
                            questions=args.get("questions", []),
                        )
                    if block.name == "signal_export_ready":
                        return CoachResponse(
                            type="export_ready",
                            narrative=args.get("narrative", narrative).strip(),
                        )

        return CoachResponse(type="text", narrative=narrative.strip())

    def synthesize_research(
        self,
        strategic_challenge: str,
        research_summaries: Dict[str, str],
        context_text: str = "",
    ) -> str:
        """Generate a cohesive strategy report from all per-question research summaries."""
        parts = [f"**Strategic Challenge:**\n{strategic_challenge}\n"]
        for q, summary in research_summaries.items():
            parts.append(f"**Research Question:** {q}\n\n{summary[:5000]}")
        combined = "\n\n---\n\n".join(parts)

        system = _SYNTHESIS_SYSTEM
        if context_text:
            system += f"\n\nContext from uploaded files:\n{context_text[:2000]}"

        response = _CLIENT.messages.create(
            model=_MODEL,
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": combined}],
        )
        text = ""
        for block in response.content:
            if hasattr(block, "text"):
                text += block.text
        return text.strip()
