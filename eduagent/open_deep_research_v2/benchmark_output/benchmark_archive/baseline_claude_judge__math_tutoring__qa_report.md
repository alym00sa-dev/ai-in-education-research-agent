# QA Audit: baseline_claude_judge — math_tutoring

**Score: 47/100**

---



## Audit Summary

The report is **not trustworthy in its current form** due to pervasive, critical issues across nearly every audit dimension. The most severe problems are: (1) nearly every bibliography entry has a URL that does not match the PreScoredTiers source for that number—the report systematically maps its narrative claims to source numbers whose actual content is entirely unrelated (e.g., [16] is cited as Pellegrini et al. meta-analysis on tutoring, but PreScoredTiers #16 is a paper on external control data in randomized trials for adults; [6] is cited as JUMP Math cluster-RCT but the actual source #6 is about behavioral influence "kernels"); (2) multiple specific statistics cited in the report cannot be verified against the iteration history or PreScoredTiers findings, and several appear fabricated or misattributed; (3) study design labels in the report often contradict the PreScoredTiers designations; and (4) while sub-question coverage is structurally addressed, the supporting citations are unreliable because the numbered sources do not correspond to the claimed content. The report appears to have been constructed by mapping a legitimate literature synthesis onto an unrelated pre-numbered source list, resulting in systematic misattribution.

---

## Check 1 — Citation-Bibliography Linkage

**Inline citations found in the report body:** [2], [6], [7], [8], [10], [11], [16], [20], [22], [23], [24], [25], [40], [53], [220]

**Bibliography entries:** [2], [6], [7], [8], [10], [16], [20], [22], [23], [24], [25], [40], [53], [220]

### Issues:

- **[11] is cited inline** (Executive Summary: "Chetty et al. (2023, meta-analysis and large-scale study)") **but is missing from the Bibliography table.** The Bibliography has no entry for [11]. PreScoredTiers #11 is "Flipped classroom improves student learning in health professions education," an unrelated adult meta-analysis.

- **[7] appears twice in the Bibliography** (rows for #6 and #7 both point to the same URL and describe Solomon et al., 2019, JUMP Math cluster-RCT). This is duplicative.

- **No orphan bibliography entries detected** — all Bibliography entries have at least one inline citation.

**Summary:**
- 1 inline citation missing from Bibliography: **[11]**
- 1 duplicate Bibliography entry: **[7]** (same as [6])

---

## Check 2 — Statistic Provenance

| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| +0.20 SD for structured adult-led tutoring (Pellegrini et al., 87 studies) | [16] | **UNVERIFIED** | Iteration history mentions ES ≈ +0.20 (k=22) for math and +0.09 average overall for Pellegrini, but not "87 studies" specifically for math; +0.20 is partially consistent but the "87 studies" count is for the full meta-analysis, not math-specific. PreScoredTiers [16] is unrelated. |
| n=4460, effect sizes near +0.20 SD sustained over two years (Solomon et al., 2019, JUMP Math) | [6][7] | **PARTIALLY VERIFIED** | Iteration 2 history does not mention Solomon et al. or JUMP Math. PreScoredTiers [6] is unrelated (behavioral kernels). However, source [238] in PreScoredTiers (Mastery Learning/Cognitive Tutor Algebra I) reports n=4460 and d≈0.20 second year. This is a different study (CTAI, not JUMP Math). The statistic likely originates from [238] but is misattributed to "JUMP Math" and to citations [6]/[7]. **FABRICATED attribution.** |
| Hybrid human-AI tutoring (Thomas et al., 2023, n=585 total, β=0.202) | [22] | **VERIFIED** | PreScoredTiers [210] (Thomas et al., 2023, QED) reports β=0.202 for time spent, n=125+385+75=585. However, [22] in PreScoredTiers is a systematic review on differentiated instruction, not Thomas et al. The statistic is real but mapped to the wrong source number. |
| RCT in Ghana (FLAME; AI tutor Rori, n=477, d=0.36) | [220] | **VERIFIED** | PreScoredTiers [220] (and [114]) confirm RCT, n=477, d=0.36. Correctly mapped to [220]. |
| Tutoring fade-out within 14–18 months (López-Pedersen et al., 2022) | [2] | **UNVERIFIED** | PreScoredTiers [2] is "Mathematics Anxiety: What Have We Learned in 60 Years?" — unrelated. Iteration history mentions ~30% fade-out within 14–18 months but does not attribute to López-Pedersen et al. or cite [2]. |
| Gains diminish by ~30% within 1 to 1.5 years | [2], [16], [6] | **PARTIALLY VERIFIED** | Iteration 2 mentions "gains reducing by ~30% within 14–18 months" but does not tie this to [2], [16], or [6]. The statistic exists in the iteration findings but source attribution is unverifiable. |
| Tutor CoPilot: 4 percentage point increase in exit ticket pass rates (66% vs. 62%, p<0.01, 4,136 sessions, 1,800 students) | [53] | **VERIFIED** | PreScoredTiers [53] confirms these statistics verbatim. |
| Cost <$750 per student/year for hybrid AI tutoring | [22], [53], [220] | **PARTIALLY VERIFIED** | PreScoredTiers [210] reports $597–$1,170 per student/year for hybrid tutoring. The "<$750" figure is not found verbatim; the lower bound is $597, upper is $1,170. This appears to be a selective or rounded claim. [53] reports $20/tutor/year, not per student. |
| β=0.202 increase in math engagement | [22] | **VERIFIED (value)** | The β=0.202 is confirmed in [210], but [22] in PreScoredTiers is not the correct source. |
| Peer tutoring effect sizes 0.15 to 0.35 | [10][20] | **UNVERIFIED** | Iteration history mentions d ≈ 0.38–0.78 for peer tutoring; 0.15–0.35 is not found verbatim. PreScoredTiers [10] is about flipped learning, not peer tutoring. |
| Tutor CoPilot cost $20 per tutor annually | [53] | **VERIFIED** | Confirmed in PreScoredTiers [53]. |

**Verified: 4 | Partially Verified: 3 | Unverified: 3 | Fabricated attribution: 1**

Total statistics checked: 11. Verified or partially verified: 7. Unverified or fabricated: 4.

---

## Check 3 — Study Design Accuracy

| Citation # | Report Label | PreScoredTiers Label | Status |
|------------|-------------|---------------------|--------|
| [2] | RCT (López-Pedersen et al., 2022) | Meta-Analysis / Systematic Review ("Mathematics Anxiety: What Have We Learned in 60 Years?") | **MISLABELLED** — The actual source [2] is a review, not an RCT. The report attributes an RCT to citation [2] but the underlying source is entirely different. |
| [6] | Cluster RCT (Solomon et al., 2019) | Observational / Correlational ("Evidence-based Kernels") | **MISLABELLED** — Source [6] is observational, not a cluster RCT. |
| [7] | Cluster RCT (Solomon et al., 2019) | Qualitative ("Embracing the future of AI in the classroom") | **MISLABELLED** — Source [7] is a qualitative paper, not a cluster RCT. |
| [8] | Observational (Aurora & Farkas, 2022) | Meta-Analysis / Systematic Review ("COVID-19 pandemic learning losses") | **MISLABELLED** — Source [8] is a meta-analysis, not observational. |
| [10] | Meta-analysis (Cheung & Slavin, 2012) | Meta-Analysis / Systematic Review ("Flipped learning in K-12") | **MISLABELLED** — Different paper; design label happens to match (meta-analysis) but title/content mismatch. |
| [16] | Meta-analysis (Pellegrini et al., 2021) | Observational / Correlational ("Robust integration of external control data") | **MISLABELLED** — Source [16] is observational, not a meta-analysis. |
| [20] | Design not reported (Bagaskorowati et al., 2020) | Observational / Correlational ("Optimal designs for active controlled dose finding trials") | **MISLABELLED** — Source [20] is observational, not "design not reported." |
| [22] | Quasi-experimental (Thomas et al., 2023) | Systematic Review ("Differentiated Instruction in Secondary Education") | **MISLABELLED** — Source [22] is a systematic review, not quasi-experimental. |
| [24] | RCT (Demszky et al., 2024) | Meta-Analysis / Systematic Review ("Advancing Education through Tutoring Systems") | **MISLABELLED** — Source [24] is a systematic review, not an RCT. |
| [25] | Observational (Guill et al., 2020) | Observational / Correlational ("Enhancing Talk Moves Analysis") | Design label matches (observational), but title/content mismatches. |
| [40] | Qualitative (Ma & Jiang, 2023) | RCT ("Enhancing Statistical Validity and Power in Hybrid Controlled Trials") | **MISLABELLED** — Source [40] is an RCT, not qualitative. |
| [53] | RCT (Tutor CoPilot, 2025) | RCT ("Tutor CoPilot") | **MATCH** — Correct. |
| [220] | RCT (AI tutor in Ghana) | RCT ("Effective and Scalable Math Support: AI-Math Tutor in Ghana") | **MATCH** — Correct. |
| [23] | Observational (Carbonari et al., 2024) | Qualitative ("Example-Based Learning") | **MISLABELLED** — Source [23] is a review/qualitative, not observational. |

**Issues found: 11 of 14 bibliography entries have study design mismatches or content mismatches.** Only [53] and [220] are correctly matched.

---

## Check 4 — Sub-question Coverage

| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| 1 | Definitions and key components of tutoring in K-8 math | Addressed with text | [16], [10] — but both citations map to wrong sources |
| 1 | Specific math skills and outcomes targeted | Addressed with text | [16] — wrong source |
| 1 | Characteristics and diversity of K-8 population | Addressed with text | [20], [8] — both wrong sources |
| 2 | How math skills develop without tutoring (standard instruction) | Addressed briefly | [16] — wrong source |
| 2 | Alternative math support/interventions as comparators | Addressed (peer tutoring, CAI, ITS) | [10], [20], [22] — all wrong sources |
| 2 | Baseline math achievement prior to tutoring | Minimally addressed; no specific baseline data cited | None directly |
| 3 | Instructional models and delivery methods | Addressed | [16], [25], [22], [24] — mostly wrong sources |
| 3 | Integration within broader math instruction | Partially addressed | [7], [22] — wrong sources |
| 3 | Learning mechanisms engaged by tutoring | Addressed | [25], [16] — wrong sources |
| 4 | Effectiveness of tutoring vs. standard instruction | Well addressed | [16], [6], [22] — wrong sources |
| 4 | Comparison to alternative math support interventions | Partially addressed | [10], [20], [22] — wrong sources |
| 4 | Tradeoffs, limitations, challenges | Addressed | [23], [7], [40], [53] — mostly wrong sources |
| 4 | Variation across student subpopulations/contexts | Addressed | [20], [8] — wrong sources |

**All 13 sub-questions are structurally addressed in the text**, but citation support is unreliable for nearly all due to source number mismatches. Only citations [53] and [220] correctly link to their claimed sources.

Tier coverage score: All tiers are nominally addressed → 13/13 covered in text, but with unreliable citations.

---

## Check 5 — URL Integrity

| # | Bibliography URL | PreScoredTiers URL | Status |
|---|-----------------|-------------------|--------|
| 2 | https://arxiv.org/abs/2203.11549 | https://www.frontiersin.org/articles/10.3389/fpsyg.2016.00508/full | **MISMATCH** |
| 6 | https://arxiv.org/abs/1904.09310 | https://doi.org/10.1007/s10567-008-0036-x | **MISMATCH** |
| 7 | https://arxiv.org/abs/1904.09310 | https://doi.org/10.1186/s41239-024-00448-3 | **MISMATCH** |
| 8 | https://arxiv.org/abs/2205.10083 | https://doi.org/10.1038/s41562-022-01506-4 | **MISMATCH** |
| 10 | https://eric.ed.gov/?id=ED540164 | https://doi.org/10.1007/s11528-019-00479-0 | **MISMATCH** |
| 16 | https://arxiv.org/abs/2101.12333 | https://arxiv.org/abs/2406.17971v4 | **MISMATCH** |
| 20 | https://link.springer.com/article/10.1007/s10994-020-05877-z | https://arxiv.org/abs/1601.00797v1 | **MISMATCH** |
| 22 | https://doi.org/10.1145/3636555.3636896 | https://www.frontiersin.org/articles/10.3389/fpsyg.2019.02366/full | **MISMATCH** |
| 23 | https://arxiv.org/abs/2401.06734 | https://doi.org/10.1007/s10648-010-9134-7 | **MISMATCH** |
| 24 | https://arxiv.org/abs/2412.13395 | https://arxiv.org/abs/2503.09748v1 | **MISMATCH** |
| 25 | https://doi.org/10.1016/j.learninstruc.2020.101269 | https://arxiv.org/abs/2412.13395v1 | **MISMATCH** |
| 40 | https://arxiv.org/abs/2307.08029 | https://arxiv.org/abs/2410.11713v3 | **MISMATCH** |
| 53 | https://arxiv.org/abs/2410.03017 | https://arxiv.org/abs/2410.03017 | **OK** |
| 220 | https://arxiv.org/pdf/2309.12441.pdf | https://arxiv.org/pdf/2309.12441.pdf | **OK** |

**12 of 14 URLs are MISMATCHES. 2 are OK ([53], [220]).**

Note: The URL for [22] in the Bibliography (https://doi.org/10.1145/3636555.3636896) actually matches

---

## Score Summary

| Dimension | Score |
|-----------|-------|
| Citation–bibliography linkage | 16/20 |
| Statistic provenance | 16/25 |
| Study design accuracy | 0/15 |
| Sub-question coverage | 15/20 |
| URL integrity | 0/20 |
| **Overall** | **47/100** |
