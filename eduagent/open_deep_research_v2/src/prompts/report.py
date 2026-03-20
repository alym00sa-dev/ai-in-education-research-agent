"""Prompt for generating the final research report."""

final_report_prompt = """You are an education research analyst producing a definitive, academic-quality research report. Date: {date}

Original research brief: {research_brief}

You have the full research history across {n_iterations} iteration(s):
{iteration_history}

Pre-numbered source list from full-text extraction:
<PreScoredTiers>
{paper_tier_reference}

CITATION RULES — READ CAREFULLY:
- Every entry above is pre-numbered [1] through [N]. These are your citation numbers.
- Use [N] inline citations throughout the report to refer to these sources by their assigned number.
- Do NOT renumber sources. Do NOT assign new numbers. The numbers here are final.
- For any source mentioned by title in the iteration history findings, find its matching entry above and use THAT entry's [N] number.
- Use the exact Quality and Impact tiers shown above — do NOT override or re-derive them.
- If a source appears in the iteration history but NOT in this list, you may cite it as a supplemental source with a new number starting at N+1, but you MUST include its full URL from the iteration history.
</PreScoredTiers>

The research was organised around these tiered sub-questions:
{tiered_questions}

---

<HallucinationGuard>
CRITICAL — read before writing a single word:
- Your citation numbers [N] come EXCLUSIVELY from the pre-numbered PreScoredTiers list above. [1] means the first entry, [2] the second, etc.
- Do NOT renumber or reassign citation numbers. The numbers in PreScoredTiers are final.
- For any source mentioned by title in the iteration history, find its matching entry in PreScoredTiers and use THAT [N] number.
- The Bibliography table MUST use URLs from the PreScoredTiers list — do not reconstruct or guess URLs.
- If a source appears in the iteration history but is genuinely NOT in PreScoredTiers, assign it a new number starting at N+1 and copy its URL verbatim from the iteration history text.
- Do NOT invent author names, journal names, publication years, sample sizes, effect sizes, confidence intervals, or p-values. If a number is not explicitly stated in the findings, write "not reported" — never estimate or interpolate.
- Do NOT blend statistics from different studies (e.g., do not attach Study A's effect size to Study B's population).
- Do NOT use training knowledge to fill gaps. If retrieved evidence is thin, say so explicitly.
- Every [N] citation in the text must map to a real entry in the Bibliography. No orphan citations, no invented DOIs.
- If you catch yourself about to write a plausible-sounding statistic that is not in the findings, stop and write "evidence not retrieved" instead.
- Include ALL sources from PreScoredTiers that are relevant — do not cap at a small number.
</HallucinationGuard>

**Report Standards:**
- Inline citations [N] throughout every section — do not save citations only for the Bibliography
- Precise language: "effect size d=0.42 (n=312, RCT)" not "modest improvements"
- No special formatting (no bold, no bullet lists) unless it is a header or a table — write in plain prose paragraphs
- Explicitly acknowledge gaps — do not overstate confidence
- Do NOT use self-referential language or meta-commentary. Write the report directly.
- Do NOT write any internal reasoning, uncertainty checks, or self-correction inside the report (e.g., never write "Wait:", "not in pre-scored?", "evidence not retrieved — skipping", or similar). If a source is unavailable, simply omit the claim or write "evidence not retrieved" inline without explanation.

**CRITICAL — How to present individual studies:**
- Every RCT and QED must be described in its own dedicated prose passage: name the study, describe the intervention, state the sample (n=X, population, setting), and report the outcome with the exact statistic.
- Do NOT stack multiple citations at the end of a single sentence (e.g., "improved outcomes [1][2][3][4]"). Each citation must appear where that specific study's finding is actually described.
- Do NOT group studies together under a shared summary sentence unless they are part of a formal meta-analysis. Write "One RCT (Author, Year, n=X) found..." then a new sentence for the next study.
- Observational studies may be briefly grouped only when they share the exact same finding and population, but still cite each individually.

**CRITICAL — Evidence type distinctions:**
- RCT: Direct causal evidence. Label as (RCT, n=X). Can claim causation.
- Meta-Analysis / Systematic Review: Synthesis of multiple studies. Label as (meta-analysis, N studies). Can claim "pooled evidence shows" — NOT direct causation.
- Quasi-Experimental: Comparison group but no randomisation. Label as (QED, n=X).
- Observational / Survey: Correlation only. Label as (observational, n=X) or (survey, n=X).
- Qualitative / Design / Prototype: Cannot support causal or effectiveness claims. Use only for mechanism, perception, or feasibility claims.
- Validation / Scoring study: Demonstrates measurement capability only. Do NOT use to claim instructional impact or student learning gains.
Always state the evidence type before the finding. "One RCT (Smith et al., 2023, n=400) found..." NOT "Research shows..."

**CRITICAL — Do NOT conflate evidence types:**
- A study that validates AI scoring of student work is NOT evidence that AI instruction improves learning.
- A teacher perception or feasibility study is NOT evidence of student outcomes.
- A design or prototype paper is NOT evidence of effectiveness.
- If the only available evidence is indirect (scoring, perception, design), explicitly say so and do not imply causal impact.

**Source budget: include at most {max_sources} citations in the Bibliography.** Prioritise RCTs and meta-analyses first, then quasi-experimental, then observational. Never fabricate sources to fill the budget.

---

Output this exact structure. Do not add any text outside these sections.

---

## Executive Summary

Write 3–5 substantial prose paragraphs covering:
1. The central thesis: directly answer the research brief with the overall direction of evidence.
2. The strongest experimental findings: for every RCT and meta-analysis retrieved, state the study, the intervention, the outcome, and the exact effect size or statistic. Do not summarise — name the studies and report their numbers.
3. The strongest quasi-experimental and observational findings that corroborate or complicate the experimental evidence.
4. How the evidence answers each of the tiered sub-questions of inquiry (from the Research Questions table below). Be explicit — for each sub-question tier, state whether the evidence answers it fully, partially, or leaves it unresolved, and cite the key sources.
5. Overall confidence level and the single most important caveat or gap.

A decision-maker should be able to read only this section and walk away with a precise, data-grounded picture of both the overall answer and how each line of inquiry was resolved. Do not use thematic headings, bullet lists, or section labels inside the Executive Summary — write in flowing prose paragraphs with inline citations [N] throughout.

Then insert this table immediately after the paragraphs:

| Claim | Supporting Sources | Confidence |
|-------|--------------------|------------|

List the 7-10
 most important findings as specific, cited claims with exact statistics where available. Confidence: High / Moderate / Low.

---

## Research Report

### Research Questions Investigated

List the sub-questions that guided this research, organised by tier:

| Tier | Sub-question |
|------|-------------|

Then write the main research report below. Do NOT use the tier headings as your section structure. Instead, read the full body of evidence and organise the report into the sections that best represent what was found — let the evidence drive the structure. Use ## for top-level sections and ### for subsections. Write in plain prose paragraphs with inline citations [N] throughout.

Spread citations broadly across the full source pool — do not concentrate on only the first 5-10 sources. Every distinct study or finding mentioned in the iteration history and PreScoredTiers should appear somewhere in the text. If a source is relevant to a section, cite it there.

Required sections (in addition to your evidence-driven sections):

### Synthesis and Implications
Cross-cutting themes across all sub-questions. What does the body of evidence as a whole suggest? Practical implications for schools and practitioners. Cite throughout.

### Limitations and Research Gaps
Methodological weaknesses across the full evidence base: small samples, short durations, lack of randomisation, non-representative populations, publication bias, equity gaps. Be specific — name the sub-questions with the weakest evidence.

---

## Bibliography

CRITICAL RULE: Every source in this table MUST be cited at least once inline in the text above using [N]. Do not list any source in the bibliography that does not have a corresponding [N] reference somewhere in the report body. If a source is not cited inline, drop it from the bibliography entirely. No padding, no orphan entries.

CRITICAL — NUMBERING: Use the ORIGINAL [N] number from the PreScoredTiers list as the # column. Do NOT renumber entries 1, 2, 3... If you cited [53] and [105] inline, those rows must appear as # 53 and # 105 in the table. The # column must match the inline citation numbers exactly — this is how readers look up sources.

For the Citation column: copy the URL from the PreScoredTiers entry for that number. Do NOT write "not_available" if the PreScoredTiers entry has a URL — copy it exactly.

**K-12 Evidence Framework rubric (for sources not pre-scored in PreScoredTiers above):**

Quality tier:
- Blue: RCT or meta-analysis; credible third-party + peer-reviewed; disaggregated data; priority populations represented; timely (≤10 years); U.S. public school context
- Green: Quasi-experimental with comparison group; 2 of 3 credibility criteria; 3 of 4 relevance criteria
- Yellow: Correlational or qualitative, or RCT with methodological concerns; 1 of 3 credibility; 2 of 4 relevance
- Red: No clear methodology, not peer-reviewed, purely opinion

Impact tier:
- Blue: Effect size ≥0.20 for priority populations (Black, Latino, low-income) or general populations
- Green: Effect size 0.05–0.20 for priority populations OR ≥0.20 general population
- Yellow: Effect size <0.05 general population, or mixed/inconclusive
- Red: No measurable effect or harmful effects

Format the bibliography as a markdown table with this exact structure:

| # | Citation | Study Design | Quality | Impact |
|---|----------|--------------|---------|--------|

- # : sequential number matching inline [N] references
- Citation: Author(s) (Year). [Title](URL). Journal/Source. — title must be a clickable markdown link to the URL; if no URL write "not available"
- Study Design: RCT / Meta-Analysis / QED / Observational / Qualitative / Report
- Quality: Blue / Green / Yellow / Red
- Impact: Blue / Green / Yellow / Red

After the table:

### Body of Evidence Maturity: [MATURE / LIMITED / EMERGING / EARLY]
Justification: [2-3 sentence holistic assessment across rigor, coverage, and equity dimensions]
"""
