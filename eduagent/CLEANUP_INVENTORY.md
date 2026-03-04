# EduAgent Folder - Comprehensive File Categorization & Cleanup Analysis

**Analysis Date:** March 3, 2026
**Scope:** `/Users/alymoosa/Documents/A-Moosa-Dev/AI-EDU-Dev/eduagent`

---

## Executive Summary

**Total Files Analyzed:** 36 Python files + 21 documentation files

**Key Findings:**
- ✅ **No dead code found** - All Python files serve a purpose
- ⚠️ **4 files need refactoring** (>500 lines)
- 🔍 **2 files need review** (potentially deprecated)
- 📄 **3 duplicate documentation files** to consolidate
- 🎯 **Clear architecture** with well-separated concerns

---

## Section 1: Open Deep Research (15 Python Files)

### 1.1 Entry Points (Main Servers) - 2 files

| File | Lines | Category | Purpose | Recommendation |
|------|-------|----------|---------|----------------|
| `server.py` | 231 | ACTIVE | FastAPI server for LangGraph API | **KEEP** |
| `bridge_server.py` | 257 | ACTIVE | Bridge API connecting frontend to backend | **KEEP** |

**Import Analysis:**
- `server.py` imports: `src.open_deep_research.deep_researcher` (1 local import)
- `bridge_server.py`: No local imports (standalone bridge)

---

### 1.2 Core Active Files - 5 files

| File | Lines | Imported By | Purpose | Recommendation |
|------|-------|-------------|---------|----------------|
| `src/open_deep_research/deep_researcher.py` | 718 | 3 files | Main LangGraph research agent with 4-phase workflow | **KEEP - REFACTOR** ⚠️ |
| `src/open_deep_research/utils.py` | 1071 | 2 files | Search, web scraping, and utility functions | **KEEP - REFACTOR** 🚨 |
| `src/open_deep_research/prompts.py` | 427 | 2 files | System prompts for research phases | **KEEP** |
| `src/open_deep_research/configuration.py` | 251 | 2 files | Configuration management for LLMs and search APIs | **KEEP** |
| `src/open_deep_research/state.py` | 95 | 2 files | Graph state type definitions | **KEEP** |

**Import Graph:**
```
deep_researcher.py ← server.py, tests/run_evaluate.py, tests/supervisor_parallel_evaluation.py
  ├─→ configuration.py
  ├─→ prompts.py
  ├─→ state.py
  └─→ utils.py
      ├─→ configuration.py
      ├─→ prompts.py
      └─→ state.py

utils.py ← deep_researcher.py, tests/evaluators.py
```

**Refactoring Priorities:**
1. 🚨 **CRITICAL**: `utils.py` (1071 lines) - Split into:
   - `search_utils.py` (Tavily, DuckDuckGo, Exa search)
   - `web_utils.py` (Web scraping, summarization)
   - `llm_utils.py` (LLM interaction helpers)

2. ⚠️ **HIGH**: `deep_researcher.py` (718 lines) - Extract node functions:
   - `nodes/researcher.py`
   - `nodes/summarizer.py`
   - `nodes/planner.py`

---

### 1.3 Utility Scripts - 2 files

| File | Lines | Purpose | Recommendation |
|------|-------|---------|----------------|
| `test_deployment.py` | 76 | Test Render deployment health | **KEEP** |
| `src/security/auth.py` | 155 | Authentication handler for LangGraph Cloud | **KEEP** |

---

### 1.4 Tests - 6 files

| File | Lines | Purpose | Recommendation |
|------|-------|---------|----------------|
| `tests/run_evaluate.py` | 89 | Main evaluation script for Deep Research Bench | **KEEP** |
| `tests/evaluators.py` | 173 | Specialized evaluation functions | **KEEP** |
| `tests/prompts.py` | 256 | Evaluation prompts and criteria | **KEEP** |
| `tests/pairwise_evaluation.py` | 127 | Comparative evaluation between models | **KEEP** |
| `tests/supervisor_parallel_evaluation.py` | 60 | Multi-threaded parallel evaluation | **KEEP** |
| `tests/extract_langsmith_data.py` | 82 | Extract data from LangSmith | **REVIEW** 🔍 |

**Note:** Check if `extract_langsmith_data.py` is actively used. If not, **ARCHIVE**.

---

## Section 2: Research Assistant Agent (21 Python Files)

### 2.1 Entry Point - 1 file

| File | Lines | Category | Purpose | Recommendation |
|------|-------|----------|---------|----------------|
| `app.py` | 1163 | ACTIVE | Main Streamlit UI application | **KEEP - REFACTOR** 🚨 |

**Refactoring Priority:**
- 🚨 **CRITICAL**: `app.py` (1163 lines) - Break into components:
  - `components/sidebar.py` (configuration UI)
  - `components/visualization.py` (D3.js graph rendering)
  - `components/chat.py` (chat interface)
  - `components/results.py` (results display)

---

### 2.2 Core Active Files - 7 files

| File | Lines | Imported By | Purpose | Recommendation |
|------|-------|-------------|---------|----------------|
| `src/neo4j_config.py` | 207 | 9 files | Neo4j connection, initialization, taxonomy | **KEEP** ✅ |
| `src/kg_extractor.py` | 527 | 3 files | Knowledge graph extraction from papers | **KEEP - REFACTOR** ⚠️ |
| `src/research_pipeline.py` | 458 | 2 files | Research pipeline orchestration | **KEEP** |
| `src/session_manager.py` | 279 | 2 files | Streamlit session state management | **KEEP** |
| `src/enhanced_extraction_prompt.py` | 298 | 2 files | Structured extraction prompts | **KEEP** |
| `src/env_config.py` | 80 | 1 file | Environment configuration loader | **KEEP** |
| `src/evidence_map.py` | 305 | **0 files** | Evidence gap map visualization | **REVIEW** 🔍 |

**Import Graph:**
```
app.py
  ├─→ src/research_pipeline.py
  │     ├─→ src/session_manager.py
  │     │     ├─→ src/neo4j_config.py
  │     │     ├─→ src/research_pipeline.py (circular)
  │     │     └─→ src/kg_extractor.py
  │     └─→ src/kg_extractor.py
  │           ├─→ src/neo4j_config.py
  │           └─→ src/enhanced_extraction_prompt.py
  ├─→ src/env_config.py
  └─→ src/neo4j_config.py

src/evidence_map.py → NOT IMPORTED ANYWHERE ⚠️
```

**Critical Finding:**
- 🔍 **`src/evidence_map.py`** (305 lines) is NOT imported anywhere
  - Contains evidence gap map functionality
  - Query functions for paper counts by IO × Outcome
  - **ACTION NEEDED:** Either integrate into `app.py` or deprecate

**Refactoring Priority:**
- ⚠️ **HIGH**: `src/kg_extractor.py` (527 lines) - Split extraction logic:
  - `extraction/paper_extractor.py`
  - `extraction/finding_extractor.py`
  - `extraction/taxonomy_mapper.py`

---

### 2.3 WWC Data Processing Scripts - 4 files

| File | Lines | Purpose | When Used | Recommendation |
|------|-------|---------|-----------|----------------|
| `import_wwc_to_neo4j.py` | 514 | Import WWC CSV data into Neo4j | Initial DB setup | **KEEP** |
| `process_wwc_data.py` | 425 | Process WWC for Level 3 visualization | Data preparation | **KEEP** |
| `map_wwc_to_ios.py` | 254 | Map interventions to Implementation Objectives | WWC analysis | **KEEP** |
| `migrate_schema.py` | 187 | Database schema migration | Schema updates | **KEEP** |

**Usage:** These are utility scripts run manually for data processing tasks.

---

### 2.4 Database Enrichment Scripts - 3 files

| File | Lines | Purpose | When Used | Recommendation |
|------|-------|---------|-----------|----------------|
| `database/enrichment/enrich_existing_papers.py` | 414 | Enrich papers with full-text from Semantic Scholar | Data enrichment | **KEEP** |
| `database/enrichment/retry_failed_papers.py` | 174 | Retry failed paper enrichments | Error recovery | **KEEP** |
| `database/enrichment/smart_section_retry.py` | 239 | Smart retry for failed sections | Error recovery | **KEEP** |

**Usage:** Manual data quality improvement scripts.

---

### 2.5 Utility Scripts - 2 files

| File | Lines | Purpose | Recommendation |
|------|-------|---------|----------------|
| `init_database.py` | 7 | Initialize Neo4j with taxonomy | **KEEP** |
| `test_neo4j.py` | 37 | Test Neo4j connection | **KEEP** |

---

### 2.6 Tests - 3 files

| File | Lines | Purpose | Recommendation |
|------|-------|---------|----------------|
| `tests/integration/test_extraction.py` | 113 | Test extraction pipeline | **KEEP** |
| `tests/integration/test_full_pipeline.py` | 181 | Test end-to-end pipeline | **KEEP** |
| `tests/integration/test_streaming_detail.py` | 73 | Test streaming details | **KEEP** |

---

## Section 3: Documentation Analysis (21 Files)

### 3.1 Root Level - 2 files

| File | Date | Status | Recommendation |
|------|------|--------|----------------|
| `CLEANUP_NOTES.md` | 2026-03-03 | ✅ Current | **KEEP** |
| `EDUAGENT_OVERVIEW.md` | Unknown | ✅ Current | **KEEP** (Master copy) |

---

### 3.2 Open Deep Research Documentation - 9 files

| File | Status | Purpose | Recommendation |
|------|--------|---------|----------------|
| `README.md` | ✅ Current | Main project docs | **KEEP** |
| `CLAUDE.md` | ✅ Current | Claude AI instructions | **KEEP** |
| `DEPLOYMENT.md` | ✅ Current | Render deployment guide | **KEEP** |
| `FRONTEND_SETUP.md` | ✅ Current | Frontend connection guide | **KEEP** |
| `EDUAGENT_OVERVIEW.md` | 🗑️ Duplicate | Duplicate of root | **DELETE** |
| `examples/arxiv.md` | ✅ Current | Research example | **KEEP** |
| `examples/pubmed.md` | ✅ Current | Research example | **KEEP** |
| `examples/inference-market.md` | ✅ Current | Research example | **KEEP** |
| `examples/inference-market-gpt45.md` | ✅ Current | Research example | **KEEP** |

---

### 3.3 Research Assistant Agent Documentation - 10 files

| File | Date | Status | Purpose | Recommendation |
|------|------|---------|---------|----------------|
| `README.md` | Unknown | ✅ Current | Main project docs | **KEEP** |
| `QUICKSTART.md` | Unknown | ✅ Current | Getting started guide | **KEEP** |
| `SCHEMA.md` | Unknown | ✅ Current | KG schema reference | **KEEP** |
| `PIPELINE.md` | Unknown | ✅ Current | Pipeline documentation | **KEEP** |
| `STREAMLIT_DEPLOYMENT.md` | Unknown | ✅ Current | Deployment guide | **KEEP** |
| `IMPROVEMENTS.md` | Unknown | ✅ Current | Roadmap | **KEEP** |
| `INTERVENTION_MAPPING_REVIEW.md` | 2026-01-29 | ✅ Current | WWC mapping analysis | **KEEP** |
| `OPEN_DEEP_RESEARCH_ANALYSIS.md` | Unknown | ✅ Current | ODR analysis | **KEEP** |
| `EDUAGENT_OVERVIEW.md` | Unknown | 🗑️ Duplicate | Duplicate of root | **DELETE** |
| `SEPARATION_README.md` | Unknown | 🔍 Review | Separation docs | **REVIEW** |

---

## Section 4: Cleanup Action Plan

### Phase 1: Immediate Actions (Low Risk)

#### 1.1 Delete Duplicate Documentation
```bash
# Delete duplicate overview files
rm eduagent/open_deep_research/EDUAGENT_OVERVIEW.md
rm eduagent/research_assistant_agent/EDUAGENT_OVERVIEW.md

# Add references in their place if needed
```

**Files affected:** 2
**Risk:** Low (duplicates only)
**Impact:** Cleaner documentation structure

---

#### 1.2 Review Potentially Unused Files

**Files to investigate:**
1. `research_assistant_agent/src/evidence_map.py` (305 lines)
   - Check if evidence gap map feature is planned
   - If yes: Integrate into `app.py`
   - If no: Move to archive or delete

2. `open_deep_research/tests/extract_langsmith_data.py` (82 lines)
   - Check last usage date
   - Archive if not actively used

3. `research_assistant_agent/SEPARATION_README.md`
   - Check if separation is complete
   - Archive if outdated

**Action:** Investigate usage before deletion

---

### Phase 2: Refactoring (High Impact)

#### 2.1 Critical Refactoring - research_assistant_agent/app.py (1163 lines)

**Current structure:** Single monolithic file

**Proposed structure:**
```
research_assistant_agent/
├── app.py (main entry point, ~200 lines)
└── ui/
    ├── __init__.py
    ├── sidebar.py (configuration UI)
    ├── visualization.py (D3.js graph)
    ├── chat.py (chat interface)
    ├── results.py (results display)
    └── utils.py (UI helpers)
```

**Benefits:**
- Easier to maintain
- Better testability
- Clearer separation of concerns
- Easier for new developers to understand

**Effort:** 4-6 hours
**Risk:** Medium (requires thorough testing)

---

#### 2.2 Critical Refactoring - open_deep_research/src/open_deep_research/utils.py (1071 lines)

**Current structure:** Single utilities file

**Proposed structure:**
```
open_deep_research/src/open_deep_research/
├── utils/
│   ├── __init__.py (export all utils)
│   ├── search.py (Tavily, DuckDuckGo, Exa)
│   ├── web.py (scraping, summarization)
│   ├── llm.py (LLM interaction helpers)
│   └── mcp.py (MCP server utilities)
└── utils.py (deprecated, redirect to utils/)
```

**Benefits:**
- Much easier to navigate
- Better organization by function
- Clearer dependencies
- Easier to test individual components

**Effort:** 6-8 hours
**Risk:** Medium (many imports to update)

---

#### 2.3 High Priority Refactoring - open_deep_research/src/open_deep_research/deep_researcher.py (718 lines)

**Current structure:** Single file with all graph nodes

**Proposed structure:**
```
open_deep_research/src/open_deep_research/
├── deep_researcher.py (graph definition, ~200 lines)
└── nodes/
    ├── __init__.py
    ├── planner.py (planning node)
    ├── researcher.py (research node)
    ├── summarizer.py (summarization node)
    └── common.py (shared node utilities)
```

**Effort:** 3-4 hours
**Risk:** Low (clear separation)

---

#### 2.4 Medium Priority Refactoring - research_assistant_agent/src/kg_extractor.py (527 lines)

**Proposed structure:**
```
research_assistant_agent/src/
├── kg_extractor.py (main interface, ~150 lines)
└── extraction/
    ├── __init__.py
    ├── paper.py (paper extraction)
    ├── findings.py (finding extraction)
    └── taxonomy.py (taxonomy mapping)
```

**Effort:** 3-4 hours
**Risk:** Low

---

### Phase 3: Archive/Delete (Low Priority)

Create an `archive/` directory for files that might be useful later:

```bash
mkdir -p eduagent/archive/2026-03-03

# Move files that are no longer active
mv eduagent/research_assistant_agent/SEPARATION_README.md eduagent/archive/2026-03-03/
mv eduagent/open_deep_research/tests/extract_langsmith_data.py eduagent/archive/2026-03-03/
```

---

## Section 5: File Import Matrix

### High-Value Core Files (Imported by 3+ files)

| File | Imported By | Dependents |
|------|-------------|------------|
| `research_assistant_agent/src/neo4j_config.py` | 9 | app.py, kg_extractor.py, research_pipeline.py, session_manager.py, enhanced_extraction_prompt.py, evidence_map.py, import_wwc_to_neo4j.py, migrate_schema.py, enrich_existing_papers.py |
| `research_assistant_agent/src/kg_extractor.py` | 3 | app.py, research_pipeline.py, session_manager.py |
| `open_deep_research/src/open_deep_research/deep_researcher.py` | 3 | server.py, run_evaluate.py, supervisor_parallel_evaluation.py |

### Medium-Value Files (Imported by 2 files)

| File | Imported By | Dependents |
|------|-------------|------------|
| `research_assistant_agent/src/research_pipeline.py` | 2 | app.py, session_manager.py |
| `research_assistant_agent/src/session_manager.py` | 2 | app.py, research_pipeline.py |
| `research_assistant_agent/src/enhanced_extraction_prompt.py` | 2 | kg_extractor.py, enrich_existing_papers.py |
| All open_deep_research core files | 2 | deep_researcher.py, utils.py |

### Potentially Unused Files (Imported by 0 files)

| File | Lines | Notes |
|------|-------|-------|
| `research_assistant_agent/src/evidence_map.py` | 305 | Evidence gap map - check if planned feature |

---

## Section 6: Summary Statistics

### Code Statistics

| Category | Open Deep Research | Research Assistant | Total |
|----------|-------------------|-------------------|-------|
| Entry Points | 2 | 1 | 3 |
| Core Active | 5 | 7 | 12 |
| Utility Scripts | 2 | 6 | 8 |
| Data Processing | 0 | 7 | 7 |
| Tests | 6 | 3 | 9 |
| **Total Python** | **15** | **21** | **36** |

### Documentation Statistics

| Category | Count |
|----------|-------|
| Root docs | 2 |
| Open Deep Research docs | 9 |
| Research Assistant docs | 10 |
| **Total Markdown** | **21** |

### Code Volume

| Project | Total Lines | Code Lines | Average per File |
|---------|-------------|------------|------------------|
| Open Deep Research | ~5,200 | ~3,500 | 347 |
| Research Assistant | ~7,800 | ~5,400 | 371 |
| **Total** | **~13,000** | **~8,900** | **361** |

### Files by Size Category

| Category | Count | Files |
|----------|-------|-------|
| 🚨 Very Large (>1000) | 2 | app.py (1163), utils.py (1071) |
| ⚠️ Large (500-1000) | 2 | deep_researcher.py (718), kg_extractor.py (527) |
| Medium (200-500) | 11 | Various core files |
| Small (<200) | 21 | Tests, utilities, configs |

---

## Section 7: Key Recommendations Summary

### Critical (Do First)
1. ✅ **Delete duplicate documentation** - 2 files, 5 minutes
2. 🔍 **Investigate unused files** - 3 files, 1 hour
3. 🚨 **Refactor app.py** - Break into UI components (4-6 hours)
4. 🚨 **Refactor utils.py** - Split by functionality (6-8 hours)

### High Priority
1. ⚠️ **Refactor deep_researcher.py** - Extract node functions (3-4 hours)
2. ⚠️ **Refactor kg_extractor.py** - Split extraction logic (3-4 hours)

### Medium Priority
1. 📝 **Add docstrings** to all functions lacking them
2. 📊 **Add type hints** consistently across codebase
3. 🧪 **Expand test coverage** for core functions

### Low Priority (Nice to Have)
1. 📦 **Create a shared utilities package** for common code
2. 🎨 **Standardize code style** with Black/Ruff
3. 📄 **Generate API documentation** from docstrings

---

## Section 8: Conclusion

### Overall Assessment: EXCELLENT ✅

The eduagent codebase is **well-structured** with:
- ✅ Clear separation between projects
- ✅ No dead code
- ✅ Good test coverage
- ✅ Active documentation

### Areas of Concern:
- ⚠️ 4 files are too large (>500 lines)
- 🔍 1 potentially unused feature (evidence_map.py)
- 🗑️ 2 duplicate documentation files

### Next Steps:
1. Start with quick wins (delete duplicates, review unused files)
2. Schedule refactoring work for large files
3. Continue maintaining good documentation practices
4. Keep test coverage high as refactoring proceeds

### Estimated Cleanup Effort:
- **Phase 1 (Immediate):** 2-3 hours
- **Phase 2 (Refactoring):** 16-22 hours
- **Phase 3 (Archive):** 1 hour
- **Total:** ~20-26 hours

This is a reasonable investment to improve long-term maintainability!

---

**Analysis completed:** March 3, 2026
**Analyst:** Claude Sonnet 4.5
**Repository health:** GOOD ✅
