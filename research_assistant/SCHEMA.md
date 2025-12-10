# Knowledge Graph Schema

## Node Types

### Paper
- `paper_id`: Unique identifier (e.g., "paper_123")
- `title`: Paper title
- `year`: Publication year
- `venue`: Publication venue
- `session_id`: Research session that added this paper
- `added_date`: When added to knowledge graph

### EmpiricalFinding
- `finding_id`: Unique identifier
- `direction`: "Positive", "Negative", "No Effect", "Mixed"
- `results_summary`: 2-3 sentence summary
- `measure`: What was measured (test scores, completion rates, etc.)
- `study_size`: Number of participants
- `effect_size`: Statistical effect size

### Population (Taxonomy)
- `id`: Same as type
- `type`: One of:
  - Elementary (PreK-5th)
  - Middle School (6th-8th)
  - High School (9th-12th)
  - Undergraduate
  - Graduate
  - Adult

### UserType (Taxonomy)
- `id`: Same as type
- `type`: One of:
  - Student
  - Educator
  - Administrator
  - Parent
  - School
  - Community
  - Systematic: social/political level information

### StudyDesign (Taxonomy)
- `id`: Same as type
- `type`: One of:
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
- `Paper -[TARGETS_POPULATION]-> Population`
  - Links paper to the population it studied

- `Paper -[TARGETS_USER_TYPE]-> UserType`
  - Links paper to the type of user

- `Paper -[USES_STUDY_DESIGN]-> StudyDesign`
  - Links paper to its research methodology

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
    ┌──────────┐              ┌─────────────────────┐
    │Population│              │ImplementationObj.  │
    └────▲─────┘              └──────────┬──────────┘
         │                               │
  TARGETS_POPULATION          HAS_IMPL_OBJECTIVE
         │                               │
    ┌────┴─────────┐                    │
    │   Paper      │◄───────────────────┘
    │              │
    │ session_id   │─────FOCUSES_ON_OUTCOME────┐
    │ added_date   │                            │
    └────┬─────────┘                            │
         │   │   │                       ┌──────▼──────┐
         │   │   └─USES_STUDY_DESIGN───►│  Outcome    │
         │   │                           └──────┬──────┘
         │   └─TARGETS_USER_TYPE──►             │
         │                          ┌───────────┘
         │                          │ HAS_FINDING
         │                          │
  REPORTS_FINDING          ┌────────▼────────┐
         │                 │ EmpiricalFinding│
         │                 │  - direction    │
         ▼                 │  - summary      │
    ┌────────┐            │  - measure      │
    │StudyDes│            │  - study_size   │
    └────────┘            │  - effect_size  │
                          └─────────────────┘
         ▲
         │
         └─────TARGETS_OUTCOME────┐
                                  │
                        ┌─────────┴────────┐
                        │ImplementationObj│
                        └──────────────────┘
```

## Key Features

1. **Session-based tracking**: Every paper is tagged with `session_id` for filtering
2. **No duplicates**: Papers are MERGEd by title to avoid duplicates
3. **One-to-one taxonomy links**: Each paper has exactly one population, user type, study design, objective, and outcome
4. **Derived relationships**: Objective→Outcome connections are built from paper data
5. **Cumulative knowledge**: Database grows with each research session

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

### See which objectives target which outcomes
```cypher
MATCH (obj:ImplementationObjective)-[r:TARGETS_OUTCOME]->(out:Outcome)
RETURN obj.type, out.name, r.weight
ORDER BY r.weight DESC
```
