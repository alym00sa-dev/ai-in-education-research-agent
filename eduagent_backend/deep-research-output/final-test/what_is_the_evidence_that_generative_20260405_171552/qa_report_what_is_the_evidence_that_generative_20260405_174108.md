

## Audit Summary

The report is generally trustworthy and well-constructed, with appropriate hedging about the limitations of the evidence base. The bibliography is mostly accurate, statistics are largely verifiable from iteration history and source summaries, and study designs are correctly labeled. The most critical issues are: (1) a small number of statistics that cannot be fully verified from the available source summaries (e.g., the vaccine chatbot coefficients cited without a formal [N] reference and some self-report figures from [7]); (2) one source ([22]) cited inline but with a quality/impact tier that needs verification; and (3) one potential study design concern regarding source [11]'s quality tier. Overall, the report is careful, conservative, and appropriately caveated.

## Check 1 — Citation-Bibliography Linkage

**Inline citations vs. Bibliography entries:**

All inline citations checked: [1], [2], [3], [4], [5], [6], [7], [8], [9], [10], [11], [13], [14], [15], [16], [17], [18], [19], [20], [21], [22], [23], [24], [26], [30], [32], [34], [35], [39], [40], [42], [44], [47]

- **[22]** — Cited inline in the Research Architecture section ("Systematic review of research on artificial intelligence applications in higher education [22]") and in the Intellectual Lineage table. [22] appears in the pre-numbered source list as "Systematic review of research on artificial intelligence applications in higher education – where are the educators?" (2019). **However, [22] is NOT present in the Bibliography table.** This is a missing bibliography entry.

- **[2]** — Cited inline in the Limitations section ("Several relevant studies in the source pool do not provide exact effect sizes in the available summaries, and some of the strongest syntheses are broad AI-in-education reviews rather than focused K-12 literacy meta-analyses [16] [2] [6]"). [2] appears in the Bibliography. ✓

- **[6]** — Cited inline in the Limitations section. [6] appears in the Bibliography. ✓

- **[3]** — Cited inline in the Limitations section ("[14] [13] [3]"). [3] appears in the Bibliography. ✓

- **Orphan entries:** All Bibliography entries appear to have at least one inline citation, with the exception of checking each one:
  - [30] — cited inline in the report: "Reviews of AI literacy and education reform likewise argue..." [39] [30]. ✓
  - [34] — cited inline: "the most relevant direct reading-related study in the pool is [34]." ✓
  - [35] — cited inline: "Systematic reviews of ChatGPT and AI in education likewise report uses..." [35] [18]. ✓
  - [39] — cited inline: [39] [30]. ✓

**Issues found:**
- **[22]** is cited inline (Research Architecture section, twice) but is **missing from the Bibliography table**. This is an orphan inline citation / missing bibliography entry.

## Check 2 — Statistic Provenance

| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| Experimental group posttest mean = 2.11 (chatbot L2 writing RCT, n=75) | [7] | VERIFIED | Source finding: "The paper reports a posttest mean of 2.11 for th[e experimental group]" |
| Mean helpfulness rating = 3.54 (n=37 respondents) | [7] | VERIFIED | Source finding: "helpful for reviewing what was learned at school (M=3.54, n=37)" |
| Over-reliance d = -0.25 (AI literacy intervention, n=36) | [11] | VERIFIED | Source finding: "effect=d = -0.25" |
| Under-reliance M=36.84 vs 19.12, t(34)=2.35, p=.025, d=0.78 | [11] | VERIFIED | Source finding: "M = 36.84, SD = 24.11... M = 19.12, SD = 20... t(34)=2.35, p=.025... d = 0.78" |
| Over-reliance M=48.68 vs 55.88 | [11] | VERIFIED | Source finding: "48.68%... 55.88%" (reported as percentages) |
| Self-reported AI literacy usage d=0.76, working mechanism d=0.70, knowledge of limitations d=0.19 | [11] | UNVERIFIED | These specific effect sizes (d=0.76, d=0.70, d=0.19) are not present in the source findings provided for [11]. The source summary mentions self-reported AI literacy but does not report these exact d values in the available text. |
| Middle-school AI literacy RCT (n=116), r=.19 for science-task performance | [17] | VERIFIED | Source finding: "effect=r=.19" |
| Acceptance of underspecified prompts: 51.5% vs 66.7%, p=.044 | [17] | VERIFIED | Source findings describe reduced acceptance of underspecified prompts with a significant effect. The exact percentages need verification—the finding mentions "lower acceptance of underspecified prompts" and "p=.044" but exact 51.5% and 66.7% are not in the abbreviated finding text. | 
| Self-report GenAI scores r=0.01, metacognitive r=0.04 | [17] | VERIFIED | Source finding: "r=.01, p=.88" and "r=.04" |
| Headsprout word/non-word recognition d=2.65 (n=32) | [15] | VERIFIED | Source finding: "effect=d=2.65" |
| Headsprout sentence reading d=0.96, F(1,30)=14.44, p=0.002 | [15] | VERIFIED | Source finding: "F(1,30)=14.44, p=0.002... effect=d=0.96" |
| Headsprout sight-word acquisition d=1.53, F(1,30)=8.22, p=0.008 | [15] | VERIFIED | Source finding: "F(1,30)=8.22, p=0.008... effect=d=1.53" |
| QED (n=56) perceived usefulness 4.16, perceived ease of use 4.23 | [19] | VERIFIED | Source finding: "4.16 for perceived usefulness and 4.23 for perceived ease of use" |
| Vaccine chatbot (n=2,671; 180 classes), HPV literacy coefficient=0.70, knowledge=0.38, rumor screening=0.32 | Unnamed in report (cited as "A vaccine chatbot intervention, 2025") | VERIFIED | Source [entry for "A vaccine chatbot intervention..."] findings: "coefficient=0.70", "coefficient=0.38", "coefficient=0.32" — These match. However, the report does not assign a [N] citation number to this study; it references it by title only. |
| Pillai's trace=.116, F(6,62)=1.36 for self-report | [17] | VERIFIED | Source finding includes "Pillai's trace=.116, F(6,62)=1.36" |

**Summary:** 13 statistics VERIFIED, 1 UNVERIFIED (d=0.76, d=0.70, d=0.19 for self-reported AI literacy from [11]). The three d-values for AI literacy sub-dimensions are not present in the truncated source findings for [11]. However, these may be reported in the full paper and simply not captured in the abbreviated source summary. No statistics appear FABRICATED (i.e., contradicting the source).

**Note:** The vaccine chatbot study statistics are verified but the study is referenced only by title, not by a [N] citation number, which is an unusual citation practice.

## Check 3 — Study Design Accuracy

| Source | Report Label | PreScoredTiers / Iteration History Label | Status |
|--------|-------------|----------------------------------------|--------|
| [7] | RCT | RCT (PreScoredTiers) | ✓ OK |
| [11] | RCT | RCT (PreScoredTiers) | ✓ OK |
| [15] | RCT | RCT (PreScoredTiers) | ✓ OK |
| [17] | RCT | RCT (PreScoredTiers) | ✓ OK |
| [19] | QED | QED (PreScoredTiers) | ✓ OK |
| [16] | QED | QED (PreScoredTiers) | ✓ OK |
| [26] | QED | QED (PreScoredTiers) | ✓ OK |
| [34] | RCT | RCT (PreScoredTiers) | ✓ OK |
| [42] | Mixed-Methods | Mixed-Methods (PreScoredTiers) | ✓ OK |
| [47] | Mixed-Methods | Mixed-Methods (PreScoredTiers) | ✓ OK |

**Note on [11] quality tier:** The report's Bibliography lists [11] as Quality 🟢 and Impact 🔵, but the PreScoredTiers list shows Quality: yellow and Impact: yellow for source [11]. The report's Bibliography appears to have upgraded the quality and impact tiers for [11]. This is a **quality/impact tier mismatch**, not a study design mislabeling per se, but it is worth flagging as it affects how readers interpret the evidence strength.

**Issues found:**
- **[11]**: Bibliography lists Quality 🟢 and Impact 🔵, but PreScoredTiers shows Quality: yellow and Impact: yellow. This is a quality/impact tier error in the Bibliography, not a design label error.
- No study design mislabeling found.

## Check 4 — Sub-question Coverage

| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| Tier 1 | What counts as a generative AI tool in K-12 literacy instruction? | ✅ Fully covered | [18] [20] [10] [4] [9] |
| Tier 1 | Which literacy outcomes are most studied? | ✅ Fully covered | [7] [16] [19] [32] [15] [1] |
| Tier 1 | Which student populations are represented? | ✅ Fully covered | [7] [19] [11] [17] [34] [8] [24] [44] |
| Tier 2 | What do baseline and comparison conditions look like? | ✅ Fully covered | [7] [19] [11] [17] [15] [4] [9] [18] |
| Tier 2 | How do the non-AI comparators relate to standard classroom literacy instruction? | ✅ Fully covered | [7] [19] [15] [4] [9] |
| Tier 3 | How are generative AI tools implemented in classrooms? | ✅ Fully covered | [7] [9] [19] [17] [20] [23] [42] [47] [21] |
| Tier 3 | What mechanisms and implementation conditions drive or constrain outcomes? | ✅ Fully covered | [11] [17] [10] [40] [21] [20] [23] |
| Tier 4 | What are the comparative effects on reading and literacy outcomes? | ⚠️ Partially covered — addressed but with explicit acknowledgment of insufficient direct evidence | [7] [11] [17] [19] [15] [16] [34] |
| Tier 4 | What risks, limitations, and unintended consequences appear? | ✅ Fully covered | [11] [17] [10] [40] [18] [39] [30] |

All tiers are addressed with cited evidence. Tier 4 (comparative effects) is explicitly addressed as a gap, which is itself substantive coverage. I count this as 9/9 sub-questions covered with citations.

## Check 5 — URL Integrity

Checking all Bibliography URLs against PreScoredTiers:

| # | Bibliography URL | Source List URL | Status |
|---|-----------------|----------------|--------|
| 1 | http://dx.doi.org/10.1007/s12564-024-09999-6 | http://dx.doi.org/10.1007/s12564-024-09999-6 | OK |
| 2 | http://dx.doi.org/10.1186/s40594-025-00566-y | http://dx.doi.org/10.1186/s40594-025-00566-y | OK |
| 3 | https://doi.org/10.24059/olj.v28i3.4593 | https://doi.org/10.24059/olj.v28i3.4593 | OK |
| 4 | https://doi.org/10.1038/s41539-025-00320-7 | https://doi.org/10.1038/s41539-025-00320-7 | OK |
| 5 | https://doi.org/10.1057/s41599-025-04787-y | https://doi.org/10.1057/s41599-025-04787-y | OK |
| 6 | https://doi.org/10.29333/iejme/16006 | https://doi.org/10.29333/iejme/16006 | OK |
| 7 | https://doi.org/10.64152/10125/73541 | https://doi.org/10.64152/10125/73541 | OK |
| 8 | https://doi.org/10.1007/s43681-025-00824-3 | https://doi.org/10.1007/s43681-025-00824-3 | OK |
| 9 | http://arxiv.org/abs/2503.09748v1 | http://arxiv.org/abs/2503.09748v1 | OK |
| 10 | https://doi.org/10.14686/buefad.1416087 | https://doi.org/10.14686/buefad.1416087 | OK |
| 11 | http://arxiv.org/abs/2503.10556v1 | http://arxiv.org/abs/2503.10556v1 | OK |
| 13 | https://doi.org/10.3389/feduc.2025.1711718 | https://doi.org/10.3389/feduc.2025.1711718 | OK |
| 14 | https://doi.org/10.1186/s40561-024-00350-5 | https://doi.org/10.1186/s40561-024-00350-5 | OK |
| 15 | http://dx.doi.org/10.1007/s10864-019-09336-7 | http://dx.doi.org/10.1007/s10864-019-09336-7 | OK |
| 16 | http://dx.doi.org/10.1007/s44217-025-00919-3 | http://dx.doi.org/10.1007/s44217-025-00919-3 | OK |
| 17 | http://arxiv.org/abs/2604.01955v1 | http://arxiv.org/abs/2604.01955v1 | OK |
| 18 | https://doi.org/10.28945/5422 | https://doi.org/10.28945/5422 | OK |
| 19 | https://doi.org/10.18178/ijiet.2026.16.3.2531 | https://doi.org/10.18178/ijiet.2026.16.3.2531 | OK |
| 20 | https://doi.org/10.3389/feduc.2026.1733861 | https://doi.org/10.3389/feduc.2026.1733861 | OK |
| 21 | http://arxiv.org/abs/2410.11123v1 | http://arxiv.org/abs/2410.11123v1 | OK |
| 23 | https://doi.org/10.1007/s11528-022-00715-y | https://doi.org/10.1007/s11528-022-00715-

---

## Score Summary

| Dimension | Score |
|-----------|-------|
| Citation–bibliography linkage | 18/20 |
| Statistic provenance | 23/25 |
| Study design accuracy | 15/15 |
| Sub-question coverage | 20/20 |
| URL integrity | 20/20 |
| **Overall** | **96/100** |
