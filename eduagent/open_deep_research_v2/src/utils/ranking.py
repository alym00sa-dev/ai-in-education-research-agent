"""Relevance + quality ranking for paper profiles.

Sorts paper profiles by a composite score so the LLM sees the strongest,
most query-relevant papers first (before any context truncation).

Composite score (0–1):
    relevance   × 0.50   — keyword overlap with research brief + tiered questions
    evidence    × 0.30   — study design strength (RCT/meta > QED > observational)
    quality     × 0.20   — K-12 Evidence Framework tier (blue > green > yellow > red)
"""

import re
import logging

logger = logging.getLogger(__name__)

# Stopwords excluded from keyword overlap (common English function words)
_STOPWORDS = {
    "the", "and", "for", "are", "with", "that", "this", "from", "have",
    "how", "what", "does", "which", "can", "they", "its", "was", "but",
    "not", "all", "has", "been", "were", "their", "who", "one", "more",
    "also", "into", "out", "use", "used", "using", "both", "such", "may",
}

_DESIGN_STRENGTH: dict[str, float] = {
    "Randomized Controlled Trial (RCT)": 1.0,
    "Meta-Analysis / Systematic Review": 1.0,
    "Quasi-Experimental Design (QED)": 0.7,
    "Mixed-Methods": 0.5,
    "Observational / Correlational": 0.4,
    "Qualitative": 0.2,
    "not_reported": 0.3,
}

_TIER_SCORE: dict[str, float] = {
    "blue": 1.0,
    "green": 0.75,
    "yellow": 0.5,
    "red": 0.25,
}


def _build_query_tokens(research_brief: str, tqm: dict) -> set[str]:
    """Extract meaningful tokens from the research brief and tiered question map."""
    question_text = " ".join(
        q for questions in tqm.values() if isinstance(questions, list) for q in questions
    )
    raw = re.findall(r'\b[a-z]{3,}\b', (research_brief + " " + question_text).lower())
    return {t for t in raw if t not in _STOPWORDS}


def _score_paper(paper, query_tokens: set[str]) -> float:
    """Compute composite relevance+quality score for a single paper."""
    if isinstance(paper, dict):
        quality = paper.get("quality_tier", "yellow")
        impact = paper.get("impact_tier", "yellow")
        design = paper.get("study_design", "not_reported")
        text = " ".join(filter(None, [
            paper.get("title", ""),
            paper.get("extended_summary", ""),
        ]))
    else:
        quality = getattr(paper, "quality_tier", "yellow")
        impact = getattr(paper, "impact_tier", "yellow")
        design = getattr(paper, "study_design", "not_reported")
        text = " ".join(filter(None, [
            getattr(paper, "title", "") or "",
            getattr(paper, "extended_summary", "") or "",
        ]))

    # Relevance: keyword overlap (capped at 1.0)
    if query_tokens:
        paper_tokens = set(re.findall(r'\b[a-z]{3,}\b', text.lower())) - _STOPWORDS
        # Normalise by 30% of query length so partial overlap still scores well
        overlap = len(paper_tokens & query_tokens) / max(1, len(query_tokens) * 0.3)
        relevance = min(1.0, overlap)
    else:
        relevance = 0.5

    evidence = _DESIGN_STRENGTH.get(design, 0.3)
    # Average quality and impact tiers
    q_score = (_TIER_SCORE.get(quality, 0.5) + _TIER_SCORE.get(impact, 0.5)) / 2.0

    return relevance * 0.50 + evidence * 0.30 + q_score * 0.20


def rank_profiles(
    profiles: list,
    research_brief: str,
    tqm: dict,
) -> list:
    """Return profiles sorted by composite relevance+quality score, highest first.

    Args:
        profiles: list of PaperProfile objects or dicts
        research_brief: the original research query
        tqm: tiered question map {tier1: [...], tier2: [...], ...}

    Returns:
        New sorted list (original list unchanged).
    """
    if not profiles:
        return profiles

    query_tokens = _build_query_tokens(research_brief, tqm or {})

    def _score_with_breakdown(p):
        if isinstance(p, dict):
            quality = p.get("quality_tier", "yellow")
            impact = p.get("impact_tier", "yellow")
            design = p.get("study_design", "not_reported")
            text = " ".join(filter(None, [p.get("title", ""), p.get("extended_summary", "")]))
        else:
            quality = getattr(p, "quality_tier", "yellow")
            impact = getattr(p, "impact_tier", "yellow")
            design = getattr(p, "study_design", "not_reported")
            text = " ".join(filter(None, [getattr(p, "title", "") or "", getattr(p, "extended_summary", "") or ""]))
        paper_tokens = set(re.findall(r'\b[a-z]{3,}\b', text.lower())) - _STOPWORDS
        relevance = min(1.0, len(paper_tokens & query_tokens) / max(1, len(query_tokens) * 0.3)) if query_tokens else 0.5
        evidence = _DESIGN_STRENGTH.get(design, 0.3)
        q_score = (_TIER_SCORE.get(quality, 0.5) + _TIER_SCORE.get(impact, 0.5)) / 2.0
        total = relevance * 0.50 + evidence * 0.30 + q_score * 0.20
        return total, relevance, evidence, q_score

    scored_with_meta = [(p, _score_with_breakdown(p)) for p in profiles]
    scored_with_meta.sort(key=lambda x: x[1][0], reverse=True)
    scored = [p for p, _ in scored_with_meta]

    # Log top-20 with full score breakdown
    logger.info(f"[rank_profiles] Ranked {len(scored)} papers — top 20:")
    for i, (p, (total, rel, evid, qual)) in enumerate(scored_with_meta[:20], 1):
        if isinstance(p, dict):
            title = (p.get("title", "") or "")[:70]
            design = p.get("study_design", "?")
            quality = p.get("quality_tier", "?")
        else:
            title = (getattr(p, "title", "") or "")[:70]
            design = getattr(p, "study_design", "?")
            quality = getattr(p, "quality_tier", "?")
        logger.info(
            f"  #{i:02d} [{total:.2f}] rel={rel:.2f} evid={evid:.2f} qual={qual:.2f} "
            f"| {design[:20]} | {quality} | {title}"
        )

    return scored
