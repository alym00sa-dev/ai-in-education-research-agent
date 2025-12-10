"""Knowledge graph extraction from research papers."""
import os
import re
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import requests
from pypdf import PdfReader
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from src.neo4j_config import (
    get_neo4j_connection,
    POPULATIONS, USER_TYPES, STUDY_DESIGNS,
    IMPLEMENTATION_OBJECTIVES, OUTCOMES, FINDING_DIRECTIONS
)

load_dotenv()


@dataclass
class PaperDocument:
    """Represents a paper with its text content."""
    url: str
    title: str
    text: str
    source_type: str  # pdf, arxiv, pubmed, web


@dataclass
class StructuredPaper:
    """Represents a paper with extracted structured information."""
    url: str
    title: str
    year: Optional[int]
    venue: Optional[str]
    population: str
    user_type: str
    study_design: str
    implementation_objective: str
    outcome: str
    empirical_finding: Dict[str, Any]


class KGExtractor:
    """Extracts knowledge graph data from research papers."""

    def __init__(self):
        """Initialize the KG extractor."""
        # Load environment variables
        load_dotenv()

        # Also try loading from parent directory
        import os.path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        env_file = os.path.join(parent_dir, '.env')
        if os.path.exists(env_file):
            load_dotenv(dotenv_path=env_file, override=True)

        self.conn = get_neo4j_connection()

        # Use Anthropic Claude for better structured extraction
        from anthropic import Anthropic

        # Get API key with debugging
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        print(f"DEBUG: ANTHROPIC_API_KEY found: {bool(anthropic_api_key)}")
        print(f"DEBUG: .env file path: {env_file}")
        print(f"DEBUG: .env file exists: {os.path.exists(env_file)}")

        if not anthropic_api_key:
            # Try one more time with explicit read
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.startswith('ANTHROPIC_API_KEY='):
                            anthropic_api_key = line.split('=', 1)[1].strip()
                            break
            except:
                pass

        if not anthropic_api_key:
            raise ValueError(f"ANTHROPIC_API_KEY not found. Checked: {env_file}")

        self.anthropic_client = Anthropic(api_key=anthropic_api_key)

        # LLM extraction prompt (from build_kg_csvs.py)
        self.extraction_prompt = self._build_extraction_prompt()

    def _build_extraction_prompt(self) -> str:
        """Build the system prompt for LLM extraction."""
        return f"""
You are an expert research assistant extracting structured metadata from
academic papers about Artificial Intelligence in Education.
Your task is to produce a STRICT JSON object that captures the paper's details
using ONLY the controlled vocabulary provided below.

IMPORTANT RULES:
1. You MUST select exactly ONE value for each category (no lists).
2. You MUST use the exact category strings provided (no synonyms, no paraphrases).
3. If the information is missing, return null or an empty string.
4. All output MUST be valid JSON. No commentary.

-----------------------------------------
FIXED CONTROLLED VOCABULARY (USE EXACT STRINGS)
-----------------------------------------

STUDY POPULATION (MUST choose ONE):
{chr(10).join(f'- "{p}"' for p in POPULATIONS)}

USER TYPE (MUST choose ONE):
{chr(10).join(f'- "{u}"' for u in USER_TYPES)}

STUDY DESIGN (MUST choose ONE):
{chr(10).join(f'- "{s}"' for s in STUDY_DESIGNS)}

IMPLEMENTATION OBJECTIVE (MUST choose ONE):
{chr(10).join(f'- "{i}"' for i in IMPLEMENTATION_OBJECTIVES)}

DEFINITIONS TO HELP CLASSIFICATION:
• "Intelligent Tutoring and Instruction" includes real-time feedback,
  instructional planning, lesson adjustment, teacher coaching, automated grading.

• "AI-Enable Personalized Advising" includes college application support,
  financial aid guidance, and mental health support.

• "Institutional Decision-making" includes resource allocation, predictive analytics,
  administrative decisions, and policy-level AI tools.

• "AI-Enabled Learner Mobility" includes career navigation, skill identification,
  program/credential selection, and academic placement tools.

OUTCOME (MUST choose ONE):
{chr(10).join(f'- "{o}"' for o in OUTCOMES)}

DEFINITIONS TO HELP CLASSIFICATION:
• "Affective - motivation": internal/external factors driving engagement decisions.
• "Affective - engagement": attention, curiosity, and interest during an activity.
• "Affective - persistence": sustained engagement over time, especially through challenges.

EMPIRICAL FINDING DIRECTION (MUST choose ONE):
{chr(10).join(f'- "{f}"' for f in FINDING_DIRECTIONS)}

-----------------------------------------
STRICT OUTPUT JSON SCHEMA
-----------------------------------------

You MUST return JSON in this exact structure:

{{
  "title": "",
  "year": 2023 or null,
  "venue": "",

  "population": "",
  "user_type": "",
  "study_design": "",
  "implementation_objective": "",
  "outcome": "",

  "empirical_finding": {{
      "direction": "",
      "results_summary": "2-3 sentences summarizing the main empirical finding.",
      "measure": "this sub-category is asking what the authors used to compare result (test scores, assignment completion, reading comprehension)",
      "study_size": integer or null,
      "effect_size": number or null
  }}
}}

NOTES:
• All fields MUST contain exactly ONE value.
• If information cannot be determined, return null but DO NOT invent values.
• Do not output anything outside the JSON object.
"""

    def extract_papers_from_sources(self, sources: List[Dict[str, str]]) -> List[PaperDocument]:
        """Extract paper documents from research sources.

        Args:
            sources: List of source dictionaries with 'url' and 'title'

        Returns:
            List of PaperDocument objects
        """
        papers = []

        for source in sources:
            url = source.get('url', '')
            title = source.get('title', 'Untitled')

            if not url:
                continue

            print(f"📄 Fetching: {title[:60]}...")

            try:
                # Determine source type and fetch text
                if 'arxiv.org' in url:
                    text = self._fetch_arxiv(url)
                    source_type = 'arxiv'
                elif '.pdf' in url.lower():
                    text = self._fetch_pdf(url)
                    source_type = 'pdf'
                elif 'pubmed' in url or 'ncbi.nlm.nih.gov' in url:
                    text = self._fetch_pubmed(url)
                    source_type = 'pubmed'
                else:
                    text = self._fetch_webpage(url)
                    source_type = 'web'

                if text and len(text.strip()) > 500:  # Minimum viable content
                    papers.append(PaperDocument(
                        url=url,
                        title=title,
                        text=text,
                        source_type=source_type
                    ))
                    print(f"  ✅ Fetched {len(text)} characters")
                else:
                    print(f"  ⚠️  Skipped (insufficient content)")

            except Exception as e:
                print(f"  ❌ Error: {e}")
                continue

        print(f"\n📊 Successfully fetched {len(papers)} papers")
        return papers

    def _fetch_arxiv(self, url: str) -> str:
        """Fetch text from ArXiv paper."""
        # Convert to PDF URL if needed
        if '/abs/' in url:
            url = url.replace('/abs/', '/pdf/') + '.pdf'

        return self._fetch_pdf(url)

    def _fetch_pdf(self, url: str) -> str:
        """Fetch and extract text from PDF URL."""
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Save temporarily
        temp_path = '/tmp/temp_paper.pdf'
        with open(temp_path, 'wb') as f:
            f.write(response.content)

        # Extract text
        reader = PdfReader(temp_path)
        texts = []
        for page in reader.pages:
            try:
                texts.append(page.extract_text() or "")
            except:
                continue

        return "\n".join(texts)

    def _fetch_pubmed(self, url: str) -> str:
        """Fetch text from PubMed article."""
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Try to find article text
        article_text = soup.find('div', class_='article-details')
        if article_text:
            return article_text.get_text(strip=True, separator='\n')

        # Fallback to abstract
        abstract = soup.find('div', class_='abstract')
        if abstract:
            return abstract.get_text(strip=True, separator='\n')

        return soup.get_text(strip=True, separator='\n')

    def _fetch_webpage(self, url: str) -> str:
        """Fetch text from generic webpage."""
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        return soup.get_text(strip=True, separator='\n')

    def extract_structured_info(self, papers: List[PaperDocument]) -> List[StructuredPaper]:
        """Extract structured information from papers using LLM.

        Args:
            papers: List of PaperDocument objects

        Returns:
            List of StructuredPaper objects
        """
        structured_papers = []

        for i, paper in enumerate(papers, 1):
            print(f"\n🤖 Extracting info from paper {i}/{len(papers)}: {paper.title[:60]}...")

            try:
                # Call Claude for extraction (using Opus 4.5 for better strict instruction following)
                response = self.anthropic_client.messages.create(
                    model="claude-opus-4-5",
                    max_tokens=4000,
                    temperature=0,
                    system=self.extraction_prompt,
                    messages=[
                        {
                            "role": "user",
                            "content": f"Extract structured information from this research paper:\n\n{paper.text[:120000]}"
                        }
                    ]
                )

                content = response.content[0].text.strip()

                # Handle code fences
                if content.startswith("```"):
                    content = content.strip("`")
                    if content.startswith("json"):
                        content = content[4:].strip()

                data = json.loads(content)

                # Validate and create StructuredPaper
                # Match build_kg_csvs.py pattern: validate THEN set to empty if invalid

                # Get raw values
                population = data.get("population")
                user_type = data.get("user_type")
                study_design = data.get("study_design")
                implementation_objective = data.get("implementation_objective")
                outcome = data.get("outcome")

                # Validate against controlled vocabulary - if not in list, set to empty
                if population not in POPULATIONS:
                    population = ""
                if user_type not in USER_TYPES:
                    user_type = ""
                if study_design not in STUDY_DESIGNS:
                    study_design = ""
                if implementation_objective not in IMPLEMENTATION_OBJECTIVES:
                    implementation_objective = ""
                if outcome not in OUTCOMES:
                    outcome = ""

                # Skip papers where all key taxonomy fields are empty
                if not any([population, user_type, study_design, implementation_objective, outcome]):
                    print(f"  ⚠️  Skipping paper - all taxonomy fields are null/empty")
                    continue

                # Clean up empirical_finding - match build_kg_csvs.py pattern
                empirical_finding = data.get("empirical_finding", {}) or {}

                # Validate direction
                direction = empirical_finding.get("direction")
                if direction not in FINDING_DIRECTIONS:
                    direction = ""
                empirical_finding['direction'] = direction

                # Clean up other finding fields
                empirical_finding['results_summary'] = empirical_finding.get('results_summary') or ""
                empirical_finding['measure'] = empirical_finding.get('measure') or ""

                structured_paper = StructuredPaper(
                    url=paper.url,
                    title=data.get("title", paper.title),
                    year=data.get("year"),
                    venue=data.get("venue"),
                    population=population,
                    user_type=user_type,
                    study_design=study_design,
                    implementation_objective=implementation_objective,
                    outcome=outcome,
                    empirical_finding=empirical_finding
                )

                structured_papers.append(structured_paper)

                # Debug output with validation
                print(f"  ✅ Extracted:")
                print(f"     Population: '{structured_paper.population}' {'✓' if structured_paper.population in POPULATIONS else '✗ MISMATCH' if structured_paper.population else '(empty)'}")
                print(f"     UserType: '{structured_paper.user_type}' {'✓' if structured_paper.user_type in USER_TYPES else '✗ MISMATCH' if structured_paper.user_type else '(empty)'}")
                print(f"     StudyDesign: '{structured_paper.study_design}' {'✓' if structured_paper.study_design in STUDY_DESIGNS else '✗ MISMATCH' if structured_paper.study_design else '(empty)'}")
                print(f"     Objective: '{structured_paper.implementation_objective}' {'✓' if structured_paper.implementation_objective in IMPLEMENTATION_OBJECTIVES else '✗ MISMATCH' if structured_paper.implementation_objective else '(empty)'}")
                print(f"     Outcome: '{structured_paper.outcome}' {'✓' if structured_paper.outcome in OUTCOMES else '✗ MISMATCH' if structured_paper.outcome else '(empty)'}")

                # Safely handle empirical_finding
                finding = structured_paper.empirical_finding
                if finding and isinstance(finding, dict):
                    direction = finding.get('direction') or ''
                    summary = finding.get('results_summary') or ''
                    measure = finding.get('measure') or ''
                    study_size = finding.get('study_size')
                    effect_size = finding.get('effect_size')

                    print(f"     Finding Direction: '{direction}' {'✓' if direction in FINDING_DIRECTIONS else '✗ MISMATCH' if direction else '(empty)'}")
                    print(f"     Finding Summary: {len(summary)} chars" if summary else "     Finding Summary: 0 chars")
                    print(f"     Measure: '{measure}'")
                    print(f"     Study Size: {study_size}")
                    print(f"     Effect Size: {effect_size}")
                else:
                    print(f"     Finding: No empirical finding data")

            except Exception as e:
                print(f"  ❌ Extraction failed: {e}")
                continue

        print(f"\n📊 Successfully extracted info from {len(structured_papers)} papers")
        return structured_papers

    def add_to_neo4j(self, papers: List[StructuredPaper], session_id: str) -> int:
        """Add structured papers to Neo4j knowledge graph.

        Args:
            papers: List of StructuredPaper objects
            session_id: The session ID to tag papers with

        Returns:
            Number of papers successfully added
        """
        added_count = 0
        added_date = datetime.now().isoformat()

        with self.conn.driver.session(database=self.conn.database) as db_session:
            for paper in papers:
                try:
                    # Generate IDs
                    paper_id = f"paper_{hash(paper.title) % 100000}"
                    finding_id = f"finding_{hash(paper.title) % 100000}"

                    print(f"  Adding paper: {paper.title[:60]}...")

                    # MERGE Paper node (avoid duplicates by title)
                    db_session.run(
                        """
                        MERGE (p:Paper {title: $title})
                        ON CREATE SET
                            p.paper_id = $paper_id,
                            p.year = $year,
                            p.venue = $venue,
                            p.url = $url,
                            p.session_id = $session_id,
                            p.added_date = $added_date
                        ON MATCH SET
                            p.session_id = $session_id
                        """,
                        paper_id=paper_id,
                        title=paper.title,
                        year=paper.year,
                        venue=paper.venue or "",
                        url=paper.url,
                        session_id=session_id,
                        added_date=added_date
                    )

                    # CREATE EmpiricalFinding node - ensure finding_data is always a dict
                    finding_data = paper.empirical_finding if isinstance(paper.empirical_finding, dict) else {}

                    # Safely extract values with defaults
                    direction = finding_data.get("direction") if finding_data else ""
                    results_summary = finding_data.get("results_summary") if finding_data else ""
                    measure = finding_data.get("measure") if finding_data else ""
                    study_size = finding_data.get("study_size") if finding_data else None
                    effect_size = finding_data.get("effect_size") if finding_data else None

                    db_session.run(
                        """
                        MERGE (p:Paper {title: $title})
                        MERGE (f:EmpiricalFinding {finding_id: $finding_id})
                        ON CREATE SET
                            f.direction = $direction,
                            f.results_summary = $results_summary,
                            f.measure = $measure,
                            f.study_size = $study_size,
                            f.effect_size = $effect_size
                        MERGE (p)-[:REPORTS_FINDING]->(f)
                        """,
                        title=paper.title,
                        finding_id=finding_id,
                        direction=direction or "",
                        results_summary=results_summary or "",
                        measure=measure or "",
                        study_size=study_size,
                        effect_size=effect_size
                    )

                    # Create taxonomy relationships
                    if paper.population in POPULATIONS:
                        db_session.run(
                            """
                            MATCH (p:Paper {title: $title})
                            MATCH (pop:Population {id: $population})
                            MERGE (p)-[:TARGETS_POPULATION]->(pop)
                            """,
                            title=paper.title,
                            population=paper.population
                        )

                    if paper.user_type in USER_TYPES:
                        db_session.run(
                            """
                            MATCH (p:Paper {title: $title})
                            MATCH (ut:UserType {id: $user_type})
                            MERGE (p)-[:TARGETS_USER_TYPE]->(ut)
                            """,
                            title=paper.title,
                            user_type=paper.user_type
                        )

                    if paper.study_design in STUDY_DESIGNS:
                        db_session.run(
                            """
                            MATCH (p:Paper {title: $title})
                            MATCH (sd:StudyDesign {id: $study_design})
                            MERGE (p)-[:USES_STUDY_DESIGN]->(sd)
                            """,
                            title=paper.title,
                            study_design=paper.study_design
                        )

                    if paper.implementation_objective in IMPLEMENTATION_OBJECTIVES:
                        db_session.run(
                            """
                            MATCH (p:Paper {title: $title})
                            MATCH (io:ImplementationObjective {id: $objective})
                            MERGE (p)-[:HAS_IMPLEMENTATION_OBJECTIVE]->(io)
                            """,
                            title=paper.title,
                            objective=paper.implementation_objective
                        )

                    if paper.outcome in OUTCOMES:
                        db_session.run(
                            """
                            MATCH (p:Paper {title: $title})
                            MATCH (out:Outcome {id: $outcome})
                            MERGE (p)-[:FOCUSES_ON_OUTCOME]->(out)
                            """,
                            title=paper.title,
                            outcome=paper.outcome
                        )

                        # Link Outcome to Finding
                        db_session.run(
                            """
                            MATCH (out:Outcome {id: $outcome})
                            MATCH (f:EmpiricalFinding {finding_id: $finding_id})
                            MERGE (out)-[:HAS_FINDING]->(f)
                            """,
                            outcome=paper.outcome,
                            finding_id=finding_id
                        )

                    # Create/update derived relationship: ImplementationObjective -> Outcome
                    if (paper.implementation_objective in IMPLEMENTATION_OBJECTIVES and
                        paper.outcome in OUTCOMES):
                        db_session.run(
                            """
                            MATCH (io:ImplementationObjective {id: $objective})
                            MATCH (out:Outcome {id: $outcome})
                            MERGE (io)-[r:TARGETS_OUTCOME]->(out)
                            ON CREATE SET r.weight = 1
                            ON MATCH SET r.weight = r.weight + 1
                            """,
                            objective=paper.implementation_objective,
                            outcome=paper.outcome
                        )

                    added_count += 1
                    print(f"  ✅ Added to Neo4j: {paper.title[:60]}")

                except Exception as e:
                    import traceback
                    print(f"  ❌ Failed to add {paper.title[:60]}: {e}")
                    print(f"     Error type: {type(e).__name__}")
                    print(f"     Traceback: {traceback.format_exc()}")
                    continue

        print(f"\n✅ Successfully added {added_count}/{len(papers)} papers to Neo4j")
        return added_count
