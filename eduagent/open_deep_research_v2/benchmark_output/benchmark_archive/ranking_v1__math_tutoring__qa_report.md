# QA Audit: ranking_v1 — math_tutoring

**Score: 74/100**

---



## Audit Summary

The report is broadly trustworthy in its core claims about tutoring effectiveness for K-8 math outcomes, and the major statistics cited can be traced to the iteration history. However, several issues undermine precision: (1) source [156] is cited for multiple distinct studies/findings (Tutor CoPilot RCT, dosage analysis, talk-time feedback RCT) that actually correspond to different papers conflated under one bibliography entry; (2) the Tutor CoPilot RCT findings are attributed to [156] when the academic-DB source list identifies [12] as the Tutor CoPilot paper; (3) some statistics (e.g., specific effect sizes for teacher-led vs. paraprofessional-led tutoring from [211]) are presented with precision not fully verifiable from the iteration history; and (4) study design labels for notes-sourced papers cannot always be verified because the bibliography lists "not_reported" for all of them. Overall, the report's conclusions are well-supported, but citation hygiene and attribution accuracy need correction.

## Check 1 — Citation-Bibliography Linkage

**Inline citations present in bibliography:**
- [211] ✅ Present in bibliography, title matches supplementary source
- [227] ✅ Present in bibliography, title matches supplementary source
- [147] ✅ Present in bibliography, title matches supplementary source
- [155] ✅ Present in bibliography, title matches supplementary source
- [255] ✅ Present in bibliography, title matches supplementary source
- [156] ✅ Present in bibliography — but see note below
- [206] ✅ Present in bibliography, title matches supplementary source
- [213] ✅ Present in bibliography, title matches supplementary source
- [181] ✅ Present in bibliography, title matches supplementary source
- [193] ✅ Present in bibliography, title matches supplementary source
- [201] ✅ Present in bibliography, title matches supplementary source
- [258] ✅ Present in bibliography, title matches supplementary source
- [236] ✅ Present in bibliography, title matches supplementary source
- [256] ✅ Present in bibliography, title matches supplementary source
- [316] ✅ Present in bibliography, title matches supplementary source
- [228] ✅ Present in bibliography, title matches supplementary source

**Issues:**
1. **[156] is used for at least three distinct studies/findings**: (a) Tutor CoPilot RCT (Wang et al., 2024, n=1,800) — this is actually source [12] in the academic-DB list; (b) a dosage analysis with 188 struggling readers — not clearly matching [156]'s title about talk-time feedback; (c) talk-time feedback RCT findings. The bibliography entry for [156] is "Does Feedback on Talk Time Increase Student Engagement?" which is about talk-time feedback, not Tutor CoPilot or dosage with struggling readers. This constitutes misattribution.
2. **Orphan entries**: All 17 bibliography entries have at least one inline citation. No orphan entries found.
3. **Missing bibliography entries**: No inline citations reference numbers absent from the bibliography.

## Check 2 — Statistic Provenance

| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| d=0.36 for tutoring interventions (low-SES elementary/middle) | [211] | VERIFIED | Iteration history: "tutoring interventions averaged effects of d = 0.36" |
| Teacher-led tutoring d=0.59 | [211] | VERIFIED | Iteration history: "teacher-led tutoring reaching d = 0.59" |
| Paraprofessional-led tutoring d=0.46 | [211] | VERIFIED | Iteration history: "paraprofessional-led at d = 0.46" |
| 36 studies in [211] meta-analysis | [211] | UNVERIFIED | Iteration history says "101 studies" for Dietrichson et al.; report says "36 studies" — possible confusion with subset or different count |
| d=0.38 for one-to-one tutoring (PreK-12) | [227] | VERIFIED | Iteration history: "average effect size of +0.38 for one-to-one tutoring" |
| d=0.20 overall effect size from 23 studies | [147] | VERIFIED | Iteration history: "Pellegrini et al. (2021) meta-analyzed 23 elementary math programs, reporting an overall tutoring effect size of d = 0.20" |
| d=+0.95 to +1.47 within-group gains (online tutoring) | [155] | VERIFIED | Iteration history: "large within-group effect sizes (d=+0.95 and d=+1.47)" |
| n=119 for [155] | [155] | VERIFIED | Iteration history: "119 struggling students" |
| n=over 500 for [255] | [255] | UNVERIFIED | Iteration history mentions "three U.S. middle schools" but does not specify n=over 500 |
| 4 percentage point increase in mastery (Tutor CoPilot) | [156] (should be [12]) | VERIFIED | Iteration history and source [12]: "4 percentage points more likely to master lesson topics" |
| n=1,800 for Tutor CoPilot RCT | [156] (should be [12]) | VERIFIED | Source [12]: "1,800 K-8 students" |
| 9 percentage point gain for lower-performing tutors | [156] (should be [12]) | VERIFIED | Iteration history: "9 percentage points for lower-rated tutors" |
| Dosage analysis n=188 elementary struggling readers | [156] | UNVERIFIED | Not found in iteration history for [156]; may be conflated from another source |
| Peer tutoring g=0.42 to 0.84 for math anxiety | [193] | UNVERIFIED | Iteration history does not contain these specific effect sizes; report claims QED with 420 students — not verifiable from provided history |
| n=420 middle school students for [193] | [193] | UNVERIFIED | Not found in iteration history |
| d=0.02 per 10 sessions (frequency association) | [211] | UNVERIFIED | Not explicitly stated in iteration history |
| d=-0.09 per 10 weeks (duration association) | [211] | UNVERIFIED | Not explicitly stated in iteration history |
| Peer tutoring Hedges g ~0.33 | [213] | UNVERIFIED | Not found verbatim in iteration history |
| ITS effect sizes d=0.09 to 0.27 | [228] | UNVERIFIED | Not found verbatim in iteration history; source [44] mentions ITS effects but no specific range cited in iterations |
| Annual cost below $750 per student for hybrid tutoring | [255] | VERIFIED | Iteration history: "at an annual cost below $750 per student" |

**Summary**: 9 VERIFIED, 8 UNVERIFIED, 0 FABRICATED. The "36 studies" claim for [211] is potentially inaccurate (iteration history says 101 studies), approaching FABRICATED but could reflect a subset count.

## Check 3 — Study Design Accuracy

For notes-sourced papers ([147]+), verifying against iteration history descriptions:

| Source | Report Label | Iteration History Description | Status |
|--------|-------------|-------------------------------|--------|
| [147] | "meta-analysis, 23 studies" | "Pellegrini et al.'s (2021) meta-analysis of 23 randomized studies" | ✅ OK |
| [155] | "RCT, n=119" | Iteration 1 says "quasi-experimental designs"; Iteration 2 says "quasi-experimental study" | ⚠️ **MISLABELLED** — iteration history consistently calls this a QED, not an RCT |
| [156] | "RCT, n=1800" (for Tutor CoPilot) | This is actually source [12] (Tutor CoPilot), which is labelled RCT in academic-DB. [156] itself is about talk-time feedback, also labelled RCT in academic-DB [not in numbered list but matching title]. | ⚠️ **MISATTRIBUTION** — correct design for wrong source number |
| [211] | "meta-analysis, 36 studies" | Iteration history: "synthesized 101 studies" — report says 36 | ⚠️ Study count discrepancy; design label "meta-analysis" is correct |
| [227] | "meta-analysis" | Iteration history: systematic review and meta-analysis | ✅ OK |
| [255] | "QED, n=varied" | Iteration history: "quasi-experimental studies" | ✅ OK |
| [206] | Not explicitly labelled in report | Supplementary source; iteration history references RCT | OK (not labelled) |
| [193] | "quasi-experimental study" in body; "QED" implied | Not described in iteration history with design label | UNVERIFIABLE |
| [201] | "QED" | Iteration history: implementation study | Plausible |
| [181] | "observational" | Iteration history: "observational" | ✅ OK |

**Key issues:**
1. **[155] labelled as RCT** in the Executive Summary but iteration history consistently describes it as quasi-experimental. The report body also mentions "propensity score matching" which confirms QED, not RCT.
2. **[156] misattributed** as the Tutor CoPilot study. The Tutor CoPilot study is [12] in the academic-DB.

## Check 4 — Sub-question Coverage

| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| 1 | What defines tutoring as an educational intervention in K-8 mathematics? | ✅ Fully covered | [211], [147] |
| 1 | What are the typical mathematics skills and outcomes targeted? | ✅ Fully covered | [211], [147] |
| 1 | What populations are most studied? | ✅ Fully covered | [211], [256], [193] |
| 2 | What are the baseline/comparison conditions? | ✅ Covered | [155], [201] |
| 2 | What alternative supplemental supports are used as comparators? | ✅ Partially covered | [228], [211], [227] |
| 3 | What tutoring models and delivery modes are utilized? | ✅ Fully covered | [147], [206], [213], [181], [155], [255] |
| 3 | Which learning mechanisms drive tutoring outcomes? | ✅ Covered | [211], [156], [193] |
| 4 | What is the quantitative evidence of tutoring impacts vs controls? | ✅ Fully covered | [211], [227], [147], [155], [255], [156] |
| 4 | How do effects vary by delivery model, student characteristics, or setting? | ✅ Covered | [211], [147], [255], [193] |
| 4 | How does tutoring compare with alternative interventions? | ✅ Partially covered | [228], [211], [227], [213] |
| 4 | What are limitations and trade-offs at scale? | ✅ Covered | [201], [156], Limitations section |

All tiers and sub-questions are addressed with cited evidence. No tier is completely uncovered.

## Check 5 — URL Integrity

All cited sources are notes-sourced ([147]+). Checking against supplementary sources list:

| # | URL in Bibliography | Supplementary Source URL | Status |
|---|---|---|---|
| [147] | https://www.semanticscholar.org/paper/d6300c1e71a0cadde609370e1d323f0d070a4aa0 | Same | ✅ OK |
| [155] | https://www.semanticscholar.org/paper/ca92b313f03626bc5592e7f07e66af6161124c94 | Same | ✅ OK |
| [156] | https://www.semanticscholar.org/paper/73e5fd02e1305f58df04515b8c4fb0c968f3d30f | Same | ✅ OK |
| [181] | https://www.semanticscholar.org/paper/c445c46ae66962c1a9e3edaad748026c5c78d821 | Same | ✅ OK |
| [193] | https://doi.org/10.3390/math10132360 | Same | ✅ OK |
| [201] | https://www.semanticscholar.org/paper/2099336e709eb7a4fd25e292db658370c10a344a | Same | ✅ OK |
| [206] | https://www.semanticscholar.org/paper/a1278e3b811ec8431c27636ab2867440dc020253 | Same | ✅ OK |
| [211] | https://doi.org/10.1002/14651858.CD012831.pub2 | Same | ✅ OK |
| [213] | https://doi.org/10.12973/EJMSTE/79805 | Same | ✅ OK |
| [227] | https://doi.org/10.3386/w27476 | Same | ✅ OK |
| [228] | https://arxiv.org/abs/2511.04997 | Same | ✅ OK |
| [236] | https://pubmed.ncbi.nlm.nih.gov/26419418/ | Same | ✅ OK |
| [255] | https://www.semanticscholar.org/paper/0a4178fb09903d66da6692cba393bc920a8b8422 | Same | ✅ OK |
| [256] | https://www.semanticscholar.org/paper/116d72e3b587a8aa2eb24d45a627f492b8ffce2b | Same | ✅ OK |
| [258] | https://pmc.ncbi.nlm.nih.gov/articles/PMC10543627 | Same | ✅ OK |
| [316] | https://www.semanticscholar.org/paper/8d56a9b8a7f0ca6eb8f2c4a45b304474be15182f | Same | ✅ OK |

No issues found.

## Recommended Fixes

1. **[CRITICAL] Correct misattribution of Tutor CoPilot findings**: The Tutor CoPilot RCT (Wang et al., 2024, n=1,800) is source [12] in the academic-DB, not [156]. Source [156] is Demszky et al. (2024), "Does Feedback on Talk Time Increase Student Engagement?" Either add [12] to the bibliography or correctly re-attribute the Tutor CoPilot claims.

2. **[CRITICAL] Fix study design label for [155]**: The report labels [155] (Chappell et al., 2015) as "RCT" in the Executive Summary, but the iteration history consistently describes it as a quasi-experimental design using propensity score matching. Change to QED throughout.

3. **[HIGH] Correct study count for [211]**: The report states "[211] meta-analyzed 36 studies" but the iteration history describes Dietrichson et al. (2017) as synthesizing "101 studies." Verify the correct number and correct the report.

4. **[HIGH] Verify and source the dosage analysis claim (n=188 struggling readers)**: The claim attributed to [156] about 188 elementary struggling readers does not match the title or known content of that source. Identify and cite the correct source or remove the claim.

5. **[MODERATE] Verify statistics for [193]**: The specific effect sizes (g=0.42 to 0.84) and sample size (n=420) for peer tutoring and math anxiety are not verifiable from the iteration history. Either provide the source verification or mark these as approximate.

6. **[MODERATE] Verify granular statistics from [211]**: The dosage-effect associations (d=0.02 per 10 sessions; d=-0.09 per 10 weeks) are not found in the iteration history. Verify against the primary source or remove.

7. **[LOW] Add ITS effect size source verification**: The d=0.09 to 0.27 range attributed to [228] for intelligent tutoring

---

## Score Summary

| Dimension | Score |
|-----------|-------|
| Citation–bibliography linkage | 16/20 |
| Statistic provenance | 13/25 |
| Study design accuracy | 5/15 |
| Sub-question coverage | 20/20 |
| URL integrity | 20/20 |
| **Overall** | **74/100** |
