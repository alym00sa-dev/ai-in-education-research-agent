# Benchmark: two_pass_delim_v1 — math_tutoring

**Query:** What is the evidence that tutoring improves math outcomes in K-8 students?

**Date/Time:** 2026-03-26 13:15:15

**QA Score:** 85/100

---

## Executive Summary

The direct evidence base indicates that tutoring can improve K-8 mathematics outcomes relative to standard instruction or business-as-usual, but the certainty is only moderate because the strongest studies are heterogeneous, and several of the most policy-relevant findings come from adjacent or partially overlapping tutoring technologies rather than traditional human tutoring. In the clearest causal evidence, a kindergarten intelligent tutoring system, Native Numbers, produced significant numeracy gains in an RCT with n=46 total; the first post-test favored the first-treatment group with ηp²=0.147 and d=1.48 [12]. A separate early-elementary RCT of My Math Academy found treatment students outperformed controls on a researcher-developed math assessment after 12–13 weeks of use, with d=0.11 (n=922) [2]. In Grade 3–8 Ghana, an AI math tutor study reported larger math growth for treatment than control over 8 months, with d=0.36 (n=477) [3]. These studies support a positive direction overall, but the effect sizes range from small to large, and not all are directly comparable to conventional school-based tutoring.

The strongest tutoring-specific experimental findings also show that tutor support can improve proximal learning and tutoring quality. In a preregistered RCT, Tutor CoPilot improved exit-ticket performance by 4 percentage points, with subgroup effects up to 9 percentage points, in n=1,787 students across 4,136 sessions [11]. The intervention also changed tutor behavior on more than 550,000 messages, with treatment tutors using more high-quality strategies, reported as approximately 2 standard deviations more frequent on a log-odds scale [11]. In middle school, a quasi-experimental three-site investigation of hybrid human-AI tutoring found improved mathematics learning-process outcomes relative to software-only or lower-support conditions, including β=0.202 in Site 1 (n=125) and 0.36 more workspaces/hour in Site 3 (n=75) [10]. A UK classroom RCT of LearnLM reported that interactive math tutoring improved immediate remediation and misconception resolution, and supervised LearnLM was at least as effective as human tutors on knowledge transfer, with a 5.5 percentage-point advantage for LearnLM over human tutors and n=165 [22]. These are promising, but they mostly speak to proximal achievement, workflow, or process outcomes rather than long-run standardized test effects.

The broader synthesis evidence is consistent with a positive but heterogeneous tutoring effect, and it helps explain why the direct K-8 math evidence should be interpreted cautiously. A meta-analysis of intelligent tutoring systems for K-12 students concluded that ITS generally benefits achievement, with treatment effects varying by study quality and implementation conditions [1]. A systematic review of primary-school mathematics interventions concluded that classroom-based mathematics interventions can be effective but also emphasized variability across programs and designs [6]. A review of scaffolding in teacher–student interaction likewise supports the plausibility of tutoring mechanisms such as contingent support, but it does not provide a single causal estimate for K-8 math tutoring [21]. Adjacent evidence also suggests that peer tutoring can reduce math anxiety: a middle-school quasi-experimental study found lower learning anxiety with g=0.84 and lower evaluation anxiety with g=0.42 for reciprocal peer tutoring relative to classroom instruction/business-as-usual, though this is an affective rather than achievement outcome [18]. Taken together, the evidence supports tutoring as beneficial, but not as uniformly transformative across formats, outcomes, and contexts.

Across the tiered questions, the evidence answers Tier 1 partially: tutoring is most often defined as individualized or small-group supplemental support, including human tutoring, peer tutoring, AI-supported tutoring, and adaptive software, but the source pool is unevenly distributed across early elementary and middle school, with fewer clean human-tutoring studies in K-8 math than the policy question would require. Tier 2 is partially answered: comparators are usually business-as-usual classroom instruction, wait-control, software-only support, or lower-support conditions, but there is little direct head-to-head evidence comparing tutoring with other supplemental math interventions in the same K-8 settings. Tier 3 is partially answered: the evidence repeatedly points to aligned materials, immediate feedback, structured practice, and tutor guidance as likely mechanisms, yet implementation features are often descriptive rather than causally isolated. Tier 4 is partially answered: effects vary by intervention type, grade band, and outcome domain, but the source pool does not support a single best tutoring model, a precise dosage-response curve, or robust subgroup conclusions for ELs, students with disabilities, rural learners, or low-SES students.

Overall confidence is moderate. The single most important caveat is that the strongest positive findings often come from intelligent tutoring, AI-supported tutoring, or hybrid models, not from abundant direct RCT evidence of traditional K-8 math tutoring against standard instruction; therefore, the literature supports tutoring as effective in principle, but not yet a definitive hierarchy of which human tutoring model, dosage, or implementation package is best across K-8 settings.

| Claim | Supporting Sources | Confidence |
|-------|--------------------|------------|
| Tutoring and tutoring-like supports generally improve K-8 math outcomes relative to business-as-usual or lower-support conditions, but effects are heterogeneous. | [1]; [6] | Moderate |
| Native Numbers produced significant kindergarten numeracy gains, with ηp²=0.147 and d=1.48 in an RCT (n=46 total). | [12] | High |
| My Math Academy improved early elementary math assessment performance after 12–13 weeks, with d=0.11 in an RCT (n=922). | [2] | High |
| The AI math tutor in Ghana increased math growth over 8 months, with d=0.36 in an RCT (n=477). | [3] | High |
| Tutor CoPilot improved exit-ticket pass rates by 4 percentage points, with subgroup effects up to 9 points, in an RCT of n=1,787 students and 4,136 sessions. | [11] | High |
| Hybrid human-AI tutoring improved middle-school learning-process outcomes, including β=0.202 in Site 1 (n=125) and 0.36 more workspaces/hour in Site 3 (n=75). | [10] | Moderate |
| Supervised LearnLM tutoring was at least as effective as human tutors on knowledge transfer, with a 5.5 percentage-point advantage for LearnLM over human tutors (n=165). | [22] | Moderate |
| Reciprocal peer tutoring reduced middle-school mathematics anxiety, with g=0.84 for learning anxiety and g=0.42 for evaluation anxiety (n=420). | [18] | Moderate |
| Adaptive and scaffolded tutoring mechanisms are repeatedly associated with positive learning or engagement outcomes, but mechanism evidence is often descriptive rather than causal. | [24]; [21]; [11] | Moderate |
| The direct evidence base is still thin for precise claims about one-to-one versus small-group tutoring, dosage thresholds, and subgroup moderation in K-8 math. | [1]; [6] | High |

## Research Report

### Research Questions Investigated

| Tier | Sub-question |
|------|-------------|
| 1 | How is tutoring defined in K-8 mathematics research, and what distinguishes one-on-one, small-group, peer, cross-age, and high-dosage tutoring models? |
| 1 | Which math outcomes are most commonly measured in K-8 tutoring studies, and how are they operationalized? |
| 1 | What K-8 student populations and school contexts are typically studied in math tutoring research? |
| 2 | How do schools typically support K-8 students’ math learning without tutoring, and what are the usual counterfactual conditions in tutoring studies? |
| 2 | What alternative or prior instructional approaches are used to improve K-8 math outcomes besides tutoring? |
| 2 | In the absence of tutoring, what baseline growth or achievement trajectories in K-8 math are reported for comparable students and contexts? |
| 3 | How is math tutoring implemented in K-8 settings, including tutor type, session length, frequency, group size, alignment with classroom curriculum, and use of structured materials? |
| 3 | What instructional mechanisms are most commonly proposed for tutoring’s effects on K-8 math outcomes? |
| 3 | How do implementation features vary across school-day, after-school, in-person, and online tutoring models for K-8 mathematics? |
| 4 | What is the effect of tutoring on K-8 students’ math achievement compared with standard instruction or no tutoring, and how large are the reported gains? |
| 4 | Do tutoring effects on K-8 math outcomes differ by grade level, baseline achievement, student subgroup, or tutoring model? |
| 4 | Which tutoring features or delivery conditions are associated with stronger math outcomes in K-8 studies, and what tradeoffs or limitations are reported? |
| 4 | How do adjacent findings on intensive math intervention, high-dosage tutoring, or targeted remediation inform expectations when direct K-8 tutoring evidence is limited? |

## Evidence on Definitions, Populations, Comparators, and Outcomes

### What counts as tutoring in this literature

Across the source pool, tutoring is not a single intervention type but a family of supplemental supports that include human tutoring, peer tutoring, cross-age tutoring, intelligent tutoring systems, adaptive apps, and hybrid human-AI tutoring. The K-12 meta-analysis of intelligent tutoring systems explicitly centers one-to-one or adaptive digital tutoring as a form of individualized instruction and asks when it improves achievement in U.S. schools [1]. The early-elementary My Math Academy trial studied an adaptive game-based math learning app used alongside classroom instruction, which functions as a supplemental tutor-like support rather than a replacement for the core classroom [2]. The Native Numbers replication is similarly an individualized numeracy tutor, while Tutor CoPilot and LearnLM are tutor-support or AI-tutoring systems intended to improve real-time instructional guidance rather than serve as traditional stand-alone classroom lessons [12]; [11]; [22].

The source pool also includes peer tutoring and hybrid human-AI models, which are important because they broaden the intervention class beyond adult-delivered tutoring. Reciprocal peer tutoring in middle school mathematics was studied as a cooperative learning format, and the intervention was aimed at math anxiety rather than achievement per se [18]. The hybrid human-AI study in middle school and the Tutor CoPilot study in school-based tutoring settings show that “tutoring” may also refer to systems that scaffold the tutor, not just the student [10]; [11].

### Who is studied

The direct K-8 evidence is heaviest in early elementary and middle school. The Native Numbers study was in kindergarten, the My Math Academy trial in early elementary, and the Ghana AI tutor trial included grades 3–8 [12]; [2]; [3]. The Tutor CoPilot RCT included elementary and middle school grades 3–8, providing one of the few larger school-based tutoring studies in the focal grade band [11]. The LearnLM classroom RCT targeted secondary years 9–10 and is outside the focal K-8 population, but it remains relevant as adjacent evidence on AI tutoring mechanisms and feasibility [22].

Several reviews underscore that much of the broader evidence base spans multiple grade bands rather than isolating K-8. The K-12 ITS meta-analysis pools elementary, middle, and high school, which strengthens general inference but weakens direct grade-specific conclusions for K-8 tutoring [1]. The primary-school math intervention review focuses more tightly on elementary ages, while the scaffolding review covers primary and secondary settings broadly [6]; [21]. That distribution matters because the evidence base does not yet support a highly precise statement that the same tutoring model works equally well in K-2, grades 3–5, and grades 6–8.

### What outcomes are measured

Achievement is the dominant outcome category, but it is operationalized in multiple ways: researcher-developed numeracy measures, standardized achievement tests, curriculum-based exit tickets, growth scores, and knowledge-transfer assessments. Native Numbers used post-test numeracy outcomes and maintenance testing; My Math Academy used a researcher-developed math assessment; the Ghana AI tutor study used math growth scores; Tutor CoPilot used exit-ticket pass rates; and LearnLM measured misconception resolution and knowledge transfer [12]; [2]; [3]; [11]; [22].

The source pool also includes related outcomes such as engagement, motivation, confidence, and anxiety. My Math Academy improved engagement, motivation, enjoyment, persistence, and confidence according to teacher survey and interview evidence [2]. Reciprocal peer tutoring reduced mathematics anxiety in middle school, with strong effects for learning anxiety and smaller but still meaningful effects for evaluation anxiety [18]. Tutor CoPilot and the LearnLM study also reported improved tutor or student experience and workflow, but those outcomes are intermediate to achievement rather than substitutes for it [11]; [22].

## Experimental and Quasi-Experimental Evidence

### RCT evidence in elementary mathematics

The Native Numbers conceptual replication is the clearest K-8 numeracy RCT in the source pool. In this study, a numeracy intelligent tutoring system was compared with a wait-control/business-as-usual sequence in kindergarten, with n=46 total students. The first post-test showed a significant group difference favoring the first-treatment group, with F(1,44) and a reported effect size of ηp²=0.147 and d=1.48 [12]. The study also reported that intrinsic motivation was not improved overall, and mathematical language outcomes were not significant, which means the achievement effect did not generalize to all related outcomes in the same trial [12].

The My Math Academy RCT provides a larger but more modest early-elementary estimate. In a randomized controlled trial with n=922, students using the adaptive game-based math learning app for 12–13 weeks outperformed controls on a researcher-developed math assessment; the adjusted post-test means were 20.97 (SD=8.01) for treatment and 20.08 (SD=7.99) for control, with d=0.11 [2]. Teacher reports also indicated gains in engagement, motivation, enjoyment, persistence, and confidence, with significantly higher treatment effects on survey and interview evidence, reported as d=0.6 to 1.05 across those non-achievement indicators [2]. This trial is relevant because it shows that a tutoring-like supplement can improve early math learning, but the effect on math achievement itself was small.

The Botswana low-tech remote instruction trial is not a tutoring study in the narrow sense, but it is informative as adjacent supplemental support for primary-school numeracy during school disruption. In an RCT with n=4,550 households, the main phone-plus-SMS intervention increased numeracy learning by 0.121 standard deviations relative to control on the average ASER numeracy level, with 95% CI 0.031 to 0.210 and P=0.008 [8]. Because the intervention involved remote support rather than individualized tutoring, it should not be treated as direct tutoring evidence, but it does reinforce the idea that structured supplemental instruction outside the regular classroom can improve numeracy [8].

### RCT evidence in school-based and AI-supported tutoring

Tutor CoPilot is one of the strongest school-based tutoring trials in the pool. In a preregistered RCT with 1,787 students and 4,136 tutoring sessions across 9 schools in one southern U.S. district, access to the human-AI tutoring support system improved proximal math outcomes: students whose tutors had access to the system were 4 percentage points more likely to pass exit tickets, with subgroup effects up to 9 percentage points [11]. The same study also found that treatment tutors used more high-quality instructional strategies in over 550,000 messages, reported as approximately 2 standard deviations more frequent on a log-odds scale [11]. That combination of student and tutor outcomes is important because it links an implementation feature—real-time expert guidance—to measurable gains in tutoring quality and immediate student performance.

The UK LearnLM classroom experiment is adjacent rather than focal, but it adds causal evidence that interactive AI tutoring can support math learning. In an exploratory RCT with n=165, interactive math tutoring improved immediate remediation and misconception resolution relative to static hints, and supervised LearnLM was at least as effective as human tutoring on knowledge transfer, with a 5.5 percentage-point advantage for LearnLM over human tutors on transfer [22]. Student survey responses were generally favorable, but the survey sample was small and the study does not provide a K-8 math-only estimate [22]. Even so, it strengthens the case that AI-supported tutoring can be educationally viable in math when supervised.

The Ghana AI tutor RCT provides another direct causal estimate in grades 3–8. Over an 8-month study period with n=477, students assigned to the AI math tutor had substantially larger math growth than controls, with growth scores of 5.13 (SD=7.03) for treatment versus 2.12 (SD=6.30) for control and d=0.36 [3]. Because the source pool summary describes the study as an AI-powered math tutor and gives a clear outcome contrast, it is strong evidence that a tutoring-like adaptive system can improve K-8 math learning under relatively low-resource conditions [3].

### Quasi-experimental evidence in middle school tutoring models

The strongest quasi-experimental evidence in the focal grade range comes from hybrid human-AI tutoring in middle school mathematics. In a three-study quasi-experimental investigation, the authors report that hybrid tutoring improved learning-process outcomes relative to software-only or lower-support conditions. Site 1, with n=125, reported tutoring effects of β=0.202; Site 2, with n=385, found that average time spent increased from 24 to 33 minutes per week; and Site 3, with n=75, reported 0.36 more workspaces per hour, with 95% CI 0.02 to 0.70 for that productivity measure [10]. These findings are useful because they suggest a plausible pathway through which hybrid tutoring may raise math learning: more engagement, more work completed, and more time on task. However, they do not establish the same level of causal confidence as a randomized comparison with a clean math-achievement outcome.

Peer tutoring offers another quasi-experimental signal, but it is mainly an affective one. In a middle-school experience with n=420, reciprocal peer tutoring reduced mathematics anxiety relative to classroom instruction/business-as-usual, with g=0.84 for learning anxiety and g=0.42 for evaluation anxiety [18]. Because the outcome is anxiety rather than achievement, this study should not be taken as direct evidence of math learning gains. It does, however, indicate that peer tutoring may improve the emotional conditions under which math learning takes place.

## Synthesis Evidence and Moderator Patterns

### Meta-analytic and review evidence

The meta-analysis of intelligent tutoring systems for K-12 students is the most directly relevant synthesis source in the pool. It asks whether ITS improve achievement in U.S. schools and under what conditions effects are strongest, and it explicitly evaluates heterogeneity by study quality and dimensions of external validity [1]. The summary indicates positive overall effects, but because the extracted source text does not provide a pooled coefficient in the pool, the key takeaway is qualitative: ITS benefit students on average, and effects vary with study characteristics [1]. This supports the general efficacy of adaptive tutoring while reinforcing the caution that implementation quality and study design matter.

The review of interventions to improve mathematical achievement in primary school-aged children also supports a positive but uneven evidence base. It synthesizes classroom-based mathematics interventions and asks which are effective and what characteristics are associated with better outcomes [6]. The source pool summary does not provide a single pooled effect, so the main use of this review is as corroborating evidence that primary math interventions, including tutoring-like supports, can raise achievement but vary substantially by format and context [6].

The scaffolding review is relevant to mechanisms. It examines a decade of research on scaffolding in teacher–student interaction and argues that scaffolding is often loosely defined, while its instructional logic involves contingent support rather than fixed assistance [21]. This matters for tutoring because many of the strongest intervention studies in the pool rely on immediate feedback, guided practice, and adaptive prompts rather than generic extra time alone [11]; [24].

### Mixed or indirect evidence on tutor type, format, and timing

The source pool does not support a single superior tutoring model across all K-8 contexts. Teacher-mediated digital support, AI tutor systems, peer tutoring, and hybrid models all show benefits on some outcomes, but the evidence is not directly comparable because the outcome measures, grade bands, and study designs differ. The kindergarten and early-elementary RCTs show strong to small effects for adaptive systems [12]; [2], while the middle-school quasi-experiment and peer tutoring study mainly show improvements in engagement or anxiety rather than achievement [10]; [18].

There is also not enough direct evidence to identify whether school-day, after-school, pull-out, or online tutoring is superior in K-8 math. The available studies include classroom-embedded AI supports, supplemental app use alongside classroom instruction, district-based tutoring sessions, and remote phone/SMS learning support, but none of these directly and cleanly compare schedule formats as a causal moderator in K-8 math [2]; [11]; [8]. As a result, claims about after-school versus school-day superiority remain unresolved in this source pool.

### Mechanisms and implementation features

The clearest mechanism across the evidence base is individualized feedback and scaffolding. Tutor CoPilot improved tutor use of high-quality strategies, suggesting that real-time guidance can change instruction in ways that immediately affect student performance [11]. The LearnLM experiment likewise found gains in remediation and misconception resolution, which are plausible downstream consequences of adaptive feedback and interactive questioning [22]. The MathSpring/Wayang Outpost paper is a mixed-methods study rather than an outcome RCT, but it is still useful because it explicitly frames tutoring as integrating cognition, metacognition, and affect, reinforcing the idea that effective math tutoring does more than supply answers [24].

Implementation quality is therefore central, but it is rarely isolated as a causal moderator. The meta-analysis of ITS explicitly evaluates heterogeneity, implying that effects differ by study quality and validity conditions [1]. Tutor CoPilot provides some of the best evidence that tutor support quality itself can be improved at scale, but it does not establish that every improvement in tutor talk produces proportional achievement gains [11]. The evidence base is stronger on the plausibility of mechanisms than on definitive tests of which mechanism is most important.

## Population and Equity Considerations

The source pool offers limited but suggestive evidence on subgroup differences. Tutor CoPilot reported subgroup effects up to 9 percentage points on exit tickets, but the extracted summary does not specify the subgroup definitions, so the exact equity pattern cannot be reconstructed from the source pool alone [11]. The Ghana AI tutor RCT is especially important for equity because it was implemented in a low-resource, LMIC context with grades 3–8 and still produced d=0.36 on math growth, suggesting that scalable tutoring can work outside high-resource U.S. settings [3]. The Botswanan low-tech remote instruction trial further indicates that structured low-tech support can raise numeracy in contexts where school disruption or limited infrastructure constrain tutoring access [8].

That said, subgroup evidence for students with disabilities, multilingual learners, rural students, or students below grade level is sparse in the retrieved pool. The meta-analytic ITS paper explicitly studies heterogeneity, but the available extraction does not provide enough subgroup detail to support strong claims about which K-8 populations benefit most [1]. The available studies therefore justify a cautious statement: tutoring appears promising across several settings, but equity conclusions remain underdeveloped.

## What the evidence says about outcomes beyond test scores

The most consistent direct outcome is general math achievement or numeracy, but there is some evidence of broader related outcomes. My Math Academy improved engagement, motivation, enjoyment, persistence, and confidence in teacher reports, while Native Numbers did not improve intrinsic motivation overall and did not show meaningful gains in mathematical language [2]; [12]. Reciprocal peer tutoring reduced math anxiety, especially learning anxiety, which may matter for sustained participation and willingness to engage with difficult content [18]. Tutor CoPilot and LearnLM also suggest gains in immediate performance and instructional process quality rather than long-term standardized outcomes [11]; [22].

What remains weak is evidence on long-term retention, course grades, standardized tests over time, and transfer to later algebra readiness. The source pool includes maintenance testing in Native Numbers, but the summary does not provide a robust long-term follow-up effect size beyond the first post-test result [12]. As a result, the durability of tutoring gains in K-8 math remains uncertain.

### Synthesis and Implications

The best-supported conclusion is that tutoring and tutoring-like supplemental supports generally improve K-8 math achievement and related outcomes, especially when they provide individualized feedback, structured practice, and real-time scaffolding. The strongest causal evidence comes from adaptive or AI-supported systems in kindergarten, early elementary, and grades 3–8, where RCTs report positive effects ranging from d=0.11 to d=1.48 and one larger study reports d=0.36 on growth [12]; [2]; [3]. School-based support for tutors themselves also appears promising, as Tutor CoPilot improved exit tickets by 4 percentage points and changed tutor behavior at scale [11].

For practice, the evidence suggests that schools should prioritize structured tutoring aligned with classroom content, delivered frequently enough to sustain engagement, and supported by rapid feedback loops for both students and tutors [1]; [11]; [24]. However, schools should not assume that any tutoring is automatically high-impact: the effect sizes are heterogeneous, and the evidence does not establish a universal winner between one-to-one, small-group, peer, or AI-assisted formats in K-8 math.

### Limitations and Research Gaps

The evidence base is limited by the small number of direct K-8 math tutoring RCTs and by substantial heterogeneity in intervention type, outcome measure, and grade band. Several of the strongest studies are not traditional human tutoring trials but intelligent tutoring, hybrid human-AI support, or adaptive software studies, which makes it difficult to isolate what human tutoring alone contributes [1]; [11].

Methodological weaknesses include small samples in some of the most informative studies, short durations, and the presence of quasi-experimental and descriptive designs that cannot establish causal effects as cleanly as RCTs [12]; [10]; [24]. Equity and subgroup evidence is also thin: the source pool does not provide robust, disaggregated estimates for ELs, students with disabilities, rural students, or specific low-prior-achievement strata, even though these are central to policy decisions [1].

## Bibliography

| # | Citation | Study Design | Quality | Impact |
|---|----------|--------------|---------|--------|
| 1 |  (n.d.). [Do intelligent tutoring systems benefit K-12 students? A meta-analysis and evaluation of heterogeneity of treatment effects in the U.S.](not_reported). | Meta-Analysis / Systematic Review | Blue | Blue |
| 2 |  (2023). [Efficacy of an Adaptive Game-Based Math Learning App to Support Personalized Learning and Improve Early Elementary School Students’ Learning](https://doi.org/10.1007/s10643-022-01332-3). | Randomized Controlled Trial (RCT) | Green | Green |
| 3 |  (n.d.). [Effective and Scalable Math Support: Experimental Evidence on the Impact of an AI-Math Tutor in Ghana](http://arxiv.org/abs/2402.09809v2). | Randomized Controlled Trial (RCT) | Blue | Blue |
| 6 |  (2019). [Interventions to improve mathematical achievement in primary school-aged children](https://pure.ulster.ac.uk/en/publications/interventions-to-improve-mathematical-achievement-in-primary-school-aged-children). | Meta-Analysis / Systematic Review | Green | Yellow |
| 8 |  (2022). [Experimental evidence on learning using low-tech when school is out](https://doi.org/10.1038/s41562-022-01381-z). | Randomized Controlled Trial (RCT) | Blue | Green |
| 10 |  (2024). [Improving Student Learning with Hybrid Human-AI Tutoring: A Three-Study Quasi-Experimental Investigation](https://doi.org/10.1145/3636555.3636896). | Quasi-Experimental Design (QED) | Green | Green |
| 11 |  (2025). [Tutor CoPilot: A Human-AI Approach for Scaling Real-Time Expertise](https://arxiv.org/abs/2410.03017). | Randomized Controlled Trial (RCT) | Blue | Green |
| 12 |  (2021). [Effectiveness of a Numeracy Intelligent Tutoring System in Kindergarten: A Conceptual Replication](https://doi.org/10.5964/jnc.6931). | Randomized Controlled Trial (RCT) | Green | Blue |
| 18 |  (2020). [Peer Tutoring Effects on Students’ Mathematics Anxiety: A Middle School Experience](https://doi.org/10.3389/fpsyg.2020.01610). | Quasi-Experimental Design (QED) | Green | Blue |
| 21 |  (2010). [Scaffolding in Teacher–Student Interaction: A Decade of Research](https://doi.org/10.1007/s10648-010-9127-6). | Meta-Analysis / Systematic Review | Green | Yellow |
| 22 |  (2025). [AI tutoring can safely and effectively support students: An exploratory RCT in UK classrooms](https://arxiv.org/abs/2512.23633v1). | Randomized Controlled Trial (RCT) | Green | Green |
| 24 |  (2014). [A Multimedia Adaptive Tutoring System for Mathematics that Addresses Cognition, Metacognition and Affect](https://doi.org/10.1007/s40593-014-0023-y). | Mixed-Methods | Yellow | Green |

## Body of Evidence Maturity: LIMITED
Justification: The evidence is promising and includes several RCTs plus a relevant meta-analysis, but it is not yet comprehensive for traditional K-8 math tutoring as a distinct intervention class. Coverage is uneven across grade bands, outcome domains, and equity groups, and many of the strongest effects come from AI-supported or adaptive tutoring systems rather than clean human-tutoring comparisons.