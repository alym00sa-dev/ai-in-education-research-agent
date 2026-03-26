# QA Audit: post-refactor-v1 — math_tutoring

**Score: 62/100**

---



## Audit Summary

The report is largely trustworthy in its core claims about tutoring effectiveness for K-8 math, drawing on legitimate high-quality sources. However, several significant issues were identified: (1) multiple inline citations reference sources that are absent from the Bibliography table (citations [1], [2], [18], [125], [156]), creating orphan inline references; (2) source [1] and [2] are cited for peer tutoring claims but the PreScoredTiers entries for [1] and [2] are about ADHD medication and ITS authoring tools respectively—not peer tutoring—representing a serious mismatch; (3) the source [19] in the Bibliography is attributed to a paper about tutor discourse and math achievement prediction, but the PreScoredTiers entry [19] describes a study on using LLMs to assess tutors' reactions to student math errors (while [57] matches the URL/title cited in the Bibliography for [19]); (4) several statistics could not be verified verbatim from iteration history or source summaries; and (5) one Bibliography URL differs from its PreScoredTiers counterpart. These issues collectively undermine confidence in the referencing accuracy, though the substantive conclusions about tutoring efficacy are well-supported by the underlying evidence.

---

## Check 1 — Citation-Bibliography Linkage

**Inline citations missing from Bibliography:**
- **[1]** — Cited inline (peer tutoring) but absent from Bibliography table.
- **[2]** — Cited inline (peer tutoring) but absent from Bibliography table.
- **[18]** — Cited inline (alternative interventions section) but absent from Bibliography table.
- **[125]** — Cited inline (alternative supports, achievement gap) but absent from Bibliography table.
- **[156]** — Cited inline (tutor move taxonomy, Tier 3 mechanisms) but absent from Bibliography table.

**Bibliography entries with no inline citation (orphans):**
- None found — all Bibliography entries ([22], [24], [26], [27], [28], [31], [19], [124]) are cited inline.

**Title/URL mismatches between Bibliography and PreScoredTiers:**
- **[19]**: The Bibliography lists the title "Aligning Tutor Discourse Supporting Rigorous Thinking with Tutee Content Mastery for Predicting Math Achievement" with URL `https://arxiv.org/abs/2402.02660`. In the PreScoredTiers, entry [19] is titled "Using Large Language Models to Assess Tutors' Performance in Reacting to Students Making Math Errors" with URL `https://arxiv.org/abs/2401.03238`. The Bibliography entry for [19] actually matches PreScoredTiers entry **[57]**. This is a **MISMATCH**.
- **[24]**: Bibliography URL is `https://arxiv.org/abs/2503.09748`; PreScoredTiers URL is `https://arxiv.org/abs/2503.09748v1`. Minor version discrepancy — substantively OK.

**Critical content mismatch:**
- **[1]**: PreScoredTiers [1] is "A systematic review and economic model of the effectiveness and cost-effectiveness of methylphenidate, dexamfetamine and atomoxetine for the treatment of attention deficit hyperactivity disorder in children and adolescents" — an ADHD medication review, **not** a peer tutoring study.
- **[2]**: PreScoredTiers [2] is "Authoring Tools for Designing Intelligent Tutoring Systems: a Systematic Review of the Literature" — about ITS authoring tools, **not** a peer tutoring study.

These represent **fabricated citation mappings** — the report cites [1] and [2] for peer tutoring claims that have no basis in the actual sources numbered [1] and [2].

---

## Check 2 — Statistic Provenance

| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| Effect sizes d=0.20 to 0.36 for tutoring on math achievement | [24][26][28][22] | PARTIALLY VERIFIED | d=0.36 verified from [26] findings; ~0.27 from [22] summary; 0.20 range mentioned in iteration history referencing Pellegrini et al. but attributed to [4] in iteration history, not [24]. The specific range "0.20 to 0.36" as a single bound is a synthesis, not a verbatim statistic from any one source. |
| 4 percentage point increase in mastery exit ticket passing rates (Tutor CoPilot) | [28] | VERIFIED | Found verbatim in [28] findings: "4 percentage points more likely to pass exit tickets" |
| Up to 9 percentage points for students with lower-performing tutors (Tutor CoPilot) | [28] | VERIFIED | Found verbatim in [28] findings: "up to 9 percentage points for students with lower-rated tutors" |
| 900 tutors and 1,800 K-8 students (Tutor CoPilot) | [28] | VERIFIED | Found in [28] findings: "900 tutors and 1,800 K-8 students" |
| d=0.36 for Rori AI tutor in Ghana | [26] | VERIFIED | Found verbatim in [26] findings: "effect=d=0.36" |
| 477 students in Rori RCT | [26] | VERIFIED | Found in [26] findings: "n=477" |
| 585 middle school students in hybrid human-AI tutoring QED | [27] | VERIFIED | Sum of site samples (125+385+75=585) matches [27] findings |
| Pooled effect size g=0.27 for ITS on math outcomes | [22] | UNVERIFIED | The [22] summary mentions "18 experimental studies" and the iteration history references "average effect sizes near 0.27," but the exact pooled g=0.27 is not found verbatim in the PreScoredTiers summary for [22]. Iteration history states it as approximately 0.27. |
| 18 experimental studies in ITS meta-analysis | [22] | UNVERIFIED | Not explicitly stated in [22] PreScoredTiers summary; mentioned in iteration history but not source entry. |
| "125 to 385 students per site" in hybrid tutoring QED | [27] | VERIFIED | Matches [27] findings: n=125, n=385, n=75 across three sites |
| Tutor CoPilot costs ~$20 per tutor annually | [28] | VERIFIED | Found in [28] findings: "Cost approximately $20 per tutor per year" |
| β=0.202 for time spent (Site 1, hybrid tutoring) | [27] | VERIFIED | Found in [27] findings |
| Medium to large effect sizes for peer tutoring (d=0.78) | [1][2] | FABRICATED | Sources [1] and [2] in PreScoredTiers are about ADHD drugs and ITS authoring tools respectively; the d=0.78 statistic appears only in iteration history attributed to "Alegre et al., 2020" which is not a numbered source. |
| Per-student costs below $750 for hybrid AI tutoring | [27] | UNVERIFIED | Mentioned in iteration 2 summary but not found in [27] PreScoredTiers findings or summary |

**Summary:** 8 VERIFIED, 3 UNVERIFIED, 1 FABRICATED (peer tutoring d=0.78 attributed to [1][2] which are wrong sources), 1 PARTIALLY VERIFIED.

---

## Check 3 — Study Design Accuracy

| Source | Report Label | PreScoredTiers Label | Status |
|--------|-------------|---------------------|--------|
| [26] | RCT | RCT | ✅ Correct |
| [28] | RCT | RCT | ✅ Correct |
| [27] | QED | QED | ✅ Correct |
| [22] | Meta-Analysis | Meta-Analysis / Systematic Review | ✅ Correct |
| [24] | Meta-Analysis / Systematic Review | Meta-Analysis / Systematic Review | ✅ Correct |
| [31] | Observational / Correlational | Observational / Correlational | ✅ Correct |
| [19] | Observational / Correlational | Observational / Correlational (but wrong source mapped — see Check 1) | ⚠️ Design label correct but source identity is wrong |
| [124] | Observational / Correlational | Observational / Correlational | ✅ Correct |

**Issues:**
- **[19]**: The Bibliography entry for [19] describes [57]'s paper. Source [57] in PreScoredTiers is indeed Observational/Correlational, so the design label happens to match — but the source identity is wrong.
- **[1] and [2]**: Cited for peer tutoring findings. PreScoredTiers [1] is a Meta-Analysis/Systematic Review (about ADHD drugs) and [2] is a Meta-Analysis/Systematic Review (about ITS authoring). The report does not explicitly label [1] or [2] as RCT or QED, but attributes peer tutoring evidence to them which is entirely mismatched content.

No study is mislabeled as an RCT or QED when it is not — the design labels used are consistent with the actual source designs where identifiable. The primary issue is source identity mismatch rather than design mislabeling.

---

## Check 4 — Sub-question Coverage

| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| 1 | Defining characteristics and models of tutoring for K-8 math | ✅ Fully covered | [24], [28], [26] |
| 1 | How math achievement is defined and measured in K-8 research | ✅ Fully covered | [24], [26], [22] |
| 1 | Typical demographics and educational contexts for K-8 tutoring | ✅ Fully covered | [24], [28], [26] |
| 2 | Approaches K-8 students typically experience without tutoring | ⚠️ Partially covered | [22], [18]*, [125]* — *[18] and [125] not in Bibliography |
| 2 | How standard classroom instruction addresses math skills development | ⚠️ Partially covered | [22], [18]* — [18] not in Bibliography |
| 2 | Alternative instructional interventions beyond tutoring | ⚠️ Partially covered | [22], [125]*, [18]* — [125] and [18] not in Bibliography |
| 3 | How tutoring programs are implemented (delivery models, dosage) | ✅ Covered with citations | [27], [24] |
| 3 | Instructional strategies targeting specific math skills in tutoring | ⚠️ Partially covered | [19] (wrong source mapping), [156]* — [156] not in Bibliography |
| 3 | Mechanisms explaining how tutoring improves math outcomes | ⚠️ Partially covered | [19], [31], [156]* — [156] not in Bibliography |
| 4 | Effectiveness of tutoring vs standard instruction for K-8 math | ✅ Fully covered | [24], [26], [28], [22] |
| 4 | Impact variation by student characteristics | ✅ Covered | [27], [28], [24] |
| 4 | Comparative advantages/trade-offs between tutoring and other interventions | ⚠️ Partially covered | [28], [27], [22] — limited direct comparison evidence acknowledged |
| 4 | Sustainability and scalability of effective tutoring interventions | ⚠️ Partially covered | [27], [28], [124] |

**Flagged Tiers:** Tier 2 sub-questions rely on citations [18] and [125] which are not in the Bibliography. Tier 3 sub-questions on instructional strategies and mechanisms rely on [156] (not in Bibliography) and [19] (wrong source mapping).

---

## Check 5 — URL Integrity

| # | Bibliography URL | PreScoredTiers URL | Status |
|---|------------------|--------------------|--------|
| 22 | `https://osf.io/link_to_data_and_code_placeholder` | `https://osf.io/link_to_data_and_code_placeholder` | OK |
| 24 | `https://arxiv.org/abs/2503.09748` | `https://arxiv.org/abs/2503.09748v1` | OK (minor version difference) |
| 26 | `https://arxiv.org/abs/2309.07044` | `https://arxiv.org/abs/2309.07044` | OK |
| 27 | `https://doi.org/10.1145/3636555.3636896` | `https://doi.org/10.1145/3636555.3636896` | OK |
| 28 | `https://arxiv.org/abs/2410.03017` | `https://arxiv.org/abs/2410.03017` | OK |
| 31 | `https://arxiv.org/abs/2602.19296` | `https://arxiv.org/abs/2602.19296` | OK |
| 19 | `https://arxiv.org/abs/2402.02660` | `https://arxiv.org/abs/2401.03238` | **MISMATCH** — Bibliography URL matches PreScoredTiers [57], not [19] |
| 124 | `https://doi.org/10.1787/edu_wkp-2024-23-en` | `https://doi.org/10.1787/edu_wkp-2024-23-en` | OK |

**Issues found:**
- **[19]**: MISMATCH — the URL in the Bibliography (`https://arxiv.org/abs/2402.02660`) corresponds to PreScoredTiers source [57], not source [19] (`https://arxiv.org/abs/2401.03238`).

---

## Recommended Fixes

1. **[CRITICAL] Remove or replace citations [1] and [2] for peer tutoring claims.** PreScoredTiers [1] is about ADHD medication and [2] is about ITS authoring tools. The peer tutoring evidence attributed to these sources (including d=0.78) appears to originate from an uncited source (Alegre et al., 2020). Either add the correct source to the Bibliography or remove these claims.

2. **[CRITICAL] Correct citation [19] mapping.** The Bibliography entry for [19] contains the title, URL, and content of PreScoredTiers source [57] ("Aligning Tutor Discourse..."). Either renumber the citation to [57] throughout the report or correct the Bibliography entry to match PreScoredTiers [19] ("Using Large Language Models to Assess Tutors' Performance...") and adjust claims accordingly.

3. **[HIGH] Add missing Bibliography entries for [18], [125], and [156].** These are cited inline but have no corresponding Bibliography entries. [18] is about ML-assisted RCT analysis (not directly about educational interventions), [125] is a systematic review of educational strategies to reduce achievement gaps, and [156] is a qualitative paper on tutor move taxonomy. Verify appropriateness and add entries, or remove inline citations.

4. **[HIGH] Verify and source the statistic "pooled effect size g=0.27" attributed to [22].** This number appears in iteration history but is not confirmed verbatim in the PreScoredTiers summary for [22]. If it comes from the full paper, provide verification; otherwise, qualify the claim.

5. **[MODERATE] Remove or qualify the claim of "per-student costs below $750" for hybrid AI tutoring.** This statistic is not found in the [27] source findings or summary.

6. **[MODERATE] Qualify the effect size range "d=0.20 to 0.36" in the Executive Summary.** The lower bound (0.20) originates from iteration history citing Pellegrini et al. and is attributed to source [4] in iteration history (which is actually about games/simulations in higher education per PreScoredTiers). The upper bound (0.36) is verified from [26]. The range should be more carefully sourced.

7. **[LOW] Add the peer tutoring source (Alegre et al., 2020 or equivalent) as a numbered reference if peer tutoring claims are retained.** Currently these claims have no valid source backing.

8. **[LOW] Note in limitations that source [22] uses a placeholder URL, limiting verifiability of the meta-analytic data.**

---

## Score Summary

| Dimension | Score |
|-----------|-------|
| Citation–bibliography linkage | 8/20 |
| Statistic provenance | 15/25 |
| Study design accuracy | 15/15 |
| Sub-question coverage | 8/20 |
| URL integrity | 16/20 |
| **Overall** | **62/100** |
