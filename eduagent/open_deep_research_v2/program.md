# Autoresearch — Edu Pipeline Prompt Optimization

You are an autonomous research agent improving an education research pipeline by modifying its prompts and measuring quality via a QA scoring benchmark.

---

## Setup (run once before the experiment loop)

1. Ensure you are on branch `autoresearch-exp`:
   ```
   git checkout autoresearch-exp
   git status
   ```

2. Run the baseline benchmark and record the score:
   ```
   python -u benchmark.py baseline > benchmark_baseline.log 2>&1
   ```
   Extract the average score from the log — this is your **baseline**. Every subsequent experiment must beat this average AND pass the floor rule (no individual query below 90/100).

3. Confirm `benchmark_results.tsv` now has a `baseline` row.

---

## What you can modify

Only edit files in:
- `src/prompts/synthesis.py` — `compress_findings_prompt`, `draft_report_prompt`
- `src/prompts/critique.py` — `critique_prompt`
- `src/prompts/report.py` — `final_report_prompt`
- `src/graph.py` — ONLY to wire/unwire the `draft_report` node (structural experiment)

**Do NOT modify:**
- `src/nodes/` (except graph.py wiring)
- `src/prompts/researcher.py`
- `src/prompts/education_discovery.py`
- `src/prompts/supervisor.py`
- `src/prompts/qa.py`
- `benchmark.py` or `BENCHMARK_QUERIES`
- `CONFIG` in `benchmark.py` (tavily_budget, serp_budget, model, iterations must stay fixed)
- Any `src/utils/` files
- `src/state.py`

---

## Experiment loop

Repeat indefinitely until manually stopped:

### Step 1 — Pick a hypothesis

Choose ONE of the following experiment types per loop iteration (vary them, don't repeat the same type consecutively):

**Type A — Structural: remove draft_report**
- In `src/graph.py`, rewire: `compress_findings → critique` (skip `draft_report`)
- Update `critique` prompt in `src/prompts/critique.py` to accept compressed findings directly instead of a draft report

**Type B — Improve compress_findings prompt**
- In `src/prompts/synthesis.py`, improve `compress_findings_prompt`
- Goals: better evidence hierarchy (RCTs first), explicit effect size surfacing, clearer gap identification

**Type C — Improve critique prompt**
- In `src/prompts/critique.py`, improve `critique_prompt`
- Goals: more targeted gap identification, better direction for next iteration, distinguish evidence-thin vs evidence-present gaps

**Type D — Improve final_report prompt**
- In `src/prompts/report.py`, improve `final_report_prompt`
- Goals: stricter evidence type labelling, better handling of sparse/emerging evidence topics, cleaner citation discipline

**Type E — Combined: compress_findings + critique**
- Improve both together as a coherent unit

### Step 2 — Implement and commit

Make your change. Then commit with a clear message:
```
git add src/prompts/synthesis.py src/prompts/critique.py src/prompts/report.py src/graph.py
git commit -m "exp: <type> — <one line description of change>"
```

### Step 3 — Run the benchmark

```
python -u benchmark.py "<type>: <short description>" > benchmark_run.log 2>&1
```

Wait for all 4 queries to complete. Extract:
- Average score
- Individual scores (math_tutoring, formative_assessment, genai_math, genai_learning)
- Whether floor rule passed (all scores ≥ 90)

### Step 4 — Keep or discard

| Condition | Action |
|-----------|--------|
| avg > baseline AND all scores ≥ 90 | **KEEP**: update baseline to new avg, continue |
| avg ≤ baseline OR any score < 90 | **DISCARD**: `git reset --hard HEAD~1`, continue |
| Crash / timeout (>90 min) | **CRASH**: `git reset --hard HEAD~1`, log it, continue |

### Step 5 — Log and loop

After each experiment (keep or discard), print a one-line summary:
```
[exp N] Type=<A/B/C/D/E> | avg=<X.X> | baseline=<Y.Y> | delta=<+/-Z.Z> | status=<KEEP/DISCARD/CRASH>
```

Then go back to Step 1 with a different hypothesis.

---

## Constraints

- Do NOT pause between experiments
- Do NOT stop unless manually interrupted or you hit 20 experiments
- Do NOT modify `benchmark.py` or the 4 benchmark queries under any circumstances
- Do NOT add new Python dependencies
- If a run crashes with an API error, wait 60 seconds and retry once before discarding
- Keep prompt changes focused — one clear idea per experiment, not a complete rewrite
- When improving prompts, preserve all existing formatting variables (`{research_brief}`, `{iteration_history}`, etc.)

---

## Tracking

All results are automatically written to `benchmark_results.tsv`. After each KEEP, also note:
- What specifically changed
- Which query benefited most
- Which query, if any, regressed

---

## Success criteria

An experiment run is considered successful if after 10+ experiments:
- Average score has improved by ≥ 3 points over baseline
- All individual query scores are ≥ 90
- At least 2 different experiment types have been explored
