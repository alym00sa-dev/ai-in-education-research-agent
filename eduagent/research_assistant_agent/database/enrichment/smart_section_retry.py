"""
Smart sectioning script for long dissertations/papers.
Extracts only key sections: Abstract, Methods, Participants, Results, Discussion
"""

import re
import json
from typing import Optional, Dict, List
from enrich_existing_papers import PaperEnricher


def extract_key_sections(full_text: str) -> str:
    """
    Extract key sections from a dissertation/paper using pattern matching.
    Returns concatenated key sections that are relevant for metadata extraction.
    """

    # Convert to lowercase for matching, but keep original for extraction
    text_lower = full_text.lower()

    # Section patterns (in order of priority)
    section_patterns = [
        # Abstract
        (r'\babstract\b', r'\b(introduction|chapter|background)\b', 'Abstract'),

        # Methods/Methodology
        (r'\b(methods?|methodology|research design|procedures?)\b',
         r'\b(results?|findings?|analysis|discussion)\b', 'Methods'),

        # Participants/Sample
        (r'\b(participants?|sample|subjects?|population)\b',
         r'\b(materials?|instruments?|measures?|procedures?|results?)\b', 'Participants'),

        # Results/Findings
        (r'\b(results?|findings?)\b',
         r'\b(discussion|conclusion|implications?|limitations?)\b', 'Results'),

        # Discussion (first part only)
        (r'\b(discussion)\b',
         r'\b(conclusion|implications?|recommendations?|references?)\b', 'Discussion'),
    ]

    extracted_sections = []
    total_chars = 0
    max_chars = 200000  # Conservative limit

    for start_pattern, end_pattern, section_name in section_patterns:
        # Find section start
        start_match = re.search(start_pattern, text_lower)
        if not start_match:
            continue

        start_pos = start_match.start()

        # Find section end (look for next major section)
        end_match = re.search(end_pattern, text_lower[start_pos + 100:])  # Skip 100 chars to avoid matching the same word

        if end_match:
            end_pos = start_pos + 100 + end_match.start()
        else:
            # If no end found, take reasonable chunk (10k chars)
            end_pos = min(start_pos + 10000, len(full_text))

        # Extract section
        section_text = full_text[start_pos:end_pos].strip()

        # Limit each section to 50k chars
        if len(section_text) > 50000:
            section_text = section_text[:50000]

        if len(section_text) > 500:  # Only include if substantial
            extracted_sections.append(f"\n\n=== {section_name.upper()} ===\n\n{section_text}")
            total_chars += len(section_text)

            # Stop if we have enough
            if total_chars >= max_chars:
                break

    if not extracted_sections:
        # Fallback: take first 150k chars if no sections found
        print("  ⚠️  No sections detected, using first 150k characters")
        return full_text[:150000]

    result = "\n\n".join(extracted_sections)
    print(f"  ✓ Extracted {len(extracted_sections)} sections ({len(result)} chars)")
    return result


def retry_with_smart_sectioning():
    """Retry failed long papers with smart sectioning."""

    # Load original enrichment log to find papers that failed due to token limit
    try:
        with open('enrichment_log.json', 'r') as f:
            log_data = json.load(f)
    except:
        print("❌ Could not load enrichment_log.json")
        return

    # Filter to papers that failed and are likely dissertations (>300k chars)
    token_limit_papers = []
    for entry in log_data.get('papers', []):
        if entry.get('status') == 'failed':
            error = entry.get('error', '')
            # Check if it's a token limit error or likely a long paper
            if 'prompt is too long' in str(error) or 'tokens >' in str(error) or 'extraction failed' in str(error):
                token_limit_papers.append(entry)

    print(f"🔄 Found {len(token_limit_papers)} papers that failed due to token limits\n")

    if not token_limit_papers:
        print("✅ No papers to retry with smart sectioning!")
        return

    for paper in token_limit_papers:
        print(f"  [{paper['index']}] {paper['title'][:60]}...")

    print(f"\n{'='*80}")
    proceed = input(f"\nProceed with smart sectioning retry? (yes/no): ")
    if proceed.lower() != 'yes':
        print("Cancelled.")
        return

    enricher = PaperEnricher()
    success_count = 0
    still_failed = 0

    for i, paper in enumerate(token_limit_papers, 1):
        print(f"\n{'='*80}")
        print(f"SMART RETRY [{i}/{len(token_limit_papers)}] Paper {paper['index']}: {paper['title'][:60]}...")
        print(f"URL: {paper['url']}")

        # Fetch full text
        print("  📄 Fetching full text...")
        paper_text = enricher.fetch_paper_text(paper['url'], paper['title'])

        if not paper_text or len(paper_text.strip()) < 500:
            print(f"  ⚠️  Could not fetch text")
            still_failed += 1
            continue

        print(f"  ✅ Fetched {len(paper_text)} characters")

        # Apply smart sectioning
        print("  🔪 Applying smart sectioning...")
        sectioned_text = extract_key_sections(paper_text)

        if len(sectioned_text) < 1000:
            print(f"  ⚠️  Sectioning produced too little text ({len(sectioned_text)} chars)")
            still_failed += 1
            continue

        print(f"  📏 Reduced to {len(sectioned_text)} characters")

        # Extract enhanced data
        print("  🤖 Extracting enhanced data with Claude...")
        try:
            # Use sectioned text instead of full text
            response = enricher.anthropic_client.messages.create(
                model="claude-opus-4-5",
                max_tokens=6000,
                temperature=0,
                system=enricher.extraction_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"Extract comprehensive structured information from these KEY SECTIONS of a research paper:\n\n{sectioned_text}"
                    }
                ]
            )

            content = response.content[0].text.strip()

            # Handle code fences
            if content.startswith("```"):
                content = content.strip("`")
                if content.startswith("json"):
                    content = content[4:].strip()

            extracted_data = json.loads(content)

            # Validate and clean
            print("  ✓ Validating data...")
            validated_data = enricher.validate_and_clean(extracted_data)
            finding_data = validated_data['empirical_finding']

            # Show summary
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
            if enricher.update_neo4j(paper['finding_id'], finding_data):
                print(f"  ✅ Successfully enriched with smart sectioning!")
                success_count += 1

                # Log success
                with open('smart_section_log.json', 'a') as f:
                    log_entry = {
                        "index": paper['index'],
                        "title": paper['title'],
                        "status": "success",
                        "method": "smart_sectioning",
                        "original_chars": len(paper_text),
                        "sectioned_chars": len(sectioned_text),
                        "extracted_fields": finding_data
                    }
                    json.dump(log_entry, f, indent=2)
                    f.write(',\n')
            else:
                print(f"  ❌ Neo4j update failed")
                still_failed += 1

        except Exception as e:
            print(f"  ❌ Exception: {str(e)[:200]}")
            still_failed += 1
            continue

    print(f"\n{'='*80}")
    print(f"🎉 SMART SECTIONING COMPLETE!")
    print(f"   ✅ Newly successful: {success_count}")
    print(f"   ❌ Still failed: {still_failed}")
    print(f"   📊 Total attempted: {len(token_limit_papers)}")
    print(f"   📝 Success log saved to: smart_section_log.json")

    if success_count > 0:
        print(f"\n🎊 Recovered {success_count} long papers using smart sectioning!")


if __name__ == "__main__":
    retry_with_smart_sectioning()
