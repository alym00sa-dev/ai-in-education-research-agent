# Knowledge Graph Schema

## Node Types

### Paper
- `paper_id`: Unique identifier (e.g., "paper_123")
- `title`: Paper title
- `year`: Publication year
- `venue`: Publication venue
- `url`: Paper URL
- `session_id`: Research session that added this paper
- `added_date`: When added to knowledge graph
- `population`: Target population (e.g., "Elementary (PreK-5th)") - **PROPERTY**
- `user_type`: User type studied (e.g., "Student") - **PROPERTY**
- `study_design`: Research methodology (e.g., "Randomized Control Trial") - **PROPERTY**

### EmpiricalFinding
**Core Finding Data:**
- `finding_id`: Unique identifier
- `direction`: "Positive", "Negative", "No Effect", "Mixed"
- `results_summary`: 4-5 sentence summary (intervention, population/context, design, outcomes, finding direction)
- `measure`: What was measured (test scores, completion rates, etc.)
- `study_size`: Number of participants or "not_reported"
- `effect_size`: Statistical effect size (0-1 scale) or "not_reported"

**Student/Participant Composition:**
- `student_racial_makeup`: Racial/ethnic composition (free text or "not_reported")
- `student_socioeconomic_makeup`: SES description (free text or "not_reported")
- `student_gender_makeup`: Gender breakdown (free text or "not_reported")
- `student_age_distribution`: Age range/mean/grade levels (free text or "not_reported")

**School/Institution Context:**
- `school_type`: "K-12" | "postsecondary" | "vocational" | "not_reported"
- `public_private_status`: "public" | "private" | "mixed" | "not_reported"
- `title_i_status`: "title_i" | "non_title_i" | "not_reported" | "not_applicable"
- `ses_indicator`: "low" | "mixed" | "high" | "not_reported"
- `ses_numeric`: Numeric SES proxy (e.g., "65% FRPL") or "not_reported"
- `special_education_services`: "yes" | "no" | "not_reported"
- `urban_type`: "urban" | "suburban" | "rural" | "mixed" | "not_reported"
- `governance_type`: "district" | "charter" | "independent" | "mixed" | "not_reported"

**Institution Classification:**
- `institutional_level`: "elementary" | "secondary" | "postsecondary"
- `postsecondary_type`: "community_college" | "four_year" | "technical_vocational" | "research_university" | "not_applicable"

**Geography:**
- `region`: "United States" | "Canada" | "Mexico" | "Europe" | "East Asia" | "South Asia" | "Southeast Asia" | "Middle East & North Africa" | "Sub-Saharan Africa" | "Latin America & Caribbean" | "Oceania" | "Global" | "not_reported"

**System Coordination Indicators (0-4 scales, -1 = not_reported):**
- `system_impact_levels`: 0 (classroom only) to 4 (cross-sector)
- `decision_making_complexity`: 0 (one actor) to 4 (>10 actors or multi-agency)

**Evidence Map Indicators (0-4 scales, -1 = not_reported):**
- `evidence_type_strength`: 0 (≥2 replications) to 4 (pilot/prototype)
- `evaluation_burden_cost`: 0 (short-term, single outcome) to 4 (sustained follow-up/custom instruments)

### Population (Legacy - Deprecated)
**NOTE**: Population is now stored as a **property** on Paper nodes, not as separate nodes.
Legacy nodes may still exist in database but are not used for new papers.

Controlled vocabulary:
  - Elementary (PreK-5th)
  - Middle School (6th-8th)
  - High School (9th-12th)
  - Undergraduate
  - Graduate
  - Adult

### UserType (Legacy - Deprecated)
**NOTE**: UserType is now stored as a **property** on Paper nodes, not as separate nodes.
Legacy nodes may still exist in database but are not used for new papers.

Controlled vocabulary:
  - Student
  - Educator
  - Administrator
  - Parent
  - School
  - Community
  - Systematic: social/political level information

### StudyDesign (Legacy - Deprecated)
**NOTE**: StudyDesign is now stored as a **property** on Paper nodes, not as separate nodes.
Legacy nodes may still exist in database but are not used for new papers.

Controlled vocabulary:
  - Randomized Control Trial
  - Quasi-Experimental Design
  - Meta-Analysis/Systematic Review
  - Mixed-Methods Study
  - Qualitative Study

### ImplementationObjective (Taxonomy)
- `id`: Same as type
- `type`: One of:
  - Intelligent Tutoring and Instruction
  - AI-Enable Personalized Advising
  - Institutional Decision-making
  - AI-Enabled Learner Mobility

### Outcome (Taxonomy)
- `id`: Same as name
- `name`: One of:
  - Cognitive - Critical Thinking/Metacognitive skills
  - Cognitive - Reading and writing literacy
  - Cognitive - speaking, listening, and language fluency
  - Cognitive - Mathematical numeracy
  - Cognitive - Scientific Reasoning
  - Behavioral - task and assignment efficiency
  - Behavioral - study habits, concentration
  - Behavioral - participation and social engagement
  - Behavioral - productivity
  - Affective - motivation
  - Affective - engagement
  - Affective - persistence

## Relationships

### Paper Relationships
- **DEPRECATED**: `Paper -[TARGETS_POPULATION]-> Population` (now stored as `Paper.population` property)
- **DEPRECATED**: `Paper -[TARGETS_USER_TYPE]-> UserType` (now stored as `Paper.user_type` property)
- **DEPRECATED**: `Paper -[USES_STUDY_DESIGN]-> StudyDesign` (now stored as `Paper.study_design` property)

- `Paper -[HAS_IMPLEMENTATION_OBJECTIVE]-> ImplementationObjective`
  - Links paper to the AI implementation purpose

- `Paper -[FOCUSES_ON_OUTCOME]-> Outcome`
  - Links paper to what outcome it measured

- `Paper -[REPORTS_FINDING]-> EmpiricalFinding`
  - Links paper to its main empirical finding

### Finding Relationships
- `Outcome -[HAS_FINDING]-> EmpiricalFinding`
  - Links outcome types to specific findings

### Cross-Taxonomy Relationships
- `ImplementationObjective -[TARGETS_OUTCOME]-> Outcome`
  - Derived relationship: created when papers link an objective to an outcome
  - Shows which AI objectives typically target which learning outcomes
  - Weight property indicates how many papers show this connection

## Visual Schema

```
                         ┌─────────────────────┐
                         │ImplementationObj.  │
                         └──────────┬──────────┘
                                    │
                         HAS_IMPL_OBJECTIVE
                                    │
                                    │
                         ┌──────────▼──────────┐
                         │   Paper             │
                         │                     │
                         │ PROPERTIES:         │
                         │ - paper_id          │
                         │ - title             │
                         │ - year              │
                         │ - venue             │
                         │ - url               │
                         │ - session_id        │
                         │ - added_date        │
                         │ - population ⭐     │
                         │ - user_type ⭐      │
                         │ - study_design ⭐   │
                         └──────────┬──────────┘
                                    │
                     ┌──────────────┼──────────────┐
                     │              │              │
          FOCUSES_ON_OUTCOME  REPORTS_FINDING     │
                     │              │              │
              ┌──────▼──────┐  ┌───▼──────────┐   │
              │  Outcome    │  │ Empirical    │   │
              │             │  │ Finding      │   │
              └──────┬──────┘  │ - direction  │   │
                     │         │ - summary    │   │
                     │         │ - measure    │   │
              HAS_FINDING     │ - study_size │   │
                     │         │ - effect_sz  │   │
                     └─────────►──────────────┘   │
                                                   │
                                                   │
                                 TARGETS_OUTCOME   │
                               (derived weight)   │
                                                   │
                         ┌─────────────────────────┘
                         │
                         └────►ImplementationObj
```

**⭐ = New schema**: These are now stored as properties, not relationships to separate nodes

## Key Features

1. **Session-based tracking**: Every paper is tagged with `session_id` for filtering
2. **No duplicates**: Papers are MERGEd by title to avoid duplicates
3. **Property-based taxonomy** (NEW): Population, UserType, StudyDesign stored as properties for faster queries
4. **Relationship-based taxonomy**: ImplementationObjective and Outcome remain as nodes for evidence map matrix
5. **Derived relationships**: Objective→Outcome connections are built from paper data
6. **Cumulative knowledge**: Database grows with each research session
7. **Enhanced EmpiricalFinding** (NEW): 23 additional context fields for visualization support
   - Student/participant composition (4 fields)
   - School/institution context (8 fields)
   - Institution classification (2 fields)
   - Geography (1 field)
   - System coordination indicators (2 scored fields, 0-4)
   - Evidence map indicators (2 scored fields, 0-4)

## Example Queries

### Get all papers from a session
```cypher
MATCH (p:Paper {session_id: $session_id})
RETURN p
```

### Find papers by objective and outcome
```cypher
MATCH (p:Paper)-[:HAS_IMPLEMENTATION_OBJECTIVE]->(obj:ImplementationObjective)
MATCH (p)-[:FOCUSES_ON_OUTCOME]->(out:Outcome)
WHERE obj.type = "Intelligent Tutoring and Instruction"
  AND out.name = "Cognitive - Mathematical numeracy"
RETURN p
```

### Filter papers by properties (NEW)
```cypher
MATCH (p:Paper)
WHERE p.population = "Elementary (PreK-5th)"
  AND p.study_design = "Randomized Control Trial"
  AND p.user_type = "Student"
RETURN p.title, p.year, p.venue
```

### Query enhanced EmpiricalFinding data (NEW)
```cypher
MATCH (p:Paper)-[:REPORTS_FINDING]->(f:EmpiricalFinding)
WHERE f.region = "United States"
  AND f.urban_type = "urban"
  AND f.system_impact_levels >= 2
  AND f.evidence_type_strength <= 2
RETURN p.title,
       f.region,
       f.school_type,
       f.system_impact_levels,
       f.decision_making_complexity,
       f.evidence_type_strength
```

### See which objectives target which outcomes
```cypher
MATCH (obj:ImplementationObjective)-[r:TARGETS_OUTCOME]->(out:Outcome)
RETURN obj.type, out.name, r.weight
ORDER BY r.weight DESC
```
