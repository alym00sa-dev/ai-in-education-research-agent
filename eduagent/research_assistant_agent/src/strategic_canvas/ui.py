"""Strategic Canvas mode — fully chat-driven UI with deep research integration."""
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict

import streamlit as st

from src.strategic_canvas.coach_skill import CoachSkill, CoachResponse
from src.strategic_canvas.prompts import KG_CONTEXT_INJECTION
from src.deep_guided.pdf_ingester import extract_text_from_bytes
from src.exports import export_report_as_docx

_coach = CoachSkill()

_MODEL_OPTIONS = {
    "Claude Sonnet 4.6": "anthropic:claude-sonnet-4-6",
    "Claude Opus 4.6": "anthropic:claude-opus-4-6",
    "Claude Haiku 4.5": "anthropic:claude-haiku-4-5-20251001",
    "Claude Sonnet 4.5": "anthropic:claude-sonnet-4-5",
    "Claude Opus 4.5": "anthropic:claude-opus-4-5",
    "GPT 4o": "openai:gpt-4o",
    "GPT 4.1": "openai:gpt-4.1",
    "GPT 5.4": "openai:gpt-5.4-2026-03-05",
    "GPT 5.2": "openai:gpt-5.2-2025-12-11",
    "GPT 5 Mini": "openai:gpt-5-mini-2025-08-07",
}

_DEPTH_LABELS = {
    "standard (~3-5 min)": "standard",
    "deep (~5-7 min)": "deep",
}


# ── Session state ──────────────────────────────────────────────────────────────

def _init_sc_state():
    defaults = {
        "sc_chat_history": [],
        "sc_model": "openai:gpt-5.2-2025-12-11",
        "sc_depth": "standard",
        "sc_max_sources": 15,
        "sc_context_text": "",
        "sc_research_states": {},
        "sc_active_research": None,
        "sc_kg_queried": False,
        "sc_kg_coverage": None,
        "sc_proposed_questions": [],   # list of question dicts from KGAgent
        "sc_approved_questions": [],   # list of approved core_question strings
        "sc_pending_approval": False,  # triggers auto agent response after approval
        "sc_question_coverage": {},    # {question: QuestionExploration}
        "sc_research_queue": [],       # questions queued for sequential deep research
        "sc_last_synthesized_count": 0,  # how many questions were included in last synthesis
        "sc_synthesis_report": "",       # cached synthesis for persistent download button
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── Coverage badge ─────────────────────────────────────────────────────────────

def _coverage_badge(coverage: str) -> str:
    styles = {
        "strong":  ("background:#d1fae5;color:#065f46", "● Strong signal"),
        "partial": ("background:#fef3c7;color:#92400e", "◑ Partial signal"),
        "limited": ("background:#fef3c7;color:#92400e", "◑ Partial signal"),
        "none":    ("background:#fee2e2;color:#991b1b", "○ Not in database"),
    }
    style, label = styles.get(coverage, ("background:#f3f4f6;color:#374151", coverage))
    return (
        f"<span style='{style};padding:2px 10px;border-radius:12px;"
        f"font-size:0.75rem;font-weight:600'>{label}</span>"
    )


def _thought_block(text: str) -> str:
    return (
        f"<div style='color:#374151;font-style:italic;"
        f"border-left:2px solid #d1d5db;padding-left:0.75rem;"
        f"margin-bottom:0.5rem'>{text}</div>"
    )


# ── Question approval UI ───────────────────────────────────────────────────────

def _render_question_approval(questions_data: dict, key_suffix: str = "0"):
    """Render proposed questions as plain text list with a single approve button."""
    questions = questions_data.get("questions", [])
    if not questions:
        return

    # If already approved, show as read-only list only
    already_approved = bool(st.session_state.get("sc_approved_questions"))

    for i, q in enumerate(questions):
        st.markdown(f"{i + 1}. {q.get('core_question', '')}")

    if already_approved:
        return

    st.markdown("<div style='margin-top:0.75rem'></div>", unsafe_allow_html=True)
    add_key = f"sc_q_add_{key_suffix}"
    st.text_input(
        "Add a question",
        placeholder="Add your own research question...",
        key=add_key,
    )

    if st.button("Approve & Continue →", type="primary", key=f"sc_q_approve_{key_suffix}"):
        approved = [q.get("core_question", "").strip() for q in questions if q.get("core_question", "").strip()]
        custom = st.session_state.get(add_key, "").strip()
        if custom:
            approved.append(custom)
        if approved:
            st.session_state.sc_approved_questions = approved
            approved_text = "\n".join(f"- {q}" for q in approved)
            approval_msg = f"I'd like to research these questions:\n{approved_text}"
            st.session_state.sc_chat_history.append({"role": "user", "content": approval_msg})
            st.session_state.sc_pending_approval = True
            st.rerun()


# ── Assistant content renderer ─────────────────────────────────────────────────

def _render_assistant_content(content: str, key_suffix: str = "live"):
    """Render an assistant message from chat history."""
    # Extract and strip any appended ---PROPOSE RESEARCH--- block
    research_questions: list = []
    research_match = re.search(
        r"\n\n---PROPOSE RESEARCH---(.*?)---END RESEARCH---",
        content, re.DOTALL,
    )
    if research_match:
        research_questions = [
            q.strip() for q in research_match.group(1).strip().splitlines() if q.strip()
        ]
        content = content[: research_match.start()].strip()

    # Route by content type
    if content.startswith("__QUESTIONS__\n"):
        response = CoachResponse.from_storage_string(content)
        if response.narrative:
            st.markdown(response.narrative)
        _render_question_approval({"questions": response.questions}, key_suffix=key_suffix)

    elif content.startswith("__EXPORT_READY__\n"):
        response = CoachResponse.from_storage_string(content)
        if response.narrative:
            st.markdown(response.narrative)

    else:
        # Legacy ---DRAFT QUESTIONS--- (backward compat for old sessions)
        q_match = re.search(
            r"(.*?)---DRAFT QUESTIONS---(.*?)---END DRAFT---(.*)",
            content, re.DOTALL,
        )
        if q_match:
            before = q_match.group(1).strip()
            questions_raw = q_match.group(2).strip()
            after = q_match.group(3).strip()
            if before:
                st.markdown(before)
            try:
                questions_data = json.loads(questions_raw)
                _render_question_approval(questions_data, key_suffix=key_suffix)
                st.session_state.sc_proposed_questions = questions_data.get("questions", [])
            except json.JSONDecodeError:
                st.markdown(f"```\n{questions_raw}\n```")
            if after:
                st.markdown(after)
        else:
            display = (
                content
                .replace("---READY TO QUERY KG---", "")
                .replace("---READY FOR EXPORT---", "")
                .strip()
            )
            if display:
                st.markdown(display)

    # Always render research cards if present
    if research_questions:
        _render_question_research_cards(research_questions)


def _render_question_research_cards(questions: list):
    """Render per-question coverage cards with checkboxes, coverage info, and batch research button."""
    if not questions:
        return

    explorations: Dict = st.session_state.get("sc_question_coverage", {})
    queue = st.session_state.get("sc_research_queue", [])

    has_unstarted = any(
        not isinstance(st.session_state.sc_research_states.get(q), dict)
        and st.session_state.sc_active_research != q
        and q not in queue
        for q in questions
    )

    for i, q in enumerate(questions):
        exploration = explorations.get(q)
        state = st.session_state.sc_research_states.get(q)
        is_done = isinstance(state, dict) and "summary" in state
        is_running = st.session_state.sc_active_research == q
        is_queued = q in queue

        col_check, col_content = st.columns([1, 11])
        with col_check:
            if is_done:
                st.markdown("<div style='padding-top:0.4rem;color:#059669;font-size:1rem'>✓</div>", unsafe_allow_html=True)
            elif is_running or is_queued:
                st.markdown("<div style='padding-top:0.4rem;color:#6b7280;font-size:0.9rem'>⏳</div>", unsafe_allow_html=True)
            else:
                st.checkbox("", value=True, key=f"sc_drcheck_{i}_{abs(hash(q)) % 10**6}", label_visibility="collapsed")

        with col_content:
            st.markdown(f"**{q}**")
            if exploration:
                if exploration.synthesis:
                    st.markdown(
                        f"<div style='font-size:0.82rem;color:#374151;margin:0.2rem 0 0.3rem'>"
                        f"{exploration.synthesis}</div>",
                        unsafe_allow_html=True,
                    )
                if exploration.replication_candidates:
                    cand = exploration.replication_candidates[0]
                    if isinstance(cand, dict):
                        title = cand.get("title", "")
                        why = cand.get("why", "")
                        if title or why:
                            st.markdown(
                                f"<div style='font-size:0.78rem;color:#7c3aed;margin-bottom:0.2rem'>"
                                f"⭐ <strong>Standout:</strong> {title}{' — ' + why if why else ''}</div>",
                                unsafe_allow_html=True,
                            )
            if is_running:
                st.caption("Running...")
            elif is_queued:
                st.caption("Queued...")

        st.markdown("<hr style='margin:0.4rem 0;border-color:#f3f4f6'>", unsafe_allow_html=True)

    if has_unstarted:
        batch_key = f"sc_run_batch_{abs(hash(tuple(questions))) % 10**8}"
        if st.button("Run Deep Research on Selected →", type="primary", key=batch_key):
            selected = [
                questions[i] for i in range(len(questions))
                if st.session_state.get(f"sc_drcheck_{i}_{abs(hash(questions[i])) % 10**6}", True)
                and not isinstance(st.session_state.sc_research_states.get(questions[i]), dict)
                and st.session_state.sc_active_research != questions[i]
                and questions[i] not in queue
            ]
            if selected:
                st.session_state.sc_research_queue = selected
                st.rerun()


# ── KG query flow ──────────────────────────────────────────────────────────────

def _run_kg_query_and_followup(approved_questions: list):
    """Use QuestionExplorer to exhaustively search KG per question, then agent narrates."""
    from src.kg_agent.question_explorer import QuestionExplorer
    from src.strategic_canvas.prompts import KG_CONTEXT_INJECTION

    explorer = QuestionExplorer()
    status = st.empty()

    # Run all questions in parallel against the KG
    explorations = {}
    status.markdown(
        _thought_block(f"Querying the Edu Knowledge Graph for all {len(approved_questions)} questions in parallel..."),
        unsafe_allow_html=True,
    )
    with ThreadPoolExecutor(max_workers=len(approved_questions)) as executor:
        futures = {executor.submit(explorer.explore_question, q): q for q in approved_questions}
        for future in as_completed(futures):
            q = futures[future]
            try:
                explorations[q] = future.result()
            except Exception as e:
                from src.kg_agent.question_explorer import QuestionExploration
                explorations[q] = QuestionExploration(question=q, synthesis=f"Search failed: {e}")

    st.session_state.sc_question_coverage = explorations
    st.session_state.sc_kg_queried = True

    # Show summary of what was found
    total_papers = sum(e.paper_count for e in explorations.values())
    status.markdown(
        _thought_block(
            f"Knowledge graph queried. Found signals across {len(approved_questions)} questions "
            f"({total_papers} total paper references). Building coverage summary..."
        ),
        unsafe_allow_html=True,
    )

    # Build KG summary for agent narration
    kg_summary_lines = [f"Total papers in database: — (see per-question below)\n"]
    for q, exp in explorations.items():
        short = q[:100] + "..." if len(q) > 100 else q
        kg_summary_lines.append(
            f"Question: {short}\n"
            f"  Coverage: {exp.coverage_level} ({exp.paper_count} papers)\n"
            f"  Synthesis: {exp.synthesis}\n"
            f"  Gaps: {'; '.join(exp.evidence_gaps[:2]) if exp.evidence_gaps else 'none identified'}\n"
        )
    kg_summary = "\n".join(kg_summary_lines)

    kg_injection = KG_CONTEXT_INJECTION.format(kg_summary=kg_summary)

    status.empty()

    with st.spinner("Synthesizing findings..."):
        response = _coach.chat_turn(
            history=st.session_state.sc_chat_history,
            user_message="[KG exploration complete — please narrate what you found across all questions]",
            context_text=st.session_state.sc_context_text,
            kg_injection=kg_injection,
        )

    # Append research cards block so cards persist on every replay
    research_block = (
        "\n\n---PROPOSE RESEARCH---\n"
        + "\n".join(approved_questions)
        + "\n---END RESEARCH---"
    )
    stored_response = response.to_storage_string() + research_block
    _render_assistant_content(stored_response)
    st.session_state.sc_chat_history.append({"role": "assistant", "content": stored_response})


# ── Parallel deep research ─────────────────────────────────────────────────────

def _research_one(pipeline, question: str, model: str, depth: str, max_sources: int):
    """Run a full research stream for one question in a thread. Returns (summary, event_log)."""
    accumulated = ""
    event_log = []
    try:
        for event in pipeline.stream_research(
            query=question,
            model_provider=model,
            search_depth=depth,
            skip_clarification=True,
            max_sources=max_sources,
        ):
            event_log.append(event)
            if event["type"] == "token":
                accumulated += event["content"]
    except Exception as e:
        accumulated = f"Research error: {e}"
    return accumulated, event_log


def _run_parallel_research(questions: list):
    """Run deep research for all questions in parallel, update state, rerun."""
    pipeline = st.session_state.pipeline
    model = st.session_state.sc_model
    depth = st.session_state.sc_depth
    max_sources = st.session_state.get("sc_max_sources", 15)

    status = st.empty()
    done_count = [0]

    def _run_one(q):
        result = _research_one(pipeline, q, model, depth, max_sources)
        done_count[0] += 1
        status.markdown(
            _thought_block(f"Research complete for {done_count[0]}/{len(questions)} questions..."),
            unsafe_allow_html=True,
        )
        return result

    status.markdown(
        _thought_block(f"Running deep research on {len(questions)} questions in parallel..."),
        unsafe_allow_html=True,
    )

    with ThreadPoolExecutor(max_workers=len(questions)) as executor:
        futures = {executor.submit(_run_one, q): q for q in questions}
        for future in as_completed(futures):
            q = futures[future]
            try:
                accumulated, event_log = future.result()
                st.session_state.sc_research_states[q] = {
                    "summary": accumulated,
                    "event_log": event_log,
                }
            except Exception as e:
                st.session_state.sc_research_states[q] = {"error": str(e)}

    status.empty()
    st.session_state.sc_chat_history.append({
        "role": "assistant",
        "content": f"✅ Deep research complete across {len(questions)} question(s). Synthesizing findings...",
    })
    st.rerun()


# ── Export ─────────────────────────────────────────────────────────────────────

def _build_strategy_report(chat_history: list, research_states: dict, synthesis: str = "") -> str:
    parts = ["# Strategy Research Report\n"]
    first_user = next((m["content"] for m in chat_history if m["role"] == "user"), "")
    if first_user:
        parts.append(f"## Strategic Challenge\n{first_user}\n")
    if synthesis:
        parts.append(synthesis)
    else:
        completed = {q: v for q, v in research_states.items() if isinstance(v, dict) and "summary" in v}
        if completed:
            parts.append("## Deep Research Findings\n")
            for q, result in completed.items():
                parts.append(f"### {q}\n{result['summary']}\n")
    return "\n".join(parts)


# ── Main entry point ───────────────────────────────────────────────────────────

def render_strategic_canvas():
    _init_sc_state()

    # ── Controls row ───────────────────────────────────────────────────────────
    col_model, col_depth, col_sources, col_upload = st.columns([2, 2, 2, 3])

    with col_model:
        st.caption("Deep Research Model")
        selected_model_label = st.selectbox(
            "Model",
            options=list(_MODEL_OPTIONS.keys()),
            index=list(_MODEL_OPTIONS.keys()).index("GPT 5.2"),
            key="sc_model_select",
            label_visibility="collapsed",
        )
        st.session_state.sc_model = _MODEL_OPTIONS[selected_model_label]

    with col_depth:
        st.caption("Research Depth")
        selected_depth_label = st.selectbox(
            "Research Depth",
            options=list(_DEPTH_LABELS.keys()),
            key="sc_depth_select",
            label_visibility="collapsed",
        )
        st.session_state.sc_depth = _DEPTH_LABELS[selected_depth_label]

    with col_sources:
        st.caption("Max Sources")
        st.session_state.sc_max_sources = st.slider(
            "Max Sources",
            min_value=10,
            max_value=30,
            value=st.session_state.sc_max_sources,
            step=1,
            key="sc_sources_slider",
            label_visibility="collapsed",
        )

    with col_upload:
        st.caption("Context Files (optional)")
        uploaded = st.file_uploader(
            "Upload context PDFs",
            type=["pdf"],
            accept_multiple_files=True,
            key="sc_file_uploader",
            label_visibility="collapsed",
        )
        if uploaded:
            texts = []
            for f in uploaded:
                f.seek(0)
                extracted = extract_text_from_bytes(f.read())
                texts.append(f"[{f.name}]\n{extracted[:2000]}")
            st.session_state.sc_context_text = "\n\n".join(texts)

    st.divider()

    # ── Chat history ───────────────────────────────────────────────────────────
    for msg_idx, msg in enumerate(st.session_state.sc_chat_history):
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                _render_assistant_content(msg["content"], key_suffix=str(msg_idx))
            else:
                st.markdown(msg["content"])

    # ── Flat research thought log (post-completion) ────────────────────────────
    finished_states = {
        q: v for q, v in st.session_state.sc_research_states.items()
        if isinstance(v, dict) and "event_log" in v
    }
    if finished_states:
        all_thoughts = []
        for q, v in finished_states.items():
            short_q = q if len(q) <= 60 else q[:57] + "..."
            for event in v["event_log"]:
                etype = event.get("type")
                if etype == "thought":
                    all_thoughts.append({
                        "label": short_q,
                        "content": event["content"],
                        "is_critique": False,
                    })
                elif etype == "critique":
                    all_thoughts.append({
                        "label": short_q,
                        "content": event["content"],
                        "is_critique": True,
                    })
        if all_thoughts:
            with st.expander("✅ Research Thoughts", expanded=False):
                for entry in all_thoughts:
                    label_html = (
                        f"<span style='font-size:0.7rem;font-weight:600;color:#6b7280;"
                        f"text-transform:uppercase;letter-spacing:0.04em'>{entry['label']}</span><br>"
                    )
                    if entry.get("is_critique"):
                        st.markdown(
                            f"<div style='color:#7c3aed;font-style:italic;font-size:0.82rem;"
                            f"border-left:2px solid #a78bfa;padding-left:0.75rem;"
                            f"margin-bottom:0.4rem'>{label_html}"
                            f"<strong>Critique:</strong> {entry['content']}</div>",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            f"<div style='color:#374151;font-style:italic;font-size:0.82rem;"
                            f"border-left:2px solid #d1d5db;padding-left:0.75rem;"
                            f"margin-bottom:0.4rem'>{label_html}{entry['content']}</div>",
                            unsafe_allow_html=True,
                        )

    # ── Parallel deep research ─────────────────────────────────────────────────
    if st.session_state.sc_research_queue:
        questions = list(st.session_state.sc_research_queue)
        st.session_state.sc_research_queue = []
        _run_parallel_research(questions)

    # ── Synthesis: generate final report once all queued research finishes ─────
    completed_research = {
        q: v for q, v in st.session_state.sc_research_states.items()
        if isinstance(v, dict) and "summary" in v
    }
    all_idle = not st.session_state.sc_research_queue
    last_synthesized = st.session_state.get("sc_last_synthesized_count", 0)

    if completed_research and all_idle and len(completed_research) > last_synthesized:
        strategic_challenge = next(
            (m["content"] for m in st.session_state.sc_chat_history if m["role"] == "user"),
            "",
        )
        summaries = {q: v["summary"] for q, v in completed_research.items()}

        synthesis = ""
        synthesis_error = ""
        try:
            with st.chat_message("assistant"):
                with st.spinner("Synthesizing all findings into strategy report..."):
                    synthesis = _coach.synthesize_research(
                        strategic_challenge=strategic_challenge,
                        research_summaries=summaries,
                        context_text=st.session_state.sc_context_text,
                    )
                st.markdown(synthesis)
        except Exception as e:
            synthesis_error = str(e)
            st.error(f"Synthesis failed: {synthesis_error}")

        # Always advance the counter so we never re-enter this block
        st.session_state.sc_last_synthesized_count = len(completed_research)

        if synthesis:
            st.session_state.sc_chat_history.append({
                "role": "assistant",
                "content": synthesis,
            })
            st.session_state.sc_synthesis_report = synthesis
        elif synthesis_error:
            st.session_state.sc_chat_history.append({
                "role": "assistant",
                "content": f"⚠️ Synthesis failed: {synthesis_error}",
            })

        # Centered download button (rendered once; persists via sc_synthesis_report below)
        report_md = _build_strategy_report(
            st.session_state.sc_chat_history,
            st.session_state.sc_research_states,
            synthesis=synthesis,
        )
        docx_bytes = export_report_as_docx(
            research_summary=report_md,
            session_query="Strategy Research Report",
            structured_papers=None,
        )
        _, col_dl, _ = st.columns([1, 2, 1])
        with col_dl:
            st.download_button(
                "⬇ Download Strategy Report (.docx)",
                data=docx_bytes,
                file_name="strategy_report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
                use_container_width=True,
                key="sc_dl_initial",
            )

        # Coach follow-up: ask if the user wants to explore more
        if synthesis:
            try:
                with st.chat_message("assistant"):
                    with st.spinner("..."):
                        followup = _coach.chat_turn(
                            history=st.session_state.sc_chat_history,
                            user_message="[Strategy report delivered. Follow up naturally — ask if the user has more questions to explore or wants to refine any findings.]",
                            context_text=st.session_state.sc_context_text,
                        )
                    st.markdown(followup.narrative)
                st.session_state.sc_chat_history.append({
                    "role": "assistant",
                    "content": followup.narrative,
                })
            except Exception:
                pass
        st.rerun()

    # ── Persistent download (shown after rerun once synthesis exists) ──────────
    if st.session_state.get("sc_synthesis_report") and all_idle and not (completed_research and len(completed_research) > last_synthesized):
        report_md = _build_strategy_report(
            st.session_state.sc_chat_history,
            st.session_state.sc_research_states,
            synthesis=st.session_state.sc_synthesis_report,
        )
        docx_bytes = export_report_as_docx(
            research_summary=report_md,
            session_query="Strategy Research Report",
            structured_papers=None,
        )
        _, col_dl, _ = st.columns([1, 2, 1])
        with col_dl:
            st.download_button(
                "⬇ Download Strategy Report (.docx)",
                data=docx_bytes,
                file_name="strategy_report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="secondary",
                use_container_width=True,
                key="sc_dl_persistent",
            )

    # ── KG query after approval ────────────────────────────────────────────────
    if st.session_state.sc_pending_approval:
        st.session_state.sc_pending_approval = False
        approved = st.session_state.sc_approved_questions
        if approved:
            _run_kg_query_and_followup(approved_questions=approved)
        st.rerun()

    # ── Chat input ─────────────────────────────────────────────────────────────
    placeholder = (
        "Describe your strategic challenge..."
        if not st.session_state.sc_chat_history
        else "Continue the conversation..."
    )
    if prompt := st.chat_input(placeholder):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.sc_chat_history.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = _coach.chat_turn(
                    history=st.session_state.sc_chat_history[:-1],
                    user_message=prompt,
                    context_text=st.session_state.sc_context_text,
                )
            stored = response.to_storage_string()
            _render_assistant_content(stored)

        st.session_state.sc_chat_history.append({"role": "assistant", "content": stored})
        st.rerun()
