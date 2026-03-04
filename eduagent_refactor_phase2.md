# EDU Agent Refactoring Plan - Phase 2 (Deep Cleanup)

**Date:** March 3, 2026 (Updated: March 4, 2026)
**Based on:** Comprehensive code usage analysis (CLEANUP_INVENTORY.md)
**Timeline:** 4 sessions (12-17 hours total)

---

## 🛡️ Safety First

Before starting any refactoring work:

```bash
# Create main backup branch
git checkout -b refactor-phase2-backup
git push -u origin refactor-phase2-backup
git checkout main

# Create session-specific branch
git checkout -b refactor-phase2-session0
```

**Branch Strategy:**
- Each session gets its own branch: `refactor-phase2-session0`, `refactor-phase2-session1`, etc.
- Sessions can be reviewed independently
- Easy to rollback individual sessions if needed

---

## 📊 Analysis Results Summary

**Good News:**
- ✅ Well-structured architecture with clear separation
- ✅ Good test coverage in both projects
- ✅ Active documentation

**Issues Found:**
- 🗑️ **2 duplicate docs** to delete
- ⚠️ **1 dead code file** - `evidence_map.py` (not imported AND broken schema)
- 🔍 **2 files** need review (potentially unused)
- 🚨 **4 large files** need breaking up (>500 lines each)
- 🐛 **4 concrete bugs** found in active code
- ⚠️ **~20 files** need manual human review (product/technical decisions)

**Critical Insights:**
1. Just because a file is **imported/used** doesn't mean it **should exist**
2. Dead code = not imported OR imported but broken/obsolete
3. `evidence_map.py` is BOTH not imported AND broken (references non-existent schema relationships)

---

## 🎯 Four-Session Plan

### SESSION 0: Manual Review (2-3 hours)

**Branch:** `refactor-phase2-session0`

**IMPORTANT:** Even if a file is being imported/used, it might still need to be deleted, moved, or consolidated. This session reviews each file to make human judgment calls about whether it should exist at all.

---

#### Manual Review Checklist

For each file, ask:
1. **Should this feature exist?** (Product decision)
2. **Is this the right approach?** (Technical decision)
3. **Is this duplicating functionality?** (Could be consolidated)
4. **Is this in the right location?** (Organizational)
5. **Is this technical debt?** (Should be replaced/removed)

**Pre-Decided Items (no review needed):**

These decisions are obvious from code analysis:

**ARCHIVE (move to scripts/):**
- `database/enrichment/enrich_existing_papers.py` (414 lines) - One-time DB maintenance script
- `database/enrichment/retry_failed_papers.py` (174 lines) - One-time DB maintenance script
- `database/enrichment/smart_section_retry.py` (239 lines) - One-time DB maintenance script
  - *Rationale: Not called from active code, mutual imports between them only*

**DELETE:**
- `evidence_map.py` (305 lines) - NOT imported AND broken
  - *Rationale: References non-existent Neo4j relationships (`TARGETS_POPULATION`, `TARGETS_USER_TYPE`, `USES_STUDY_DESIGN`). Active schema stores these as Paper node properties, not relationships. Would require complete rewrite to integrate.*

**KEEP (no review needed):**
- `init_database.py` (7 lines) - Simple, clearly useful utility

**Result:** Session 0 reduced from 36 files to ~20 files requiring human judgment.

---

#### 0.1 Open Deep Research Files (~10 files requiring review)

**Entry Points:**
- [ ] `server.py` (231 lines) - **Decision:** KEEP / DELETE / MOVE / CONSOLIDATE
- [ ] `bridge_server.py` (257 lines) - **Decision:** KEEP / DELETE / MOVE / CONSOLIDATE

**Core Active Files:**
- [ ] `src/open_deep_research/deep_researcher.py` (718 lines) - **Decision:** KEEP / DELETE / MOVE / CONSOLIDATE
- [ ] `src/open_deep_research/utils.py` (1071 lines) - **Decision:** KEEP / DELETE / MOVE / CONSOLIDATE
- [ ] `src/open_deep_research/prompts.py` (427 lines) - **Decision:** KEEP / DELETE / MOVE / CONSOLIDATE
- [ ] `src/open_deep_research/configuration.py` (251 lines) - **Decision:** KEEP / DELETE / MOVE / CONSOLIDATE
- [ ] `src/open_deep_research/state.py` (95 lines) - **Decision:** KEEP / DELETE / MOVE / CONSOLIDATE

**Utility Scripts:**
- [ ] `test_deployment.py` (76 lines) - **Decision:** KEEP / DELETE / ARCHIVE
- [ ] `src/security/auth.py` (155 lines) - **Decision:** KEEP / DELETE / MOVE

**Tests:**
- [ ] `tests/run_evaluate.py` (89 lines) - **Decision:** KEEP / DELETE / ARCHIVE
- [ ] `tests/evaluators.py` (173 lines) - **Decision:** KEEP / DELETE / ARCHIVE
- [ ] `tests/prompts.py` (256 lines) - **Decision:** KEEP / DELETE / ARCHIVE
- [ ] `tests/pairwise_evaluation.py` (127 lines) - **Decision:** KEEP / DELETE / ARCHIVE
- [ ] `tests/supervisor_parallel_evaluation.py` (60 lines) - **Decision:** KEEP / DELETE / ARCHIVE
- [ ] `tests/extract_langsmith_data.py` (82 lines) - **Decision:** KEEP / DELETE / ARCHIVE

---

#### 0.2 Research Assistant Agent Files (~10 files requiring review)

**Entry Point:**
- [ ] `app.py` (1163 lines) - **Decision:** KEEP / DELETE / MOVE / CONSOLIDATE

**Core Active Files:**
- [ ] `src/neo4j_config.py` (207 lines) - **Decision:** KEEP / DELETE / MOVE / CONSOLIDATE
- [ ] `src/kg_extractor.py` (527 lines) - **Decision:** KEEP / DELETE / MOVE / CONSOLIDATE
- [ ] `src/research_pipeline.py` (458 lines) - **Decision:** KEEP / DELETE / MOVE / CONSOLIDATE
- [ ] `src/session_manager.py` (279 lines) - **Decision:** KEEP / DELETE / MOVE / CONSOLIDATE
- [ ] `src/enhanced_extraction_prompt.py` (298 lines) - **Decision:** KEEP / DELETE / MOVE / CONSOLIDATE
- [ ] `src/env_config.py` (80 lines) - **Decision:** KEEP / DELETE / MOVE / CONSOLIDATE

**WWC Data Processing Scripts:**
- [ ] `import_wwc_to_neo4j.py` (514 lines) - **Decision:** KEEP / DELETE / ARCHIVE
- [ ] `process_wwc_data.py` (425 lines) - **Decision:** KEEP / DELETE / ARCHIVE
- [ ] `map_wwc_to_ios.py` (254 lines) - **Decision:** KEEP / DELETE / ARCHIVE
- [ ] `migrate_schema.py` (187 lines) - **Decision:** KEEP / DELETE / ARCHIVE

**Utility Scripts:**
- [ ] `test_neo4j.py` (37 lines) - **Decision:** KEEP / DELETE / ARCHIVE

**Tests:**
- [ ] `tests/integration/test_extraction.py` (113 lines) - **Decision:** KEEP / DELETE / ARCHIVE
- [ ] `tests/integration/test_full_pipeline.py` (181 lines) - **Decision:** KEEP / DELETE / ARCHIVE
- [ ] `tests/integration/test_streaming_detail.py` (73 lines) - **Decision:** KEEP / DELETE / ARCHIVE

---

#### 0.3 Common Questions to Ask During Review

**For each file, consider:**

**Product/Feature Questions:**
- Is this feature actually being used by users?
- Does this feature align with current product direction?
- Should this feature be deprecated?
- Is there a better way to achieve this goal?

**Technical Questions:**
- Is this the right technical approach?
- Is this duplicating functionality elsewhere?
- Could this be consolidated with another file?
- Is this technical debt from an old implementation?
- Is this a workaround that should be fixed properly?

**Organizational Questions:**
- Is this file in the right project? (research_assistant vs open_deep_research)
- Is this in the right folder?
- Should this be a standalone tool vs. integrated feature?

**Examples of files that might be used but should be deleted:**
- Old implementation that's been replaced but code still references it
- Feature that was never finished and shouldn't be completed
- Workaround that should be properly fixed instead
- Duplicate functionality that should be consolidated
- Test utilities for features that no longer exist

---

#### 0.4 Document Decisions

**Option A (Recommended):** Update checkboxes inline in this plan document (Section 0.1 and 0.2) with decisions.

**Option B:** Use inline checkboxes in this plan with brief rationale notes.

**Option C:** Create `MANUAL_REVIEW_DECISIONS.md` but **DELETE IT after Session 1** to avoid documentation debt.

**Do NOT create permanent documentation files** - decisions should be captured in git commits and this plan only.

**Output:** Clear action plan based on human judgment, not just automated import analysis.

---

### SESSION 1: Quick Wins + Bug Fixes (2-3 hours)

**Branch:** `refactor-phase2-session1`

Low-risk cleanup - delete duplicates, fix concrete bugs, and execute decisions from manual review.

---

#### Step 1: Fix Concrete Bugs (30-45 min)

**Bug fixes found during code review:**

**A. Fix `session_manager.py` line 249 - AttributeError bug**
```python
# CURRENT (BROKEN):
StructuredPaper(
    text_content="",  # StructuredPaper has no text_content field!
    ...
)

# FIX: Remove the text_content="" argument from the StructuredPaper() constructor call.
# Do NOT add text_content to the StructuredPaper dataclass — it has no meaning there.
# The fallback code is creating a minimal StructuredPaper for display only.
```
**Risk:** HIGH - This is a latent `AttributeError` that fires if session graph rebuild fallback executes.

**B. Remove unused import from `kg_extractor.py` line 3**
```python
# REMOVE:
import re  # Never used in this file
```

**C. Remove debug print statements from `kg_extractor.py` lines 69-86**
```python
# DELETE these debug prints:
print(f"ANTHROPIC_API_KEY is {'set' if os.getenv('ANTHROPIC_API_KEY') else 'not set'}")
# ... (all debug logging about environment variables)
```
**Risk:** MEDIUM - Debug statements should not be in production code.

**D. Move import to module top in `research_pipeline.py`**
```python
# CURRENT: import re inside functions
# FIX: Move to top of file with other imports
```

**Testing:**
- [ ] Run app.py and verify no AttributeError
- [ ] Check kg_extractor.py has no debug output
- [ ] All imports at module level

**Commands:**
```bash
# Navigate to working directory
cd eduagent/research_assistant_agent

# After fixes:
git add src/session_manager.py src/kg_extractor.py src/research_pipeline.py
git commit -m "Fix bugs: session_manager AttributeError, remove unused imports, remove debug prints"
```

**Risk:** Low-Medium - These are targeted fixes
**Files affected:** 3 files

---

#### Step 2: Delete Duplicate Documentation (5 min)

**What's being deleted:**
- `open_deep_research/EDUAGENT_OVERVIEW.md` (duplicate)
- `research_assistant_agent/EDUAGENT_OVERVIEW.md` (duplicate)

**Master copy kept:** Root `eduagent/EDUAGENT_OVERVIEW.md`

**Commands:**
```bash
cd eduagent
rm open_deep_research/EDUAGENT_OVERVIEW.md
rm research_assistant_agent/EDUAGENT_OVERVIEW.md
git add .
git commit -m "Remove duplicate EDUAGENT_OVERVIEW.md files"
```

**Risk:** None - these are exact duplicates
**Files affected:** 2 deleted

---

#### Step 3: Execute Pre-Decided Deletions/Archives (15 min)

**A. DELETE `evidence_map.py` (BROKEN + NOT IMPORTED)**
```bash
rm research_assistant_agent/src/evidence_map.py
git add research_assistant_agent/src/evidence_map.py
git commit -m "Delete evidence_map.py: not imported and broken schema

References non-existent Neo4j relationships (TARGETS_POPULATION,
TARGETS_USER_TYPE, USES_STUDY_DESIGN). Active schema stores these as
Paper node properties, not relationships. Would require complete rewrite
to integrate."
```

**B. ARCHIVE database enrichment scripts**
```bash
# Move to scripts/ folder
mkdir -p scripts/database_maintenance
mv database/enrichment/enrich_existing_papers.py scripts/database_maintenance/
mv database/enrichment/retry_failed_papers.py scripts/database_maintenance/
mv database/enrichment/smart_section_retry.py scripts/database_maintenance/

# Also handle the log files left behind:
mv database/enrichment/*.json scripts/database_maintenance/
# (Moves enrichment_log.json, retry_log.json, smart_section_log.json)

# Remove the now-empty folder
rmdir database/enrichment

git add database/enrichment/ scripts/
git commit -m "Archive database enrichment scripts to scripts/database_maintenance

These are one-time maintenance scripts not called from active code."
```

**Risk:** Low - not imported by active code
**Files affected:** 4 files moved/deleted

---

#### Step 4: Review Remaining Potentially Unused Files (30-45 min)

**Files to investigate:**

**A. `open_deep_research/tests/extract_langsmith_data.py` (82 lines)**
- **Status:** Utility for extracting LangSmith evaluation data
- **Decision needed:** Still used for evals? Or archive?

**B. `research_assistant_agent/SEPARATION_README.md`**
- **Status:** Documentation about code separation
- **Decision needed:** Is separation complete? Archive if outdated.

**Actions:**
```bash
# If deleting:
rm open_deep_research/tests/extract_langsmith_data.py
rm research_assistant_agent/SEPARATION_README.md

# If archiving:
cd eduagent
mkdir -p archive/2026-03-04
mv open_deep_research/tests/extract_langsmith_data.py archive/2026-03-04/
mv research_assistant_agent/SEPARATION_README.md archive/2026-03-04/
```

**Risk:** Low - not imported by active code
**Files affected:** 0-2 files (depending on decisions)

---

### SESSION 2: Critical Refactoring - Part 1 (6-8 hours)

**Branch:** `refactor-phase2-session2`

Break up the largest file - app.py. This is complex due to Streamlit's execution model.

---

#### Step 5: Refactor `app.py` (1,163 lines → ~200 lines) [6-8 hours]

**Current problem:** Monolithic Streamlit app - everything in one file

**CRITICAL: Streamlit re-runs the entire script from top to bottom on every user interaction.**
- If module A initializes a session key and module B reads it before A has run → `KeyError`
- Session state sharing is the primary risk when splitting files

**PREP STEP (REQUIRED BEFORE ANY EXTRACTION):**

**5a. Enumerate all `st.session_state` keys (1 hour)**

Before writing ANY extracted code, create a session state inventory:

```markdown
## Session State Inventory

| Key | Owner Module | Initialized Where | Read By | Type |
|-----|--------------|-------------------|---------|------|
| `research_state` | chat.py | chat.py L45 | chat.py, results.py | ResearchState |
| `selected_node` | visualization.py | visualization.py L102 | visualization.py, results.py | str or None |
| ... | ... | ... | ... | ... |
```

**Questions to answer for each key:**
1. Which module owns this state?
2. Where is it initialized?
3. Which modules read it?
4. What happens if it's read before initialization?

**This prevents session state bugs that are annoying to trace.**

---

**Proposed structure:**
```
research_assistant_agent/
├── app.py (main entry, ~200 lines)
└── ui/
    ├── __init__.py
    ├── sidebar.py (~150 lines) - Configuration sidebar
    ├── visualization.py (~250 lines) - D3.js graph rendering
    ├── chat.py (~200 lines) - Chat interface
    ├── results.py (~200 lines) - Results display
    └── components.py (~150 lines) - Reusable UI components
```

**What stays in `app.py` (~200 lines):**
- Page config (`st.set_page_config()`)
- Top-level routing between tabs
- Imports from `ui/` modules
- Session state initialization (if centralized)
- Main entry point logic

**Benefits:**
- Each component is self-contained and testable
- Easier to modify individual features
- Clearer code organization
- Better for new developers

**Approach:**
1. **FIRST:** Complete session state inventory (Step 5a above)
2. Create `ui/` folder structure
3. Extract sidebar logic → `ui/sidebar.py`
4. Extract visualization → `ui/visualization.py`
5. Extract chat interface → `ui/chat.py`
6. Extract results display → `ui/results.py`
7. Update `app.py` to import from ui modules
8. Test thoroughly after each extraction

**Testing checklist:**
- [ ] Session state inventory complete and accurate
- [ ] App loads without errors
- [ ] No `KeyError` exceptions from session state
- [ ] Sidebar configuration works
- [ ] Graph visualization renders
- [ ] Chat interface functional
- [ ] Results display correctly
- [ ] All tabs navigate properly
- [ ] State persists correctly across re-runs

**Risk:** Medium-High - Streamlit state management is tricky
**Estimated time:** 6-8 hours (includes session state enumeration)
**Files affected:** 1 file split into 6 files

---

### SESSION 3: Critical Refactoring - Part 2 (2-3 hours)

**Branch:** `refactor-phase2-session3`

Break up utils.py and optionally other large files.

---

#### Step 6: Refactor `utils.py` (1,071 lines → ~300 lines) [2-3 hours]

**File:** `open_deep_research/src/open_deep_research/utils.py`

**Current problem:** Giant utilities file with everything

**Proposed structure:**
```
open_deep_research/src/open_deep_research/
└── utils/
    ├── __init__.py (export all)
    ├── search.py (~300 lines) - Tavily, DuckDuckGo, Exa search
    ├── web.py (~250 lines) - Web scraping, summarization
    ├── llm.py (~200 lines) - LLM interaction helpers
    └── mcp.py (~150 lines) - MCP server utilities
```

**NO backward compatibility shim** - this is an internal codebase where the only caller is `deep_researcher.py`. Just update the imports directly.

**Benefits:**
- Much easier to navigate
- Clear separation by function
- Easier to test individual components
- Better dependency management
- No unnecessary indirection layer

**Approach:**
1. Create `utils/` folder
2. Split functions by category into new files
3. Create `utils/__init__.py` as package marker (empty or with version string only - NOT a re-export shim)
4. **Update imports in `deep_researcher.py` to point to specific submodules** (e.g., `from utils.search import search_tavily`)
5. Delete old `utils.py` file
6. Test all search and web scraping functionality

**Testing checklist:**
- [ ] Search functions work (Tavily, DuckDuckGo, Exa)
- [ ] Web scraping works
- [ ] LLM interaction works
- [ ] MCP servers work
- [ ] All tests pass

**Risk:** Low-Medium - straightforward import updates
**Files affected:** 1 file deleted, 4 new files created

---

#### Step 7 (OPTIONAL): Refactor `deep_researcher.py` (718 lines → ~250 lines) [If time]

**File:** `open_deep_research/src/open_deep_research/deep_researcher.py`

**Proposed structure:**
```
open_deep_research/src/open_deep_research/
├── deep_researcher.py (graph definition, ~200 lines)
└── nodes/
    ├── __init__.py
    ├── planner.py (~150 lines)
    ├── researcher.py (~200 lines)
    ├── summarizer.py (~150 lines)
    └── common.py (~100 lines)
```

**Benefits:**
- Clearer node separation
- Easier to modify individual nodes
- Better testability

**Risk:** Low - clear functional separation
**Files affected:** 1 file split into 5 files

---

## ✅ Success Criteria

### After Session 0:
- ✅ ~20 files reviewed with human judgment
- ✅ Clear decisions documented (inline or in temporary doc)
- ✅ Action plan for deletions, moves, consolidations
- ✅ Pre-decided items verified

### After Session 1:
- ✅ 4 concrete bugs fixed (session_manager, kg_extractor, research_pipeline)
- ✅ No duplicate documentation
- ✅ evidence_map.py deleted (broken + not imported)
- ✅ database/enrichment scripts archived
- ✅ Clear decisions on remaining potentially unused files
- ✅ Archive/scripts folders created as needed

### After Session 2:
- ✅ Session state inventory complete and accurate
- ✅ `app.py` is manageable size (~200 lines: page config, routing, imports only)
- ✅ UI components are in separate files
- ✅ All app features still work
- ✅ No session state KeyErrors

### After Session 3:
- ✅ `utils.py` deleted, split into focused modules (utils/search.py, web.py, llm.py, mcp.py)
- ✅ Imports in deep_researcher.py updated directly (no shim)
- ✅ All search and web functionality works
- ✅ (Optional) `deep_researcher.py` has clear node separation

---

## 📋 Session Checklists

### SESSION 0: Manual Review
- [ ] Review pre-decided items (verify Archive/Delete decisions)
- [ ] Review ~10 open_deep_research Python files requiring judgment
- [ ] Review ~10 research_assistant_agent Python files requiring judgment
- [ ] For each file, decide: KEEP / DELETE / MOVE / CONSOLIDATE / ARCHIVE
- [ ] Document decisions (inline in plan OR temporary MANUAL_REVIEW_DECISIONS.md)
- [ ] Get user/product approval on deletions
- [ ] Create branch: `refactor-phase2-session0`

**Estimated time:** 2-3 hours

### SESSION 1: Quick Wins + Bug Fixes
- [ ] Create branch: `refactor-phase2-session1`
- [ ] **FIX:** session_manager.py line 249 - StructuredPaper AttributeError
- [ ] **FIX:** Remove unused `import re` from kg_extractor.py line 3
- [ ] **FIX:** Remove debug prints from kg_extractor.py lines 69-86
- [ ] **FIX:** Move `import re` to module top in research_pipeline.py
- [ ] Delete 2 duplicate EDUAGENT_OVERVIEW.md files
- [ ] **DELETE:** evidence_map.py (broken schema + not imported)
- [ ] **ARCHIVE:** database/enrichment/*.py to scripts/database_maintenance/
- [ ] Review extract_langsmith_data.py - decide: keep/archive
- [ ] Review SEPARATION_README.md - decide: keep/archive
- [ ] Create archive/ or scripts/ folders as needed
- [ ] Commit all changes
- [ ] **DELETE MANUAL_REVIEW_DECISIONS.md if created**

**Estimated time:** 2-3 hours

### SESSION 2: Refactor app.py
- [ ] Create branch: `refactor-phase2-session2`
- [ ] **PREP:** Enumerate all st.session_state keys (create inventory)
- [ ] **PREP:** Document which module owns each key
- [ ] **PREP:** Document initialization order and dependencies
- [ ] Create ui/ folder structure
- [ ] Extract sidebar → ui/sidebar.py
- [ ] Extract visualization → ui/visualization.py
- [ ] Extract chat → ui/chat.py
- [ ] Extract results → ui/results.py
- [ ] Update app.py to import from ui/ (page config, routing, imports only)
- [ ] Test all features work (especially session state)
- [ ] Commit after each extraction

**Estimated time:** 6-8 hours (includes session state enumeration)

### SESSION 3: Refactor utils.py
- [ ] Create branch: `refactor-phase2-session3`
- [ ] Create utils/ folder
- [ ] Split search functions → utils/search.py
- [ ] Split web functions → utils/web.py
- [ ] Split LLM functions → utils/llm.py
- [ ] Split MCP functions → utils/mcp.py
- [ ] Create utils/__init__.py that exports all
- [ ] **Update imports in deep_researcher.py directly** (no backward compat shim)
- [ ] **Delete old utils.py file**
- [ ] Test all functionality
- [ ] (Optional) Refactor deep_researcher.py
- [ ] Commit all changes

**Estimated time:** 2-3 hours (4-5 if including deep_researcher.py)

---

## 🎯 Expected Results

### Before Phase 2:
- **Duplicate docs:** 2 files
- **Dead code:** 1 file (evidence_map.py - not imported AND broken)
- **Concrete bugs:** 4 bugs in active code
- **Potentially unused:** 2-3 files
- **Very large files (>1000 lines):** 2 files (app.py, utils.py)
- **Large files (500-1000 lines):** 2 files (deep_researcher.py, kg_extractor.py)

### After Phase 2:
- **Duplicate docs:** 0 files
- **Dead code:** 0 files (deleted)
- **Concrete bugs:** 0 bugs (all fixed in Session 1)
- **Potentially unused:** 0 files (all reviewed)
- **Very large files (>1000 lines):** 0 files
- **Large files (500-1000 lines):** 1-2 files (depending on optional refactoring)
- **New structure:** Clean component-based organization
- **Database scripts:** Clearly organized in scripts/database_maintenance/

### Code Quality Improvements:
- ✅ Better maintainability
- ✅ Easier to onboard new developers
- ✅ Clearer separation of concerns
- ✅ Better testability
- ✅ Easier to modify features

---

## ⚠️ Risks & Mitigation

### Medium-High Risk: app.py Refactoring
**Risk:** Streamlit state management might break - script re-runs from top on every interaction
**Mitigation:**
- **REQUIRED:** Enumerate all st.session_state keys BEFORE any extraction
- Document ownership, initialization order, and dependencies
- Test after each extraction
- Session-specific branches for easy rollback
- Commit incrementally

### Low-Medium Risk: utils.py Refactoring
**Risk:** Import updates in deep_researcher.py
**Mitigation:**
- Direct import updates (no shim complexity)
- Run all tests after changes
- Use IDE refactoring tools if available

### Low Risk: Bug Fixes
**Risk:** session_manager.py AttributeError fix might reveal other issues
**Mitigation:**
- Test session graph rebuild functionality
- Standard git backup

### Low Risk: Everything Else
**Mitigation:** Standard git backup and testing with session-specific branches

---

## 📝 Notes

### Files NOT Being Refactored (Out of Scope)
These are reasonable sizes and well-structured:
- `kg_extractor.py` (527 lines) - Could be split but not urgent
- `research_pipeline.py` (458 lines) - Reasonable size
- `prompts.py` (427 lines) - Just prompts, fine as-is
- All other files (<400 lines)

### Why These Priorities?
1. **Session 0** - Human judgment on what should exist (critical first step)
2. **Session 1** - Quick wins: fix bugs, execute decisions from manual review
3. **Session 2** - Biggest pain point (app.py), highest impact, highest risk
4. **Session 3** - Second biggest pain point (utils.py), high impact, lower risk

### Session-Specific Branches
Each session gets its own branch for independent review:
- `refactor-phase2-session0` - Manual review decisions
- `refactor-phase2-session1` - Bug fixes and deletions
- `refactor-phase2-session2` - app.py refactoring
- `refactor-phase2-session3` - utils.py refactoring

**Benefits:**
- Sessions can be reviewed independently
- Easy to rollback individual sessions
- Clear git history
- Can merge sessions individually after review

---

## 🚀 Ready to Start?

**Prerequisites:**
1. Complete Phase 1 cleanup (already done!)
2. Review this plan
3. Get staff engineer approval (COMPLETED - feedback addressed)
4. Schedule 4 focused sessions

**When ready:**
See "Safety First" section at top of document for branch creation.

---

## 💬 Staff Engineer Review - ADDRESSED

**Reviewer:** Staff Engineer
**Review Date:** March 4, 2026
**Status:** ✅ ALL FEEDBACK ADDRESSED (March 4, 2026)

---

### Summary of Changes Made

**BLOCKER FIXES:**
- ✅ Corrected Analysis Results: evidence_map.py identified as dead code (not imported AND broken schema)
- ✅ Documented that evidence_map.py references non-existent Neo4j relationships
- ✅ Changed from "might integrate" to explicit **DELETE** decision

**HIGH PRIORITY FIXES:**
- ✅ Added Session 2 prep step: "Enumerate all st.session_state keys before extraction"
- ✅ Created session state inventory template with ownership/initialization tracking
- ✅ Updated Session 2 estimate from 4-5 hours to 6-8 hours
- ✅ Added 4 concrete bug fixes to Session 1:
  - session_manager.py line 249: StructuredPaper text_content AttributeError
  - kg_extractor.py line 3: Remove unused `import re`
  - kg_extractor.py lines 69-86: Remove debug print statements
  - research_pipeline.py: Move `import re` to module top

**MEDIUM PRIORITY FIXES:**
- ✅ Removed backward compatibility shim from utils.py plan
- ✅ Changed to direct import updates in deep_researcher.py
- ✅ Updated MANUAL_REVIEW_DECISIONS.md approach: inline checkboxes OR delete after Session 1
- ✅ Pre-decided obvious Session 0 items:
  - database/enrichment/*.py → ARCHIVE (move to scripts/)
  - evidence_map.py → DELETE (broken schema)
  - init_database.py → KEEP (no review needed)
- ✅ Reduced Session 0 from 36 files to ~20 files needing judgment

**LOW PRIORITY FIXES:**
- ✅ Added explicit description of what stays in app.py (~200 lines: page config, routing, imports)
- ✅ Moved backup branch creation to top (Safety First section)
- ✅ Each session gets its own branch (refactor-phase2-session0, session1, session2, session3)

---

## 💬 Staff Engineer Follow-Up Review — Round 2

**Reviewer:** Staff Engineer
**Review Date:** March 4, 2026

Strong revision — all previous blockers and high-priority items resolved. Four remaining issues, all medium or low.

---

**1. MEDIUM: Bug fix A needs a specific action, not two options**

Step 1A says: `# FIX: Remove text_content field or check StructuredPaper schema`. The word "or" leaves the engineer guessing. These are different fixes with different implications — one changes a caller, the other changes a data model shared across the codebase.

The correct fix is to **remove `text_content=""` from the constructor call in `session_manager.py`**. The fallback code at line 249 is creating a minimal `StructuredPaper` for display purposes only. It doesn't need `text_content` — the field simply shouldn't be passed. Adding `text_content` to the dataclass would be the wrong fix because the field has no meaning in the rest of the codebase.

Update the fix description to be explicit:
```python
# FIX: Remove the text_content="" argument from the StructuredPaper() constructor call.
# Do NOT add text_content to the StructuredPaper dataclass — it has no meaning there.
```

---

**2. MEDIUM: database/enrichment/ has orphaned log files after Step 3B**

Step 3B moves the three Python scripts out of `database/enrichment/` into `scripts/database_maintenance/`, but the folder also contains three log files: `enrichment_log.json`, `retry_log.json`, `smart_section_log.json`. After the move, these files remain in `database/enrichment/` with their parent scripts gone. The plan needs to address them — either move them alongside the scripts, add them to `.gitignore`, or delete them. Add a line to Step 3B:

```bash
# Also handle the log files left behind:
mv database/enrichment/*.json scripts/database_maintenance/
# OR: rm database/enrichment/*.json  (if logs are no longer needed)
rmdir database/enrichment  # Remove the now-empty folder
```

---

**3. MEDIUM: `utils/__init__.py` "exports all" contradicts "no shim" approach**

Session 3 Step 6 says: "Create `utils/__init__.py` that exports everything" — and also says "Update imports in `deep_researcher.py` directly (no backward compat shim)." These two instructions are contradictory. An `__init__.py` that re-exports everything from submodules IS the shim pattern, just placed in `__init__.py` instead of a separate file.

Pick one approach and drop the other:

- **Option A (recommended — clean):** `__init__.py` exists only as a package marker (empty or with a version string). Update `deep_researcher.py` to import from the specific submodule: `from utils.search import search_tavily`. This is consistent with "no shim."
- **Option B:** `__init__.py` re-exports everything so `deep_researcher.py` doesn't need to change. But this is a shim.

The Session 3 checklist already says "Update imports in deep_researcher.py directly" which implies Option A. Update the step description and `__init__.py` note to match: `__init__.py` is a package marker, not a full re-export.

---

**4. LOW: Working directory context missing from Step 1 and Step 4 commands**

Step 1 (bug fixes) ends with:
```bash
git add src/session_manager.py src/kg_extractor.py src/research_pipeline.py
```
This assumes the engineer is in `research_assistant_agent/`. Add `cd eduagent/research_assistant_agent` before the git add.

Step 4 (archive unused files) uses:
```bash
mkdir -p archive/2026-03-04
```
Without a working directory, the archive folder could land anywhere. Specify `cd eduagent` before this command so it creates `eduagent/archive/2026-03-04/` consistently.

---

**Summary:** Four targeted fixes needed. Once addressed, plan is ready to execute.

---

**Last Updated:** March 4, 2026
**Status:** Ready for execution
