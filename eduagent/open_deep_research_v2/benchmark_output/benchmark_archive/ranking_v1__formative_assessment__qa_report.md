# QA Audit: ranking_v1 — formative_assessment

**Score: 71/100**

---



## Audit Summary

The report is moderately trustworthy but contains several issues that undermine confidence. The most critical problems are: (1) the report cites a source "[263]" as involving "140 schools and 604 students" but the iteration history describes the physics RCT as having "29 teachers and 604 students" — the 140 schools figure appears only in Iteration 3 and may conflate two different studies or represent updated information; (2) the bibliography is incomplete with missing design labels (all listed as "not_reported") despite the report assigning specific designs to these studies; (3) the reference style is inconsistent — some sources are cited by author name inline rather than by bracketed number, creating linkage ambiguity; (4) several bibliography entries have missing or truncated titles/URLs; and (5) the report uses a Monash University 2026 future-dated web source [205] in the iteration history that does not appear in the bibliography. Overall, the core claims are supported by the iteration history, but citation hygiene, design labeling transparency, and some specific statistics require correction.

## Check 1 — Citation-Bibliography Linkage

**Inline citations found in the report body (bracketed numbers):**
- [263] — Present in bibliography ✓
- [285] — Present in bibliography ✓
- [396] — Present in bibliography ✓
- [250] — Present in bibliography ✓
- [197] — Present in bibliography ✓
- [278] — Present in bibliography ✓
- [374] — Present in bibliography ✓
- [235] — Present in bibliography ✓

**Inline citations by author name (not bracketed):**
- "Xuan, Cheung, & Sun, 2022" — Corresponds to [197] in bibliography ✓
- "Beekman, Joosten-ten Brinke, & Boshuizen, 2021" — Corresponds to [396] in bibliography ✓
- "Double, McGrane, & Hopfenbeck, 2019" — Not in bibliography (corresponds to supplementary [260] or [271]) ✗ **MISSING FROM BIBLIOGRAPHY**
- "Yan, Li, & Panadero, 2021" — Corresponds to [235] in bibliography ✓
- "Hagos & Andargie, 2022" — Corresponds to [285] in bibliography ✓
- "Anders et al., 2022" — Corresponds to [263] in bibliography ✓

**Orphan bibliography entries (in bibliography but not cited inline):**
- None — all bibliography entries have at least one inline citation.

**Issues:**
1. "Double, McGrane, & Hopfenbeck, 2019" is cited by name in the report body but has no corresponding entry in the bibliography table.
2. The report inconsistently mixes bracketed number citations and author-name citations, making linkage verification difficult.

## Check 2 — Statistic Provenance

| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| Effect size d = 0.09 to 0.11 (cluster RCT, 140 schools) | [263] Anders et al., 2022 | PARTIALLY VERIFIED | Iteration 3 mentions "d = 0.09 to 0.11" and "140 English secondary schools." Iteration 1 and 2 describe "29 teachers and 604 students" for a physics RCT. The 140 schools figure appears only in Iteration 3 and may represent a different study or an updated finding. The effect size range is consistent across iterations. |
| 604 students | [263] | VERIFIED | Mentioned in Iterations 1, 2, and 3. |
| Meta-analysis: 48 studies, n=116,051, d=0.19 for reading | [197] Xuan et al., 2022 | VERIFIED | Iteration 1: "48 studies with over 116,000 students, reported a modest but positive average effect size of +0.19." Iteration 2: "48 studies with 116,051 K-12 students found a weighted effect size of 0.19." Iteration 3 confirms. |
| Stronger effects with differentiated instruction and collaborative teacher-student assessment | [197] | VERIFIED | Stated in Iterations 1, 2, and 3. |
| QED n=132, chemistry, technology-integrated FA improved retention | [285] Hagos & Andargie, 2022 | VERIFIED | Iteration 2: "quasi-experimental study with 132 chemistry students." Iteration 3 confirms. |
| Longitudinal QED n=695, Dutch primary students, self-regulation and motivation improvements | [396] Beekman et al., 2021 | VERIFIED | Iteration 3: "longitudinal study (n = 695) of Dutch primary students." |
| Digital FA did not significantly outperform traditional FA in reading | [197] | VERIFIED | Iteration 1: "Digital formative assessment tools show promise for supporting timely feedback but do not alone guarantee learning gains." Iteration 2 confirms. |
| No reported adverse effects (umbrella review of 13 meta-analyses) | Executive summary table | UNVERIFIED | The "umbrella review of 13 meta-analyses" is not explicitly mentioned in the iteration history. The supplementary source [224] (Sortwell et al., 2024) is referenced in Iteration 3 as "Sortwell et al., 2024" but the specific claim of "13 meta-analyses" and "no adverse effects" is not verbatim in the iteration history. |
| "140 schools" for the Anders et al. RCT | [263] | UNVERIFIED | Iterations 1 and 2 describe a physics RCT with "29 teachers and 604 students." Only Iteration 3 mentions "140 English secondary schools." This may reflect a different study or updated sourcing, but the discrepancy is notable. |

## Check 3 — Study Design Accuracy

All bibliography entries are from supplementary sources ([197], [235], [250], [263], [278], [285], [374], [396] — all ≥183). Per instructions, design labels should be verified against iteration history descriptions, not the bibliography's "not_reported" column.

| Source | Report Label | Iteration History Description | Status |
|--------|-------------|-------------------------------|--------|
| [263] Anders et al., 2022 | "cluster-randomized controlled trial" (RCT) | Iteration 3: "large cluster RCT involving 140 English secondary schools"; Iterations 1–2: described as RCT with 604 students | ✓ CONSISTENT |
| [197] Xuan et al., 2022 | "Meta-analysis" | Iteration 1: "large meta-analysis synthesizing 48 studies" | ✓ CONSISTENT |
| [285] Hagos & Andargie, 2022 | "quasi-experimental study" (QED) | Iteration 2: "quasi-experimental study with 132 chemistry students" | ✓ CONSISTENT |
| [396] Beekman et al., 2021 | "longitudinal QED" | Iteration 3: "longitudinal study (n = 695)" — described as observational/longitudinal but labeled QED in report | ⚠️ UNCERTAIN — Iteration history says "longitudinal study" without explicitly labeling it QED. The report's QED label is plausible but not confirmed by iteration history. |

**Issues:**
1. [396] is labeled "longitudinal QED" in the report, but the iteration history describes it as a "longitudinal study" without explicitly confirming quasi-experimental design. This is a minor concern — possible but not confirmed mislabeling.

## Check 4 — Sub-question Coverage

| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| 1 | Definitions and key components of formative assessment | ✅ Fully addressed | Xuan et al. (2022)/[197], [396] |
| 1 | Which student learning outcomes are targeted and measured | ✅ Fully addressed | [396], [263], [197] |
| 1 | Populations and settings | ✅ Fully addressed | [396], [250], [197] |
| 2 | Instructional practices without systematic formative assessment | ✅ Addressed | [263], [197], [285] |
| 2 | How outcomes develop under standard methods | ⚠️ Partially addressed — brief mention of conventional methods but no deep evidence with citations | [263], [197] |
| 2 | Alternative assessment strategies as comparators | ⚠️ Partially addressed — summative assessment mentioned, differentiated instruction briefly noted | [285] |
| 3 | How FA is implemented (delivery models, teacher practices) | ✅ Fully addressed | [278], [374], [285], [263], [235] |
| 3 | Mechanisms linking FA to improved outcomes | ✅ Addressed with theoretical grounding | [396], Beekman et al. |
| 3 | How teachers/students engage with feedback | ⚠️ Partially addressed — mentioned but limited specific cited evidence | [396], [263] |
| 4 | Comparative effectiveness of FA vs standard practices | ✅ Fully addressed | [263], [197], [285] |
| 4 | How effects vary across populations, grade levels, subjects | ⚠️ Partially addressed — noted as a limitation/gap, limited specific evidence cited | [197] |
| 4 | Limitations/tradeoffs of FA implementation | ✅ Fully addressed | Multiple sources |
| 4 | Evidence from analogous interventions (peer assessment, feedback) | ⚠️ Partially addressed — peer assessment discussed, Double et al. cited but not in bibliography | Double et al. (not in bibliography), [396] |

**Flags:**
- Tier 2 sub-questions on baseline development and alternative comparators are only lightly addressed.
- Tier 3 sub-question on teacher/student engagement with feedback lacks deep cited evidence.
- Tier 4 sub-question on variation across populations lacks specific cited evidence.
- Tier 4 sub-question on analogous interventions cites a source (Double et al.) not in the bibliography.

## Check 5 — URL Integrity

All bibliography entries are supplementary sources ([197]+). Verification against supplementary sources list:

| # | Bibliography URL | Supplementary URL | Status |
|---|-----------------|-------------------|--------|
| 197 | https://pmc.ncbi.nlm.nih.gov/articles/PMC9443994 | https://pmc.ncbi.nlm.nih.gov/articles/PMC9443994 | ✅ OK |
| 235 | not provided in bibliography | not available in supplementary | ✅ OK (no URL to check) |
| 250 | https://doi.org/10.3389/feduc.2023.1270700 | https://doi.org/10.3389/feduc.2023.1270700 | ✅ OK |
| 263 | https://www.semanticscholar.org/paper/4f754cb289831bf3d3eefd4b1b46fe96fd02d154 | https://www.semanticscholar.org/paper/4f754cb289831bf3d3eefd4b1b46fe96fd02d154 | ✅ OK |
| 278 | https://doi.org/10.23887/jet.v7i3.67770 | https://doi.org/10.23887/jet.v7i3.67770 | ✅ OK |
| 285 | No URL in bibliography | not available in supplementary | ✅ OK (no URL to check) |
| 374 | https://doi.org/10.9743/jeo.2019.16.2.11 | Not in supplementary list but present in pre-numbered list [374] — however [374] is NOT in the [1]-[182] range. Wait — [374] is beyond [182], so it should be in supplementary sources. It is NOT listed in supplementary sources. | ⚠️ UNCERTAIN — [374] is not in the supplementary sources list provided. The URL matches a plausible DOI domain. |
| 396 | No URL in bibliography | not available in supplementary | ✅ OK (no URL to check) |

**Note on [374]:** Source [374] (Robertson, Humphrey, Steele, 2019) is numbered above 182 but does not appear in the supplementary sources list. The URL (https://doi.org/10.9743/jeo.2019.16.2.11) is a plausible DOI. This is an anomaly — the source exists in neither the pre-numbered list nor the supplementary list, suggesting it may have been added without proper sourcing. However, the URL itself is plausible.

**Issues:**
1. Source [374] is not found in either the pre-numbered source list or the supplementary sources list — its provenance cannot be verified, though the URL appears plausible.

## Recommended Fixes

1. **[CRITICAL] Add Double, McGrane, & Hopfenbeck (2019) to the bibliography.** This peer assessment meta-analysis is cited by name in the report body but has no bibliography entry. Assign it a number (e.g., [260] or [271] from supplementary sources).

2. **[HIGH] Clarify the "140 schools" claim for [263].** Iterations 1 and 2 describe the formative assessment RCT as involving "29 teachers and 604 students" in physics. Iteration 3 introduces "140 English secondary schools." The report should verify whether these are the same or different studies and correct accordingly. The mention of "140 schools and 604 students" in the report body seems inconsistent — 140 schools would likely involve far more than 604 students.

3. **[HIGH] Verify and cite the "umbrella review of 13 meta-analyses" claim.** The executive summary table references this as supporting "no reported adverse effects," but the iteration history does not explicitly mention "13 meta-analyses" or this specific claim. Either cite [224] Sortwell et al. (2024) explicitly and verify the statistic, or remove the claim.

4. **[MODERATE] Verify source [374]'s provenance.** This source appears in neither the pre-numbered academic-DB list nor the supplementary sources. Add it to the appropriate source list or remove it.

5. **[MODERATE] Confirm QED label for [396] Beekman et al. (2021).** The iteration history describes this as a "longitudinal study" without explicitly confirming quasi-experimental design. Either verify the design through the original paper or soften the label to "longitudinal study."

6. **[MODERATE] Standardize citation format.** The report mixes bracketed number citations (e.g., [263]) with author-name citations (e.g., "Xuan, Cheung, & Sun, 2022"). Use a consistent format throughout.

7. **[LOW] Strengthen coverage of Tier 2 sub-questions.** Baseline and comparator conditions are only lightly addressed. Add more specific evidence about standard instructional practices and alternative assessment strategies.

8. **[LOW] Add design labels to bibliography.** All entries show "not_reported" for study design, yet the report text assigns specific designs. Populate the design column to match the report's stated labels.

## Score

| Dimension | Max | Score | Rationale |
|-----------|-----|-------|-----------|
| Citation–bibliography linkage | 20 | 14 | Double et al. missing from bibliography (−2), [374] provenance unverifiable (−2), inconsistent citation format causes ambiguity (−2) |
| Statistic provenance | 25 | 19 | 7 of 9 statistics verified; "umbrella review of 13 meta-analyses" unverified, "140 schools" partially verified with discrepancy; (7/9) × 25 ≈ 19 |
| Study design accuracy | 15 | 10 | [396] QED label uncertain (−5); all others consistent |
| Sub-question coverage | 20 | 14 | 8 of 13 sub-questions fully covered; 5 partially covered; approximately 10/13 effective coverage × 20 ≈ 14 |
| URL integrity | 20 | 16 | [374] not found in any source list (−4); all other URLs OK |
| **Overall** | **100** | **73** | |

---

## Score Summary

| Dimension | Score |
|-----------|-------|
| Citation–bibliography linkage | 14/20 |
| Statistic provenance | 19/25 |
| Study design accuracy | 10/15 |
| Sub-question coverage | 12/20 |
| URL integrity | 16/20 |
| **Overall** | **71/100** |
