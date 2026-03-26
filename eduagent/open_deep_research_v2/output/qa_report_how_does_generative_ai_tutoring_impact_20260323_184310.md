

## Audit Summary

The report is generally trustworthy in its cautious framing and directional conclusions, but it contains several significant issues: (1) a critical citation error where [183] is cited as "Tutor CoPilot" (Wang et al., 2024) but the bibliography entry for [183] is actually a systematic review on prompt engineering by Chen et al. — the actual Tutor CoPilot paper is source [49] in the academic-DB; (2) source [271] (Henkel et al., 2024, the Ghana study) is cited prominently but does not appear in the bibliography table; (3) the meta-analytic statistic g=0.42 from iteration 2 is referenced in the claims table but the exact figure does not appear in the final report text, while the claims table describes it vaguely; (4) several bibliography entries are orphaned; and (5) the study design labels cannot be verified against the pre-numbered source list for notes-sourced papers since all are listed as "not_reported." The statistics cited in the report are largely traceable to the iteration history, with a few exceptions. Overall, the report is a reasonable synthesis but needs corrections to citation-bibliography linkage and one key source misidentification.

## Check 1 — Citation-Bibliography Linkage

**Inline citations checked against bibliography:**

| Citation | In Bibliography? | Issue |
|----------|-----------------|-------|
| [168] | Yes | OK |
| [147] | Yes | OK |
| [153] | Yes | OK |
| [158] | Yes | OK |
| [183] | Yes | **MISMATCH**: Report cites [183] as "Tutor CoPilot" (Wang et al., 2024) describing an RCT of real-time LLM guidance for human tutors. However, bibliography entry [183] is "A Systematic Review on Prompt Engineering in Large Language Models for K-12 STEM Education" by Eason Chen et al. (2024). The actual Tutor CoPilot paper is [49] in the academic-DB source list. |
| [186] | Yes | OK |
| [199] | Yes | OK |
| [142] | Yes | OK |
| [171] | Yes | OK |
| [170] | Yes | OK |
| [376] | Yes | OK |
| [285] | Yes | OK |
| [166] | Yes | OK |
| [167] | Yes | OK |
| [368] | Yes | OK |
| [363] | Yes | OK |
| [271] | **NO** — cited inline in Executive Summary and body but **missing from Bibliography table** | **MISSING** |

**Orphan bibliography entries (in bibliography but never cited inline):**
- None detected — all bibliography entries appear to have at least one inline citation.

**Summary of issues:**
1. [271] is cited inline but missing from the bibliography.
2. [183] bibliography entry does not match the content attributed to it in the report (should be [49]).

## Check 2 — Statistic Provenance

| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| LearnLM 5.5 percentage point gain on novel-problem transfer | [168] | VERIFIED | Iteration 1, 2, 3 all report "5.5 percentage points more likely to solve novel problems on subsequent topics" and source [32] finding confirms |
| 66.2% success vs 60.7% for human tutoring | [168] | VERIFIED | Iteration 2 and 3 report "66.2% versus 60.7%" |
| n=165 students in LearnLM RCT | [168] | VERIFIED | Iteration 1, 2, 3 confirm n=165; source [32] confirms |
| Supervisors approved 76.4% of drafted messages with zero or minimal edits | [168] | VERIFIED | Iteration 2 and 3 confirm "76.4% of drafted messages" |
| Ghana study d=0.37, p<0.001 | [271] | VERIFIED | Iteration 2 reports "effect size of 0.37, with p<0.001" |
| Ghana study approximately n≈1,000, grades 3-9, 11 schools | [271] | VERIFIED | Iteration 2 reports "approximately 1,000 students in grades 3–9 across 11 schools" |
| Ghana study two 30-minute sessions per week for eight months | [271] | VERIFIED | Iteration 2 reports "two 30-minute sessions per week for eight months" |
| AI-based tutoring improved practice but students underperformed when AI removed | [147] | VERIFIED | Iteration 2 and 3 report this finding |
| Teacher-designed hints mitigated negative effects (exact effect size not reported) | [147] | VERIFIED | Iteration 2 and 3 note "exact effect size was not reported" |
| Tutor CoPilot: 4 percentage points more likely to master topics overall | [183] (should be [49]) | VERIFIED | Source [49] finding confirms "4 percentage points more likely to pass exit tickets (62% vs 66%)" |
| Tutor CoPilot: 9 percentage points more likely for lower-rated tutors | [183] (should be [49]) | VERIFIED | Iteration 1 summary mentions this statistic; source [49] summary does not give exact 9pp figure in excerpts, but iteration history attributes it. Found in iteration 2 indirectly but the "9 percentage points" figure does not appear verbatim in the iteration history excerpts provided. | 
| 9 percentage points for lower-rated tutors' students | [183] (should be [49]) | UNVERIFIED | The "9 percentage points" figure does not appear verbatim in any iteration history excerpt or source [49] findings provided. The source findings mention "4 percentage points" overall but the 9pp for lower-rated tutors is not confirmed in the materials given. |
| ChatGPT vs human hint study n=274 | [186] | VERIFIED | Iteration 2 reports "274 learners" |
| Positive gains in all conditions, only human tutor hints statistically significant | [186] | VERIFIED | Iteration 2 and 3 confirm this pattern |
| Algebra hint study n=77 | [199] | VERIFIED | Iteration 2 and 3 report "77 participants"; source [92] confirms |
| Human tutor hints substantially and statistically significantly higher gains than ChatGPT | [199] | VERIFIED | Iteration 2 and 3 confirm |
| LLM-Tutor proof study n=148, improved homework but not exam performance | [153] | VERIFIED | Iteration 3 reports "N=148 students found improved homework performance versus a control group…but no significant impact on exams or time spent" |
| Living meta-analysis: small positive average effect, exploratory and inconclusive | [142] | VERIFIED | Iteration 2 reports "g = 0.42 across 21 studies and 38 effect sizes" and notes heterogeneity; the report's claims table describes it as "small positive average effect" which is consistent |
| Lower-achieving students benefiting more in hybrid human-AI tutoring | [158] | VERIFIED | Iterations 1, 2, 3 all report "lower-achieving students benefited more" |

**Verified: 15/17, Unverified: 1, Fabricated: 0**

The "9 percentage points" statistic for Tutor CoPilot is UNVERIFIED — it does not appear verbatim in the provided iteration history or source findings.

## Check 3 — Study Design Accuracy

All sources cited as RCTs or QEDs in the report are notes-sourced ([142]+), so design labels must be verified against the iteration history, not the bibliography's "not_reported" column.

| Source | Report Label | Iteration History Description | Status |
|--------|-------------|------------------------------|--------|
| [168] LearnLM | "exploratory RCT" | Iteration 1: "RCT-style studies"; Iteration 2: "exploratory RCT"; Source [32] in academic-DB: RCT | **OK** |
| [271] Ghana study | "quasi-experimental study" | Iteration 2: "treatment or control" but described as QED-like; no explicit RCT label in iteration history | **OK** — labeled quasi-experimental, consistent with iteration history description |
| [147] Bastani et al. | "large-scale high-school field experiment" | Iteration 1: "quasi-experimental study"; Iteration 3: "high-school field experiment" | **OK** — report does not label it as RCT; "field experiment" is consistent |
| [158] Thomas et al. | "three-study quasi-experimental investigation" | Iteration 1, 2, 3: "quasi-experimental"; source [91] in academic-DB: QED | **OK** |
| [183] cited as Tutor CoPilot | "randomized trial" | Source [49] in academic-DB is labeled RCT | **OK** for the actual study, but the citation number is wrong (should be [49]) |
| [186] Pardos & Bhandari 2024 | "online randomized study" | Iteration 2: "randomly assigned"; source is described as randomized | **OK** |
| [199] Pardos & Bhandari 2023 | Implied experimental (n=77) | Source [92] in academic-DB: RCT | **OK** |
| [153] Chen et al. | Not explicitly labeled as RCT/QED in body; claims table says study with n=148 | Iteration 3: mentions "control group" suggesting experimental; no explicit RCT label | **OK** — report does not mislabel |

**Issue:** The Tutor CoPilot study is correctly described as an RCT, but it is attributed to [183] instead of [49]. This is a citation linkage error (already flagged in Check 1) rather than a design accuracy error per se.

No study design mislabelling detected.

## Check 4 — Sub-question Coverage

| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| 1 | What counts as generative AI tutoring in K-12 math? | Partially covered — discussed in executive summary noting the fuzzy boundary | [142][171] |
| 1 | Which mathematics outcomes are most relevant? | Partially covered — achievement, transfer, homework, engagement mentioned | [168][153][186] |
| 1 | How do grade span, prior achievement, language status, and special education status shape populations? | Partially covered — grade span addressed (secondary/middle vs elementary gap noted); subgroup characteristics flagged as gaps | [158][285][368] |
| 2 | How are K-12 math skills typically supported without generative AI? | Partially covered — comparators mentioned but evidence thin | [186][158][376] |
| 2 | What baseline instructional models are used? | Partially covered — static hints, human tutors, no-access controls discussed | [168][186] |
| 2 | Which comparison conditions are most appropriate? | Partially covered — report explicitly notes comparator gap | [168][186][158] |
| 3 | How is generative AI tutoring integrated into instruction? | Covered — supervised supplement vs standalone discussed | [168][147][170] |
| 3 | What types of AI-generated support are provided? | Covered — hints, Socratic prompts, feedback, scaffolds | [168][183][170] |
| 3 | Implementation features (teacher mediation, guardrails, dosage, alignment)? | Partially covered — discussed qualitatively but not systematically | [147][168][170] |
| 4 | Impact on achievement, conceptual understanding, problem-solving? | Covered — multiple studies cited with effects | [168][271][147][186][199][153] |
| 4 | Subgroup effects? | Minimally covered — flagged as major gap, only indirect evidence | [158][376][285] |
| 4 | Effects by implementation model, dosage, teacher oversight? | Partially covered — discussed but not systematically evidenced | [147][168][170] |
| 4 | Tradeoffs, risks, limitations? | Covered — answer-giving, overreliance, reduced transfer discussed | [147][153][199] |

**Summary:** All tiers are addressed with at least some cited evidence. Tier 1, Tier 2, and Tier 4 (subgroups) are the weakest but the report explicitly acknowledges these as gaps. No tier is completely unaddressed.

- Tier 1: Partially covered (3 sub-questions partially addressed)
- Tier 2: Partially covered (3 sub-questions partially addressed)
- Tier 3: Mostly covered (3 sub-questions addressed, one partially)
- Tier 4: Mixed (2 covered, 2 partially/minimally covered)

## Check 5 — URL Integrity

**Academic-DB sources ([1]–[141]) cited in bibliography:**
No academic-DB sources appear in the bibliography (all bibliography entries are [142]+).

**Notes-sourced sources ([142]+):**

| # | Bibliography URL | Supplementary Sources URL | Status |
|---|-----------------|--------------------------|--------|
| 142 | https://arxiv.org/abs/2601.18685 | https://arxiv.org/abs/2601.18685 | OK |
| 147 | https://pmc.ncbi.nlm.nih.gov/articles/PMC12232635 | https://pmc.ncbi.nlm.nih.gov/articles/PMC12232635 | OK |
| 153 | https://arxiv.org/abs/2509.16778 | https://arxiv.org/abs/2509.16778 | OK |
| 158 | https://arxiv.org/abs/2312.11274 | https://arxiv.org/abs/2312.11274 | OK |
| 166 | https://arxiv.org/abs/2409.06723 | https://arxiv.org/abs/2409.06723 | OK |
| 167 | https://arxiv.org/abs/2601.17962 | https://arxiv.org/abs/2601.17962 | OK |
| 168 | https://arxiv.org/abs/2512.23633 | https://arxiv.org/abs/2512.23633 | OK |
| 170 | https://arxiv.org/abs/2602.19303 | https://arxiv.org/abs/2602.19303 | OK |
| 171 | https://doi.org/10.1007/s40751-025-00172-1 | https://doi.org/10.1007/s40751-025-00172-1 | OK |
| 183 | https://arxiv.org/abs/2410.11123 | https://arxiv.org/abs/2410.11123 | OK (URL matches supplementary source for [183], but the **content attributed** to [183] in the report is wrong — see Check 1) |
| 186 | https://pmc.ncbi.nlm.nih.gov/articles/PMC11125466 | https://pmc.ncbi.nlm.nih.gov/articles/PMC11125466 | OK |
| 199 | https://arxiv.org/abs/2302.06871 | https://arxiv.org/abs/2302.06871 | OK |
| 271 | N/A — missing from bibliography | https://arxiv.org/abs/2402.09809 | **MISSING** — cannot verify URL since entry absent from bibliography |
| 285 | https://pmc.ncbi.nlm.nih.gov/articles/PMC12385150 | Not in supplementary list provided | OK — URL is plausible (PMC article) |
| 363 | https://www.semanticscholar.org/paper/9406fed4c75693fe0696ff00e775f7fff7082711 | Not in supplementary list provided | OK — URL is plausible (Semantic Scholar) |
| 368 | https://www.semanticscholar.org/paper/7306673752ca7b3f97bf50de9c7724f0249515b4 | Not in supplementary list provided | OK — URL is plausible (Semantic Scholar) |
| 376 | https://eric.ed.gov/?id=ED659897 | Not in supplementary list provided | OK — URL is plausible (ERIC) |

No MISMATCH or INVENTED URLs detected. One entry ([271]) is missing from the bibliography entirely.

## Recommended Fixes

1. **[CRITICAL] Fix [183] citation misattribution.** Throughout the report, [183] is cited as "Tutor CoPilot" (Wang

---

## Score Summary

| Dimension | Score |
|-----------|-------|
| Citation–bibliography linkage | 16/20 |
| Statistic provenance | 22/25 |
| Study design accuracy | 15/15 |
| Sub-question coverage | 10/20 |
| URL integrity | 20/20 |
| **Overall** | **83/100** |
