# QA Audit: no_exec_in_report_v1 — math_tutoring

**Score: 37/100**

---



## Audit Summary

The report is partially trustworthy but contains several significant issues that undermine its reliability. The most critical problems are: (1) systematic mislabeling of source numbers — the report cites sources [1], [2], [3], [4], [5], [9], [15], [38], [82], [83] in the bibliography but maps them to papers that correspond to entirely different entries in the pre-numbered source list, creating pervasive citation-bibliography-source mismatches; (2) multiple URLs in the bibliography do not match the pre-numbered source list URLs for the claimed source numbers; (3) several statistics are verifiable against the iteration history or source findings, but the attribution to specific source numbers is incorrect due to the numbering confusion; and (4) the report conflates source numbers with different papers, e.g., citing [38] as "Tutor CoPilot" when source [38] in the pre-numbered list is actually "Tutor CoPilot" (this one happens to be correct), but [1] is cited as "Effective and Scalable Math Support" when source [1] is actually "Student Engagement and Achievement in American Secondary Schools (1992)." The report appears to have constructed its own numbering scheme that partially overlaps with but substantially deviates from the official pre-numbered source list.

---

## Check 1 — Citation-Bibliography Linkage

**Inline citations found in report body:** [1], [2], [3], [4], [5], [9], [15], [38], [82], [83]

**Bibliography entries:** 1, 2, 3, 4, 5, 9, 15, 38, 82, 83

**Issues:**

1. **[1] — MISMATCH**: Report bibliography lists [1] as "Effective and Scalable Math Support: Experimental Evidence on the Impact of an AI-Math Tutor in Ghana (2023)" with URL `https://arxiv.org/pdf/2309.15436.pdf`. The pre-numbered source list [1] is "Student Engagement and Achievement in American Secondary Schools (1992)" with URL `https://eric.ed.gov/?id=ED371047`. The paper the report calls [1] actually corresponds to source [33] in the pre-numbered list.

2. **[2] — MISMATCH**: Report bibliography lists [2] as "Differentiation within and across classrooms (2015)" with URL matching source [79] in the pre-numbered list. Pre-numbered source [2] is "Learning strategies: a synthesis and conceptual model (2016)."

3. **[3] — MISMATCH**: Report bibliography lists [3] as "Educational strategies to reduce the achievement gap (2023)" with URL matching source [28]. Pre-numbered source [3] is "A systematic review and meta-analysis of the evidence on learning during the COVID-19 pandemic (2023)."

4. **[4] — MISMATCH**: Report bibliography lists [4] as "Do intelligent tutoring systems benefit K-12 students? (2025)" with URL matching source [43]. Pre-numbered source [4] is "Early Alert of Academically At-Risk Students (2014)."

5. **[5] — MISMATCH**: Report bibliography lists [5] as "Tutor CoPilot (2025)" with URL matching source [38]. Pre-numbered source [5] is "A Systematic Review of Automatic Question Generation for Educational Purposes (2020)."

6. **[9] — MISMATCH**: Report bibliography lists [9] as "Experimental evidence on learning using low-tech when school is out (2022)" with URL matching source [77]. Pre-numbered source [9] is "Differentiated Instruction in a Standards-Based Middle School Science Classroom (2014)."

7. **[15] — MISMATCH**: Report bibliography lists [15] as "Improving Student Learning with Hybrid Human-AI Tutoring (2024)" with URL matching source [37]. Pre-numbered source [15] is "Blurring Boundaries in Education: Context and Impact of MOOCs (2016)."

8. **[38] — MATCH (partial)**: Report bibliography lists [38] as "Online eLearning for undergraduates in health professions (2014)" with URL `https://www.jogh.org/documents/issue201401/jogh-04-010406.pdf`. This matches source [168] in the pre-numbered list. Pre-numbered source [38] is "Tutor CoPilot: A Human-AI Approach for Scaling Real-Time Expertise (2025)." However, in the report body, [38] is cited in the context of "technology-supported tutoring models in low-resource settings, such as rural Nigerian schools and Botswana primary schools" — which doesn't match either paper.

9. **[82] — MISMATCH**: Report bibliography lists [82] as "Aligning Tutor Discourse Supporting Rigorous Thinking with Tutee Content Mastery (2024)" with URL matching source [34]. Pre-numbered source [82] is "Subgroup analysis methods for time-to-event outcomes (2024)."

10. **[83] — MISMATCH**: Report bibliography lists [83] as "Teaching According to Students' Aptitude: Personalized Mathematics Tutoring (2026)" with URL matching source [108]. Pre-numbered source [83] is "Harmonized Estimation of Subgroup-Specific Treatment Effects (2025)."

11. **Named citations without numbers**: The report cites several papers by title inline (e.g., "Effective and Scalable Math Support, 2023", "Do intelligent tutoring systems benefit K-12 students?, 2025", "Tutor CoPilot, 2025", "Improving Student Learning with Hybrid Human-AI Tutoring, 2024", "Experimental evidence on learning using low-tech when school is out, 2022", "Impact of Technology Interventions on Student Achievement, 2014", "Differentiation within and across classrooms, 2015", "Aligning Tutor Discourse Supporting Rigorous Thinking with Tutee Content Mastery, 2024") without always using [N] format, creating ambiguity.

12. **No orphan bibliography entries** — all bibliography entries are cited somewhere in the report.

---

## Check 2 — Statistic Provenance

| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| d=0.36 increase in math proficiency, n=477, 8-month period (Rori AI tutor, Ghana) | "Effective and Scalable Math Support, 2023" (= source [33]) | VERIFIED | Source [33] finding: "effect=d=0.36, n=477" confirmed |
| 4 percentage points more likely to pass exit tickets (Tutor CoPilot, 1,800 students, 900 tutors) | "Tutor CoPilot, 2025" (= source [38]) | VERIFIED | Source [38] finding: "4 percentage point increase in exit ticket pass rate (p<0.01), n=1800 students, 782 tutors" — report says 900 tutors, source says 782 tutors |
| 9 percentage points improvement for less experienced tutors | "Tutor CoPilot, 2025" | UNVERIFIED | Source [38] findings do not mention 9 percentage points; iteration history does not contain this figure verbatim |
| ~$20 per tutor annually (Tutor CoPilot cost) | "Tutor CoPilot, 2025" | UNVERIFIED | Not found in source [38] findings or iteration history findings verbatim |
| n=125 to 385 middle school students, hybrid human-AI tutoring | "Improving Student Learning with Hybrid Human-AI Tutoring, 2024" (= source [37]) | VERIFIED | Source [37] finding: "n=125, 385, and 75 students across three sites" |
| Tutor-to-student ratio from 1:8 to 1:4 | "Improving Student Learning with Hybrid Human-AI Tutoring, 2024" | UNVERIFIED | Not found verbatim in source [37] findings or iteration history |
| ~$700 per student annually (hybrid model cost) | "Improving Student Learning with Hybrid Human-AI Tutoring, 2024" | UNVERIFIED | Iteration 1 mentions "below $750" from Thomas et al. (2023); report says "~$700." Close but not exact match |
| 0.121 SD improvement, Botswana phone/SMS RCT | "Experimental evidence on learning using low-tech when school is out, 2022" (= source [77]) | VERIFIED | Source [77] finding: "0.121 standard deviations increase (combined phone + SMS), n=4,550" |
| 62% baseline increased to 66% (exit ticket pass rate) | "Tutor CoPilot, 2025" | UNVERIFIED | Not found in source [38] findings or iteration history |
| 900 tutors in Tutor CoPilot study | "Tutor CoPilot, 2025" | FABRICATED | Source [38] states 782 tutors, not 900 |
| Hedge's g = 0.72 for middle school peer tutoring | Iteration history (Alegre et al., 2021) | VERIFIED | Found in Iteration 3 executive summary |

**Summary:** 4 VERIFIED, 5 UNVERIFIED, 1 FABRICATED (900 tutors vs. 782 tutors)

---

## Check 3 — Study Design Accuracy

1. **[1] in bibliography (= source [33] "Effective and Scalable Math Support")**: Report labels as RCT. Source [33] design is "Randomized Controlled Trial (RCT)." ✅ Correct (though number is wrong).

2. **[4] in bibliography (= source [43] "Do intelligent tutoring systems benefit K-12 students?")**: Report labels as "Meta-Analysis / Systematic Review." Source [43] design is "Meta-Analysis / Systematic Review." ✅ Correct.

3. **[5] in bibliography (= source [38] "Tutor CoPilot")**: Report labels as RCT. Source [38] design is "Randomized Controlled Trial (RCT)." ✅ Correct.

4. **[9] in bibliography (= source [77] "Experimental evidence on learning using low-tech")**: Report labels as RCT. Source [77] design is "Randomized Controlled Trial (RCT)." ✅ Correct.

5. **[15] in bibliography (= source [37] "Improving Student Learning with Hybrid Human-AI Tutoring")**: Report labels as QED. Source [37] design is "Quasi-Experimental Design (QED)." ✅ Correct.

6. **[38] in bibliography (= source [168] "Online eLearning for undergraduates")**: Report labels as "Meta-Analysis / Systematic Review." Source [168] is "Meta-Analysis / Systematic Review." ✅ Correct — but this source is irrelevant to the report's claims about "technology-supported tutoring models in low-resource settings."

7. **[82] in bibliography (= source [34] "Aligning Tutor Discourse")**: Report labels as "Observational / Correlational." Source [34] design is "Observational / Correlational." ✅ Correct.

8. **[83] in bibliography (= source [108] "Teaching According to Students' Aptitude")**: Report labels as QED. Source [108] design is "Quasi-Experimental Design (QED)." ✅ Correct.

9. **[2] in bibliography (= source [79] "Differentiation within and across classrooms")**: Report labels as "Meta-Analysis / Systematic Review." Source [79] is "Meta-Analysis / Systematic Review." ✅ Correct.

10. **[3] in bibliography (= source [28] "Educational strategies to reduce the achievement gap")**: Report labels as "Meta-Analysis / Systematic Review." Source [28] is "Meta-Analysis / Systematic Review." ✅ Correct.

**Issue flagged:** While design labels match the actual papers referenced (not the pre-numbered IDs), the **source number assignments are systematically wrong**, meaning the bibliography numbers do not match the pre-numbered source list. This is a structural problem rather than a design labeling problem per se.

No design mislabeling issues found when matching against actual papers.

---

## Check 4 — Sub-question Coverage

| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| 1 | What are the key definitions and characteristics of tutoring in the context of K-8 mathematics education? | ✅ Fully covered | [1], [4] (as mapped in report) |
| 1 | What specific math skills and learning outcomes are targeted in K-8 education for improvement? | ✅ Fully covered | [82], [5], [15] (as mapped in report) |
| 1 | What are the typical educational contexts and structures of mathematics instruction for K-8 students? | ✅ Covered | [1], [9] |
| 2 | What instructional methods and practices are commonly used to develop math skills among K-8 students without tutoring? | ⚠️ Partially covered — brief mention of alternatives | [2], [3] |
| 2 | How is mathematics achievement typically measured in K-8 students without tutoring intervention? | ⚠️ Partially covered — mentions standardized tests briefly | [82], general references |
| 2 | What alternative or supplementary interventions to tutoring exist for supporting math achievement in K-8 populations? | ⚠️ Partially covered — brief mention of differentiation, ed tech, parental engagement | [2], [3] |
| 3 | How is tutoring typically implemented for K-8 students: formats, dosage, tutor qualifications? | ✅ Covered | [5], [15], [1], Tutor CoPilot |
| 3 | What theoretical mechanisms underlie tutoring to enhance math skills in K-8 students? | ✅ Covered | [1], [15], Tutor CoPilot |
| 3 | What are common delivery models and durations of tutoring interventions in K-8 math education? | ✅ Covered | [5], [15], [1] |
| 3 | How do tutor expertise and student engagement influence effectiveness? | ✅ Covered | [5], [15], Tutor CoPilot |
| 4 | What is the evidence comparing math outcomes of K-8 students receiving tutoring versus standard instruction? | ✅ Fully covered | "Effective and Scalable Math Support", [4], Tutor CoPilot, [9] |
| 4 | How do different types of tutoring compare in impact on math achievement? | ⚠️ Partially covered — mentions peer vs. professional/AI but limited direct comparison evidence | [2] (Differentiation), general discussion |
| 4 | What are the observed effects on different subpopulations within K-8? | ⚠️ Partially covered — mentions low-SES benefit more, limited detail | [4], [15] |
| 4 | What are limitations, trade-offs, and scalability considerations? | ✅ Covered | Tutor CoPilot, [15], general synthesis |

**Summary:** 9/14 fully covered, 5/14 partially covered. By tier: Tier 1 (3/3 full), Tier 2 (0/3 full, 3 partial), Tier 3 (4/4 full), Tier 4 (2/4 full, 2 partial).

---

## Check 5 — URL Integrity

| # | Bibliography URL | Pre-numbered Source URL | Status |
|---|-----------------|----------------------|--------|
| 1 | `https://arxiv.org/pdf/2309.15436.pdf` | Source [1]: `https://eric.ed.gov/?id=ED371047` | **MISMATCH** — URL belongs to source [33] |
| 2 | `http://www.rug.nl/research/portal/files/3209202/2015_deunk.pdf` | Source [2]: `https://www.nature.com/articles/npjscilearn201613` | **MISMATCH** — URL belongs to source [79] |
| 3 | `https://doi.org/10.3389/feduc.2023.1155741` | Source [3]: `https://doi.org/10.1038/s41562-022-01506-4` | **MISMATCH** — URL belongs to source [28] |
| 4 | `https://osf.io/download/anonymous/ITS_Meta_Analysis_2025.pdf` | Source [4]: `https://learning-analytics.info/index.php/

---

## Score Summary

| Dimension | Score |
|-----------|-------|
| Citation–bibliography linkage | 0/20 |
| Statistic provenance | 9/25 |
| Study design accuracy | 15/15 |
| Sub-question coverage | 13/20 |
| URL integrity | 0/20 |
| **Overall** | **37/100** |
