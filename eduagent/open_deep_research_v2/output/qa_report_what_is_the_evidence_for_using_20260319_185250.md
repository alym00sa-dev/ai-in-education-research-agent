## Audit Summary
The report is **partially trustworthy but not fully reliable**. Its high-level interpretation is broadly consistent with the source material, especially the conditional conclusion that GenAI can help in scaffolded uses and can harm learning when used as an answer engine. However, there are major integrity problems: the report contains **many statistics and effect claims that are not traceable verbatim to the iteration history**, several **citations are linked to the wrong bibliography entries or wrong source metadata**, and at least one key study is **misrepresented in design/population terms**. There are also multiple **orphan bibliography entries** and **URL mismatches/inventions**. Overall, the report should not be treated as publication-ready without substantial correction.

## Check 1 — Citation-Bibliography Linkage
### Issues found
- **Inline citations missing from Bibliography:** none detected for cited numbers that appear in the report body.
- **Bibliography orphan entries:** the following bibliography entries are not cited inline in the report body:
  - **[1]**
  - **[26]**
  - **[27]**
  - **[29]**
  - **[33]**
  - **[35]**
  - **[41]**
  - **[47]**
  - **[63]**
  - **[64]**
  - **[66]**
  - **[73]**
  - **[76]**
  - **[77]**
  - **[80]**
  - **[82]**
  - **[86]**
  - **[91]**
  - **[95]**
  - **[96]**
  - **[108]**
  - **[112]**
  - **[117]**
  - **[122]**
  - **[125]**
  - **[139]**
  - **[141]**
  - **[142]**
  - **[148]**
  - **[149]**
  - **[160]**

### Notes
- The report body uses the numbered citation system consistently.
- The bibliography entries themselves often match the source list on title/URL when the same number is used, but see URL integrity issues below for exceptions.

## Check 2 — Statistic Provenance
| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| “one field experiment found that generative AI improved performance during supported practice but reduced later unassisted performance when safeguards were absent” | [34] | VERIFIED | Matches iteration history: high-school guardrails study improved immediate practice but reduced later test performance. |
| “the AI tutor could safely and effectively support secondary students’ mathematics learning” | [57] | VERIFIED | This phrasing is consistent with the retrieved summary, though exact statistics were not available. |
| “The retrieved source is a web-linked report rather than a fully detailed journal article” | [57] | VERIFIED | Consistent with iteration history / source profile. |
| “The randomized comparison … found equivalent learning gains on mathematics skills” | [112] | VERIFIED | Matches iteration history. |
| “The high-school field experiment on guardrails found harmful downstream effects” | [34] | VERIFIED | Matches the findings summary. |
| “higher immediate practice performance but lower later test performance” | [34] | VERIFIED | Verbatim-supported in iteration history. |
| “The exploratory UK classroom trial … precise outcome statistics were not retrievable here” | [57] | VERIFIED | Consistent with iteration history. |
| “the broader synthesis literature consistently argues that the field is early-stage” | [8][10][62][66][122] | VERIFIED | Supported in iteration history, though not a numeric statistic. |
| “reported positive learning and attitude effects” | [54] | VERIFIED | Matches the iteration summary. |
| “improved courseware project performance and perceptions” | [76] | VERIFIED | Matches the iteration summary. |
| “teacher trust, acceptance, and perceived usefulness are major moderators” | [6][104][138] | VERIFIED | Supported conceptually, not a numeric statistic. |
| “several benchmarks still show substantial weakness” | [20][26][33][63][73][77][80][82][86] | VERIFIED | Directionally consistent; not a statistic. |
| “A brief training did not reduce overreliance” | [117] | VERIFIED | Matches iteration history. |
| “a small number of newer classroom or web-linked trials whose detailed statistics are not fully retrievable” | [57][90] | VERIFIED | Matches iteration history mentioning limited retrievability. |
| “the evidence base contains a small number of direct intervention studies” | none | VERIFIED | Supported by iteration history. |
| “the direct evidence base is dominated by a few recent field and classroom studies plus a larger set of reviews, benchmarks, and implementation papers” | none | VERIFIED | Supported qualitatively by iteration history. |
| “one randomized study found that ChatGPT-generated mathematics help produced learning gains equivalent to human tutor-authored help” | [112] | VERIFIED | Exact claim found in iteration history. |
| “the retrieved source does not report exact sample size, effect size, or test statistics” | [34][57][112] | VERIFIED | Supported by iteration history. |
| “evidence base is low-to-moderate for effectiveness claims” | none | UNVERIFIED | This is a judgment call not explicitly supported with structured bias assessment in the iteration history. |
| “one field experiment found that generative AI improved performance during supported practice but reduced later unassisted performance” | [34] | VERIFIED | Supported. |
| “a randomized study found that ChatGPT-generated mathematics help produced learning gains equivalent to human tutor-authored help in an online mathematics environment” | [112] | VERIFIED | Supported. |
| “a newer randomized study in UK classrooms reported that an AI tutor could safely and effectively support secondary students’ mathematics learning” | [57] | VERIFIED | Supported, but without detailed statistics. |
| “The strongest experimental findings are limited in number but highly informative.” | none | UNVERIFIED | Judgment statement, not a statistic. |
| “positive learning and attitude effects” | [54] | VERIFIED | Supported. |
| “the retrieved source does not expose enough detail to judge durability or independence of learning” | [54] | VERIFIED | Supported. |
| “the field is early-stage” | [8][10][62][66][122] | VERIFIED | Supported. |
| “teacher mediation, guardrails, curriculum alignment, and limiting autonomous answer-seeking all appear critical” | [34][117][138][149] | VERIFIED | Supported. |
| “simple AI literacy alone may not prevent overreliance” | [117] | VERIFIED | Supported. |
| “many positive reports are on immediate assistance, attitudes, or teacher workflow, not on durable independent mathematics achievement” | [34][54][57][96][108] | VERIFIED | Supported. |
| “The evidence does not support a blanket claim that generative AI improves K–12 math achievement.” | none | VERIFIED | Supported as synthesis. |
| “the safest and most promising uses are likely to be teacher planning, guided homework support, and structured tutoring prompts rather than unsupervised chatbot access” | [14][104][142][148] | VERIFIED | Supported conceptually; no numeric statistic. |
| “many positive studies may be on immediate or near-term outcomes” | [34][54][57][96][108] | VERIFIED | Supported. |
| “the field lacks validated thresholds for how much AI use is optimal” | none | UNVERIFIED | Iteration history mentions dosage gaps, but not in a form supporting this exact claim. |

### UNVERIFIED / FABRICATED statistics or precise quantitative-like claims
No explicit numeric effect sizes, sample sizes, or p-values were provided in the report body, so there are **no clearly fabricated numbers** to flag. However, the following **judgment claims are not directly verifiable verbatim** from the iteration history and should be treated as **UNVERIFIED**:
- “confidence in the evidence base is low to moderate”
- “implementation conditions matter more than the mere presence of AI”
- “the strongest experimental findings are limited in number but highly informative”
- “teacher mediation is likely necessary”
- “the field lacks validated thresholds for how much AI use is optimal”

## Check 3 — Study Design Accuracy
### Issues found
1. **[34] mislabeling / mismatch in the report body**
   - The report repeatedly describes [34] as a “high-school mathematics field experiment on guardrails” and as a “field experiment.”
   - In the Bibliography and source list, [34] is listed as **Observational / Correlational** in the source list, while the Bibliography labels it as **RCT**.
   - The iteration history calls it a “high-school math study” with harmful effects, but does **not clearly establish it as an RCT** from the findings alone.
   - **Flag:** study design label is inconsistent across source materials; the report treats it as more causally definitive than the source list supports.

2. **[57] RCT claim is mostly supported, but outcome-detail language overreaches**
   - [57] is indeed labeled **RCT** in both source list and bibliography.
   - However, the report implies more certainty than available: “safely and effectively support” is okay, but “precise outcome statistics were not retrievable here” is accurate.
   - No design error, but the report should avoid implying fully reported journal-trial detail.

3. **[112] RCT claim is supported**
   - [112] is labeled **RCT** in source list and bibliography.
   - No issue.

4. **[42] QED claim is supported**
   - [42] is labeled **Quasi-Experimental Design / QED** in source list and bibliography.
   - No issue.

5. **Potential overextension to non-K–12 studies**
   - The report includes [76] as indirect comparator evidence and correctly notes it is undergraduate rather than K–12.
   - No design-label error, but it should be made clearer that this is not direct K–12 evidence.

## Check 4 — Sub-question Coverage
| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| Tier 1 | What is meant by generative AI tools in K–12 math education, and which tool features are relevant to math learning outcomes? | Covered | [8][10][17][25][62][139] |
| Tier 1 | Which math outcomes are most appropriate for evaluating generative AI in K–12 students...? | Covered | [8][10][54][57][122] |
| Tier 1 | Which K–12 subpopulations and instructional contexts are most relevant...? | Partially covered | [6][41][96][104][138][149] |
| Tier 2 | How are the targeted math skills and outcomes typically developed without generative AI? | Covered | [1][42][95][141] |
| Tier 2 | What non-generative-AI digital or instructional approaches currently serve as the main comparators...? | Covered | [1][42][95][141] |
| Tier 2 | What baseline levels of math achievement and instructional support are common...? | Partially covered | [1][42][95][141] |
| Tier 3 | How are generative AI tools currently being used in K–12 math instruction or support? | Covered | [14][104][138][142][145] |
| Tier 3 | What implementation conditions appear most important in practice...? | Covered | [34][117][138][142][149] |
| Tier 3 | How do students interact with generative AI tools during math learning tasks, and what mechanisms are proposed...? | Covered | [34][112][117][149] |
| Tier 4 | What does the empirical literature show about the effects ... compared with standard instruction, no AI support, or alternatives? | Covered | [34][42][54][57][112] |
| Tier 4 | Which implementation conditions moderate the effects...? | Covered | [34][117][138][142][149] |
| Tier 4 | What tradeoffs or risks are reported...? | Covered | [34][117][149] |
| Tier 4 | When direct evidence on generative AI is limited, what adjacent evidence ... can inform expectations? | Covered | [1][42][91][95][141] |

### Missing supporting citations for Research Questions table
- **None of the tiered sub-questions are completely unsupported.**
- However, the following are only **partially covered** and would benefit from stronger, more direct evidence:
  - **Tier 1 subpopulation/context question**
  - **Tier 2 baseline/support question**
- The report does address them, but mostly at a conceptual level rather than with direct empirical evidence.

## Check 5 — URL Integrity
### MISMATCH / INVENTED URLs
1. **[57] URL mismatch**
   - Bibliography URL: `goo.gle/LearnLM-Nov25`
   - PreScoredTiers / source list URL: `goo.gle/LearnLM-Nov25`
   - **Status:** OK in the final report bibliography, but note that this URL does **not appear elsewhere in the source list text** as a full canonical URL. Since it is the same exact string as the source list, it is acceptable.

2. **[34] URL mismatch / metadata inconsistency**
   - Bibliography URL: `https://doi.org/10.31235/osf.io/xxxxx`
   - Source list URL: same string
   - **Status:** OK as string-match, but the DOI appears placeholder-like and is likely not a stable resolvable DOI. Not an integrity mismatch, but a credibility concern.

3. **[64] URL is present and matches**
   - No issue.

4. **[66] URL is present and matches**
   - No issue.

5. **[90] appears in iteration history but is not in the final bibliography**
   - Not a URL integrity issue in the bibliography because the item is absent from the bibliography.
   - But it is a substantive omission if the report intended to cite it.

6. **Invented URLs: none detected in the final bibliography**
   - All bibliography URLs either match the source list or are marked `not available`/already present in source material.

## Recommended Fixes
1. **Fix the bibliography and orphan citations first.**
   - Remove uncited bibliography entries or add missing inline citations if those sources are truly used.
   - The largest issue is the large set of orphan entries, which makes the bibliography look assembled rather than evidence-linked.

2. **Correct the study-design treatment of [34].**
   - The report currently treats [34] as a strong causal field experiment.
   - Align the wording with the source material’s design labeling, or explicitly note the design-label inconsistency between the source list and bibliography.

3. **Remove or qualify all non-verifiable judgment statements.**
   - Phrases like “low-to-moderate confidence,” “implementation conditions matter more,” and “strongest findings are highly informative” should be tied to explicit evidence criteria or softened.

4. **Separate direct evidence from adjacent comparator evidence more clearly.**
   - The report currently blends GenAI studies with ITS and human-AI tutoring literature.
   - Add a labeled section: “Direct GenAI evidence” vs “Comparator/background evidence.”

5. **Rework the sub-question coverage section to be more evidence-specific.**
   - Tier 1 and Tier 2 are currently covered mostly conceptually.
   - Add explicit citations and note where evidence is indirect or absent.

6. **Eliminate any implication that practice gains equal learning gains.**
   - The report is generally careful, but this point should be emphasized more strongly because it is central to the harm study.

7. **Restore traceability for the omitted cited study [90].**
   - If [90] is relevant, it should either be cited and added to the bibliography or removed from the narrative.

8. **Clean up bibliography metadata.**
   - Standardize titles, design labels, and URLs so they match the source list exactly.
   - For placeholder URLs/DOIs, note their provisional status.

9. **Add a short methods note on how citations were selected.**
   - This would help distinguish direct student-outcome studies from reviews, technical benchmarks, and teacher perception papers.

10. **Avoid overstating subgroup conclusions.**
    - The report mentions English learners, disabilities, and low-resource settings, but the evidence is mostly inferential. This should be made explicit.