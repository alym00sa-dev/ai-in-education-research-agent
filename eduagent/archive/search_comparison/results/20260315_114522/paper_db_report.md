# Paper Database Comparison Report
Generated: 2026-03-15 11:45

## Databases Tested
- **OpenAlex** — 250M+ works, free, no key required
- **ERIC** — US Dept of Education, education-specific, free
- **Semantic Scholar** — AI2, 225M+ papers, AI-powered, free

## Queries Tested
1. effect size of retrieval practice on long-term retention in K-12 students
2. AI tutoring systems versus human tutoring academic outcomes meta-analysis
3. socioeconomic achievement gap interventions evidence randomized controlled trial

## Results by Query

### Query: *AI tutoring systems versus human tutoring academic outcomes meta-analysis*

| DB | Results | Latency (s) | Academic % | Avg Snippet | Relevance | Source Quality | Snippet Usefulness | Notes |
|----|---------|-------------|------------|-------------|-----------|----------------|--------------------|-------|
| eric | 10 | 2.93 | 100% | 500 chars | 4 | 5 | 3 | Most results focus on AI/ITS effectiveness but lack direct comparisons to human tutoring as specified in the query. Sour |
| openalex | 10 | 1.38 | 100% | 274 chars | 2 | 4 | 2 | Results focus on AI in education generally but lack direct comparison studies between AI and human tutoring, or meta-ana |
| semantic_scholar | 0 | 2.68 | 0% | 0 chars | 0 | 0 | 0 | ⚠ Client error '429 ' for url 'https://api.semanticscholar.org/graph/v1/paper/search?query=AI+tutoring+systems+versus+hu |

<details><summary>eric — top results</summary>

- **Supporting 2e Bilingual Students with Motor Dysgraphia and ADHD in Writing: Efficacy and Acceptability of Human-AI Hybrid Tutoring [2025, Journal of Advanced Academics, Peer-reviewed]**
  http://dx.doi.org/10.1177/1932202X251348549
  > This study examined the efficacy and acceptability of human-artificial intelligence (AI) hybrid tutoring in improving the writing skills of twice exceptional (2e) bilingual students with motor dysgraphia and attention-deficit hyperactivity disorder (ADHD) by employing an explanatory sequential desig

- **A Meta-Analysis of the Effectiveness of Intelligent Tutoring Systems on College Students' Academic Learning [2014, Journal of Educational Psychology, Peer-reviewed, Higher Education, Postsecondary Education]**
  http://dx.doi.org/10.1037/a0034752
  > This meta-analysis synthesizes research on the effectiveness of intelligent tutoring systems (ITS) for college students. Thirty-five reports were found containing 39 studies assessing the effectiveness of 22 types of ITS in higher education settings. Most frequently studied were AutoTutor, Assessmen

- **Defining and Classifying the Roles of Intelligent Learning Companion Systems: A Scoping Review of the Literature [2025, TechTrends: Linking Research and Practice to Improve Learning, Peer-reviewed]**
  http://dx.doi.org/10.1007/s11528-025-01058-0
  > This scoping review investigates the roles of intelligent learning companion systems (LCS) within educational settings, as well as the presences artificial intelligence (AI) embodies within these roles, and their application in education. Employing the PRISMA (Preferred Reporting Items for Systemati

- **Exploring the Impact of Artificial Intelligence in Advancing Smart Learning in Education: A Meta-Analysis with Statistical Evidence [2025, Open Praxis, Peer-reviewed, Elementary Secondary Education, Postsecondary Education]**
  https://eric.ed.gov/?id=EJ1481274
  > This meta-analysis examines the diverse effects of artificial intelligence (AI), notably ChatGPT, on intelligent learning in the education industry over the last four years. Despite the rapid integration into education of AI tools such as ChatGPT, which have the potential to enhance personalized lea

- **Intelligent Tutoring Systems and Learning Outcomes: A Meta-Analysis [2014, Journal of Educational Psychology, Peer-reviewed]**
  http://dx.doi.org/10.1037/a0037123
  > Intelligent Tutoring Systems (ITS) are computer programs that model learners&apos; psychological states to provide individualized instruction. They have been developed for diverse subject areas (e.g., algebra, medicine, law, reading) to help learners acquire domain-specific, cognitive and metacognit

</details>

<details><summary>openalex — top results</summary>

- **Opinion Paper: “So what if ChatGPT wrote it?” Multidisciplinary perspectives on opportunities, challenges and implications of generative conversational AI for research, practice and policy [2023] Cited by 3309**
  https://doi.org/10.1016/j.ijinfomgt.2023.102642

- **The Knowledge‐Learning‐Instruction Framework: Bridging the Science‐Practice Chasm to Enhance Robust Student Learning [2012] Cited by 691**
  https://doi.org/10.1111/j.1551-6709.2012.01245.x
  > Despite the accumulation of substantial cognitive science research relevant to education, there remains confusion and controversy in the application of research to educational practice. In support of a more systematic approach, we describe the Knowledge-Learning-Instruction (KLI) framework. KLI prom

- **School Readiness and Self-Regulation: A Developmental Psychobiological Approach [2014] Cited by 1115**
  https://doi.org/10.1146/annurev-psych-010814-015221
  > Research on the development of self-regulation in young children provides a unifying framework for the study of school readiness. Self-regulation abilities allow for engagement in learning activities and provide the foundation for adjustment to school. A focus on readiness as self-regulation does no

- **AI-generated feedback on writing: insights into efficacy and ENL student preference [2023] Cited by 366**
  https://doi.org/10.1186/s41239-023-00425-2
  > Abstract The question of how generative AI tools, such as large language models and chatbots, can be leveraged ethically and effectively in education is ongoing. Given the critical role that writing plays in learning and assessment within educational institutions, it is of growing importance for edu

- **Effectiveness of problem-based learning methodology in undergraduate medical education: a scoping review [2022] Cited by 416**
  https://doi.org/10.1186/s12909-022-03154-8
  > PBL is an effective and satisfactory methodology for medical education. It is likely that through PBL medical students will not only acquire knowledge but also other competencies that are needed in medical professionalism.

</details>

### Query: *socioeconomic achievement gap interventions evidence randomized controlled trial*

| DB | Results | Latency (s) | Academic % | Avg Snippet | Relevance | Source Quality | Snippet Usefulness | Notes |
|----|---------|-------------|------------|-------------|-----------|----------------|--------------------|-------|
| eric | 10 | 2.88 | 100% | 500 chars | 4 | 5 | 2 | Results strongly align with the query's focus on socioeconomic achievement gaps, interventions, and RCT evidence (result |
| openalex | 10 | 1.73 | 100% | 223 chars | 1 | 5 | 2 | The results are almost entirely off-topic, containing mostly medical/health guidelines and epidemiological studies unrel |
| semantic_scholar | 10 | 5.06 | 100% | 318 chars | 2 | 5 | 3 | While all results are from high-quality peer-reviewed journals and many are RCTs, only result #9 directly addresses the  |

<details><summary>eric — top results</summary>

- **Effects of Simulated Interventions to Improve School Entry Academic Skills on Socioeconomic Inequalities in Educational Achievement [2014, Child Development, Peer-reviewed]**
  http://dx.doi.org/10.1111/cdev.12309
  > Randomized controlled trial evidence shows that interventions before age 5 can improve skills necessary for educational success; the effect of these interventions on socioeconomic inequalities is unknown. Using trial effect estimates, and marginal structural models with data from the Avon Longitudin

- **Four-Year Degree and Employment Findings from a Randomized Controlled Trial of a One-Year Performance-Based Scholarship Program in Ohio [2016, Journal of Research on Educational Effectiveness, Peer-reviewed, Two Year Colleges, Higher Education, Postsecondary Education]**
  http://dx.doi.org/10.1080/19345747.2015.1086914
  > A college degree is often viewed as a key step toward better employment and higher earnings. Many community college students, however, never graduate and cannot reap the financial benefits associated with a college degree. Although existing research suggests that financial aid interventions can mode

- **WWC Review of the Report &quot;Closing the Achievement Gap through Modification of Neurocognitive and Neuroendocrine Function: Results from a Cluster Randomized Controlled Trial of an Innovative Approach to the Education of Children in Kindergarten.&quot; What Works Clearinghouse Single Study Review [2015, What Works Clearinghouse, Peer-reviewed, Kindergarten, Primary Education, Early Childhood Education]**
  https://eric.ed.gov/?id=ED561258
  > In the 2014 report, &quot;Closing the Achievement Gap Through Modification of Neurocognitive and Neuroendocrine Function: Results from a Cluster Randomized Controlled Trial of an Innovative Approach to the Education of Children in Kindergarten,&quot; researchers examined the impacts of &quot;Tools o

- **The Impact of Interactive Shared Book Reading on Children&apos;s Language Skills: A Randomized Controlled Trial [2020, Journal of Speech, Language, and Hearing Research, Peer-reviewed]**
  https://doi.org/10.1044/2020_JSLHR-19-00288
  > Purpose: Research has indicated that interactive shared book reading can support a wide range of early language skills and that children who are read to regularly in the early years learn language faster, enter school with a larger vocabulary, and become more successful readers at school. Despite th

- **Evidence Summary for the Promise Academy Charter Middle School in Harlem Children's Zone. Top Tier Evidence Initiative [2010, Coalition for Evidence-Based Policy, Middle Schools, Secondary Education, Junior High Schools]**
  https://eric.ed.gov/?id=ED572711
  > U.S. social programs, set up to address important problems, often fall short by funding specific models/strategies (&quot;interventions&quot;) that are not effective. When evaluated in scientifically-rigorous studies, social interventions in K-12 education, job training, crime prevention, and other 

</details>

<details><summary>openalex — top results</summary>

- **Breastfeeding in the 21st century: epidemiology, mechanisms, and lifelong effect [2016] Cited by 7765**
  https://doi.org/10.1016/s0140-6736(15)01024-7

- **A new framework for developing and evaluating complex interventions: update of Medical Research Council guidance [2021] Cited by 5502**
  https://doi.org/10.1136/bmj.n2061
  > The UK Medical Research Council’s widely used guidance for developing and evaluating complex interventions has been replaced by a new framework, commissioned jointly by the Medical Research Council and the National Institute for Health Research, which takes account of recent developments in theory a

- **2018 ESC/ESH Guidelines for the management of arterial hypertension [2018] Cited by 10223**
  https://doi.org/10.1093/eurheartj/ehy339
  > The ESC/ESH Guidelines represent the views of the ESC and ESH and were produced after careful consideration of the scientific and medical knowledge and the evidence available at the time of their dating. The ESC and ESH are not responsible in the event of any contradiction, discrepancy, and/or ambig

- **Contribution of Primary Care to Health Systems and Health [2005] Cited by 5417**
  https://doi.org/10.1111/j.1468-0009.2005.00409.x
  > Evidence of the health-promoting influence of primary care has been accumulating ever since researchers have been able to distinguish primary care from other aspects of the health services delivery system. This evidence shows that primary care helps prevent illness and death, regardless of whether t

- **2021 ESC Guidelines on cardiovascular disease prevention in clinical practice [2021] Cited by 5882**
  https://doi.org/10.1093/eurheartj/ehab484
  > The ESC Guidelines represent the views of the ESC and were produced after careful consideration of the scientific and medical knowledge and the evidence available at the time of their publication. The ESC is not responsible in the event of any contradiction, discrepancy and/or ambiguity between the 

</details>

<details><summary>semantic_scholar — top results</summary>

- **Insights from a randomized controlled trial of flipped classroom on academic achievement: the challenge of student resistance [2023] Cited by 8**
  https://doi.org/10.1186/s41239-023-00413-6
  > Flipped classroom has been found to positively influence student achievement but the magnitude of the effect varies greatly according to discipline and local design, and few studies have been methodologically rigorous enough to establish causal evidence. Using a randomized controlled trial, this stu

- **Applying a mobile intervention for chronic insomnia in routine care: Study protocol for a multicenter randomized controlled trial [2025] Cited by 1 | Internet Interventions**
  https://doi.org/10.1016/j.invent.2025.100848
  > This study aims to examine the effectiveness of a mobile dCBT-I intervention, “SleepQ,” in a routine clinical setting and contribute to the evaluation of the clinical implementation of digital therapeutics for insomnia and inform the integration of mobile-based CBT-I into routine care.

- **Bridging the evidence-to-practice gap: a stepped-wedge cluster randomized controlled trial evaluating practice facilitation as a strategy to accelerate translation of a multi-level adherence intervention into safety net practices [2021] Cited by 13 | Implementation Science Communications**
  https://doi.org/10.1186/s43058-021-00111-2
  > This study evaluates the effectiveness of practice facilitation (PF) as a practical and tailored strategy for implementing Advancing Medication Adherence for Latinos with Hypertension through a Team-based Care Approach (ALTA), a multi-level approach to improving medication adherence and BP control i

- **Effectiveness of Topic-Based Chatbots on Mental Health Self-Care and Mental Well-Being: Randomized Controlled Trial [2024] Cited by 12 | Journal of Medical Internet Research**
  https://doi.org/10.2196/70436
  > A rule-based, topic-specific chatbot intervention in improving self-care efficacy, mental health literacy, self-care intention, self-care behaviors, and mental well-being immediately after 10 days and 1 month of its use is evaluated.

- **The Behavioral Education in Social Media (BE-Social) Program for Postgraduate Academic Achievement: A Randomized Controlled Trial [2024] Cited by 4 | Journal of Behavioral Education**
  https://doi.org/10.1007/s10864-024-09545-9
  > Few randomized controlled trials have evaluated social media study groups as educational aids in the context of online and blended teaching programs. We present the Behavioral Education in Social Media (BE-Social) intervention package, which integrates key evidence-informed behavioral intervention s

</details>

### Query: *effect size of retrieval practice on long-term retention in K-12 students*

| DB | Results | Latency (s) | Academic % | Avg Snippet | Relevance | Source Quality | Snippet Usefulness | Notes |
|----|---------|-------------|------------|-------------|-----------|----------------|--------------------|-------|
| eric | 10 | 3.06 | 100% | 500 chars | 4 | 5 | 3 | Results strongly address retrieval practice and long-term retention with multiple K-12 studies (preschool, middle school |
| openalex | 10 | 1.74 | 100% | 250 chars | 2 | 5 | 2 | The search returned peer-reviewed academic sources of high quality, but most results are tangentially related to retriev |
| semantic_scholar | 0 | 2.88 | 0% | 0 chars | 0 | 0 | 0 | Error or no results: empty |

<details><summary>eric — top results</summary>

- **Expanding Retrieval Practice Promotes Short-Term Retention, but Equally Spaced Retrieval Enhances Long-Term Retention [2007, Journal of Experimental Psychology: Learning, Memory, and Cognition, Peer-reviewed]**
  http://content2.apa.org/journals/xlm/33/4/704
  > Expanding retrieval practice (T. K. Landauer &amp; R. A. Bjork, 1978) is regarded as a superior technique for promoting long-term retention relative to equally spaced retrieval practice. In Experiments 1 and 2, the authors found that expanding retrieval practice of vocabulary word pairs produced sho

- **Retrieval Practice: Beneficial for All Students or Moderated by Individual Differences? [2021, Psychology Learning and Teaching, Peer-reviewed, Secondary Education]**
  http://dx.doi.org/10.1177/1475725720973494
  > Retrieval practice is a learning technique that is known to produce enhanced long-term memory retention when compared to several other techniques. This difference in learning outcome is commonly called &quot;the testing effect&quot;. Yet there is little research on how individual differences in pers

- **When Does Retrieval Induce Forgetting and when Does It Induce Facilitation? Implications for Retrieval Inhibition, Testing Effect, and Text Processing [2009, Journal of Memory and Language, Peer-reviewed]**
  http://dx.doi.org/10.1016/j.jml.2009.04.004
  > Retrieval practice can enhance long-term retention of the tested material (the testing effect), but it can also impair later recall of the nontested material--a phenomenon known as retrieval-induced forgetting (Anderson, M. C., Bjork, R. A., & Bjork, E. L. (1994). "Remembering can cause forgetting: 

- **Multiple Practice Success Scaffolds Long-Term Test-Enhanced Learning in Preschoolers [2025, Child Development, Peer-reviewed, Early Childhood Education, Preschool Education]**
  http://dx.doi.org/10.1111/cdev.70018
  > Retrieval practice is known to enhance long-term memory retention, a phenomenon termed as retrieval practice effect. Two experiments (NWhite = 202), showed that the effect was present in preschool age (5-6 years) and had a boundary condition, namely, amount of initial learning. Specifically, there w

- **Is Covert Retrieval an Effective Learning Strategy? Is It as Effective as Overt Retrieval? Answers from a Meta-Analytic Review [2025, Educational Psychology Review, Peer-reviewed]**
  http://dx.doi.org/10.1007/s10648-025-10024-4
  > Retrieval practice is well-established as a powerful tool for reinforcing long-term learning. Most previous research has concentrated on the effectiveness of overt retrieval, involving recalling information from memory and generating overt responses by writing, typing, or speaking aloud the retrieve

</details>

<details><summary>openalex — top results</summary>

- **The magical number 4 in short-term memory: A reconsideration of mental storage capacity [2001] Cited by 6691**
  https://doi.org/10.1017/s0140525x01003922
  > Miller (1956) summarized evidence that people can remember about seven chunks in short-term memory (STM) tasks. However, that number was meant more as a rough estimate and a rhetorical device than as a real capacity limit. Others have since suggested that there is a more precise capacity limit, but 

- **Multidisciplinary research priorities for the COVID-19 pandemic: a call for action for mental health science [2020] Cited by 6012**
  https://doi.org/10.1016/s2215-0366(20)30168-1

- **Working memory span tasks: A methodological review and user’s guide [2005] Cited by 2830**
  https://doi.org/10.3758/bf03196772

- **Effects of problem-based learning: a meta-analysis [2003] Cited by 1667**
  https://doi.org/10.1016/s0959-4752(02)00025-7

- **Progress in information technology and tourism management: 20 years on and 10 years after the Internet—The state of eTourism research [2008] Cited by 3606**
  https://doi.org/10.1016/j.tourman.2008.01.005

</details>

## Aggregate Summary

| DB | Avg Relevance | Avg Source Quality | Avg Snippet Usefulness | Avg Latency (s) | Avg Academic % |
|----|---------------|--------------------|------------------------|-----------------|----------------|
| eric | 4.0 | 5.0 | 2.67 | 2.96 | 100% |
| openalex | 1.67 | 4.67 | 2.0 | 1.62 | 100% |
| semantic_scholar | 0.67 | 1.67 | 1.0 | 3.54 | 33% |
