"""
Retry script for failed and skipped papers with better error handling.
"""

import json
from enrich_existing_papers import PaperEnricher


def get_failed_and_skipped_papers(log_file: str = "enrichment_log.json"):
    """Get list of papers that failed or were skipped."""
    with open(log_file, 'r') as f:
        log_data = json.load(f)

    retry_papers = []
    for entry in log_data['papers']:
        if entry['status'] in ['failed', 'skipped']:
            retry_papers.append({
                'index': entry['index'],
                'title': entry['title'],
                'url': entry['url'],
                'paper_id': entry['paper_id'],
                'finding_id': entry['finding_id'],
                'previous_status': entry['status'],
                'previous_error': entry.get('error', 'unknown')
            })

    return retry_papers


def main():
    """Retry failed and skipped papers."""
    print("🔄 Loading failed/skipped papers from enrichment_log.json\n")

    retry_papers = get_failed_and_skipped_papers()

    if not retry_papers:
        print("✅ No failed or skipped papers to retry!")
        return

    print(f"📊 Found {len(retry_papers)} papers to retry:\n")
    for paper in retry_papers:
        print(f"  [{paper['index']}] {paper['title'][:70]}...")
        print(f"      Previous: {paper['previous_status']} - {paper['previous_error']}")

    print(f"\n{'='*80}")
    proceed = input(f"\nProceed with retry? (yes/no): ")
    if proceed.lower() != 'yes':
        print("Cancelled.")
        return

    enricher = PaperEnricher()

    success_count = 0
    still_failed = 0

    for i, paper in enumerate(retry_papers, 1):
        print(f"\n{'='*80}")
        print(f"RETRY [{i}/{len(retry_papers)}] Paper {paper['index']}: {paper['title'][:70]}...")
        print(f"URL: {paper['url']}")
        print(f"Previous error: {paper['previous_error']}")

        # Initialize log entry
        log_entry = {
            "index": paper['index'],
            "paper_id": paper['paper_id'],
            "finding_id": paper['finding_id'],
            "title": paper['title'],
            "url": paper['url'],
            "retry_attempt": True,
            "previous_status": paper['previous_status'],
            "previous_error": paper['previous_error'],
            "status": None,
            "extracted_fields": {},
            "error": None
        }

        # Fetch paper text
        print("  📄 Fetching full text...")
        paper_text = enricher.fetch_paper_text(paper['url'], paper['title'])

        if not paper_text or len(paper_text.strip()) < 500:
            print(f"  ⚠️  Still insufficient content ({len(paper_text) if paper_text else 0} chars)")
            still_failed += 1
            log_entry["status"] = "still_failed"
            log_entry["error"] = "insufficient content"

            # Log retry result
            with open('retry_log.json', 'a') as f:
                json.dump(log_entry, f, indent=2)
                f.write(',\n')
            continue

        print(f"  ✅ Fetched {len(paper_text)} characters")

        # ADJUSTED: Reduce to 500k chars to stay well under 200k tokens
        if len(paper_text) > 500000:
            print(f"  ⚠️  Text too long ({len(paper_text)} chars), truncating to 500k")
            paper_text = paper_text[:500000]

        # Extract enhanced data
        print("  🤖 Extracting enhanced data with Claude...")
        try:
            extracted_data = enricher.extract_enhanced_data(paper_text, paper['title'])

            if not extracted_data:
                print(f"  ❌ Extraction returned empty")
                still_failed += 1
                log_entry["status"] = "still_failed"
                log_entry["error"] = "extraction returned empty"

                with open('retry_log.json', 'a') as f:
                    json.dump(log_entry, f, indent=2)
                    f.write(',\n')
                continue

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
                print(f"  ✅ Successfully enriched on retry!")
                success_count += 1
                log_entry["status"] = "success"
                log_entry["extracted_fields"] = finding_data
            else:
                print(f"  ❌ Neo4j update failed")
                still_failed += 1
                log_entry["status"] = "still_failed"
                log_entry["error"] = "neo4j update failed"

            # Log retry result
            with open('retry_log.json', 'a') as f:
                json.dump(log_entry, f, indent=2)
                f.write(',\n')

        except Exception as e:
            print(f"  ❌ Exception during retry: {str(e)[:200]}")
            still_failed += 1
            log_entry["status"] = "still_failed"
            log_entry["error"] = str(e)[:500]

            with open('retry_log.json', 'a') as f:
                json.dump(log_entry, f, indent=2)
                f.write(',\n')
            continue

    print(f"\n{'='*80}")
    print(f"🎉 RETRY COMPLETE!")
    print(f"   ✅ Newly successful: {success_count}")
    print(f"   ❌ Still failed: {still_failed}")
    print(f"   📊 Total attempted: {len(retry_papers)}")
    print(f"   📝 Retry log saved to: retry_log.json")

    if success_count > 0:
        print(f"\n🎊 Recovered {success_count} papers that were previously failed/skipped!")


if __name__ == "__main__":
    main()
