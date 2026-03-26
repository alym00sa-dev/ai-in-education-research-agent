# QA Audit: ranking_v1 — genai_math

**Score: 44/100**

---



## Audit Summary

The report is partially trustworthy but contains several significant issues that undermine its reliability. The most critical problems are: (1) systematic citation numbering mismatches — the report's inline citations [191], [192], [195], [196], [263], and [276] do not correspond to the correct sources in the pre-numbered academic-DB list or supplementary sources list, creating a pervasive cross-referencing failure; (2) some statistics cited in the report (e.g., the primary vs. secondary effect size breakdown g=0.754 vs. g=0.313) are attributed to sources that cannot be precisely verified in the iteration history beyond general mentions; (3) study design labels for notes-sourced papers are applied without clear iteration-history support in some cases. The report's substantive conclusions are broadly consistent with the iteration history, but the bibliographic infrastructure is unreliable enough to warrant a comprehensive correction pass before the report can be considered audit-ready.

---

## Check 1 — Citation-Bibliography Linkage

**Numbering misalignment issues:**

The report uses inline citations [191], [192], [195], [196], [200], [228], [250], [263], [276], [292]. The bibliography lists entries numbered 191, 192, 195, 196, 200, 228, 250, 263, 276, 292. However, there are critical mismatches between what the report intends to cite and the actual source at that number:

| Inline [N] | Report Intended Source | Bibliography Entry | Supplementary Source List Entry [N] | Issue |
|---|---|---|---|---|
| [191] | Rizos et al., 2024 (special ed case study) | Rizos et al., 2024 — correct title | Supp [191] = Pan et al., 2026 (motivation survey) | **MISMATCH**: Supp list [191] is Pan et al., not Rizos. Rizos is supp [190]. Bibliography entry 191 has the Rizos URL (matching supp [190]), so the bibliography itself is internally inconsistent with supplementary numbering. |
| [192] | Pan et al., 2026 (motivation survey) | Pan et al., 2026 — correct title | Supp [192] = Kehoe, 2023 (lesson planning) | **MISMATCH**: Supp list [192] is Kehoe, not Pan. Pan is supp [191]. Bibliography entry 192 has the Pan URL (matching supp [191]). |
| [195] | Strohmaier et al., 2026 (LLAMA LIMA meta-analysis) | Strohmaier et al., 2026 — correct title | Supp [195] = Liu et al., 2025 (K-12 educators) | **MISMATCH**: Supp list [195] is Liu et al., not Strohmaier. Strohmaier is supp [194]. Bibliography entry 195 has the Strohmaier URL (matching supp [194]). |
| [196] | Liu et al., 2025 (K-12 educators survey) | Liu et al., 2025 — correct title | Supp [196] = Coşkun et al., 2025 (engineering design) | **MISMATCH**: Supp list [196] is Coşkun, not Liu. Liu is supp [195]. Bibliography entry 196 has the Liu URL (matching supp [195]). |
| [200] | Kadaruddin, 2023 | Kadaruddin, 2023 — correct title | Supp [200] = Lyu et al., 2026 (AI peers collaborative math) | **MISMATCH**: Supp list [200] is Lyu et al., not Kadaruddin. Kadaruddin is supp [199]. |
| [228] | Bura & Myakala, 2024 | Bura & Myakala, 2024 — correct title | Supp [228] = Hazzan-Bishara et al., 2025 (teacher adoption factors) | **MISMATCH**: Supp list [228] is Hazzan-Bishara, not Bura & Myakala. Bura & Myakala is supp [227]. |
| [250] | Bower et al., 2025 | Bower et al., 2025 — correct title | Supp [250] = Karpouzis et al., 2024 (lesson planning with GenAI) | **MISMATCH**: Supp list [250] is Karpouzis, not Bower. Bower is supp [249]. |
| [263] | Bastani et al., 2025 | Bastani et al., 2025 — correct title | Supp [263] = Bonnie Stewart, 2023 (GenAI position paper) | **MISMATCH**: Supp list [263] is Stewart, not Bastani. Bastani is supp [262]. |
| [276] | Thomas et al., 2025 (hybrid human-AI tutoring) | Thomas et al., 2025 — correct title | Supp [276] = Grünke et al., 2025 (Pegword method, math difficulties) | **MISMATCH**: Supp list [276] is Grünke, not Thomas. Thomas is supp [275]. |
| [292] | Adams et al., 2023 (ethical principles) | Adams et al., 2023 — correct title | No supp [292] in list (list appears to end before 292) | **Cannot verify** — source may exist beyond listed supplementary sources. |

**Summary**: The bibliography was constructed with titles and URLs that are consistently one number off from the supplementary source list for most entries (each bibliography number corresponds to the supplementary entry one number lower). This is a systematic off-by-one indexing error. The bibliography entries themselves are internally consistent (title matches URL), but they do NOT match the official supplementary source numbering.

**Orphan entries**: No orphan bibliography entries were found — all 10 bibliography entries are cited inline.

**Missing inline citations**: The report body mentions "Areen Hazzan-Bishara et al., 2025" by name without a bracketed number in some instances; this source appears to correspond to supp [228] but is cited by name rather than number. Similarly, "Oregon Department of Education, 2023" is mentioned with [250] but is actually Bower et al., 2025 in the bibliography. "Gabriel et al., 2025" appears in the executive summary table but has no corresponding bibliography entry — **FLAG: missing bibliography entry**.

---

## Check 2 — Statistic Provenance

| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| g ≈ 0.42 average effect size across 21 studies, 38 effect sizes | Strohmaier et al., 2026 [195] | VERIFIED | Mentioned in iterations 1, 2, and 3 |
| g = 0.754 for primary grades | Strohmaier et al., 2026 / "OpenAI Web Search" | VERIFIED | Mentioned in iteration 3 executive summary |
| g = 0.313 for secondary grades | Strohmaier et al., 2026 / "OpenAI Web Search" | VERIFIED | Mentioned in iteration 3 executive summary |
| 21 studies and 38 effect sizes in living meta-analysis | Strohmaier et al., 2026 [195] | VERIFIED | Consistent across iterations 2 and 3 |
| n ≈ 839 for Bastani et al. RCT | [263] Bastani et al., 2025 | VERIFIED | Mentioned in iteration 3 and source [46] finding (n=839) |
| n = 2 for Rizos et al. case study | [191] Rizos et al., 2024 | VERIFIED | Mentioned in iteration 2 (sample n=2) |
| n ≈ 2,000 for Thomas et al. QED | [276] Thomas et al., 2025 | UNVERIFIED | The iteration history does not report n≈2,000 for Thomas et al.; source [46] mentions different studies. Cannot confirm this sample size from iteration history. |
| 50% of educators use AI for lesson planning | [196] Liu et al., 2025 | VERIFIED | Mentioned in iteration 2: "50% AI usage primarily for lesson planning" |
| n = 979 for Liu et al. survey | [196] Liu et al., 2025 | VERIFIED | Iteration 2 mentions "nearly 1,000 K-12 science and math educators" |
| g = 1.164 for creative transformation instructional modes | "OpenAI Web Search, 2026" | VERIFIED | Mentioned in iteration 3 but attributed vaguely to "OpenAI Web Search" — not a formal citation |
| "effect size not reported" for Bastani et al. | [263] | VERIFIED | Iteration 2 states "statistic not reported" |

**Score calculation**: 9 verified, 1 unverified, 0 fabricated out of 10 distinct statistics checked.

---

## Check 3 — Study Design Accuracy

All cited studies are notes-sourced ([189]+), so design labels must be verified against iteration history, not the bibliography's "not_reported" column.

| Citation | Report Label | Iteration History Description | Status |
|----------|-------------|------------------------------|--------|
| [263] Bastani et al., 2025 | RCT, n ≈ 839 | Iteration 1: "large-scale field experiment"; Iteration 2: "large-scale randomized controlled trial"; Iteration 3: "large-scale field experiment" | **ACCEPTABLE** — described as RCT in iteration 2. Also confirmed in source [46] as RCT with n=839. |
| [191] Rizos et al., 2024 | Qualitative, n=2 | Iteration 2: "focused case study of two 8th-grade students" | **ACCEPTABLE** — case study with n=2 is consistent with qualitative. |
| [276] Thomas et al., 2025 | QED, n ≈ 2,000 | Iteration history does not explicitly describe Thomas et al. as QED or report n≈2,000. The title says "Quasi-Experimental Investigation." | **ACCEPTABLE** — title includes "Quasi-Experimental" which supports QED label. n≈2,000 is UNVERIFIED (see Check 2). |
| [196] Liu et al., 2025 | Observational survey, n = 979 | Iteration 2: "surveyed nearly 1,000 K-12 science and math educators" | **ACCEPTABLE** — survey is consistent with observational design. |
| [195] Strohmaier et al., 2026 | Meta-analysis | Iteration 1-3: "living meta-analysis" | **ACCEPTABLE** |

No mislabelling detected that contradicts iteration history.

---

## Check 4 — Sub-question Coverage

| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| 1 | What defines generative AI tools in K-8 math education, target skills/outcomes, and student populations? | **FULLY COVERED** — dedicated section with cited evidence | [195], [191] |
| 1 | What are the typical educational contexts for AI tool deployment in K-8 math learning? | **PARTIALLY COVERED** — mentioned in context of studies but no dedicated analysis of deployment contexts | [195], [196] |
| 2 | What baseline instructional methods and practice conditions serve as comparators? | **PARTIALLY COVERED** — brief section with limited specific comparator description | [276], [263] |
| 2 | How are math skills and outcomes commonly assessed without generative AI? | **PARTIALLY COVERED** — brief mention of standardized tests and formative assessments | [195] |
| 3 | How are generative AI tools implemented in K-8 math instruction, and what mechanisms drive learning gains? | **PARTIALLY COVERED** — hybrid models discussed, mechanisms described at high level | [276], [263], [196], [195] |
| 3 | What instructional delivery models are used alongside generative AI? | **PARTIALLY COVERED** — mentions teacher-led, hybrid, self-directed but acknowledges sparse evidence | [276], [196] |
| 4 | What is the evidence for generative AI effectiveness on math outcomes vs. standard methods? | **FULLY COVERED** — meta-analytic and experimental evidence presented | [195], [263], [276], [191] |
| 4 | How do effectiveness and trade-offs vary across K-8 subpopulations? | **PARTIALLY COVERED** — noted as gap, limited empirical coverage | [191], [263] |
| 4 | How does generative AI compare with other educational technologies? | **ADDRESSED BUT NOT SUPPORTED** — explicitly states no rigorous comparative evidence exists | None (acknowledged gap) |

Coverage assessment: 2 fully covered, 6 partially covered, 1 addressed but unsupported. Approximately 4/9 tiers have substantive cited evidence; the remaining are noted as gaps.

---

## Check 5 — URL Integrity

All bibliography entries are notes-sourced ([189]+), so URLs are compared against the supplementary sources list.

| Bib # | Bibliography URL | Supp Source URL at Same Number | Status | Notes |
|---|---|---|---|---|
| 191 | https://www.semanticscholar.org/paper/c5176feb286e0e266032f5277c20d0ded1837bf3 | Supp [191] URL: https://www.semanticscholar.org/paper/ed11f6da6dbbce539c93a3031db9358b3804fd08 | **MISMATCH** — Bibliography URL matches supp [190] (Rizos), not supp [191] (Pan). Off-by-one error. |
| 192 | https://www.semanticscholar.org/paper/ed11f6da6dbbce539c93a3031db9358b3804fd08 | Supp [192] URL: https://www.semanticscholar.org/paper/a610485fa634e2c4f95cec5db643289c5c1f7fed | **MISMATCH** — Bibliography URL matches supp [191] (Pan), not supp [192] (Kehoe). |
| 195 | https://www.semanticscholar.org/paper/dc4424ba8e77f9bf11df017c58ebf3f08e82242d | Supp [195] URL: https://arxiv.org/abs/2507.17985 | **MISMATCH** — Bibliography URL matches supp [194] (Strohmaier), not supp [195] (Liu). |
| 196 | https://arxiv.org/abs/2507.17985 | Supp [196] URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC12453255 | **MISMATCH** — Bibliography URL matches supp [195] (Liu), not supp [196] (Coşkun). |
| 200 | https://www.semanticscholar.org/paper/97d8be9c22d9bc76b5febbd989a7b48ecb951b81 | Supp [200] URL: https://www.semanticscholar.org/paper/eb33f2e155fb6409ab090259436838260b695acd | **MISMATCH** — Bibliography URL matches supp [199] (Kadaruddin), not supp [200] (Lyu). |
| 228 | https://arxiv.org/abs/2411.15971 | Supp [228] URL: https://www.semanticscholar.org/paper/18b8af39397a8771fcf373e9b3ca2f97b9fb985b | **MISMATCH** — Bibliography URL matches supp [227] (Bura & Myakala), not supp [228] (Hazzan-Bishara). |
| 250 | https://doi.org/10.1007/s13384-025-00801-z | Supp [250] URL: https://arxiv.org/abs/2403.12071 | **MISMATCH** — Bibliography URL matches supp [249] (Bower), not supp [250] (Karpouzis). |
| 263 | https://pmc.ncbi.nlm.nih.gov/articles/PMC12232635 | Supp [263] URL: https://www.semanticscholar.org/paper/f7cd3da6fe3a76cd80e968f919bbd7253690989d

---

## Score Summary

| Dimension | Score |
|-----------|-------|
| Citation–bibliography linkage | 2/20 |
| Statistic provenance | 23/25 |
| Study design accuracy | 15/15 |
| Sub-question coverage | 4/20 |
| URL integrity | 0/20 |
| **Overall** | **44/100** |
