"""PDF extraction — fetches full text for academic papers and produces KG-aligned PaperProfiles.

Extraction uses two parallel LLM calls:
  Call 1 (_extract_metadata): factual fields — title, doi, year, venue, population,
      study_design, extended_summary, limitations, implementation context, geographic context.
  Call 2 (_extract_taxonomy): taxonomy-heavy fields — interventions, outcome assignments,
      quality/impact tiers + rationales.

Both calls receive the same paper text and run concurrently. Results are merged into
a single PaperProfile.

Only papers with successful full-text extraction produce a PaperProfile.
Abstract-only results are annotated but not stored.
"""

import asyncio
import os
import re

import fitz  # pymupdf
import httpx
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage

from state import PaperProfile, PaperMetadataExtract, PaperTaxonomyExtract

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; EduResearchBot/2.0)"}
_DEFAULT_MODEL = "gpt-5.4-mini-2026-03-17"

PDF_EXTRACTABLE_TOOLS = {
    "eric_search",
    "openalex_search",
    "arxiv_search",
    "elsevier_search",
    "semantic_scholar_search",
}


# ── Call 1: Metadata ───────────────────────────────────────────────────────────

_METADATA_SYSTEM = """You are extracting factual metadata from an academic paper for a knowledge graph about AI and technology interventions in education.
Be precise. Use "not_reported" for any field where the information is genuinely absent from the text."""

_METADATA_HUMAN = """Research topic this paper was retrieved for: {research_topic}

Paper text:
{pdf_text}

---

Extract the following fields:

### Metadata
- title: full paper title
- doi: DOI if present, else null
- year: publication year as integer, else null
- venue: journal or conference name, else null
- populations: list all population groups studied — include every group present. Use these values only:
  "Elementary (PreK-5th)", "Middle School (6th-8th)", "High School (9th-12th)",
  "Undergraduate", "Graduate / Doctoral", "Adult (non-academic)", "K-12 (unspecified grade)"
  Return [] if not reported.
- user_types: list all user roles present. Use these values only:
  "Student", "Educator", "Administrator", "Parent", "School", "Community"
  Return [] if not reported.
- study_design: exactly one of:
  - Randomized Controlled Trial (RCT) — participants randomly assigned to treatment and control groups
  - Quasi-Experimental Design (QED) — treatment/control comparison without random assignment (matched groups, regression discontinuity, difference-in-differences)
  - Meta-Analysis / Systematic Review — aggregates findings across multiple primary studies using systematic search and quantitative or qualitative synthesis
  - Observational / Correlational — measures existing conditions or associations without manipulating an intervention (surveys, regression, longitudinal cohort)
  - Mixed-Methods — combines quantitative and qualitative data collection and analysis in the same study
  - Qualitative — interviews, case studies, ethnography, thematic analysis — no quantitative outcome measurement
  - Framework / Theoretical — proposes a model, taxonomy, design principles, or position without empirical data collection

### Extended Summary
Write 2-4 paragraphs covering: (1) what problem or question the paper addresses, (2) the intervention or approach studied, (3) the population and context, (4) the main conclusions. Detailed enough that a reader understands the paper without reading it.

### Limitations
Tag all applicable limitations (return only tags that apply):
- small_sample — fewer than ~100 participants
- short_duration — intervention lasted less than 4 weeks
- single_site — conducted at one school or institution only
- no_control_group — no comparison condition
- self_reported_measures — outcomes rely on self-report rather than objective assessment
- non_representative_population — sample unlikely to generalise
- high_attrition — significant dropout affecting validity
- implementation_fidelity_not_reported — no information on how the intervention was delivered
- no_long_term_followup — outcomes measured immediately, no delayed retention data

### Implementation Context
- duration_weeks: integer as string (e.g. "8") or "not_reported"
- setting: exactly one of — classroom / lab / online / blended / not_reported
- teacher_training: yes / no / not_reported
- implementation_fidelity: high / medium / low / not_reported

### Geographic Context
- study_country: country where participants were located (e.g. "United States") or "not_reported"
- study_region: one of — North America / Latin America & Caribbean / Europe / Sub-Saharan Africa / East Asia & Pacific / South Asia / Middle East & North Africa / Central Asia / not_reported
"""


# ── Call 2: Taxonomy ───────────────────────────────────────────────────────────

_TAXONOMY_SYSTEM = """You are a research analyst mapping academic papers to a structured knowledge graph taxonomy about AI and technology interventions in education.
You are an expert at identifying intervention types, measuring outcomes, and applying evidence quality frameworks."""

_TAXONOMY_HUMAN = """Research topic this paper was retrieved for: {research_topic}

Paper text:
{pdf_text}

---

### Intervention Assignments
Identify every technology or AI intervention this paper evaluates. For each, map to the closest pre-seeded category.

Pre-seeded categories:
- Intelligent Tutoring System (ITS) — classical rule/model-based adaptive tutoring (e.g. ASSISTments, Cognitive Tutor)
- LLM-based Tutoring / Conversational AI — modern GenAI tutors, chatbots, AI course assistants (post-2022)
- Adaptive Learning Platform — personalises content/pacing without dialogue tutoring (e.g. Khan Academy, DreamBox)
- Automated Feedback System — AI feedback on student work (essays, code, math) without full tutoring
- AI Writing / Language Tool — writing assistants, EFL tools, grammar AI, speech-to-text for language learners
- Robot / Embodied Tutor — physical or avatar-based robotic tutoring systems
- Predictive Analytics / Early Warning — AI analysis of student data to flag risk and trigger intervention
- Computer-Assisted Instruction (CAI) — software-delivered instruction, minimally adaptive or non-adaptive
- Educational Game / Simulation — game-based learning, simulations with a technology component
- Mobile / Microlearning App — app-based, bite-sized content delivery
- Other — nothing above fits; will be reviewed manually

For each intervention:
- confidence (0.0-1.0): how centrally does the paper evaluate this? Only include >= 0.5
- role: "primary" for the main focus, "secondary" for comparators or supporting tools
- use_case: specific free-text description of HOW this paper applies the intervention — be precise (e.g. "adaptive algebra tutoring with hint generation for middle schoolers", "automated essay scoring for persuasive writing in EFL contexts")

Return an empty list if no technology/AI intervention is described.

### Outcome Assignments
Map to these 9 outcome categories:
1. Academic — Literacy (reading, writing)
2. Academic — Language Fluency (speaking, listening)
3. Academic — Mathematical Numeracy
4. Academic — Scientific Reasoning
5. Academic — Other (history, arts, vocational, etc.)
6. Social-Emotional Skills (motivation, engagement, self-regulation, persistence)
7. Durable Skills (critical thinking, metacognition, collaboration, time management)
8. Operational Efficiency (productivity, task efficiency, teacher workload)
9. Systemic / Institutional Impact (policy, governance, institutional outcomes)

For each outcome the paper substantively studies (not just mentions):
- confidence (0.0-1.0): only include >= 0.5
- finding: direction (Positive/Negative/No Effect/Mixed), finding_summary (2-3 sentences with effect sizes), measure, study_size, effect_size, confidence_interval, std_deviation
- For comparison papers (A vs B): create a separate OutcomeAssignment per intervention with the intervention field set. For single-intervention papers, leave intervention null.
- Framework / Theoretical papers may have empty outcome_assignments.

### Evidence Quality and Impact Tiers (K-12 Evidence Framework)
Assign quality_tier and impact_tier — use exactly one of: blue, green, yellow, red.
Provide a 1-2 sentence rationale for each.

Quality tier:
- blue: Meta-analysis OR well-designed RCT with all credibility and relevance criteria met
- green: Well-designed QED or meta-analysis/RCT with some concerns; 2 of 3 credibility criteria
- yellow: Correlational or qualitative study; 1 of 3 credibility criteria
- red: No clear methodology, no peer review, purely opinion/grey literature

Impact tier:
- blue: Medium or large impact on general or priority populations (effect size >= 0.20)
- green: Modest impact on priority populations or on general population (0.05-0.20)
- yellow: Modest or unclear impact on general population
- red: No impact or negative impact
"""


# ── Helpers ────────────────────────────────────────────────────────────────────

def _get_api_key(model_name: str) -> str:
    if model_name.startswith("anthropic:") or model_name.startswith("claude"):
        return os.getenv("ANTHROPIC_API_KEY", "")
    return os.getenv("OPENAI_API_KEY", "")


def _derive_pdf_url(url: str) -> str:
    if "arxiv.org/abs/" in url:
        pdf = url.replace("/abs/", "/pdf/")
        return pdf if pdf.endswith(".pdf") else pdf + ".pdf"
    if "arxiv.org/pdf/" in url and not url.endswith(".pdf"):
        return url + ".pdf"
    return url


def _parse_blocks_with_urls(text: str) -> list[dict]:
    matches = list(re.finditer(r"\[(\d+)\] Title:", text))
    results = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[start:end].strip()

        pdf_url = None
        abstract_url = ""

        pdf_match = re.search(r"^\s+PDF:\s*(https?://\S+)", block, re.MULTILINE)
        if pdf_match:
            pdf_url = pdf_match.group(1).rstrip(".,);>\"'")

        url_match = re.search(r"^\s+URL:\s*(https?://\S+)", block, re.MULTILINE)
        if url_match:
            abstract_url = url_match.group(1).rstrip(".,);>\"'")

        results.append({
            "index": int(match.group(1)),
            "block": block,
            "pdf_url": pdf_url,
            "abstract_url": abstract_url,
        })
    return results


async def _fetch_pdf_bytes(url: str) -> tuple[bytes | None, str]:
    pdf_url = _derive_pdf_url(url)
    try:
        async with httpx.AsyncClient(
            follow_redirects=True, timeout=15.0, headers=_HEADERS
        ) as client:
            response = await client.get(pdf_url)

        if response.status_code in (401, 403):
            return None, f"paywall (HTTP {response.status_code})"
        if response.status_code != 200:
            return None, f"HTTP {response.status_code}"

        content_type = response.headers.get("content-type", "").lower()
        body = response.content
        is_pdf = "pdf" in content_type or "octet-stream" in content_type or body[:4] == b"%PDF"
        if not is_pdf:
            return None, "not a PDF"

        return body, "ok"
    except httpx.TimeoutException:
        return None, "timeout"
    except Exception as e:
        return None, f"fetch error: {type(e).__name__}"


def _extract_text_from_pdf(pdf_bytes: bytes) -> str:
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        pages = min(40, len(doc))
        return "\n".join(doc[i].get_text() for i in range(pages))
    except Exception:
        return ""


# ── LLM calls ─────────────────────────────────────────────────────────────────

async def _extract_metadata(
    text: str, research_topic: str, model_name: str
) -> PaperMetadataExtract:
    """Call 1 — factual metadata, summary, limitations, implementation/geographic context."""
    model = init_chat_model(
        model=model_name,
        max_tokens=4096,
        api_key=_get_api_key(model_name),
        tags=["langsmith:nostream"],
    ).with_structured_output(PaperMetadataExtract)

    return await model.ainvoke([
        SystemMessage(content=_METADATA_SYSTEM),
        HumanMessage(content=_METADATA_HUMAN.format(
            research_topic=research_topic,
            pdf_text=text[:60000],
        )),
    ])


async def _extract_taxonomy(
    text: str, research_topic: str, model_name: str
) -> PaperTaxonomyExtract:
    """Call 2 — intervention assignments, outcome assignments, evidence tiers."""
    model = init_chat_model(
        model=model_name,
        max_tokens=6144,
        api_key=_get_api_key(model_name),
        tags=["langsmith:nostream"],
    ).with_structured_output(PaperTaxonomyExtract)

    return await model.ainvoke([
        SystemMessage(content=_TAXONOMY_SYSTEM),
        HumanMessage(content=_TAXONOMY_HUMAN.format(
            research_topic=research_topic,
            pdf_text=text[:60000],
        )),
    ])


async def _extract_profile(
    text: str,
    research_topic: str,
    metadata_model: str,
    taxonomy_model: str,
) -> PaperProfile:
    """Run both extraction calls in parallel and merge into a PaperProfile."""
    meta, taxonomy = await asyncio.gather(
        _extract_metadata(text, research_topic, metadata_model),
        _extract_taxonomy(text, research_topic, taxonomy_model),
    )

    return PaperProfile(
        # From metadata call
        title=meta.title,
        doi=meta.doi,
        year=meta.year,
        venue=meta.venue,
        populations=meta.populations,
        user_types=meta.user_types,
        study_design=meta.study_design,
        extended_summary=meta.extended_summary,
        limitations=meta.limitations,
        duration_weeks=meta.duration_weeks,
        setting=meta.setting,
        teacher_training=meta.teacher_training,
        implementation_fidelity=meta.implementation_fidelity,
        study_country=meta.study_country,
        study_region=meta.study_region,
        # From taxonomy call
        interventions=taxonomy.interventions,
        outcome_assignments=taxonomy.outcome_assignments,
        quality_tier=taxonomy.quality_tier,
        quality_tier_rationale=taxonomy.quality_tier_rationale,
        impact_tier=taxonomy.impact_tier,
        impact_tier_rationale=taxonomy.impact_tier_rationale,
    )


# ── Public API ─────────────────────────────────────────────────────────────────

async def extract_paper_profile(
    paper_block: str,
    pdf_url: str | None,
    abstract_url: str,
    research_topic: str,
    source_db: str,
    metadata_model: str = _DEFAULT_MODEL,
    taxonomy_model: str = _DEFAULT_MODEL,
) -> PaperProfile:
    """Attempt full-text extraction for one paper. Returns PaperProfile with extraction_status."""
    text_for_extraction: str | None = None
    extraction_status = "abstract_only"
    extraction_note = ""

    # 1. Try explicit PDF: field
    if pdf_url:
        pdf_bytes, status = await _fetch_pdf_bytes(pdf_url)
        if pdf_bytes:
            pdf_text = _extract_text_from_pdf(pdf_bytes)
            if len(pdf_text.strip()) >= 300:
                text_for_extraction = pdf_text
                extraction_status = "full_text"
            else:
                extraction_note = "PDF too short to extract"
        else:
            extraction_note = status

    # 2. Try deriving PDF URL from abstract URL (e.g. arXiv)
    if text_for_extraction is None and abstract_url:
        derived = _derive_pdf_url(abstract_url)
        if derived != abstract_url:
            pdf_bytes, status = await _fetch_pdf_bytes(derived)
            if pdf_bytes:
                pdf_text = _extract_text_from_pdf(pdf_bytes)
                if len(pdf_text.strip()) >= 300:
                    text_for_extraction = pdf_text
                    extraction_status = "full_text"
                else:
                    extraction_note = "derived PDF too short"
            else:
                extraction_note = status

    # 3. Fall back to abstract snippet from block text
    if text_for_extraction is None:
        text_for_extraction = paper_block
        if not extraction_note:
            extraction_note = "no PDF available"

    try:
        profile = await _extract_profile(
            text_for_extraction, research_topic, metadata_model, taxonomy_model
        )
        profile.extraction_status = extraction_status
        profile.extraction_note = extraction_note
        profile.source_db = source_db
        if abstract_url and not profile.url:
            profile.url = abstract_url
        return profile
    except Exception as e:
        title_match = re.search(r"\[\d+\] Title:\s*(.+)", paper_block)
        title = title_match.group(1).strip() if title_match else "Unknown"
        return PaperProfile(
            title=title,
            url=abstract_url,
            source_db=source_db,
            extraction_status="abstract_only",
            extraction_note=f"extraction failed: {type(e).__name__}",
        )


async def enrich_tool_output(
    tool_name: str,
    tool_output: str,
    research_topic: str,
    metadata_model: str = _DEFAULT_MODEL,
    taxonomy_model: str = _DEFAULT_MODEL,
) -> tuple[str, list[PaperProfile]]:
    """Extract PaperProfiles for all papers in a tool output string.

    Only full_text profiles are returned — abstract-only profiles are NOT stored.

    Returns:
        enriched_output: annotated string with [FULL TEXT EXTRACTED] or [ABSTRACT ONLY — reason]
        paper_profiles: list of full-text PaperProfile objects only
    """
    blocks = _parse_blocks_with_urls(tool_output)
    if not blocks:
        return tool_output, []

    tasks = [
        extract_paper_profile(
            b["block"], b["pdf_url"], b["abstract_url"],
            research_topic, tool_name, metadata_model, taxonomy_model,
        )
        for b in blocks
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    enriched = tool_output
    profiles: list[PaperProfile] = []

    for block_info, result in zip(blocks, results):
        if isinstance(result, Exception):
            tag = "[ABSTRACT ONLY — unexpected error]"
        elif result.extraction_status == "full_text":
            tag = "[FULL TEXT EXTRACTED]"
            profiles.append(result)
        else:
            note = result.extraction_note or "no PDF available"
            tag = f"[ABSTRACT ONLY — {note}]"

        enriched = enriched.replace(
            block_info["block"],
            block_info["block"] + f"\n  {tag}",
            1,
        )

    return enriched, profiles
