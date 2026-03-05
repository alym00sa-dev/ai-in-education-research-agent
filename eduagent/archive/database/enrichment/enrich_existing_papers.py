"""
Batch enrichment script to update all existing papers in Neo4j with enhanced EmpiricalFinding data.

This script:
1. Queries all papers from Neo4j
2. Re-fetches full text from stored URLs
3. Extracts enhanced information using updated prompt
4. Updates EmpiricalFinding nodes with new properties
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv

from src.neo4j_config import get_neo4j_connection, FINDING_DIRECTIONS
from src.enhanced_extraction_prompt import (
    build_enhanced_extraction_prompt,
    REGIONS, SCHOOL_TYPES, PUBLIC_PRIVATE_STATUS, TITLE_I_STATUS,
    SES_INDICATOR, SPECIAL_ED_SERVICES, URBAN_TYPE, GOVERNANCE_TYPE,
    INSTITUTIONAL_LEVEL, POSTSECONDARY_TYPE
)

# Import fetch methods from kg_extractor
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.kg_extractor import KGExtractor

load_dotenv()


class PaperEnricher:
    """Enriches existing papers with enhanced EmpiricalFinding data."""

    def __init__(self):
        """Initialize the enricher."""
        self.conn = get_neo4j_connection()
        self.anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.extraction_prompt = build_enhanced_extraction_prompt()
        self.extractor = KGExtractor()  # Reuse fetch methods

    def get_all_papers(self) -> List[Dict[str, Any]]:
        """Get all papers from Neo4j with their URLs and finding IDs."""
        with self.conn.driver.session(database=self.conn.database) as session:
            result = session.run("""
                MATCH (p:Paper)-[:REPORTS_FINDING]->(f:EmpiricalFinding)
                RETURN p.title as title,
                       p.url as url,
                       p.paper_id as paper_id,
                       f.finding_id as finding_id,
                       f.direction as current_direction,
                       f.results_summary as current_summary,
                       f.effect_size as current_effect_size
                ORDER BY p.added_date DESC
            """)

            papers = []
            for record in result:
                papers.append({
                    'title': record['title'],
                    'url': record['url'],
                    'paper_id': record['paper_id'],
                    'finding_id': record['finding_id'],
                    'current_direction': record.get('current_direction'),
                    'current_summary': record.get('current_summary'),
                    'current_effect_size': record.get('current_effect_size')
                })

            return papers

    def fetch_paper_text(self, url: str, title: str) -> Optional[str]:
        """Fetch full text from paper URL using existing methods."""
        if not url:
            return None

        try:
            # Determine source type and fetch
            if 'arxiv.org' in url:
                return self.extractor._fetch_arxiv(url)
            elif '.pdf' in url.lower():
                return self.extractor._fetch_pdf(url)
            elif 'pubmed' in url or 'ncbi.nlm.nih.gov' in url:
                return self.extractor._fetch_pubmed(url)
            else:
                return self.extractor._fetch_webpage(url)

        except Exception as e:
            print(f"  ❌ Failed to fetch text: {e}")
            return None

    def extract_enhanced_data(self, paper_text: str, paper_title: str) -> Optional[Dict[str, Any]]:
        """Extract enhanced information using Claude with updated prompt."""
        try:
            response = self.anthropic_client.messages.create(
                model="claude-opus-4-5",
                max_tokens=6000,
                temperature=0,
                system=self.extraction_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"Extract comprehensive structured information from this research paper:\n\n{paper_text[:500000]}"
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
            return data

        except Exception as e:
            print(f"  ❌ Extraction failed: {e}")
            return None

    def validate_and_clean(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extracted data against controlled vocabularies."""
        finding = data.get('empirical_finding', {})

        # Validate direction
        direction = finding.get('direction', 'not_reported')
        if direction not in FINDING_DIRECTIONS:
            direction = 'not_reported'
        finding['direction'] = direction

        # Validate effect_size (must be 0-1 or "not_reported")
        effect_size = finding.get('effect_size', 'not_reported')
        if effect_size != 'not_reported':
            try:
                effect_size = float(effect_size)
                if effect_size < 0 or effect_size > 1:
                    print(f"  ⚠️  Effect size {effect_size} out of range (0-1), setting to not_reported")
                    effect_size = 'not_reported'
            except (ValueError, TypeError):
                effect_size = 'not_reported'
        finding['effect_size'] = effect_size

        # Validate controlled vocabularies
        finding['region'] = finding.get('region', 'not_reported') if finding.get('region') in REGIONS else 'not_reported'
        finding['school_type'] = finding.get('school_type', 'not_reported') if finding.get('school_type') in SCHOOL_TYPES else 'not_reported'
        finding['public_private_status'] = finding.get('public_private_status', 'not_reported') if finding.get('public_private_status') in PUBLIC_PRIVATE_STATUS else 'not_reported'
        finding['title_i_status'] = finding.get('title_i_status', 'not_reported') if finding.get('title_i_status') in TITLE_I_STATUS else 'not_reported'
        finding['ses_indicator'] = finding.get('ses_indicator', 'not_reported') if finding.get('ses_indicator') in SES_INDICATOR else 'not_reported'
        finding['special_education_services'] = finding.get('special_education_services', 'not_reported') if finding.get('special_education_services') in SPECIAL_ED_SERVICES else 'not_reported'
        finding['urban_type'] = finding.get('urban_type', 'not_reported') if finding.get('urban_type') in URBAN_TYPE else 'not_reported'
        finding['governance_type'] = finding.get('governance_type', 'not_reported') if finding.get('governance_type') in GOVERNANCE_TYPE else 'not_reported'
        finding['institutional_level'] = finding.get('institutional_level', 'not_reported') if finding.get('institutional_level') in INSTITUTIONAL_LEVEL else 'not_reported'
        finding['postsecondary_type'] = finding.get('postsecondary_type', 'not_reported') if finding.get('postsecondary_type') in POSTSECONDARY_TYPE else 'not_reported'

        # Validate 0-4 scales
        for field in ['system_impact_levels', 'decision_making_complexity', 'evidence_type_strength', 'evaluation_burden_cost']:
            value = finding.get(field, -1)
            try:
                value = int(value)
                if value < 0 or value > 4:
                    value = -1  # Use -1 to indicate not_reported for numeric fields
            except (ValueError, TypeError):
                value = -1
            finding[field] = value

        # Ensure free-text fields have defaults
        for field in ['student_racial_makeup', 'student_socioeconomic_makeup', 'student_gender_makeup',
                      'student_age_distribution', 'ses_numeric', 'results_summary', 'measure']:
            if field not in finding or not finding[field]:
                finding[field] = 'not_reported'

        # Ensure study_size has default
        if 'study_size' not in finding or finding['study_size'] is None:
            finding['study_size'] = 'not_reported'

        data['empirical_finding'] = finding
        return data

    def update_neo4j(self, finding_id: str, finding_data: Dict[str, Any]) -> bool:
        """Update EmpiricalFinding node in Neo4j with enhanced data."""
        try:
            with self.conn.driver.session(database=self.conn.database) as session:
                # Update all properties
                session.run("""
                    MATCH (f:EmpiricalFinding {finding_id: $finding_id})
                    SET f.direction = $direction,
                        f.results_summary = $results_summary,
                        f.measure = $measure,
                        f.study_size = $study_size,
                        f.effect_size = $effect_size,

                        f.student_racial_makeup = $student_racial_makeup,
                        f.student_socioeconomic_makeup = $student_socioeconomic_makeup,
                        f.student_gender_makeup = $student_gender_makeup,
                        f.student_age_distribution = $student_age_distribution,

                        f.school_type = $school_type,
                        f.public_private_status = $public_private_status,
                        f.title_i_status = $title_i_status,
                        f.ses_indicator = $ses_indicator,
                        f.ses_numeric = $ses_numeric,
                        f.special_education_services = $special_education_services,
                        f.urban_type = $urban_type,
                        f.governance_type = $governance_type,

                        f.institutional_level = $institutional_level,
                        f.postsecondary_type = $postsecondary_type,

                        f.region = $region,

                        f.system_impact_levels = $system_impact_levels,
                        f.decision_making_complexity = $decision_making_complexity,
                        f.evidence_type_strength = $evidence_type_strength,
                        f.evaluation_burden_cost = $evaluation_burden_cost,

                        f.enriched_at = $enriched_at
                """,
                    finding_id=finding_id,
                    direction=finding_data.get('direction', 'not_reported'),
                    results_summary=finding_data.get('results_summary', 'not_reported'),
                    measure=finding_data.get('measure', 'not_reported'),
                    study_size=finding_data.get('study_size', 'not_reported'),
                    effect_size=finding_data.get('effect_size', 'not_reported'),

                    student_racial_makeup=finding_data.get('student_racial_makeup', 'not_reported'),
                    student_socioeconomic_makeup=finding_data.get('student_socioeconomic_makeup', 'not_reported'),
                    student_gender_makeup=finding_data.get('student_gender_makeup', 'not_reported'),
                    student_age_distribution=finding_data.get('student_age_distribution', 'not_reported'),

                    school_type=finding_data.get('school_type', 'not_reported'),
                    public_private_status=finding_data.get('public_private_status', 'not_reported'),
                    title_i_status=finding_data.get('title_i_status', 'not_reported'),
                    ses_indicator=finding_data.get('ses_indicator', 'not_reported'),
                    ses_numeric=finding_data.get('ses_numeric', 'not_reported'),
                    special_education_services=finding_data.get('special_education_services', 'not_reported'),
                    urban_type=finding_data.get('urban_type', 'not_reported'),
                    governance_type=finding_data.get('governance_type', 'not_reported'),

                    institutional_level=finding_data.get('institutional_level', 'not_reported'),
                    postsecondary_type=finding_data.get('postsecondary_type', 'not_reported'),

                    region=finding_data.get('region', 'not_reported'),

                    system_impact_levels=finding_data.get('system_impact_levels', -1),
                    decision_making_complexity=finding_data.get('decision_making_complexity', -1),
                    evidence_type_strength=finding_data.get('evidence_type_strength', -1),
                    evaluation_burden_cost=finding_data.get('evaluation_burden_cost', -1),

                    enriched_at=datetime.now().isoformat()
                )

                return True

        except Exception as e:
            print(f"  ❌ Failed to update Neo4j: {e}")
            return False

    def enrich_all_papers(self, start_index: int = 0, limit: Optional[int] = None, log_file: str = "enrichment_log.json"):
        """Main enrichment loop with real-time JSON logging."""
        papers = self.get_all_papers()
        total = len(papers)

        print(f"🔄 Found {total} papers to enrich\n")
        print(f"📝 Logging to: {log_file}\n")

        # Initialize or load existing log
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                log_data = json.load(f)
            print(f"📂 Loaded existing log with {len(log_data.get('papers', []))} entries\n")
        else:
            log_data = {
                "started_at": datetime.now().isoformat(),
                "total_papers": total,
                "papers": []
            }

        if limit:
            papers = papers[start_index:start_index + limit]
            print(f"📊 Processing papers {start_index} to {start_index + len(papers)}\n")

        success_count = 0
        skip_count = 0
        fail_count = 0

        for i, paper in enumerate(papers, start=start_index + 1):
            print(f"\n{'='*80}")
            print(f"[{i}/{total}] Processing: {paper['title'][:70]}...")
            print(f"URL: {paper['url']}")

            # Initialize log entry
            log_entry = {
                "index": i,
                "paper_id": paper['paper_id'],
                "finding_id": paper['finding_id'],
                "title": paper['title'],
                "url": paper['url'],
                "processed_at": datetime.now().isoformat(),
                "status": None,
                "extracted_fields": {},
                "error": None
            }

            # Fetch paper text
            print("  📄 Fetching full text...")
            paper_text = self.fetch_paper_text(paper['url'], paper['title'])

            if not paper_text or len(paper_text.strip()) < 500:
                print(f"  ⚠️  Skipping - insufficient content")
                skip_count += 1
                log_entry["status"] = "skipped"
                log_entry["error"] = "insufficient content"
                log_data["papers"].append(log_entry)
                # Write to disk immediately
                with open(log_file, 'w') as f:
                    json.dump(log_data, f, indent=2)
                continue

            print(f"  ✅ Fetched {len(paper_text)} characters")

            # Extract enhanced data
            print("  🤖 Extracting enhanced data with Claude...")
            extracted_data = self.extract_enhanced_data(paper_text, paper['title'])

            if not extracted_data:
                print(f"  ❌ Extraction failed")
                fail_count += 1
                log_entry["status"] = "failed"
                log_entry["error"] = "extraction failed"
                log_data["papers"].append(log_entry)
                # Write to disk immediately
                with open(log_file, 'w') as f:
                    json.dump(log_data, f, indent=2)
                continue

            # Validate and clean
            print("  ✓ Validating data...")
            validated_data = self.validate_and_clean(extracted_data)
            finding_data = validated_data['empirical_finding']

            # Show summary of new fields
            print(f"  📊 Extracted new fields:")
            print(f"     Region: {finding_data.get('region', 'not_reported')}")
            print(f"     School Type: {finding_data.get('school_type', 'not_reported')}")
            print(f"     Urban Type: {finding_data.get('urban_type', 'not_reported')}")
            print(f"     System Impact: {finding_data.get('system_impact_levels', -1)}")
            print(f"     Decision Complexity: {finding_data.get('decision_making_complexity', -1)}")
            print(f"     Evidence Strength: {finding_data.get('evidence_type_strength', -1)}")
            print(f"     Evaluation Burden: {finding_data.get('evaluation_burden_cost', -1)}")
            print(f"     Effect Size: {finding_data.get('effect_size', 'not_reported')}")
            print(f"     Summary Length: {len(finding_data.get('results_summary', ''))} chars")

            # Update Neo4j
            print("  💾 Updating Neo4j...")
            if self.update_neo4j(paper['finding_id'], finding_data):
                print(f"  ✅ Successfully enriched!")
                success_count += 1
                log_entry["status"] = "success"
                log_entry["extracted_fields"] = finding_data
            else:
                print(f"  ❌ Failed to update Neo4j")
                fail_count += 1
                log_entry["status"] = "failed"
                log_entry["error"] = "neo4j update failed"

            # Write to log immediately after each paper
            log_data["papers"].append(log_entry)
            with open(log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
            print(f"  📝 Logged to {log_file}")

        # Final log update with completion info
        log_data["completed_at"] = datetime.now().isoformat()
        log_data["summary"] = {
            "success": success_count,
            "skipped": skip_count,
            "failed": fail_count,
            "total": total
        }
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)

        print(f"\n{'='*80}")
        print(f"🎉 ENRICHMENT COMPLETE!")
        print(f"   ✅ Success: {success_count}")
        print(f"   ⚠️  Skipped: {skip_count}")
        print(f"   ❌ Failed: {fail_count}")
        print(f"   📊 Total: {total}")
        print(f"   📝 Full log saved to: {log_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Enrich existing papers with enhanced EmpiricalFinding data')
    parser.add_argument('--start', type=int, default=0, help='Start index (for resuming)')
    parser.add_argument('--limit', type=int, default=None, help='Limit number of papers to process')
    parser.add_argument('--test', action='store_true', help='Test mode: process only first 3 papers')
    parser.add_argument('--log', type=str, default='enrichment_log.json', help='JSON log file path')

    args = parser.parse_args()

    if args.test:
        print("🧪 TEST MODE: Processing first 3 papers only\n")
        args.limit = 3
        args.log = 'enrichment_test_log.json'  # Use separate log for testing

    enricher = PaperEnricher()
    enricher.enrich_all_papers(start_index=args.start, limit=args.limit, log_file=args.log)
