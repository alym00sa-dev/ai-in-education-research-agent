# Intervention Mapping Review: P1 vs P5 Gap Analysis

**Date:** 2026-01-29
**Issue:** P5 shows 40 interventions, but P1 only shows 19-20 interventions

---

## Summary

**Current State:**
- P5 (Pillar & Intervention Distribution): Uses all **40 interventions** from `wwc_level3_mapped.json`
- P1 (Effect Size Evolution): Uses only **20 interventions** from `intervention_use_case_mapping.json`
- **21 interventions** are missing from P1 visualization

**Root Cause:**
The original P1 mapping was created with only 20 manually selected interventions mapped to 5 use cases. The remaining interventions were never mapped.

---

## Two Mapping Tasks Created

### Task 1: Map Missing 21 Interventions
**File:** `missing_interventions_to_map.json`

**Purpose:** Extend existing mapping by adding the 21 interventions missing from P1

**Key Findings:**
- **20 interventions** have data available (1 has no data: Accelerated Math®)
- Suggested mapping breakdown:
  - **Real-time feedback:** 11 interventions
  - **Instructional planning:** 5 interventions
  - **Math tutoring:** 3 interventions
  - **Teacher coaching:** 2 interventions
  - **Automated grading:** 0 interventions

**High-Impact Missing Interventions:**
1. **National Board for Professional Teaching Standards** - 12.9M students, 73 findings
2. **Literacy Design Collaborative (LDC)** - 72,895 students, 8 findings
3. **READ 180®** - 65,621 students, 103 findings
4. **Intelligent Tutoring for Structure Strategy (ITSS)** - 61,881 students, 25 findings

---

### Task 2: Fresh Evaluation of ALL 40 Interventions
**File:** `all_40_interventions_fresh_mapping.json`

**Purpose:** Unbiased re-evaluation of ALL 40 interventions to check if original 20 were properly categorized

**Approach:** Blind re-assessment without looking at original mappings to identify any bias

**Fresh Mapping Results:**
- **Math tutoring:** 4 interventions
- **Automated grading:** 0 (but appears as secondary for 4 interventions)
- **Real-time feedback:** 23 interventions
- **Instructional planning:** 10 interventions
- **Teacher coaching:** 3 interventions

---

## Key Observations

### 1. Real-time Feedback Dominates
- Both original and fresh mappings show **real-time feedback** is the dominant category
- Original: 13/20 (65%)
- Fresh: 23/40 (57.5%)
- This reflects WWC's focus on responsive/adaptive teaching

### 2. Math Tutoring Consistency
- Original: 4 interventions (Cognitive Tutor Algebra I, Cognitive Tutor Geometry, Saxon Algebra I, UCSMP Algebra)
- Fresh: 4 interventions (same + reclassified Saxon & UCSMP)
- **NOTE:** Saxon and UCSMP could be argued as "instructional planning" (textbooks/curricula) vs "math tutoring"

### 3. Teacher Coaching
- Original: 1 intervention (My Teaching Partner-Secondary)
- Fresh: 3 interventions (added NBPTS Certification, TAP system)
- **Missing high-impact:** NBPTS has 12.9M students - largest intervention by far!

### 4. No Automated Grading Primary Category
- Pre-LLM era data predates widespread edtech assessment automation
- Some interventions have automated components (READ 180, Accelerated Reader, Read Naturally, Waterford)
- Could consider these as secondary matches

---

## Potential Issues with Original Mapping

### Issue 1: Saxon Algebra I & UCSMP Algebra Classification
**Original mapping:** "math_tutoring"
**Alternative:** "instructional_planning"

**Justification for reconsideration:**
- These are textbooks/curricula, not tutoring systems
- Primary purpose is providing lesson plans and instructional sequences
- Unlike Cognitive Tutor (true tutoring system), these are structured curricula
- Fresh evaluation suggests these might be miscategorized

### Issue 2: Missing Major Teacher Development Interventions
**Original mapping:** Only included My Teaching Partner-Secondary
**Missing:**
- National Board for Professional Teaching Standards (12.9M students!)
- TAP: The System for Teacher and Student Advancement

These are significant teacher coaching interventions that should appear in P1.

### Issue 3: High-Impact Interventions Missing Entirely
Several interventions with substantial evidence base aren't in P1:
- READ 180® (65,621 students, 103 findings)
- ITSS (61,881 students, 25 findings)
- LDC (72,895 students, 8 findings)

---

## Recommendations

### Option A: Conservative Approach
1. Add the 20 interventions with data from Task 1
2. Keep original 20 mappings unchanged
3. Result: P1 shows 39-40 interventions (matches P5)

**Pros:**
- Maintains consistency with existing mapping
- Quick to implement

**Cons:**
- May perpetuate any bias in original categorization
- Saxon/UCSMP classification remains questionable

---

### Option B: Comprehensive Re-evaluation (RECOMMENDED)
1. Use fresh mapping from Task 2 for ALL 40 interventions
2. Reclassify Saxon Algebra I and UCSMP Algebra as "instructional_planning"
3. Add missing teacher coaching interventions
4. Result: Unbiased, comprehensive mapping

**Pros:**
- Eliminates potential bias
- More accurate categorization
- Includes all major interventions

**Cons:**
- Changes existing visualization (but likely more accurate)

---

## Next Steps

**Decision needed:** Which approach to use?

**If Option A:**
- Merge `missing_interventions_to_map.json` into `intervention_use_case_mapping.json`
- Test P1 visualization

**If Option B:**
- Replace `intervention_use_case_mapping.json` with fresh mapping
- Update use case counts in metadata
- Test P1 visualization

**Then:**
- Verify P1 "By Intervention" view shows all mapped interventions
- Ensure Gates Investment overlay uses same filters as P5 ✓ (already fixed)

---

## Files Created

1. **missing_interventions_to_map.json** - 21 missing interventions with suggested mappings
2. **all_40_interventions_fresh_mapping.json** - Fresh evaluation of all 40 interventions
3. **INTERVENTION_MAPPING_REVIEW.md** - This summary document

---

## Additional Notes

- **Cognitive Tutor® Geometry** appears in both P1 mapping file and missing list - this is because it's mapped but has minimal data (1 finding, 669 students)
- **Accelerated Math®** has no data in CSV - won't appear in P1 even if mapped
- Some interventions legitimately span multiple use cases - fresh mapping includes secondary matches for these
