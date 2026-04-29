"""PDF extraction v2 — fetches full text and produces KG-aligned PaperProfileV2 objects.

Extraction uses two parallel LLM calls:
  Call 1 (_extract_metadata): unchanged from v1 — factual fields (title, doi, year, venue,
      population, study_design, extended_summary, limitations, implementation context, geography).
  Call 2 (_extract_kg_taxonomy): NEW — identifies the specific named AI tool(s) studied
      (not a pre-seeded category classifier), extracts per-tool findings, and assigns
      evidence quality/impact tiers.

Call 2 schema is aligned with the KG curator deep-dive schema:
  - IdentifiedTool: name, specificity, category_key, is_named_product, description, use_case, findings
  - KGFinding: outcome_category, finding_type, direction, finding_summary, measure,
               effect_size, confidence_interval, sample_size
  - verdict: named_tool_found | genai_general | archetype_only | framework_only | no_tool

Only papers with successful full-text extraction (>= 300 chars) produce a PaperProfileV2.
Abstract-only results are logged but not returned.
"""

import asyncio
import os
import re
from typing import Literal, Optional

import fitz  # pymupdf
import httpx
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from state import PaperMetadataExtract, KGFinding, IdentifiedTool

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; EduResearchBot/2.0)"}
_DEFAULT_MODEL = "gpt-5.4-2026-03-05"

PDF_EXTRACTABLE_TOOLS = {
    "eric_search",
    "openalex_search",
    "arxiv_search",
    "elsevier_search",
    "semantic_scholar_search",
}

# Known tools_final node names — passed to LLM as lookup hints
_KNOWN_TOOLS = [
    # Named LLM families (canonical names — see normalization table in prompt)
    "ChatGPT",
    "Claude",
    "Gemini",
    "LLaMA",
    "DeepSeek",
    "Mistral",
    "Kimi",
    "Qwen",
    # Named EdTech products
    "ALEKS",
    "ASSISTments",
    "Cognitive Tutor",
    "Duolingo",
    "I Can Learn",
    "Khan Academy",
    "Khanmigo",
    "Lexia PowerUp",
    "MATHia",
    "MWPTutor",
    "POE",
    "Pebasco",
    "Photomath",
    "Spark",
    "Tutor CoPilot",
    "Yixue Squirrel AI",
    # Generic archetypes
    "Adaptive Feedback System (General)",
    "CAI (General)",
    "GenAI (General)",
    "ITS (General)",
    "Mobile Learning Apps (General)",
]

# LLM family normalization — maps model variants to canonical tool names
_LLM_FAMILY_TABLE = {
    "ChatGPT": "Any OpenAI / GPT model: GPT-4, GPT-4o, GPT-4-turbo, GPT-3.5, GPT-3.5-turbo, ChatGPT, ChatGPT-4, o1, o3, any 'GPT-*' variant",
    "Claude":  "Any Anthropic model: Claude, Claude 2, Claude 3, Sonnet, Haiku, Opus, Claude Instant, any 'Claude-*' variant",
    "Gemini":  "Any Google model: Gemini, Gemini Pro, Gemini Ultra, Gemini Flash, Bard (Google's prior name), PaLM, PaLM 2",
    "LLaMA":   "Any Meta / LLaMA model: LLaMA, Llama 2, Llama 3, Meta AI, OPT, any open-weight Meta model",
    "DeepSeek":"Any DeepSeek model: DeepSeek, DeepSeek-R1, DeepSeek-V2, DeepSeek-Coder, any DeepSeek variant",
    "Mistral": "Any Mistral AI model: Mistral, Mistral 7B, Mixtral, Mistral Large, Mistral Small, any Mistral variant",
    "Kimi":    "Any Moonshot AI / Kimi model: Kimi, Kimi Chat, Moonshot, any Kimi variant",
    "Qwen":    "Any Alibaba / Qwen model: Qwen, Qwen2, Qwen-VL, Tongyi Qianwen, any Qwen variant",
}

CATEGORY_KEY_OPTIONS = [
    "tutoring_instruction",
    "feedback_evaluation",
    "content_generation",
    "personalization_adaptation",
    "prediction_analytics",
    "language_speech",
    "other",
]

# ── New KG taxonomy models — now defined in state.py, imported above ───────────

# class KGFinding(BaseModel):
#     """One finding tied to a specific tool — aligned with tools_final finding schema."""
#
#     outcome_category: str = Field(
#         description=(
#             "One of: Academic — Literacy, Academic — Language Fluency, "
#             "Academic — Mathematical Numeracy, Academic — Scientific Reasoning, "
#             "Academic — Other, Social-Emotional Skills, Durable Skills, "
#             "Operational Efficiency, Systemic / Institutional Impact"
#         )
#     )
#     finding_type: str = Field(
#         description="primary (RCT/QED single study) | pooled_meta (meta-analysis aggregate) | review_synthesis (systematic review)"
#     )
#     direction: str = Field(
#         description="positive | negative | null | mixed"
#     )
#     finding_summary: str = Field(
#         description="2-3 sentences. Include effect sizes (e.g. d=0.42), sample sizes (n=), and measures exactly as reported."
#     )
#     measure: str = Field(
#         default="not_reported",
#         description="What was measured (e.g. standardized test scores, engagement survey)"
#     )
#     effect_size: str = Field(default="not_reported")
#     confidence_interval: str = Field(default="not_reported")
#     sample_size: str = Field(
#         default="not_reported",
#         description="e.g. 'n=312' or 'not_reported'"
#     )
#
#
# class IdentifiedTool(BaseModel):
#     """A specific AI tool or archetype identified as the focus of this paper."""
#
#     name: str = Field(
#         description=(
#             "Canonical name of the tool. "
#             "If it matches a known node, use that exact name. "
#             "If no specific named tool, use 'GenAI (General)'. "
#             "For review/meta papers with no per-tool breakdown, use the archetype (e.g. 'ITS (General)', 'CAI (General)'). "
#             "For framework papers, use the conceptual system name if one exists."
#         )
#     )
#     is_named_product: bool = Field(
#         description="True if this is a specific named commercial or research product. False if generic/archetype."
#     )
#     specificity: str = Field(
#         description="named_tool (specific product) | category (archetype or generic)"
#     )
#     category_key: list[str] = Field(
#         description=f"1-2 functional roles from: {', '.join(CATEGORY_KEY_OPTIONS)}"
#     )
#     description: str = Field(
#         description="What the tool IS at a product/system level (not study-specific)"
#     )
#     use_case: str = Field(
#         description="How this tool was specifically used or studied in this paper"
#     )
#     findings: list[KGFinding] = Field(default_factory=list)


class PaperKGExtract(BaseModel):
    """Call 2 output — KG taxonomy with tool identification and per-tool findings."""

    tools: list[IdentifiedTool] = Field(default_factory=list)
    verdict: str = Field(
        description=(
            "named_tool_found — specific named product identified. "
            "genai_general — generic LLM/chatbot, no named product. "
            "archetype_only — review/meta paper, only category-level findings. "
            "framework_only — theoretical/framework paper, no empirical tool evaluation. "
            "no_tool — paper does not study an AI tool."
        )
    )
    quality_tier: str = Field(
        default="yellow",
        description="K-12 Evidence Framework Quality tier: blue | green | yellow | red"
    )
    quality_tier_rationale: str = Field(default="")
    impact_tier: str = Field(
        default="yellow",
        description="K-12 Evidence Framework Impact tier: blue | green | yellow | red"
    )
    impact_tier_rationale: str = Field(default="")


class CitationRef(BaseModel):
    """One cited work extracted from the paper's bibliography."""
    title: str
    doi: Optional[str] = None
    year: Optional[int] = None
    venue: Optional[str] = None
    citation_level: Literal[1, 2, 3] = Field(
        default=1,
        description=(
            "Depth of intellectual dependency. "
            "1 = Shallow/Referential: mentioned in passing, grouped list cite, 'see also', cited in intro/discussion without engagement. "
            "2 = Conceptual/Grounded: theory, framework, or construct that shapes what this study measures or argues — removing it would require rewriting the theory/framing section. "
            "3 = Methodological/Foundational: directly shapes design, protocol, measures, or serves as comparison condition — removing it would require rewriting the methods section."
        )
    )
    citation_context: Optional[str] = Field(
        default=None,
        description="Brief phrase (≤15 words) showing exactly how this work is used. Only for L2/L3 — leave null for L1."
    )


class PaperCitationExtract(BaseModel):
    """Call 3 output — structured bibliography."""
    citations: list[CitationRef] = Field(default_factory=list)


class PaperProfileV2(BaseModel):
    """Full KG-aligned paper profile — Call 1 metadata + Call 2 KG taxonomy + Call 3 citations."""

    # ── Core metadata (from Call 1) ──────────────────────────────────────────
    title: str
    doi: Optional[str] = None
    year: Optional[int] = None
    venue: Optional[str] = None
    url: str = ""
    source_db: str = ""
    populations: list[str] = Field(default_factory=list)
    user_types: list[str] = Field(default_factory=list)
    study_design: str = "not_reported"
    extended_summary: str = ""
    limitations: list[str] = Field(default_factory=list)
    duration_weeks: str = "not_reported"
    setting: str = "not_reported"
    teacher_training: str = "not_reported"
    implementation_fidelity: str = "not_reported"
    study_country: str = "not_reported"
    study_region: str = "not_reported"

    # ── KG taxonomy (from Call 2) ────────────────────────────────────────────
    identified_tools: list[IdentifiedTool] = Field(default_factory=list)
    verdict: str = "no_tool"
    quality_tier: str = "yellow"
    quality_tier_rationale: str = ""
    impact_tier: str = "yellow"
    impact_tier_rationale: str = ""

    # ── Citations (from Call 3) ──────────────────────────────────────────────
    citations: list[CitationRef] = Field(default_factory=list)

    # ── Extraction metadata ──────────────────────────────────────────────────
    extraction_status: str = "abstract_only"  # full_text | abstract_only
    extraction_note: str = ""


# ── Call 1: Metadata (unchanged from v1) ──────────────────────────────────────

_METADATA_SYSTEM = """You are extracting factual metadata from an academic paper for a knowledge graph about AI and technology interventions in education.
Be precise. Use "not_reported" for any field where the information is genuinely absent from the text."""

_METADATA_HUMAN = """Research topic this paper was retrieved for: {research_topic}

Paper text:
{pdf_text}

---

Extract the following fields:

### Metadata (all of these fields are important, do not skip out on them)
- title: full paper title
- doi: DOI if present, else null (this is important to find)
- year: publication year as integer, else null
- venue: journal or conference name, else null
- populations: list all population groups studied — include every group present. Use these values only:
  "Elementary (PreK-5th)", "Middle School (6th-8th)", "High School (9th-12th)",
  "Undergraduate", "Graduate / Doctoral", "Adult (non-academic)", "K-12 (unspecified grade)"
  If no population is reported, return [].
  Examples: a paper studying undergrads and faculty → ["Undergraduate", "Graduate / Doctoral", "Adult (non-academic)"]
  A K-12 meta-analysis spanning elementary through high school → ["Elementary (PreK-5th)", "Middle School (6th-8th)", "High School (9th-12th)"]
- user_types: list all user roles present — include every role. Use these values only:
  "Student", "Educator", "Administrator", "Parent", "School", "Community"
  Examples: a paper studying both students and teachers → ["Student", "Educator"]
  If no role is reported, return [].
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


# ── Call 2: KG Taxonomy (new) ──────────────────────────────────────────────────

_TAXONOMY_SYSTEM_V2 = """You are extracting AI tool identity and findings from academic education research papers for a knowledge graph.
Be precise. Identify the specific named product where one exists. Do not infer beyond the text."""

_TAXONOMY_HUMAN_V2 = """Research topic: {research_topic}

Paper text:
{pdf_text}

---

## Step 1 — Identify the AI tool(s) this paper studies

Known nodes already in our knowledge graph (match these exactly if applicable):
{known_tools}

### LLM Family Normalization — ALWAYS apply before naming any LLM tool
When a paper uses any LLM model, normalize to the canonical family name below.
Do NOT use version numbers, variant names, or raw model IDs as the tool name.

{llm_family_table}

Examples:
- Paper uses "GPT-4o" → name="ChatGPT"
- Paper uses "Claude 3 Sonnet" → name="Claude"
- Paper uses "Llama 2 70B" → name="LLaMA"
- Paper uses "Bard" → name="Gemini"
- Paper uses "Mixtral 8x7B" → name="Mistral"
- Paper uses an unnamed LLM chatbot → name="GenAI (General)"

Rules:
1. SPECIFIC NAMED PRODUCT (ChatGPT, ASSISTments, Duolingo, Khan Academy, Khanmigo, etc.)
   → use the exact canonical name, is_named_product=true, specificity="named_tool"
   → if it matches a known node above, use that exact name
   → ALWAYS apply LLM Family Normalization first for any LLM-based tool

2. GENERIC LLM / AI ASSISTANT with no specific product or family named
   → name="GenAI (General)", is_named_product=false, specificity="category"

3. META-ANALYSIS / REVIEW studying many heterogeneous tools with no per-tool breakdown
   → use the archetype name (e.g. "ITS (General)", "CAI (General)"), specificity="category"
   → verdict="archetype_only"

4. FRAMEWORK / THEORETICAL paper — no empirical tool evaluation
   → name the AI system TYPE being proposed/discussed using a functional category name
   → do NOT use the study methodology as the name (e.g. not "storyboard scenarios", not "conceptual framework")
   → do NOT use generic descriptions (e.g. not "AI applications for SRL support")
   → findings=[], verdict="framework_only"

5. NEVER pool named tools (e.g. do not write "ChatGPT — pooled")
6. NEVER include ML prediction algorithms (Decision Tree, Random Forest, SVM) as tools
7. Named LLM models (ChatGPT, GPT-*, Claude, Gemini, Llama) are ALWAYS named_tool

## Step 2 — Extract findings per tool

For each tool, extract all findings the paper reports.
- finding_type: "primary" for RCT/QED, "pooled_meta" for meta-analysis aggregates, "review_synthesis" for systematic reviews
- Framework/Theoretical papers → findings=[] (empty list)
- Include effect sizes, sample sizes, confidence intervals exactly as reported — use "not_reported" if absent
- One finding per distinct outcome measured

## Step 3 — Evidence quality and impact tiers

Quality tier:
- blue: Meta-analysis OR well-designed RCT with all credibility criteria
- green: Well-designed QED or meta-analysis/RCT with some concerns
- yellow: Correlational, qualitative, or mixed-methods
- red: No clear methodology, opinion, or grey literature

Impact tier:
- blue: Medium or large impact (effect size >= 0.20)
- green: Modest impact (0.05–0.20)
- yellow: Modest or unclear impact
- red: No impact or negative impact

Provide a 1-2 sentence rationale for each tier.
"""


# ── Call 3: Citation extraction ───────────────────────────────────────────────

_CITATION_SYSTEM = """You are extracting a structured bibliography from an academic paper, including the depth of each citation's intellectual role.
Be precise and complete. Extract every reference in the References/Bibliography section."""

_CITATION_HUMAN = """Paper text (focus on the References / Bibliography section near the end, but also scan the full text to understand how each work is used):
{pdf_text}

---

Extract every cited work from the References or Bibliography section.
For each entry return:
- title: the full title of the cited work (required)
- doi: DOI if present (e.g. "10.1016/j.compedu.2023.104801"), else null
- year: publication year as integer if present, else null
- venue: journal or conference name if present, else null
- citation_level: depth of intellectual dependency — assign using the removal test below
- citation_context: brief phrase (≤15 words) showing how this work is used — only for L2/L3, null for L1

## Citation depth — the removal test

Ask: "If this citation were removed, would the authors need to rewrite a substantive section?"

**Level 1 — Shallow/Referential** (default for most citations)
- No → it's L1
- Signals: grouped list cites ("Smith, 2018; Jones, 2019; Lee, 2020"), "as noted by", "prior work includes", "see also", cited in intro/discussion without direct engagement
- citation_context: null

**Level 2 — Conceptual/Grounded**
- Yes, they'd need to rewrite the theory or framing section → L2
- Signals: named and engaged with — "drawing on Smith's (2018) SRL framework", "consistent with Jones's (2019) conceptualization of...", the study's construct or argument is built on this work
- citation_context: required — e.g. "SRL framework adopted from this work"

**Level 3 — Methodological/Foundational**
- Yes, they'd need to rewrite the methods section → L3
- Signals: "following the protocol of", "we replicate", "extending Smith's experimental design", cited in methods as the design blueprint, or explicitly serves as the comparison/control condition
- citation_context: required — e.g. "direct methodological replication of Study 2"

Return an empty list if no references section is found.
Do NOT extract the paper's own metadata — only its cited references.
"""


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _try_unpaywall(doi: str) -> str | None:
    """Look up an open-access PDF URL via Unpaywall."""
    if not doi:
        return None
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            r = await client.get(
                f"https://api.unpaywall.org/v2/{doi}?email=research@aiedu.dev"
            )
        if r.status_code != 200:
            return None
        best = r.json().get("best_oa_location") or {}
        return best.get("url_for_pdf") or best.get("url")
    except Exception:
        return None


async def _try_semantic_scholar_pdf(title: str) -> str | None:
    """Look up an open-access PDF URL via Semantic Scholar title search."""
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            r = await client.get(
                "https://api.semanticscholar.org/graph/v1/paper/search",
                params={"query": title[:100], "limit": 1, "fields": "openAccessPdf"},
            )
        if r.status_code != 200:
            return None
        papers = r.json().get("data", [])
        if papers and papers[0].get("openAccessPdf"):
            return papers[0]["openAccessPdf"].get("url")
    except Exception:
        return None
    return None


def _extract_doi_from_url(url: str) -> str | None:
    """Extract a DOI from a doi.org URL or inline DOI pattern."""
    m = re.search(r"(?:doi\.org/|doi=)(10\.\d{4,}/\S+)", url)
    if m:
        return m.group(1).rstrip(".,);>\"'")
    m = re.search(r"\b(10\.\d{4,}/\S+)", url)
    return m.group(1).rstrip(".,);>\"'") if m else None


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


async def _extract_citations(
    text: str, model_name: str
) -> PaperCitationExtract:
    """Call 3 — bibliography extraction."""
    model = init_chat_model(
        model=model_name,
        max_tokens=8192,
        api_key=_get_api_key(model_name),
        tags=["langsmith:nostream"],
    ).with_structured_output(PaperCitationExtract)

    # Feed the last 30k chars — references section is almost always at the end
    text_slice = text[-30000:] if len(text) > 30000 else text

    return await model.ainvoke([
        SystemMessage(content=_CITATION_SYSTEM),
        HumanMessage(content=_CITATION_HUMAN.format(pdf_text=text_slice)),
    ])


async def _extract_kg_taxonomy(
    text: str, research_topic: str, model_name: str,
    known_interventions: list[str] | None = None,
) -> PaperKGExtract:
    """Call 2 — tool identification, per-tool findings, evidence tiers."""
    model = init_chat_model(
        model=model_name,
        max_tokens=6144,
        api_key=_get_api_key(model_name),
        tags=["langsmith:nostream"],
    ).with_structured_output(PaperKGExtract)

    combined = list(_KNOWN_TOOLS)
    if known_interventions:
        existing_set = {t.lower() for t in combined}
        for name in known_interventions:
            if name.lower() not in existing_set:
                combined.append(name)
                existing_set.add(name.lower())
    known_tools_str = "\n".join(f"- {t}" for t in combined)
    llm_family_str = "\n".join(
        f"- {name}: {variants}" for name, variants in _LLM_FAMILY_TABLE.items()
    )

    return await model.ainvoke([
        SystemMessage(content=_TAXONOMY_SYSTEM_V2),
        HumanMessage(content=_TAXONOMY_HUMAN_V2.format(
            research_topic=research_topic,
            pdf_text=text[:60000],
            known_tools=known_tools_str,
            llm_family_table=llm_family_str,
        )),
    ])


async def _extract_profile_v2(
    text: str,
    research_topic: str,
    metadata_model: str,
    taxonomy_model: str,
    extract_citations: bool = True,
    known_interventions: list[str] | None = None,
) -> PaperProfileV2:
    """Run extraction calls in parallel and merge into a PaperProfileV2.

    When extract_citations=False, skips Call 3 (bibliography extraction) for speed
    during the research pipeline. Pass True for KG pipeline runs.
    """
    if extract_citations:
        meta, taxonomy, citation_extract = await asyncio.gather(
            _extract_metadata(text, research_topic, metadata_model),
            _extract_kg_taxonomy(text, research_topic, taxonomy_model, known_interventions),
            _extract_citations(text, taxonomy_model),
        )
        citations = citation_extract.citations
    else:
        meta, taxonomy = await asyncio.gather(
            _extract_metadata(text, research_topic, metadata_model),
            _extract_kg_taxonomy(text, research_topic, taxonomy_model, known_interventions),
        )
        citations = []

    return PaperProfileV2(
        # From Call 1
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
        # From Call 2
        identified_tools=taxonomy.tools,
        verdict=taxonomy.verdict,
        quality_tier=taxonomy.quality_tier,
        quality_tier_rationale=taxonomy.quality_tier_rationale,
        impact_tier=taxonomy.impact_tier,
        impact_tier_rationale=taxonomy.impact_tier_rationale,
        # From Call 3
        citations=citations,
    )


# ── Public API ─────────────────────────────────────────────────────────────────

async def extract_paper_profile_v2(
    paper_block: str,
    pdf_url: str | None,
    abstract_url: str,
    research_topic: str,
    source_db: str,
    metadata_model: str = _DEFAULT_MODEL,
    taxonomy_model: str = _DEFAULT_MODEL,
    extract_citations: bool = True,
    known_interventions: list[str] | None = None,
) -> PaperProfileV2:
    """Attempt full-text extraction for one paper. Returns PaperProfileV2.

    Only produces a usable profile if full-text PDF extraction succeeds (>= 300 chars).
    Abstract-only papers are returned with extraction_status='abstract_only'.
    """
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

    # 3. Try Unpaywall (DOI-based OA lookup)
    if text_for_extraction is None:
        doi_hint = _extract_doi_from_url(abstract_url) or _extract_doi_from_url(pdf_url or "")
        if not doi_hint:
            doi_hint = _extract_doi_from_url(paper_block)
        if doi_hint:
            oa_url = await _try_unpaywall(doi_hint)
            if oa_url:
                pdf_bytes, status = await _fetch_pdf_bytes(oa_url)
                if pdf_bytes:
                    pdf_text = _extract_text_from_pdf(pdf_bytes)
                    if len(pdf_text.strip()) >= 300:
                        text_for_extraction = pdf_text
                        extraction_status = "full_text"
                        extraction_note = f"via unpaywall"
                    else:
                        extraction_note = "unpaywall PDF too short"
                else:
                    extraction_note = f"unpaywall fetch: {status}"

    # 4. Try Semantic Scholar open-access PDF (title-based)
    if text_for_extraction is None:
        title_match = re.search(r"\[\d+\] Title:\s*(.+)", paper_block)
        if title_match:
            ss_url = await _try_semantic_scholar_pdf(title_match.group(1).strip())
            if ss_url:
                pdf_bytes, status = await _fetch_pdf_bytes(ss_url)
                if pdf_bytes:
                    pdf_text = _extract_text_from_pdf(pdf_bytes)
                    if len(pdf_text.strip()) >= 300:
                        text_for_extraction = pdf_text
                        extraction_status = "full_text"
                        extraction_note = "via semantic scholar"
                    else:
                        extraction_note = "semantic scholar PDF too short"

    # 5. No full text — skip extraction, return shell profile
    if text_for_extraction is None:
        title_match = re.search(r"\[\d+\] Title:\s*(.+)", paper_block)
        title = title_match.group(1).strip() if title_match else "Unknown"
        return PaperProfileV2(
            title=title,
            url=abstract_url,
            source_db=source_db,
            extraction_status="abstract_only",
            extraction_note=extraction_note or "no PDF available",
        )

    try:
        profile = await _extract_profile_v2(
            text_for_extraction, research_topic, metadata_model, taxonomy_model,
            extract_citations=extract_citations,
            known_interventions=known_interventions,
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
        return PaperProfileV2(
            title=title,
            url=abstract_url,
            source_db=source_db,
            extraction_status="abstract_only",
            extraction_note=f"extraction failed: {type(e).__name__}",
        )


async def enrich_tool_output_v2(
    tool_name: str,
    tool_output: str,
    research_topic: str,
    metadata_model: str = _DEFAULT_MODEL,
    taxonomy_model: str = _DEFAULT_MODEL,
    extract_citations: bool = False,
) -> tuple[str, list[PaperProfileV2]]:
    """Extract PaperProfileV2 objects for all papers in a tool output string.

    Only full_text profiles are returned — abstract-only profiles are NOT stored.
    extract_citations=False (default) skips Call 3 — use True for KG pipeline runs.

    Returns:
        enriched_output: annotated string with [FULL TEXT EXTRACTED] or [ABSTRACT ONLY — reason]
        paper_profiles: list of full-text PaperProfileV2 objects only
    """
    blocks = _parse_blocks_with_urls(tool_output)
    if not blocks:
        return tool_output, []

    tasks = [
        extract_paper_profile_v2(
            b["block"], b["pdf_url"], b["abstract_url"],
            research_topic, tool_name, metadata_model, taxonomy_model,
            extract_citations=extract_citations,
        )
        for b in blocks
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    enriched = tool_output
    profiles: list[PaperProfileV2] = []

    for block_info, result in zip(blocks, results):
        if isinstance(result, Exception):
            tag = "[ABSTRACT ONLY — unexpected error]"
        elif result.extraction_status == "full_text":
            tag = f"[FULL TEXT EXTRACTED | verdict={result.verdict} | tools={[t.name for t in result.identified_tools]}]"
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
