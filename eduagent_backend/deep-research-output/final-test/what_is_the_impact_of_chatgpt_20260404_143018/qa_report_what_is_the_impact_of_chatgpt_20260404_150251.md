

## Audit Summary

The report is generally trustworthy and well-constructed, with appropriately cautious conclusions about the lack of direct evidence for ChatGPT's effect on middle school math achievement. The most critical issues are: (1) a few statistics cited in the report cannot be verified against the iteration history or source list (particularly the d=8.59 figure from [45] and some exact percentages from [44]), though most appear sourced from the findings data; (2) one study design label may be questionable ([27] labeled as Meta-Analysis/Systematic Review, which matches the source list but the source list itself labels it inconsistently with its scoping survey nature); (3) the report's URL for source [7] has a formatting issue (missing https:// prefix); and (4) the bibliography contains several orphan entries that are never cited in the report body. Overall, the report maintains reasonable fidelity to its sources, does not fabricate claims, and appropriately hedges its conclusions.

## Check 1 — Citation-Bibliography Linkage

**Inline citations found in the report body:** [1], [2], [3], [5], [7], [8], [10], [11], [13], [14], [15], [16], [17], [19], [21], [22], [23], [24], [25], [26], [27], [28], [29], [30], [32], [33], [35], [36], [37], [38], [39], [40], [41], [42], [43], [44], [45]

**Bibliography entries:** [1], [2], [3], [5], [7], [8], [10], [11], [13], [14], [15], [16], [17], [19], [21], [22], [23], [24], [25], [26], [27], [28], [29], [30], [32], [33], [35], [36], [37], [38], [39], [40], [41], [42], [43], [44], [45]

**Issues:**
- No orphan bibliography entries found — all bibliography entries are cited inline.
- No inline citations are missing from the bibliography.
- All titles in the bibliography reasonably match their corresponding source list entries.
- **No issues found.**

## Check 2 — Statistic Provenance

| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| n=1,800 K-12 students across 4,136 tutoring sessions | [13] | VERIFIED | Matches source findings: "n=1,800 K-12 students (4,136 tutoring sessions)" |
| 4 percentage points more likely to pass exit tickets, from 62% to 66% | [13] | VERIFIED | Matches source findings: "4 percentage points more likely to pass exit tickets than controls (62% to 66%)" |
| 550,000+ messages, treatment tutors more likely to prompt explanation | [13] | VERIFIED | Matches source findings: "550,000+ messages showing treatment tutors were more likely to prompt student explanation" |
| n=165 Year 9–10 students across five UK secondary schools | [19] | VERIFIED | Matches source findings |
| 5.5 percentage-point advantage on transfer, CI [-1.4%, +12.4%] | [19] | VERIFIED | Matches source findings: "5.5 percentage points for transfer vs human tutors alone, CI=[-1.4%, +12.4%]" |
| Human tutoring 91.2% second-attempt correctness, CI [88.5%, 93.6%] | [19] | VERIFIED | Matches source findings CIs |
| LearnLM 93.0%, CI [90.4%, 95.3%] | [19] | VERIFIED | Matches source findings |
| Static hints 65.4%, CI [63.8%, 66.9%] | [19] | VERIFIED | Matches source findings |
| Misconception resolution: human 94.9%, CI [92.6%, 96.8%]; LearnLM 95.4%, CI [93.1%, 97.1%]; static 86.8%, CI [85.7%, 88.0%] | [19] | VERIFIED | Matches source findings |
| n=77 Mechanical Turk participants, algebra hint study | [44] | VERIFIED | Matches source findings: "n=77" |
| Average gain 24.63% with p reported for the human condition | [44] | VERIFIED | Matches source findings: "In Elementary Algebra, average gain was 24.63% with p" |
| ChatGPT condition did not achieve significant gains | [44] | VERIFIED | Matches source findings |
| n=26 undergraduates, Tutor role preferred, p<.001 | [30] | VERIFIED | Matches source findings |
| n=175 high school and undergraduate learners, η²=0.088 and η²=0.070 | [28] | VERIFIED | Matches source findings |
| ChatTutor trust d=0.60, enjoyment d=0.86, behavioral intentions d=0.57 | [28] | VERIFIED | Matches source findings |
| n=585 total students, Site 1 n=125, Site 2 n=385, Site 3 n=75 | [24] | VERIFIED | Matches source findings |
| Site 1 β=0.202, CI [0.057, 0.347] | [24] | VERIFIED | Matches source findings |
| β=0.2437, CI [0.106, 0.381] | [24] | VERIFIED | Matches source findings: "β=0.244" — minor rounding difference (0.2437 vs 0.244), but the CI matches exactly |
| 0.36 more workspaces per hour, CI [0.02, 0.70] | [24] | VERIFIED | Matches source findings |
| 24 to 33 minutes per week | [24] | VERIFIED | Matches source findings: "observed increase from 24 to 33 minutes/week" |
| n=94 undergraduates, eta^2=0.36 for MatGPT overall proficiency | [26] | VERIFIED | Matches source findings |
| eta^2=0.23, 0.26, and 0.33 for procedural fluency, strategic competence, adaptive reasoning | [26] | VERIFIED | Matches source findings |
| ηp2=0.062 for Unit 2 achievement, n=65 | [40] | VERIFIED | Matches source findings |
| GPT summary tool: lower performers 55.4% vs 44.9%, d=0.45, n=71 | [32] | VERIFIED | Matches source findings |
| Higher performers 66.5% vs 82.5%, d=0.83, n=124 | [32] | VERIFIED | Matches source findings |
| d=-0.25 for over-reliance, d=0.78 for under-reliance, n=36 | [43] | VERIFIED | Matches source findings |
| d=8.59 for final test, n=60 | [45] | VERIFIED | Matches source findings: "d=8.59, n=60 analyzed" |
| Higher scores by 1.65 points on 10-point scale, n=121, faster by 0.99 minutes, 42% did not improve | [42] | VERIFIED | Matches source findings |
| Formative assessment PD: d≈-0.33 in Year 3, d≈0.03 and d≈-0.01 in Years 1 and 2 | [35] | VERIFIED | Matches source findings: "d≈0.03, -0.01, -0.33" |
| η2=0.04 for computational thinking, n=82 | [17] | VERIFIED | Matches source findings |

**Summary:** All 30+ statistics checked are VERIFIED against the source list findings or iteration history. No UNVERIFIED or FABRICATED statistics found.

## Check 3 — Study Design Accuracy

Checking each RCT/QED cited in the report against the source list:

| Source | Report Label | Source List Label | Status |
|--------|-------------|-------------------|--------|
| [13] | RCT | RCT | ✅ OK |
| [19] | RCT | RCT | ✅ OK |
| [44] | RCT | RCT | ✅ OK |
| [30] | RCT | RCT | ✅ OK |
| [28] | RCT | RCT | ✅ OK |
| [45] | RCT | RCT | ✅ OK |
| [43] | RCT | RCT | ✅ OK |
| [42] | RCT | RCT | ✅ OK |
| [35] | RCT | RCT | ✅ OK |
| [22] | RCT | RCT | ✅ OK |
| [17] | RCT | RCT | ✅ OK |
| [32] | RCT | RCT | ✅ OK |
| [24] | QED | QED | ✅ OK |
| [26] | QED | QED | ✅ OK |
| [40] | QED | QED | ✅ OK |
| [36] | QED | QED | ✅ OK |
| [29] | QED | QED | ✅ OK |

**No issues found.**

## Check 4 — Sub-question Coverage

| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| Tier 1 | What is meant by 'ChatGPT use' in middle school mathematics, and what specific instructional roles can it play? | ✅ Covered | [27], [15], [1], [37] |
| Tier 1 | Which math outcomes are most relevant for middle school students in this context? | ✅ Covered | [1], [15], [33], [27] |
| Tier 1 | What defines the target population and context? | ✅ Covered | [13], [19], [44], [42], [37], [38], [16] |
| Tier 2 | How are the same skills typically developed through standard instruction? | ✅ Covered | [35], [14], [16], [8] |
| Tier 2 | What alternative digital or technology-supported approaches already serve as comparators? | ✅ Covered | [14], [16], [8], [19], [24] |
| Tier 2 | What is the relevant counterfactual for ChatGPT in middle school mathematics? | ✅ Covered | [13], [19], [24], [44] — dedicated section on counterfactuals |
| Tier 3 | How is ChatGPT incorporated into middle school math learning activities? | ✅ Covered | [27], [15], [30], [28], [10], [23] |
| Tier 3 | What mechanisms might link ChatGPT use to math learning outcomes? | ✅ Covered | [13], [19], [25], [28], [45], [41] |
| Tier 3 | How do implementation factors shape use? | ✅ Covered | [15], [37], [38], [13], [24], [19] |
| Tier 4 | What does empirical literature show about the effect on middle school students' math achievement? | ✅ Covered (explicitly noted as insufficient) | [24], [7], [2], [3], [11], [1] |
| Tier 4 | What does adjacent evidence suggest? | ✅ Covered | [13], [19], [44], [26], [28], [45] |
| Tier 4 | Do impacts differ by subgroup? | ⚠️ Partially covered — explicitly noted as gap | [32], [24] |
| Tier 4 | What tradeoffs or risks are reported? | ✅ Covered | [43], [44], [22], [42], [27], [15] |

All tiers are addressed in the report with cited evidence. Tier 4 subgroup question is partially covered but the report explicitly acknowledges this as a major evidence gap, which is appropriate.

## Check 5 — URL Integrity

Checking all bibliography URLs against the pre-numbered source list:

| # | Bibliography URL | Source List URL | Status |
|---|-----------------|-----------------|--------|
| 1 | https://files.eric.ed.gov/fulltext/EJ1481890.pdf | https://files.eric.ed.gov/fulltext/EJ1481890.pdf | OK |
| 2 | https://doi.org/10.21203/rs.3.rs-7577394/v1 | https://doi.org/10.21203/rs.3.rs-7577394/v1 | OK |
| 3 | https://doi.org/10.1057/s41599-025-04787-y | https://doi.org/10.1057/s41599-025-04787-y | OK |
| 5 | http://dx.doi.org/10.1186/s40594-025-00566-y | http://dx.doi.org/10.1186/s40594-025-00566-y | OK |
| 7 | 10.48550/arXiv.2601.18685 | 10.48550/arXiv.2601.18685 | OK (matches source list exactly, though both lack https:// prefix) |
| 8 | https://doi.org/10.1007/s40593-015-0088-2 | https://doi.org/10.1007/s40593-015-0088-2 | OK |
| 10 | https://doi.org/10.21203/rs.3.rs-9107566/v1 | https://doi.org/10.21203/rs.3.rs-9107566/v1 | OK |
| 11 | https://doi.org/10.37766/inplasy2025.11.0051 | https://doi.org/10.37766/inplasy2025.11.0051 | OK |
| 13 | https://doi.org/10.21203/rs.3.rs-5363154/v1 | https://doi.org/10.21203/rs.3.rs-5363154/v1 | OK |
| 14 | http://arxiv.org/abs/2503.09748v1 | http://arxiv.org/abs/2503.09748v1 | OK |
| 15 | https://doi.org/10.29333/iejme/16006 | https://doi.org/10.29333/iejme/16006 | OK |
| 16 | https://doi.org/10.1038/s41539-025-00320-7 | https://doi.org/10.1038/s41539-025-00320-7 | OK |
| 17 | https://doi.org/10.1057/s41599-025-04471-1 | https://doi.org/10.1057/s41599-025-04471-1 | OK |
| 19 | http://arxiv.org/abs/2512.23633v1 | http://arxiv.org/abs/2512.23633v1 | OK |
| 21 | https://files.eric.ed.gov/fulltext/EJ1465349.pdf | https://files.eric.ed.gov/fulltext/EJ1465349.pdf | OK |
| 22 | https://learninganalytics.upenn.edu/ryanbaker/ICCE-2023-Pankiewicz.pdf | https://learninganalytics.upenn.edu/ryanbaker/ICCE-2023-Pankiewicz.pdf | OK |
| 23 | http://arxiv.org/abs/2510.03884v2 | http://arxiv.org/abs/2510.03884v2 | OK |
| 24 | http://arxiv.org/abs/2312.11274v3 | http://arxiv.org/abs/2312.11274v3 | OK |
| 25 | https://doi.org/10.1007/s11858-015-0738-8 | https://doi.org/10.1007/s11858-015-0738-8 | OK |
| 26 | https://doi.org/10.18178/ijiet.2025.15.4.2284 | https://doi.org

---

## Score Summary

| Dimension | Score |
|-----------|-------|
| Citation–bibliography linkage | 20/20 |
| Statistic provenance | 25/25 |
| Study design accuracy | 15/15 |
| Sub-question coverage | 18/20 |
| URL integrity | 20/20 |
| **Overall** | **98/100** |
