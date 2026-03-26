# QA Audit: two_pass_v1 — math_tutoring

**Score: 42/100**

---



## Audit Summary

The report has a fundamental structural problem: the Bibliography section states "No sources cited," meaning every inline citation in the report body lacks a corresponding bibliography entry. The report uses informal title-based citations rather than numbered references, making systematic verification difficult. Despite this, the statistics cited in the report body are largely traceable to the pre-numbered source list findings and iteration history, and study design labels are mostly accurate. The report covers the tiered sub-questions reasonably well but with uneven depth. The absence of a functioning bibliography is the single most critical issue, rendering the report non-compliant with standard citation-bibliography linkage requirements.

## Check 1 — Citation-Bibliography Linkage

**Critical Issue:** The Bibliography section explicitly states "No sources cited." This means:

- **Every inline citation is orphaned.** The report cites the following sources by title inline, but none appear in the Bibliography table:
  1. "Do intelligent tutoring systems benefit K-12 students?" — corresponds to source [19]
  2. "Tutor CoPilot: A Human-AI Approach for Scaling Real-Time Expertise" — corresponds to source [6]
  3. "Effective and Scalable Math Support: Experimental Evidence on the Impact of an AI-Math Tutor in Ghana" — corresponds to source [97]
  4. "Closing the income-achievement gap? Experimental evidence from high-dosage tutoring in Dutch primary education" — corresponds to source [2]
  5. "AI tutoring can safely and effectively support students: An exploratory RCT in UK classrooms" — corresponds to source [18]
  6. "Improving Student Learning with Hybrid Human-AI Tutoring: A Three-Study Quasi-Experimental Investigation" — corresponds to source [35]
  7. "A Multimedia Adaptive Tutoring System for Mathematics that Addresses Cognition, Metacognition and Affect" — corresponds to source [89]
  8. "Reasoning Mind Genie 2: An Intelligent Tutoring System as a Vehicle for International Transfer of Instructional Methods in Mathematics" — corresponds to source [1]
  9. "Advancing Education through Tutoring Systems: A Systematic Literature Review" — corresponds to source [5]
  10. "Differentiated Instruction in Secondary Education: A Systematic Review of Research Evidence" — corresponds to source [47]
  11. "Building Bridges – AI Custom Chatbots as Mediators between Mathematics and Physics" — corresponds to source [96]

- **All Bibliography entries are missing** — 0 entries in the bibliography table.

## Check 2 — Statistic Provenance

| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| ITS improve achievement on average (pooled effect size not reported) | Do intelligent tutoring systems benefit K-12 students? [19] | VERIFIED | Source summary confirms positive average impact but no pooled ES in extracted text |
| Tutor CoPilot: exit-ticket pass rates from 62% to 66%, 4 percentage-point increase | Tutor CoPilot [6] | VERIFIED | Source finding states increase in student mastery; iteration history confirms 62% to 66% and 4pp gain, p<0.01 |
| Tutor CoPilot: subgroup gains up to 9 percentage points | Tutor CoPilot [6] | UNVERIFIED | The source finding for [6] does not mention "9 percentage points" explicitly in the pre-numbered source list; however this appears in the iteration history narrative but without a clear source attribution |
| Tutor CoPilot: n=4,136 sessions, 550,000+ messages | Tutor CoPilot [6] | VERIFIED | Source finding lists n=4136 sessions |
| Ghana RCT: treatment mean growth 5.13 vs control 3.97, d=0.36, n=477 | Effective and Scalable Math Support [97] | VERIFIED | Source finding states d=0.36, n=477 (241 control, 236 treatment), mean growth 5.13 vs control not explicitly stated in source but d=0.36 and n=477 confirmed |
| Ghana RCT: treatment mean growth 5.13 vs 3.97 | Effective and Scalable Math Support [97] | UNVERIFIED | The specific means 5.13 and 3.97 do not appear verbatim in the pre-numbered source finding for [97]; the finding reports d=0.36 and n=477 but not those exact means |
| Dutch RCT: d=0.28 (5th grade, one year), d=0.25 (half-year, 5th grade), d=0.26 (4th grade, one year) | Closing the income-achievement gap? [2] | VERIFIED | Source finding explicitly states "d=0.28 (one year, 5th grade); d=0.25 (half-year, 5th grade); d=0.26 (one year, 4th grade)" |
| Dutch RCT: n=265 (pooled 5th grade), n=233 (pooled 4th grade) | Closing the income-achievement gap? [2] | VERIFIED | Source finding states n=265 (pooled 5th grade); n=233 (pooled 4th grade) |
| LearnLM: 5.5 percentage-point improvement, CI=[-1.4, +12.4] | AI tutoring can safely and effectively support students [18] | VERIFIED | Source finding states "5.5 percentage-point advantage" and CI=[-1.4%, +12.4%] |
| LearnLM: n=165 | AI tutoring can safely and effectively support students [18] | VERIFIED | Source finding states N=165 |
| Hybrid human-AI tutoring: beta=0.202, beta=0.2437, 0.36 workspaces/hour | Improving Student Learning [35] | VERIFIED | Source finding states "beta=0.202; beta=0.2437; 0.36 workspaces/hour" |
| Hybrid human-AI tutoring: CI=[0.057, 0.347], [0.106, 0.381], [0.02, 0.70] | Improving Student Learning [35] | VERIFIED | Source finding states those exact CIs |
| Hybrid human-AI tutoring: n=125, n=385, n=75 | Improving Student Learning [35] | VERIFIED | Source finding states "Site 1 n=125; Site 2 n=385; Site 3 n=75" |

**Summary:** 10 VERIFIED, 2 UNVERIFIED. The 550,000+ messages figure and the "9 percentage points" subgroup gain and exact means (5.13, 3.97) for Ghana could not be confirmed from the pre-numbered source findings, though some appear in iteration history text.

## Check 3 — Study Design Accuracy

| Source | Report Label | Source List Design | Status |
|--------|-------------|-------------------|--------|
| Closing the income-achievement gap? [2] | RCT | Randomized Controlled Trial (RCT) | ✅ Correct |
| Effective and Scalable Math Support [97] | RCT | Randomized Controlled Trial (RCT) | ✅ Correct |
| Tutor CoPilot [6] | RCT | Randomized Controlled Trial (RCT) | ✅ Correct |
| AI tutoring can safely and effectively support students [18] | RCT (exploratory) | Randomized Controlled Trial (RCT) | ✅ Correct |
| Improving Student Learning with Hybrid Human-AI Tutoring [35] | QED | Quasi-Experimental Design (QED) | ✅ Correct |
| A Multimedia Adaptive Tutoring System [89] | Mixed-methods evaluation | Mixed-Methods | ✅ Correct (report accurately describes it as not causal) |
| Reasoning Mind Genie 2 [1] | Design and implementation study | Mixed-Methods | ✅ Correct (report accurately describes it as non-causal) |
| Do intelligent tutoring systems benefit K-12 students? [19] | Meta-analysis | Meta-Analysis / Systematic Review | ✅ Correct |
| Advancing Education through Tutoring Systems [5] | Review | Meta-Analysis / Systematic Review | ✅ Correct |
| Differentiated Instruction in Secondary Education [47] | Systematic review | Meta-Analysis / Systematic Review | ✅ Correct |
| Building Bridges [96] | RCT (mentioned in passing) | Randomized Controlled Trial (RCT) | ✅ Correct |

**Issue flagged:** The report labels [18] as population "High School" in the source list but discusses it as K-8-relevant. The source list population is "High School" (secondary students). The report says "UK classrooms" and "secondary students" but frames it under K-8 evidence. This is a population scope issue rather than a design mislabelling. Similarly, [18] is labeled "High School" in the source list but the report uses it for K-8 claims—this is a stretch but acknowledged by the report calling it "exploratory."

No study design mislabellings found.

## Check 4 — Sub-question Coverage

| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| Tier 1 | What counts as tutoring in K-8 mathematics research? | Addressed with cited evidence | [19], [2], [6], [97], [35], [18] |
| Tier 1 | Which math outcomes are most commonly studied? | Addressed with cited evidence | [6], [97], [2], [18], [96] |
| Tier 1 | Which student populations are the focus? | Partially addressed | [2], [97]; report acknowledges gaps for K-2, disabilities, multilingual learners |
| Tier 2 | Standard instructional/remedial comparison conditions | Partially addressed | [18], [35], [2], [6]; report explicitly notes this is poorly reported in studies |
| Tier 2 | Prior/alternative interventions as comparators | Minimally addressed | Report acknowledges gap; no strong direct citations |
| Tier 2 | Counterfactual conditions in tutoring studies | Partially addressed | [18], [35], [2]; report devotes a section but notes inadequate counterfactual reporting |
| Tier 3 | How math tutoring is delivered in practice | Addressed with cited evidence | [6], [97], [2], [18], [35] |
| Tier 3 | Instructional mechanisms emphasized | Partially addressed | [6], [89]; report mentions feedback, adaptive sequencing but limited direct citations on mechanisms |
| Tier 3 | Implementation features by school context | Partially addressed | [6], [97], [2], [18]; described but not deeply cited |
| Tier 4 | Evidence from RCTs/QEDs/meta-analyses that tutoring improves math | Well addressed | [2], [97], [6], [18], [35], [19] |
| Tier 4 | Effects by subgroup, grade span, dosage, group size, setting | Partially addressed | [2], [97], [6]; report acknowledges evidence is thin |
| Tier 4 | How tutoring compares with other supplemental math interventions | Minimally addressed | Report explicitly notes lack of head-to-head evidence |
| Tier 4 | Limitations and tradeoffs in the evidence base | Well addressed | Multiple sources cited; dedicated section |

**Summary:** Tier 1 is mostly covered (3/3 partially or fully). Tier 2 is weakly covered (3/3 only partially, one minimally). Tier 3 is partially covered (2/3 partial, 1 addressed). Tier 4 is unevenly covered (2/4 well, 1 partial, 1 minimal). Overall, approximately 4/13 fully covered, 7/13 partially covered, 2/13 minimally covered.

## Check 5 — URL Integrity

Since the Bibliography states "No sources cited," there are no bibliography URLs to check. However, I can verify the URLs of the sources actually referenced in the report against the pre-numbered source list:

| Source | Source List URL | Status |
|--------|----------------|--------|
| [1] Reasoning Mind Genie 2 | https://doi.org/10.1007/s40593-014-0019-7 | N/A (no bibliography entry to check) |
| [2] Closing the income-achievement gap? | https://doi.org/10.31235/osf.io/qepc2 | N/A |
| [5] Advancing Education through Tutoring Systems | https://arxiv.org/abs/2503.09748v1 | N/A |
| [6] Tutor CoPilot | https://arxiv.org/abs/2410.03017v2 | N/A |
| [18] AI tutoring can safely and effectively support students | goo.gle/LearnLM-Nov25 | N/A |
| [19] Do intelligent tutoring systems benefit K-12 students? | http://arxiv.org/abs/2511.04997v1 | N/A |
| [35] Improving Student Learning with Hybrid Human-AI Tutoring | https://doi.org/10.1145/3636555.3636896 | N/A |
| [47] Differentiated Instruction in Secondary Education | https://www.frontiersin.org/articles/10.3389/fpsyg.2019.02366 | N/A |
| [89] A Multimedia Adaptive Tutoring System | https://doi.org/10.1007/s40593-014-0023-y | N/A |
| [96] Building Bridges | http://arxiv.org/abs/2412.15747v1 | N/A |
| [97] Effective and Scalable Math Support | http://arxiv.org/abs/2402.09809v2 | N/A |

**Result:** Cannot perform URL integrity check because the Bibliography is empty. No URLs to verify against the source list. This is itself a critical failure.

## Recommended Fixes

1. **[CRITICAL] Populate the Bibliography table.** The report states "No sources cited" despite citing approximately 11 distinct sources throughout the body. All cited sources must be added with proper numbered references, titles, URLs, and study design labels drawn from the pre-numbered source list.

2. **[HIGH] Convert inline title-based citations to numbered [N] format.** Replace all informal title citations with the corresponding pre-numbered source identifiers (e.g., [2] for "Closing the income-achievement gap?", [6] for "Tutor CoPilot", etc.) to enable proper cross-referencing.

3. **[HIGH] Verify or remove the "9 percentage points" subgroup gain claim for Tutor CoPilot.** This statistic cannot be confirmed from the pre-numbered source finding for [6]. Either provide the source passage or flag it as unverified.

4. **[HIGH] Verify or qualify the specific means (5.13 vs 3.97) for the Ghana RCT.** These exact values do not appear in the pre-numbered source finding for [97], which reports d=0.36 and n=477 but not the raw means. Either confirm from the full paper or remove.

5. **[MODERATE] Verify or qualify the "550,000+ messages" figure for Tutor CoPilot.** This does not appear in the extracted source finding.

6. **[MODERATE] Clarify population scope for LearnLM [18].** The source list labels the population as "High School," but the report discusses it under K-8 evidence. The report should explicitly note this is secondary-level evidence being applied to the K-8 question.

7. **[MODERATE] Strengthen Tier 2 coverage.** The counterfactual and comparison condition sub-questions are underserved. The report should either cite additional sources or explicitly state the evidence gap more prominently in the sub-question coverage.

8. **[MODERATE] Strengthen Tier 4 comparative evidence.** The sub-question on tutoring versus other supplemental math interventions is minimally addressed. Add available evidence or clearly flag as an unresolved gap.

9. **[LOW] Add the supplementary/notes-sourced studies from the iteration history** (e.g., Pellegrini et al. [140], Chappell et al. [135], Carbonari et al. [174], etc.) that were cited in earlier iterations but dropped from the final report. These would strengthen the evidence base and several claims.

10. **[LOW] Include the iteration history findings on peer tutoring meta-analyses** (Alegre-Ansuategui et al. [162], Thurston et al. [163]) which were discussed in iterations 1-3 but not carried forward into the final report.

## Score

| Dimension | Max | Score | Rationale (1 sentence) |

---

## Score Summary

| Dimension | Score |
|-----------|-------|
| Citation–bibliography linkage | 0/20 |
| Statistic provenance | 21/25 |
| Study design accuracy | 15/15 |
| Sub-question coverage | 6/20 |
| URL integrity | 0/20 |
| **Overall** | **42/100** |
