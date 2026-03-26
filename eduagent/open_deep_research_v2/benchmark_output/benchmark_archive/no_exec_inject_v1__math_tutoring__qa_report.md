# QA Audit: no_exec_inject_v1 — math_tutoring

**Score: 42/100**

---



## Audit Summary

The report is generally well-structured and draws on a coherent body of evidence from the iteration history. However, there are several significant issues. Most critically, there are **major citation number mismatches** — the report cites sources using numbers that correspond to entirely different papers in the source lists, indicating the bibliography was constructed with numbering errors. For example, [141] in the report refers to Hodgen et al. (2022), but [141] in the supplementary sources is Clarke et al. (2017). Similarly, [136] in the report refers to Chappell et al. (2015), but [136] in the supplementary sources is Kraft & Falken (2021). The bibliography table in the report appears internally consistent (numbers match the titles/URLs listed there), but these numbers conflict with the supplementary source list assignments. Additionally, [194] is described in the report as a hybrid human-AI tutoring study (Thomas et al., 2023), but [194] in the supplementary list is Lehmann (2024) on definite integrals in calculus. The actual Thomas et al. paper appears at [193] and [202]. Several statistics are verifiable from the iteration history but a few lack precise provenance. Study design labels cannot be verified against the academic-DB list since all cited sources are notes-sourced ([135]+), and design accuracy checks rely on iteration history descriptions.

---

## Check 1 — Citation-Bibliography Linkage

**Issues found:**

1. **[141] Number conflict**: The bibliography lists Hodgen et al. (2022) at [141], matching the URL from supplementary source [140]. But supplementary source [141] is Clarke et al. (2017) — a completely different paper. The report uses [141] to refer to Hodgen et al., which contradicts the master supplementary list numbering.

2. **[136] Number conflict**: The bibliography lists Chappell et al. (2015) at [136], matching supplementary source [135] (and [192]). But supplementary source [136] is Kraft & Falken (2021) — a different paper. The report uses [136] for Chappell et al., contradicting the master list.

3. **[194] Number conflict**: The bibliography lists Thomas et al. (2023) at [194], but supplementary source [194] is Lehmann (2024) on calculus integrals. The actual Thomas et al. paper is at [193] and [202] in supplementary sources.

4. **[151] Number conflict**: The bibliography lists Pellegrini et al. (2021) at [151], but supplementary source [151] is Clements, Lizcano & Sarama (2023) "Research and Pedagogies for Early Math." The Pellegrini et al. paper appears at [150] and [186] in the supplementary list.

5. **[205] Number conflict**: The bibliography lists Demszky et al. (2024) at [205], but supplementary source [205] is Patterson & Xu (2020) "Enhancing Teachers' Competence in Building Students' Numeracy." The Demszky et al. paper is at [204].

6. **[218] Number conflict**: The bibliography lists Dietrichson et al. (2017) at [218], but supplementary source [218] is Mauer & Swanson (2024) "Cross-Age Peer Tutoring to Improve Literacy Outcomes for Students With Disabilities." The Dietrichson et al. paper is at [217].

7. **[252] Number conflict**: The bibliography lists Shenderovich et al. (2014) at [252], but supplementary source [252] does not appear in the provided supplementary list (list ends around [230]). However, a paper by Shenderovich et al. is not visible in the supplementary list at all — this number may be fabricated or from an unprovided range.

8. **[278] Number conflict**: The bibliography lists Dietrichson et al. (2021) at [278], which is far beyond the supplementary list range. This number cannot be verified.

9. **[168] Number conflict**: The bibliography lists Moliner et al. (2022) at [168], but supplementary source [168] is Hassidov (2017) "The Link between Teaching Methods and Achievement in Math." The Moliner et al. paper is at [167].

10. **[148] Number conflict**: The bibliography lists Barahona et al. (2023) at [148], but supplementary source [148] is Alegre et al. (2020) "Academic Achievement and Peer Tutoring in Mathematics." The Barahona et al. paper is at [147].

**Summary**: Nearly every citation number in the report is off by one or more positions relative to the supplementary source master list. The bibliography was apparently constructed with shifted numbering.

**Orphan entries**: No orphan entries — all bibliography entries are cited inline.

---

## Check 2 — Statistic Provenance

| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| Cohen's d = 0.30 (small group tutoring, teaching assistants) | [141] (Hodgen et al., 2022) | VERIFIED | Iteration 1 and 3 both report d = 0.30 for small group tutoring |
| Cohen's d = 0.19 (one-on-one tutoring, teaching assistants) | [141] (Hodgen et al., 2022) | VERIFIED | Iteration 1 reports d = 0.19 for one-on-one tutoring |
| d = 0.36 (adult-led tutoring, low-SES) | [218] (Dietrichson et al., 2017) | VERIFIED | Iterations 1 and 3 report d = 0.36 for tutoring by adults |
| +0.20 pooled effect size for 23 tutoring programs | [151] (Pellegrini et al., 2021) | PARTIALLY VERIFIED | Iteration 1 states ES = +0.20 for tutoring; Iteration 3 says "23 studies" for Hodgen, but Pellegrini's "23 programs" appears in iteration 2. The "23 elementary math tutoring programs" claim in the report may conflate sources — Iteration 1 says 87 studies/66 programs, Iteration 2 says "23 elementary mathematics tutoring programs" |
| Estimate = 0.244, 95% CI [0.106, 0.381], p < 0.001 (hybrid human-AI tutoring) | [194] (Thomas et al., 2023) | VERIFIED | Iteration 3 reports parameter estimate = 0.244, 95% CI [0.106, 0.381], p < 0.001 |
| n = 1,800 (hybrid human-AI tutoring) | [194] (Thomas et al., 2023) | VERIFIED | Iteration 3 reports "around 1,800 K-8 students" |
| d = 0.95 and d = 1.47 (synchronous online tutoring) | [136] (Chappell et al., 2015) | VERIFIED | Iterations 1, 2, and 3 report d = 0.95 and d = 1.47 |
| n = 119 (online tutoring study) | [136] (Chappell et al., 2015) | VERIFIED | Iteration 2 reports "119 low-achieving middle school students" |
| 112 students (peer tutoring + digital tools) | [168] (Moliner et al., 2022) | VERIFIED | Iteration 2 reports "quasi-experimental study of 112 students" |
| g = 0.18 (cross-age peer tutoring, reading) | [252] (Shenderovich et al., 2014) | VERIFIED | Iteration 3 reports g = 0.18 for composite reading outcomes |
| d = 0.02 per 10 sessions (dosage effect) | [218] (Dietrichson et al., 2017) | NOT IN REPORT | Mentioned in iteration 3 but not in final report — no issue |
| "n not reported" for [141] | [141] | UNVERIFIED | Report says "n not reported" for Hodgen et al. RCT — iteration history does not specify n either, so this is consistent |
| 4 percentage points increase in pass rate (Tutor CoPilot) | Attributed to [194] in report | VERIFIED | Iteration 2 reports this figure but attributes it to Wang et al. (2024)/Tutor CoPilot [95], not Thomas et al. The report conflates two different studies under [194] |

**Critical note on conflation**: The report attributes the "n=1,800" and "estimate = 0.244" statistics to [194], which is described as Thomas et al. (2023) hybrid human-AI tutoring. However, the "4 percentage points" and "9 percentage points" statistics from [95] (Tutor CoPilot, Wang et al. 2024) are a different study. The iteration 2 summary mentions both studies, and the report appears to correctly separate them — the 0.244 estimate comes from Thomas et al. and the 4 pp increase from the Tutor CoPilot study. However, the Executive Summary's claims table attributes the 0.244 to [194] without mentioning the Tutor CoPilot findings separately. This is acceptable but worth noting.

---

## Check 3 — Study Design Accuracy

All cited sources are notes-sourced ([135]+), so design labels are checked against iteration history:

1. **[141] (Hodgen et al., 2022)**: Report labels as RCT. Iteration history confirms "large-scale RCT." ✅ Correct.

2. **[218] (Dietrichson et al., 2017)**: Report labels as meta-analysis. Iteration history confirms "meta-analysis" / "synthesized 36 studies." ✅ Correct.

3. **[151] (Pellegrini et al., 2021)**: Report labels as meta-analysis. Iteration history confirms "meta-analyzed" / "synthesized findings from 87 studies." ✅ Correct.

4. **[194] (Thomas et al., 2023)**: Report labels as quasi-experimental. Iteration history (Iteration 3) confirms "quasi-experimental investigation." ✅ Correct.

5. **[136] (Chappell et al., 2015)**: Report does not explicitly label it in the body, but bibliography says "not_reported." Iteration history describes it as having "pre-post" design with comparison groups — quasi-experimental is implied. The report's narrative treatment is reasonable.

6. **[168] (Moliner et al., 2022)**: Report labels as quasi-experimental. Iteration 2 describes it as "quasi-experimental study." ✅ Correct.

7. **[252] (Shenderovich et al., 2014)**: Report labels as meta-analysis. Iteration 3 confirms "synthesized randomized studies" — meta-analysis. ✅ Correct.

8. **[205] (Demszky et al., 2024)**: Report references it for observational research on tutor training. The academic-DB pre-numbered list does not contain this number. The bibliography says "not_reported." The iteration history (Iteration 1) describes Demszky et al. as demonstrating effects via an RCT ("providing tutors with real-time feedback on tutor-student talk time"). The report labels it as observational, which may be a **mislabelling** — Demszky et al. (2024) is described as an RCT in the pre-numbered source list at [205] (which is actually Patterson & Xu in the supplementary list). However, looking at pre-numbered sources, [205] in the academic-DB is not listed (academic-DB only goes to [134]). The actual Demszky et al. paper at supplementary [204] is described in the iteration history as providing "evidence from a randomized controlled trial." **The report treats [205] as observational but the iteration history suggests RCT.** ⚠️ Potential mislabelling.

9. **[148] (Barahona et al., 2023)**: Report references for observational research. Iteration history does not explicitly describe its design. The supplementary source [147] (which is the correct number for Barahona et al.) does not specify design. The bibliography says "not_reported." No clear mislabelling.

**Issues found:**
- **[205]** (intended to be Demszky et al., 2024): Report treats as observational/qualitative evidence, but iteration history describes it as an RCT. This is a potential mislabelling, though the report doesn't explicitly assign a design label — it just uses it for "observational" claims about tutor training.

---

## Check 4 — Sub-question Coverage

| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| 1 | How is tutoring defined in K-8 mathematics education? | ✅ Fully addressed | [141][218][151][194] |
| 1 | What mathematics skills are targeted for improvement in K-8 students? | ✅ Addressed | [148][151] |
| 1 | What are the characteristics of the K-8 student population relevant to tutoring? | ✅ Addressed | [218][141][136][194] |
| 2 | What are standard instructional approaches in K-8 math without tutoring? | ✅ Addressed | [151][278] |
| 2 | What alternative math support interventions exist for comparison? | ⚠️ Partially addressed — mentioned briefly but no deep comparative evidence cited | [141][136] mentioned as comparators |
| 2 | What is baseline math achievement among students without tutoring? | ⚠️ Partially addressed — described generally but no specific baseline data cited | [151][218] |
| 3 | How is tutoring typically implemented for K-8 math students? | ✅ Fully addressed | [141][148][136][194] |
| 3 | What instructional strategies and pedagogical approaches are used during math tutoring? | ✅ Fully addressed | [136][148][194][205] |
| 3 | What mechanisms explain how tutoring improves math learning? | ✅ Addressed | [218][205][194] |
| 4 | What is the comparative effectiveness of tutoring versus standard instruction on math outcomes? | ✅ Fully addressed with effect sizes | [141][218][151][136][194] |
| 4 | How does tutoring impact subpopulations such as English learners and students with disabilities? | ⚠️ Partially addressed — mentioned as limited evidence | [218][148] |
| 4 | What are the tradeoffs or limitations of tutoring (cost, scalability, engagement)? | ⚠️ Partially addressed — discussed qualitatively, limited cited evidence | [194] |
| 4 | How does tutoring compare to other math support interventions and what contextual factors influence? | ⚠️ Partially addressed — some comparison but limited direct evidence | [168][252] |

**Tiers fully covered**: Tier 1 (3/3), Tier 3 (3/3) = 6 sub-questions fully covered
**Tiers partially covered**: Tier 2 (1/3 fully, 2/3 partial), Tier 4 (1/4 fully, 3/4 partial) = 5 sub-questions partially covered, 2 fully covered
**Total**: 8 of 13 sub-questions fully addressed with citations; 5 partially addressed.

---

## Check 5 — URL Integrity

All sources cited are notes-sourced ([135]+). Checking against supplementary source list:

| # | Bibliography URL | Supplementary Source URL | Status |
|---|-----------------|------------------------|--------|
| 136 | `https://www.semanticscholar.org/paper/ca92b313f03626bc5592e7f07e66af6161124c94` | [135] has this URL (Chappell et al.) but [136] in supplementary is Kraft & Falken with URL `https://www.semanticscholar.org/paper/29765e751b2e40a6ee510486100682450ffb6de9` | **MISMATCH** — URL belongs to [135], not [136] |
| 141 | `https://www.semanticscholar.org/paper/a1278e3b811ec8431c27636ab2867440dc020253` | [140] has this URL (Hodgen et al.) but [141] in supplementary is Clarke et al. with URL `https://www.semanticscholar.org/paper/bcae3d170789e05fe1122e089379c7ad968b40bb` | **MISMATCH** — URL belongs to [140], not [141] |
| 148 

---

## Score Summary

| Dimension | Score |
|-----------|-------|
| Citation–bibliography linkage | 0/20 |
| Statistic provenance | 20/25 |
| Study design accuracy | 10/15 |
| Sub-question coverage | 12/20 |
| URL integrity | 0/20 |
| **Overall** | **42/100** |
