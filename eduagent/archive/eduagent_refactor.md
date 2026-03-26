# EDU Agent Refactoring Plan

**Date:** March 3, 2026 (Revised after Staff Engineer Review)
**Goal:** Clean up codebase, remove unnecessary code, and create clear structure
**Timeline:** 1-2 focused sessions (3-5 hours total)
**Priority:** Maintain all current functionality (research paper extraction, KG population, report generation)

**Approach:** Quick cleanup and organization, NOT comprehensive refactoring
- Focus: Remove duplication, fix structural issues, organize files
- Test incrementally after each change to catch issues early
- Keep scripts and JSONs at root (scripts are never used, no need to fix paths)

---

## 🚨 SAFETY FIRST - READ BEFORE STARTING

**⚠️ CRITICAL: Do this BEFORE any other steps**

```bash
# Navigate to the repo root
cd /Users/alymoosa/Documents/A-Moosa-Dev/AI-EDU-Dev

# Create backup branch
git checkout -b refactor-eduagent-backup
git add -A
git commit -m "Backup before refactoring cleanup - $(date)"

# Create working branch
git checkout -b refactor-eduagent-session1
```

**After each major step in the plan:**
```bash
# Commit incrementally
git add .
git commit -m "Descriptive message about what was done"
```

**If something breaks:**
```bash
# Easy rollback
git checkout refactor-eduagent-backup
```

---

## 📊 Current State Analysis

### Structure Overview
```
eduagent/
├── open_deep_research/           # Deep research engine
│   ├── src/
│   │   ├── open_deep_research/   # ✅ Active code (5 files)
│   │   ├── legacy/               # 🔴 OLD CODE - UNUSED (13 files, ~1500 lines)
│   │   └── security/             # Auth (1 file)
│   ├── tests/                    # ✅ Evaluation scripts (kept as-is)
│   ├── audit_logs/               # 🔴 8 audit log JSON files (should not be in git)
│   ├── examples/                 # ✅ Example outputs (kept as-is)
│   └── [Config files]
│
└── research_assistant_agent/     # Knowledge management
    ├── src/                      # Core logic (8 files)
    ├── database enrichement/     # 🔴 TYPO + enrichment scripts (6 files)
    ├── tests/integration/        # ✅ API tests (kept as-is)
    ├── docs/                     # Documentation (1 file)
    ├── app.py                    # Main Streamlit app (1,163 lines - out of scope)
    ├── [6 JSON files at root]    # 🔴 WWC mapping data (kept at root, scripts expect them there)
    ├── [5 utility scripts]       # 🔴 Never used, have hardcoded paths (kept at root)
    └── [10+ documentation files] # 🟡 Deferred for later consolidation
```

### Key Issues to Fix

1. **Folder naming:** `database enrichement/` has typo (should be `database/enrichment/`)
2. **Legacy code:** 13 unused files (~1,500 lines) in `open_deep_research/src/legacy/`
3. **Audit logs:** 8 JSON files committed to git
4. **app.py size:** 1,163 lines (noted as out of scope - tracked separately)

### Verified Facts

✅ **Legacy code confirmed unused:**
- Active implementation: `src/open_deep_research/deep_researcher.py`
- No imports found outside legacy folder
- Safe to delete

✅ **Scripts never used:**
- 5 utility scripts at root have hardcoded file paths
- Won't be updated (not worth the effort since never used)
- Kept at root, documented for reference

✅ **JSON files (6 total):**
- All are WWC mapping data
- Scripts expect them at root level
- Kept at root (moving would break scripts unnecessarily)

---

## 🎯 Session-Based Refactoring Plan

### SESSION 1: Cleanup & Organization (2-3 hours)

---

#### Step 1: Fix Database Folder Typo (10 min)

**Current structure:**
```
research_assistant_agent/
└── database enrichement/    # Typo + space in name
    └── [6 files inside]
```

**Target structure:**
```
research_assistant_agent/
└── database/
    └── enrichment/          # Fixed typo, nested structure
        └── [6 files inside]
```

**Pre-check:**
```bash
cd research_assistant_agent
ls -la "database enrichement"    # Confirm folder exists
```

**Commands:**
```bash
# Rename folder (removes space and typo)
mv "database enrichement" database_temp

# Create proper nested structure
mkdir -p database/enrichment

# Move files into nested structure
mv database_temp/* database/enrichment/

# Remove temporary folder
rmdir database_temp
```

**Verify:**
```bash
ls -la database/enrichment/     # Should show 6 files
grep -r "database enrichement" .  # Check for references in all files
```

**Expected result:** No references found (folder not imported, only scripts reference it which are never used)

**If any results are returned:** Update the referenced path in each file before committing.

**Commit:**
```bash
git add .
git commit -m "Step 1: Fix database folder typo (enrichement → enrichment)"
```

---

#### Step 2: Remove Legacy Code (10 min)

**What's being removed:**
```
open_deep_research/src/legacy/     # 13 files, ~1,500 lines
├── __init__.py
├── configuration.py
├── graph.py                       # Old graph-based implementation
├── multi_agent.py                 # Old multi-agent implementation
├── prompts.py
├── state.py
├── utils.py
├── CLAUDE.md
├── legacy.md
├── files/vibe_code.md
└── tests/
    ├── conftest.py
    ├── run_test.py
    └── test_report_quality.py
```

**Why safe:** Active code uses `deep_researcher.py`, not legacy implementations. Verified no imports outside legacy folder.

**Pre-check:**
```bash
cd ../open_deep_research
ls -la src/legacy/                 # Confirm folder exists
```

**Commands:**
```bash
rm -rf src/legacy/
```

**Verify:**
```bash
ls src/                            # Should not show legacy/
grep -r "from.*legacy\|import.*legacy" src/ tests/ --include="*.py"  # Should be empty
```

**Commit:**
```bash
git add .
git commit -m "Step 2: Remove unused legacy code (1,500 lines)"
```

---

#### Step 3: Remove Audit Logs (5 min)

**What's being removed:**
```
open_deep_research/audit_logs/
├── audit_2025-12-11_163116.json
├── audit_2025-12-11_163143.json
├── audit_2025-12-17_222728.json
├── audit_2025-12-17_222801.json
├── audit_2026-02-02_220640.json
├── audit_2026-02-02_220648.json
├── audit_2026-02-02_220651.json
└── audit_2026-02-02_220711.json
```

**Why:** Log files should not be committed to git

**Pre-check:**
```bash
ls -la audit_logs/                 # Confirm logs exist
```

**Commands:**
```bash
# Remove audit logs entirely
rm -rf audit_logs/

# Add to .gitignore
echo "" >> .gitignore
echo "# Audit logs and runtime logs" >> .gitignore
echo "audit_logs/" >> .gitignore
echo "*.log" >> .gitignore
```

**Verify:**
```bash
ls audit_logs/ 2>&1               # Should show "No such file or directory"
cat .gitignore                     # Should include audit_logs/
```

**Commit:**
```bash
git add .
git commit -m "Step 3: Remove audit logs from git and update .gitignore"
```

---

#### Step 4: Quick Smoke Test (15 min)

**Test after Steps 1-3 to catch issues early**

**Test 1: Check Neo4j Connection**
```bash
cd ../../research_assistant_agent
python3 -c "from src.neo4j_config import test_connection; print('Neo4j OK' if test_connection() else 'Neo4j FAILED')"
```

**Test 2: Import Core Modules**
```bash
python3 -c "from src.kg_extractor import extract_paper_from_url; print('kg_extractor OK')"
python3 -c "from src.research_pipeline import ResearchPipeline; print('research_pipeline OK')"
```

**Test 3: Launch Streamlit App**
```bash
streamlit run app.py
# Should load without errors
# Test: Navigate to each tab, verify no crashes
# Then: Ctrl+C to stop
```

**If any test fails:** Check commit history, investigate which step caused the issue

**If all tests pass:**
```bash
git add .
git commit -m "Step 4: Smoke tests passed after initial cleanup"
```

---

### SESSION 2: Documentation & Final Verification (1-2 hours)

---

#### Step 1: Update Documentation Files (30 min)

**Deferred:** Full documentation consolidation (10+ files) requires careful content mapping. This is saved for a future session.

**For now:** Create a simple note documenting the changes

**Commands:**
```bash
cd ..   # eduagent/ root

# Create a cleanup notes file
cat > CLEANUP_NOTES.md << 'EOF'
# Cleanup Notes (March 3, 2026)

## Changes Made

### 1. Fixed Database Folder Structure
- **Before:** `database enrichement/` (typo + space)
- **After:** `database/enrichment/` (nested, proper naming)
- **Note:** Utility scripts at root may have old paths, but scripts are never used

### 2. Removed Legacy Code
- Deleted: `open_deep_research/src/legacy/` (13 files, ~1,500 lines)
- Reason: Unused old implementations (graph-based, multi-agent)
- Active code: Uses `deep_researcher.py`

### 3. Removed Audit Logs
- Deleted: `open_deep_research/audit_logs/*.json` (8 files)
- Added to `.gitignore`

### 4. Files Kept At Root (Unchanged)

**JSON files (6):**
- `all_40_interventions_data.json`
- `all_40_interventions_fresh_mapping.json`
- `missing_interventions_to_map.json`
- `wwc_level3_mapped.json`
- `wwc_level3_metrics.json`
- `wwc_mapping_results.json`

**Utility scripts (5):**
- `init_database.py`
- `migrate_schema.py`
- `process_wwc_data.py`
- `import_wwc_to_neo4j.py` (has hardcoded paths)
- `map_wwc_to_ios.py` (has hardcoded paths)

These scripts are **never used** and have hardcoded file paths expecting files at root.
Paths were not updated since scripts aren't needed.

### 5. Out of Scope (For Future Work)

**app.py (1,163 lines):**
- Flagged for potential modularization
- Out of scope for this cleanup
- Tracked separately for future refactoring

**Documentation consolidation:**
- 10+ overlapping doc files
- Needs careful content mapping
- Deferred to future session

**Test coverage:**
- Only 3 integration tests currently
- Future work: Add unit tests

## Folders/Files Kept As-Is

- `open_deep_research/tests/` - Evaluation scripts (working)
- `open_deep_research/examples/` - Example outputs (reference)
- `research_assistant_agent/tests/integration/` - API tests (working)
- `research_assistant_agent/docs/` - Existing docs (to be consolidated later)

## Next Steps (Future Sessions)

1. Consolidate documentation (10 files → 5 focused docs)
2. Consider app.py modularization (if needed)
3. Add unit test infrastructure
4. Clean up unused scripts (if truly never needed)
EOF

cat CLEANUP_NOTES.md  # Review the content
```

**Commit:**
```bash
git add CLEANUP_NOTES.md
git commit -m "Step 1: Add cleanup notes documenting changes"
```

---

#### Step 2: Run Integration Tests (20 min)

**Run existing tests:**
```bash
cd tests/integration
pytest -v

# Expected: All tests should pass
# If any fail: Investigate which cleanup step broke them
```

**Check open_deep_research tests:**
```bash
cd ../../open_deep_research/tests
ls -la                           # Note: These are kept as-is (evaluation scripts)

# Optional: Try running them if you want
# python run_evaluate.py
```

---

#### Step 3: Comprehensive Manual Testing (30 min)

**Test checklist - verify all key features work:**

```bash
cd ../../research_assistant_agent
streamlit run app.py
```

**In the app:**
- [ ] App loads without errors
- [ ] Neo4j connection indicator shows green
- [ ] **Research Tab:**
  - [ ] Can enter a research query
  - [ ] Can start research process
  - [ ] Can view results
- [ ] **Evidence Map Tab:**
  - [ ] Can view knowledge graph
  - [ ] Can browse papers
  - [ ] Can see evidence gaps
- [ ] **History Tab:**
  - [ ] Can view past research sessions
  - [ ] Can load previous results

**If any feature is broken:**
- Check git history
- Identify which step caused the issue
- Use `git checkout refactor-eduagent-backup` if needed to rollback

**If all tests pass:**
```bash
git add .
git commit -m "Step 3: Manual testing complete - all features working"
```

---

#### Step 4: Final Verification & Cleanup (10 min)

**Review what was accomplished:**
```bash
# Count lines of code removed
git diff refactor-eduagent-backup..HEAD --stat

# Review all commits
git log --oneline refactor-eduagent-backup..HEAD
```

**Final checks:**
```bash
cd research_assistant_agent

# Verify folder structure
ls -la database/enrichment/      # Should show 6 files
ls *.json | wc -l                 # Should show 6 (ls -la adds header line)
ls -la *.py                       # Should show app.py + 6 scripts

cd ../open_deep_research
ls -la src/                       # Should NOT show legacy/
ls -la audit_logs/ 2>&1           # Should show "No such file"
```

**Final commit:**
```bash
git add .
git commit -m "Session 2 complete: All tests passing, cleanup successful"
```

---

## ✅ Session Checklists

### SESSION 1: Cleanup & Organization (Completed: [ ])
- [ ] Safety: Create backup branches
- [ ] Step 1: Fix `database enrichement` → `database/enrichment/`
- [ ] Step 2: Remove legacy code (13 files)
- [ ] Step 3: Remove audit logs (8 files)
- [ ] Step 4: Run smoke tests (Neo4j, imports, app launch)
- [ ] Commit after each step

**Estimated time:** 2-3 hours

### SESSION 2: Documentation & Verification (Completed: [ ])
- [ ] Step 1: Create CLEANUP_NOTES.md
- [ ] Step 2: Run integration tests
- [ ] Step 3: Comprehensive manual testing (all features)
- [ ] Step 4: Final verification
- [ ] Review git history and diffs

**Estimated time:** 1-2 hours

---

## 🎯 Expected Results

### Before Cleanup
- **Code:** ~8,000 lines (including 1,500 lines of unused legacy code)
- **Folder Issues:** 1 typo (`enrichement`), audit logs in git
- **Structure:** Scattered files, unclear what's active vs. legacy

### After Cleanup
- **Code:** ~6,500 lines (19% reduction, legacy removed)
- **Folder Issues:** 0 (clean structure, proper naming)
- **Structure:** Clear separation, documented what's kept vs. removed
- **Git:** No log files, clean history

### What Changed
✅ Fixed database folder typo
✅ Removed 1,500 lines of unused legacy code
✅ Removed audit logs from git
✅ Documented cleanup in CLEANUP_NOTES.md
✅ All tests passing

### What Stayed the Same
- app.py (1,163 lines - out of scope)
- 6 JSON files at root (scripts expect them there)
- 5 utility scripts at root (never used, not worth fixing)
- 10+ documentation files (deferred for future consolidation)
- All active functionality intact

---

## 📝 Important Notes

### Files With Outdated Paths (Not Fixed - Scripts Never Used)

**These scripts have hardcoded paths but are NEVER used:**

1. **`import_wwc_to_neo4j.py`**
   - Expects: `wwc_level3_mapped.json` at same directory
   - Expects: `../kg-viz-frontend/level-3/Interventions_Studies_And_Findings.csv`

2. **`map_wwc_to_ios.py`**
   - Has hardcoded absolute path: `/Users/alymoosa/Documents/A-Moosa-Dev/AI-EDU-Dev/research_assistant/`
   - Expects: `wwc_level3_metrics.json`, `wwc_level3_mapped.json`, `wwc_mapping_results.json`

3. **`process_wwc_data.py`**
   - Expects: `wwc_level3_metrics.json` at same directory
   - Expects: `../kg-viz-frontend/level-3/Interventions_Studies_And_Findings.csv`

**Why not fixed:** Scripts are never used. If they're needed in the future, paths can be updated then.

### Out of Scope for This Cleanup

1. **app.py modularization** (1,163 lines)
   - Flagged as a code quality issue
   - Would require 1-2 weeks of careful refactoring
   - Tracked separately for future work
   - Current priority: Leave functional, address later if needed

2. **Documentation consolidation** (10+ files → 5 focused docs)
   - Requires careful content mapping
   - Risk of losing important information
   - Deferred to future session when there's time to do it properly

3. **Test infrastructure improvements**
   - Only 3 integration tests currently
   - Adding unit tests would be multi-week effort
   - Out of scope for quick cleanup

4. **Data folder organization**
   - Originally planned to move JSONs to `data/wwc/mappings/`
   - Would break 3 scripts that expect files at root
   - Not worth effort since scripts never used
   - Kept at root for simplicity

---

## 🚀 Ready to Execute?

**When ready to start Session 1:**
1. Read "SAFETY FIRST" section at top
2. Create backup branches
3. Follow Session 1 steps in order
4. Test after each major step
5. Commit incrementally

**After Session 1:**
- Take a break
- Review what was done
- Schedule Session 2 when ready

**Total time estimate:** 3-5 hours across both sessions

---

## 💬 Staff Engineer Review - ADDRESSED

All feedback from staff engineer review has been addressed:

### BLOCKERS - ✅ Fixed
- [x] Safety First moved to top of document
- [x] Folder rename commands now consistent and verified
- [x] JSON files explicitly inventoried (6 files listed by name)

### HIGH Priority - ✅ Fixed
- [x] Import updates ordered immediately after each move
- [x] Incremental testing added (after Steps 1-3, not just at end)
- [x] Scripts analyzed for dependencies and documented

### MEDIUM Priority - ✅ Fixed
- [x] Scripts noted as never used, paths not updated
- [x] Documentation consolidation explicitly deferred
- [x] app.py status clarified (out of scope, tracked separately)

### LOW Priority - ✅ Fixed
- [x] open_deep_research tests noted as kept as-is
- [x] data/config/ removed (not creating empty folders)
- [x] examples/ folder noted as kept as-is

### SUGGESTION - ✅ Implemented
- [x] Pre-move checks added (ls commands before each mv)

---

## 💬 Staff Engineer Follow-Up Review — Round 2

**Review Date:** March 3, 2026

Good progress — all blockers and high-priority items from Round 1 are resolved. Four minor issues remain before execution:

**1. `ls -la *.json | wc -l` will return 7, not 6 (Session 2, Step 4)** ✅ FIXED
`ls -la` includes a "total" header line in its output, so `wc -l` will be off by one.
- Changed to: `ls *.json | wc -l`

**2. Step 1 grep is too narrow — will miss file path string references** ✅ FIXED
The current verify command only searches `.py` files for the folder name as a Python import. If `app.py` or any script references the folder as a string path (e.g. `open("database enrichement/file.json")`), this grep would miss it.
- Changed to: `grep -r "database enrichement" .` (searches all files)

**3. No contingency if the Step 1 grep returns results** ✅ FIXED
The plan says "Expected result: No references found" but gives no guidance on what to do if something *is* found.
- Added: "If any results are returned: Update the referenced path in each file before committing."

**4. `CLEANUP_NOTES.md` is placed in the wrong directory** ✅ FIXED
It's created inside `research_assistant_agent/` but documents changes that span both `research_assistant_agent/` and `open_deep_research/`.
- Changed to: `cd ..` (creates at eduagent/ root)

---

**All Round 2 feedback addressed. Plan is ready for execution.**

---

**Last Updated:** March 3, 2026 (Post staff engineer review — Round 2, all issues fixed)
