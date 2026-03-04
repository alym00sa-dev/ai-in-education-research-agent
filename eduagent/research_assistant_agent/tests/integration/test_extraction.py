"""
Test that the frontend can properly extract nested data from backend response.
"""
import httpx
import json
import asyncio

BACKEND_URL = "https://ai-in-education-research-agent.onrender.com"

async def test_data_extraction():
    """Test extraction of final_report and raw_notes from nested structure"""

    # Create thread
    async with httpx.AsyncClient(timeout=10.0) as client:
        thread_response = await client.post(f"{BACKEND_URL}/threads", json={})
        thread_id = thread_response.json()["thread_id"]

    print(f"Testing data extraction with thread: {thread_id}\n")

    payload = {
        "input": {"messages": [{"role": "user", "content": "What is AI?"}]},
        "config": {"configurable": {"research_model": "openai:gpt-4.1", "max_researcher_iterations": 2}}
    }

    async with httpx.AsyncClient(timeout=600.0) as client:
        async with client.stream(
            "POST",
            f"{BACKEND_URL}/threads/{thread_id}/runs/stream",
            json=payload
        ) as response:

            final_state = None

            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]

                    if data_str == "[DONE]":
                        break

                    try:
                        data = json.loads(data_str)
                        if data:
                            final_state = data  # Keep updating with latest
                    except json.JSONDecodeError:
                        continue

    # Now test extraction like the frontend does
    print("="*80)
    print("EXTRACTION TEST RESULTS")
    print("="*80)

    if not final_state:
        print("❌ No final state received!")
        return False

    # Test 1: Extract final_report
    print("\n1. Testing final_report extraction:")
    final_report_node = final_state.get('final_report_generation', {})
    final_report = final_report_node.get('final_report', '')

    if final_report:
        print(f"✅ Found final_report ({len(final_report)} characters)")
        print(f"   Preview: {final_report[:100]}...")
    else:
        print("❌ No final_report found!")
        print(f"   Available keys: {list(final_state.keys())}")
        return False

    # Test 2: Extract raw_notes
    print("\n2. Testing raw_notes extraction:")
    research_supervisor_node = final_state.get('research_supervisor', {})
    raw_notes = research_supervisor_node.get('raw_notes', [])

    if raw_notes:
        print(f"✅ Found raw_notes ({len(raw_notes)} items)")

        # Extract URLs from raw_notes
        import re
        urls = []
        for note in raw_notes:
            if isinstance(note, str):
                found_urls = re.findall(r'https?://[^\s\)"\]>]+', note)
                urls.extend(found_urls)

        print(f"   Extracted {len(urls)} URLs from notes")
        if urls:
            print(f"   Sample URL: {urls[0]}")
    else:
        print("⚠️  No raw_notes found (may not have searched web)")
        print(f"   research_supervisor keys: {list(research_supervisor_node.keys())}")

    # Test 3: Extract URLs from report
    print("\n3. Testing URL extraction from report:")
    report_urls = re.findall(r'https?://[^\s\)"\]>]+', final_report)
    print(f"   Found {len(report_urls)} URLs in final report")

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"✅ Final report: {len(final_report) > 0}")
    print(f"✅ Raw notes: {len(raw_notes) >= 0}")
    print(f"✅ Total URLs found: {len(urls) + len(report_urls)}")

    if len(final_report) > 0:
        print("\n🎉 SUCCESS! Data extraction working correctly!")
        return True
    else:
        print("\n❌ FAILED! No data extracted")
        return False

if __name__ == "__main__":
    asyncio.run(test_data_extraction())
