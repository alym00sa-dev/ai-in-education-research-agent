

## Audit Summary

The report is broadly trustworthy in its directional claims but contains several notable issues. The most critical problems are: (1) significant citation-number confusion, where the report's bibliography numbers do not consistently match the pre-numbered source list (e.g., [206], [211], [212], [213], etc. are notes-sourced papers but the bibliography numbers are offset by one from the supplementary source list, and source [7] in the pre-numbered list is about rubrics, not physics); (2) several inline citations reference studies by name without a bracketed number or with inconsistent referencing (e.g., "Toward Reducing Anxiety and Increasing Performance in Physics Education, 2021" appears inline without a consistent [67] tag, and is mapped to bibliography entry [7] which in the academic-DB list is a rubrics review); (3) some statistics are verified against the iteration history but a few are not fully traceable; (4) study design labels cannot be verified for notes-sourced papers against the bibliography (which lists "not_reported" for all), but cross-referencing with iteration history and the academic-DB list reveals mismatches. The report's substance is reasonable and caveats are appropriately stated, but the bibliography mapping is a significant integrity concern.

## Check 1 — Citation-Bibliography Linkage

**Issues found:**

1. **[7] — Mismatch between bibliography and pre-numbered source list.** The bibliography lists [7] as "Toward Reducing Anxiety and Increasing Performance in Physics Education" (an RCT). In the pre-numbered academic-DB source list, [7] is "The Role of Rubrics in Learning and Implementation of Authentic Assessment: A Literature Review." The physics RCT is actually source [67] in the academic-DB list. This is a critical mismatch.

2. **Inline citations without bracketed numbers.** The report cites "Toward Reducing Anxiety and Increasing Performance in Physics Education, 2021" and "Kültür & Kutlu, 2021" by name inline rather than consistently using bracket numbers, creating ambiguity. The claims table references "Toward Reducing Anxiety and Increasing Performance in Physics [7]" and "Kültür & [324]" — the latter mixes a name with a number.

3. **[206] — Number offset.** The bibliography lists [206] as "Rosdinah Abdul Rashid, Jainatul Halida Jaidin (2014). Exploring Primary School Teachers' Conceptions of 'Assessment for Learning.'" In the supplementary source list, [206] corresponds to "Examining Early Career Teachers' Formative Practices..." by Wenzel et al. (2024). The pre-numbered source list [206] does not exist (only goes to [202]). The bibliography's [206] actually matches supplementary source [205]. The report text cites [206] as defining formative assessment in ways consistent with Wenzel et al. (the supplementary [206]), but the bibliography title is from supplementary [205]. **Mismatch.**

4. **[371] in the bibliography** matches supplementary source [371] (Wenzel, Hovey, Ittner, 2023) — but the bibliography [206] also appears to be the same Rashid/Jaidin paper that is supplementary [205]. This suggests the report's bibliography conflated [205] and [206].

5. **[211] and [212]** — In the supplementary list, [211] = Xuan et al. (2022) reading meta-analysis, and [212] = Karaman (2021) meta-analysis. But in the report bibliography, [211] = Sortwell et al. (2024) umbrella review and [212] = Xuan et al. (2022). Checking supplementary sources: [210] = Sortwell et al. (2024), [211] = Xuan et al. (2022), [212] = Karaman (2021). **The report's [211] (Sortwell) should be [210]; the report's [212] (Xuan) should be [211]; the report's [213] (Karaman) should be [212].** The bibliography numbers are systematically shifted by +1 for these entries.

6. **[213]** — The bibliography lists Karaman (2021), which is supplementary [212]. The supplementary [213] is Ramdhani et al. (2024), a different paper. **Mismatch.**

7. **[217]** — Bibliography lists Boussakuk et al. (2021), which matches supplementary [216]. Supplementary [217] is Gezer et al. (2021). **Off by one.**

8. **[218]** — Bibliography lists Gezer et al. (2021), which matches supplementary [217]. Supplementary [218] is DeLuca et al. (2021). **Off by one.**

9. **[221]** — Bibliography lists Bulut et al. (2020), which matches supplementary [220]. **Off by one.**

10. **[223]** — Bibliography lists Andrade et al. (2021), which matches supplementary [222]. Supplementary [223] is Palabıyık & Daloglu (2025). **Off by one.**

11. **[228]** — Bibliography lists Schneider & Meyer (2011), which matches supplementary [227]. **Off by one.**

12. **[233]** — Bibliography lists Ismail & Osman (2024), which matches supplementary [232]. **Off by one.**

13. **[284]** — Bibliography lists Young & Kim (2010), which matches supplementary [283]. Supplementary [284] is Gischlar (2019). **Off by one.**

14. **[300]** — Bibliography lists Cho et al. (2021) ELL reading meta-analysis, which matches supplementary [299]. Supplementary [300] is Graham et al. (2015) writing meta-analysis. **Off by one.**

15. **[301]** — Bibliography lists Graham et al. (2015) writing meta-analysis, which matches supplementary [300]. Supplementary [301] is Kuhlenengel et al. (2021) about visual environment. **Off by one.**

16. **[309]** — Bibliography lists Yao et al. (2024). This is not in the visible supplementary list (list cuts off at [306]). Cannot verify numbering but the title and content are consistent with iteration history references to "Yao et al. (2024)."

17. **[317], [319], [324], [325], [336], [346], [371], [384], [387], [392], [431]** — These are all above the supplementary list cutoff ([306]), so I cannot verify numbering against the supplementary list. However, the titles and authors are consistent with iteration history references.

18. **Orphan entries:** All bibliography entries appear to be cited inline. No orphan entries detected.

**Summary:** There is a systematic +1 offset in bibliography numbering for supplementary sources in the range ~[206]–[301], and a critical mismatch for [7] (should be [67]).

## Check 2 — Statistic Provenance

| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| ES = +0.19 across 48 studies and 116,051 students (reading) | [212] (Xuan et al.) | VERIFIED | Found in iteration 1 and 3 summaries: "average weighted effect of 0.19" and "48 studies and 116,051 K-12 students" |
| Umbrella review of 13 meta-analyses, trivial to large positive effects, low to very low certainty | [211] (Sortwell et al.) | VERIFIED | Found in iteration 1: "13 meta-analyses...trivial to large positive effects...low to very low" |
| Writing d = .63, teacher feedback d = .89, self-assessment d = .62, peer feedback d = .62, computer feedback d = .38 | [301] (Graham et al.) | VERIFIED | Found in iteration 2 and 3: "d = .63...teacher feedback d = .89...self- and peer-assessment each around d = .62...computer feedback d = .38" |
| Physics RCT: 139 students, 0.34 SD gain, 0.28 SD anxiety reduction | [7]/[67] | VERIFIED | Found in academic-DB source [67] findings: "effect=0.34 SD" and "effect=-0.28 SD" and "n=139" |
| Chemistry: ηp² = 0.21 (conceptual), ηp² = 0.27 (procedural) | [346] (Hagos & Andargie) | VERIFIED | Found in academic-DB source [72] findings: "ηp²=0.21 (group)" and "ηp²=0.27 (group)" and iteration 3 text |
| 12-week QED with 51 tenth graders, formative assessment improved math achievement | [324] (Kültür & Kutlu) | VERIFIED | Found in iteration 3: "12-week quasi-experimental study with 51 tenth graders" |
| K-12 meta-analysis: 258 effect sizes, 118 studies, Hedges' g = 0.25 | [309] (Yao et al.) | VERIFIED | Found in iteration 3: "258 effect sizes from 118 primary studies with an overall effect size of 0.25 (Hedges' g)" |
| Primary math: stronger in first grade than kindergarten, lower-performing classrooms benefited more | [218] (Gezer et al.) | VERIFIED | Found in iterations 1 and 3 |
| Karaman (2021): overall mean effect .72, student-initiated d = 1.16, mixed d = .83, adult d = .69, computer d = .42, 32 studies/47 effect sizes | [213] | VERIFIED | Found in iteration 1 and 3 |
| Peer assessment g = .29 | [431] (Double et al.) | VERIFIED | Found in iteration 3: "g = .29" and in academic-DB source [66] |
| 94% of differentiated-instruction interventions coupled with PD | [212] | UNVERIFIED | Not found verbatim in any iteration history or source findings. The report states this as a specific statistic but it does not appear in the iteration summaries or critiques. |
| Medium effects for ELL reading, upper-elementary stronger than secondary | [300] (Cho et al.) | VERIFIED | Consistent with iteration history references to Cho et al. findings |
| Schneider and Meyer: students tended to demonstrate lower achievement | [228] | VERIFIED | Found in iteration 1: "student achievement tended to be lower than matched comparison students" |

## Check 3 — Study Design Accuracy

1. **[7] in bibliography** — Labeled as "Randomized Controlled Trial (RCT)" with Quality: Blue, Impact: Blue. The actual academic-DB source [7] is "The Role of Rubrics in Learning and Implementation of Authentic Assessment" — a Meta-Analysis/Systematic Review, Quality: red, Impact: yellow. The paper the report intends to reference is academic-DB [67], which is indeed an RCT, Blue/Blue. **The design label is correct for [67] but misattributed to the wrong source number.** FLAG: Source number mismatch.

2. **[206]** — Listed as "not_reported." This is a notes-sourced paper. The iteration history describes it as defining formative assessment (conceptual/qualitative). The bibliography design is "not_reported" which is expected. No mislabeling.

3. **[317] (Boström & Palm, 2023)** — Listed as "not_reported" in bibliography. The academic-DB source [53] has the same paper as "Quasi-Experimental Design" with Quality: green. The report body describes it as a secondary-school study without explicitly labeling it as QED. No explicit mislabeling in the report text.

4. **[324] (Kültür & Kutlu, 2021)** — Listed as "not_reported" in bibliography. The academic-DB source [81] has the same paper as "Quasi-Experimental Design" with Quality: green, Impact: green. The report describes it as "quasi-experimental study" — consistent. No issue beyond numbering.

5. **[346] (Hagos & Andargie, 2022)** — Listed as "not_reported" in bibliography. The academic-DB source [72] has the same paper as "Quasi-Experimental Design (QED)" with Quality: green, Impact: blue. The report describes it as a study with group effects but does not explicitly label the design. No explicit mislabeling.

6. **[431] (Double et al., 2019)** — Listed as "not_reported" in bibliography. The academic-DB source [66] is a "Meta-Analysis / Systematic Review" with Quality: blue, Impact: blue. The report cites it for peer assessment meta-analytic findings, which is consistent. No mislabeling.

**Summary:** The primary issue is the [7]/[67] source number swap, which causes a design mismatch in the bibliography entry (the actual [7] is not an RCT). No other explicit design mislabeling detected.

## Check 4 — Sub-question Coverage

| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| Tier 1 | How is the intervention defined? What outcomes and populations are most studied? | **Fully covered** with dedicated sections on definition and outcomes/populations | [206], [371], [212], [223], [387], [217], [392], [384], [301], [346], [324], [218], [317] |
| Tier 2 | What do baseline or comparison conditions look like? What do studies use as a counterfactual? | **Partially covered** — dedicated section exists but notes frequent under-specification; limited direct evidence on comparator details | [211], [284], [346], [218], [7]/[67] |
| Tier 3 | How is the intervention implemented in practice? What mechanisms or features drive outcomes? | **Partially to well covered** — detailed section on mechanisms, feedback, PD, technology, but limited direct causal tests of components | [223], [212], [213], [431], [301], [228], [221] |
| Tier 4 | What are the effect sizes and how do they vary across populations, designs, or conditions? | **Partially covered** — effect sizes reported for reading, writing, math, science, and overall K-12; subgroup evidence for ELLs, disability, and low-income acknowledged as sparse | [212], [301], [213], [309], [218], [7]/[67], [346], [300], [324], [317] |

## Check 5 — URL Integrity

**Academic-DB sources ([1]–[202]):**

| # | Bibliography URL | Source List URL | Status |
|---|-----------------|----------------|--------|
| 7 | https://doi.org/10.1007/s11165-019-9845-9 | https://doi.org/10.28945/4606 (source [7]) | **MISMATCH** — The bibliography URL matches academic-DB [67], not [7]. |

**Notes-sourced sources ([203]+):**

| # | Bibliography URL | Supplementary URL | Status |
|---|-----------------|-------------------|--------|
| 206 | https://doi.org/10.5539/ies.v7n9p69 | Supplementary [206] URL: https://doi.org/10.30958/aje.10-1-5 | **MISMATCH** — Bibliography URL matches supplementary [205], not [206]. |
| 211 | https://doi.org/10.3390/su16177826 | Supplementary [211] URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC9443994 | **MISMATCH** — Bibliography URL matches supplementary [210]. |
| 212 | https://pmc.ncbi.nlm.nih.gov/articles/PMC9443994 | Supplementary [212] URL: https://doi.org/10.21449/ijate.870300 | **MISMATCH** — Bibliography URL matches supplementary [211]. |
| 213 | https://doi.org/10.21449/ijate.870300 | Supplementary [213] URL: https://doi.org/10.23887/mi.v29i3.89840 | **MISMATCH** — Bibliography URL matches supplementary [212]. |
| 217 | https://doi.org/10.3991/ijet.v16i18.23841 | Supplementary [217] URL: https://doi.org/10.26822/iejee.2021.220 | **MISMATCH** — Matches supplementary [216]. |
| 218 | https://doi.org/10.26822/iejee.2021.220 | Supplementary [218] URL: https

---

## Score Summary

| Dimension | Score |
|-----------|-------|
| Citation–bibliography linkage | 2/20 |
| Statistic provenance | 23/25 |
| Study design accuracy | 10/15 |
| Sub-question coverage | 10/20 |
| URL integrity | 0/20 |
| **Overall** | **45/100** |
