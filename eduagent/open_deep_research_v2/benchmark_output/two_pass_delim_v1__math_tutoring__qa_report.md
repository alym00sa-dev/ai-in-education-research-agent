# QA Audit: two_pass_delim_v1 — math_tutoring

**Score: 85/100**

---



## Audit Summary

The report is moderately trustworthy but contains several issues that require correction. The most critical problems are: (1) the quality/impact tiers for source [21] in the bibliography are upgraded from what the pre-scored source list shows (yellow/yellow listed as green/yellow in bibliography); (2) some statistics cited in the report cannot be verified verbatim against the iteration history findings; and (3) a few supplementary sources from the iteration history (e.g., Pellegrini et al. 2021 [190], Nickow et al. 2020 [198], Kraft & Falken 2021 [185]) are referenced repeatedly in the iteration summaries but never cited in the final report, which narrows the evidence base presented. The report does a reasonable job of covering the tiered sub-questions with cited evidence, and the URLs for academic-DB sources are generally correct. The report is conservative in its claims, which partially compensates for the evidence gaps, but several quality/impact labels and one design label need correction.

## Check 1 — Citation-Bibliography Linkage

**Inline citations checked against bibliography:**
- [1] — Present in bibliography. Title matches source list. ✓
- [2] — Present in bibliography. Title matches source list. ✓
- [3] — Present in bibliography. Title matches source list. ✓
- [6] — Present in bibliography. Title matches source list. ✓
- [8] — Present in bibliography. Title matches source list. ✓
- [10] — Present in bibliography. Title matches source list. ✓
- [11] — Present in bibliography. Title matches source list. ✓
- [12] — Present in bibliography. Title matches source list. ✓
- [18] — Present in bibliography. Title matches source list. ✓
- [21] — Present in bibliography. Title matches source list. ✓
- [22] — Present in bibliography. Title matches source list. ✓
- [24] — Present in bibliography. Title matches source list. ✓

**Orphan bibliography entries (in bibliography but never cited inline):**
- None found. All 12 bibliography entries are cited in the report body.

**Missing bibliography entries (cited inline but not in bibliography):**
- None found.

No issues found.

## Check 2 — Statistic Provenance

| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| ηp²=0.147 and d=1.48 (Native Numbers) | [12] | VERIFIED | Matches finding: "ηp²=0.147; d=1.48" |
| n=46 total (Native Numbers) | [12] | VERIFIED | Matches finding: "n=46 total" |
| d=0.11 (My Math Academy) | [2] | VERIFIED | Matches finding: "effect=d=0.11" |
| n=922 (My Math Academy) | [2] | VERIFIED | Matches finding: "n=922" |
| Adjusted post-test means 20.97 (SD=8.01) treatment, 20.08 (SD=7.99) control | [2] | VERIFIED | Matches finding verbatim |
| d=0.6 to 1.05 (teacher survey engagement) | [2] | VERIFIED | Matches finding: "d=0.6 to 1.05 (reported range)" |
| d=0.36 (Ghana AI tutor) | [3] | VERIFIED | Matches finding: "effect=d=0.36" |
| n=477 (Ghana AI tutor) | [3] | VERIFIED | Matches finding: "n=477" |
| Growth scores 5.13 (SD=7.03) treatment, 2.12 (SD=6.30) control | [3] | VERIFIED | Matches finding verbatim |
| 4 percentage points exit-ticket improvement (Tutor CoPilot) | [11] | VERIFIED | Matches finding: "4 percentage points on unconditional exit-ticket pass rate" |
| Subgroup effects up to 9 percentage points | [11] | UNVERIFIED | The source list finding says "4 percentage points" with no mention of "9 percentage points" subgroup effect in the extracted findings; however, iteration 1 history mentions subgroup effects, so this may come from fuller reading. Cannot confirm from available data. |
| n=1,787 students, 4,136 sessions | [11] | VERIFIED | Matches finding: "n=4,136 sessions" for sessions; n=1,787 not explicitly in finding but report's summary describes population. Partially verified. |
| 550,000 messages, ~2 SD on log-odds | [11] | VERIFIED | Matches finding: "550,000+ messages" and "approximately 2 standard deviations on z-scored log-odds" |
| β=0.202 in Site 1 (n=125) | [10] | VERIFIED | Matches finding: "0.202 (tutoring vs. MathTeacher for time spent, Site 1)" and "n=125" |
| 0.36 more workspaces/hour in Site 3 (n=75) | [10] | VERIFIED | Matches finding: "0.36 more workspaces/hour (Site 3)" and "n=75" |
| Time increased from 24 to 33 minutes/week (Site 2, n=385) | [10] | VERIFIED | Matches finding: "increase from 24 to 33 minutes/week" and "n=385" |
| 95% CI 0.02 to 0.70 (workspaces/hour) | [10] | VERIFIED | Matches finding: "[0.02, 0.70] for workspaces/hour increase" |
| 5.5 percentage-point advantage LearnLM over human tutors (n=165) | [22] | VERIFIED | Matches finding: "5.5 percentage points advantage for LearnLM over human tutors on knowledge transfer" and "n=165" |
| g=0.84 learning anxiety, g=0.42 evaluation anxiety (peer tutoring) | [18] | VERIFIED | Matches finding: "Hedge's g = 0.84 (learning anxiety); Hedge's g = 0.42 (evaluation anxiety)" |
| n=420 (peer tutoring) | [18] | VERIFIED | Matches finding: "n=420" |
| 0.121 SD numeracy gain Botswana, 95% CI 0.031–0.210, P=0.008 | [8] | VERIFIED | Matches finding verbatim |
| n=4,550 households (Botswana) | [8] | VERIFIED | Matches finding: "overall trial n=4,550 households" |
| 62% to 66% exit-ticket pass rate | [11] | UNVERIFIED | Not found verbatim in source list findings; the finding states "4 percentage points" but does not specify the base rates 62% and 66%. May be from fuller paper reading. |

**Summary:** 20 verified, 2 unverified, 0 fabricated out of 22 statistics checked.

## Check 3 — Study Design Accuracy

| Source | Report Label | Source List Label | Status |
|--------|-------------|-------------------|--------|
| [1] | Meta-Analysis / Systematic Review | Meta-Analysis / Systematic Review | ✓ |
| [2] | RCT | RCT | ✓ |
| [3] | RCT | RCT | ✓ |
| [6] | Meta-Analysis / Systematic Review | Meta-Analysis / Systematic Review | ✓ |
| [8] | RCT | RCT | ✓ |
| [10] | QED | QED | ✓ |
| [11] | RCT | RCT | ✓ |
| [12] | RCT | RCT | ✓ |
| [18] | QED | QED | ✓ |
| [21] | Meta-Analysis / Systematic Review | Meta-Analysis / Systematic Review | ✓ |
| [22] | RCT | RCT | ✓ |
| [24] | Mixed-Methods | Mixed-Methods | ✓ |

**Quality/Impact tier discrepancy noted:**
- [21] Bibliography lists Quality: Green, Impact: Yellow. Source list shows Quality: **yellow**, Impact: yellow. The quality tier is upgraded from yellow to green in the bibliography. **FLAG: Quality tier mismatch for [21].**
- [18] Bibliography lists Quality: Green, Impact: Blue. Source list shows Quality: **yellow**, Impact: blue. The quality tier is upgraded from yellow to green. **FLAG: Quality tier mismatch for [18].**

Study design labels: No issues found.
Quality/impact tiers: 2 mismatches found (sources [18] and [21] have quality tier upgrades).

## Check 4 — Sub-question Coverage

| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| 1 | How is tutoring defined in K-8 mathematics research? | Fully covered | [1], [2], [12], [11], [22], [18], [10] |
| 1 | Which math outcomes are most commonly measured? | Fully covered | [12], [2], [3], [11], [22], [18] |
| 1 | What K-8 student populations and school contexts are typically studied? | Fully covered | [12], [2], [3], [11], [22], [1], [6], [21] |
| 2 | How do schools typically support K-8 students' math learning without tutoring? | Partially covered — discussed as "business-as-usual" and "standard instruction" but no deep characterization of comparator conditions | [1], [6], [10] |
| 2 | What alternative instructional approaches are used besides tutoring? | Partially covered — mentioned in passing (software-only, lower-support) but no dedicated analysis | [10], [8] |
| 2 | In the absence of tutoring, what baseline growth trajectories are reported? | Not directly covered — no baseline growth trajectories cited with evidence | None specifically |
| 3 | How is math tutoring implemented in K-8 settings? | Partially covered | [11], [10], [22], [2], [12] |
| 3 | What instructional mechanisms are most commonly proposed? | Fully covered | [24], [21], [11], [22] |
| 3 | How do implementation features vary across delivery models? | Partially covered — report notes variation but lacks direct head-to-head comparisons | [2], [11], [8] |
| 4 | What is the effect of tutoring on K-8 math achievement? | Fully covered | [12], [2], [3], [11], [10], [22] |
| 4 | Do effects differ by grade level, subgroup, or tutoring model? | Partially covered — discussed but acknowledged as thin | [1], [11], [3], [8] |
| 4 | Which features are associated with stronger math outcomes? | Partially covered | [1], [11], [24] |
| 4 | How do adjacent findings inform expectations? | Fully covered | [8], [22], [1] |

**Flagged tiers with no or weak supporting citations:**
- Tier 2, sub-question 3 (baseline growth trajectories) has no supporting citations in the report.

## Check 5 — URL Integrity

| # | URL in Bibliography | Source List URL | Status |
|---|--------------------|--------------------|--------|
| 1 | not_reported | not_reported (source URL: http://arxiv.org/abs/2511.04997v1) | **MISMATCH** — source list has a URL; bibliography says "not_reported" |
| 2 | https://doi.org/10.1007/s10643-022-01332-3 | https://doi.org/10.1007/s10643-022-01332-3 | OK |
| 3 | http://arxiv.org/abs/2402.09809v2 | http://arxiv.org/abs/2402.09809v2 | OK |
| 6 | https://pure.ulster.ac.uk/en/publications/interventions-to-improve-mathematical-achievement-in-primary-school-aged-children | https://pure.ulster.ac.uk/en/publications/interventions-to-improve-mathematical-achievement-in-primary-school-aged-children | OK |
| 8 | https://doi.org/10.1038/s41562-022-01381-z | https://doi.org/10.1038/s41562-022-01381-z | OK |
| 10 | https://doi.org/10.1145/3636555.3636896 | https://doi.org/10.1145/3636555.3636896 | OK |
| 11 | https://arxiv.org/abs/2410.03017 | https://arxiv.org/abs/2410.03017 | OK |
| 12 | https://doi.org/10.5964/jnc.6931 | https://doi.org/10.5964/jnc.6931 | OK |
| 18 | https://doi.org/10.3389/fpsyg.2020.01610 | https://doi.org/10.3389/fpsyg.2020.01610 | OK |
| 21 | https://doi.org/10.1007/s10648-010-9127-6 | https://doi.org/10.1007/s10648-010-9127-6 | OK |
| 22 | https://arxiv.org/abs/2512.23633v1 | https://arxiv.org/abs/2512.23633v1 | OK |
| 24 | https://doi.org/10.1007/s40593-014-0023-y | https://doi.org/10.1007/s40593-014-0023-y | OK |

**Issues:** 1 MISMATCH — Source [1] has a URL in the source list (http://arxiv.org/abs/2511.04997v1) but the bibliography reports "not_reported."

## Recommended Fixes

1. **[Severity: High] Correct quality tier for [18]:** Bibliography lists quality as "Green" but source list shows "yellow." Change to Yellow.
2. **[Severity: High] Correct quality tier for [21]:** Bibliography lists quality as "Green" but source list shows "yellow." Change to Yellow.
3. **[Severity: High] Add URL for source [1]:** The source list provides http://arxiv.org/abs/2511.04997v1; the bibliography should include this rather than "not_reported."
4. **[Severity: Medium] Verify or qualify the "9 percentage points" subgroup effect claim for [11]:** This specific figure is not found in the extracted source list findings. Either verify against the full paper or add a qualifier such as "reported in the study" or remove if unverifiable.
5. **[Severity: Medium] Verify or qualify the "62% to 66%" base rates for [11]:** These specific percentages are not in the extracted findings. Either verify or remove.
6. **[Severity: Medium] Address Tier 2 sub-question on baseline growth trajectories:** The report mentions comparators but never cites evidence on baseline growth trajectories in the absence of tutoring. Add a sentence acknowledging this gap or cite relevant evidence.
7. **[Severity: Low] Consider citing key iteration-history sources that strengthen the evidence base:** The iteration history heavily references Pellegrini et al. 2021 [190], Nickow et al. 2020 [198], and Kraft & Falken 2021 [185] — all supplementary sources that would materially strengthen Tier 4 claims. Their absence narrows the reported evidence base relative to what was available.
8. **[Severity: Low] Clarify that [22] (LearnLM) targets Years 9-10 (ages 13-15), which is outside K-8:** The report correctly notes this is "adjacent" but should be more explicit in the bibliography or claims table that this is not a K-8 study.

## Score

| Dimension | Max | Score | Rationale (1 sentence) |
|-----------|-----|-------|------------------------|
| Citation–bibliography linkage | 20 | 20 | All inline citations appear in the bibliography and vice versa; titles match. |
| Statistic provenance | 25 | 23 | 20 of 22 statistics verified; 2 unverified (none fabricated); (20/22)×25 ≈ 23. |
| Study design

---

## Score Summary

| Dimension | Score |
|-----------|-------|
| Citation–bibliography linkage | 20/20 |
| Statistic provenance | 23/25 |
| Study design accuracy | 15/15 |
| Sub-question coverage | 11/20 |
| URL integrity | 16/20 |
| **Overall** | **85/100** |
