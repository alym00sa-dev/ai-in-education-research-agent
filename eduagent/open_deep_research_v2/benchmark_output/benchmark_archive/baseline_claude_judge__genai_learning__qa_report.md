# QA Audit: baseline_claude_judge — genai_learning

**Score: 27/100**

---



## Audit Summary

The final report presents a coherent narrative on generative AI in K-12 education, but suffers from **severe and systematic citation-bibliography mismatches**. The vast majority of inline citation numbers [N] do not correspond to the actual sources listed in the PreScoredTiers. The report appears to have constructed a bibliography by matching citation numbers to sources that share thematic relevance but are factually different papers (e.g., [3] cites "Dai et al., 2025" about high school physics, but PreScoredTiers [3] is a mixed-methods study on AI in language instruction with undergraduate EFL students in China). Nearly every URL in the bibliography is either invented or mismatched. Multiple study designs are mislabelled. Several key statistics are unverifiable or fabricated relative to the source material. The report is **not trustworthy in its current form** for citation-level claims, though the general thematic conclusions are broadly consistent with the iteration history's qualitative synthesis.

---

## Check 1 — Citation-Bibliography Linkage

### Inline citations checked against Bibliography and PreScoredTiers:

| Inline [N] | In Bibliography? | Title/URL match PreScoredTiers? | Issue |
|-------------|------------------|---------------------------------|-------|
| [2] | No | [2] in PreScoredTiers is "Mapping Learning and Game Mechanics for Serious Games Analysis" — report cites it as defining generative AI tools, which does not match | **Missing from bibliography; misattributed content** |
| [3] | Yes | PreScoredTiers [3] = "Artificial intelligence in language instruction…" (undergraduate EFL, mixed-methods). Report claims "Dai et al., 2025. Effects of AI-Assisted Instruction on High School Physics Achievement: A Randomized Controlled Trial." **Title, author, population, and design do not match.** | **MISMATCH — fabricated citation entry** |
| [4] | No | Referenced inline ("Prior educational technology innovations…[4]") but not in bibliography | **Missing from bibliography** |
| [7] | Yes | PreScoredTiers [7] = "Parents' Perceptions of Student Academic Motivation During the COVID-19 Lockdown" (observational, elementary/middle). Report claims "Schneider et al., 2025. Big Data Observational Analysis on Generative AI Use in Classrooms." **Complete mismatch.** | **MISMATCH — fabricated citation entry** |
| [8] | Yes | PreScoredTiers [8] = "ChatGPT: Bullshit spewer or the end of traditional assessments…" (undergraduate). Report claims "Molina et al., 2024. Conceptual Review of Generative AI Risks and Benefits in Education." **Different paper.** | **MISMATCH** |
| [9] | No | Cited inline ("[9]") but not in bibliography | **Missing from bibliography** |
| [10] | No | Cited inline ("[10]") but not in bibliography | **Missing from bibliography** |
| [11] | Yes | PreScoredTiers [11] = "A survey on large language model based autonomous agents" (adult, meta-analysis/systematic review, red quality). Report claims "Alqarni, 2026. Survey Study on Teacher AI Adoption…" **Complete mismatch.** | **MISMATCH — fabricated citation entry** |
| [12] | Yes | PreScoredTiers [12] = "Revolutionizing education with AI: Exploring the transformative potential of ChatGPT" (systematic review, not_reported population). Report claims "Liu et al., 2024. Experimental and Observational Analysis of AI Impact on Creativity." **Different paper.** | **MISMATCH** |
| [14] | Yes | PreScoredTiers [14] = "The Promises and Challenges of Artificial Intelligence for Teachers: a Systematic Review" (K-12 teachers, systematic review). Report claims "Ruiz-Rojas et al., 2024. Observational and Qualitative Study on AI-Supported Collaborative Learning." **Different paper.** | **MISMATCH** |
| [15] | Yes | PreScoredTiers [15] = "Human-in-the-loop machine learning: a state of the art" (adult, systematic review). Report claims "Hong & Guo, 2024. Mixed Methods Study on AI Instructional Scaffolding." **Complete mismatch.** | **MISMATCH** |
| [16] | Yes | PreScoredTiers [16] = "The AI generation gap: Are Gen Z students more interested in adopting generative AI…" (undergraduate, mixed-methods). Report claims "Zhao et al., 2024. Meta-Analysis on Generative AI Impact on K-12 Critical Thinking and Problem Solving." **Complete mismatch.** | **MISMATCH — fabricated citation entry** |
| [17] | Yes | PreScoredTiers [17] = "Evaluating Generative AI Tools for Personalized Offline Recommendations" (undergraduate, QED). Report claims "Ahmed et al., 2024. Analysis of Equity and Access Challenges in AI Education." **Different paper.** | **MISMATCH** |
| [18] | Yes | PreScoredTiers [18] = "E-EVAL: A Comprehensive Chinese K-12 Education Evaluation Benchmark" (observational). Report claims "Morris & Maes, 2026. Observational Study on AI's Impact on Social-Emotional Development." **Complete mismatch.** | **MISMATCH** |
| [19] | Yes | PreScoredTiers [19] = "Leveraging external data in the analysis of randomized controlled trials" (adult, observational). Report claims "Thanh et al., 2023. AI Assessment Scale Using Bloom's Taxonomy." **Complete mismatch.** | **MISMATCH** |
| [22] | Yes | PreScoredTiers [22] = "Co-Designing Collaborative Generative AI Tools for Freelancers" (adult, qualitative). Report claims "Barnes & Tour, 2025. Qualitative Investigation of Educator Concealment of AI Use." **Complete mismatch.** | **MISMATCH** |
| [27] | Yes | PreScoredTiers [27] = "Federated Learning in Distributed Medical Databases" (adult, observational). Report claims "Sardi et al., 2025. Systematic Review on AI and Creative Problem Solving." **Complete mismatch.** | **MISMATCH** |
| [29] | Yes (orphan) | PreScoredTiers [29] = "Generative AI and the future of higher education…" (mixed-methods, undergraduate). Report bibliography entry: "Bura & Myakala, 2024. Systematic Review and Conceptual Framework on Generative AI in K-12." **Mismatch, and [29] is never cited in the report body.** | **MISMATCH + ORPHAN** |
| [162] | Yes | PreScoredTiers [162] = "Tutor CoPilot: A Human-AI Approach for Scaling Real-Time Expertise" (RCT, elementary and middle school). Report claims "Wang et al., 2024. Tutor CoPilot RCT in K-12 Math Tutoring." **Title and design broadly match, URL matches.** | **OK (closest match in entire bibliography)** |

**Orphan entries:**
- [29] appears in bibliography but is never cited inline in the report body.

**Missing from bibliography but cited inline:**
- [2], [4], [9], [10]

---

## Check 2 — Statistic Provenance

| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| "meta-analysis spanning 29 experiments reported moderate positive effects on critical thinking and problem solving" [16] | [16] in PreScoredTiers is about Gen Z AI adoption, not a meta-analysis of 29 experiments | **FABRICATED** | No such meta-analysis at source [16]; the iteration history references "Zhao et al., 2024" but this is not source [16] |
| "RCT with 387 high school physics students demonstrated improvements in achievement" [3] | [3] in PreScoredTiers is a mixed-methods study with EFL university students, not 387 high school physics students | **FABRICATED** | No source in PreScoredTiers matches "Dai et al., 2025" or 387 physics students |
| "Tutor CoPilot's RCT involving 1,800 K-12 students showed a 4 percentage point increase in math mastery" [162] | PreScoredTiers [162] Finding: "students tutored by those with access to Tutor CoPilot were 4 percentage points more l[ikely to achieve mastery]… n=1,800 students, 782 tutors" | **VERIFIED** | Matches source [162] findings |
| "over 17,000 student interactions" [7] | [7] in PreScoredTiers is about COVID-19 parental perceptions, not 17,000 AI interactions. Iteration history references "Schneider et al., 2024/2025" but this is not source [7] | **FABRICATED** | Statistic exists in iteration history but is misattributed to wrong source number |
| "$20 per tutor annually" (implied in cost discussion) [162] | PreScoredTiers [162]: "Tutor CoPilot costs approximately $20 per tutor annually" | **VERIFIED** | |
| "4 percentage point increase in mastery" [162] | PreScoredTiers [162]: confirmed | **VERIFIED** | |
| "differentiated instruction d=+0.509–+0.741; project-based learning Hedge's g=0.387" (Iteration 1 draft, repeated context) | Not in any PreScoredTiers source | **UNVERIFIED** | Appears only in iteration history without source attribution to a numbered source |

---

## Check 3 — Study Design Accuracy

| Citation | Report Label | PreScoredTiers Label | Status |
|----------|-------------|---------------------|--------|
| [3] "Dai et al., 2025" | RCT | PreScoredTiers [3]: Mixed-Methods, Undergraduate | **MISLABELLED** — not an RCT per source material; also wrong paper entirely |
| [7] "Schneider et al., 2025" | Observational | PreScoredTiers [7]: Observational / Correlational | Design label coincidentally matches, but **wrong paper** |
| [8] "Molina et al., 2024" | Conceptual / Observational | PreScoredTiers [8]: Observational / Correlational | Broadly similar label, but **wrong paper** |
| [11] "Alqarni, 2026" | Survey / Observational | PreScoredTiers [11]: Meta-Analysis / Systematic Review | **MISLABELLED** (also wrong paper) |
| [12] "Liu et al., 2024" | Experimental | PreScoredTiers [12]: Meta-Analysis / Systematic Review | **MISLABELLED** (also wrong paper) |
| [14] "Ruiz-Rojas et al., 2024" | Observational / Qualitative | PreScoredTiers [14]: Meta-Analysis / Systematic Review | **MISLABELLED** (also wrong paper) |
| [15] "Hong & Guo, 2024" | Mixed Methods | PreScoredTiers [15]: Meta-Analysis / Systematic Review | **MISLABELLED** (also wrong paper) |
| [16] "Zhao et al., 2024" | Meta-Analysis | PreScoredTiers [16]: Mixed-Methods | **MISLABELLED** (also wrong paper) |
| [17] "Ahmed et al., 2024" | Report / Review | PreScoredTiers [17]: Quasi-Experimental Design (QED) | **MISLABELLED** (also wrong paper) |
| [18] "Morris & Maes, 2026" | Observational | PreScoredTiers [18]: Observational / Correlational | Coincidentally similar, but **wrong paper** |
| [19] "Thanh et al., 2023" | Observational | PreScoredTiers [19]: Observational / Correlational | Coincidentally matches, but **wrong paper** |
| [22] "Barnes & Tour, 2025" | Qualitative | PreScoredTiers [22]: Qualitative | Coincidentally matches, but **wrong paper** |
| [27] "Sardi et al., 2025" | Systematic Review | PreScoredTiers [27]: Observational / Correlational | **MISLABELLED** (also wrong paper) |
| [29] "Bura & Myakala, 2024" | Systematic Review / Report | PreScoredTiers [29]: Mixed-Methods | **MISLABELLED** (also wrong paper) |
| [162] "Wang et al., 2024. Tutor CoPilot" | RCT | PreScoredTiers [162]: RCT | **CORRECT** |

**Critical RCT mislabelling:** [3] is described as an RCT in the report but is Mixed-Methods in PreScoredTiers (and is the wrong paper entirely).

**Flagged mislabelled designs (counting those that affect RCT/QED claims specifically):**
- [3]: Claimed RCT, source is Mixed-Methods → **mislabelled RCT**
- [16]: Claimed Meta-Analysis, source is Mixed-Methods → mislabelled (not RCT/QED but core claim depends on it)

---

## Check 4 — Sub-question Coverage

| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| Tier 1 | What are generative AI tools and how are they defined within K-12 education? | ✅ Addressed | [2], [7] (both misattributed) |
| Tier 1 | Which learning outcomes are relevant and measurable? | ✅ Addressed | [8], [12], [18], [27] (all misattributed) |
| Tier 1 | What are the characteristics and needs of K-12 students re: AI integration? | ✅ Addressed | [11] (misattributed) |
| Tier 2 | What traditional instructional methods develop skills targeted by generative AI? | ⚠️ Briefly addressed, no cited evidence with valid source numbers | [4] (missing from bibliography) |
| Tier 2 | How have non-generative educational technologies supported K-12 outcomes? | ⚠️ Briefly addressed | [4] (missing from bibliography) |
| Tier 2 | What baseline academic achievement exists without generative AI? | ⚠️ Mentioned generally, no specific cited evidence | None with valid citations |
| Tier 3 | How are generative AI tools integrated into instruction? | ✅ Addressed | [7], [15] (misattributed) |
| Tier 3 | What mechanisms explain generative AI's influence? | ✅ Addressed | [14], [15], [19] (all misattributed) |
| Tier 3 | How do teachers and students effectively use generative AI? | ✅ Addressed | [11], [22] (misattributed) |
| Tier 4 | What comparative evidence exists for generative AI vs. standard instruction? | ✅ Addressed | [16], [3], [162] (only [162] valid) |
| Tier 4 | How do learning gains vary by demographics or subject area? | ⚠️ Mentioned as a gap, not substantively addressed with cited evidence | [11] (misattributed) |
| Tier 4 | What tradeoffs or limitations arise? | ✅ Addressed | [12], [8], [19] (all misattributed) |
| Tier 4 | How do generative AI tools compare to other EdTech interventions? | ⚠️ Briefly mentioned, minimal cited evidence | [16], [10] (both misattributed or missing) |

**Tier-level assessment:**
- Tier 1: Addressed but with invalid citations → partially covered
- Tier 2: Weakly covered, missing valid citations
- Tier 3: Addressed but with invalid citations → partially covered
- Tier 4: Addressed but with mostly invalid citations → partially covered

---

## Check 5 — URL Integrity

| Bib # | Report URL | PreScoredTiers URL | Status |
|-------|-----------|-------------------|--------|
| [3] | `https://doi.org/10.1186/fpsyg.

---

## Score Summary

| Dimension | Score |
|-----------|-------|
| Citation–bibliography linkage | 6/20 |
| Statistic provenance | 11/25 |
| Study design accuracy | 5/15 |
| Sub-question coverage | 5/20 |
| URL integrity | 0/20 |
| **Overall** | **27/100** |
