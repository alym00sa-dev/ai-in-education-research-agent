## Audit Summary
The report is **not fully trustworthy as written**. It contains substantial citation-bibliography linkage problems, many unsupported or unverifiable statistics, and several instances where study design labels are overstated relative to the source material. The overall narrative is broadly consistent with the source set, but the final report overclaims precision in places where the iteration history and pre-scored source list do not provide it. The most critical issues are: (1) bibliography numbering is largely disconnected from inline citations, (2) many numerical/statistical claims are not traceable to the iteration history, and (3) several studies are described as RCTs/QEDs without source-backed confirmation.

## Check 1 — Citation-Bibliography Linkage
Issues found:
- **Inline citations do not match the Bibliography numbering scheme.** The report body cites numbers like `[165]`, `[69]`, `[121]`, etc., but the Bibliography table is numbered **1–30 only**. Therefore, most or all inline citations are **missing from the Bibliography**.
- **Bibliography entries 1–30 are orphaned relative to the body citation system.** The body does not cite `[1]`–`[30]` inline in the report text, so the Bibliography table entries are not linked to the body citations.
- **Title/URL matching cannot be validated for the inline citations** because the cited numbers do not correspond to the Bibliography entries.
- **The Bibliography includes source names that are not present in the pre-numbered source list** as cited report numbers; however, the main auditable issue is numbering mismatch rather than specific title mismatch.

### Specific problems
- Inline citations cited in the body: `[165] [69] [121] [121] [71] [166] [73] [83] [116] [181] [79] [128] [59] [57] [54] [149] [136] [118] [182] [87] [167] [70] [74] [77] [88] [51] [53] [91] [56] [145] [165] [121] [166]` and many others.
- Bibliography entries present only for `1–30`, with no correspondence to those inline citation numbers.
- **Result:** citation-bibliography linkage is effectively broken.

## Check 2 — Statistic Provenance

| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| “grades 9–12 is still limited, heterogeneous, and often indirect” | [165][69][121][121] / narrative claim | UNVERIFIED | General synthesis claim; not a specific statistic. Not found verbatim in iteration history as a numeric statistic. |
| “The most defensible conclusion is that AI tools are most likely to help with revision, mechanics, and immediate writing performance…” | [165][69][121] | UNVERIFIED | Directional synthesis, not a specific statistic. |
| “The retrieved source records do not report the effect sizes or pooled coefficients…” | [165][121][166] | VERIFIED | Matches iteration history’s repeated note that exact effect sizes were not retrieved. |
| “The RCT titled Artificial Intelligence, Teacher Tasks and Individualized Pedagogy studied automated writing evaluation in high school” | [121] | VERIFIED | Study exists in source list; however the claim about exact study framing is broad and not numeric. |
| “the retrieved record does not provide the exact sample size or effect estimate” | [121] | VERIFIED | Iteration history explicitly says exact statistics were not provided. |
| “The quasi-experimental study The Role of AI Assisted Writing Feedback in Developing Secondary Students Writing Skills compared AI-assisted feedback with traditional teacher feedback” | [83] | VERIFIED | Source list confirms QED, but exact outcome stats absent. |
| “The pilot study Learning to Prompt in the Classroom to Understand AI Limits indicates that a short classroom AI-literacy workshop can help…” | [87] | UNVERIFIED | The iteration history supports a pilot workshop but does not provide the claimed directional outcome verbatim. |
| “many are small, preliminary, or not fully reported” | [73][79][116][128][181] | UNVERIFIED | General characterization, not a checkable statistic. |
| “The meta-analysis of automated feedback and writing reports positive pooled effects on writing performance, though heterogeneous” | [165] | VERIFIED | Iteration history supports positive overall pooled effects with heterogeneity. |
| “The school-setting systematic review reaches a broadly similar conclusion…” | [121] | VERIFIED | Consistent with iteration history. |
| “The direct high-school studies are more mixed.” | [121][83][87] | UNVERIFIED | Synthesis statement; not a statistic. |
| “The study on AI-generated feedback for ELL writers highlights coherence and cohesion…” | [116] | VERIFIED | Source title indicates coherence and cohesion focus. |
| “students may accept, modify, or rework machine-produced text in different ways” | [79] | VERIFIED | Matches the study description in source list. |
| “benefit may depend on prior proficiency” | [128] | UNVERIFIED | Plausible from source summary but not a precise statistic. |
| “The evidence is stronger for automated writing evaluation and hybrid feedback systems than for generative chatbot use alone” | [165][121][71][166] | UNVERIFIED | Comparative synthesis, not a statistic. |
| “confidence is moderate” / “confidence is low” | various | UNVERIFIED | No formal quantitative confidence metric in source material. |
| “one clear high-school RCT record and at least one direct high-school comparison” | [121][83] | VERIFIED | This matches the iteration history and source list. |
| “The evidence base contains one clear high-school RCT record and at least one direct high-school comparison…” | [121][83] | VERIFIED | Supported by source list/iteration history. |

### FABRICATED statistics
No clear numeric value was found to be explicitly fabricated, but the report contains **many numerically styled claims without provenance**:
- “grades 9–12”
- “11th-grade ELA”
- “8-week high-school comparison” (not substantiated in provided source history)
- “short classroom AI-literacy workshop” (duration not sourced)
- any implied pooled-effect magnitude beyond “positive pooled effects”

### UNVERIFIED statistics / quantitative claims needing removal or sourcing
- Any claim of **exact sample size**
- Any claim of **effect estimate / effect size**
- Any claim of **pooled coefficient**
- Any claim of **percentages** or **durations** not explicitly stated in the iteration history
- Any claim of **moderate/low confidence** if intended as a formal evidence-grade statistic

## Check 3 — Study Design Accuracy
Issues found:
- **Potential overstatement of RCT/QED labels** in the narrative:
  - **Artificial Intelligence, Teacher Tasks and Individualized Pedagogy** is labeled as an RCT in the Bibliography and source list, so the report’s RCT label is supported.
  - **The Role of AI Assisted Writing Feedback in Developing Secondary Students Writing Skills** is labeled QED in the source list, so the report’s QED label is supported.
- **However, several studies are described as causal-comparison designs in ways not supported by the source material**, especially when the report implies experimental strength beyond the metadata:
  - **Learning to Prompt in the Classroom to Understand AI Limits** is a **Mixed-Methods pilot** in the source list, not an RCT/QED.
  - **The high-school case study on the CGScholar AI Helper Project** is qualitative, not causal.
  - **The study of secondary students’ prompt engineering pathways** is qualitative, not experimental.
- **No explicit false RCT/QED labels were identified for the two named studies above**, but the report repeatedly uses causal-sounding wording for non-causal studies.

### Specific design-risk issue
- “The pilot study Learning to Prompt in the Classroom to Understand AI Limits indicates that a short classroom AI-literacy workshop can help…” is **not an RCT/QED claim**, but the wording implies intervention efficacy beyond a pilot design.

## Check 4 — Sub-question Coverage

| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| Tier 1 | What counts as an AI writing assistant in high school literacy research, and how do studies distinguish generative AI, AWE, grammar aids, and ITS tools? | Covered with cited evidence | [165][121][71][166][83][73][87] |
| Tier 1 | Which literacy outcomes are most commonly targeted and how are they operationalized? | Covered with cited evidence | [116][79][70][165][121] |
| Tier 1 | For which populations/settings has AI-supported writing been studied? | Covered with cited evidence | [121][83][69][73][128] |
| Tier 2 | How do students develop writing outcomes without AI writing assistants? | Covered with cited evidence | [69][74][121][165] |
| Tier 2 | What alternative digital approaches have been used as comparison conditions? | Covered with cited evidence | [69][121][165] |
| Tier 2 | What is the baseline level of literacy growth or writing performance under standard instruction? | Partially covered | [69][121][165] |
| Tier 3 | How are AI writing assistants integrated into instruction? | Covered with cited evidence | [73][79][83][118][182][87] |
| Tier 3 | What implementation features matter most? | Covered with cited evidence | [83][118][167][73][87][121] |
| Tier 3 | What mechanisms explain impact? | Covered with cited evidence | [165][121][79][73][87] |
| Tier 4 | Do AI writing assistants improve outcomes more than standard instruction/teacher feedback/non-AI tools? | Covered with cited evidence | [165][121][83] |
| Tier 4 | Which implementation conditions are associated with stronger or weaker effects? | Covered with cited evidence | [83][118][167][121] |
| Tier 4 | Are effects different for specific subgroups? | Covered with cited evidence | [54][116][128][149] |
| Tier 4 | What tradeoffs, risks, or unintended consequences are reported? | Covered with cited evidence | [57][59][79][116][88][51][53][91][56][145][203] |

### Missing tier support
- **No tier is entirely unsupported**, but **Tier 2 “baseline level of literacy growth”** is only partially answered because the report does not provide a concrete baseline estimate or clearly sourced comparator statistics.

## Check 5 — URL Integrity
Issues found:
- The Bibliography URLs are mostly **not auditable against the report body** because the body citations are not mapped to the Bibliography numbering.
- The source list contains many entries with **not_reported** URLs or placeholder/invalid URLs; those are not necessarily invented by the report, but they complicate verification.
- No report-invented URL string was introduced in the Bibliography table itself beyond what appears in the source list, but several URLs are placeholder-like.

### MISMATCH / INVENTED
- **No definitive MISMATCH or INVENTED URLs in the Bibliography table can be confirmed from the supplied material**, because the Bibliography table uses the same titles as the source list items for the included studies, and most URLs are “not available” placeholders.
- However, because the report’s inline citation numbers do not match the Bibliography numbering, **URL integrity is effectively uncheckable for the body citations**.

## Recommended Fixes
1. **Rebuild the citation system so inline citations match Bibliography numbers exactly.**  
   This is the most serious issue. The body should cite `[1]`, `[2]`, etc., matching the Bibliography, or the Bibliography should be renumbered to match the inline citations.

2. **Remove or qualify all unsupported numeric/statistical claims.**  
   Any sample size, effect size, p-value, percentage, or duration not directly present in the iteration history should be deleted or clearly labeled as unavailable.

3. **Stop implying causal strength for non-causal studies.**  
   Keep “pilot,” “case study,” “qualitative,” and “observational” studies framed as implementation or descriptive evidence, not efficacy evidence.

4. **Align design labels with the source list exactly.**  
   Verify each RCT/QED claim against the pre-numbered source list; do not upgrade qualitative or mixed-method studies into quasi-experimental evidence.

5. **Clarify which evidence is direct high-school evidence versus indirect higher-education or EFL evidence.**  
   The current report blends these too freely and overstates applicability to grades 9–12.

6. **Tighten the Bibliography to only sources actually used in the report body.**  
   Remove orphan entries or add missing in-text citations so every bibliography item is linked.

7. **Replace confidence language with explicit evidence grades if available.**  
   “Moderate confidence” and “low confidence” are not substantiated as formal metrics in the source material.

8. **Audit the URL field for each bibliography entry.**  
   Ensure every URL exactly matches the source list entry; if a URL is unavailable in the source list, mark it as unavailable rather than implying a stable link.