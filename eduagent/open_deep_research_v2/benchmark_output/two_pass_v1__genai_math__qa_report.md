\# QA Audit: two_pass_v1 — genai_math

**Score: 52/100**

---



## Audit Summary

The report is largely trustworthy in its cautious framing and directional conclusions, but it suffers from a critical structural deficiency: the Bibliography section states "No sources cited," meaning there is no formal bibliography table at all despite extensive inline citations throughout the report body. This makes it impossible to verify citation-bibliography linkage, URL integrity against a bibliography, or confirm titles match. The report relies entirely on inline parenthetical citations using short titles rather than numbered references, which creates ambiguity. Statistic provenance is generally strong — most key numbers can be traced to the pre-numbered source list findings. Study design labels are mostly accurate. Sub-question coverage is reasonably thorough across all tiers, though Tier 4 subgroup questions remain thin. The single most critical issue is the absent bibliography.

## Check 1 — Citation-Bibliography Linkage

**Critical Issue:** The Bibliography section explicitly states "No sources cited." There is no bibliography table in the report. All inline citations are given as parenthetical short-title references rather than numbered [N] references. Since there is no bibliography table, every inline citation is technically an orphan — it cannot be linked to a bibliography entry.

Inline citations found in the report body (mapped to source list numbers where identifiable):

| Inline Citation (Short Title) | Likely Source # | In Bibliography? |
|-------------------------------|----------------|-----------------|
| Do intelligent tutoring systems benefit K-12 students?, n.d. | Not clearly in source list (no exact match by title in [1]-[174]) | NO |
| Tutor CoPilot, 2024 | [131] | NO |
| Improving Student Learning with Hybrid Human-AI Tutoring, 2024 | [57] | NO |
| The effect of ChatGPT on students' learning performance…, 2025 | [46] | NO |
| Current practices and future direction of AI in mathematics education, 2025 | [14] | NO |
| Unveiling the potential, 2024 | [105] | NO |
| A Scoping Survey of ChatGPT in Mathematics Education, 2025 | [13] | NO |
| Digital learning using ChatGPT in elementary school mathematics learning, 2024 | [118] | NO |
| Question Personalization in an Intelligent Tutoring System, 2022 | [119] | NO |
| Personalized Recommendations in EdTech, 2022 | [52] | NO |
| Design and evaluation of ChatGPT-MWPS, 2025 | [6] | NO |
| Interacting with educational chatbots, 2022 | [43] | NO |
| ChatGPT-generated help produces learning gains equivalent…, 2024 | [99] | NO |
| Learning gain differences between ChatGPT and human tutor generated algebra hints, 2023 | [28] | NO |
| AI tutoring can safely and effectively support students, 2025 | [82] | NO |
| Improving rational number knowledge using the NanoRoboMath digital game, 2022 | [35] | NO |
| Investigating Students' Preferences for AI Roles in Mathematical Modelling, 2025 | [48] | NO |

**All inline citations are orphans** because the bibliography is empty. This is a severe structural failure.

## Check 2 — Statistic Provenance

| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| 4 percentage points more likely to pass exit ticket (62% vs 58%) | Tutor CoPilot [131] | VERIFIED | Matches finding: "4 percentage point increase in exit-ticket pass rate" and "62%" vs controls |
| 4,136 tutoring sessions | Tutor CoPilot [131] | VERIFIED | Matches finding: "n=4136 sessions" |
| 1,800 students; 900 tutors at study launch, 782 tutors in launch sample | Tutor CoPilot [131] | VERIFIED | Matches finding: "1,800 students; 900 tutors (study launch sample n=782 tutors)" |
| 550,000+ messages and 2,000+ system uses | Tutor CoPilot [131] | VERIFIED | Matches finding: "NLP analysis of 550,000+ messages and 2,000+ uses" |
| β=0.202 (Site 1, hybrid tutoring) | Hybrid Human-AI Tutoring [57] | VERIFIED | Matches finding: "β=0.202 (Site 1 time spent)" |
| 0.36 more workspaces per hour | Hybrid Human-AI Tutoring [57] | VERIFIED | Matches finding: "0.36 additional workspaces per hour" |
| Time on task from 24 to 33 minutes (Site 2) | Hybrid Human-AI Tutoring [57] | VERIFIED | Matches finding: "24 to 33 minutes/week (Site 2 descriptive change)" |
| CI=[0.057, 0.347] for tutoring effect | Hybrid Human-AI Tutoring [57] | VERIFIED | Matches finding: "CI=Site 1: [0.057, 0.347]" |
| Sites n=125, n=385, n=75 | Hybrid Human-AI Tutoring [57] | VERIFIED | Matches finding: "n=125; n=385; n=75" |
| r=0.969 (ChatGPT-MWPS, cognitive engagement to intention) | ChatGPT-MWPS [6] | VERIFIED | Matches finding: "effect=r=0.969" |
| n=52 students (ChatGPT-MWPS) | ChatGPT-MWPS [6] | VERIFIED | Matches finding: "n=52" |
| n=274 overall, n=98 ChatGPT condition (ChatGPT help study) | ChatGPT hints [99] | PARTIALLY VERIFIED | n=274 matches; n=98 for the ChatGPT condition is not explicitly stated in findings (findings say "274 participants" across 3 conditions but do not break out n=98 for ChatGPT) |
| n=77 (algebra hints study) | Algebra hints [28] | VERIFIED | Matches finding: "n=77 overall" |
| 5.5 percentage-point increase for knowledge transfer (LearnLM) | AI tutoring [82] | VERIFIED | Matches finding: "effect=5.5 percentage-point increase for knowledge transfer" |
| n=165 (LearnLM) | AI tutoring [82] | VERIFIED | Matches finding: "n=165" |
| ηp²=0.04 conceptual knowledge, ηp²=0.03 operations (NanoRoboMath) | NanoRoboMath [35] | VERIFIED | Matches finding: "effect=ηp²=0.04 (conceptual composite); ηp²=0.03 (operations)" |
| n=195 (NanoRoboMath) | NanoRoboMath [35] | VERIFIED | Matches finding: "n=195" |
| n=110 experimental-group students (NanoRoboMath regressions) | NanoRoboMath [35] | VERIFIED | Matches finding: "n=110 experimental-group students in regression analyses" |
| n=7,750 (Personalized Recommendations) | Personalized Recs [52] | VERIFIED | Matches finding: "n=7750 randomized" |
| 14% increase total story engagement; 60% in recommended section | Personalized Recs [52] | VERIFIED | Matches finding: "14% increase in Total Story Engagement" and "60% increase in Total Story Engagement" in recommended section |
| n=470 total (Question Personalization) | Question Personalization [119] | VERIFIED | Matches finding: "n=470 total in test groups" |
| Expected n=190, non-expected n=139, control n=141 | Question Personalization [119] | VERIFIED | Matches finding: "expected n=190, non-expected n=139, control n=141" |
| 51 studies (ChatGPT meta-analysis) | ChatGPT effect [46] | UNVERIFIED | The source summary says it's a meta-analysis but does not explicitly state "51 studies" in the pre-numbered source entry. However, it is plausible from the description "51 quasi-experimental and experimental studies" — this likely comes from iteration history or the full paper. Marking as UNVERIFIED since not in extracted profile. |
| 17.00% learning gain ChatGPT condition, 11.62% human condition | ChatGPT hints [99] | VERIFIED | Matches finding: "ChatGPT hints showed a statistically significant pre-to-post learning gain of 17.00% (p < 0.001), compared with 11.62% for h..." |
| 31 studies (Unveiling the potential review) | Unveiling potential [105] | UNVERIFIED | The source summary mentions "systematic review of 31 studies" but this specific number is not in the extracted findings. It is in the summary text of source [105]. Marking as borderline VERIFIED from summary. |

**Summary:** 22 VERIFIED, 1 PARTIALLY VERIFIED (n=98 breakdown), 2 UNVERIFIED (51 studies count; 31 studies count — both plausible from summaries but not in explicit findings). 0 FABRICATED.

## Check 3 — Study Design Accuracy

| Study | Report Label | Source List Label | Status |
|-------|-------------|-------------------|--------|
| Tutor CoPilot [131] | RCT | RCT | ✅ CORRECT |
| Improving Student Learning with Hybrid Human-AI Tutoring [57] | QED | QED | ✅ CORRECT |
| ChatGPT-generated help [99] | RCT | RCT | ✅ CORRECT |
| Learning gain differences ChatGPT algebra hints [28] | RCT | RCT | ✅ CORRECT |
| AI tutoring can safely and effectively support students [82] | RCT (implied: "randomized trial") | RCT | ✅ CORRECT |
| Design and evaluation of ChatGPT-MWPS [6] | "QED/design study" | QED | ✅ CORRECT (report appropriately hedges) |
| Improving rational number knowledge NanoRoboMath [35] | QED | QED | ✅ CORRECT |
| Personalized Recommendations in EdTech [52] | RCT | RCT | ✅ CORRECT |
| Question Personalization in ITS [119] | "QED/A/B test" | QED | ✅ CORRECT |
| The effect of ChatGPT on students' learning performance [46] | "meta-analysis" | Meta-Analysis / Systematic Review | ✅ CORRECT |
| Unveiling the potential [105] | "meta-analysis" | Meta-Analysis / Systematic Review | ✅ CORRECT |
| Interacting with educational chatbots [43] | Not explicitly labeled | Meta-Analysis / Systematic Review | OK (no mislabel) |
| A Scoping Survey of ChatGPT in Mathematics Education [13] | Described as scoping/descriptive | Meta-Analysis / Systematic Review | ✅ CORRECT |
| Investigating Students' Preferences for AI Roles [48] | Described as "within-subjects RCT" (in equity section) | RCT | ✅ CORRECT |
| Digital learning using ChatGPT in elementary school [118] | "meta-analysis, elementary" | Meta-Analysis / Systematic Review | ✅ CORRECT |

**"Do intelligent tutoring systems benefit K-12 students?"** — This study is cited frequently but does not have an obvious exact match in the [1]-[174] pre-numbered source list. The title and description (meta-analysis of ITS in K-12 U.S.) do not match any entry I can identify. It may be a supplementary source that was not numbered, or it may correspond to an unlisted source. The report labels it as "meta-analysis" which is consistent with the iteration history descriptions. **FLAG: Source identification uncertain.**

No mislabelling found.

## Check 4 — Sub-question Coverage

| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| Tier 1 | How are generative AI tools for K-8 math defined? | ✅ Fully covered | Current practices [14]; Unveiling [105]; Scoping Survey [13] |
| Tier 1 | Which math outcomes are studied for K-8? | ✅ Covered | ChatGPT effect [46]; Digital learning [118]; ChatGPT-MWPS [6] |
| Tier 1 | What K-8 populations and contexts are included? | ⚠️ Partially covered | Digital learning [118]; discussed generally but thin on specific populations |
| Tier 2 | How are K-8 math skills developed without GenAI? | ✅ Covered | ITS meta-analysis; NanoRoboMath [35]; Question Personalization [119] |
| Tier 2 | Alternative digital/classroom approaches? | ✅ Covered | ITS meta-analysis; Personalized Recs [52]; NanoRoboMath [35] |
| Tier 2 | What is the relevant counterfactual? | ✅ Covered | Hybrid tutoring [57]; ChatGPT hints [99]; algebra hints [28]; Personalized Recs [52] |
| Tier 3 | How are GenAI tools actually used in K-8 math? | ⚠️ Partially covered | ChatGPT-MWPS [6]; Tutor CoPilot [131]; noted as thin |
| Tier 3 | What learning mechanisms are proposed? | ✅ Covered | Tutor CoPilot [131]; Hybrid tutoring [57]; discussed in mechanisms section |
| Tier 3 | What implementation conditions affect use? | ✅ Covered | Tutor CoPilot [131]; Hybrid tutoring [57]; Interacting with chatbots [43] |
| Tier 4 | Direct evidence from RCTs/QEDs on K-8 math outcomes? | ✅ Covered (answer: insufficient evidence) | Tutor CoPilot [131]; Hybrid tutoring [57]; ChatGPT hints [99]; algebra hints [28] |
| Tier 4 | Which math outcomes improve most consistently? | ✅ Covered | Engagement vs achievement discussed; ChatGPT-MWPS [6]; Personalized Recs [52] |
| Tier 4 | How do effects vary by grade, prior achievement, etc.? | ⚠️ Partially covered | ITS meta-analysis; Question Personalization [119]; AI roles [48]; flagged as largely unresolved |
| Tier 4 | Tradeoffs, risks, limitations? | ✅ Covered | Tutor CoPilot [131]; algebra hints [28]; ChatGPT effect [46]; Interacting with chatbots [43] |

**Summary:** 10/13 sub-questions fully covered; 3 partially covered (Tier 1 populations, Tier 3 actual use patterns, Tier 4 differential effects). All tiers have at least partial coverage with cited evidence.

## Check 5 — URL Integrity

Since the bibliography states "No sources cited," there is no bibliography URL table to verify. However, I can verify that the studies cited inline correspond to real entries in the pre-numbered source list:

| Source | Source List URL | Status |
|--------|----------------|--------|
| [6] ChatGPT-MWPS | https://doi.org/10.1186/s40561-025-00419-9 | OK (matches source list) |
| [13] Scoping Survey | https://doi.org/10.1007/s40751-025-00172-1 | OK |
| [14] Current practices | https://www.iejme.com | OK |
| [28] Algebra hints | https://arxiv.org/abs/2302.06871v1 | OK |
| [35] NanoRoboMath | https://doi.org/10.1007/s10649-021-10120-6 | OK |
| [43] Interacting with chatbots | https://doi.org/10.1007/s10639-022-11177-3 | OK |
| [46] ChatGPT effect meta-analysis | https://doi.org/10.1057/s41599-025-04787-y | OK |
| [48] AI Roles

---

## Score Summary

| Dimension | Score |
|-----------|-------|
| Citation–bibliography linkage | 0/20 |
| Statistic provenance | 22/25 |
| Study design accuracy | 15/15 |
| Sub-question coverage | 15/20 |
| URL integrity | 0/20 |
| **Overall** | **52/100** |
