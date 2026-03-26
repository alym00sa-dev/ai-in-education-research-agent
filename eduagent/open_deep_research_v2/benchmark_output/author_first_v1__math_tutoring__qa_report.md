# QA Audit: author_first_v1 — math_tutoring

**Score: 78/100**

---



## Audit Summary

The report is moderately trustworthy in its directional claims but has significant structural and provenance issues. The bibliography is severely incomplete — it lists only 5 of the ~12+ sources cited inline, creating widespread citation-bibliography linkage failures. Many inline citations use informal title-based references rather than numbered [N] brackets, making traceability difficult. Key statistics from the Rori RCT, Tutor CoPilot RCT, and hybrid human-AI QED are verifiable against the source list findings, but several statistics (e.g., the Botswana study's 0.121 SD, the SKOPE-IT d=0.2) are drawn from the pre-numbered source list without proper bibliography entries. The report also appears to have been written primarily from the iteration 3 / pre-numbered source data, largely ignoring the richer quantitative evidence from iterations 1-2 (Pellegrini et al., Nickow et al., Thurston et al.) — those studies are not in the bibliography and are barely cited in the body. Study design labels are mostly accurate. Sub-question coverage is partial across all tiers, with Tiers 2 and 3 receiving the weakest treatment.

## Check 1 — Citation-Bibliography Linkage

**Inline citations using [N] format:**
- [7] — appears in bibliography (Tutor CoPilot) ✓
- [8] — appears in bibliography (Improving Student Learning with Hybrid Human-AI Tutoring) ✓
- [20] — appears in bibliography (Effects of Online Parent Coaching) ✓
- [23] — appears in bibliography (An Examination of an Online Tutoring Program) ✓
- [24] — appears in bibliography (Cognitive tutoring induces widespread neuroplasticity) ✓

**Inline citations using title/author format that have NO bibliography entry:**
- "Bowman-Perrott et al., 2016" — corresponds to source #19 in the pre-numbered list. NOT in bibliography. Cited multiple times.
- "Effective and Scalable Math Support: Experimental Evidence on the Impact of an AI- Math Tutor in Ghana" — corresponds to source #41 in the pre-numbered list. NOT in bibliography. Cited multiple times.
- "Do intelligent tutoring systems benefit K-12 students?" — corresponds to supplementary source [230]. NOT in bibliography. Cited multiple times.
- "SKOPE-IT (Shareable Knowledge Objects as Portable Intelligent Tutors)" — corresponds to source #88 in the pre-numbered list. NOT in bibliography. Cited multiple times.
- "Experimental evidence on learning using low-tech when school is out" — corresponds to source #18 in the pre-numbered list. NOT in bibliography. Cited once.
- "Kraft & Falken, 2021" — referenced indirectly in iteration history but NOT in bibliography and not explicitly cited inline in the body (though "Kraft" appears in iteration summaries).

**Orphan bibliography entries:**
- All 5 bibliography entries ([7], [8], [20], [23], [24]) are cited inline. No orphans.

**Issues:**
- At least 5-6 sources are cited inline (by title or author) but missing from the bibliography table (sources #19, #41, #88, #18, and [230]).
- The report mixes [N] bracket citations with informal title-based citations inconsistently, making auditing difficult.

## Check 2 — Statistic Provenance

| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| Rori treatment mean growth 5.13 vs 2.12 for control, d=0.36, n=477 | Source #41 findings | VERIFIED | Matches finding: "mean growth score was 5.13 compared with 2.12 for control, effect=d=0.36, n=477" |
| Tutor CoPilot: +4 p.p. exit-ticket pass rate, n=4,136 sessions, 782 tutors, 1,787-1,800 students | Source #7 findings | VERIFIED | Matches finding: "4 percentage point increase in exit-ticket pass rate; n=4136 sessions; n=1787-1800 students; n=782 tutors at launch" |
| Tutor CoPilot subgroup effects +9 p.p. and +7 p.p. | Source #7 findings | VERIFIED | Matches finding: "subgroup effects +9 p.p. and +7 p.p." |
| Tutor CoPilot: no significant differences on student survey outcomes (motivation, perceived tutor care, confidence) | Source #7 findings | VERIFIED | Matches finding about student survey outcomes |
| Tutor CoPilot: ~2 SD on log-odds scale for selected tutor strategies | Source #7 findings | VERIFIED | Matches finding: "approximately 2 standard deviations on log-odds scale for selected strategies" |
| Hybrid human-AI tutoring: β=0.202, 95% CI [0.057, 0.347] for time spent in Site 1 | Source #8 findings | VERIFIED | Matches finding: "β=0.202; CI=[0.057, 0.347]" |
| Hybrid human-AI tutoring: weekly usage rise from 24 to 33 minutes in Site 2 | Source #8 findings | VERIFIED | Matches finding: "24 to 33 minutes/week increase" |
| Hybrid human-AI tutoring: Site 3 progress estimate CI [0.02, 0.70] | Source #8 findings | VERIFIED | Matches finding: "CI=[0.02, 0.70]" |
| Hybrid human-AI tutoring: n=125; n=385; n=75 | Source #8 findings | VERIFIED | Matches finding: "n=125; n=385; n=74 analyzed" (report says 75 vs 74 in one instance but source summary also says n=75 in social-emotional finding) |
| Cognitive tutoring: d=0.86 on in-scanner arithmetic verification, n=15 MLD, n=15 TD | Source #24 findings | VERIFIED | Matches finding: "effect=d=0.86, n=15 MLD; n=15 TD" |
| Parent coaching: n=94, improved all numeracy outcomes | Source #20 findings | VERIFIED | Matches finding: "n=94" and "significantly improved all measured numeracy outcomes" |
| SKOPE-IT: d=0.2, regression coefficient=8.0, n=76 | Source #88 findings | VERIFIED | Matches finding: "effect=d=0.2; regression coefficient=8.0, n=76" |
| Botswana phone+SMS: 0.121 SD, n=4,550 households | Source #18 findings | VERIFIED | Matches finding: "effect=0.121, n=2815 to n=2751 depending on outcome" (household n=4,550 matches) |
| SKOPE-IT: no statistically significant difference in ALEKS learning gains | Source #88 findings | VERIFIED | Matches finding: "no statistically significant difference in ALEKS learning gains" |

All checked statistics: **14 VERIFIED, 0 UNVERIFIED, 0 FABRICATED**

## Check 3 — Study Design Accuracy

| Source | Report Label | Source List Label | Status |
|--------|-------------|-------------------|--------|
| [7] Tutor CoPilot | RCT | RCT | ✓ OK |
| [8] Hybrid Human-AI Tutoring | QED | QED | ✓ OK |
| [20] Parent Coaching Filipino Children | RCT | RCT | ✓ OK |
| [23] Online Tutoring Middle School | Mixed-Methods | Mixed-Methods | ✓ OK |
| [24] Cognitive tutoring neuroplasticity | QED | QED | ✓ OK |
| #41 Rori AI Math Tutor Ghana | RCT | RCT | ✓ OK |
| #88 SKOPE-IT | RCT | RCT | ✓ OK |
| #18 Botswana phone+SMS | RCT | RCT | ✓ OK |
| #19 Bowman-Perrott peer tutoring | Meta-analysis | Meta-Analysis / Systematic Review | ✓ OK |
| [230] ITS meta-analysis | Meta-analysis | Not in pre-numbered list; supplementary source — iteration history describes it as "meta-analysis" | ✓ OK |

No issues found.

## Check 4 — Sub-question Coverage

| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| Tier 1 | What is meant by tutoring in K-8 math research? | COVERED | Bowman-Perrott 2016, ITS meta-analysis [230], [8], [7], [23], [24] — report has dedicated section "What counts as tutoring" |
| Tier 1 | Which math outcomes are most commonly measured? | PARTIALLY COVERED | Report has "Outcomes Measured" section with [41], [7], [8], [24] but coverage is thin on operationalization of fluency, conceptual understanding, problem solving |
| Tier 1 | What student populations are typically included? | PARTIALLY COVERED | "Populations and grade bands" section addresses grade bands but is thin on disability/multilingual learner subgroups; [24] addresses MLD |
| Tier 2 | How is K-8 math proficiency developed without tutoring? | PARTIALLY COVERED | "Standard Comparators" section discusses BAU and software-only but lacks depth on standard instructional supports |
| Tier 2 | What alternative approaches to tutoring are used? | WEAKLY COVERED | Brief mentions MTSS, computer-assisted practice in passing but no dedicated evidence; SKOPE-IT (#88) is undergraduate |
| Tier 2 | What baseline levels and instructional conditions do researchers use? | WEAKLY COVERED | Mentioned in comparator section but no systematic treatment |
| Tier 3 | How is tutoring delivered (tutor type, frequency, duration, etc.)? | PARTIALLY COVERED | "Tutor Type, Dosage, and Delivery Conditions" section present with [7], [41], [24], [8] but lacks systematic evidence on frequency/duration thresholds |
| Tier 3 | What instructional mechanisms explain tutoring effects? | PARTIALLY COVERED | "Mechanisms" subsection with [7], [8], [24] |
| Tier 3 | How do implementation features influence delivery? | WEAKLY COVERED | Mentioned in limitations but not systematically addressed with cited evidence |
| Tier 4 | What is the overall effect of tutoring on K-8 math? | COVERED | Multiple sources cited; meta-analytic and RCT evidence discussed |
| Tier 4 | Do effects vary by grade, prior achievement, disability, etc.? | PARTIALLY COVERED | [24] for MLD, [23] for low achievers, but thin on EL, race, SES |
| Tier 4 | Which tutoring models show strongest evidence? | PARTIALLY COVERED | Discussed but report explicitly notes insufficient evidence for ranking |
| Tier 4 | What tradeoffs, limitations, or constraints are reported? | COVERED | Limitations section addresses scalability, dosage, design quality |

**Summary:** No tier is fully covered with comprehensive cited evidence. Tier 1 and Tier 4 are the best covered. Tier 2 and Tier 3 are the weakest. I count approximately 5 sub-questions as adequately covered, 6 as partially covered, and 2 as weakly covered.

## Check 5 — URL Integrity

| # | URL in Bibliography | Source List URL | Status |
|---|--------------------|--------------------|--------|
| 7 | https://arxiv.org/abs/2410.03017 | https://arxiv.org/abs/2410.03017 | OK |
| 8 | https://doi.org/10.1145/3636555.3636896 | https://doi.org/10.1145/3636555.3636896 | OK |
| 20 | https://doi.org/10.1016/j.ecresq.2024.05.006 | https://doi.org/10.1016/j.ecresq.2024.05.006 | OK |
| 23 | https://doi.org/10.24059/olj.v19i5.694 | https://doi.org/10.24059/olj.v19i5.694 | OK |
| 24 | https://www.nature.com/articles/ncomms9453 | https://www.nature.com/articles/ncomms9453 | OK |

**Sources cited inline but missing from bibliography (URLs cannot be checked against bibliography but are verifiable against source list):**
- #19 (Bowman-Perrott): source list URL is https://doi.org/10.1016/j.ijer.2015.11.010 — not in bibliography, so N/A
- #41 (Rori): source list URL is http://arxiv.org/abs/2402.09809v2 — not in bibliography, so N/A
- #88 (SKOPE-IT): source list URL is https://doi.org/10.1186/s40594-018-0109-4 — not in bibliography, so N/A
- #18 (Botswana): source list URL is https://doi.org/10.1038/s41562-022-01381-z — not in bibliography, so N/A
- [230] (ITS meta-analysis): supplementary source URL is https://www.semanticscholar.org/paper/64480a19e02c75125fa86442171f5cd424e1a8b7 — not in bibliography, so N/A

No issues found with the 5 URLs that are in the bibliography.

## Recommended Fixes

1. **CRITICAL — Add missing bibliography entries.** Sources #19 (Bowman-Perrott et al., 2016), #41 (Rori AI Math Tutor Ghana), #88 (SKOPE-IT), #18 (Botswana phone+SMS), and [230] (ITS meta-analysis) are cited multiple times in the body but are entirely absent from the bibliography table. Add full entries with correct URLs, designs, and quality/impact tiers.

2. **CRITICAL — Standardize citation format.** The report inconsistently mixes [N] bracket citations with inline title-based citations (e.g., "Bowman-Perrott et al., 2016" vs "[7]"). All citations should use consistent [N] bracket notation matching the bibliography.

3. **HIGH — Add quality and impact tiers for all bibliography entries.** Source #41 (Rori) is listed as green/blue in the source list but is missing from the bibliography entirely. Source [230] is a supplementary source. All should be included with appropriate tier labels.

4. **HIGH — Strengthen Tier 2 and Tier 3 coverage.** The report's treatment of baseline/comparator conditions (Tier 2) and implementation features (Tier 3) is thin and often lacks direct cited evidence. Either add evidence from the iteration history (e.g., Kraft & Falken 2021 on high-dosage implementation features, Carbonari et al. 2024 on dosage shortfalls) or explicitly acknowledge these as evidence gaps.

5. **MODERATE — Acknowledge dropped iteration 1-2 evidence.** The report largely ignores the quantitative estimates from Pellegrini et al. (2021), Nickow et al. (2020), Thurston et al. (2020), and Alegre et al. (2020) that were central to iterations 1-2. These were either dropped without explanation or the report shifted focus. If they were excluded for quality reasons, state so; otherwise, incorporate them.

6. **MODERATE — Correct the bibliography quality tier for source #8.** The source list rates #8 (Hybrid Human-AI Tutoring) as quality=yellow, but the bibliography lists it as quality=Green. Verify and correct.

7. **LOW — Clarify the n=75 vs n=74 discrepancy for Site 3 of source #8.** The report says n=75 but the source findings report n=74 analyzed. Use the analyzed sample size.

8. **LOW — Note that the "Body of Evidence Maturity: LIMITED" rating is appropriate** but the justification should explicitly mention that 5+ cited sources are missing from the bibliography, which understates the actual evidence base used.

## Score

| Dimension | Max | Score | Rationale |
|-----------|-----|-------|-----------|
| Citation–bibliography linkage | 20 | 10 | Five sources cited inline are missing from the bibliography table (−2 each

---

## Score Summary

| Dimension | Score |
|-----------|-------|
| Citation–bibliography linkage | 10/20 |
| Statistic provenance | 25/25 |
| Study design accuracy | 15/15 |
| Sub-question coverage | 8/20 |
| URL integrity | 20/20 |
| **Overall** | **78/100** |
