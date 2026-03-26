"""Prompt for generating the final academic-quality research report from all sub-researcher findings."""

final_report_generation_prompt = """Based on all the research conducted, create a comprehensive, well-structured answer to the overall research brief:
<Research Brief>
{research_brief}
</Research Brief>

For more context, here is all of the messages so far. Focus on the research brief above, but consider these messages as well for more context.
<Messages>
{messages}
</Messages>

CRITICAL: Make sure the answer is written in the same language as the human messages!
For example, if the user's messages are in English, then MAKE SURE you write your response in English. If the user's messages are in Chinese, then MAKE SURE you write your entire response in Chinese.
This is critical. The user will only understand the answer if it is written in the same language as their input message.

Today's date is {date}.

Here are the findings from the research that you conducted:
<Findings>
{findings}
</Findings>

Please create a detailed, academic-quality research report answering the overall research brief. This is a deep research report — users expect rigor, specificity, and comprehensive coverage equivalent to a professional literature review.

**Report Standards:**
- Named studies with specific evidence characteristics wherever found: effect sizes, confidence intervals, sample sizes (n=), study design, and duration
- Inline citations [N] throughout — do not save citations only for the Sources section
- Precise language: "effect size d=0.42 (n=312, RCT)" not "modest improvements"
- Explicitly acknowledge gaps and limitations — do not overstate confidence
- Do NOT use self-referential language or meta-commentary. Write the report directly.

**CRITICAL — RCT vs. Meta-Analysis distinction:**
These are fundamentally different types of evidence. NEVER conflate them:
- **RCT (Randomized Controlled Trial)**: Direct causal evidence. An experiment where participants were randomly assigned. Can claim causation. Label as: `(RCT, n=X)`.
- **Meta-Analysis / Systematic Review**: A synthesis of multiple studies. Its quality depends entirely on the quality of the underlying studies it includes. Can claim "the literature suggests" or "pooled evidence shows" — NOT direct causation. Label as: `(meta-analysis of N studies)`.
- **Observational / Survey**: Correlation only, no causal claim. Label as: `(survey, n=X)` or `(observational)`.

When reporting findings, always state the evidence type first. Example: "One RCT (Bastani et al., n=1,000) found..." NOT "Research shows...". If the only evidence is a meta-analysis, say so and note what study designs it pooled.

**CRITICAL — Source Grounding:**
- You MUST ONLY cite sources that appear in the `### SOURCES USED` blocks within the `<Findings>` above.
- Do NOT invent, fabricate, or draw on training-knowledge citations. If a study is not in the findings, it does not exist for this report.
- If the retrieved evidence is thin, say so explicitly — do not pad with invented studies.
- Every [N] citation in the text must correspond to a real URL from the SOURCES USED blocks.

<HallucinationGuard>
CRITICAL — read before writing a single word:
- You MAY ONLY cite sources that appear verbatim in the `### SOURCES USED` blocks within `<Findings>`. If a study is not listed there, it does not exist for this report.
- Do NOT invent author names, journal names, publication years, sample sizes, effect sizes, confidence intervals, or p-values. If a number is not explicitly stated in the findings, write "not reported" — never estimate or interpolate.
- Do NOT blend statistics from different studies (e.g., do not attach Study A's effect size to Study B's population).
- Do NOT use your training-knowledge to fill gaps. If the retrieved evidence is thin on a sub-question, say so explicitly rather than supplementing from memory.
- Every [N] citation in the text must map to a real URL in the Bibliography. No orphan citations, no invented DOIs.
- If you catch yourself about to write a plausible-sounding statistic that isn't in the findings, stop and write "evidence not retrieved" instead.
</HallucinationGuard>

**Source Budget: include at most {max_sources} citations in the final Bibliography.** Prioritize by evidence quality: RCTs and meta-analyses of RCTs first, then quasi-experimental, then observational/survey. If you have more sources than the budget allows, drop the weakest ones (lowest evidence rung, least relevant to the research brief). Never fabricate sources to fill the budget.

**Output this exact three-section structure. Do not add any text outside these three sections.**

---

## Executive Summary

Write 1 focused, clear, and detailed nparagraph tshat state the central thesis and main argument of the report. This is the practitioner-facing summary — directly answer the research brief, cite the strongest supporting evidence inline [N], state the overall confidence level, and flag the single most important caveat or limitation. A busy decision-maker should be able to read only this section and walk away with an accurate picture.

One table with the list of claims/findings and the associated papers they are coming from.
---

## Research Report

The research was conducted across multiple focused sub-questions. Organize this section with one dedicated subsection per sub-question investigated, followed by cross-cutting synthesis sections.

**Step 1 — Identify the sub-questions**: Read the `<Findings>` and identify each distinct research sub-question that was investigated (look for researcher notes, each covering a specific angle). Create one `###` subsection per sub-question.

**Step 2 — Write each sub-question section** following this structure:
- **Sub-question**: State the exact sub-question investigated (1 sentence)
- **Evidence found**: What RCTs, meta-analyses, and observational studies were retrieved — always label evidence type explicitly (RCT / meta-analysis / survey / observational). Lead with RCTs and causal evidence. Name individual studies with design, sample size, and effect size where reported.
- **Gaps**: What evidence is missing or insufficient for this sub-question specifically

Example sub-question section format:
### [Sub-question topic, e.g. "Effectiveness of GenAI for Mathematics Achievement"]
**Sub-question investigated:** [exact question]

[Evidence paragraphs — RCTs first, then meta-analyses, then observational. Always label: "(RCT, n=X)", "(meta-analysis, N studies)", "(survey, n=X)"]

**Evidence gaps for this sub-question:** [what's missing]

---

**Step 3 — Cross-cutting synthesis sections** (after all sub-question sections):

### Demographic and Contextual Moderators
Factors that moderate effectiveness across all sub-questions: prior achievement, SES, race/ethnicity, ELL status, disability, school setting, implementation fidelity, teacher involvement. Report disaggregated findings where available. Explicitly state when subgroup data is absent.

### Limitations and Research Gaps
Methodological weaknesses across the full evidence base: small samples, short durations, lack of randomization, non-representative populations, publication bias, outcome gaps. Be specific — name the sub-questions with weakest evidence.

### Recommendations
Practitioner priorities, required implementation conditions, and most urgent research gaps — tied back to specific sub-questions where evidence is actionable.

---

## Bibliography

List every source cited in this report, numbered sequentially. Only include sources from `### SOURCES USED` blocks in the findings.

<PreScoredTiers>
The following sources have been pre-scored by the evidence pipeline using full-text extraction. Use these exact quality and impact tiers — do NOT override or re-derive them. For sources not listed here, derive the tier yourself using the rubric below.

{paper_tier_reference}
</PreScoredTiers>

**K-12 Evidence Framework rubric (for sources not pre-scored above):**

Quality tier — Research Design + Credibility + Relevance:
- 🔵 Blue: RCT or meta-analysis; credible third-party + peer-reviewed + addresses positionality; disaggregated by race/income + priority populations represented + timely (≤10 yrs) + U.S. public school context
- 🟢 Green: Quasi-experimental with comparison group; 2 of 3 credibility; 3 of 4 relevance
- 🟡 Yellow: Correlational/qualitative or RCT with methodological concerns; 1 of 3 credibility; 2 of 4 relevance
- 🔴 Red: No clear methodology, not peer-reviewed, purely opinion; 0 credibility, ≤1 relevance

Impact tier — Effect size + priority population focus:
- 🔵 Blue: Effect size ≥0.20 for priority populations (Black, Latino, low-income) or general populations
- 🟢 Green: Effect size 0.05–0.20 for priority populations OR ≥0.20 general population
- 🟡 Yellow: Effect size <0.05 general population, or mixed/inconclusive
- 🔴 Red: No measurable effect or harmful effects

**Format each entry exactly as:**
[N] Author(s) (Year). *Title*. Publication/Source.
URL: <url>
Quality: 🔵/🟢/🟡/🔴 [one sentence justification]
Impact: 🔵/🟢/🟡/🔴 [one sentence justification]

After all entries:

### Body of Evidence Maturity: [MATURE 🔵 / LIMITED 🟢 / EMERGING 🟡 / EARLY 🔴]
**Justification**: [2–3 sentence holistic assessment across rigor, coverage, and equity dimensions]

REMEMBER: Write in the same language as the human messages.
"""
