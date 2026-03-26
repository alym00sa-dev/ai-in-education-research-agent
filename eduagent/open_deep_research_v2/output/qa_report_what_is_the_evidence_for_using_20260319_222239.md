## Audit Summary
The report is **not fully trustworthy as written**. Its citation linkage is mostly coherent, but there are several substantive integrity problems: many inline citations refer to studies whose exact details are not supported by the source material, several statistics are only partially verifiable or lack exact provenance, and the report repeatedly overstates specificity beyond what the iteration history supports. The biggest issue is **statistical provenance**: the report includes exact percentages and comparative claims that are not fully traceable in the findings, plus some study-design labels are presented with more certainty than the source material warrants.

## Check 1 — Citation-Bibliography Linkage
No major linkage errors found in the final report bibliography: the inline citations used in the body are generally present in the Bibliography table, and the bibliography entries cited in the report largely match the corresponding PreScoredTiers entries for title and URL.

Issues found:
- **Potential orphan bibliography entries exist** insofar as the bibliography contains many sources not cited in the body; however, since the instruction defines orphans as entries with no inline citation in the report body, there are **many orphan entries**.
- Most notable orphan entries include: **[4], [5], [26], [30], [39], [49], [62], [63], [77], [84], [89], [95], [96], [97], [99], [100], [105], [107], [112], [118], [126], [127], [128], [137], [140], [141], [149], [150], [152], [163], [167], [168], [177], [178], [184]**.
- No inline citation number appears to be missing from the bibliography.

## Check 2 — Statistic Provenance
| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| 5.5 percentage point advantage on novel problems on subsequent topics | [19] | VERIFIED | Matches iteration history summary of LearnLM exploratory RCT. |
| 76.4% tutor approval of drafted messages with zero or minimal edits | [19] | VERIFIED | Explicitly present in iteration history. |
| “at least as well as those tutored by humans alone on measured outcomes” | [19] | VERIFIED | Supported in the findings summary. |
| “positive effects on proficiency and usage” | [25] | VERIFIED | Directional claim supported, though exact effect sizes were not retrieved. |
| “effects are exploratory and highly context-dependent” | [178] | VERIFIED | Matches meta-analysis framing in iteration history. |
| “positive average learning effects” | [141][177] | VERIFIED | Broadly consistent with meta-analytic summary, but not a precise numeric statistic. |
| “not all syntheses are specific to K-12 math or to generative AI interventions” | [141][177] | VERIFIED | Supported by source summaries. |
| “some benchmark studies show that LLMs can answer some elementary and high-school math questions” | [39][62][167] | VERIFIED | Supported qualitatively by benchmark summaries. |
| “performance drops on benchmark-variant formulations” | [30][39][62][167] | VERIFIED | Supported by robustness/variant benchmark summaries. |
| “Several evaluations show weaknesses when irrelevant information is added” | [30][39][62] | VERIFIED | Supported directly. |
| “some studies explicitly warn that unguided use can reduce learning or encourage overreliance” | [18][49][168] | VERIFIED | Supported by iteration history. |
| “strongest positive studies may reflect environments with better infrastructure or stronger implementation capacity” | [23][126][149][187] | UNVERIFIED | No explicit support in the iteration history. |
| “The report reports positive average effects across educational outcomes” | [141] | VERIFIED | Supported as a general meta-analytic claim. |
| “The strongest directly relevant studies are one exploratory RCT in UK secondary classrooms, one quasi-experimental middle-school hybrid tutoring investigation, and several benchmark/evaluation studies” | [19][25] | VERIFIED | Supported by iteration history. |
| “76.4% tutor approval...” (appears again in table) | [19] | VERIFIED | Repeated statistic. |
| “5.5 percentage point advantage...” (appears again in body and summary table) | [19] | VERIFIED | Repeated statistic. |

Unverified / fabricated statistics or quantitative claims:
- **No exact sample sizes** were provided for the RCT/QED outcomes in the final report, despite the report implying quantitative rigor.
- **“moderate positive effect on student math skills”** in the draft/iteration context is **UNVERIFIED** because no exact effect size or result was preserved in the findings.
- **“improved homework performance”** and **“no significant improvement on exam performance”** are not quantified in the iteration history and are therefore **UNVERIFIED as statistics-like claims** (even if directionally plausible).
- **“frequent chatbot use may be associated with lower exam performance”** is **UNVERIFIED** in the exact form presented in the draft; the iteration history mentions overreliance risk, not this precise association.
- Any **sample-size, p-value, confidence interval, or effect-size claims are absent** from the final report, so none are directly fabricated; rather, the report is **under-specified** compared with what a rigorous synthesis would require.

## Check 3 — Study Design Accuracy
Issues found:
- **[19]** labeled as **RCT** in the bibliography and body: **matches** source material.
- **[25]** labeled as **QED / Quasi-Experimental**: **matches** source material.
- **[84]** labeled as **RCT** in the bibliography, but the iteration history says it is **adult-based** and only indirectly informative for K-12. The design label itself is correct; the issue is **contextual relevance**, not design mislabeling.
- **[140]** labeled as **RCT** in the bibliography, and the iteration history supports RCT; again, the issue is that it is **adult-based**, not K-12.
- **[168]** labeled as **RCT** in the bibliography and iteration history: **matches**.
- The final report text itself sometimes refers to studies using broad phrases like “separate quasi-experimental investigation” or “exploratory RCT” without explicit grade/population caveats, which can **overstate K-12 directness**, but these are not design-label mismatches.

No clear cases were found where a study is described as an RCT or QED in the report but is not labeled as such in the source material.

## Check 4 — Sub-question Coverage
| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| Tier 1 | How are generative AI tools in K-12 math education defined in the literature, and what distinct functions do they serve? | Covered | [3][9][71][178] |
| Tier 1 | What math outcome constructs are most commonly studied and how are they operationalized? | Covered | [19][25][39][62][141][177] |
| Tier 1 | Which K-12 student populations and instructional contexts are most relevant? | Covered | [19][23][25][126][149] |
| Tier 2 | How are the same K-12 math skills developed without generative AI, and what counterfactual conditions represent standard practice? | Covered | [77][112][152][184] |
| Tier 2 | What baseline instructional approaches are commonly used when generative AI is not present? | Covered | [77][112][152][184] |
| Tier 2 | How do non-generative AI technologies serve as prior or alternative approaches? | Covered | [77][112][152] |
| Tier 3 | How are generative AI tools integrated into K-12 math instruction or practice, and what tasks do students perform? | Covered | [18][19][89][96][97][107][126][127] |
| Tier 3 | What pedagogical mechanisms are proposed? | Covered | [18][25][95][99][100][128] |
| Tier 3 | What implementation features and constraints are reported in K-12 settings? | Covered | [25][63][95][100][118][128][137][149][168] |
| Tier 4 | What is the comparative evidence that generative AI tools improve K-12 math achievement or related outcomes relative to standard instruction, tutoring, or non-AI digital supports? | Covered | [19][25][77][84][95][140][141][178] |
| Tier 4 | Do effects vary by grade level, student subgroup, topic area, dosage, or implementation model? | Covered | [23][25][30][96][118][126][137][149] |
| Tier 4 | What limitations or risks are identified in studies of generative AI for K-12 math? | Covered | [18][49][100][137][149][168][194] |
| Tier 4 | Where direct K-12 evidence is limited, what do adjacent studies suggest about likely benefits and boundary conditions? | Covered | [84][140][141][152][178] |

No tiered sub-question appears in the Research Questions table without supporting citations in the report body.

## Check 5 — URL Integrity
No URL mismatches or invented URLs were identified for bibliography entries cited in the report. The following URLs are present in the PreScoredTiers source list and match the bibliography entries:
- [19] `goo.gle/LearnLM-Nov25`
- [25] `https://doi.org/10.1145/3636555.3636896`
- [77] `http://arxiv.org/abs/2511.04997v1`
- [84] `https://doi.org/10.1371/journal.pone.0304013`
- [95] `https://doi.org/10.21203/rs.3.rs-5363154/v1`
- [112] `https://doi.org/10.1007/s40593-014-0023-y`
- [141] `https://doi.org/10.1057/s41599-025-04787-y`
- [152] `https://arxiv.org/abs/2503.09748`
- [168] `http://arxiv.org/abs/2503.10556v1`
- [178] `https://doi.org/10.1007/s40751-025-00172-1`
- [184] `not available`

## Recommended Fixes
1. **Add exact quantitative details only where they are actually present in source findings.** The report should either provide the exact effect sizes/sample sizes for [25] and related studies or explicitly say they were not retrievable.
2. **Remove or qualify unsupported pseudo-quantitative claims** such as “moderate positive effect,” “improved homework performance,” and “lower exam performance” unless traceable verbatim to iteration findings.
3. **Tighten K-12 relevance language** for [84] and [140]. They are RCTs, but adult-based and only indirectly informative for K-12; the report should state that explicitly.
4. **Reduce overclaiming in the implications section.** Phrases implying broad evidence of benefit should be softened to reflect that the evidence remains early, heterogeneous, and indirect.
5. **Use a more rigorous evidence table.** Each claim should distinguish between direct K-12 causal evidence, adjacent evidence, and conceptual/descriptive evidence.
6. **Audit the bibliography for orphan entries and trim or justify them.** If they are intentionally included as background sources, label them as such; otherwise remove unreferenced entries.
7. **Clarify which cited sources are benchmarks versus intervention studies.** Several benchmark studies are used to support learning claims, which can blur the distinction between capability and educational effectiveness.
8. **Add missing provenance for subgroup and equity claims.** Statements about multilingual learners, students with disabilities, and infrastructure-related effects need explicit support or should be marked as gaps/hypotheses rather than findings.