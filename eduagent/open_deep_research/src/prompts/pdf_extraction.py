"""Prompt for extracting structured metadata and findings from an academic paper PDF."""

pdf_extraction_prompt = """You are extracting structured information from an academic paper for a knowledge graph about AI in education research. Be precise. Use "not_reported" for any field where the information is genuinely absent.

Research sub-question this paper was retrieved for: {research_topic}

Paper text:
{pdf_text}

---

## Instructions

### Metadata
Extract title, DOI, year, venue (journal or conference name), population studied (e.g. "Elementary (PreK-5th)", "High School", "Undergraduate", "Adult"), user type (Student / Educator / Administrator / Parent / School / Community), and study design.

Study design must be exactly one of:
- Randomized Controlled Trial (RCT)
- Quasi-Experimental Design (QED)
- Meta-Analysis / Systematic Review
- Observational / Correlational
- Mixed-Methods
- Qualitative

### Extended Summary
Write 2–4 paragraphs covering: (1) what problem or question the paper addresses, (2) the intervention or approach studied, (3) the population and context, (4) the main conclusions. This should be detailed enough that a reader understands the paper without reading it.

### Outcome Assignments
Review the paper against these 9 outcome categories:
1. Academic — Literacy (reading, writing)
2. Academic — Language Fluency (speaking, listening)
3. Academic — Mathematical Numeracy
4. Academic — Scientific Reasoning
5. Academic — Other (history, arts, vocational, etc.)
6. Social-Emotional Skills (motivation, engagement, self-regulation, persistence)
7. Durable Skills (critical thinking, metacognition, collaboration, time management)
8. Operational Efficiency (productivity, task efficiency, teacher workload)
9. Systemic / Institutional Impact (policy, governance, institutional outcomes)

For each outcome the paper **substantively studies** (not just mentions):
- Assign a confidence score (0.0–1.0): how directly and centrally does this paper study this outcome?
  - 0.9–1.0: primary focus with empirical findings reported
  - 0.7–0.8: clearly studied, with some quantitative or qualitative evidence
  - 0.5–0.6: studied but secondary or limited evidence
  - Below 0.5: tangential mention only — do NOT include
- Only return outcome assignments with confidence ≥ 0.5 and provide a brief justification on the outcome area and confidence scoring
- For each included outcome, extract the empirical finding:
  - direction: Positive / Negative / No Effect / Mixed
  - finding_summary: 2–3 sentences. Include effect sizes (e.g. d=0.42), sample sizes (n=), and specific outcome measures where reported.
  - measure: what instrument or metric was used
  - study_size, effect_size, confidence_interval, std_deviation: exact values or "not_reported"

If multiple outcomes share the same underlying finding (same study, same measures), you may report the same finding data for each — do not invent separate findings.

### Evidence Quality and Impact Tiers (K-12 Evidence Framework)

Assign one tier each for **quality_tier** and **impact_tier**. Use exactly one of: blue, green, yellow, red.

**Quality tier** — assess across three dimensions: Research Design, Credibility, and Relevance:

🔵 **blue (Highest Quality)**:
- Research Design: Meta-analysis OR well-designed RCT with appropriate method, sufficient power and duration
- Credibility (ALL 3): Credible third-party evaluator + Peer-reviewed/reputable publication + Addresses participant context and researcher positionality
- Relevance (ALL 4): Disaggregated by race/income + Representative of priority populations (Black, Latino, low-income) + Timely (within 10 years) + Relevant context (U.S. public schools)

🟢 **green (Moderate to Strong)**:
- Research Design: Well-designed quasi-experimental study (QED) with treatment/comparison groups or OR meta-analysis/RCT with some concerns (small sample, short duration, weak generalizability)
- Credibility (2 of 3): Credible third-party + Peer reviewed/reputable + Acknowledges positionality/context
- Relevance (3 of 4): Representative of priority populations + Prioritizes outcomes for priority populations + Timely + Relevant context

🟡 **yellow (Limited or Weaker)**:
- Research Design: Correlational or qualitative study
- Credibility (1 of 3): Credible third-party OR Peer reviewed/reputable OR Considers context/positionality
- Relevance (2 of 4): Meets 2 of the 4 relevance criteria above

🔴 **red (Low or Unacceptable)**:
- Research Design: Does not meet quality standards — no clear methodology, no peer review, purely opinion/grey literature, or insufficient power
- Credibility (0 of 3): Meets none of the credibility criteria
- Relevance (≤1 of 4): Meets 1 or fewer relevance criteria

**Impact tier** — assess effect size and population focus:

🔵 **blue**: Medium or large impact on general AND priority populations (Black, Latino, low-income)
- Effect size ≥ 0.20 for priority populations

🟢 **green**: Modest impact on priority populations OR medium/large impact on general population
- Effect size 0.05–0.20 for priority populations OR ≥ 0.20 for general population

🟡 **yellow**: Modest or unclear impact on general population, not priority populations
- Effect size < 0.05 for general population, or mixed/inconclusive effects

🔴 **red**: No impact or negative impact
- No measurable effect, harmful effects, or effect sizes not reported with no other evidence of impact

"""
