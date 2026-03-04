# EDU Agent Refactoring Plan - Phase 2 (Deep Cleanup)

**Date:** March 3, 2026
**Based on:** Comprehensive code usage analysis (CLEANUP_INVENTORY.md)
**Timeline:** 4 sessions (10-15 hours total)

---

## 📊 Analysis Results Summary

**Good News:**
- ✅ **No dead code found** - All 36 Python files serve a purpose
- ✅ Well-structured architecture with clear separation
- ✅ Good test coverage in both projects
- ✅ Active documentation

**Areas for Improvement:**
- 🗑️ **2 duplicate docs** to delete
- 🔍 **3 files** need review (potentially unused)
- 🚨 **4 large files** need breaking up (>500 lines each)
- ⚠️ **36 files** need manual human review (even if being used)

**Critical Insight:**
Just because a file is **imported/used** doesn't mean it **should exist**. Session 0 provides human judgment on:
- Is this feature still wanted?
- Is this the right technical approach?
- Should this be deleted/moved/consolidated?

---

## 🎯 Four-Session Plan

### SESSION 0: Manual Review (2-3 hours)

**IMPORTANT:** Even if a file is being imported/used, it might still need to be deleted, moved, or consolidated. This session reviews each file to make human judgment calls about whether it should exist at all.

---

#### Manual Review Checklist

For each file, ask:
1. **Should this feature exist?** (Product decision)
2. **Is this the right approach?** (Technical decision)
3. **Is this duplicating functionality?** (Could be consolidated)
4. **Is this in the right location?** (Organizational)
5. **Is this technical debt?** (Should be replaced/removed)

**Review all 36 Python files and make decisions:**

---

#### 0.1 Open Deep Research Files (15 files)

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

#### 0.2 Research Assistant Agent Files (21 files)

**Entry Point:**
- [ ] `app.py` (1163 lines) - **Decision:** KEEP / DELETE / MOVE / CONSOLIDATE

**Core Active Files:**
- [ ] `src/neo4j_config.py` (207 lines) - **Decision:** KEEP / DELETE / MOVE / CONSOLIDATE
- [ ] `src/kg_extractor.py` (527 lines) - **Decision:** KEEP / DELETE / MOVE / CONSOLIDATE
- [ ] `src/research_pipeline.py` (458 lines) - **Decision:** KEEP / DELETE / MOVE / CONSOLIDATE
- [ ] `src/session_manager.py` (279 lines) - **Decision:** KEEP / DELETE / MOVE / CONSOLIDATE
- [ ] `src/enhanced_extraction_prompt.py` (298 lines) - **Decision:** KEEP / DELETE / MOVE / CONSOLIDATE
- [ ] `src/env_config.py` (80 lines) - **Decision:** KEEP / DELETE / MOVE / CONSOLIDATE
- [ ] `src/evidence_map.py` (305 lines) - **Decision:** KEEP / DELETE / MOVE / CONSOLIDATE
  - *Note: Not imported anywhere - is this feature wanted?*

**WWC Data Processing Scripts:**
- [ ] `import_wwc_to_neo4j.py` (514 lines) - **Decision:** KEEP / DELETE / ARCHIVE
- [ ] `process_wwc_data.py` (425 lines) - **Decision:** KEEP / DELETE / ARCHIVE
- [ ] `map_wwc_to_ios.py` (254 lines) - **Decision:** KEEP / DELETE / ARCHIVE
- [ ] `migrate_schema.py` (187 lines) - **Decision:** KEEP / DELETE / ARCHIVE

**Database Enrichment Scripts:**
- [ ] `database/enrichment/enrich_existing_papers.py` (414 lines) - **Decision:** KEEP / DELETE / ARCHIVE
- [ ] `database/enrichment/retry_failed_papers.py` (174 lines) - **Decision:** KEEP / DELETE / ARCHIVE
- [ ] `database/enrichment/smart_section_retry.py` (239 lines) - **Decision:** KEEP / DELETE / ARCHIVE

**Utility Scripts:**
- [ ] `init_database.py` (7 lines) - **Decision:** KEEP / DELETE / ARCHIVE
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

Create `MANUAL_REVIEW_DECISIONS.md` with:

```markdown
# Manual Review Decisions

## Files to DELETE (even though used)
- `filename.py` - Reason: [why it should be deleted]

## Files to MOVE
- `filename.py` - Move from: X, Move to: Y, Reason: [why]

## Files to CONSOLIDATE
- `filename1.py` + `filename2.py` → `new_filename.py` - Reason: [why]

## Files to ARCHIVE
- `filename.py` - Reason: [not active but keep for reference]

## Files to KEEP
- All other files (list if needed)
```

**Output:** Clear action plan based on human judgment, not just automated import analysis.

---

### SESSION 1: Quick Wins (2 hours)

Low-risk cleanup - delete duplicates and execute decisions from manual review.

---

#### Step 1: Delete Duplicate Documentation (5 min)

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

#### Step 2: Review Potentially Unused Files (1-2 hours)

**Files to investigate:**

**A. `research_assistant_agent/src/evidence_map.py` (305 lines)**
- **Status:** NOT imported anywhere
- **Contains:** Evidence gap map visualization queries
- **Decision needed:**
  - **Option 1:** Is this feature planned? → Integrate into app.py
  - **Option 2:** Feature abandoned? → Delete
  - **Option 3:** Might use later? → Move to archive/

**Investigation:**
```bash
# Check if referenced in docs or comments
grep -r "evidence_map" --include="*.py" --include="*.md" eduagent/
```

**B. `open_deep_research/tests/extract_langsmith_data.py` (82 lines)**
- **Status:** Utility for extracting LangSmith evaluation data
- **Decision needed:** Still used for evals? Or archive?

**C. `research_assistant_agent/SEPARATION_README.md`**
- **Status:** Documentation about code separation
- **Decision needed:** Is separation complete? Archive if outdated.

**Actions:**
```bash
# If deleting:
rm research_assistant_agent/src/evidence_map.py
rm open_deep_research/tests/extract_langsmith_data.py
rm research_assistant_agent/SEPARATION_README.md

# If archiving:
mkdir -p archive/2026-03-03
mv research_assistant_agent/src/evidence_map.py archive/2026-03-03/
mv open_deep_research/tests/extract_langsmith_data.py archive/2026-03-03/
mv research_assistant_agent/SEPARATION_README.md archive/2026-03-03/
```

**Risk:** Low - not imported by active code
**Files affected:** 0-3 files (depending on decisions)

---

### SESSION 2: Critical Refactoring - Part 1 (4-5 hours)

Break up the two largest files.

---

#### Step 3: Refactor `app.py` (1,163 lines → ~300 lines) [4-5 hours]

**Current problem:** Monolithic Streamlit app - everything in one file

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

**Benefits:**
- Each component is self-contained and testable
- Easier to modify individual features
- Clearer code organization
- Better for new developers

**Approach:**
1. Create `ui/` folder structure
2. Extract sidebar logic → `ui/sidebar.py`
3. Extract visualization → `ui/visualization.py`
4. Extract chat interface → `ui/chat.py`
5. Extract results display → `ui/results.py`
6. Update `app.py` to import from ui modules
7. Test thoroughly after each extraction

**Testing checklist:**
- [ ] App loads without errors
- [ ] Sidebar configuration works
- [ ] Graph visualization renders
- [ ] Chat interface functional
- [ ] Results display correctly
- [ ] All tabs navigate properly

**Risk:** Medium - requires thorough testing
**Files affected:** 1 file split into 6 files

---

### SESSION 3: Critical Refactoring - Part 2 (2-3 hours)

Break up utils.py and optionally other large files.

---

#### Step 4: Refactor `utils.py` (1,071 lines → ~300 lines) [2-3 hours]

**File:** `open_deep_research/src/open_deep_research/utils.py`

**Current problem:** Giant utilities file with everything

**Proposed structure:**
```
open_deep_research/src/open_deep_research/
├── utils.py (backward compatibility shim, ~50 lines)
└── utils/
    ├── __init__.py (export all)
    ├── search.py (~300 lines) - Tavily, DuckDuckGo, Exa search
    ├── web.py (~250 lines) - Web scraping, summarization
    ├── llm.py (~200 lines) - LLM interaction helpers
    └── mcp.py (~150 lines) - MCP server utilities
```

**Benefits:**
- Much easier to navigate
- Clear separation by function
- Easier to test individual components
- Better dependency management

**Approach:**
1. Create `utils/` folder
2. Split functions by category into new files
3. Create `utils/__init__.py` that exports everything
4. Update `utils.py` to import from `utils/` (backward compatibility)
5. Update imports in `deep_researcher.py`
6. Test all search and web scraping functionality

**Testing checklist:**
- [ ] Search functions work (Tavily, DuckDuckGo, Exa)
- [ ] Web scraping works
- [ ] LLM interaction works
- [ ] MCP servers work
- [ ] All tests pass

**Risk:** Medium - many imports to update
**Files affected:** 1 file split into 5 files

---

#### Step 5 (OPTIONAL): Refactor `deep_researcher.py` (718 lines → ~250 lines) [If time]

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
- ✅ Every file reviewed with human judgment
- ✅ Clear decisions documented in MANUAL_REVIEW_DECISIONS.md
- ✅ Action plan for deletions, moves, consolidations

### After Session 1:
- ✅ No duplicate documentation
- ✅ Clear decisions on potentially unused files
- ✅ Archive folder created (if needed)

### After Session 2:
- ✅ `app.py` is manageable size (<300 lines)
- ✅ UI components are in separate files
- ✅ All app features still work

### After Session 3:
- ✅ `utils.py` is split into focused modules
- ✅ All search and web functionality works
- ✅ (Optional) `deep_researcher.py` has clear node separation

---

## 📋 Session Checklists

### SESSION 0: Manual Review
- [ ] Review all 15 open_deep_research Python files
- [ ] Review all 21 research_assistant_agent Python files
- [ ] For each file, decide: KEEP / DELETE / MOVE / CONSOLIDATE / ARCHIVE
- [ ] Document all decisions in MANUAL_REVIEW_DECISIONS.md
- [ ] Create action plan based on decisions
- [ ] Get user/product approval on deletions

**Estimated time:** 2-3 hours

### SESSION 1: Quick Wins
- [ ] Delete 2 duplicate EDUAGENT_OVERVIEW.md files
- [ ] Review evidence_map.py - decide: integrate/delete/archive
- [ ] Review extract_langsmith_data.py - decide: keep/archive
- [ ] Review SEPARATION_README.md - decide: keep/archive
- [ ] Create archive/ folder if archiving files
- [ ] Commit all changes

**Estimated time:** 2 hours

### SESSION 2: Refactor app.py
- [ ] Create ui/ folder structure
- [ ] Extract sidebar → ui/sidebar.py
- [ ] Extract visualization → ui/visualization.py
- [ ] Extract chat → ui/chat.py
- [ ] Extract results → ui/results.py
- [ ] Update app.py imports
- [ ] Test all features work
- [ ] Commit after each extraction

**Estimated time:** 4-5 hours

### SESSION 3: Refactor utils.py
- [ ] Create utils/ folder
- [ ] Split search functions → utils/search.py
- [ ] Split web functions → utils/web.py
- [ ] Split LLM functions → utils/llm.py
- [ ] Split MCP functions → utils/mcp.py
- [ ] Update utils.py for backward compatibility
- [ ] Update imports in deep_researcher.py
- [ ] Test all functionality
- [ ] (Optional) Refactor deep_researcher.py
- [ ] Commit all changes

**Estimated time:** 2-3 hours (4-5 if including deep_researcher.py)

---

## 🎯 Expected Results

### Before Phase 2:
- **Duplicate docs:** 2 files
- **Potentially unused:** 3 files
- **Very large files (>1000 lines):** 2 files (app.py, utils.py)
- **Large files (500-1000 lines):** 2 files (deep_researcher.py, kg_extractor.py)

### After Phase 2:
- **Duplicate docs:** 0 files
- **Potentially unused:** 0 files (all reviewed)
- **Very large files (>1000 lines):** 0 files
- **Large files (500-1000 lines):** 1-2 files (depending on optional refactoring)
- **New structure:** Clean component-based organization

### Code Quality Improvements:
- ✅ Better maintainability
- ✅ Easier to onboard new developers
- ✅ Clearer separation of concerns
- ✅ Better testability
- ✅ Easier to modify features

---

## ⚠️ Risks & Mitigation

### Medium Risk: app.py Refactoring
**Risk:** Streamlit state management might break
**Mitigation:**
- Test after each extraction
- Keep backup branch
- Commit incrementally

### Medium Risk: utils.py Refactoring
**Risk:** Many imports to update, might miss some
**Mitigation:**
- Create backward compatibility shim
- Run all tests after changes
- Use IDE refactoring tools if available

### Low Risk: Everything Else
**Mitigation:** Standard git backup and testing

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
2. **Session 1** - Quick wins, execute decisions from manual review
3. **Session 2** - Biggest pain point (app.py), highest impact
4. **Session 3** - Second biggest pain point (utils.py), high impact

---

## 🚀 Ready to Start?

**Prerequisites:**
1. Complete Phase 1 cleanup (already done!)
2. Review this plan
3. Get staff engineer approval
4. Schedule 3 focused sessions

**When ready:**
```bash
# Create new working branch
git checkout -b refactor-phase2-session1
```

---

**Last Updated:** March 3, 2026
**Status:** Ready for staff engineer review
