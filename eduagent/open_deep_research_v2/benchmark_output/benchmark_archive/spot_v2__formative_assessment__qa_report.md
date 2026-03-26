

## Audit Summary

The report is partially trustworthy but contains several critical issues that undermine its integrity. The most severe problems are: (1) **major citation-bibliography misattributions**, where source numbers in the report do not correspond to the correct entries in the PreScoredTiers list — most critically, [3] is used for the EFA/Black & Wiliam content but actually corresponds to the Boström & Palm RCT, [4] is cited for the Boström & Palm RCT but corresponds to a different meta-analysis on feedback, [6] is cited as a meta-analysis from Turkey but is actually an observational study on student perceptions of AfL, and [25] is cited as a reading achievement meta-analysis but actually corresponds to an MRI artifact detection review; (2) **URL mismatches** where multiple bibliography entries have URLs that do not match their PreScoredTiers entries or are incorrectly paired; (3) **study design misattributions**, where at least two sources are labelled with incorrect study designs. These systematic cross-referencing errors suggest the report conflated source numbering, creating a cascade of inaccuracies across citations, URLs, and study design labels.

---

## Check 1 — Citation-Bibliography Linkage

**Inline citations found in report body:** [3], [4], [5], [6], [7], [25], [176]

**Bibliography entries:** [3], [4], [5], [6], [7], [25], [176], [1], [2], [26]

**Issues found:**

1. **[1] — Orphan bibliography entry.** Entry [1] (IPV intervention in Congolese refugees) appears in the bibliography but is never cited inline in the report body.

2. **[2] — Orphan bibliography entry.** Entry [2] (Automated Writing Evaluation RCT) appears in the bibliography but is never cited inline in the report body.

3. **[26] — Orphan bibliography entry.** Entry [26] (multivariate meta-analysis model) appears in the bibliography but is never cited inline in the report body.

4. **[3] — Content mismatch.** The report uses [3] to cite both the Embedding Formative Assessment (EFA) cluster RCT in 140 English secondary schools AND the Black & Wiliam (2009) formative assessment definition. However, PreScoredTiers [3] is "The impact on student achievement of an assessment for learning teacher professional development program (2022)" — the Boström & Palm Netherlands RCT. The EFA study (Anders et al., 2022) does not appear in the PreScoredTiers list at all.

5. **[4] — Content mismatch.** The report uses [4] to cite the Boström & Palm RCT (AfL, d=0.27, n=599). However, PreScoredTiers [4] is "Reframing the effectiveness of feedback in improving teaching and learning achievement (2020)" — a meta-analysis/systematic review on feedback, not the Boström & Palm RCT. The Boström & Palm study corresponds to PreScoredTiers [3].

6. **[6] — Content mismatch.** The report uses [6] to cite a meta-analysis of 32 Turkish studies (Karaman, 2021, d=0.72). However, PreScoredTiers [6] is "Key stakeholder voices: Investigating student perceptions of teachers' use of assessment for learning (2024)" — an observational/correlational study, not a meta-analysis.

7. **[25] — Content mismatch.** The report uses [25] to cite a meta-analysis of 48 reading achievement studies (Xuan, Cheung & Sun, 2022, n=116,051). However, PreScoredTiers [25] is "Systematic Review and Meta-analysis of AI-driven MRI Motion Artifact Detection and Correction (2025)" — completely unrelated to K-12 reading assessment.

---

## Check 2 — Statistic Provenance

| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| EFA RCT in 140 English secondary schools, d=0.09 overall, d=0.11 after sensitivity | [3] | UNVERIFIED | This study (Anders et al., 2022) does not appear in the PreScoredTiers or iteration history findings. The iteration 3 summary mentions it but no source finding with these exact figures exists. |
| n=~25,877 pupils for EFA RCT | [3] | UNVERIFIED | Not found in any source finding or iteration history. |
| AfL TPD RCT, d=0.27, n=599 students | [4] | VERIFIED | Found verbatim in PreScoredTiers [3] finding: "effect size d = 0.27 (n=599 students, 41 teachers)" |
| LA Cockpit QED, d=0.34 to 0.53, n=393 students | [7] | VERIFIED | Found verbatim in PreScoredTiers [7] finding: "effect=d=0.34 to 0.53 | n=393 (after removing 10 outliers)" |
| Meta-analysis of 48 studies, n=116,051, effect size 0.19 for reading | [25] | UNVERIFIED | Found in iteration history summaries (Iterations 1, 2, 3) but NOT in any PreScoredTiers finding. PreScoredTiers [25] is about MRI artifacts. The actual source paper is not in the numbered source list. |
| Meta-analysis of 32 Turkish studies, d=0.72, student-initiated feedback d=1.16 | [6] | UNVERIFIED | Found in iteration history summaries (Iterations 1, 2) but NOT in any PreScoredTiers finding. PreScoredTiers [6] is an observational study on student perceptions, not a meta-analysis. The actual source is not in the numbered source list. |
| SEL-integrated assessment, medium effect sizes for pupil well-being and engagement | [176] | VERIFIED | PreScoredTiers [176] findings confirm: "η²=0.08, d=0.57" for well-being, "η²=0.09, d=0.61" for academic engagement. |
| F(1,357)=15.62, p<0.001 for well-being (mentioned implicitly via "medium effect sizes") | [176] | VERIFIED | Found in PreScoredTiers [176] finding. |
| TAM score 4.95/7 for LA Cockpit teachers | [7] | VERIFIED | Found in PreScoredTiers [7] finding: "mean TAM score 4.95/7" |
| 43.97% process-related feedback from LA Cockpit | [7] | VERIFIED | Found in PreScoredTiers [7] finding: "43.97% of feedback messages" |

**Summary:** 5 VERIFIED, 4 UNVERIFIED, 0 FABRICATED.

The UNVERIFIED statistics include the core EFA RCT figures (d=0.09, d=0.11, n=25,877), the reading meta-analysis (48 studies, n=116,051, ES=0.19), and the Turkish meta-analysis (32 studies, d=0.72, d=1.16). The latter two appear in iteration history text but lack source entries in the PreScoredTiers. The EFA RCT details appear only in Iteration 3 narrative without a corresponding source entry.

---

## Check 3 — Study Design Accuracy

1. **[6] described as "Meta-Analysis" in report and bibliography.** PreScoredTiers [6] is labelled "Observational / Correlational" — it is a study on student perceptions of AfL, not a meta-analysis. **MISLABELLED.**

2. **[25] described as "Meta-Analysis" in report and bibliography.** PreScoredTiers [25] is labelled "Meta-Analysis / Systematic Review" but is about AI-driven MRI motion artifact detection, not reading achievement. The study design label technically matches but the **content is completely wrong** — it is not the reading meta-analysis described. **CONTENT MISMATCH (effective mislabelling).**

3. **[3] described as "RCT (Embedding Formative Assessment)" in the bibliography.** PreScoredTiers [3] is an "RCT" but it is the Boström & Palm AfL study, not the EFA study. The EFA study is not in the source list. **MISATTRIBUTION.**

4. **[4] described as "RCT (Assessment for Learning PD)" in the bibliography.** PreScoredTiers [4] is a "Meta-Analysis / Systematic Review" on feedback effectiveness, not an RCT. **MISLABELLED as RCT.**

---

## Check 4 — Sub-question Coverage

| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| 1 | Key characteristics and definitions of formative assessment | Fully covered | [3] (though misattributed) |
| 1 | Specific learning outcomes and skills FA aims to improve | Fully covered | [3], [4], [6] (misattributed sources) |
| 1 | Typical K-12 educational settings and populations | Covered with evidence | [6], [25] (misattributed sources) |
| 2 | How student outcomes develop without FA | Partially covered — discussed generally but no specific cited study directly measures baseline-only outcomes | [4], [7] |
| 2 | Existing alternative instructional approaches | Partially covered — summative and standard practices discussed generally but limited comparative citations | [7], [25] |
| 2 | Baseline assessment/feedback practices | Partially covered — mentioned in text but no dedicated cited study on baseline practices | [4], [7] |
| 3 | How FAs are implemented across settings | Covered | [4], [5], [7] |
| 3 | Instructional practices and feedback mechanisms | Covered | [4], [5], [7] |
| 3 | Practical challenges and facilitators | Covered | [5], [7] |
| 4 | Comparative effectiveness vs. standard practices | Partially covered — some comparative data but limited direct RCT comparisons | [3], [4], [6] |
| 4 | Variation across populations, grades, subjects | Partially covered — acknowledged but limited specific citations for differential effects | [6], [25] |
| 4 | Tradeoffs: teacher workload, resources, engagement | Covered but lightly, mostly qualitative assertions | [5] |
| 4 | Comparison to other assessment interventions | Flagged as underresearched; limited direct evidence cited | [3], [4], [6], [7] — confidence rated Low |

**Tier-level assessment:**
- **Tier 1:** 3/3 sub-questions covered with cited evidence (albeit misattributed citations) — **Covered**
- **Tier 2:** 3/3 sub-questions only partially addressed with limited specific citations — **Partially covered**
- **Tier 3:** 3/3 sub-questions covered with cited evidence — **Covered**
- **Tier 4:** 4/4 sub-questions partially addressed; acknowledged as gaps — **Partially covered**

---

## Check 5 — URL Integrity

| Bib # | Bibliography URL | PreScoredTiers URL | Status |
|-------|------------------|--------------------|--------|
| 3 | https://doi.org/10.1016/j.stueduc.2022.101184 | https://doi.org/10.1016/j.stueduc.2022.101184 | **OK** (URL matches [3] in source list, but report describes it as the EFA study, not the Boström & Palm study it actually is) |
| 4 | https://doi.org/10.1016/j.stueduc.2022.101184 | http://ijere.iaescore.com | **MISMATCH** — Bibliography gives the same URL as [3], but PreScoredTiers [4] URL is http://ijere.iaescore.com |
| 5 | https://doi.org/10.14786/flr.v8i4.641 | https://doi.org/10.14786/flr.v8i4.641 | **OK** |
| 6 | https://doi.org/10.1007/s11092-024-09428-7 | https://doi.org/10.1007/s11092-024-09428-7 | **OK** (URL matches PreScoredTiers [6], but [6] is observational, not the Turkish meta-analysis described) |
| 7 | https://doi.org/10.18608/jla.2024.8399 | https://doi.org/10.18608/jla.2024.8399 | **OK** |
| 25 | https://doi.org/10.1371/journal.pone.0266752 | https://arxiv.org/abs/2509.05071 | **MISMATCH** — Bibliography URL does not match PreScoredTiers [25]. The bibliography URL appears nowhere in the source list. This is effectively **INVENTED**. |
| 176 | https://doi.org/10.1038/s41598-025-33328-5 | https://doi.org/10.1038/s41598-025-33328-5 | **OK** |
| 1 | https://doi.org/10.1186/s13031-019-0222-0 | https://doi.org/10.1186/s13031-019-0222-0 | **OK** |
| 2 | https://www.frontiersin.org/articles/10.3389/fpsyg.2023.1249991/full | https://www.frontiersin.org/articles/10.3389/fpsyg.2023.1249991/full | **OK** |
| 26 | https://doi.org/10.1007/s11092-025-01696-x | https://arxiv.org/abs/2009.11808v4 | **MISMATCH** — Bibliography URL does not match PreScoredTiers [26]. The bibliography URL does not appear in PreScoredTiers. Notably, https://doi.org/10.1007/s11092-025-01696-x appears as the URL for source [174] in the PreScoredTiers (Formative Assessment in Mathematics Education: A Systematic Review), not [26]. This is a **MISMATCH**. |

**Issues:** 3 MISMATCH URLs ([4], [25], [26]); [25] URL is effectively INVENTED (not in source list).

---

## Recommended Fixes

1. **[CRITICAL] Reassign citation numbers to match PreScoredTiers.** The report systematically confuses source numbers. The Boström & Palm RCT (d=0.27, n=599) should be cited as [3], not [4]. Entry [4] in PreScoredTiers is a meta-analysis on feedback, not an RCT. The EFA study (Anders et al., 2022) does not appear in the source list and should either be removed or a new source number assigned if added.

2. **[CRITICAL] Remove or correctly reassign [25].** The reading achievement meta-analysis (Xuan, Cheung & Sun, 2022) is not source [25] in the PreScoredTiers (which is about MRI artifacts). The actual source is not in the numbered list. The URL in the bibliography (https://doi.org/10.1371/journal.pone.0266752) is invented relative to the source list.

3. **[CRITICAL] Remove or correctly reassign [6].** The Turkish meta-analysis (Karaman, 2021) is not source [6] in the PreScoredTiers. Source [6] is an observational study on student perceptions of AfL. The meta-analysis content described does not correspond to any numbered source.

4. **[CRITICAL] Correct the study design label for [4].** PreScoredTiers [4] is a Meta-Analysis/Systematic Review, not an RCT. The bibliography incorrectly labels it as "RCT (Assessment for Learning PD)."

5. **[CRITICAL] Fix URL for bibliography entry [4].** It currently duplicates [3]'s URL. It should be http://ijere.iaescore.com per PreScoredTiers.

6. **[CRITICAL] Fix URL for bibliography entry [25].** The URL https://doi.org/10.1371/journal.pone.0266752 does not appear in the source list and is effectively invented.

7. **[CRITICAL] Fix URL for bibliography entry [26].** Should be https://

---

## Score Summary

| Dimension | Score |
|-----------|-------|
| Citation–bibliography linkage | 6/20 |
| Statistic provenance | 14/25 |
| Study design accuracy | 0/15 |
| Sub-question coverage | 10/20 |
| URL integrity | 8/20 |
| **Overall** | **38/100** |
