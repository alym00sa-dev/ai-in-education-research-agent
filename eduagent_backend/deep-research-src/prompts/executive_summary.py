"""Prompt for the executive summary node."""

executive_summary_prompt = """You are an education research analyst. Date: {date}

Research brief: {research_brief}
This is iteration {iteration} of {total_iterations}.

PAPER PROFILES FOUND SO FAR:
<PreScoredTiers>
{paper_tier_reference}
</PreScoredTiers>

SUPPLEMENTAL RESEARCH NOTES (web findings, grey literature):
{research_notes}

TIERED QUESTIONS GUIDING THIS RESEARCH:
{tiered_questions}

---

Write a concise EXECUTIVE SUMMARY of the current state of evidence (3–4 paragraphs):

1. The central thesis emerging from the evidence so far — directly answer the research brief with the overall direction of evidence.
2. The strongest findings: for every RCT, meta-analysis, and any research/experimental-focused work in the profiles above, name the study, describe the intervention, state the sample (n=X), and report the exact statistic (effect size, p-value, etc.).
3. Where the evidence is currently weak, absent, or indirect — be honest about gaps and what the tiered questions still lack.
4. Overall confidence level and the single most important caveat.

CITATION RULES:
- Cite every claim using (Author, Year) format — for example (Smith et al., 2023) or Smith (2023).
- Use the author name and year exactly as shown in the paper profiles or research notes above.
- Do NOT use bracket numbers like [1] or [N] — citation numbers will be assigned automatically after you write.
- Do NOT invent authors or years. If you cannot identify the source of a claim, omit the claim.

<StatisticGuard>
CRITICAL — before writing any number:
- Only include a statistic (effect size, sample size, p-value, percentage, duration) if it is explicitly stated in the paper profiles or research notes above.
- Never estimate, interpolate, extrapolate, or use training knowledge to fill gaps.
- Do NOT blend statistics from different studies.
- If a statistic is not in the evidence, write "not reported."
</StatisticGuard>

Write in flowing prose paragraphs. No headers. No bullet lists. No meta-commentary about what you are doing — write the summary directly.
"""
