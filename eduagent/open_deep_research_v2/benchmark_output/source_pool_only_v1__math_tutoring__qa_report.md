# QA Audit: source_pool_only_v1 — math_tutoring

**Score: 88/100**

---



## Audit Summary

The report is moderately trustworthy but contains several notable issues. The bibliography is sparse (only 9 entries) yet most inline citations match. The most critical issues are: (1) a mislabelled URL for source [1] — the bibliography lists a DOI link that doesn't match the pre-numbered source list URL; (2) the bibliography entry for source [20] is labeled as QED but the pre-numbered source list indicates the population is "High School," not K-8, and the report uses it as if it were K-8 evidence; (3) several statistics cited in the report are either UNVERIFIED or only partially verifiable against the iteration history; (4) the impact tier for source [8] is listed as "Green" in the bibliography but the pre-numbered source list says "yellow"; and (5) the report cites source [20] (blended learning, secondary school) as a bibliography entry but its title does not appear with a bracketed citation [20] in the body — it is instead referenced by full title inline, creating an inconsistency. Additionally, several supplementary sources and iteration history findings (e.g., Pellegrini et al., Hodgen et al., Chappell et al., Alegre et al.) are discussed in the iteration history but are not cited or included in the final bibliography, which narrows the evidence base presented.

## Check 1 — Citation-Bibliography Linkage

| Issue | Detail |
|-------|--------|
| [1] inline citation | [1] appears inline in the report body ("Alternative supplemental instruction methods in K-8 include after-school enrichment programs... [1][20]"). Bibliography entry [1] exists. Title "Differentiated Instruction in Secondary Education: A Systematic Review of Research Evidence (2019)" matches the pre-numbered source list. **OK** |
| [2] inline citation | [2] appears inline in the claims table and body. Bibliography entry [2] exists. Title matches. **OK** |
| [3] inline citation | [3] appears inline multiple times. Bibliography entry [3] exists. Title matches. **OK** |
| [5] inline citation | [5] appears inline multiple times. Bibliography entry [5] exists. Title matches. **OK** |
| [8] inline citation | [8] appears inline in comparative effectiveness section. Bibliography entry [8] exists. Title matches. **OK** |
| [20] inline citation | [20] appears inline ("Alternative supplemental instruction methods... [1][20]"). Bibliography entry [20] exists. However, the report body refers to "Effect of blended learning approach on secondary school learners' mathematics achievement and retention (2024)" by full title elsewhere but not with [20] bracket consistently. **Minor inconsistency.** |
| [22] inline citation | [22] appears in the claims table. Bibliography entry [22] exists. Title matches. **OK** |
| [31] inline citation | [31] appears in the claims table. Bibliography entry [31] exists. Title matches. **OK** |
| [40] inline citation | [40] appears in the claims table. Bibliography entry [40] exists. Title matches. **OK** |
| Orphan check | No bibliography entries lack any inline reference — all 9 bibliography entries are referenced. **OK** |
| Missing inline citations | The report body text sometimes references studies by full title (e.g., "Effective and Scalable Math Support, 2023", "Tutor CoPilot, 2025", "Advancing Education through Tutoring Systems, 2025", "Teaching According to Students' Aptitude, 2026", "Improving Student Learning with Hybrid Human-AI Tutoring, 2024", "Aligning Tutor Discourse Supporting Rigorous Thinking..., 2024", "Continued Progress..., 2015", "Effect of blended learning approach..., 2024") without using bracketed citation numbers. While these correspond to bibliography entries, the inconsistent use of inline bracketed numbers vs. full-title references is a formatting issue. |

**Summary:** No missing bibliography entries for inline [N] citations. No orphan entries. Minor inconsistency in that many references are made by full title rather than by [N] number, creating a mixed citation style.

## Check 2 — Statistic Provenance

| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| Mean growth difference of 3.01 points on a 35-point math assessment, d=0.36 (n=477) | [2] Effective and Scalable Math Support | VERIFIED | Pre-numbered source list finding states: "mean growth difference of 3.01 points on a 35-poin[t]...d=0.36, n=477" |
| 4 percentage point increase in topic mastery; up to 9 percentage points for lower-strength tutors (n=1,800 students, n=900 tutors) | [3] Tutor CoPilot | VERIFIED | Pre-numbered source list finding states: "4 percentage points improvement overall; up to 9 percentage points for lower-strength tutors, n=1800 students, n=900 tutors" |
| Over 500 urban, low-income middle school students (hybrid human-AI tutoring) | [5] Improving Student Learning | VERIFIED | Source list says n=585 combined across three sites; "over 500" is a reasonable characterization |
| Partial eta squared = 0.548 (achievement) and 0.365 (retention), n=94 | [20] Effect of blended learning | VERIFIED | Source list finding states: "partial eta squared=0.548 (achievement); partial eta squared=0.365 (retention), n=94" |
| d=0.27 over two years, n=11,217 | [22] Continued Progress | VERIFIED | Source list finding states: "d=0.27, n=11,217 students" |
| ~11.4% normalized learning gain improvement over baselines | [31] Teaching According to Students' Aptitude | VERIFIED | Source list finding states: "~11.4% average normalized learning gain improvement over baseline" |
| Up to 92.1% personalization win rate | [31] Teaching According to Students' Aptitude | VERIFIED | Source list finding states: "up to 92.1% response personalization win rate versus baseline" |
| No significant differences in motivation or social-emotional skills (n~1900) | [3] Tutor CoPilot | VERIFIED | Source list findings state: "not significant, n=~1900 students" for social-emotional and survey outcomes |
| n=585 (hybrid human-AI tutoring, combined three sites) | [5] Improving Student Learning | VERIFIED | Source list states n=585 combined across three sites |
| Blended learning group n=48, posttest mean=84.58 | [20] | VERIFIED | Source list finding includes these details |

**All statistics checked are VERIFIED against the pre-numbered source list or iteration history.**

## Check 3 — Study Design Accuracy

| Source | Report Label | Source List Label | Status |
|--------|-------------|-------------------|--------|
| [1] Differentiated Instruction | Meta-Analysis / Systematic Review (implied by bibliography) | Meta-Analysis / Systematic Review | **OK** |
| [2] Effective and Scalable Math Support | RCT | RCT | **OK** |
| [3] Tutor CoPilot | RCT | RCT | **OK** |
| [5] Improving Student Learning | QED | QED | **OK** |
| [8] Advancing Education through Tutoring Systems | Meta-Analysis / Systematic Review | Meta-Analysis / Systematic Review | **OK** |
| [20] Effect of blended learning | QED | QED | **OK** |
| [22] Continued Progress | QED | QED | **OK** |
| [31] Teaching According to Students' Aptitude | QED | QED | **OK** |
| [40] Aligning Tutor Discourse | Observational / Correlational | Observational / Correlational | **OK** |

**Impact tier discrepancy for [8]:** The bibliography lists Impact as "Green" but the pre-numbered source list says Impact is "yellow." This is a minor metadata error in the bibliography, not a study design mislabelling.

**No study design mislabelling found.**

## Check 4 — Sub-question Coverage

| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| 1 | How is 'tutoring' defined in the context of K-8 mathematics education, including modalities and providers? | **Covered** — Dedicated section "Defining Tutoring in K-8 Mathematics Education" addresses this with cited evidence | [3], [8], [31] |
| 1 | What specific math skills and outcome measures assess improvement in K-8 students receiving tutoring? | **Covered** — Discussed in the defining section mentioning standardized tests, topic mastery, retention | [2], [3] |
| 1 | What are the characteristics of the K-8 student populations relevant to tutoring? | **Partially covered** — Low-income, Title I, LMIC contexts discussed; ELLs and students with disabilities noted as gaps | [2], [3], [5] |
| 2 | What instructional approaches and baseline comparisons are typical in studies of math tutoring? | **Covered** — Dedicated section "Baseline Instruction and Alternative Supports" | [2], [22] |
| 2 | What alternative supplemental instruction methods are employed alongside or instead of tutoring? | **Partially covered** — Mentioned (after-school, blended learning, technology) but not deeply analyzed with evidence | [1], [20] |
| 2 | What is the baseline math achievement level among students receiving standard classroom instruction? | **Partially covered** — Described qualitatively (proficiency below mastery in low-income contexts) but no specific baseline data cited | [2] |
| 3 | How is tutoring delivered regarding frequency, duration, and content? | **Partially covered** — General description of frequency/duration variation; no specific figures from RCTs | [8] |
| 3 | What tutoring instructional strategies support math learning? | **Covered** — Scaffolding, questioning, formative feedback discussed | [8], [40], [5] |
| 3 | What mechanisms explain how tutoring influences K-8 math outcomes? | **Covered** — Individualized support, engagement, corrective feedback discussed | [5], [3] |
| 4 | What evidence shows tutoring effectiveness compared to standard instruction? | **Well covered** — Multiple RCTs and QEDs cited with effect sizes | [2], [3], [22], [20] |
| 4 | How does tutoring compare with alternative supplemental supports in outcomes and cost-effectiveness? | **Weakly covered** — Acknowledged as limited; no specific comparative evidence cited | [8], [3] |
| 4 | How do population and contextual factors moderate tutoring effectiveness? | **Partially covered** — Tutor expertise noted; ELL and disability gaps acknowledged | [3] |
| 4 | What are limitations and potential unintended effects of tutoring? | **Covered** — Dedicated limitations section discusses gaps, equity risks | General discussion |

**Tier coverage summary:**
- Tier 1: 2 of 3 fully covered; 1 partially (ELL/disability populations)
- Tier 2: 1 of 3 fully covered; 2 partially
- Tier 3: 2 of 3 covered; 1 partially (frequency/duration lacks specifics)
- Tier 4: 2 of 4 well/fully covered; 2 partially/weakly covered

## Check 5 — URL Integrity

| # | Bibliography URL | Source List URL | Status |
|---|-----------------|-----------------|--------|
| 1 | `https://doi.org/10.3389/fpsyg.2019.02366` | `https://www.frontiersin.org/articles/10.3389/fpsyg.2019.02366/full` | **MISMATCH** — The DOI resolves to the same article but the URLs differ in form. The bibliography uses the DOI shortlink while the source list uses the full Frontiers URL. This is a minor format mismatch; both point to the same paper. |
| 2 | `https://arxiv.org/pdf/2309.08785.pdf` | `https://arxiv.org/pdf/2309.08785.pdf` | **OK** |
| 3 | `https://arxiv.org/abs/2410.03017v2` | `https://arxiv.org/abs/2410.03017v2` | **OK** |
| 5 | `https://doi.org/10.1145/3636555.3636896` | `https://doi.org/10.1145/3636555.3636896` | **OK** |
| 8 | `https://arxiv.org/abs/2503.09748v1` | `https://arxiv.org/abs/2503.09748v1` | **OK** |
| 20 | `https://doi.org/10.1007/s10639-024-12651-w` | `https://doi.org/10.1007/s10639-024-12651-w` | **OK** |
| 22 | `https://www.rand.org/pubs/research_reports/RR1365.html` | `https://www.rand.org/pubs/research_reports/RR1365.html` | **OK** |
| 31 | `https://arxiv.org/abs/2511.15163` | `https://arxiv.org/abs/2511.15163` | **OK** |
| 40 | `not_reported` | `not_reported` | **OK** — both match |

**Summary:** One minor URL format mismatch for [1] (DOI shortlink vs. full Frontiers URL — both resolve to the same paper). This is arguably acceptable but technically a mismatch.

## Recommended Fixes

1. **[High] Standardize citation style:** The report inconsistently uses bracketed [N] citations and full-title inline references. All references should use [N] format consistently throughout the body text to ensure traceability.

2. **[High] Correct impact tier for [8]:** The bibliography lists Impact as "Green" but the pre-numbered source list shows "yellow." Update the bibliography to reflect the correct impact tier.

3. **[Medium] Clarify population applicability of [20]:** Source [20] (blended learning) is a secondary/high school study (population: "High School" per source list). The report acknowledges this partially ("generalizability to K-8 requires caution") but the claims table lists it without this caveat. Add a qualifier in the claims table.

4. **[Medium] Harmonize URL for [1]:** Update the bibliography URL for [1] to match the source list (`https://www.frontiersin.org/articles/10.3389/fpsyg.2019.02366/full`) or note that both URLs resolve to the same article.

5. **[Medium] Expand sub-question coverage for Tier 2 and Tier 4:** The report weakly addresses alternative supplemental instruction comparisons and cost-effectiveness. Either cite additional evidence from the iteration history (e.g., Pellegrini et al., Chappell et al.) or explicitly state the evidence gap.

6. **[Medium] Include key iteration history sources in bibliography:** The iteration history cites several important studies (Pellegrini et al., 2021 [164]; Hodgen et al., 2022 [157]; Chappell et al., 2015 [160/193]; Alegre et al., 2020 [165]; Demszky et al., 2024 [196]) that inform the evidence synthesis but are absent from the final bibliography. Consider including the most relevant as supplementary citations.

7. **[Low] Clarify the year for [31]:** The source is dated 2026, which may raise questions about its availability. Confirm this is an accepted/preprint publication and note this in the bibliography.

8. **[Low] Address the "n=not_specified" for [40]:** The claims table lists sample size as "not_specified" for the Aligning Tutor Discourse study. If the source truly does not report sample size, note this limitation explicitly.

## Score

| Dimension | Max | Score | Rationale (1 sentence) |
|-----------|-----|-------|------------------------|
| Citation–bibliography linkage | 20 | 18 | Minor inconsistency in mixed citation style (full titles vs. [N]), but no missing or orphan entries. |
| Statistic provenance | 25 | 25 | All 10 statistics checked were verified against the pre-numbered source list findings. |
| Study design accuracy | 15 | 15 | All study design labels match the pre-numbered source list; impact tier error for [8] is metadata, not design. |
| Sub-question coverage | 20 | 14 | Approximately 7 of 13 sub-questions fully covered; several partially addressed, and comparative cost-

---

## Score Summary

| Dimension | Score |
|-----------|-------|
| Citation–bibliography linkage | 18/20 |
| Statistic provenance | 25/25 |
| Study design accuracy | 15/15 |
| Sub-question coverage | 14/20 |
| URL integrity | 16/20 |
| **Overall** | **88/100** |
