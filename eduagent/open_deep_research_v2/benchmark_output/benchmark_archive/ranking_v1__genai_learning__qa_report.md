# QA Audit: ranking_v1 — genai_learning

**Score: 47/100**

---



## Audit Summary

The report is partially trustworthy but contains several significant issues that undermine its reliability. The most critical problems are: (1) **systematic misalignment between bibliography reference numbers and the supplementary source list**, where multiple citations refer to the wrong papers (e.g., [193] in the report refers to the Jauhiainen & Guerra school lesson study, but [193] in the supplementary list is actually the Shanto et al. framework paper); (2) **an unverified statistic** about a "20% improvement in test scores" and "75% increased motivation" that cannot be traced to any source in the iteration history with a clear provenance; (3) **study design labels cannot be verified** against the bibliography since all notes-sourced papers show "not_reported" and the iteration history descriptions must be used instead; and (4) **the Tutor CoPilot RCT [268]** is cited as the strongest causal evidence but is mapped to a supplementary source that is actually the Molina et al. creative classroom paper, not the Wang et al. Tutor CoPilot study. These numbering mix-ups create a pervasive trust problem throughout the report.

---

## Check 1 — Citation-Bibliography Linkage

### Inline citations vs. Bibliography entries:

| Citation | In Bibliography? | Title Match? | Issue |
|----------|-----------------|--------------|-------|
| [193] | ✅ Yes | ❌ **MISMATCH**: Bibliography says "Generative AI and ChatGPT in School Children's Education" (Jauhiainen & Guerra), but supplementary source [193] is "A proposed framework for achieving higher levels of outcome-based learning using generative AI in education" (Shanto et al., 2025). The bibliography entry for [193] uses the URL from supplementary [192]. | Number-to-paper mapping is swapped. |
| [194] | ✅ Yes | ❌ **MISMATCH**: Bibliography says "A proposed framework for achieving higher levels of outcome-based learning using generative AI in education" (Shanto et al., 2025), but supplementary source [194] is "Collaborative Working and Critical Thinking: Adoption of Generative Artificial Intelligence Tools" (Ruiz-Rojas et al., 2024). | Number-to-paper mapping is wrong. |
| [196] | ✅ Yes | ❌ **MISMATCH**: Bibliography says "The Generative AI Landscape in Education" (Ahmed et al., 2024), but supplementary source [196] is "Advancing Transformative Education: Generative AI as a Catalyst for Equity and Innovation" (Bura & Myakala, 2024). | Number-to-paper mapping is wrong. |
| [198] | ✅ Yes | ❌ **MISMATCH**: Bibliography says "Leveraging Generative AI Tools for Enhanced Lesson Planning" (Kehoe, 2023), but supplementary source [198] is "Teachers and AI: Understanding the factors influencing AI integration in K-12 education" (Filiz et al., 2025). | Number-to-paper mapping is wrong. |
| [205] | ✅ Yes | ❌ **MISMATCH**: Bibliography says "Empowering Education with Generative Artificial Intelligence Tools" (Ruiz-Rojas et al., 2023), but supplementary source [205] is "A dialogic approach to transform teaching, learning & assessment with generative AI in secondary education" (Tang et al., 2024). | Number-to-paper mapping is wrong. |
| [226] | ✅ Yes | ❌ **MISMATCH**: Bibliography says "The factors affecting teachers' adoption of AI technologies" (Hazzan-Bishara et al., 2025), but supplementary source [226] is "Engaging Teachers to Co-Design Integrated AI Curriculum" (Van Brummelen & Lin, 2020). | Number-to-paper mapping is wrong. |
| [228] | ✅ Yes | ✅ OK: Bibliography says "Opportunities and risks involved in using ChatGPT to create first grade science lesson plans" (Powell & Courchesne, 2024). Supplementary [228] is "Tailoring Education with GenAI" (Karpouzis et al., 2024). | **MISMATCH** — different paper. |
| [241] | ✅ Yes | ✅ OK: Bibliography matches supplementary [240]/[241] — "Exploring the Applications of Generative AI in High School STEM Education" (Masilamony, 2025). | Minor: supplementary [241] is "AI in Education: Rationale, Principles" (Elstad), but bibliography [241] matches [240]. **MISMATCH** |
| [268] | ✅ Yes | ❌ **MISMATCH**: Bibliography says "Tutor CoPilot: A Human-AI Approach" (Wang et al., 2024), but supplementary source [268] is "Using Generative Artificial Intelligence Creatively" (Molina et al., 2024). The actual Tutor CoPilot paper is supplementary [267]. | Number-to-paper mapping is wrong. |
| [269] | ✅ Yes | ❌ **MISMATCH**: Bibliography says "Using Generative Artificial Intelligence Creatively" (Molina et al., 2024), but supplementary source [269] is "Generative AI without guardrails can harm learning" (Bastani et al., 2024). | Number-to-paper mapping is wrong. |

### Orphan bibliography entries (in bibliography but not cited inline):
- None found; all bibliography entries are cited.

### Summary:
**9 out of 10 bibliography entries have mismatched reference numbers** relative to the supplementary source list. The report author appears to have created a bibliography using the correct papers but assigned them to wrong reference numbers, or the supplementary list numbering shifted.

---

## Check 2 — Statistic Provenance

| Statistic | Source Citation | Status | Notes |
|-----------|----------------|--------|-------|
| QED, n=110 elementary/middle school students, ChatGPT-3.5, positive engagement | [193] (intended: Jauhiainen & Guerra, 2023) | **VERIFIED** | Found verbatim in iteration 1 and 3 summaries: "110 elementary and middle school pupils" |
| ~2/3 of students expressed positive attitudes | [193] | **VERIFIED** | Iteration 1: "approximately two-thirds of students enjoyed the AI-modified materials" |
| 51% of K-12 teachers report using ChatGPT | [226] (intended: Hazzan-Bishara et al., 2025) | **VERIFIED** | Iteration 3: "51% used ChatGPT" |
| n=304 teachers surveyed | [226] | **VERIFIED** | Iteration 3: "surveyed 304 teachers" |
| ~4 percentage-point mastery gain (RCT, n~1,800) | [268] (intended: Wang et al., 2024, Tutor CoPilot) | **VERIFIED** | Iteration 2: "gains of approximately 4 percentage points overall" and "n=~1,800 students" |
| 9 percentage points for students with low-quality tutors | [268] | **VERIFIED** | Iteration 2: "9 percentage points for students paired with otherwise low-quality tutors" |
| Meta-analysis N=49 studies | [196] | **UNVERIFIED** | The iteration history does not mention "N=49 studies" for any meta-analysis. This number cannot be traced. |
| 20% improvement in test scores; 75% students reported increased motivation | Not clearly cited | **UNVERIFIED** | Iteration 3 mentions these figures: "a 20% improvement in test scores and approximately 75% of students reported increased motivation" but attributes them to "(not reported)" — no clear source. Not in report body but appeared in iteration 3 summary. |
| 40% incorporating generative AI frequently | [226] | **VERIFIED** | Iteration 3: "40% incorporating generative AI frequently in practice" |
| Large average effect sizes for learning achievement and motivation (meta-analysis) | [196][194] | **UNVERIFIED** | The report claims "large average effect sizes" but no specific quantitative values are provided in iteration history for K-12 generative AI meta-analyses. The characterization "large" is unsupported. |

**Verified: 7 | Unverified: 3 | Fabricated: 0**

---

## Check 3 — Study Design Accuracy

All cited sources are notes-sourced ([192]+), so design labels must be checked against iteration history descriptions:

| Source | Report Label | Iteration History Description | Status |
|--------|-------------|------------------------------|--------|
| [193] (Jauhiainen & Guerra) | QED | Iteration 1, 2, 3: "quasi-experimental study" / "quasi-experimental case study" | ✅ **Correct** |
| [268] (Wang et al., Tutor CoPilot) | RCT | Iteration 2: described as showing AI tutoring "significantly improved mathematical topic mastery" with n~1,800; iteration history does not explicitly say "RCT" but references it as experimental with control; supplementary [267] lists it as Tutor CoPilot. The actual paper (Wang et al., 2024) is described in external sources as an RCT. | ⚠️ **Plausible but not explicitly confirmed as "RCT" in iteration history** — the iteration history says "AI tutoring systems, supplemented by human guidance, significantly improved mathematical topic mastery within under-served populations (n=~1,800 students)" without using the term "RCT." However, the paper itself is widely known as an RCT, so this is **likely correct but weakly sourced from the iterations.** |
| [196] (Ahmed et al.) | Meta-analysis | Iteration history references "systematic reviews" and "meta-analyses" from Ahmed et al. (2024). | ✅ **Correct** |
| [194] (Shanto et al. / Ruiz-Rojas et al.) | Report describes as "qualitative conceptual + empirical small sample" | Iteration 1: "proposed the ACE Framework... without empirical effect size data." This is consistent. | ✅ **Correct** |
| [226] (Hazzan-Bishara et al.) | Survey | Iteration 3: "surveyed 304 teachers" | ✅ **Correct** |

**No clear mislabelling found**, though the RCT label for [268] is not explicitly confirmed in the iteration history text.

---

## Check 4 — Sub-question Coverage

| Tier | Sub-question | Coverage | Key Citations |
|------|-------------|----------|--------------|
| 1 | How are generative AI tools defined and characterized in K-12 education, and what learning outcomes and populations are targeted? | ✅ **Fully covered** — dedicated section with definitions, populations, and target outcomes | [193][205][196][194][226] |
| 1 | What are the predominant K-12 classroom contexts for generative AI implementation? | ✅ **Covered** — discussed in definition and implementation sections | [193][226] |
| 2 | What baseline instructional methods and educational technologies serve as comparators for generative AI interventions in K-12? | ✅ **Covered** — dedicated section on comparators | [268][193][196] |
| 2 | What are typical learning outcomes without generative AI in K-12 settings? | ⚠️ **Partially covered** — mentioned as "standard classroom instruction" baseline but no specific outcome data cited | [193] |
| 3 | How are generative AI tools implemented in K-12 classrooms, and what are the mechanisms driving learning outcomes? | ✅ **Covered** — dedicated section on implementation and mechanisms | [205][226][193][198][228] |
| 3 | How do teachers and students engage with generative AI tools during instruction? | ✅ **Covered** — teacher usage patterns and student engagement discussed | [226][205] |
| 4 | What is the experimentally determined or synthesized effectiveness of generative AI tools on academic performance, engagement, and skill development in K-12 classrooms? | ⚠️ **Partially covered** — some evidence cited but acknowledged as insufficient; no K-12-specific RCT effect sizes | [193][268][196][194] |
| 4 | How do effects vary across diverse student populations, subjects, and settings? | ⚠️ **Partially covered** — acknowledged as a gap; limited evidence cited | [241][268][193][269] |
| 4 | What limitations or tradeoffs are identified in generative AI tool use in K-12? | ✅ **Covered** — dedicated limitations section | [196][205][226] |
| 4 | How does generative AI compare to standard instruction or other educational technologies in terms of learning outcomes? | ❌ **Not covered with evidence** — explicitly stated as "unresolved" with no supporting citations providing comparative data | None |

**Fully covered: 6 | Partially covered: 3 | Not covered: 1**

---

## Check 5 — URL Integrity

All sources are notes-sourced ([192]+). Checking bibliography URLs against supplementary source list:

| # | Bibliography URL | Supplementary Source URL | Status |
|---|-----------------|------------------------|--------|
| 193 | `https://www.semanticscholar.org/paper/5eb0850336e5cb952999dc8522d21799e815ec5f` | [192]: same URL (Jauhiainen & Guerra). [193] supplementary is `https://www.semanticscholar.org/paper/c16ed0ba476712cf9c8a1a3fb9843c7a152a7f4c` (Shanto et al.) | **MISMATCH** — URL belongs to supplementary [192], not [193] |
| 194 | `https://www.semanticscholar.org/paper/c16ed0ba476712cf9c8a1a3fb9843c7a152a7f4c` | [194] supplementary is `https://www.semanticscholar.org/paper/4e9fefd759c0d0f920533cd70676a59e291729e2` (Ruiz-Rojas et al.) | **MISMATCH** — URL belongs to supplementary [193] |
| 196 | `https://www.semanticscholar.org/paper/79bc4f92fce3284f7fb5eaaf580583901d2eff07` | [196] supplementary is `https://www.semanticscholar.org/paper/e3c7a3b2ebc879c519b7602c3f0db414bbc653ae` (Bura & Myakala) | **MISMATCH** — URL belongs to supplementary [195] |
| 198 | `https://www.semanticscholar.org/paper/a610485fa634e2c4f95cec5db643289c5c1f7fed` | [198] supplementary is `https://www.semanticscholar.org/paper/a7ec600b20077aebe10a74ed68d18e3bd99e8958` (Filiz et al.) | **MISMATCH** — URL belongs to supplementary [197] |
| 205 | `https://www.semanticscholar.org/paper/2eeff0f534d303581bc1199671600fbd04a2d01c` | [205] supplementary is `https://www.semanticscholar.org/paper/63834ad328cf214ea52f76b6c7f7155a769f7d85` (Tang et al.) | **MISMATCH** — URL belongs to supplementary [204] |
| 226 | `https://www.semanticscholar.org/paper/18b8af39397a8771fcf373e9b3ca2f97b9fb985b` | [226] supplementary is `https://arxiv.org/abs/2009.11100` (Van Brummelen & Lin) | **MISMATCH** — URL belongs to supplementary [225] |
| 228 | `https://pmc.ncbi.nlm.nih.gov/articles/PMC11182495` | [228] supplementary is `https://arxiv.org/abs/2403.12071` (Karpouzis et al.) | **MISMATCH** — URL belongs to supplementary [227] |
| 241 | `https://arxiv.org/abs/2510.21718` | [241] supplementary is AI in Education Rationale (Elstad). [240] is `https://arxiv.org/abs/2510.21718` (Masilamony) | **MISMATCH**

---

## Score Summary

| Dimension | Score |
|-----------|-------|
| Citation–bibliography linkage | 2/20 |
| Statistic provenance | 18/25 |
| Study design accuracy | 15/15 |
| Sub-question coverage | 12/20 |
| URL integrity | 0/20 |
| **Overall** | **47/100** |
