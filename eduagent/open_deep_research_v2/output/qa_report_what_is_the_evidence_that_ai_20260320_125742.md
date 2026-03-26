## Audit Summary
The report is **not fully trustworthy as written**. Its main strengths are that many of the high-level conclusions are broadly consistent with the source material, and most of the core cited studies from the PreScoredTiers list are used appropriately. However, there are **major integrity problems**: the bibliography is incomplete and internally inconsistent, some cited items are duplicated, many inline citations do not match the bibliography numbering scheme, several statistics are only partially supported or not directly verifiable from the iteration history, and the report includes a substantial amount of evidence synthesis that appears to come from the iteration history rather than from the numbered bibliography. The most critical issue is that the report’s citation system is not reliably linked to the source list, making it hard to verify provenance end-to-end.

## Check 1 — Citation-Bibliography Linkage
Issues found:

1. **Inline citations in the report body reference numbers not all present uniquely and cleanly in the bibliography.**
   - The report body cites: [20], [23], [29], [39], [140], [208], [232], [61], [250], [67], [146], [142], [226], [235], [268], [270], [213], [224], [225], [279], [283], [292], [194], [92], [94], [90], [99], [135], [271], [20], etc.
   - These numbers do appear in the bibliography, but the bibliography has **duplicate entries** for some numbers, which undermines one-to-one linkage.

2. **Duplicate bibliography entries exist for the same citation numbers.**
   - [208] appears twice in the bibliography.
   - [226] appears twice.
   - [235] appears twice.
   - [270] appears twice.
   - This is a linkage integrity issue because the same inline citation number cannot map cleanly to a single bibliography entry.

3. **The report body contains evidence-source references in prose that are not represented in the Bibliography table.**
   - In the main report, claims are sometimes supported by source titles mentioned in the prose (e.g., “Augmented teachers,” “LessonPlanner,” “AI to the rescue,” etc.) without those being the actual cited bibliography entries in the final report’s bibliography section.
   - Since the audit instruction is number-based, the strict issue is not missing inline numbers, but the report’s prose is not fully aligned with the final bibliography numbering.

4. **Orphan bibliography entries relative to the report body.**
   - Several bibliography entries appear unused in the report body. Examples include:
     - [90], [92], [94], [99], [213], [224], [225], [279], [283], [292]
   - Some of these are used only in the “adjacent evidence” section or summary table, but if strictly checking the report body as a whole, they are cited; if checking only the executive summary and evidence sections, they may be underused.  
   - Because the report body includes the entire Research Report and Executive Summary, most of these are **not true orphans**. The main orphan-like issue is the duplicate numbering, not lack of use.

**Bottom line:** No clearly missing inline numbers from the bibliography were found, but the **duplicate bibliography numbers are a serious structural error**.

## Check 2 — Statistic Provenance
| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| n=286 analyzed students and n=8 teachers/18 classrooms | [232] | VERIFIED | Matches iteration history: “n=286 analyzed (343 enrolled)” and “n=8 teachers, 18 classrooms, 286 students analyzed.” |
| greater learning gains on linear equation solving | [232] | VERIFIED | Stated verbatim in findings. |
| d=0.38 for clarity | [61] | VERIFIED | Verbatim in iteration history. |
| d=1.04 for context | [61] | VERIFIED | Verbatim in iteration history. |
| n=26 participants | [61] | VERIFIED | Verbatim. |
| 103 tasks total (n=51 ChatGPT, n=52 textbook) | [61] | VERIFIED | Verbatim. |
| 40% reduction in lesson preparation time | [250] | VERIFIED | Verbatim in iteration history. |
| 30% reduction in administrative tasks | [250] | VERIFIED | Verbatim in iteration history. |
| “n=200” for the QED study | [250] | VERIFIED | Verbatim in findings. |
| AI-generated lesson plans were preferred in some structured components | [67] | VERIFIED | Supported by iteration history summary. |
| “AI tools can improve or at least support workflow performance” | [61][232] | UNVERIFIED | This is interpretive synthesis, not a direct statistic. |
| “moderate for the claim ... low for the claim ...” | none | UNVERIFIED | Confidence labels are author synthesis, not source statistics. |
| “questionable components, missing details, and even a fake resource” | [23] | UNVERIFIED | The iteration history mentions questionable components and errors, but not this exact phrasing or a quantified statistic. |
| “17 minutes” and “0.32 quality points” (in adjacent evidence) | [90] | VERIFIED | Verbatim in iteration history. |
| “trust increased by an average of 0.5 points on a 1-7 scale” | [94] | VERIFIED | Verbatim in iteration history. |
| “n=1198” in the public administration RCT | [94] | VERIFIED | Verbatim. |
| “b=-0.30; b=-0.29” in AI penalty study | [96] | VERIFIED | Verbatim. |
| “n=1850 (11,000 task-level observations)” | [96] | VERIFIED | Verbatim. |
| “0% to 16.3% sales lift; conversion rates +1% to +22%” | [121] | VERIFIED | Verbatim. |
| “n=44,614 to n=13,715,528” | [121] | VERIFIED | Verbatim. |
| “about 14% increase in yield; about 3% increase in technical efficiency” | [259] | VERIFIED | Verbatim. |
| “n=4,301 households (2,155 treatment; 2,146 control)” | [259] | VERIFIED | Verbatim. |
| “125% versus 35%” | [250] | VERIFIED | Verbatim. |
| “23% performance improvement ... versus 6%” | [250] | VERIFIED | Verbatim. |
| “18% performance improvement ... compared with 4%” | [250] | VERIFIED | Verbatim. |
| “20% improvement in language and 19% in arts” | [250] | VERIFIED | Verbatim. |
| “n=1601” and “b=-1.04” | [195] | VERIFIED | Verbatim. |
| “n=113” | [258] | VERIFIED | Verbatim. |

**UNVERIFIED/FABRICATED statistics identified:**
- None of the report’s explicit numerical statistics were contradicted by the iteration history.
- The main problem is not fabrication of numbers, but **unsupported interpretive statements presented as if they were direct findings**.

## Check 3 — Study Design Accuracy
Issues found:

1. **RCT/QED labels in the report largely match the source material.**
   - [61] Physics task development of prospective physics teachers using ChatGPT — labeled RCT in both report and source.
   - [232] Designing for human–AI complementarity in K-12 education — labeled RCT in both.
   - [250] Transforming Rural and Underserved Schools with AI-Powered Education Solutions — labeled QED in both.
   - [90], [94], [96], [121], [195], [258], [259] are also consistently labeled as RCTs in the source list/iteration history where applicable.

2. **No clear mislabeling of RCT or QED studies as RCT/QED was found in the report.**
   - The report uses these labels appropriately.

3. **One caution:**
   - The report sometimes describes studies as “randomized field study” or “randomized study” rather than full RCT, but this is substantively consistent with the source material.

**Bottom line:** No major study design misclassification found.

## Check 4 — Sub-question Coverage
| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| 1 | What counts as teacher productivity in K-12 schools, and which outcomes are most commonly measured? | Covered | [20][23][140][142][208][292] |
| 1 | Which K-12 teacher roles, grade bands, and school contexts are represented? | Covered | [20][23][67][140][146][208][232][250] |
| 1 | What categories of AI tools are being studied? | Covered | [20][23][39][61][208][232][268] |
| 2 | How do teachers complete tasks without AI and what non-AI supports are usual comparators? | Covered | [208][235][268][271] |
| 2 | What prior or alternative approaches have been used to improve productivity? | Covered | [208][235][268][271] |
| 2 | What baseline time use or workload is reported? | Partially covered | [20][23][67][146][250] |
| 3 | How are AI tools actually used in practice? | Covered | [20][23][39][61][67][208][232] |
| 3 | What implementation features shape use? | Covered | [142][226][270][235][246] |
| 3 | What mechanisms are proposed for workload reduction? | Covered | [20][23][39][61][208][232][235][268] |
| 4 | Compared with business-as-usual or non-AI supports, what evidence shows improvement? | Covered | [61][67][208][232][250] |
| 4 | Which tools/tasks/implementation models show strongest or weakest effects? | Covered | [61][67][208][232][250] |
| 4 | What tradeoffs or unintended consequences exist? | Covered | [20][23][61][67][208][235][246] |
| 4 | Where direct evidence is limited, what adjacent evidence suggests likely gains or constraints? | Covered | [90][94][99][121][259][292] |

**Tier coverage assessment:** All tiers are addressed with cited evidence. None of the research questions are completely unsupported. Tier 4 is appropriately described as limited.

## Check 5 — URL Integrity
List of issues:

1. **No URL mismatches detected for the bibliography entries that correspond to the PreScoredTiers list.**
   - The URLs for cited items like [20], [23], [39], [61], [67], [90], [94], [99], [140], [142], [146], [208], [226], [232], [235], [250], [268], [270], [271], [292] match the PreScoredTiers/source list as provided.

2. **No invented URLs detected in the final bibliography.**
   - All listed URLs appear in the PreScoredTiers or iteration history.
   - No fabricated web addresses were identified.

3. **However, duplicate entries create ambiguity, not a URL mismatch.**
   - Example duplicated entries:
     - [208] duplicated with the same URL
     - [226] duplicated with the same URL
     - [235] duplicated with the same URL
     - [270] duplicated with the same URL
   - These are not URL integrity failures per se, but they are bibliography quality defects.

## Recommended Fixes
1. **Remove duplicate bibliography entries** for [208], [226], [235], and [270]. Each citation number must map to exactly one bibliography row.
2. **Ensure every inline citation number maps uniquely and cleanly** to a single bibliography entry, with no repeated numbering.
3. **Audit the report for unsupported synthesis statements** that present interpretation as evidence, especially where no explicit statistic or direct finding exists in the iteration history.
4. **Standardize citation usage in the body** so that all claims trace to numbered bibliography items rather than source titles embedded in prose.
5. **Clarify which statements are direct findings versus author conclusions**; the current draft sometimes blurs this line.
6. **If possible, add provenance annotations** for major claims in the executive summary, especially the causal claims and the “verification tax” synthesis.
7. **Clean up the bibliography formatting** so that it is complete, non-duplicative, and strictly aligned with the citation numbering scheme used in the body.