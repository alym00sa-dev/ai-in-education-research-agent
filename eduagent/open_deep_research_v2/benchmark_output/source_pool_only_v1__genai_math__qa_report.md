# QA Audit: source_pool_only_v1 — genai_math

**Score: 85/100**

---



## Audit Summary

The report is moderately trustworthy but contains several issues that undermine its reliability. The most critical problems are: (1) multiple inline citations reference studies by name/description rather than by bibliography number, making provenance tracking difficult and introducing inconsistency; (2) several specific statistics cited in the report cannot be fully verified against the iteration history or source list, particularly the "~2 SD difference" claim and the "n=585" sample size for the hybrid tutoring study; (3) the bibliography contains orphan entries that are never cited inline; and (4) some URLs in the bibliography have minor discrepancies with the source list. The report's narrative is generally consistent with the iteration history, but the informal citation style (mixing bracketed numbers with parenthetical name/year references not linked to bibliography entries) creates ambiguity about which specific sources support which claims.

---

## Check 1 — Citation-Bibliography Linkage

**Inline citations using [N] format found in the report body:**
- [3] — Present in Bibliography ✓
- [4] — Present in Bibliography ✓
- [10] — Present in Bibliography ✓
- [14] — Present in Bibliography ✓
- [15] — Present in Bibliography ✓
- [24] — Present in Bibliography ✓
- [38] — Present in Bibliography ✓
- [43] — Present in Bibliography ✓

**Inline citations using name/year format (not linked to bibliography numbers):**
- "Tutor CoPilot, 2025" — corresponds to [10] but cited inconsistently by name in the text
- "AI tutoring support, 2025" / "AI tutoring can safely and effectively support students, 2025" — this study is NOT in the bibliography table (it corresponds to source profile #97 from academic-DB or supplementary source [233]). **MISSING from bibliography.**
- "Improving Student Learning with Hybrid Human-AI Tutoring, 2024" — corresponds to [24] but cited inconsistently
- "Personalized Recommendations in EdTech, 2022" — corresponds to [15] but cited inconsistently
- "Empowering ChatGPT with guidance mechanism, 2024" — corresponds to [2] but cited inconsistently
- "AI-Powered Assessments in Mathematics Education, 2025" — corresponds to [3] but cited inconsistently
- "The role of large language models in personalized learning (2025)" — corresponds to [4] but cited inconsistently

**Orphan bibliography entries (in bibliography but not cited inline):**
- [2] (Empowering ChatGPT with guidance mechanism) — Only cited by name in text, never as [2]. **Orphan by number.**

**Issues found:**
1. The "AI tutoring can safely and effectively support students (2025)" study (LearnLM RCT) is cited repeatedly inline but has NO entry in the bibliography table. This is a significant omission.
2. Bibliography entry [2] is never cited as [2] in the report body (only referenced by title/year), making it a technical orphan.
3. The report mixes [N] citation style with parenthetical name/year style inconsistently, creating confusion about which bibliography entries support which claims.

---

## Check 2 — Statistic Provenance

| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| 4 percentage point increase in math numeracy outcomes (Tutor CoPilot, n=1,800) | [10] | VERIFIED | Matches source profile finding: "4 percentage point increase overall" |
| 9 percentage points for novice/low-rated tutors (Tutor CoPilot) | [10] | VERIFIED | Matches source profile finding: "9 p.p. for low-rated tutors" |
| n=1,800 K-12 students, grades 3-8 (Tutor CoPilot) | [10] | VERIFIED | Matches source profile: "n=1800 students, 900 tutors" |
| 93% success rate correcting math mistakes (LearnLM) | AI tutoring study | VERIFIED | Matches source profile finding: "93.0% success in correction" |
| Transfer effect +0.055 (LearnLM) | AI tutoring study | VERIFIED | Matches source profile finding: "effect=+0.055" |
| n=165 UK secondary students (LearnLM) | AI tutoring study | VERIFIED | Matches source profile: "n=165" |
| n=585 for hybrid human-AI tutoring study | [24] | FABRICATED | Source profile reports n=125, n=385, n=75 across three sites (total=585), but the report states "QED, n=585" as if it's one study with 585 participants. The total is technically 585, but this is a composite across three separate studies, not one study with n=585. Misleading but arithmetically correct. Reclassifying as UNVERIFIED — the composite number is not stated in the source. |
| 60% increase in story engagement (Personalized Recommendations) | [15] | VERIFIED | Matches source profile: "total story engagement increased by 60%" |
| n=7,750 (Personalized Recommendations) | [15] | VERIFIED | Matches source profile: "n=7750 users randomized" |
| ~2 SD difference in pedagogical strategy usage (Tutor CoPilot, 550,000+ messages) | [10] | VERIFIED | Source profile states "~2 standard deviations difference in usage frequency" and "550,000+ messages" |
| n=125, RCT (AI Instructional Agent) | [14] | VERIFIED | Matches source profile: "n=125" |
| Tutor CoPilot costs ~$20/tutor annually | [10] | VERIFIED | Matches source profile finding about cost |
| g = 0.42 average effect size from LLAMA LIMA meta-analysis | Iteration history | VERIFIED | Found in iteration 1 and iteration 2 executive summaries: "g = 0.42" |
| 5.5 percentage points higher likelihood (LearnLM) | Iteration history | VERIFIED | Iteration 2 states "5.5 percentage points more likely to correctly solve novel problems" |
| 82.4% tutors found AI improved fluidity | AI tutoring study | VERIFIED | Source profile states "82.4% tutors" |

**Summary:** 13 VERIFIED, 1 UNVERIFIED (n=585 composite). No clearly FABRICATED statistics, though the n=585 is misleadingly presented.

---

## Check 3 — Study Design Accuracy

| Study | Report Label | Source Label | Status |
|-------|-------------|-------------|--------|
| [2] Empowering ChatGPT | RCT (implied) | RCT (academic-DB) | ✓ OK |
| [3] AI-Powered Assessments | Systematic Review | Meta-Analysis / Systematic Review (academic-DB) | ✓ OK |
| [4] Role of LLMs in personalized learning | Systematic Review | Meta-Analysis / Systematic Review (academic-DB) | ✓ OK |
| [10] Tutor CoPilot | RCT | RCT (academic-DB) | ✓ OK |
| [14] AI Instructional Agent | RCT | RCT (academic-DB) | ✓ OK |
| [15] Personalized Recommendations in EdTech | RCT | RCT (academic-DB) | ✓ OK |
| [24] Improving Student Learning with Hybrid Human-AI Tutoring | QED | QED (academic-DB) | ✓ OK |
| [38] Integrating AI in education | Systematic Review (implied) | Meta-Analysis / Systematic Review (academic-DB) | ✓ OK |
| [43] ARCHED | Mixed-Methods (implied) | Mixed-Methods (academic-DB) | ✓ OK |
| AI tutoring (LearnLM) — not in bibliography | RCT | RCT (academic-DB source profile) | ✓ OK |

**No issues found** with study design labeling.

---

## Check 4 — Sub-question Coverage

| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| 1 | What are generative AI tools and how are they defined in K-8 math education? | Covered | [4], [3] |
| 1 | Which specific math skills and outcomes are targeted? | Covered | [10], [24], [4] |
| 1 | What are the educational contexts for implementation? | Partially covered | [24], [10], Empowering ChatGPT |
| 2 | How are math skills typically developed through traditional methods? | Partially covered | [3], [10] — general discussion, limited specific citations |
| 2 | What existing digital/non-digital interventions support math learning? | Partially covered | [3], [10] — mentioned but no direct comparative study cited |
| 2 | What are baseline instructional practices for comparison? | Partially covered | General discussion, limited specific citations |
| 3 | How are generative AI tools integrated into K-8 math instruction? | Covered | [10], LearnLM study, [24] |
| 3 | What delivery models and interaction modes are used? | Covered | [10], LearnLM study, Empowering ChatGPT |
| 3 | What cognitive and motivational mechanisms are proposed? | Partially covered | [2], [15] — indirect evidence, acknowledged as underexplored |
| 4 | Comparative effectiveness vs standard instruction? | Partially covered | [10], LearnLM study — limited to few studies |
| 4 | Impact variation across subpopulations? | Minimally covered | [10], [24] — acknowledged as gap, no specific subgroup data cited |
| 4 | Trade-offs, limitations, challenges? | Covered | General synthesis, multiple citations |
| 4 | Comparison to alternative digital/human interventions? | Minimally covered | Acknowledged as gap with minimal evidence |

**Flags:**
- Tier 2 sub-questions are addressed only with general discussion and limited specific cited evidence.
- Tier 4 subpopulation variation sub-question is flagged as having minimal coverage with no specific subgroup analysis citations.
- Tier 4 comparison to alternative interventions has minimal specific evidence beyond general synthesis statements.

---

## Check 5 — URL Integrity

| # | Source | Report URL | Source List URL | Status |
|---|--------|-----------|----------------|--------|
| 2 | Empowering ChatGPT | https://doi.org/10.1186/s41239-024-00447-4 | https://doi.org/10.1186/s41239-024-00447-4 | OK |
| 3 | AI-Powered Assessments | not_reported | not_reported | OK |
| 4 | Role of LLMs | https://doi.org/10.1007/s43621-025-01094-z | https://doi.org/10.1007/s43621-025-01094-z | OK |
| 10 | Tutor CoPilot | https://arxiv.org/abs/2410.03017 | https://arxiv.org/abs/2410.03017 | OK |
| 14 | AI Instructional Agent | https://arxiv.org/abs/2505.22526v1 | https://arxiv.org/abs/2505.22526 | OK (minor version suffix difference, same paper) |
| 15 | Personalized Recommendations | https://arxiv.org/abs/2208.13940v2 | https://arxiv.org/abs/2208.13940v2 | OK |
| 24 | Hybrid Human-AI Tutoring | https://doi.org/10.1145/3636555.3636896 | https://doi.org/10.1145/3636555.3636896 | OK |
| 38 | Integrating AI in education | https://doi.org/10.30574/msarr.2024.10.2.0039 | https://doi.org/10.30574/msarr.2024.10.2.0039 | OK |
| 43 | ARCHED | https://arxiv.org/abs/2503.08931 | https://arxiv.org/abs/2503.08931 | OK |

**No issues found.**

---

## Recommended Fixes

1. **[CRITICAL] Add the LearnLM/AI tutoring study to the bibliography.** The study "AI tutoring can safely and effectively support students: An exploratory RCT in UK classrooms (2025)" is cited multiple times in the report body but has no entry in the bibliography table. It should be added (it appears as supplementary source [233] or academic-DB source profile with URL https://goo.gle/LearnLM-Nov25).

2. **[HIGH] Standardize citation format.** The report inconsistently uses [N] bracketed citations and parenthetical name/year citations. All references should use the [N] format consistently, linking to the bibliography table.

3. **[HIGH] Correct or clarify n=585 for the hybrid tutoring study [24].** The source reports three separate studies with n=125, n=385, and n=75. If citing a composite, this should be stated as "total n=585 across three sites" rather than implying a single study with 585 participants.

4. **[MODERATE] Cite [2] by its number.** The Empowering ChatGPT study is referenced only by name/year but has a bibliography entry as [2]. Add the [2] citation marker where it is discussed in the text.

5. **[MODERATE] Add the LLAMA LIMA meta-analysis to the bibliography.** The report's executive summary and Tier 4 section reference the g=0.42 effect size from Strohmaier et al. (2026) repeatedly, but this study (supplementary source [142]) is not in the bibliography.

6. **[MODERATE] Add the Bastani et al. (2024/2025) study to the bibliography.** The iteration history repeatedly references this high school field experiment about generative AI without guardrails harming learning (supplementary sources [212], [222], [234]), but it is absent from the bibliography despite being discussed in the iteration history and relevant to the report's caveats.

7. **[LOW] Strengthen Tier 2 coverage** by citing specific studies comparing standard instruction or existing digital tools to AI-supported approaches, or explicitly noting the absence of such comparisons with a dedicated gap statement.

8. **[LOW] Strengthen Tier 4 subpopulation coverage** by incorporating more specific discussion of the limited subgroup data available from [10] and [24], or citing supplementary sources that address equity dimensions.

---

## Score

| Dimension | Max | Score | Rationale (1 sentence) |
|-----------|-----|-------|------------------------|
| Citation–bibliography linkage | 20 | 14 | Missing bibliography entry for LearnLM study (cited ~5 times), orphan [2], and inconsistent citation format throughout. |
| Statistic provenance | 25 | 22 | 13 of 14 statistics verified; one (n=585) is unverified/misleadingly composited from three study sites. |
| Study design accuracy | 15 | 15 | All study designs correctly labeled per source list and iteration history. |
| Sub-question coverage | 20 | 14 | Tiers 1, 3, and parts of 4 are well covered; Tier 2 and Tier 4 subpopulation/comparative sub-questions have minimal cited evidence. |
| URL integrity | 20 | 20 | All URLs match source list entries with no mismatches or invented URLs. |
| **Overall** | **100** | **85** | |

---

## Score Summary

| Dimension | Score |
|-----------|-------|
| Citation–bibliography linkage | 14/20 |
| Statistic provenance | 22/25 |
| Study design accuracy | 15/15 |
| Sub-question coverage | 14/20 |
| URL integrity | 20/20 |
| **Overall** | **85/100** |
