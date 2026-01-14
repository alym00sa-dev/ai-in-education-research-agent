Next steps: re-screen and enrich EmpiricalFinding nodes in Neo4j
Goal

Run a pass over all papers already ingested in Neo4j and update each paper’s EmpiricalFinding node(s) with additional context + quality controls, following the extraction guidelines below. Also update the extraction schema so new papers get these fields by default.

Scope

Iterate over every paper currently represented in Neo4j.

For each paper, read the full text (or stored PDF/text) and update its linked EmpiricalFinding node(s).

Some properties may already exist; do not overwrite non-null values unless the new value is clearly more complete/correct (log changes).

A) Add / populate context properties on EmpiricalFinding

Populate these fields when the paper provides the information. If not reported, set to "not_reported" (or null, depending on our convention).

Student / participant composition

student_racial_makeup — description or % breakdown of racial/ethnic composition

student_socioeconomic_makeup — description or proxy (e.g., FRPL%, low-income share)

student_gender_makeup — description or % breakdown

student_age_distribution — age range / mean / grade levels

School / institution context

school_type — one of: K–12, postsecondary, vocational

public_private_status — public, private, mixed, not_reported

title_i_status — true/false or tiered classification if the paper uses one

ses_indicator — low, mixed, high, or numeric proxy (e.g., % low-income)

special_education_services — yes/no plus capacity if stated

urban_type — urban, suburban, rural, mixed, not_reported

governance_type — district, charter, independent, mixed, not_reported

Institution classification

institutional_level — elementary, secondary, postsecondary

postsecondary_type — community_college, four_year, technical_vocational, research_university, not_applicable

Geography

region — e.g., US, South Asia, etc. If multiple distinct regions/countries are included, use global.

B) QA pass on existing extracted fields
Effect sizes

Review effect_size extractions.

Constraint: effect sizes must be between 0 and 1 (inclusive) for our normalized representation.

If the paper reports an effect size on another scale (e.g., Cohen’s d > 1), either:

convert to our normalized scale if our guidelines specify a conversion, or

store original value separately (e.g., effect_size_raw) and set effect_size to null with a note.

Flag any violations in a log (effect_size_out_of_range: true).

Summaries

Current summaries are too short. Update each paper’s summary to be 4–5 sentences.

Summary must include: intervention, population/context, design, key outcomes, and main finding direction.

C) Add three new “system/coordination/evidence” indicators
1) system_impact_levels (0–4)

Assign based on what the intervention affects or explicitly requires.

0 = Classroom practice only

1 = School-level structures

2 = District policy/resources

3 = State/national policy

4 = Cross-sector (education + labor/health/welfare)

Rule: If the paper states “requires policy change,” it counts at that level even if not directly tested.

2) decision_making_complexity (0–4)

(You called it “decision_making_?": this is a clean name suggestion.)

How to score:

Count distinct decision-making entities named or implied in implementation/discussion (e.g., teachers, principals, district officials, state agencies, NGOs, employers, etc.)

Scale:

0 = One actor (teacher or student)

1 = 2–3 actors (e.g., teacher + school leader)

2 = 4–6 actors (school + district roles)

3 = 7–10 actors

4 = >10 or explicitly “multi-agency coordination”

3) Evidence map indicators

evidence_type_strength (0–4) — score from methods only

0 = ≥2 independent replications

1 = One large RCT or strong quasi-experiment

2 = Small RCT / matched comparison

3 = Pre–post or correlational

4 = Pilot, design study, or prototype

Rule: Ignore author claims about “impact.” Score the design.

evaluation_burden_cost (0–4) — infer from sample size, duration, and measures

0 = Short-term, single outcome, low-cost data

1 = Multi-site but short duration

2 = Semester-long or multiple outcomes

3 = Year+ duration or longitudinal tracking

4 = Requires sustained follow-up or custom instruments

D) Script / agent behavior requirements

For each updated EmpiricalFinding:

Store a source_snippets or evidence_notes field with short supporting quotes/locations (methods / participants / setting).

Store extraction_confidence (high/medium/low) for the new indicators.

Log every update: paper_id, finding_id, fields changed, old→new value, and any QA flags.

E) Update extraction schema for new papers

After backfilling, update the extraction schema/prompt so all future ingests:

extract the new context fields,

enforce effect size constraints,

generate 4–5 sentence summaries,

compute the three indicators using the rubrics above.