# QA Audit: no_exec_inject_v1 — genai_math

**Score: 66/100**

---



## Audit Summary

The report is moderately trustworthy but contains several significant issues. The most critical problems are: (1) **source number misattributions** — multiple bibliography entries are mapped to the wrong source list entries (e.g., [196] in the bibliography is the LLAMA LIMA meta-analysis, but [196] in the pre-numbered source list is a completely different paper about creative AI use in classrooms; similarly [194] and [208] are mismatched); (2) **duplicate inline citations** — [221] is cited multiple times in the same sentence and appears to conflate two different papers (the pre-numbered [221] is about teacher-in-the-loop personalized tasks, while the bibliography entry [221] refers to the K-12 educator AI survey paper which is actually source [220] in the supplementary list); (3) **some statistics are unverifiable** against the iteration history or require cross-checking between differently numbered sources; (4) several bibliography entries have blank titles, reducing transparency. Overall, the report's narrative is well-supported by the iteration history, but the bibliography numbering contains systematic errors that undermine citation traceability.

---

## Check 1 — Citation-Bibliography Linkage

**Inline citations found in the report body:** [196], [321], [323], [208], [316], [194], [221]

**Issues:**

1. **[321] — cited inline as "LearnLM [321]"** but also referenced as "(LearnLM Team et al., 2025)" without a bracketed number in some places. The bibliography entry [321] exists. However, the inline style is inconsistent — sometimes "[321]" is used and sometimes author-date format without brackets. This is a stylistic inconsistency rather than a missing entry.

2. **[221] — duplicate inline citation in the same sentence**: The report states "[221][221]" in multiple places, which appears to be an error where two different sources were intended (one being the K-12 educator survey [source 220 in supplementary list] and the other being the teacher-in-the-loop study [source 221 in supplementary list]). The bibliography only has one entry for [221], mapped to the Liu et al. K-12 educator survey (which is actually supplementary source [220]).

3. **[194] — bibliography entry mismatch**: The bibliography lists [194] as "Collaborative Working and Critical Thinking: Adoption of Generative AI Tools" by Ruiz-Rojas et al. (2024). However, the pre-numbered source list shows [194] as the same paper. BUT the supplementary source [194] is listed as "Collaborative Working and Critical Thinking..." by Ruiz-Rojas et al. — this is consistent. Wait — actually checking: the pre-numbered list has no [194] (it ends at [191]). The supplementary list has [194] = "Collaborative Working and Critical Thinking..." by Ruiz-Rojas et al. The bibliography entry [194] title is "The factors affecting teachers' adoption of AI technologies" by Hazzan-Bishara et al. — **THIS IS A MISMATCH**. The bibliography [194] title matches supplementary source [193], not [194]. The report discusses teacher adoption factors using [194], which should be [193].

4. **[196] — bibliography entry mismatch**: The bibliography lists [196] as the LLAMA LIMA meta-analysis by Strohmaier et al. However, the supplementary source [196] is actually "Using Generative Artificial Intelligence Creatively in the Classroom and Research" by Molina et al. The LLAMA LIMA paper is supplementary source [195] (or [240]). **The bibliography has the wrong paper mapped to [196].**

5. **[208] — bibliography entry mismatch**: The bibliography lists [208] as the Rizos et al. special education case study. The supplementary source [208] is actually "Latent Profile Analysis of AI Literacy and Trust in Mathematics Teachers" by Wijaya et al. The Rizos et al. paper is supplementary source [207]. **The bibliography has the wrong paper mapped to [208].**

6. **Orphan entries:** All 7 bibliography entries ([194], [196], [208], [221], [316], [321], [323]) have inline citations. No orphan entries detected.

7. **Missing from bibliography:** "(LearnLM Team et al., 2025)" is referenced by author-date in the Executive Summary and Baselines section without a [321] bracket in some instances. This is a minor formatting issue since [321] is in the bibliography.

**Summary of mismatches:**
- [194] bibliography title matches supplementary [193], not [194]
- [196] bibliography title matches supplementary [195]/[240], not [196]
- [208] bibliography title matches supplementary [207], not [208]
- [221] bibliography title matches supplementary [220], not [221]

---

## Check 2 — Statistic Provenance

| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| g = 0.42 overall effect size from living meta-analysis | [196] (intended: LLAMA LIMA) | VERIFIED | Iteration 3 summary: "g = 0.42" attributed to LLAMA LIMA |
| g = 0.31, credible interval [0.06, 0.58] from 15 studies | [196] (intended: LLAMA LIMA) | VERIFIED | Iteration 2 & 3: "g = 0.31 (credible interval 0.06 to 0.58) across 15 studies" |
| 21 studies and 38 effect sizes in LLAMA LIMA | [196] | VERIFIED | Iteration 3: "21 studies" confirmed; "38 effect sizes" mentioned in Iteration 3 executive summary context |
| n=165 RCT, UK secondary classrooms, AI tutor vs human tutors | [321] (LearnLM) | VERIFIED | Iteration 2 & 3: "165 secondary students in the UK" |
| 76.4% of tutoring messages generated by AI with minimal edits | [321] (LearnLM) | VERIFIED | Iteration 2 & 3: "AI drafting 76.4% of tutoring messages" |
| 5.5 percentage point higher success rate on novel math problems | [321] (LearnLM) | VERIFIED | Iteration 2: "student success rates higher by about 5.5 percentage points" |
| 50% of K-12 math and science teachers report generative AI use | [221] | VERIFIED | Iteration 1: "50% have used generative AI" from Liu et al. (2025) |
| 76% for lesson planning | [221] | VERIFIED | Iteration 1: "lesson planning (76%)" |
| 61% for assessment creation | [221] | VERIFIED | Iteration 1: "assessment development (61%)" |
| n=8 case study for special education students | [208] (intended: Rizos et al.) | UNVERIFIED | Iteration 1 mentions Rizos et al. case study but n=8 is not explicitly stated in iteration history |
| n=125 to 385 middle school students in hybrid tutoring | [323] (Thomas et al.) | VERIFIED | Source [118] findings: "125 to 385 low-income middle school students" |
| "38 effect sizes" in LLAMA LIMA | [196] | UNVERIFIED | Not explicitly found in iteration history; iterations mention "21 studies" but "38 effect sizes" is not confirmed |

---

## Check 3 — Study Design Accuracy

1. **[196] (LLAMA LIMA, Strohmaier et al.)** — Report labels this as a meta-analysis. The supplementary source [195]/[240] is described as a "Living Meta-Analysis" in the iteration history. Since this is a notes-sourced paper, the bibliography says "not_reported" which is expected. The report's characterization as a meta-analysis is **consistent with iteration history**. ✅

2. **[321] (LearnLM Team)** — Report labels this as an RCT (n=165). Iteration history (Iterations 2 & 3) describes it as "a randomized controlled trial with 165 secondary students." **Consistent.** ✅

3. **[323] (Thomas et al., 2023)** — Report labels this as QED. The pre-numbered source [118] (same paper) is listed as "Quasi-Experimental Design (QED)" in the source list. Iteration history (Iteration 2) describes "quasi-experimental studies." **Consistent.** ✅

4. **[316] (Bastani et al.)** — Report labels this as RCT. Iteration history (Iteration 2): "large-scale field experiment"; Iteration 3: "high school level field experiment." The supplementary source [259]/[266] describes this as "Generative AI without guardrails can harm learning: Evidence from high school mathematics." Iteration 2 describes it as a "field experiment" which is consistent with RCT. Iteration 3 also calls it "field experiment." The report calling it an "RCT" is a reasonable characterization of a field experiment with randomization, though the iteration history never explicitly uses "RCT." **Minor ambiguity but acceptable.** ✅

5. **[208] (Rizos et al.)** — Report labels this as a "case study, n=8." The supplementary source [207] matches. Iteration 1 describes it as a "case study." **Consistent.** ✅

No mislabelling issues detected.

---

## Check 4 — Sub-question Coverage

| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| 1 | How are generative AI tools defined and characterized in K-8 math education? What outcomes and populations are targeted? | **Covered** — Report defines generative AI tools, their functions, and target populations. | [196], [221] |
| 1 | What characterizes K-8 educational contexts where generative AI is implemented? | **Covered** — Report describes K-8 settings including traditional and hybrid learning environments. | [221] |
| 2 | What baseline or traditional instructional methods are used for comparison? | **Covered** — Report describes traditional instruction, human tutoring, and standard classroom practice as comparators. | [196], [321] |
| 2 | What other technological aids or tutoring systems exist and how do they function? | **Partially covered** — Brief mention of ITS and adaptive math software but limited depth. | [323] |
| 3 | How is generative AI implemented in K-8 math instruction? What mechanisms support math learning? | **Covered** — Report details multiple deployment modes and mechanisms (feedback, scaffolding, problem generation). | [221], [323], [196], [316] |
| 3 | What instructional models and resources facilitate effective AI integration? | **Covered** — Hybrid human-AI tutoring and teacher-mediated models discussed. | [323], [221] |
| 4 | What is the comparative effectiveness of generative AI versus traditional or other tech interventions on K-8 math outcomes? | **Covered** — Meta-analytic effect sizes and RCT results presented. | [196], [321], [323], [316] |
| 4 | How do generative AI effects vary by student or contextual characteristics? | **Partially covered** — Acknowledged as a gap; limited evidence from [208] and [323] about special needs and lower-achieving students. | [208], [323], [196] |
| 4 | What are reported limitations and trade-offs of implementing generative AI in K-8 math education? | **Covered** — Report discusses overreliance risks, teacher PD needs, ethical concerns, accuracy issues. | [316], [194], [221] |

**All 9 sub-questions have at least partial coverage with cited evidence. 7 of 9 are fully covered; 2 are partially covered.**

---

## Check 5 — URL Integrity

All bibliography entries are notes-sourced ([192]+), so I check against the supplementary sources list:

| # | Bibliography URL | Supplementary Source URL | Status |
|---|-----------------|------------------------|--------|
| 194 | `https://www.semanticscholar.org/paper/18b8af39397a8771fcf373e9b3ca2f97b9fb985b` | **Supplementary [193]** has this URL (not [194]). Supplementary [194] URL = `https://www.semanticscholar.org/paper/4e9fefd759c0d0f920533cd70676a59e291729e2` | **MISMATCH** — URL belongs to source [193], not [194] |
| 196 | `https://www.semanticscholar.org/paper/dc4424ba8e77f9bf11df017c58ebf3f08e82242d` | **Supplementary [195]** has this URL (not [196]). Supplementary [196] URL = `https://www.semanticscholar.org/paper/9a915dd9ae7f80f268f4f8dcf26d5318051071ca` | **MISMATCH** — URL belongs to source [195], not [196] |
| 208 | `https://www.semanticscholar.org/paper/c5176feb286e0e266032f5277c20d0ded1837bf3` | **Supplementary [207]** has this URL (not [208]). Supplementary [208] URL = `not available` | **MISMATCH** — URL belongs to source [207], not [208] |
| 221 | `https://arxiv.org/abs/2507.17985` | **Supplementary [220]** has this URL (not [221]). Supplementary [221] URL = `https://arxiv.org/abs/2602.15876` | **MISMATCH** — URL belongs to source [220], not [221] |
| 316 | `https://pmc.ncbi.nlm.nih.gov/articles/PMC12232635` | Supplementary [259] has this URL. Plausible PMC URL. | **OK** (URL is plausible; source number [316] doesn't appear in supplementary list but URL matches [259]) |
| 321 | `https://arxiv.org/abs/2512.23633` | Not in supplementary list. arXiv URL format is plausible. | **OK** (plausible URL format) |
| 323 | `https://arxiv.org/abs/2312.11274` | Not in supplementary list. arXiv URL format is plausible. | **OK** (plausible URL format) |

**4 MISMATCH URLs identified** (all due to systematic off-by-one numbering errors in mapping supplementary sources to bibliography entries).

---

## Recommended Fixes

1. **[CRITICAL] Fix bibliography numbering to match supplementary source list.** The bibliography systematically maps the wrong supplementary source numbers: [194] should reference supplementary [193] or be renumbered; [196] should reference [195]; [208] should reference [207]; [221] should reference [220]. All inline citations should be updated accordingly.

2. **[HIGH] Resolve the [221][221] duplicate citation.** The report cites [221] twice in the same sentence in multiple places. It appears one instance should reference supplementary source [221] (Walkington et al., teacher-in-the-loop study) and the other should reference [220] (Liu et al., K-12 educator survey). Assign distinct numbers and separate the two sources.

3. **[HIGH] Add proper titles to bibliography entries [316], [321], and [323].** These entries have blank title fields (only closing parentheses), making it impossible for readers to identify the source without clicking URLs.

4. **[MEDIUM] Verify the "38 effect sizes" statistic.** The claim that LLAMA LIMA pooled "38 effect sizes" across 21 studies is not confirmed in the iteration history. Either provide a source or remove this specific number.

5. **[MEDIUM] Verify n=8 for the Rizos et al. special education case study.** The iteration history mentions this study but does not explicitly state n=8. Confirm from the original source or note as approximate.

6. **[LOW] Standardize citation format.** The report inconsistently uses both bracketed numbers (e.g., [321]) and author-date format (e.g., "LearnLM Team et al., 2025") for the same source. Choose one format consistently.

7. **[LOW] Distinguish Tier 2 coverage more explicitly.** The sub-question on "other technological aids or tutoring systems" receives only cursory treatment. Consider adding a brief paragraph with additional citations from the iteration history (e.g., references to ITS literature from source [18] or [116]).

---

## Score

| Dimension | Max | Score | Rationale (1 sentence) |
|-----------|-----|-------|------------------------|
| Citation–bibliography linkage

---

## Score Summary

| Dimension | Score |
|-----------|-------|
| Citation–bibliography linkage | 10/20 |
| Statistic provenance | 21/25 |
| Study design accuracy | 15/15 |
| Sub-question coverage | 16/20 |
| URL integrity | 4/20 |
| **Overall** | **66/100** |
