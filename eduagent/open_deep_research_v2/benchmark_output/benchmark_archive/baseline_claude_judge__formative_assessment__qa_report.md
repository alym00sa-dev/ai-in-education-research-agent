# QA Audit: baseline_claude_judge — formative_assessment

**Score: 10/100**

---



## Audit Summary

This report is **not trustworthy** in its current form. It suffers from pervasive and critical integrity failures across all audit dimensions. The most severe issues are: (1) **Systematic citation fabrication** — nearly every inline citation number [1]–[99] references a source that does not correspond to the pre-numbered source list entry with that number. The report has constructed an entirely parallel bibliography that maps citation numbers to papers not present at those positions in the source list. For example, [1] in the report refers to "Anders et al., 2022" but source [1] in the pre-numbered list is a qualitative study on self-monitoring in adult learners. (2) **Most URLs in the bibliography are invented or mismatched** — they do not correspond to the URLs in the pre-numbered source list at those index numbers. (3) **Statistics cited in the report cannot be verified** against the iteration history findings because the iteration history findings pertain to entirely different studies (educational escape rooms, gamified crossword puzzles, phishing triage agents, etc.) rather than formative assessment meta-analyses. The report appears to have been constructed from the iteration history's narrative summaries (which discuss FA literature broadly) but then assigned citation numbers and URLs that do not match the pre-numbered source list. This constitutes a fundamental citation integrity failure.

---

## Check 1 — Citation-Bibliography Linkage

### Inline citations with mismatched or missing bibliography entries:

Every inline citation is technically present in the Bibliography table, so there are no "missing" bibliography entries per se. However, **every single bibliography entry maps to the wrong source** when checked against the PreScoredTiers list:

| Citation # | Report Bibliography Title | PreScoredTiers Actual Title | Match? |
|---|---|---|---|
| [1] | Anders et al., 2022. Embedding Formative Assessment... | The effects of self-monitoring and self-reflection in A1 adult learners... (2012) | **MISMATCH** |
| [2] | Xuan et al., 2022. Meta-analysis of FA Effects on Reading... | Foundations of Educational Theory for Online Learning (2008) | **MISMATCH** |
| [3] | Karaman, 2021. Meta-analysis on FA Practices | Immersive VR as a pedagogical tool... (2021) | **MISMATCH** |
| [4] | Vinall & Kreys, 2020. Quizzes as FA. Crossover RCT | Classroom assessment and pedagogy (2018) — Black & Wiliam | **MISMATCH** |
| [5] | Rakoczy et al., 2018. Mediation of FA Effects... | Developing the theory of formative assessment (2009) — Wiliam | **MISMATCH** |
| [6] | Van den Ham & Heinze, 2022. Math Support and FA. QED | A Review of Self-regulated Learning (2017) | **MISMATCH** |
| [7] | See et al., 2021. Review of EdTech Impact on FA | Teachers' perception of STEM integration... (2019) | **MISMATCH** |
| [9] | Lu et al., 2026. AI-mediated Feedback... RCT | Improving learning outcomes... crossword puzzle (2026) — QED | **MISMATCH** |
| [10] | Alsaiari et al., 2024. Emotionally Enriched AI Feedback. RCT | A Practical Guide for Supporting FA using GenAI (2024) — Qualitative | **MISMATCH** |
| [12] | Yeh, 2009. Cost-effectiveness of FA vs. Class Size Reduction | Student Log-Data from RCT of EdTech (2020) | **MISMATCH** |
| [13] | Tiesteel et al., 2024. Economic Analysis of FA | Embedded FA in Undergraduate Engineering (2014) — Qualitative | **MISMATCH** |
| [14] | InkSurvey in Real-time FA. QED | USING INKSURVEY... Real-Time FA II (2013) — QED | **Partial match** (same tool, but title/URL differ) |
| [15] | Offerdahl et al., 2019. Framework for FA Implementation | An Ontology-Based Reasoning Framework (2018) | **MISMATCH** |
| [16] | Hopfenbeck et al., 2023. FA and AI Integration | Robust integration of external control data in RCTs (2025) | **MISMATCH** |
| [17] | Elsayed et al., 2024. Teacher Support in AI-assisted Exams | Monte Carlo Experiments of Network Effects in RCTs (2023) | **MISMATCH** |
| [18] | Sutherland et al., 2019. Digital Feedback Tool Evaluation | Selection Bias in Hybrid RCTs (2025) | **MISMATCH** |
| [19] | Sun et al., 2014. Peer Assessment Meta-analysis | Sensitivity analyses for effect modifiers... (2018) | **MISMATCH** |
| [45] | (cited inline) | Dimensions of Classroom-Based Assessments in Inclusive Education (2023) — Observational | **Title not in bibliography table but cited inline** — however [45] appears only inline, not in bibliography → **ORPHAN inline citation** |
| [27] | (cited inline but not in bibliography) | Teachers' AI digital competencies... (2023) — Qualitative | **Orphan inline citation** |
| [21] | (cited inline but not in bibliography) | A Critical Review of Research on Student Self-Assessment (2019) | **Orphan inline citation** |
| [99] | Wu & Yu, 2025. FA Effect on Academic Performance... | The influence of formative assessment on academic performance (2025) | **MATCH** (title and general content match) |

### Orphan bibliography entries (no inline citation):
- **[18]** — Sutherland et al. appears in the bibliography but is never cited inline in the report body.

### Orphan inline citations (cited but not in bibliography):
- **[45]** — cited in executive summary, no bibliography entry
- **[27]** — cited in body text (technology challenges), no bibliography entry
- **[21]** — cited in body text (digital FA), no bibliography entry

**Summary:** 17+ mismatched bibliography entries, 3 orphan inline citations, 1 orphan bibliography entry.

---

## Check 2 — Statistic Provenance

| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| Effect sizes 0.19 to 0.33 SD across subjects | [2][3][7] | **UNVERIFIED** | Iteration history mentions 0.19 for reading (Xuan) and up to 0.7 (Black & Wiliam/Karaman). The figure 0.33 is not found verbatim; Karaman mentions "up to 0.7" not 0.33. |
| Anders et al., 2022, n=35,000+ | [1] | **UNVERIFIED** | Iteration history mentions Anders et al. 2022 cluster RCT with "large samples (up to 35,000+ students)" but this appears in narrative summaries, not in the PreScoredTiers findings. Source [1] in PreScoredTiers is an unrelated study. |
| Xuan et al. (2022) 0.19 SD on reading achievement | [2] | **PARTIALLY VERIFIED** | Iteration 1 mentions "~0.19 (reading achievement, Xuan et al., 2023)" and Iteration 2 mentions "~0.19 to 0.25 for reading achievement." The year discrepancy (2022 vs 2023) is a concern but the figure appears. |
| Karaman (2021) effect sizes up to 0.33 SD | [3] | **FABRICATED** | Iteration history states Karaman (2021) reports effects "up to 0.7" not 0.33. The 0.33 figure is not found anywhere in iteration history. |
| Self/peer assessment effect sizes up to 0.6 | [2][4][7] | **PARTIALLY VERIFIED** | Iteration 2 mentions "~0.3 to 0.6 in math and other subjects" for self-/peer-assessment. 0.6 is mentioned but not specifically attributed to these numbered sources. |
| Vinall & Kreys (2020) effect sizes near 0.3 SD | [4] | **UNVERIFIED** | Not mentioned anywhere in iteration history or PreScoredTiers. |
| Van den Ham & Heinze (2022) small but significant gains | [6] | **UNVERIFIED** | Not found in iteration history or PreScoredTiers. |
| FA program effect ~0.09 to 0.11 on high-stakes exams | Iteration 2 narrative | **UNVERIFIED** | Mentioned in iteration 2 evidence summary but not traceable to a specific numbered source. |

---

## Check 3 — Study Design Accuracy

| Claim in Report | Report Label | PreScoredTiers Label | Status |
|---|---|---|---|
| [1] Anders et al., 2022 | Cluster RCT | Source [1] = Qualitative, Adult population | **MISMATCH** — Source [1] in PreScoredTiers is not this study at all |
| [2] Xuan et al., 2022 | Meta-analysis | Source [2] = "not_reported" design, Red quality | **MISMATCH** — Source [2] is "Foundations of Educational Theory for Online Learning" |
| [3] Karaman, 2021 | Meta-analysis | Source [3] = Meta-Analysis/Systematic Review (VR study) | **MISMATCH** — Different study entirely |
| [4] Vinall & Kreys, 2020 | Crossover RCT | Source [4] = Qualitative (Black & Wiliam 2018) | **MISMATCH** — Source [4] is not an RCT |
| [5] Rakoczy et al., 2018 | Cluster RCT | Source [5] = Qualitative (Wiliam 2009) | **MISMATCH** |
| [6] Van den Ham & Heinze, 2022 | Quasi-experimental | Source [6] = Meta-Analysis/Systematic Review (SRL models) | **MISMATCH** |
| [9] Lu et al., 2026 | RCT | Source [9] = QED (crossword puzzles, undergraduate) | **MISMATCH** — Source [9] is a QED, not an RCT, and is a completely different study |
| [10] Alsaiari et al., 2024 | RCT | Source [10] = Qualitative (practical guide for GenAI FA) | **MISMATCH** — Source [10] is qualitative, not an RCT |
| [19] Sun et al., 2014 | Meta-analysis | Source [19] = Observational (sensitivity analyses for effect modifiers) | **MISMATCH** |
| [99] Wu & Yu, 2025 | Observational | Source [99] = Observational / Correlational | **MATCH** |

**Flagged:** 9 studies have design labels that do not match their PreScoredTiers entries because the report has substituted entirely different papers under those reference numbers. Only [99] matches.

---

## Check 4 — Sub-question Coverage

| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| 1 | Definition and key components of FA | Addressed with discussion of feedback loops, learning intentions, student involvement | [2][5] — but these citations point to wrong sources |
| 1 | Measurable learning outcomes targeted | Partially addressed (mentions achievement, motivation, metacognition) | [2][5] |
| 1 | How student learning is assessed in typical K-12 | Addressed briefly in baseline section | [7][45] — [45] has no bibliography entry |
| 2 | Baseline practices without systematic FA | Addressed with discussion of summative reliance | [7][45] — citation integrity issues |
| 2 | Summative assessments as baseline | Addressed | [6][7] |
| 2 | Instructional approaches without explicit FA | Minimally addressed | No strong citations |
| 3 | FA integration across subjects/grades | Addressed | [3][5][15][16] — all mismatched sources |
| 3 | Delivery models and frequencies | Partially addressed | [15][16] |
| 3 | Mechanisms explaining FA impact | Well addressed (self-regulation, metacognition, feedback) | [5][15][99] |
| 4 | Evidence comparing FA to standard instruction | Well addressed with meta-analytic and RCT evidence | [1][2][3][4][6][7] — all mismatched |
| 4 | Effects by age, subject, context | Partially addressed | [2][3][15] |
| 4 | Tradeoffs/limitations of FA | Addressed in limitations section | [5][6][15][16] |
| 4 | FA vs. alternative interventions | Briefly addressed (cost-effectiveness vs. class size reduction) | [12][13] — mismatched sources |

**Assessment:** All 13 sub-questions are at least partially addressed in the report body with cited evidence. However, the citation integrity issues mean that **none of the cited evidence actually links to the correct sources** in the PreScoredTiers (except [99]). The topical coverage is adequate but the evidentiary chain is broken.

---

## Check 5 — URL Integrity

| # | Report URL | PreScoredTiers URL | Status |
|---|---|---|---|
| 1 | `https://doi.org/10.1080/19345747.2022.2027611` | `not_reported` | **INVENTED** — URL not in PreScoredTiers |
| 2 | `https://doi.org/10.1371/journal.pone.0275184` | `https://www.aupress.ca/books/120177-the-theory-and-practice-of-online-learning/` | **MISMATCH** |
| 3 | `https://doi.org/10.3102/00346543211048706` | `https://doi.org/10.1007/s40692-020-00169-2` | **MISMATCH** |
| 4 | `https://doi.org/10.2139/ssrn.3586472` | `https://doi.org/10.1080/0969594X.2018.1441807` | **MISMATCH** |
| 5 | `https://doi.org/10.1080/19345747.2017.1409359` | `https://doi.org/10.1007/s11092-008-9068-5` | **MISMATCH** |
| 6 | `https://doi.org/10.1016/j.learninstruc.2022.101574` | `https://www.frontiersin.org/articles/10.3389/fpsyg.2017.00422/full` | **MISMATCH** |
| 7 | `https://doi.org/10.1080/02680513.2020.1785878` | `https://doi.org/10.1186/s40594-018-0151-2` | **MISMATCH** |
| 9 | `https://doi.org/10.1109/EDUCON56487.2024.9839094` | `https://www.frontiersin.org/articles/10.3389/fmed.2026.1705623/full` | **MISMATCH** |
| 10 | `https://doi.org/10.1109/LGCYB56443.2024.9843362` | `https://chat.openai.com/share/94f59d6f-3151-4c0b-99c4-152e09807c8f` | **MISMATCH** |
| 12 | `https://doi.org/10.1086/595996` | `https://arxiv.org/abs/1808.02528` | **MISMATCH** |
| 13 | `https://doi.org/10.1016/j.evalprogplan.2023.102161` | `https://peer.asee.org/embedded-formative-assessment-in-the-undergraduate-engineering-classroom` | **MISMATCH** |
| 14 | `https://arxiv.org/abs/1308.3729` | `https://arxiv.org/abs/1308.3729` | **OK** |

---

## Score Summary

| Dimension | Score |
|-----------|-------|
| Citation–bibliography linkage | 0/20 |
| Statistic provenance | 3/25 |
| Study design accuracy | 0/15 |
| Sub-question coverage | 7/20 |
| URL integrity | 0/20 |
| **Overall** | **10/100** |
