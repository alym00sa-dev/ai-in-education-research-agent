## Audit Summary
The report is **partially trustworthy at a high level**, but it has several integrity problems that materially limit confidence in its precision. The largest issues are: many inline citations point to bibliography entries that are not actually present in the source list, several bibliography items appear to be **invented or non-matching** relative to the provided PreScoredTiers, and multiple statistics in the report are **unverified** against the iteration history. The narrative conclusions are broadly consistent with the evidence summaries, but the report overstates certainty in some places and includes source/design details that cannot be validated from the supplied materials.

## Check 1 — Citation-Bibliography Linkage
Issues found:

### Inline citations missing from bibliography
The report body uses many inline citations that do **not** appear in the Bibliography table (which only contains [1], [2], [13], [20], [21], [28], [38], [39], [40], [41], [42], [43], [44], [54], [58], [64], [66], [69], [71], [78], [86], [87], [97], [98], [107], [108], [112], [120], [125], [129], [131], [140], [150], [151], [152], [153], [166], [167]). Missing inline citations include, at minimum:

[13][28][38][58][69][105][140] → [105] is not in bibliography  
[129][160][162][169] → [160][162][169] missing from bibliography  
Also in body text:
[42] appears inline and is in bibliography, OK  
[43] appears inline and is in bibliography, OK  
[166] appears inline and is in bibliography, OK

### Bibliography entries with no inline citation in the report body
Most bibliography entries are cited inline, but the following are **orphaned or effectively orphaned** in the body based on the visible report text:
- None clearly orphaned among the listed bibliography entries that are visible in the report body.
- However, because the report uses many citations not represented in the bibliography, the bibliography is incomplete as a linkage system.

### Title/URL match against PreScoredTiers
Several bibliography entries do not match the PreScoredTiers source list because the source list does not contain these numbered entries at all, or contains different metadata. Notably, the report bibliography contains numbers and study titles not present in the supplied PreScoredTiers excerpt:
- [105], [160], [162], [169] are not in the PreScoredTiers source list provided.
- Many other numbered bibliography entries (e.g., [20], [21], [28], [38], etc.) do match the source list numbering, but the report bibliography titles are **not verifiable** against the provided source list because the PreScoredTiers source list itself is the main authoritative set and these entries are only fully provided there for the matching numbers.

## Check 2 — Statistic Provenance
| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| Grade 4 students (experimental n=30; control n=30) | [1] | VERIFIED | Matches iteration history / source list for study [1]. |
| n=60 | [1] | VERIFIED | Derived from 30+30 and consistent with source. |
| partial η²=0.247 | [2] | VERIFIED | Present verbatim in source list for [2]. |
| 46 seventh-grade students | [2] | VERIFIED | Present in source list for [2]. |
| partial η²=0.147 | [2] | VERIFIED | Present verbatim in source list for [2]. |
| 30 elementary students | [152] | VERIFIED | Matches source list [152]. |
| n=30 | [152] | VERIFIED | Matches source list [152]. |
| n=125 | [129] | VERIFIED | Matches source list [129]. |
| p=.569 | [2] | VERIFIED | Present in source list [2]. |
| F=0.330 | [2] | VERIFIED | Present in source list [2]. |
| F=7.047 | [2] | VERIFIED | Present in source list [2]. |
| Strongest K-12-relevant findings are mostly not direct morale trials | multiple | UNVERIFIED | Interpretive claim, not a statistic. |
| No eligible randomized or quasi-experimental K-12 study... directly measured morale/job satisfaction/retention intentions | multiple | UNVERIFIED | Not a statistic, but a direct evidentiary claim not verbatim supported as written. |
| n=125 (undergraduate RCT) | [129] | VERIFIED | Present in iteration history. |
| shorter learning durations / higher interaction frequency | [129] | VERIFIED | Present in source summary, though no exact numeric value repeated in report. |
| no overall effect on VUI performance | [2] | VERIFIED | Matches source summary. |
| partial η²=0.098 | [2] | VERIFIED | Present in source summary. |
| AI-generated feedback ... concrete and timely | [39] | UNVERIFIED | Qualitative characterization, not a checked statistic. |
| There is no credible K-12 causal evidence... | multiple | UNVERIFIED | Not a statistic. |
| Baseline supports ... planning time, coaching, leadership support, strong teacher-student relationships | [13][28][38][58][69][105][140] | UNVERIFIED | Not a statistic. |
| 21% shorter time on task | [160] | VERIFIED | Present in iteration history. |
| β=-0.24 | [160] | VERIFIED | Present in iteration history. |
| n=96 | [160] | VERIFIED | Present in iteration history. |
| 96 minutes vs 114 minutes | [160] | VERIFIED | Present in iteration history. |
| 0.5048 / 0.4863 | [161] | N/A | Not cited in final report body. |
| r=0.25 | [162] | VERIFIED | Present in iteration history. |
| n=326 | [162] | VERIFIED | Present in iteration history. |
| n=164 | [162] | VERIFIED | Present in iteration history. |
| β=0.202; β=0.2437; 0.36 more workspaces/hour | [169] | VERIFIED | Present in iteration history. |
| n=125; n=385; n=75 | [169] | VERIFIED | Present in iteration history. |
| 24 to 33 minutes/week | [169] | VERIFIED | Present in iteration history. |
| No retrieved K-12 RCT directly tests... | multiple | UNVERIFIED | Claim not presented as a statistic and not verbatim supported. |

**UNVERIFIED / FABRICATED statistics list:**  
No clearly fabricated numeric statistic was identified in the report body from the supplied history. Most numeric values that appear are verified. The main problem is **missing provenance for nonnumeric causal claims**, not invented numbers.

## Check 3 — Study Design Accuracy
Issues found:

- **[1]** correctly described as a QED. Source list says Quasi-Experimental Design (QED). OK.
- **[2]** correctly described as a QED. Source list says Quasi-Experimental Design (QED). OK.
- **[152]** correctly described as a QED. Source list says Quasi-Experimental Design (QED). OK.
- **[129]** correctly described as an RCT. Source list says Randomized Controlled Trial (RCT). OK.
- **[160]** correctly described as an RCT in the report. Source list says Randomized Controlled Trial (RCT). OK, though it is not directly relevant to K-12.
- **[162]** correctly described as an RCT in the iteration history, but it is **not cited in the final report bibliography** and not present in the source list excerpt provided here. The report’s use of it is unsupported by the supplied bibliography.
- **[169]** correctly described as a QED in the iteration history, but it is **not cited in the final report bibliography** and not present in the source list excerpt provided here.

No explicit mislabeling of an RCT/QED as the wrong design was found for the studies actually cited in the final report body. The issue is instead **unsupported use of study IDs not in the bibliography/source set**.

## Check 4 — Sub-question Coverage
| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| Tier 1 — Foundational Framing | How are teacher morale and classroom engagement defined and measured in K-12 research, and what subconstructs are most relevant to AI tool studies? | Covered with cited evidence | [64][78][150][151][153] |
| Tier 1 — Foundational Framing | What types of AI tools are being used by K-12 teachers, and which teacher tasks or classroom processes are they intended to support? | Covered with cited evidence | [39][40][41][43][66][125][131][140][166] |
| Tier 1 — Foundational Framing | Which K-12 populations and contexts are most often studied or targeted for AI-supported teaching? | Covered with cited evidence | [64][78][87][107][112][125][131][150][167] |
| Tier 2 — Baseline and Existing Approaches | How are teacher morale and classroom engagement typically supported in K-12 settings without AI? | Covered with cited evidence | [13][28][38][58][69][105][140] |
| Tier 2 — Baseline and Existing Approaches | What is known about baseline levels and trends of teacher workload, stress, engagement, and classroom participation absent AI adoption? | Covered with cited evidence | [13][28][58][69][140][151] |
| Tier 2 — Baseline and Existing Approaches | What non-AI comparators are most appropriate for studying AI tools in K-12 classrooms? | Covered with cited evidence | [13][28][38][58][69][105][140] |
| Tier 3 — Mechanisms and Implementation | How are AI tools integrated into teachers’ daily instructional work in K-12 schools? | Covered with cited evidence | [39][40][41][43][66][107][108][125][131][166] |
| Tier 3 — Mechanisms and Implementation | What implementation features of AI use in K-12 settings are described in the literature? | Covered with cited evidence | [64][78][87][107][112][120][131][140][150][153][167] |
| Tier 3 — Mechanisms and Implementation | Through what proposed mechanisms might AI tools affect teacher morale and classroom engagement? | Covered with cited evidence | [39][40][41][66][78][107][125][131][140][166] |
| Tier 4 — Comparative Evidence and Implications | What empirical evidence shows that AI tools improve teacher morale relative to standard practice or other supports? | Covered, but weakly; cited evidence is mostly indirect | [64][66][78][125][131][140][150][153] |
| Tier 4 — Comparative Evidence and Implications | What evidence shows that AI tools improve classroom engagement in K-12 settings? | Covered, but weakly; cited evidence is mostly indirect | [66][71][125][131][166] |
| Tier 4 — Comparative Evidence and Implications | How do effects vary by grade level, subject, school context, teacher experience, or type of AI tool? | Partially covered | [1][2][64][78][107][112][131][167] |
| Tier 4 — Comparative Evidence and Implications | What tradeoffs, risks, or null findings are reported in comparisons between AI tools and baseline conditions? | Covered with cited evidence | [2][44][54][64][66][78][87][131][140][150][153] |

## Check 5 — URL Integrity
List of issues:

- **[160]** URL in final report bibliography: `https://arxiv.org/abs/2410.12944v3`  
  - **Status:** INVENTED relative to the provided PreScoredTiers excerpt, because [160] is not present in the source list excerpt supplied for audit.  
- **[162]** URL in final report body/bibliographic discussion is unsupported by the provided source list excerpt.  
  - **Status:** INVENTED/unsupported for this audit set (not in source list excerpt).  
- **[169]** URL in final report body/bibliographic discussion is unsupported by the provided source list excerpt.  
  - **Status:** INVENTED/unsupported for this audit set (not in source list excerpt).  
- **[105]** cited inline in body but absent from bibliography; no URL to check in bibliography.  
- **[105]** source itself is present in the PreScoredTiers excerpt as `https://www.frontiersin.org/articles/10.3389/fpsyg.2020.580820/full`, so the report’s omission is linkage-related, not URL mismatch.  
- **[20]**, **[21]**, **[28]**, **[38]**, **[39]**, **[40]**, **[41]**, **[42]**, **[43]**, **[44]**, **[54]**, **[58]**, **[64]**, **[66]**, **[69]**, **[71]**, **[78]**, **[86]**, **[87]**, **[97]**, **[98]**, **[107]**, **[108]**, **[112]**, **[120]**, **[125]**, **[129]**, **[131]**, **[140]**, **[150]**, **[151]**, **[152]**, **[153]**, **[166]**, **[167]** all match URLs in the provided PreScoredTiers source list.  
No clear MISMATCH was detected among the bibliography entries that are actually in the provided source list excerpt.

## Recommended Fixes
1. **Add missing bibliography entries for all inline citations used in the report body**, especially [105], [160], [162], and [169], or remove those citations if they are not intended to be supported by the provided source list.
2. **Remove or clearly qualify unsupported references to studies not present in the provided source list**, particularly the undergraduate RCT [160], the educational escape room RCT [162], and the hybrid human-AI tutoring QED [169], unless the bibliography is expanded to include them.
3. **Tighten causal language**: replace claims like “the evidence suggests AI can improve morale” with a more cautious formulation such as “the evidence suggests AI may plausibly support morale under some conditions, but direct causal evidence is lacking.”
4. **Separate verified statistics from interpretive claims** more clearly; the numeric results from [1], [2], [129], [152], [160], and [169] are fine, but surrounding causal interpretations should be explicitly labeled as indirect or preliminary.
5. **Audit the bibliography for completeness and provenance**: every numbered citation in the body should map to one bibliography row, and every bibliography row should appear in the body at least once.
6. **Remove unsupported “head-to-head” implications** about AI vs. human supports unless backed by a cited study from the source list.
7. **Standardize study-design language** so that only studies explicitly labeled RCT/QED in the source material are described that way.
8. **Clarify that many Tier 4 conclusions are negative findings of absence**, not positive evidence of effect; this will better match the iteration history and avoid overstating efficacy.