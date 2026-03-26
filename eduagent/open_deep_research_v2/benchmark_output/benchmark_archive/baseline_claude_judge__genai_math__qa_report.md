# QA Audit: baseline_claude_judge — genai_math

**Score: 51/100**

---



## Audit Summary

The report presents a moderately trustworthy synthesis of generative AI in K-8 mathematics education, but suffers from **serious citation-bibliography mismatches** where pre-numbered source IDs are systematically mapped to the wrong papers. Nearly every bibliography entry links a source number to a paper that does not correspond to that number in the PreScoredTiers list (e.g., [6] in the report refers to "LearnLM Team Google, 2025" but [6] in the source list is a QED on ChatGPT in UAE schools about electronic magnetism; [7] is described as Strohmaier et al. meta-analysis but source [7] is a Jordanian student attitudes survey; [10] is cited as Bastani et al. quasi-experiment but source [10] is a ChatGPT flipped learning QED). This indicates the authors built an internal numbering system that diverges entirely from the pre-scored source list, rendering the bibliography unreliable for verification. URLs are similarly mismatched. Several key statistics are traceable to iteration history but not to the specific pre-numbered sources cited. Study design labels are applied to papers that do not correspond to the numbered entries they claim. The most critical issue is the wholesale mismapping of citation numbers to source entries.

---

## Check 1 — Citation-Bibliography Linkage

**Inline citations used in report body:** [6], [7], [9], [10], [11], [15], [24], [36], [86], [94], [96], [105], [120], [156]

**Bibliography entries:** [6], [7], [9], [10], [11], [15], [24], [36], [86], [94], [96], [105], [120], [156]

**Linkage check (inline → bibliography):**
- All 14 inline citations appear in the bibliography. ✔

**Orphan bibliography entries (in bibliography but never cited inline):**
- [96] is cited in the body ("effect sizes 0.18–0.70 for non-AI adaptive tools" and "standardized tests like TerraNova, CAASPP, PISA, and TIMSS [96]"). ✔ Not orphan.
- [105] is cited inline ("co-creator supporting collaborative tasks…[7; 105]"). ✔ Not orphan.
- No orphan entries found.

**Title/URL mismatches between bibliography and PreScoredTiers:** See Check 5 for details — nearly all are mismatched.

---

## Check 2 — Statistic Provenance

| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| Hedges' g ≈ 0.31 to 0.42 | [7] (Strohmaier et al., 2026) | PARTIALLY VERIFIED | Iteration 1 reports g ≈ 0.31 [95% CI: 0.06–0.58]; Iteration 2 mentions g = 0.31 to 0.42. The 0.42 upper bound is mentioned in Iteration 2 but without precise sourcing; 0.31 is verified in iteration history. |
| n=165 secondary students (LearnLM RCT) | [6] | VERIFIED | Iteration 2 states "LearnLM Team (2025) — Controlled trial (RCT, n=165 secondary students)" |
| n=15,700 students (Thomas et al. quasi-experiment) | [36] | VERIFIED | Iteration 2 states "Thomas et al. (2023) — Quasi-experimental study (n=15,700)" |
| Effect sizes 0.18–0.70 for non-AI adaptive tools | [96] | PARTIALLY VERIFIED | Iteration 1 mentions "+0.18 to +0.20" for non-generative digital tools. The upper bound of 0.70 is not found verbatim in iteration history. |
| "about half have used generative AI tools" (teacher survey) | [7] | VERIFIED | Iteration 2 states "roughly half of K-12 math teachers have used generative AI tools" |
| 4 percentage points more likely to pass exit tickets (Tutor CoPilot) | [94] | VERIFIED | PreScoredTiers [94] finding states "4 percentage point increase overall; up to 9 percentage points for lower-rated tutors" |
| 95% CI [0.06, 0.58] for g=0.31 | [7] | VERIFIED | Iteration 1 explicitly reports "g ≈ 0.31 [95% CI: 0.06–0.58]" |

**Summary of unverified/fabricated:**
- The 0.70 upper bound for non-AI adaptive tools effect sizes is **UNVERIFIED** — iteration history only mentions 0.18–0.20.
- The 0.42 upper bound for Hedges' g is loosely supported in Iteration 2 wording but not precisely sourced — **UNVERIFIED** as an exact value.

---

## Check 3 — Study Design Accuracy

| Claim in Report | Source # | Report Label | PreScoredTiers Label | Status |
|----------------|----------|-------------|---------------------|--------|
| LearnLM Team (2025) — Exploratory RCT | [6] | RCT | PreScoredTiers [6] = QED (ChatGPT in UAE schools, electronic magnetism) | **MISMATCH** — Source [6] in PreScoredTiers is a QED, not an RCT, and is a completely different study |
| Thomas et al. (2023) — Quasi-experimental | [36] | Quasi-experimental | PreScoredTiers [36] = Observational/Correlational (clinical trial digital twins) | **MISMATCH** — Source [36] in PreScoredTiers is not a QED and is a completely different study |
| Bastani et al. (2024) — Quasi-experimental | [10] | Quasi-experimental | PreScoredTiers [10] = QED (ChatGPT flipped learning) | **PARTIAL MISMATCH** — Design label matches (QED) but the study is entirely different (courseware design, not AI guardrails in math) |
| Tutor CoPilot — RCT | [94] | RCT | PreScoredTiers [94] = RCT | **MATCH** on design label and study identity ✔ |
| Strohmaier et al. — Meta-analysis | [7] | Meta-analysis | PreScoredTiers [7] = Observational/Correlational (Jordanian students' attitudes) | **MISMATCH** — Completely different study |
| Gabriel et al. (2025) — Observational | [9] | Observational | PreScoredTiers [9] = QED (ChatGPT programming problems) | **MISMATCH** — Different study and design |
| Ahmed et al. (2024) — Mixed methods review | [11] | Report/Review | PreScoredTiers [11] = Observational/Correlational (Generative AI in education) | **PARTIAL MISMATCH** — Study identity may loosely align but design label differs |

**Flagged issues:** 5 study design mismatches due to wrong source-number mapping; 1 confirmed match ([94]).

---

## Check 4 — Sub-question Coverage

| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| 1 | What are generative AI tools and how are they defined in K-8 math? | ✅ Fully covered | [7], [11] |
| 1 | What specific math skills and outcomes are targeted? | ✅ Covered | [7], [86] |
| 1 | Demographic and educational context of K-8 students? | ⚠️ Partially covered — mentioned briefly (diverse contexts, special ed) but no detailed demographic analysis | [7], [86] |
| 2 | Traditional instructional methods without AI? | ✅ Covered | [96] |
| 2 | Non-AI digital math tools as baseline comparators? | ✅ Covered | [96] |
| 2 | Common benchmarks/assessments in K-8 math research? | ✅ Covered (TerraNova, CAASPP, PISA, TIMSS mentioned) | [96] |
| 3 | How are generative AI tools integrated into K-8 math instruction? | ✅ Covered | [6], [10], [86], [24] |
| 3 | Pedagogical strategies accompanying AI use? | ✅ Covered | [6], [10], [120], [156] |
| 3 | Mechanisms enhancing engagement and understanding? | ✅ Covered | [7], [105], [9] |
| 4 | Evidence for AI effectiveness vs traditional? | ✅ Covered | [6], [36], [7], [10] |
| 4 | Impact on engagement and attitudes among diverse K-8 populations? | ⚠️ Partially covered — attitudes discussed but diversity dimensions thin | [156], [86] |
| 4 | Reported limitations and challenges? | ✅ Covered in Limitations section | [10], [9], [7] |
| 4 | Variation across contexts, demographics, or math subdomains? | ⚠️ Partially covered — acknowledged as gap but minimal cited evidence for subdomain variation | [7], [24] |

**Tiers with insufficient cited evidence:** Tier 1 (demographics sub-question), Tier 4 (diversity/subdomain variation) are only partially addressed.

---

## Check 5 — URL Integrity

| # | Report URL | PreScoredTiers URL | Status |
|---|------------|-------------------|--------|
| 6 | `https://doi.org/10.18267/j.aip.235` | `https://doi.org/10.30935/cedtech/13417` | **MISMATCH** — Report URL is actually PreScoredTiers [11]'s URL |
| 7 | `https://doi.org/10.1038/s41539-025-00320-7` | `https://doi.org/10.3991/ijim.v17i18.41753` | **MISMATCH** — Report URL is actually PreScoredTiers [2]'s URL |
| 9 | `https://doi.org/10.3389/feduc.2025.1697554/full` | `https://doi.org/10.1057/s41599-024-02751-w` | **MISMATCH** — Report URL is PreScoredTiers [154]'s URL |
| 10 | `https://doi.org/10.1057/s41599-025-04787-y` | `https://doi.org/10.14742/ajet.8923` | **MISMATCH** — Report URL is actually PreScoredTiers [4]'s URL |
| 11 | `https://doi.org/10.1057/s41599-024-02717-y` | `https://doi.org/10.18267/j.aip.235` | **MISMATCH** — Report URL is PreScoredTiers [5]'s URL |
| 15 | `https://doi.org/10.1007/s11423-023-10203-6` | Not in PreScoredTiers as [15] | **MISMATCH** — PreScoredTiers [15] URL is `https://arxiv.org/abs/2108.08756v1`; Report URL is PreScoredTiers [122]'s URL |
| 24 | `https://doi.org/10.1787/edu_wkp-v2024-15-en` | `https://doi.org/10.1787/edu_wkp-v2024-15-en` | **OK** ✔ |
| 36 | `https://doi.org/10.3389/feduc.2025.1574477/full` | `https://arxiv.org/abs/2404.17576v1` | **MISMATCH** — Report URL is PreScoredTiers [158]'s URL |
| 86 | `https://arxiv.org/abs/2504.17117` | `https://arxiv.org/abs/2504.17117` | **OK** ✔ |
| 94 | `https://arxiv.org/abs/2410.03017` | `https://arxiv.org/abs/2410.03017` | **OK** ✔ |
| 96 | `https://www.frontiersin.org/articles/10.3389/fpsyg.2025.1540169/full` | `https://www.frontiersin.org/articles/10.3389/fpsyg.2025.1540169/full` | **OK** ✔ |
| 105 | No URL in bibliography | `https://doi.org/10.1145/3772318.3791138` | **N/A** — no URL to check (entry #105 not given a URL in bibliography) |
| 120 | `https://doi.org/10.1007/s10639-022-11316-w` | `https://doi.org/10.1007/s10639-022-11316-w` | **OK** ✔ |
| 156 | `https://www.frontiersin.org/articles/10.3389/feduc.2025.1488147/full` | `https://www.frontiersin.org/articles/10.3389/feduc.2025.1488147/full` | **OK** ✔ |

**Summary:** 7 MISMATCH URLs, 6 OK URLs, 1 entry without URL in bibliography.

---

## Recommended Fixes

1. **[CRITICAL] Remap all citation numbers to match the PreScoredTiers source list.** The report uses an internal numbering system that does not correspond to the provided pre-numbered source list. Source [6] should reference the UAE ChatGPT QED study, [7] the Jordanian attitudes study, [10] the flipped learning QED, etc. The authors must either (a) renumber all citations to match the PreScoredTiers, or (b) add the actual studies (LearnLM Team, Strohmaier meta-analysis, Bastani guardrails study, etc.) as new entries with correct IDs if they are not in the pre-scored list.

2. **[CRITICAL] Correct all mismatched URLs in the bibliography** to align with the PreScoredTiers URLs for each source number, or correctly assign new source numbers.

3. **[HIGH] Verify and correct the effect size range 0.18–0.70 for non-AI adaptive tools.** The iteration history only supports 0.18–0.20. The 0.70 upper bound appears fabricated or drawn from an unsourced finding. Either provide a source or revise to 0.18–0.20.

4. **[HIGH] Verify the Hedges' g = 0.42 upper bound.** Iteration history primarily reports g ≈ 0.31 with CI [0.06, 0.58]. The 0.42 appears in Iteration 2 but without precise attribution. Clarify whether this is from a subgroup analysis or revise.

5. **[HIGH] Correct study design labels** for all entries where the report's design label does not match the PreScoredTiers (entries [6], [7], [9], [10], [11], [36]).

6. **[MEDIUM] Expand demographic coverage** for Tier 1 sub-question on K-8 student demographics and Tier 4 sub-questions on diversity and subdomain variation, with specific cited evidence.

7. **[MEDIUM] Add a URL for bibliography entry [105]** or note it explicitly.

8. **[LOW] Clarify attribution** for claims about "Yuan & Hu, 2024" noted as "evidence not retrieved" in the Executive Summary table — either find and cite or remove.

---

## Score

| Dimension | Max | Score | Rationale (1 sentence) |
|-----------|-----|-------|------------------------|
| Citation–bibliography linkage | 20 | 18 | All inline citations appear in bibliography and no orphans, but titles/papers mapped to numbers are wrong (addressed under URL/design checks). |
| Statistic provenance | 25 | 18 | 5 of 7 statistics verified or partially verified; 2 are unverified (0.70 upper bound likely fabricated, 0.42 unsourced), yielding ~71% verified. |
| Study design accuracy | 15 | 0

---

## Score Summary

| Dimension | Score |
|-----------|-------|
| Citation–bibliography linkage | 18/20 |
| Statistic provenance | 18/25 |
| Study design accuracy | 0/15 |
| Sub-question coverage | 15/20 |
| URL integrity | 0/20 |
| **Overall** | **51/100** |
