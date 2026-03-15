"""Deep Guided mode — complete UI (7 steps)."""
import json

import streamlit as st

from src.deep_guided.config_schema import ResearchGoal, TechConfig, Codebook, SupplementaryStudy
from src.deep_guided.goal_agent import GoalAgent
from src.deep_guided.pdf_ingester import extract_text_from_bytes

_agent = GoalAgent()

_DG_STEPS = ["Vision", "Config", "Codebook", "Sources", "Review", "Research", "Results"]

_MODEL_OPTIONS = {
    "Claude Sonnet 4.5": "anthropic:claude-sonnet-4-5",
    "Claude Opus 4.5": "anthropic:claude-opus-4-5",
    "GPT 4o": "openai:gpt-4o",
    "GPT 4.1": "openai:gpt-4.1",
    "GPT 5.2": "openai:gpt-5.2-2025-12-11",
    "GPT 5 Mini": "openai:gpt-5-mini-2025-08-07",
}

_EVIDENCE_OPTIONS = [
    "Randomized Controlled Trial (RCT)",
    "Quasi-experimental",
    "Longitudinal",
    "Cross-sectional",
    "Case study",
    "Literature review / meta-analysis",
    "Expert opinion / editorial",
]

_DOMAIN_OPTIONS = [
    "Academic databases",
    "Government reports",
    "Think tank reports",
    "Grey literature",
    "News / journalism",
    "Practitioner publications",
]


# ── Session state init ─────────────────────────────────────────────────────────

def _init_dg_state():
    defaults = {
        "dg_step": 1,
        "dg_vision_text": "",
        "dg_chat_history": [],
        "dg_proposed_goals": [],
        "dg_goals": [],
        "dg_tech_config": None,
        "dg_codebook": None,
        "dg_codebook_generated": False,
        "dg_supplementary_studies": [],
        "dg_results": None,
        "dg_model": "openai:gpt-4.1",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── Progress tracker ───────────────────────────────────────────────────────────

def render_dg_progress(step: int):
    parts = []
    for i, label in enumerate(_DG_STEPS):
        n = i + 1
        if n < step:
            parts.append(f"<span style='color:#7c3aed;font-weight:600'>✓ {label}</span>")
        elif n == step:
            parts.append(
                f"<span style='color:#7c3aed;font-weight:700;"
                f"border-bottom:2px solid #7c3aed;padding-bottom:2px'>● {label}</span>"
            )
        else:
            parts.append(f"<span style='color:#9ca3af'>○ {label}</span>")
    arrow = "<span style='color:#d1d5db;margin:0 8px'>→</span>"
    st.markdown(
        f"<div style='margin-bottom:0.25rem'>{arrow.join(parts)}</div>",
        unsafe_allow_html=True,
    )


# ── Step 1: Vision ─────────────────────────────────────────────────────────────

def _step1_goal_chat():
    selected = st.selectbox(
        "Model",
        list(_MODEL_OPTIONS.keys()),
        index=list(_MODEL_OPTIONS.keys()).index("GPT 4.1"),
        key="dg_model_selector",
    )
    st.session_state.dg_model = _MODEL_OPTIONS[selected]

    vision = st.text_area(
        "Describe your research vision",
        value=st.session_state.dg_vision_text,
        height=280,
        placeholder=(
            "Describe your broad research intent — what are you trying to understand, "
            "decide, or build toward? Be as specific or open-ended as you like."
        ),
        label_visibility="collapsed",
    )

    _, col_btn = st.columns([3, 1])
    with col_btn:
        if st.button("Continue →", type="primary", use_container_width=True, key="dg_vision_next"):
            if vision.strip():
                st.session_state.dg_vision_text = vision.strip()
                st.session_state.dg_goals = [ResearchGoal.new(vision.strip())]
                st.session_state.dg_step = 2
                st.rerun()
            else:
                st.error("Please describe your research vision before continuing.")


# ── Step 2: Tech Config ────────────────────────────────────────────────────────

def _step2_tech_config():
    st.caption("Configure the research engine for this session.")
    st.divider()

    if st.session_state.dg_tech_config is None:
        st.session_state.dg_tech_config = TechConfig()
    cfg = st.session_state.dg_tech_config

    st.markdown("**Model & Depth**")
    col1, col2 = st.columns(2)
    with col1:
        model_label = st.selectbox(
            "Research model",
            list(_MODEL_OPTIONS.keys()),
            index=list(_MODEL_OPTIONS.values()).index(cfg.research_model)
            if cfg.research_model in _MODEL_OPTIONS.values() else 0,
            key="dg_cfg_model",
        )
        cfg.research_model = _MODEL_OPTIONS[model_label]
    with col2:
        depth_opts = ["standard", "deep", "comprehensive"]
        cfg.search_depth = st.selectbox(
            "Search depth",
            depth_opts,
            index=depth_opts.index(cfg.search_depth),
            key="dg_cfg_depth",
        )

    st.markdown("---")
    st.markdown("**Evidence Hierarchy**")
    st.caption("Select and order evidence types from strongest to weakest.")
    cfg.evidence_hierarchy = st.multiselect(
        "evidence_hierarchy",
        options=_EVIDENCE_OPTIONS,
        default=cfg.evidence_hierarchy,
        label_visibility="collapsed",
        key="dg_cfg_evidence",
    )

    st.markdown("---")
    st.markdown("**Source Domains**")
    cfg.source_domains = st.multiselect(
        "source_domains",
        options=_DOMAIN_OPTIONS,
        default=cfg.source_domains,
        label_visibility="collapsed",
        key="dg_cfg_domains",
    )

    st.markdown("---")
    st.markdown("**Citation Scoring Weights** *(0 = ignore, 10 = highest priority)*")
    col1, col2 = st.columns(2)
    with col1:
        cfg.citation_scoring["recency"] = st.slider(
            "Recency", 0, 10, cfg.citation_scoring.get("recency", 7), key="dg_cs_recency"
        )
        cfg.citation_scoring["sample_size"] = st.slider(
            "Sample Size", 0, 10, cfg.citation_scoring.get("sample_size", 6), key="dg_cs_sample"
        )
    with col2:
        cfg.citation_scoring["study_design"] = st.slider(
            "Study Design Match", 0, 10, cfg.citation_scoring.get("study_design", 9), key="dg_cs_design"
        )
        cfg.citation_scoring["effect_size"] = st.slider(
            "Effect Size Reported", 0, 10, cfg.citation_scoring.get("effect_size", 8), key="dg_cs_effect"
        )

    st.markdown("---")
    _, col2 = st.columns(2)
    with col2:
        if st.button("Continue →", type="primary", use_container_width=True, key="dg_cfg_next"):
            st.session_state.dg_tech_config = cfg
            st.session_state.dg_step = 3
            st.rerun()


# ── Step 3: Codebook Generation ────────────────────────────────────────────────

def _step3_codebook():
    st.caption(
        "Review and refine your research codebook. Edit directly, or type a note and "
        "click Regenerate to update a section."
    )
    st.divider()

    # Auto-generate on first entry
    if not st.session_state.dg_codebook_generated:
        with st.spinner("Generating codebook from your goals and configuration..."):
            codebook = _agent.generate_codebook(
                goals=st.session_state.dg_goals,
                tech_config=st.session_state.dg_tech_config,
                model_provider=st.session_state.dg_model,
            )
        st.session_state.dg_codebook = codebook
        st.session_state.dg_codebook_generated = True
        st.rerun()

    codebook = st.session_state.dg_codebook

    # ── Scoring Rubric ─────────────────────────────────────────────────────────
    st.markdown("**Scoring Rubric**")
    st.caption("Criteria the research agents will use to evaluate and rank evidence.")
    new_rubric = st.text_area(
        "rubric",
        value=codebook.scoring_rubric,
        height=180,
        label_visibility="collapsed",
        key="dg_rubric_text",
    )
    codebook.scoring_rubric = new_rubric

    col1, col2 = st.columns([4, 1])
    with col1:
        rubric_note = st.text_input(
            "rubric_note",
            placeholder="e.g. Increase weight for studies from the last 5 years",
            label_visibility="collapsed",
            key="dg_rubric_note",
        )
    with col2:
        if st.button("↻ Regenerate", key="dg_regen_rubric", use_container_width=True):
            with st.spinner("Regenerating rubric..."):
                new_codebook = _agent.generate_codebook(
                    goals=st.session_state.dg_goals,
                    tech_config=st.session_state.dg_tech_config,
                    model_provider=st.session_state.dg_model,
                    extra_context=rubric_note or None,
                )
            codebook.scoring_rubric = new_codebook.scoring_rubric
            st.rerun()

    st.markdown("---")

    # ── Research Directions (per goal) ─────────────────────────────────────────
    st.markdown("**Research Directions**")
    st.caption("Instructions for each research agent. One set per goal.")

    for goal in st.session_state.dg_goals:
        short = goal.statement[:80] + ("..." if len(goal.statement) > 80 else "")
        with st.expander(short, expanded=True):
            direction = codebook.research_directions.get(goal.goal_id, "")
            new_dir = st.text_area(
                f"dir_{goal.goal_id}",
                value=direction,
                height=130,
                label_visibility="collapsed",
                key=f"dg_dir_{goal.goal_id}",
            )
            codebook.research_directions[goal.goal_id] = new_dir

            col1, col2 = st.columns([4, 1])
            with col1:
                dir_note = st.text_input(
                    f"note_{goal.goal_id}",
                    placeholder="e.g. Focus only on K-12 contexts, exclude higher education",
                    label_visibility="collapsed",
                    key=f"dg_dirnote_{goal.goal_id}",
                )
            with col2:
                if st.button("↻ Regenerate", key=f"dg_regen_dir_{goal.goal_id}", use_container_width=True):
                    with st.spinner("Regenerating..."):
                        new_codebook = _agent.generate_codebook(
                            goals=st.session_state.dg_goals,
                            tech_config=st.session_state.dg_tech_config,
                            model_provider=st.session_state.dg_model,
                            extra_context=dir_note or None,
                        )
                    codebook.research_directions[goal.goal_id] = new_codebook.research_directions.get(goal.goal_id, "")
                    st.rerun()

    st.markdown("---")
    _, col2 = st.columns(2)
    with col2:
        if st.button("Continue →", type="primary", use_container_width=True, key="dg_codebook_next"):
            st.session_state.dg_codebook = codebook
            st.session_state.dg_step = 4
            st.rerun()


# ── Step 4: PDF Upload ─────────────────────────────────────────────────────────

def _step4_pdf_upload():
    st.caption("Upload supplementary studies to inform the research. Optional.")
    st.divider()

    uploaded_files = st.file_uploader(
        "Upload PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        key="dg_pdf_uploader",
    )

    if uploaded_files:
        st.markdown("---")
        st.markdown("**Annotate Studies**")
        st.caption(
            "Describe how each study should inform your research, or let the agent annotate it."
        )

        for f in uploaded_files:
            with st.expander(f.name, expanded=True):
                existing = next(
                    (s for s in st.session_state.dg_supplementary_studies if s.filename == f.name),
                    None,
                )
                annotation_val = existing.annotation if existing else st.session_state.get(f"dg_ann_{f.name}", "")

                annotation = st.text_area(
                    "How should this study inform your research?",
                    value=annotation_val,
                    height=90,
                    placeholder="e.g. Key RCT on ITS effectiveness. Use as a benchmark for effect size comparisons.",
                    key=f"dg_ann_{f.name}",
                )

                if st.button("Agent annotate", key=f"dg_autoann_{f.name}"):
                    f.seek(0)
                    pdf_text = extract_text_from_bytes(f.read())
                    with st.spinner("Annotating..."):
                        auto = _agent.annotate_pdf(
                            pdf_text=pdf_text,
                            user_note=annotation or "",
                            goals=st.session_state.dg_goals,
                            model_provider=st.session_state.dg_model,
                        )
                    st.session_state[f"dg_ann_{f.name}"] = auto
                    st.rerun()

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Skip →", use_container_width=True, type="secondary", key="dg_pdf_skip"):
            st.session_state.dg_supplementary_studies = []
            st.session_state.dg_step = 5
            st.rerun()
    with col2:
        if st.button("Continue →", use_container_width=True, type="primary", key="dg_pdf_next"):
            studies = []
            for f in (uploaded_files or []):
                annotation = st.session_state.get(f"dg_ann_{f.name}", "")
                f.seek(0)
                pdf_text = extract_text_from_bytes(f.read())
                studies.append(SupplementaryStudy(
                    filename=f.name,
                    text=pdf_text,
                    annotation=annotation,
                ))
            st.session_state.dg_supplementary_studies = studies
            st.session_state.dg_step = 5
            st.rerun()


# ── Step 5: Review & Launch ────────────────────────────────────────────────────

def _step5_review():
    st.caption("Review your full research setup before launching.")
    st.divider()

    st.markdown("**Research Goals**")
    for i, goal in enumerate(st.session_state.dg_goals):
        st.markdown(f"{i + 1}. {goal.statement}")

    st.markdown("---")
    cfg = st.session_state.dg_tech_config
    st.markdown("**Configuration**")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Model:** {cfg.research_model}")
        st.markdown(f"**Search depth:** {cfg.search_depth}")
        st.markdown(f"**Sources:** {', '.join(cfg.source_domains) or 'All'}")
    with col2:
        hierarchy_preview = ", ".join(cfg.evidence_hierarchy[:3])
        if len(cfg.evidence_hierarchy) > 3:
            hierarchy_preview += "..."
        st.markdown(f"**Evidence hierarchy:** {hierarchy_preview}")
        st.markdown(
            f"**Citation scoring:** Recency={cfg.citation_scoring.get('recency')}, "
            f"Study Design={cfg.citation_scoring.get('study_design')}"
        )

    st.markdown("---")
    codebook = st.session_state.dg_codebook
    with st.expander("Codebook Preview", expanded=False):
        st.markdown("**Scoring Rubric**")
        st.markdown(codebook.scoring_rubric or "*Not generated*")
        st.markdown("**Research Directions**")
        for goal in st.session_state.dg_goals:
            st.markdown(f"*{goal.statement[:70]}...*")
            st.markdown(codebook.research_directions.get(goal.goal_id, "*None*"))
            st.markdown("---")

    if st.session_state.dg_supplementary_studies:
        st.markdown("---")
        st.markdown("**Supplementary Studies**")
        for s in st.session_state.dg_supplementary_studies:
            preview = s.annotation[:100] + "..." if len(s.annotation) > 100 else s.annotation
            st.markdown(f"- **{s.filename}**: {preview or '*No annotation*'}")

    st.markdown("---")
    _, col2 = st.columns(2)
    with col2:
        if st.button("🚀 Launch Research", type="primary", use_container_width=True, key="dg_launch"):
            st.session_state.dg_step = 6
            st.rerun()


# ── Step 6: Streaming (UI shell — parallel runner stub) ───────────────────────

def _step6_streaming():
    goals = st.session_state.dg_goals
    cfg = st.session_state.dg_tech_config

    st.markdown(
        f"<div style='background:#f5f3ff;border-left:3px solid #7c3aed;"
        f"padding:0.75rem 1rem;border-radius:4px;margin-bottom:1rem'>"
        f"<span style='color:#6b7280;font-size:0.75rem;font-weight:600;"
        f"text-transform:uppercase'>Research Agenda</span><br>"
        f"<span style='color:#111827'>{len(goals)} goals running in parallel · "
        f"Model: {cfg.research_model} · Depth: {cfg.search_depth}</span></div>",
        unsafe_allow_html=True,
    )

    for goal in goals:
        short = goal.statement[:80] + ("..." if len(goal.statement) > 80 else "")
        with st.expander(f"⏳ {short}", expanded=True):
            st.caption("Queued — parallel research runner not yet connected.")
            directions = st.session_state.dg_codebook.research_directions.get(goal.goal_id, "")
            if directions:
                st.markdown(
                    f"<div style='color:#374151;font-style:italic;border-left:2px solid #d1d5db;"
                    f"padding-left:0.75rem;font-size:0.9rem'>{directions[:200]}...</div>",
                    unsafe_allow_html=True,
                )

    st.markdown("---")
    st.info(
        "⚙️ **Coming next:** Each goal will stream independently through the deep research "
        "pipeline with its codebook injected. Progress will appear per-goal above in real time."
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Review", use_container_width=True, type="secondary", key="dg_stream_back"):
            st.session_state.dg_step = 5
            st.rerun()
    with col2:
        if st.button("Preview Results View →", use_container_width=True, type="primary", key="dg_stream_next"):
            st.session_state.dg_step = 7
            st.rerun()


# ── Step 7: Results ────────────────────────────────────────────────────────────

def _step7_results():
    st.info("Research results will appear here once the parallel runner is connected.")

    st.markdown("**Downloads**")
    st.caption("Available after research completes:")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("⬇ Full Report (.docx)", disabled=True, use_container_width=True, key="dg_dl_report")
    with col2:
        st.button("⬇ Audit Trail (.json)", disabled=True, use_container_width=True, key="dg_dl_audit")

    # Codebook is ready now — offer download immediately
    codebook = st.session_state.dg_codebook
    if codebook:
        codebook_export = {
            "scoring_rubric": codebook.scoring_rubric,
            "research_directions": {
                goal.statement: codebook.research_directions.get(goal.goal_id, "")
                for goal in st.session_state.dg_goals
            },
        }
        with col3:
            st.download_button(
                "⬇ Codebook (.json)",
                data=json.dumps(codebook_export, indent=2),
                file_name="codebook.json",
                mime="application/json",
                use_container_width=True,
                key="dg_dl_codebook",
            )

    st.markdown("---")
    if st.button("← Start New Deep Guided Session", type="secondary", key="dg_restart"):
        keys_to_clear = [k for k in st.session_state.keys() if k.startswith("dg_")]
        for k in keys_to_clear:
            del st.session_state[k]
        st.rerun()


# ── Entry point ────────────────────────────────────────────────────────────────

def render_deep_guided():
    """Main entry point for Deep Guided mode. Called from research_agent.py dispatch."""
    _init_dg_state()
    step = st.session_state.dg_step

    if step == 1:
        _step1_goal_chat()
    elif step == 2:
        _step2_tech_config()
    elif step == 3:
        _step3_codebook()
    elif step == 4:
        _step4_pdf_upload()
    elif step == 5:
        _step5_review()
    elif step == 6:
        _step6_streaming()
    elif step == 7:
        _step7_results()
