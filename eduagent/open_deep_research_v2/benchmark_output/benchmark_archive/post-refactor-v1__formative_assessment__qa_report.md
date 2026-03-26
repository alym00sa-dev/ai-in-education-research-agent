# QA Audit: post-refactor-v1 — formative_assessment

**Score: 41/100**

---



## Audit Summary

The report is **partially trustworthy but contains serious citation-bibliography linkage and URL integrity problems** that significantly undermine its credibility. The core thesis—that formative assessment positively impacts K-12 learning—is well-supported by iteration history findings. However, the majority of cited source numbers ([2], [4], [6], [7], [9], [16], [24], [40], [54]) do **not** correspond to the papers described in the PreScoredTiers source list. The report appears to have been written referencing a different numbering scheme than the pre-numbered source list provided, resulting in systematic mismatches between bibliography entries and their assigned source numbers. Nearly every URL in the bibliography is either a MISMATCH or INVENTED relative to the PreScoredTiers. Study design labels are also misattributed because the source numbers refer to entirely different papers. Statistics from the iteration history are generally verifiable, but their attribution to specific source numbers is incorrect. This is the single most critical issue: the report's internal citation system is internally consistent but **externally inconsistent** with the provided pre-numbered source list.

---

## Check 1 — Citation-Bibliography Linkage

**Inline citations used in the report body:** [2], [4], [6], [7], [9], [16], [24], [40], [54]

**All nine appear in the Bibliography table — PASS for internal consistency.**

**Cross-check against PreScoredTiers source list — FAIL for nearly all entries:**

| Bib # | Report Title (abbreviated) | PreScoredTiers Title (abbreviated) | Match? |
|-------|---------------------------|-----------------------------------|--------|
| [2] | Karaman (2021) Formative Assessment Meta-Analysis | Implementation facilitation for ED buprenorphine (2019) | ❌ MISMATCH |
| [4] | Xuan et al. (2024) Formative assessment reading meta-analysis | Origins and Real Effects of Gender Gap (2021) | ❌ MISMATCH |
| [6] | Prastikawati et al. (2024) Fostering teacher PD | Methodology diabetes prevention Latino community (2009) | ❌ MISMATCH |
| [7] | Anders et al. (2022) Embedding Formative Assessment RCT | Developing the theory of formative assessment (2009) | ❌ MISMATCH |
| [9] | Yan et al. (2021) Systematic review teachers' intentions formative assessment | Self-monitoring and self-reflection A1 adult learners (2012) | ❌ MISMATCH |
| [16] | Hopfenbeck et al. (2023) Challenges/opportunities formative assessment & AI | Teachers' perception of STEM integration (2019) | ❌ MISMATCH |
| [24] | See et al. (2021) Technology impact on formative assessment | InkSurvey real-time formative assessment (2013) | ❌ MISMATCH |
| [40] | Prompiengchai et al. (2025) Practical Guide AI formative assessment | Practical Guide Supporting Formative Assessment Using Generative AI (2024) | ✅ PARTIAL MATCH (title close, year differs 2025 vs 2024) |
| [54] | Power of Feedback Revisited meta-analysis (2020) | Power of Feedback Revisited meta-analysis (2020) | ✅ MATCH |

**Orphan entries:** None (all bibliography entries are cited inline).

**Summary:** 7 of 9 bibliography entries do not match their corresponding PreScoredTiers entries. Only [40] (partial) and [54] match.

---

## Check 2 — Statistic Provenance

| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| +0.19 effect size on reading achievement, 48 studies, 116,051 students | [4] | VERIFIED | Found verbatim in Iteration 1 and 3 history ("48 studies," "116,051 students," "+0.19") |
| Effect sizes 0.09–0.11 on GCSE attainment, 140 English secondary schools | [7] | VERIFIED | Iteration 1 mentions "effect sizes ranging from 0.09 to 0.11" and "140 secondary schools" |
| Student-initiated feedback d=1.16, adult-initiated d=0.69, computer-initiated d=0.42 | [2] | VERIFIED | Iteration 1 cites these exact figures from Karaman (2021) |
| 32 studies in Turkey meta-analysis | [2] | VERIFIED | Iteration 1 mentions "32 studies" |
| n=25,877 pupils (mentioned only in iteration history, not in report body) | [7] | N/A | Not cited in report body |
| "86% agreeing it helped instructors understand student knowledge; 76% reported InkSurvey helped" | [24] | UNVERIFIED | These statistics are from source [24] in PreScoredTiers (InkSurvey), but the report cites [24] as See et al. technology review; these specific stats are NOT in the report |
| Formative assessment supports sustained motivation, self-regulation through transitions | [7] | VERIFIED | Iteration 3 mentions "sustained self-regulation and motivation benefits through school transitions (Beekman et al., 2021)" — attributed to the EFA study context |

**Summary of statistics in report body:**
- Effect size +0.19 (48 studies, 116,051 students): **VERIFIED**
- Effect sizes 0.09–0.11 (140 schools, RCT): **VERIFIED**
- d=1.16 student-initiated, d=0.69 adult-initiated, d=0.42 computer-initiated (32 studies): **VERIFIED**
- "Formative assessment supports gains in metacognitive skills and motivation sustained longitudinally": **VERIFIED** (qualitative claim in iteration history)

All quantitative statistics in the report body are traceable to iteration history. No FABRICATED statistics found.

| Count | Status |
|-------|--------|
| 4 key statistics | VERIFIED |
| 0 | UNVERIFIED |
| 0 | FABRICATED |

---

## Check 3 — Study Design Accuracy

**Cross-checked against PreScoredTiers source list:**

| Bib # | Report Label | PreScoredTiers Label | Match? | Notes |
|-------|-------------|---------------------|--------|-------|
| [2] | Meta-Analysis | QED (PreScoredTiers: ED buprenorphine) | ❌ MISMATCH | Report describes Karaman meta-analysis; PreScoredTiers [2] is a QED |
| [4] | Meta-Analysis | Observational / Correlational (PreScoredTiers: Gender gap CEO study) | ❌ MISMATCH | Report describes Xuan reading meta-analysis; PreScoredTiers [4] is observational |
| [6] | QED | RCT (PreScoredTiers: Diabetes prevention) | ❌ MISMATCH | Report describes Indonesian preservice QED; PreScoredTiers [6] is an RCT |
| [7] | RCT | Qualitative (PreScoredTiers: Developing theory of formative assessment) | ❌ MISMATCH | Report describes Anders et al. cluster RCT; PreScoredTiers [7] is Qualitative |
| [9] | Qualitative | Qualitative (PreScoredTiers: Self-monitoring adult learners) | ✅ MATCH (design label matches by coincidence) | But different paper |
| [16] | Qualitative | Meta-Analysis / Systematic Review (PreScoredTiers: STEM integration perceptions) | ❌ MISMATCH | Report says Qualitative; PreScoredTiers [16] is systematic review |
| [24] | QED | QED (PreScoredTiers: InkSurvey) | ✅ MATCH (design label matches by coincidence) | But different paper |
| [40] | Qualitative | Qualitative | ✅ MATCH | Same/similar paper |
| [54] | Meta-Analysis / Systematic Review | Meta-Analysis / Systematic Review | ✅ MATCH | Same paper |

**Flagged issues:**
- **[7]** is described as an RCT in the report, but PreScoredTiers [7] is labeled Qualitative (it's a completely different paper).
- **[2]** is described as a Meta-Analysis (with QED label in confidence table), but PreScoredTiers [2] is a QED about buprenorphine.
- **[4]** is described as a Meta-Analysis, but PreScoredTiers [4] is Observational/Correlational about gender gap.
- **[6]** is described as QED, but PreScoredTiers [6] is an RCT about diabetes prevention.
- **[16]** is described as Qualitative, but PreScoredTiers [16] is a Meta-Analysis/Systematic Review.

**5 study design mismatches** identified (all due to source number misalignment).

---

## Check 4 — Sub-question Coverage

| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| 1 | Definition and scope of formative assessment in K-12 | ✅ Fully addressed | [7], [54] |
| 1 | Which student learning outcomes are targeted | ✅ Fully addressed | [7], [54] |
| 1 | Characteristics and diversity of K-12 populations | ✅ Addressed (briefly) | [7] |
| 2 | How outcomes are assessed without formative assessment | ⚠️ Partially addressed | [7] — limited direct comparative data cited |
| 2 | Baseline instructional and assessment approaches | ⚠️ Partially addressed | [7] — general description only |
| 2 | Summative assessment practices in K-12 | ⚠️ Partially addressed | [7] — mentioned but no dedicated citation |
| 3 | How formative assessment is implemented in practice | ✅ Addressed with citations | [6], [9], [2], [7] |
| 3 | Delivery methods and instructional models | ✅ Addressed | [2], [7], [24] |
| 3 | Learning mechanisms explaining impact | ✅ Addressed | [7] |
| 3 | Teacher training and PD effects on implementation fidelity | ✅ Addressed | [6], [9] |
| 4 | Experimental evidence on formative vs. summative/no formative | ✅ Addressed | [4], [7], [2] |
| 4 | Effectiveness variation by population, grade, subject | ⚠️ Partially addressed | [4], [2] — acknowledged as a gap |
| 4 | Challenges and tradeoffs in implementation | ✅ Addressed | [9], [16] |
| 4 | Meta-analyses/systematic reviews on comparative benefits | ✅ Addressed | [2], [4], [54] |

**Tier-level summary:**
- **Tier 1:** Fully covered (3/3 sub-questions addressed with citations) ✅
- **Tier 2:** Partially covered (3/3 sub-questions mentioned but with thin evidence and limited dedicated citations) ⚠️
- **Tier 3:** Fully covered (4/4 sub-questions addressed) ✅
- **Tier 4:** Mostly covered (3/4 fully addressed; 1 partially addressed — variation by population/grade/subject acknowledged as gap) ⚠️

---

## Check 5 — URL Integrity

| Bib # | Report URL | PreScoredTiers URL | Status |
|-------|-----------|-------------------|--------|
| [2] | `https://doi.org/10.1186/s40536-021-00110-7` | `https://doi.org/10.1186/s13012-019-0891-5` | **MISMATCH** |
| [4] | `https://doi.org/10.3389/fpsyg.2023.1124018` | `https://doi.org/10.1093/rfs/hhaa068` | **MISMATCH** |
| [6] | `https://doi.org/10.3389/feduc.2024.1271681` | `http://www.biomedcentral.com/1471-2288/9/20` | **MISMATCH** |
| [7] | `https://doi.org/10.1080/19345747.2022.2076405` | `https://doi.org/10.1007/s11092-008-9068-5` | **MISMATCH** |
| [9] | `https://doi.org/10.1080/0969594X.2021.1884042` | `not_reported` | **INVENTED** (URL does not appear in PreScoredTiers for [9]) |
| [16] | `https://doi.org/10.3389/feduc.2023.1270700` | `https://doi.org/10.1186/s40594-018-0151-2` | **MISMATCH** |
| [24] | `https://doi.org/10.1080/02671522.2021.1907778` | `https://arxiv.org/abs/1308.3729` | **MISMATCH** |
| [40] | `https://chat.openai.com/` | `https://chat.openai.com/` | **OK** |
| [54] | `https://www.frontiersin.org/articles/10.3389/fpsyg.2019.03087/full` | `https://www.frontiersin.org/articles/10.3389/fpsyg.2019.03087/full` | **OK** |

**Summary:** 6 MISMATCH + 1 INVENTED = **7 URL integrity failures** out of 9 entries. Only [40] and [54] are OK.

---

## Recommended Fixes

1. **[CRITICAL] Re-number all citations to match the PreScoredTiers source list, or add the actual formative-assessment papers as new numbered entries.** The report cites papers (Karaman 2021, Xuan et al. 2024, Anders et al. 2022, Prastikawati et al. 2024, Yan et al. 2021, Hopfenbeck et al. 2023, See et al. 2021) that do not exist at the source numbers [2], [4], [6], [7], [9], [16], [24] in the PreScoredTiers. This is the root cause of nearly all audit failures.

2. **[CRITICAL] Correct all 7 mismatched/invented URLs** in the bibliography to match the actual PreScoredTiers URLs for each source number, or reassign source numbers to match the intended papers.

3. **[HIGH] Correct study design labels** for [2], [4], [6], [7], and [16] to match the PreScoredTiers entries, or reassign numbers so labels are accurate.

4. **[HIGH] Correct the quality/impact tier labels** in the bibliography. For example, [7] is listed as Blue/Blue in the report but the PreScoredTiers [7] is Yellow/Green (Qualitative paper on theory of formative assessment). The report's tier labels correspond to the intended papers, not the PreScoredTiers numbers.

5. **[MODERATE] Strengthen Tier 2 coverage** with dedicated citations and evidence for baseline/summative assessment practices. Current coverage relies almost entirely on [7] with general statements.

6. **[MODERATE] Add explicit acknowledgment** in the Limitations section that the "Body of Evidence Maturity: MATURE" rating may be overstated given that evidence certainty is frequently rated low to very low in the underlying meta-analyses.

7. **[LOW] Provide more specific evidence** for the claim that formative assessment supports "socio-emotional competencies" — this claim currently lacks a dedicated citation or quantitative evidence.

8. **[LOW] Clarify** in the Executive Summary table that the [2] study design is a meta-analysis (not QED as implied by the confidence table label "QED" in parentheses).

---

## Score

| Dimension | Max | Score | Rationale (1 sentence) |
|-----------|-----|-------|------------------------|
| Citation–bibliography linkage | 20 | 6 | 7 of 9 bibliography entries do not match their PreScoredTiers counter

---

## Score Summary

| Dimension | Score |
|-----------|-------|
| Citation–bibliography linkage | 6/20 |
| Statistic provenance | 25/25 |
| Study design accuracy | 0/15 |
| Sub-question coverage | 10/20 |
| URL integrity | 0/20 |
| **Overall** | **41/100** |
