# QA Audit: two_pass_delim_v1 — genai_math

**Score: 85/100**

---



## Audit Summary

The report is moderately trustworthy but has several notable issues. The most critical problems are: (1) the report omits key evidence from the iteration history, particularly the LLAMA LIMA living meta-analysis (Strohmaier et al., 2026) which was the strongest synthesis finding across all three iterations but is entirely absent from the final report and bibliography; (2) several statistics cited in the report are verifiable against the source list but a few cannot be fully confirmed; (3) the bibliography is clean with no orphan entries, and all inline citations match bibliography entries; (4) URL integrity is mostly sound with one issue. The report's conservative framing is appropriate given the thin evidence base, but by dropping the meta-analytic synthesis from the iteration history, it actually understates the available evidence while simultaneously relying on a narrower set of sources.

## Check 1 — Citation-Bibliography Linkage

**Inline citations found in report body:** [1], [3], [5], [9], [11], [13], [14], [17], [18], [35]

**Bibliography entries:** [1], [3], [5], [9], [11], [13], [14], [17], [18], [35]

- All 10 inline citations have corresponding bibliography entries. ✓
- All 10 bibliography entries are cited at least once in the report body. ✓
- **Title verification:**
  - [1] "The effect of ChatGPT on students' learning performance..." — matches source list. ✓
  - [3] "Artificial Intelligence in Elementary STEM Education..." — matches source list. ✓
  - [5] "Effective and Scalable Math Support: Experimental Evidence on the Impact of an AI Math Tutor in Ghana" — matches source list. ✓
  - [9] "Improving Student Learning with Hybrid Human-AI Tutoring..." — matches source list. ✓
  - [11] "Personalized Recommendations in EdTech..." — matches source list. ✓
  - [13] "ChatGPT-generated help produces learning gains equivalent to human tutor-authored help..." — matches source list. ✓
  - [14] "A national experiment reveals where a growth mindset improves achievement" — matches source list. ✓
  - [17] "Design and evaluation of ChatGPT-MWPS..." — matches source list. ✓
  - [18] "Digital learning using ChatGPT in elementary school mathematics learning..." — matches source list. ✓
  - [35] "An Examination of an Online Tutoring Program's Impact on Low-Achieving Middle School Students' Mathematics Achievement" — matches source list. ✓

No issues found.

## Check 2 — Statistic Provenance

| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| d=0.36 for AI math tutor in Ghana among completers | [5] | UNVERIFIED | Source [5] summary mentions "substantially higher math growth than controls" but the source list summary is truncated and does not contain "d=0.36" verbatim. However, iteration history references a Ghana AI math tutor study with "d=0.36" — this appears in the report but not in the pre-numbered source profile text. The iteration history does not mention [5] by number with d=0.36; it references Bastani et al., 2025 for a different study. The d=0.36 statistic for Ghana/Rori is not found verbatim in any iteration summary. |
| CIs [0.057, 0.347], [0.106, 0.381], [0.02, 0.70] for hybrid tutoring | [9] | UNVERIFIED | Source [9] summary mentions "improved math learning-process outcomes relative to standard software-only instruction" but does not contain these specific CI values in the truncated profile. Not found in iteration history either. |
| Tutor-to-student ratio 1:8 to 1:4, 0.36 workspaces/hour | [9] | UNVERIFIED | Not found in source [9] profile summary or iteration history. |
| 51 quasi-experimental or experimental studies in ChatGPT meta-analysis | [1] | VERIFIED | Source [1] profile states "meta-analysis of 51 quasi-experimental or experimental studies." ✓ |
| r=0.969 between cognitive engagement and intention to use | [17] | VERIFIED | Source [17] findings state "r = 0.969, p < 0.05." ✓ |
| n=52 students, 3 teachers for ChatGPT-MWPS | [17] | VERIFIED | Source [17] findings state "n=52 students; 3 teachers." ✓ |
| 60% higher total story engagement, 78% more completed stories | [11] | VERIFIED | Source [11] findings state "total story engagement rose by 60% (S.E. 17%), completed stories by 78%." ✓ |
| 8-month duration, two 30-minute weekly sessions for Ghana RCT | [5] | UNVERIFIED | Source [5] profile summary is truncated and does not contain these dosage details. Not found verbatim in iteration history. |
| N=274 for ChatGPT-generated hints study | [13] | VERIFIED | Source [13] findings state "N=274 analyzed." ✓ |
| "primary students ages 7-13" included in ChatGPT meta-analysis | [1] | VERIFIED | Source [1] population field states "Primary (ages 7–13), Secondary (ages 14–17), College (ages over 18)." ✓ |

**Summary:** 6 VERIFIED, 4 UNVERIFIED, 0 FABRICATED. The UNVERIFIED statistics relate primarily to [5] (Ghana RCT) and [9] (hybrid tutoring), where the specific numbers (d=0.36, confidence intervals, dosage details, operational efficiency) are not found in the truncated source profiles or iteration history. These may come from full-text reading not captured in the profiles.

## Check 3 — Study Design Accuracy

| Source | Report Label | Source List Label | Status |
|--------|-------------|-------------------|--------|
| [1] | Meta-analysis (implied) | Meta-Analysis / Systematic Review | ✓ OK |
| [3] | Systematic review (implied) | Meta-Analysis / Systematic Review | ✓ OK |
| [5] | RCT | Randomized Controlled Trial (RCT) | ✓ OK |
| [9] | QED (three-study quasi-experimental) | Quasi-Experimental Design | ✓ OK |
| [11] | RCT | Randomized Controlled Trial (RCT) | ✓ OK |
| [13] | RCT (implied comparative study) | Randomized Controlled Trial (RCT) | ✓ OK |
| [14] | Experiment (implied RCT) | Randomized Controlled Trial (RCT) | ✓ OK |
| [17] | QED | Quasi-Experimental Design (QED) | ✓ OK |
| [18] | Systematic review | Meta-Analysis / Systematic Review | ✓ OK |
| [35] | Mixed-methods (implied observational/tutoring study) | Mixed-Methods | ✓ OK |

No issues found.

## Check 4 — Sub-question Coverage

| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| Tier 1 | What counts as a generative AI tool in K-8 mathematics education? | COVERED — dedicated section "What Counts as Generative AI in This Literature" | [13], [17], [18], [9] |
| Tier 1 | Which K-8 mathematics outcomes are most relevant? | COVERED — section "Outcomes and Populations Studied Most Often" | [9], [17], [18] |
| Tier 1 | Which student populations and instructional settings have been studied most often? | COVERED — discussed in "Outcomes and Populations" section | [5], [9], [17], [1] |
| Tier 2 | How are the same K-8 math skills typically developed without generative AI? | PARTIALLY COVERED — brief mention of comparators but no deep discussion of non-AI pedagogy | [35], [11] |
| Tier 2 | What are the standard comparison conditions used in studies? | COVERED — dedicated "Baseline and Comparator Conditions" section | [5], [9], [35], [11] |
| Tier 2 | What prior evidence exists for alternative technologies? | PARTIALLY COVERED — [35] and [11] mentioned but limited depth | [35], [11] |
| Tier 3 | How are generative AI tools actually used in K-8 math instruction? | COVERED — "Implementation Features and Mechanisms" section | [5], [9], [17] |
| Tier 3 | What implementation features are described? | COVERED — dosage, teacher oversight, prompt design discussed | [5], [9], [17], [18], [3], [1] |
| Tier 3 | What learning mechanisms are proposed? | COVERED — feedback, scaffolding, guided practice discussed | [5], [9], [17] |
| Tier 4 | What is the evidence from experimental/quasi-experimental studies? | COVERED — dedicated section "Experimental and Quasi-Experimental Effects" | [5], [9], [17] |
| Tier 4 | Do effects vary by grade level, prior achievement, language status, etc.? | PARTIALLY COVERED — section acknowledges gap but provides minimal cited evidence | [5], [9], [1], [14] |
| Tier 4 | How do generative AI tools compare with established alternatives? | PARTIALLY COVERED — section "Comparison With Existing Non-AI Supports" exists but evidence is thin | [35], [11], [9] |
| Tier 4 | What tradeoffs, risks, or implementation constraints are reported? | PARTIALLY COVERED — mentioned in Limitations section but light on specific cited risk evidence | [5], [9], [1], [13] |

All tiers are at least partially addressed. Tier 2 and Tier 4 subgroup/comparator/risk sub-questions are the weakest. No tier is completely unaddressed.

## Check 5 — URL Integrity

| # | Bibliography URL | Source List URL | Status |
|---|-----------------|-----------------|--------|
| [1] | https://doi.org/10.1057/s41599-025-04787-y | https://doi.org/10.1057/s41599-025-04787-y | OK |
| [3] | https://arxiv.org/abs/2511.00105v2 | https://arxiv.org/abs/2511.00105v2 | OK |
| [5] | not_reported | not_reported | OK |
| [9] | https://doi.org/10.1145/3636555.3636896 | https://doi.org/10.1145/3636555.3636896 | OK |
| [11] | https://arxiv.org/abs/2208.13940 | https://arxiv.org/abs/2208.13940 | OK |
| [13] | https://doi.org/10.1371/journal.pone.0304013 | https://doi.org/10.1371/journal.pone.0304013 | OK |
| [14] | https://doi.org/10.1038/s41586-019-1466-y | https://doi.org/10.1038/s41586-019-1466-y | OK |
| [17] | https://doi.org/10.1186/s40561-025-00419-9 | https://doi.org/10.1186/s40561-025-00419-9 | OK |
| [18] | http://ijeecs.iaescore.com | http://ijeecs.iaescore.com | OK |
| [35] | https://doi.org/10.24059/olj.v19i5.694 | https://doi.org/10.24059/olj.v19i5.694 | OK |

No issues found.

## Recommended Fixes

1. **[HIGH] Add the LLAMA LIMA living meta-analysis (Strohmaier et al., 2026).** This was the single strongest synthesis finding across all three iterations (g = 0.31, CI [0.06, 0.58], 15–21 studies) and is referenced prominently in every iteration summary. Its omission from the final report is the most significant evidence gap. It should be added as a supplementary source [191] and cited in the executive summary and experimental effects section.

2. **[HIGH] Verify and document the provenance of the d=0.36 statistic for the Ghana RCT [5].** This is the report's anchor finding but cannot be verified against the truncated source profile or any iteration history excerpt. The report should either cite the full-text source for this statistic or flag it as drawn from full-text review not captured in the profile summaries.

3. **[HIGH] Verify and document the confidence intervals [0.057, 0.347], [0.106, 0.381], [0.02, 0.70] and the 0.36 workspaces/hour operational efficiency estimate for [9].** These specific statistics are not found in the source profile or iteration history. The same verification recommendation applies.

4. **[MEDIUM] Add Hwang (2022) meta-analysis on AI and elementary math achievement.** This was cited in iterations 2 and 3 (overall effect 0.351, 21 studies, 30 samples, grade and topic as moderators) and is directly K-8 math relevant. It corresponds to supplementary source [286] and should be incorporated.

5. **[MEDIUM] Incorporate the Bastani et al. (2025) cautionary finding.** Iterations 2 and 3 prominently cite this study for showing that unrestricted AI access can harm learning once the tool is removed. This is a critical Tier 4 risk finding that the final report's limitations section underrepresents.

6. **[LOW] Strengthen Tier 4 subgroup coverage.** The report correctly flags sparse subgroup evidence but could cite Hwang (2022) for grade-level and topic moderation and iteration-history references to achievement-level heterogeneity to provide more concrete anchoring.

7. **[LOW] Clarify the 8-month/twice-weekly dosage claim for [5].** These implementation details are stated as fact but cannot be traced to the source profile. Either verify from full text or qualify as "as reported in the study."

## Score

| Dimension | Max | Score | Rationale (1 sentence) |
|-----------|-----|-------|------------------------|
| Citation–bibliography linkage | 20 | 20 | All inline citations match bibliography entries with no orphans in either direction. |
| Statistic provenance | 25 | 15 | 6 of 10 statistics verified (60%); 4 unverified statistics relate to the two most-cited sources [5] and [9], which is concerning given their centrality. |
| Study design accuracy | 15 | 15 | All study design labels match the source list entries exactly. |
| Sub-question coverage | 20 | 15 | All 4 tiers addressed but Tier 2 and several Tier 4 sub-questions are only partially covered with thin cited evidence (approximately 3 of 4 tiers fully or substantially covered). |
| URL integrity | 20 | 20 | All 10 bibliography URLs match their source list entries exactly. |
| **Overall** | **100** | **85** | |

---

## Score Summary

| Dimension | Score |
|-----------|-------|
| Citation–bibliography linkage | 20/20 |
| Statistic provenance | 15/25 |
| Study design accuracy | 15/15 |
| Sub-question coverage | 15/20 |
| URL integrity | 20/20 |
| **Overall** | **85/100** |
