

## Audit Summary

The report is **not fully trustworthy** and contains several critical issues. The most severe problems are: (1) **multiple source numbers in the report do not correspond to the papers described** — the report attributes findings from specific generative-AI-in-education studies to source numbers [5], [9], [25], [27], and [29], but in the PreScoredTiers list those numbers refer to entirely different papers (e.g., [5] is a flipped classroom meta-analysis, [9] is about educational escape rooms, [25] is about AI roles in mathematical modelling with high schoolers, [27] is about student-ChatGPT conversations, [29] is about ChatGPT's mathematical capabilities); (2) **most key statistics cannot be verified** from the iteration history because the iteration history does not contain the specific source numbers used in the report — the iteration history references studies by author name but the numbered mapping is wrong; (3) **study design labels are misattributed** because the underlying papers at those source numbers have different designs than claimed; and (4) **bibliography URLs are largely invented or mismatched** relative to the PreScoredTiers entries. The report appears to have been written using the iteration history's narrative content but assigned source numbers incorrectly from the PreScoredTiers list.

---

## Check 1 — Citation-Bibliography Linkage

### Inline citations used in report body: [5], [9], [25], [27], [29], [85], [173]

All seven inline citations appear in the Bibliography table. No orphan bibliography entries exist (all 7 bibliography entries are cited inline). **However, the content attributed to each number does not match the PreScoredTiers entry for that number:**

| Citation | Bibliography Title | PreScoredTiers Actual Title | Match? |
|----------|-------------------|----------------------------|--------|
| [5] | Strohmaier et al. (2026) LLAMA LIMA living meta-analysis | Flipped classroom improves student learning in health professions education (2018) | **MISMATCH** |
| [9] | Bastani et al. (2025) Generative AI without guardrails | Are Educational Escape Rooms More Effective Than Traditional Lectures? (2024) | **MISMATCH** |
| [25] | Liu et al. (2025) How K-12 Educators Use AI | Investigating Students' Preferences for AI Roles in Mathematical Modelling (2025) | **MISMATCH** |
| [27] | Thomas et al. (2023) Hybrid Human-AI Tutoring | Do Students Rely on AI? Analysis of Student-ChatGPT Conversations (2025) | **MISMATCH** |
| [29] | Rizos et al. (2024) Enhancing mathematics for SEN students | Mathematical Capabilities of ChatGPT (2023) | **MISMATCH** |
| [85] | Cross-sectional teacher reactions to generative AI (2025) | Matches PreScoredTiers [85] | **MATCH** |
| [173] | Advancing Transformative Education: Generative AI (2024) | Matches PreScoredTiers [173] | **MATCH** |

**Issues found:**
- **[5]**: Bibliography entry describes a completely different paper than PreScoredTiers #5.
- **[9]**: Bibliography entry describes a completely different paper than PreScoredTiers #9.
- **[25]**: Bibliography entry describes a completely different paper than PreScoredTiers #25.
- **[27]**: Bibliography entry describes a completely different paper than PreScoredTiers #27.
- **[29]**: Bibliography entry describes a completely different paper than PreScoredTiers #29.
- [85] and [173]: Match correctly.

---

## Check 2 — Statistic Provenance

| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| g = 0.42 average effect size for generative AI on math outcomes, 21 studies, 38 effect sizes | [5] | **UNVERIFIED** | The iteration history mentions "g = 0.42" and "21 studies with 38 effect sizes" attributed to Strohmaier et al. (2026), but [5] in PreScoredTiers is a different paper entirely. The statistic exists in the iteration narrative but not linked to the correct source number. |
| "50% reported generative AI use" among ~1,000 educators | [25] | **UNVERIFIED** | Iteration history mentions Liu et al. (2025) finding 50% usage among ~1,000 educators, but [25] in PreScoredTiers is a different paper (n=26 high school students). The statistic appears in iteration text but is misattributed by number. |
| g ≈ 0.31 (earlier reports) rising to 0.42 | [5] | **UNVERIFIED** | Mentioned in Iteration 2 narrative for Strohmaier et al., but [5] is not that paper per PreScoredTiers. |
| Average cognitive level rising from 3.35 to 4.85 (Shanto et al., n=20) | Not cited in final report | **N/A** | Mentioned in Iteration 2 but not carried into final report. |
| "Students who became reliant on generative AI showed diminished skill acquisition once AI withdrawn" | [9] | **UNVERIFIED** | Iteration history describes this finding for Bastani et al. (2025), but [9] in PreScoredTiers is an escape room RCT paper. |
| ChatGPT-generated worksheets supported engagement for 8th-grade SEN students | [29] | **UNVERIFIED** | Described in iteration history for Rizos et al. (2024), but [29] in PreScoredTiers is "Mathematical Capabilities of ChatGPT" — a different paper. |

**Summary:** 0 of 6 key statistics verified against correct source numbers. All are present in iteration narrative text but misattributed to wrong numbered sources.

---

## Check 3 — Study Design Accuracy

| Report Claim | Source # | Claimed Design | PreScoredTiers Actual Design | Status |
|-------------|----------|---------------|------------------------------|--------|
| [5] described as "Meta-Analysis" | 5 | Meta-Analysis | Meta-Analysis / Systematic Review (but different paper: flipped classroom) | **MISLABELLED** — correct design label but wrong paper |
| [9] described as "Randomized Controlled Trial" | 9 | RCT | RCT (but different paper: escape rooms, not AI tutoring) | **MISLABELLED** — correct design label but wrong paper |
| [29] described as "Quasi-Experimental Design" | 29 | QED | Observational / Correlational (Mathematical Capabilities of ChatGPT) | **MISLABELLED** — wrong design label and wrong paper |
| [25] described as "Observational / Survey" | 25 | Observational / Survey | RCT (Investigating Students' Preferences for AI Roles in Mathematical Modelling) | **MISLABELLED** — wrong design label and wrong paper |
| [27] described as "Quasi-Experimental Design" | 27 | QED | Observational / Correlational (Do Students Rely on AI?) | **MISLABELLED** — wrong design label and wrong paper |
| [85] described as "Mixed-Methods / Survey" | 85 | Mixed-Methods | Mixed-Methods | **CORRECT** |
| [173] described as "Observational / Correlational" | 173 | Observational / Correlational | Observational / Correlational | **CORRECT** |

**Issues found:**
- **[29]**: Claimed QED, but PreScoredTiers #29 is Observational/Correlational.
- **[25]**: Claimed Observational/Survey, but PreScoredTiers #25 is an RCT.
- **[27]**: Claimed QED, but PreScoredTiers #27 is Observational/Correlational.
- [5] and [9] have technically matching design labels but refer to completely wrong papers, which is fundamentally misleading.

---

## Check 4 — Sub-question Coverage

| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| 1 | What definitions and types of generative AI tools are used in K-8 math education? | **Partially covered** — described with some detail | [5], [173] (both misattributed) |
| 1 | Which math skills and outcomes are most relevant for assessing K-8 student progress? | **Partially covered** — mentioned briefly | [25] (misattributed) |
| 1 | What are the characteristics of K-8 student populations and educational contexts? | **Partially covered** — mentioned populations but limited detail | [5], [29], [173] (mostly misattributed) |
| 2 | What traditional instructional methods and educational technologies are typically used without generative AI? | **Partially covered** — briefly described | [5], [27] (both misattributed) |
| 2 | How do existing educational technologies compare to generative AI tools in K-8 math? | **Weakly covered** — acknowledged gap, no direct comparative citations with correct sources | [5], [27] (misattributed) |
| 2 | What are baseline student math achievement outcomes without AI interventions? | **Not covered** — no specific baseline data cited | None |
| 3 | How are generative AI tools integrated into instructional practice and curricula? | **Partially covered** — described teacher-led vs student-driven models | [25], [85] |
| 3 | What delivery models exist for generative AI integration? | **Partially covered** — discussed hybrid models | [27] (misattributed), [85] |
| 3 | What cognitive and motivational mechanisms do generative AI tools engage? | **Partially covered** — described scaffolding, feedback, SRL | [25] (misattributed), [9] (misattributed) |
| 4 | What is the evidence on generative AI effectiveness vs. traditional instruction in K-8 math? | **Partially covered** — meta-analytic evidence cited but source misattributed | [5], [9] (both misattributed) |
| 4 | How do generative AI tools impact different math domains? | **Weakly covered** — mentioned briefly, no specific citations with verified data | None specifically |
| 4 | What limitations and contextual factors influence generative AI effectiveness? | **Covered** — discussed in detail | [173], [85] |
| 4 | How do outcomes with generative AI compare to other EdTech interventions? | **Not substantively covered** — acknowledged as a gap | [5], [27] (misattributed) |

**Summary:** No tier is fully covered with correctly attributed citations. Tiers 1, 3, and 4 are partially addressed. Tier 2 is weakly addressed. Several sub-questions lack any verified supporting citations.

---

## Check 5 — URL Integrity

| # | Bibliography URL | PreScoredTiers URL | Status |
|---|-----------------|-------------------|--------|
| 5 | https://doi.org/10.48550/arXiv.2601.18685 | https://doi.org/10.1186/s12909-018-1144-z | **INVENTED** — URL does not appear in PreScoredTiers or iteration history for source #5 |
| 9 | https://doi.org/10.1101/2025.02.21.23286202 | https://doi.org/10.1109/TE.2024.3403913 | **INVENTED** — URL does not appear in PreScoredTiers for source #9 |
| 25 | https://arxiv.org/abs/2507.17985 | https://arxiv.org/abs/2510.06617v1 | **INVENTED** — URL does not appear in PreScoredTiers for source #25 |
| 27 | "URL from PreScoredTiers" (placeholder) | https://arxiv.org/abs/2508.20244v1 | **MISMATCH** — placeholder used instead of actual URL |
| 29 | https://doi.org/10.30935/cedtech/15487 | https://arxiv.org/abs/2301.13867v2 | **INVENTED** — URL does not appear in PreScoredTiers for source #29 |
| 85 | "URL from PreScoredTiers" (placeholder) | https://doi.org/10.1007/s10639-025-13350-w | **MISMATCH** — placeholder, but the paper identity matches |
| 173 | "URL from PreScoredTiers" (placeholder) | arXiv:2411.15971v1 | **MISMATCH** — placeholder, but the paper identity matches |

**Issues found:**
- **[5]**: INVENTED URL
- **[9]**: INVENTED URL
- **[25]**: INVENTED URL
- **[29]**: INVENTED URL
- **[27]**: MISMATCH (placeholder)
- **[85]**: MISMATCH (placeholder)
- **[173]**: MISMATCH (placeholder)

---

## Recommended Fixes

1. **[CRITICAL] Reassign source numbers or replace bibliography entries for [5], [9], [25], [27], and [29].** The report describes studies (Strohmaier et al. 2026, Bastani et al. 2025, Liu et al. 2025, Thomas et al. 2023, Rizos et al. 2024) that do not correspond to those numbers in the PreScoredTiers. Either locate the correct source numbers for these studies from the PreScoredTiers list, or remove these citations and acknowledge the studies cannot be linked to the provided source list. The studies described in the report as [5], [9], [25], [27], and [29] appear to be real research not included in the numbered source list.

2. **[CRITICAL] Correct all URLs in the bibliography.** Five of seven URLs are invented (not found in PreScoredTiers) and two are placeholders. Replace all with the correct URLs from PreScoredTiers, or if the intended papers are not in the source list, acknowledge this transparently.

3. **[CRITICAL] Correct study design labels for [25], [27], and [29].** PreScoredTiers #25 is an RCT (not Observational/Survey), #27 is Observational/Correlational (not QED), and #29 is Observational/Correlational (not QED). If the report is describing different papers, the mismatch must be resolved.

4. **[HIGH] Verify all statistics against source documents.** The effect size g = 0.42, "21 studies with 38 effect sizes," "50% teacher usage," and all other specific claims should be verified against the actual numbered sources. Currently none can be verified because the source numbers point to different papers.

5. **[HIGH] Address Tier 2 sub-questions more substantively** with correctly cited evidence. Baseline achievement data and direct comparisons between generative AI and other EdTech tools in K-8 math are not covered with valid citations.

6. **[MODERATE] Replace placeholder text "URL from PreScoredTiers"** for entries [27], [85], and [173] with actual URLs from the source list.

7. **[MODERATE] Add quality/impact tier information** from PreScoredTiers to the bibliography to enable readers to assess evidence strength — currently the tiers listed for misattributed sources (e.g., Blue/Blue for [5]) do not match the actual PreScoredTiers ratings.

8. **[LOW] Acknowledge explicitly in limitations** that several key studies cited in the iteration history (Strohmaier et al. 2026, Bastani et al. 2025, etc.) may not have been included in the provided source list, and that source attribution could not be verified.

---

## Score

| Dimension | Max | Score | Rationale |
|-----------|-----|-------|-----------|
| Citation–bibliography linkage | 20 | 10 | 5 of 7 bibliography entries describe papers that do not match their PreScoredTiers number (5 × 2 = 10 deducted). |
| Statistic provenance | 25 | 0 | 0 of 6 statistics verified against correct numbered sources; all are UNVERIFIED due to systematic source number misattribution. (0/6 × 25 = 0) |
| Study design accuracy | 15 | 0 | 5 sources have mislabelled designs when checked against the actual PreScoredTiers entries (3 outright wrong labels + 2 correct labels but wrong papers = 5 × 5 = 25, capped at 15 de

---

## Score Summary

| Dimension | Score |
|-----------|-------|
| Citation–bibliography linkage | 10/20 |
| Statistic provenance | 0/25 |
| Study design accuracy | 0/15 |
| Sub-question coverage | 0/20 |
| URL integrity | 0/20 |
| **Overall** | **10/100** |
