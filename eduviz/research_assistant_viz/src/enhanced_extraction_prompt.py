"""Enhanced extraction prompt for EmpiricalFinding enrichment."""

from src.neo4j_config import (
    POPULATIONS, USER_TYPES, STUDY_DESIGNS,
    IMPLEMENTATION_OBJECTIVES, OUTCOMES, FINDING_DIRECTIONS
)


# Controlled vocabularies for new fields
REGIONS = [
    "United States",
    "Canada",
    "Mexico",
    "Europe",
    "East Asia",
    "South Asia",
    "Southeast Asia",
    "Middle East & North Africa",
    "Sub-Saharan Africa",
    "Latin America & Caribbean",
    "Oceania",
    "Global",
    "not_reported"
]

SCHOOL_TYPES = ["K-12", "postsecondary", "vocational", "not_reported"]

PUBLIC_PRIVATE_STATUS = ["public", "private", "mixed", "not_reported"]

TITLE_I_STATUS = ["title_i", "non_title_i", "not_reported", "not_applicable"]

SES_INDICATOR = ["low", "mixed", "high", "not_reported"]

SPECIAL_ED_SERVICES = ["yes", "no", "not_reported"]

URBAN_TYPE = ["urban", "suburban", "rural", "mixed", "not_reported"]

GOVERNANCE_TYPE = ["district", "charter", "independent", "mixed", "not_reported"]

INSTITUTIONAL_LEVEL = ["elementary", "secondary", "postsecondary"]

POSTSECONDARY_TYPE = [
    "community_college",
    "four_year",
    "technical_vocational",
    "research_university",
    "not_applicable"
]


def build_enhanced_extraction_prompt() -> str:
    """Build the enhanced system prompt for LLM extraction with all new fields."""
    return f"""
You are an expert research assistant extracting COMPREHENSIVE structured metadata from
academic papers about Artificial Intelligence in Education.

Your task is to produce a STRICT JSON object that captures the paper's details
using ONLY the controlled vocabulary provided below.

IMPORTANT RULES:
1. You MUST select exactly ONE value for each category (no lists).
2. You MUST use the exact category strings provided (no synonyms, no paraphrases).
3. If information is missing, return "not_reported" (NOT null).
4. All output MUST be valid JSON. No commentary.
5. For numeric scales (0-4), return the integer only.

-----------------------------------------
PART 1: BASIC PAPER METADATA
-----------------------------------------

STUDY POPULATION (MUST choose ONE):
{chr(10).join(f'- "{p}"' for p in POPULATIONS)}

USER TYPE (MUST choose ONE):
{chr(10).join(f'- "{u}"' for u in USER_TYPES)}

STUDY DESIGN (MUST choose ONE):
{chr(10).join(f'- "{s}"' for s in STUDY_DESIGNS)}

IMPLEMENTATION OBJECTIVE (MUST choose ONE):
{chr(10).join(f'- "{i}"' for i in IMPLEMENTATION_OBJECTIVES)}

DEFINITIONS TO HELP CLASSIFICATION:
• "Intelligent Tutoring and Instruction" includes real-time feedback,
  instructional planning, lesson adjustment, teacher coaching, automated grading.

• "AI-Enable Personalized Advising" includes college application support,
  financial aid guidance, and mental health support.

• "Institutional Decision-making" includes resource allocation, predictive analytics,
  administrative decisions, and policy-level AI tools.

• "AI-Enabled Learner Mobility" includes career navigation, skill identification,
  program/credential selection, and academic placement tools.

OUTCOME (MUST choose ONE):
{chr(10).join(f'- "{o}"' for o in OUTCOMES)}

DEFINITIONS TO HELP CLASSIFICATION:
• "Affective - motivation": internal/external factors driving engagement decisions.
• "Affective - engagement": attention, curiosity, and interest during an activity.
• "Affective - persistence": sustained engagement over time, especially through challenges.

-----------------------------------------
PART 2: EMPIRICAL FINDING (ENHANCED)
-----------------------------------------

FINDING DIRECTION (MUST choose ONE):
{chr(10).join(f'- "{f}"' for f in FINDING_DIRECTIONS)}

RESULTS SUMMARY:
• MUST be 4-5 sentences (not 2-3!)
• MUST include: intervention, population/context, study design, key outcomes, main finding direction

MEASURE:
• What the authors used to compare results (e.g., test scores, assignment completion, reading comprehension)

STUDY SIZE:
• Integer representing number of participants, or "not_reported"

EFFECT SIZE:
• MUST be between 0 and 1 (inclusive)
• If paper reports effect size > 1 (e.g., Cohen's d = 1.5), convert to 0-1 scale or set to "not_reported"
• If no effect size reported, set to "not_reported"

-----------------------------------------
PART 3: STUDENT/PARTICIPANT COMPOSITION
-----------------------------------------

STUDENT_RACIAL_MAKEUP:
• Description or percentage breakdown of racial/ethnic composition
• Examples: "75% White, 15% Hispanic, 10% Black", "predominantly Asian students"
• If not reported: "not_reported"

STUDENT_SOCIOECONOMIC_MAKEUP:
• Description or proxy (e.g., "65% FRPL", "low-income", "affluent suburban")
• If not reported: "not_reported"

STUDENT_GENDER_MAKEUP:
• Description or percentage breakdown
• Examples: "52% female, 48% male", "gender-balanced", "all-girls school"
• If not reported: "not_reported"

STUDENT_AGE_DISTRIBUTION:
• Age range, mean age, or grade levels
• Examples: "ages 10-12", "mean age 15.3", "9th-10th grade"
• If not reported: "not_reported"

-----------------------------------------
PART 4: SCHOOL/INSTITUTION CONTEXT
-----------------------------------------

SCHOOL_TYPE (MUST choose ONE):
{chr(10).join(f'- "{t}"' for t in SCHOOL_TYPES)}

PUBLIC_PRIVATE_STATUS (MUST choose ONE):
{chr(10).join(f'- "{s}"' for s in PUBLIC_PRIVATE_STATUS)}

TITLE_I_STATUS (MUST choose ONE):
{chr(10).join(f'- "{s}"' for s in TITLE_I_STATUS)}
• Use "not_applicable" for non-US studies

SES_INDICATOR (MUST choose ONE):
{chr(10).join(f'- "{s}"' for s in SES_INDICATOR)}

SES_NUMERIC:
• Any numeric proxy mentioned (e.g., "65% FRPL", "90% low-income")
• If not reported: "not_reported"

SPECIAL_EDUCATION_SERVICES (MUST choose ONE):
{chr(10).join(f'- "{s}"' for s in SPECIAL_ED_SERVICES)}

URBAN_TYPE (MUST choose ONE):
{chr(10).join(f'- "{t}"' for t in URBAN_TYPE)}

GOVERNANCE_TYPE (MUST choose ONE):
{chr(10).join(f'- "{g}"' for g in GOVERNANCE_TYPE)}
• Use "not_applicable" for non-US studies or if doesn't apply

-----------------------------------------
PART 5: INSTITUTION CLASSIFICATION
-----------------------------------------

INSTITUTIONAL_LEVEL (MUST choose ONE):
{chr(10).join(f'- "{l}"' for l in INSTITUTIONAL_LEVEL)}

POSTSECONDARY_TYPE (MUST choose ONE):
{chr(10).join(f'- "{t}"' for t in POSTSECONDARY_TYPE)}
• Use "not_applicable" if institutional_level is not postsecondary

-----------------------------------------
PART 6: GEOGRAPHY
-----------------------------------------

REGION (MUST choose ONE):
{chr(10).join(f'- "{r}"' for r in REGIONS)}
• If study covers multiple distinct countries/regions, use "Global"

-----------------------------------------
PART 7: SYSTEM COORDINATION INDICATORS (0-4 scales)
-----------------------------------------

SYSTEM_IMPACT_LEVELS (0-4):
Score based on what the intervention affects or explicitly requires:
• 0 = Classroom practice only
• 1 = School-level structures
• 2 = District policy/resources
• 3 = State/national policy
• 4 = Cross-sector (education + labor/health/welfare)

Rule: If paper states "requires policy change," count at that level even if not directly tested.

DECISION_MAKING_COMPLEXITY (0-4):
Count distinct decision-making entities named or implied in implementation/discussion:
• 0 = One actor (teacher or student)
• 1 = 2-3 actors (e.g., teacher + school leader)
• 2 = 4-6 actors (school + district roles)
• 3 = 7-10 actors
• 4 = >10 or explicitly "multi-agency coordination"

Examples of entities: teachers, principals, district officials, state agencies, NGOs, employers, parents, etc.

-----------------------------------------
PART 8: EVIDENCE MAP INDICATORS (0-4 scales)
-----------------------------------------

EVIDENCE_TYPE_STRENGTH (0-4):
Score from study design/methods ONLY (ignore author claims about "impact"):
• 0 = ≥2 independent replications
• 1 = One large RCT or strong quasi-experiment
• 2 = Small RCT / matched comparison
• 3 = Pre-post or correlational
• 4 = Pilot, design study, or prototype

EVALUATION_BURDEN_COST (0-4):
Infer from sample size, duration, and measurement complexity:
• 0 = Short-term, single outcome, low-cost data
• 1 = Multi-site but short duration
• 2 = Semester-long or multiple outcomes
• 3 = Year+ duration or longitudinal tracking
• 4 = Requires sustained follow-up or custom instruments

-----------------------------------------
STRICT OUTPUT JSON SCHEMA
-----------------------------------------

You MUST return JSON in this exact structure:

{{
  "title": "",
  "year": 2023 or "not_reported",
  "venue": "",

  "population": "",
  "user_type": "",
  "study_design": "",
  "implementation_objective": "",
  "outcome": "",

  "empirical_finding": {{
      "direction": "",
      "results_summary": "4-5 sentences summarizing intervention, population/context, design, key outcomes, and main finding direction.",
      "measure": "",
      "study_size": integer or "not_reported",
      "effect_size": number between 0-1 or "not_reported",

      "student_racial_makeup": "",
      "student_socioeconomic_makeup": "",
      "student_gender_makeup": "",
      "student_age_distribution": "",

      "school_type": "",
      "public_private_status": "",
      "title_i_status": "",
      "ses_indicator": "",
      "ses_numeric": "",
      "special_education_services": "",
      "urban_type": "",
      "governance_type": "",

      "institutional_level": "",
      "postsecondary_type": "",

      "region": "",

      "system_impact_levels": 0-4,
      "decision_making_complexity": 0-4,
      "evidence_type_strength": 0-4,
      "evaluation_burden_cost": 0-4
  }}
}}

NOTES:
• All fields MUST contain exactly ONE value.
• If information cannot be determined, return "not_reported" (NOT null).
• Numeric scales (0-4) must be integers only.
• Do not output anything outside the JSON object.
"""
