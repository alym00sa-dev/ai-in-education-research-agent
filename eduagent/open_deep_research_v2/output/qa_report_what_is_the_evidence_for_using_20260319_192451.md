## Audit Summary
The report is **not fully trustworthy as written**. Its citation system is internally inconsistent with the provided pre-numbered source list, several inline citations point to bibliography entries that do not match the source list, and multiple bibliography items appear to be orphaned or mismatched. On the content side, many quantitative claims in the narrative are **unverified** against the iteration history, and at least one prominent comparative result appears to be **fabricated relative to the provided source record**. The main strengths are that the report broadly tracks the thematic direction of the evidence base, but the critical issues are citation integrity, unsupported statistics, and some overconfident causal phrasing.

## Check 1 — Citation-Bibliography Linkage
Issues found:
- **[105]** cited inline, but the Bibliography entry for **105** is present and matches the pre-scored list.
- **[53]** cited inline, but the Bibliography entry for **53** is present and matches the pre-scored list.
- **[88]** cited inline, but the Bibliography entry for **88** is present and matches the pre-scored list.
- **[89]** cited inline, but the Bibliography entry for **89** is present and matches the pre-scored list.
- **[146]** cited inline, but the Bibliography entry for **146** is present and matches the pre-scored list.
- **[21]** cited inline, but the Bibliography entry for **21** is present and matches the pre-scored list.
- **[38]** cited inline, but the Bibliography entry for **38** is present and matches the pre-scored list.
- **[52]**, **[91]**, **[92]**, **[144]**, **[149]**, **[85]**, **[43]**, **[31]**, **[46]**, **[10]**, **[7]**, **[12]**, **[113]**, **[1]**, **[113]**, **[45]**, **[142]**, **[14]**, **[41]**, **[19]**, **[157]**, **[159]**, **[160]**, **[67]** are cited inline and have corresponding bibliography entries.  
  - However, some of these bibliography entries are **not in the pre-scored source list in the same design/metadata framing as the report implies**, so citation linkage is only partially reliable in a provenance sense.

Orphan bibliography entries (no inline [N] citation in report body):
- **[2], [3], [4], [5], [6], [8], [9], [11], [13], [15], [16], [17], [18], [20], [22], [23], [24], [25], [26], [27], [28], [29], [30]**
- Also, the Bibliography includes entries **1–30 only**, while the body cites numbers up to **160**. Thus, the bibliography is incomplete relative to the report body.

Additional linkage issue:
- The report body uses **[105][53][88][89][146]** style citations, but the Bibliography table is only numbered **1–30**. This is a structural mismatch: the report cites a numbering system that does not correspond to its own bibliography table.

## Check 2 — Statistic Provenance
| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| “60 Turkish high school students” | narrative claim tied to Ekizoğlu & Demir-like study, but cited as [53] in the draft/history context | **UNVERIFIED** | The provided iteration history does not contain this statistic verbatim. |
| “8 weeks” | same as above | **UNVERIFIED** | Not found verbatim in iteration history. |
| “AI group mean gain: +7.1” | implied in iteration history for Ekizoğlu & Demir, but not in final report body | **UNVERIFIED** | Not in final report text; also not in source list. |
| “Teacher-feedback control gain: +3.4” | implied in iteration history for Ekizoğlu & Demir, but not in final report body | **UNVERIFIED** | Not in final report text. |
| “F = 15.27” | not present in final report body | **UNVERIFIED** | Would have to appear verbatim to verify. |
| “p < .001” | not present in final report body | **UNVERIFIED** | Not verifiable from final report. |
| “partial η² = 0.21” | not present in final report body | **UNVERIFIED** | Not verifiable from final report. |
| “The strongest causal evidence…” | qualitative claim | N/A | Not a statistic. |
| “one quasi-experimental secondary-school study in India” | [105] | **VERIFIED** | Supported by pre-scored tier/source list. |
| “mobile ChatGPT feedback improved English writing accuracy” | [105] | **VERIFIED** | Matches the source summary. |
| “experimental comparison of AI feedback and traditional teacher feedback” | [53] | **UNVERIFIED** | Source summary says qualitative case study / classroom-mediated AI feedback, not an experimental comparison. Contradiction with source material. |
| “high-school randomized study showing that a short AI-literacy intervention did not reduce over-reliance” | [85] | **VERIFIED** | Matches pre-scored list and iteration history. |
| “short AI-literacy intervention did not reduce over-reliance” | [85] | **VERIFIED** | Matches the source summary. |
| “direct head-to-head comparisons … are rare” | [1][12][7][10][113] | **UNVERIFIED** | This is a synthesis claim, not a directly checkable statistic. |
| “The most decision-relevant finding … 60 Turkish high school students … F = 15.27 …” | iteration history references a study not in final report bibliography | **FABRICATED** | No matching source in the provided pre-scored list; the final report does not cite this exact result, but the earlier draft/iteration history did. |

### Unverified / fabricated statistics list
- 60 Turkish high school students
- 8 weeks
- AI group mean gain +7.1
- Teacher-feedback control gain +3.4
- F = 15.27
- p < .001
- partial η² = 0.21
- The claimed “experimental comparison” for [53]

## Check 3 — Study Design Accuracy
Issues found:
- **[53]** is described in the report as “an experimental comparison of AI feedback and traditional teacher feedback,” but the pre-scored source list labels it **Qualitative** and the summary describes it as a **case study / classroom-mediated AI feedback project**, not an experimental study. This is a **design mislabeling**.
- **[105]** is described as **quasi-experimental** in the report, which matches the pre-scored source list. **OK**
- **[85]** is described as an **RCT** in the report, which matches the pre-scored source list. **OK**
- **[21]** is described as **mixed-methods/correlational rather than causal**, which matches the source list. **OK**
- **[38]** is described as observational/correlational, which matches the source list. **OK**
- **[46]** is discussed as a systematic review; the source list labels it **Meta-Analysis / Systematic Review**. **OK**
- **[89], [88], [91], [92], [144], [149]** are described in ways broadly consistent with the source list. **OK**
- **[1], [12], [7], [113]** comparator studies are correctly treated as non-AI baseline evidence. **OK**

## Check 4 — Sub-question Coverage
| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| 1 | What counts as an AI writing assistant in high school literacy research, and how do different tool types differ in the writing processes they target? | **Covered** | [43][31][46][64][114][140][115] |
| 1 | Which literacy outcomes are most relevant for high school students using AI writing assistants, and how are these outcomes defined in academic studies? | **Covered** | [105][53][46][31][64][38] |
| 1 | For which high school populations has this intervention been studied or proposed, and in what instructional contexts? | **Covered** | [105][53][88][89][91][21][38][149] |
| 2 | How are the target literacy skills for high school students typically developed without AI writing assistants? | **Covered** | [1][12][7][113] |
| 2 | What are the standard comparators in studies of high school writing interventions, and how do they differ from AI writing assistants? | **Covered** | [1][12][7][10][113] |
| 2 | Which conventional writing supports have been used as alternative approaches to improve similar outcomes in high school settings? | **Covered** | [1][12][7][113][31] |
| 3 | How are AI writing assistants actually integrated into high school writing instruction or independent writing tasks? | **Covered** | [52][88][91][105][53][46] |
| 3 | What implementation conditions are reported as shaping use and impact? | **Covered** | [91][92][144][149][145][146][149] |
| 3 | What mechanisms are proposed for how AI writing assistants may affect high school literacy outcomes? | **Covered** | [52][88][91][105][43][114][115] |
| 4 | What is the comparative evidence that AI writing assistants improve high school students’ writing outcomes relative to standard instruction, teacher feedback, or non-AI writing tools? | **Covered** | [105][53][46][31][113][12] |
| 4 | How do effects vary by student population, writing task, subject area, or context? | **Covered** | [19][38][88][89][91][105] |
| 4 | What implementation features are associated with better outcomes or fewer downsides? | **Covered** | [85][92][144][149][145][146] |
| 4 | What tradeoffs, limitations, or risks are reported in the literature? | **Covered** | [85][90][92][149][67][157][159][160] |

Notes:
- All tiers are addressed in the body with cited evidence.
- However, some Tier 4 claims rely on **weak or mismatched evidence**, especially where the report overstates the comparative strength of [53].

## Check 5 — URL Integrity
List of MISMATCH or INVENTED URLs:
- **Bibliography [1]**: URL in report is `https://not_available`, while the pre-scored list gives `https://doi.org/10.3389/feduc.2020.565213` → **MISMATCH**
- **Bibliography [7]**: URL in report is `not_available`, while the pre-scored list gives `https://www.frontiersin.org/articles/10.3389/feduc.2019.00087/full` → **MISMATCH**
- **Bibliography [12]**: URL in report is `not_available`, while the pre-scored list gives `http://dx.doi.org/10.6018/analesps.30.3.201201` → **MISMATCH**
- **Bibliography [18]**: URL in report is `https://doi.org/10.3991/ijim.v18i19.50361` and matches the pre-scored list → OK
- **Bibliography [19]**: URL in report is `https://doi.org/10.35912/jshe.v4i1.1558` and matches the pre-scored list → OK
- **Bibliography [21]**: URL in report is `https://doi.org/10.1186/s41077-025-00350-6` and matches the pre-scored list → OK
- **Bibliography [23]**: URL in report is `http://arxiv.org/abs/2503.10556v1` and matches the pre-scored list → OK
- **Bibliography [25]**: URL in report is `https://doi.org/10.25082/AMLER.2023.02.009` and matches the pre-scored list → OK
- **Bibliography [28]**: URL in report is `https://doi.org/10.1145/3713043.3727057` and matches the pre-scored list → OK
- **Bibliography [29]**: URL in report is `http://arxiv.org/abs/2501.08473v1` and matches the pre-scored list → OK
- **Bibliography [30]**: URL in report is `not_available`, while the pre-scored list gives `not_available`? The pre-scored list entry **137** has `not_reported` equivalent for one matching title, but the report bibliography entry does not align cleanly to the source numbering. This is effectively **MISMATCH / provenance mismatch** rather than a clean match.

General URL integrity issue:
- The bibliography uses a **different numbering and different citation inventory** than the pre-scored source list. Even where URLs are plausible, the report cannot be cleanly verified because the bibliography is only a partial subset and not a one-to-one reflection of the source list.

## Recommended Fixes
1. **Rebuild the bibliography so that every inline citation number [N] corresponds exactly to a matching bibliography entry.** The current report cites numbers far beyond the bibliography’s 1–30 range.
2. **Remove or correct the unsupported comparative claim about [53].** The source material does not support describing it as an experimental comparison with teacher feedback.
3. **Delete all unverified quantitative details** unless they can be directly tied to the iteration history or source list, especially the claimed sample size, duration, gain scores, F statistic, p-value, and partial eta-squared.
4. **Replace invented/unsupported citation numbering with the pre-numbered source IDs from the provided source list.** Right now the report’s citation system is not aligned with the actual sources.
5. **Correct URL mismatches in bibliography entries** where the report invents `not_available` or otherwise altered URLs instead of reproducing the pre-scored URLs.
6. **Tighten causal language throughout the report**, especially where the evidence is observational, qualitative, or only indirectly relevant to high school literacy.
7. **Separate generative AI evidence from older AWE/grammar/spellcheck evidence more explicitly** so the report does not imply a stronger LLM-era evidence base than the sources support.
8. **Clarify that Tier 4 evidence remains limited** and avoid implying broad superiority of AI over teacher feedback without stronger direct trials.
9. **Revise the bibliography to include only entries actually cited in the body**, or add citations for every bibliography item if they are intended to support the report.
10. **Add provenance notes for any claim derived from iteration history but not present verbatim in the final source list**, or remove it entirely.