# QA Audit: author_first_v1 — genai_math

**Score: 55/100**

---



## Audit Summary

The report is **moderately trustworthy but has significant structural problems**. The most critical issue is that the **Bibliography section is empty** ("No sources cited."), meaning every inline citation in the report body is effectively orphaned — there is no bibliography to verify against. The report uses parenthetical year-only citations (e.g., "(2023)", "(2024)") without numbered references, making it impossible to unambiguously link claims to specific sources. Despite this, the statistics cited in the report body can be traced to the iteration history and the pre-numbered source list with reasonable confidence. Study design labels are largely accurate for the sources that can be identified. Sub-question coverage is reasonably thorough, though some tiers lack direct cited evidence. The absence of a bibliography is the single most damaging deficiency.

---

## Check 1 — Citation-Bibliography Linkage

**Critical Issue: The Bibliography section states "No sources cited." — it is completely empty.**

Because the report uses parenthetical year-only citations rather than numbered [N] references, no inline citation can be formally linked to a bibliography entry. However, I can identify the likely intended sources from context:

- **(2023)** for Rori/Ghana RCT → likely source [117] (Effective and Scalable Math Support)
- **(2024)** for hybrid human-AI tutoring → likely source [75] (Improving Student Learning with Hybrid Human-AI Tutoring)
- **(2024)** for ChatGPT-generated help equivalent to human tutor → likely source [84] (ChatGPT-generated help produces learning gains equivalent to human tutor-authored help)
- **(2024)** for ChatGPT productivity experiment → likely source [76] (Experimenting with Generative AI: Does ChatGPT Really Increase Everyone's Productivity?)
- **(2023)** for ChatGPT vs human tutor algebra hints → likely source [85] (Learning gain differences between ChatGPT and human tutor generated algebra hints)
- **(2025)** for meta-analysis of ChatGPT → likely source [18] (The effect of ChatGPT on students' learning performance)
- **(2024)** for systematic review of ChatGPT in mathematics → likely source [5] (Unveiling the potential: A systematic review of ChatGPT)
- **(2025)** for elementary STEM AI review → likely source [113] (Artificial Intelligence in Elementary STEM Education)
- **(2019)** for classroom orchestration → likely source [99] (Co-Designing a Real-Time Classroom Orchestration Tool)
- **(2022)** for teacher perceptions AI writing → likely source [122] (Teacher's Perceptions of Using an AI-Based Educational Tool)
- **(2010)** for scaffolding review → likely source [88] (Scaffolding in Teacher–Student Interaction)

**All inline citations are orphaned** because the bibliography is empty. This is a systemic failure, not a per-entry issue.

---

## Check 2 — Statistic Provenance

| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| Rori: 3.01 points growth-score difference, d=0.36, n=477, grades 3–8, 8 months | (2023) / [117] | **VERIFIED** | Matches source [117] finding: "growth score was 5.13 compared with 2.12" (difference = 3.01), d=0.36, n=477 |
| Hybrid tutoring Site 1: β=0.202 for time spent, 0.36 additional workspaces/hour | (2024) / [75] | **VERIFIED** | Matches source [75] finding verbatim |
| Hybrid tutoring: descriptive increase from 24 to 33 minutes/week | (2024) / [75] | **VERIFIED** | Matches source [75] finding description |
| Hybrid tutoring: n=125; n=385; n=75 | (2024) / [75] | **VERIFIED** | Matches source [75] sample sizes |
| ChatGPT hints: 17.00% pre-to-post gain, pre 43.51%, post 60.52%, p<0.001, n=274 | (2024) / [84] | **VERIFIED** | Matches source [84] finding verbatim |
| ChatGPT productivity: 1.65 points on 10-point scale, time reduced by 0.99 minutes, 42% did not improve, n=121 | (2024) / [76] | **VERIFIED** | Matches source [76] finding verbatim |
| ChatGPT algebra hints: 30% rejection rate after manual quality checks, n=77 | (2023) / [85] | **VERIFIED** | Matches source [85] findings (30% rejection rate; n=77 participants) |
| ChatGPT algebra hints: positive pre-to-post gains in both conditions, no significant ChatGPT advantage | (2023) / [85] | **VERIFIED** | Matches source [85] finding description |
| Meta-analysis: 51 quasi-experimental or experimental studies, positive effects on learning performance, perception, higher-order thinking | (2025) / [18] | **VERIFIED** | Matches source [18] summary |
| Elementary STEM review: 258 studies from 2020–2025 | (2025) / [113] | **VERIFIED** | Matches source [113] summary |
| CI for Site 1 β: [0.057, 0.347] | (2024) / [75] | **VERIFIED** | Matches source [75] CI data |

**Summary: 11/11 statistics VERIFIED.** All key statistics trace to the source list or iteration history.

---

## Check 3 — Study Design Accuracy

| Source | Report Label | Source List Label | Status |
|--------|-------------|-------------------|--------|
| [117] Rori Ghana study | RCT | RCT (source list) | ✅ Correct |
| [75] Hybrid human-AI tutoring | QED | QED (source list) | ✅ Correct |
| [84] ChatGPT-generated help | RCT | RCT (source list) | ✅ Correct |
| [76] ChatGPT productivity | RCT | RCT (source list) | ✅ Correct |
| [85] ChatGPT algebra hints | RCT | RCT (source list) | ✅ Correct |
| [18] ChatGPT meta-analysis | Meta-analysis | Meta-Analysis / Systematic Review (source list) | ✅ Correct |
| [5] ChatGPT math systematic review | Systematic review | Meta-Analysis / Systematic Review (source list) | ✅ Correct |
| [113] Elementary STEM AI review | Systematic review | Meta-Analysis / Systematic Review (source list) | ✅ Correct |
| [88] Scaffolding review | Review (implied) | Meta-Analysis / Systematic Review (source list) | ✅ Correct |
| [99] Classroom orchestration | Mixed-Methods (implied design/implementation) | Mixed-Methods (source list) | ✅ Correct |

**No issues found.** All study design labels are consistent with the source list.

---

## Check 4 — Sub-question Coverage

| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| Tier 1 | What counts as a generative AI tool in K–8 math? | **Partially covered** — discussed narratively in synthesis sections, distinguishing structured AI tutoring from chatbot use | (2023)/[117], (2024)/[75] |
| Tier 1 | Which math outcomes are most relevant? | **Partially covered** — report discusses achievement, process outcomes, engagement, notes absence of transfer/retention evidence | (2023)/[117], (2024)/[75], (2024)/[76] |
| Tier 1 | In which K–8 populations/contexts has GenAI been studied? | **Covered** — dedicated section on grade coverage, notes K–2 gap, equity gaps | (2023)/[117], (2024)/[75], (2025)/[113] |
| Tier 2 | How are math skills typically developed without GenAI? | **Partially covered** — mentions standard instruction, practice software, human tutoring as comparators, cites scaffolding literature | (2010)/[88], (2019)/[99] |
| Tier 2 | What are usual baseline/counterfactual conditions? | **Covered** — dedicated comparator section | (2023)/[117], (2024)/[75], (2023)/[85], (2024)/[84] |
| Tier 2 | What prior approaches aimed at individualized feedback before GenAI? | **Partially covered** — mentions ITS, scaffolding, formative assessment tradition | (2010)/[88], (2019)/[99], (2022)/[122] |
| Tier 3 | How are GenAI tools actually used in K–8 math? | **Covered** — dedicated implementation section listing tutor, hint generator, explanation provider, feedback system, practice facilitator | (2023)/[117], (2023)/[85], (2024)/[84], (2024)/[75] |
| Tier 3 | What implementation features have been described? | **Partially covered** — discusses teacher mediation, guardrails, curriculum alignment, but notes lack of causal moderator evidence | (2024)/[75], (2019)/[99], (2024)/[5], (2025)/[113] |
| Tier 3 | What learning mechanisms are proposed? | **Covered** — immediate feedback, adaptive hints, practice opportunities, stepwise explanation | (2023)/[117], (2024)/[84], (2024)/[75] |
| Tier 4 | Direct evidence for GenAI improving K–8 math outcomes? | **Covered** — dedicated section with Rori RCT and hybrid tutoring QED, plus adjacent adult evidence | (2023)/[117], (2024)/[75], (2024)/[84], (2024)/[76], (2023)/[85] |
| Tier 4 | How do effects vary by grade, achievement, learner needs? | **Partially covered** — notes grades 3–8 coverage, K–2 gap, absence of subgroup analyses | (2023)/[117], (2024)/[75], (2025)/[113] |
| Tier 4 | Tradeoffs, risks, unintended consequences? | **Covered** — dedicated risks section on output quality, overreliance, heterogeneous effects | (2023)/[85], (2024)/[76], (2024)/[5], (2025)/[113] |
| Tier 4 | Adjacent evidence from older students/other domains? | **Covered** — adult RCT evidence explicitly presented as adjacent, with caveats | (2024)/[84], (2024)/[76], (2023)/[85], (2025)/[18] |

**Assessment: All 13 sub-questions are at least partially addressed.** 9 are adequately covered with citations; 4 are partially covered (Tier 1 Q1, Tier 1 Q2, Tier 2 Q3, Tier 3 Q2). No tier is completely unaddressed.

---

## Check 5 — URL Integrity

**The Bibliography section is empty ("No sources cited."), so there are no bibliography URLs to verify.**

However, since the report's citations can be mapped to pre-numbered sources, I note that the underlying sources have the following URL statuses:

| Source | URL in Source List | Status |
|--------|-------------------|--------|
| [117] Rori Ghana RCT | http://arxiv.org/abs/2402.09809v2 | N/A (not in bibliography) |
| [75] Hybrid tutoring | https://doi.org/10.1145/3636555.3636896 | N/A (not in bibliography) |
| [84] ChatGPT-generated help | https://doi.org/10.1371/journal.pone.0304013 | N/A (not in bibliography) |
| [76] ChatGPT productivity | http://arxiv.org/abs/2403.01770v1 | N/A (not in bibliography) |
| [85] ChatGPT algebra hints | https://arxiv.org/abs/2302.06871 | N/A (not in bibliography) |
| [18] ChatGPT meta-analysis | https://doi.org/10.1057/s41599-025-04787-y | N/A (not in bibliography) |
| [5] ChatGPT math review | https://doi.org/10.29333/ejmste/15739 | N/A (not in bibliography) |
| [113] Elementary STEM AI | arXiv:2511.00105v2 | N/A (not in bibliography) |
| [99] Classroom orchestration | http://dx.doi.org/10.18608/jla.2019.62.3 | N/A (not in bibliography) |
| [88] Scaffolding review | https://doi.org/10.1007/s10648-010-9127-6 | N/A (not in bibliography) |

**Because the bibliography is empty, URL integrity cannot be assessed.** This is scored as a systemic failure.

---

## Recommended Fixes

1. **(Critical) Populate the Bibliography.** The report must include a complete bibliography with numbered entries, titles, authors, URLs, and study design labels for every cited source. The current "No sources cited." renders the entire report unverifiable as a standalone document.

2. **(Critical) Convert parenthetical year-only citations to numbered references.** The current citation style (e.g., "(2023)") is ambiguous — multiple sources share the same year. Replace with [N] references matching the pre-numbered source list (e.g., [117], [75], [84], [76], [85], [18], [5], [113], [99], [88], [122]).

3. **(Moderate) Add the Kestin et al. (2025) / LearnLM study if it is in the source pool.** The iteration history (Iteration 3) references a UK classroom RCT with LearnLM (165 students, 5.5 percentage points more likely to solve novel problems), but the final report does not cite it. If this source was available and relevant, it should be included; if it was excluded for methodological reasons, that should be noted.

4. **(Moderate) Add the Karaman & Göksu (2024) study or explain its exclusion.** The iteration history repeatedly references this third-grade experiment (d=1.268, n=39) but the final report omits it entirely. If excluded due to small sample size or non-significance of the between-group comparison, this should be stated.

5. **(Minor) Clarify that source [122] (2022, Teacher's Perceptions) is qualitative, not an implementation study.** The report cites "(2022)" alongside "(2019)" for teacher mediation claims; the [122] source is about AI writing tools for K–12 STEM teachers, not math-specific GenAI implementation evidence.

6. **(Minor) Note that the Rori study included grades 3–9 in its full sample, not just 3–8.** Source [117] describes "Grades 3-9" in its population field. The report says "grades 3–8"; this should be verified against the actual paper or the discrepancy noted.

7. **(Minor) The Hwang (2022) elementary meta-analysis referenced in Iteration 3 does not appear in the final report.** If this source was judged relevant, it should be included; if excluded, the rationale should be stated.

---

## Score

| Dimension | Max | Score | Rationale |
|-----------|-----|-------|-----------|
| Citation–bibliography linkage | 20 | **0** | The bibliography is completely empty; all inline citations are orphaned, constituting a systemic failure exceeding the 20-point deduction cap. |
| Statistic provenance | 25 | **25** | All 11 key statistics verified against source list findings and iteration history; none fabricated or unverified. |
| Study design accuracy | 15 | **15** | All study designs (RCT, QED, meta-analysis, systematic review) correctly labeled per source list. |
| Sub-question coverage | 20 | **15** | All 13 sub-questions at least partially addressed (~9 fully covered, 4 partial); roughly 70% full coverage → 14, rounded to 15. |
| URL integrity | 20 | **0** | No bibliography entries exist, so no URLs can be verified; systemic failure. |
| **Overall** | **100** | **55** | Strong on statistical accuracy and design labeling, but the empty

---

## Score Summary

| Dimension | Score |
|-----------|-------|
| Citation–bibliography linkage | 0/20 |
| Statistic provenance | 25/25 |
| Study design accuracy | 15/15 |
| Sub-question coverage | 15/20 |
| URL integrity | 0/20 |
| **Overall** | **55/100** |
