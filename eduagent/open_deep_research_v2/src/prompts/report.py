"""Prompts for generating the final research report (two-pass: content then citation normalization)."""

# ---------------------------------------------------------------------------
# Pass 1 — Content generation
# The LLM focuses purely on synthesis quality. It references papers however
# feels natural (by title, author, description). A second LLM pass normalizes
# all references to (Author, Year) format before programmatic [N] injection.
# ---------------------------------------------------------------------------

final_report_prompt = """You are an education research analyst producing a definitive, academic-quality research report. Date: {date}

Original research brief: {research_brief}

Available source pool from full-text extraction (ranked by relevance and quality):
<SourcePool>
{paper_tier_reference}
</SourcePool>

SOURCING RULES:
- Every factual claim must be supported by a source from the SourcePool above.
- CITATION FORMAT: wrap every paper reference in double angle brackets: <<Author, Year>>. Example: <<Wang, 2024>> or (<<Wang, 2024>>). Use the first author's last name and the year exactly as shown in the SourcePool. Where the author is unclear, use the title keyword and year: <<TutorCoPilot, 2024>>.
- Do NOT use bracket numbers like [1] or [N] — these are assigned automatically after you write.
- Do NOT invent statistics, effect sizes, sample sizes, or author names. Only report what is stated in the SourcePool.
- TARGET: draw on at least {max_sources} distinct sources across the full report. Every section must include citations. The pool is ranked — prioritise sources near the top but draw broadly.
- Assess each source's utility before citing — does its design, population, and findings genuinely speak to the research question? Cite broadly but only where the source adds real evidential weight.
- Do NOT write a References or Bibliography section.

CRITIQUE HISTORY (gaps identified and addressed across research iterations):
{critique_summaries}

The research was organised around these tiered sub-questions:
{tiered_questions}

---

<HallucinationGuard>
CRITICAL — read before writing a single word:
- Do NOT invent author names, journal names, publication years, sample sizes, effect sizes, confidence intervals, or p-values. If a number is not explicitly stated in the SourcePool, write "not reported."
- Do NOT blend statistics from different studies.
- Do NOT use training knowledge to fill gaps. If retrieved evidence is thin, say so explicitly.
</HallucinationGuard>

**Report Standards:**
- Reference sources inline throughout every section
- Precise language: "effect size d=0.42 (n=312, RCT)" not "modest improvements"
- No special formatting (no bold, no bullet lists) unless it is a header or a table — write in plain prose paragraphs
- Explicitly acknowledge gaps — do not overstate confidence
- Do NOT use self-referential language or meta-commentary.

**CRITICAL — How to present individual studies:**
- Every RCT and QED must be described in its own dedicated prose passage: name the study, describe the intervention, state the sample (n=X, population, setting), and report the outcome with the exact statistic.
- Do NOT stack multiple citations at the end of a single sentence. Each citation must appear where that specific study's finding is described.
- Do NOT group studies under a shared summary sentence unless they are part of a formal meta-analysis.

**CRITICAL — Evidence type distinctions:**
- RCT: Direct causal evidence. Label as (RCT, n=X). Can claim causation.
- Meta-Analysis / Systematic Review: Label as (meta-analysis, N studies). Can claim "pooled evidence shows."
- Quasi-Experimental: Label as (QED, n=X).
- Observational / Survey: Label as (observational, n=X) or (survey, n=X).
- Qualitative / Design / Prototype: Cannot support causal or effectiveness claims.
- Validation / Scoring study: Demonstrates measurement capability only.
Always state the evidence type before the finding.

**CRITICAL — Do NOT conflate evidence types:**
- A study that validates AI scoring is NOT evidence that AI instruction improves learning.
- A teacher perception study is NOT evidence of student outcomes.
- If the only available evidence is indirect, explicitly say so.

---

Output this exact structure. Do not add any text outside these sections.

---

## Executive Summary

Write 3–5 substantial prose paragraphs covering:
1. The central thesis: directly answer the research brief with the overall direction of evidence.
2. The strongest experimental findings: for every RCT and meta-analysis retrieved, state the study, the intervention, the outcome, and the exact effect size or statistic.
3. The strongest quasi-experimental and observational findings that corroborate or complicate the experimental evidence.
4. How the evidence answers each of the tiered sub-questions. For each tier, state whether the evidence answers it fully, partially, or leaves it unresolved.
5. Overall confidence level and the single most important caveat or gap.

Then insert this table immediately after the paragraphs:

| Claim | Supporting Sources | Confidence |
|-------|--------------------|------------|

List the 7–10 most important findings as specific, cited claims with exact statistics. Confidence: High / Moderate / Low.

---

## Research Report

### Research Questions Investigated

List the sub-questions that guided this research, organised by tier:

| Tier | Sub-question |
|------|-------------|

Then write the main research report below. Organise into sections that best represent what was found — let the evidence drive the structure. Use ## for top-level sections and ### for subsections. Write in plain prose paragraphs with inline source references throughout.

CRITICAL — before finalising the report body, check that the following are covered with at least one cited claim each. Do NOT create a named section for each tier — weave them into your evidence-driven structure naturally:
- Tier 1: How is the intervention defined? What outcomes and populations are most studied?
- Tier 2: What do baseline or comparison conditions look like? What do studies use as a counterfactual?
- Tier 3: How is the intervention implemented in practice? What mechanisms or features drive outcomes?
- Tier 4: What are the effect sizes and how do they vary across populations, designs, or conditions?
If any of these are absent from your draft, add the relevant evidence before finalising.

Required sections (these must appear in this order at the end of the report body):

### Synthesis and Implications
Cross-cutting themes across all sub-questions. Practical implications for schools and practitioners.

### Limitations and Research Gaps
Methodological weaknesses: small samples, short durations, lack of randomisation, non-representative populations, publication bias, equity gaps.

---

## Body of Evidence Maturity: [MATURE / LIMITED / EMERGING / EARLY]
Justification: [2-3 sentence holistic assessment across rigor, coverage, and equity dimensions]
"""


# ---------------------------------------------------------------------------
# Pass 2 — Citation normalization
# Takes the raw report + source pool and converts all paper references to
# (First_Author_Last_Name, Year) format for programmatic [N] injection.
# ---------------------------------------------------------------------------

citation_normalize_prompt = """You are a citation resolver. Your task is to replace every <<...>> citation tag in the report with the correct [N] number from the numbered source pool below.

Numbered source pool:
<SourcePool>
{paper_tier_reference}
</SourcePool>

Rules:
- Every <<Author, Year>> or <<Title, Year>> tag must be replaced with [N] where N is the number of the matching source in the pool above.
- Match by author last name + year first. If no author match, try title keywords + year.
- If you cannot confidently match a <<...>> tag to a source, replace it with the tag contents in plain text: e.g. <<Wang, 2024>> → (Wang, 2024).
- Do NOT add new citations that aren't already tagged in the report.
- Do NOT change any other text — preserve the report structure, statistics, and wording exactly.
- Do NOT write a References or Bibliography section.
- Return the full report text with all <<...>> tags resolved. Nothing else.

Report:
{report}
"""
