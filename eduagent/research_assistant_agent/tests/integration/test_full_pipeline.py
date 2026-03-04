"""
Test the full research pipeline end-to-end.
Tests: Backend API → Research execution → Response streaming
"""
import httpx
import json
import asyncio
from datetime import datetime

# Configuration
BACKEND_URL = "https://ai-in-education-research-agent.onrender.com"
TEST_QUERY = "What is machine learning?"

async def test_health_check():
    """Test 1: Backend health check"""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BACKEND_URL}/ok")
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Response: {response.json()}")
            return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

async def test_create_thread():
    """Test 2: Create thread"""
    print("\n" + "="*60)
    print("TEST 2: Create Thread")
    print("="*60)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{BACKEND_URL}/threads", json={})
            response.raise_for_status()
            thread_data = response.json()
            thread_id = thread_data["thread_id"]
            print(f"✅ Thread created: {thread_id}")
            return thread_id
    except Exception as e:
        print(f"❌ Thread creation failed: {e}")
        return None

async def test_research_stream(thread_id: str):
    """Test 3: Stream research results"""
    print("\n" + "="*60)
    print("TEST 3: Stream Research")
    print("="*60)
    print(f"Query: '{TEST_QUERY}'")
    print(f"Thread ID: {thread_id}")
    print("-"*60)

    payload = {
        "input": {
            "messages": [{"role": "user", "content": TEST_QUERY}]
        },
        "config": {
            "configurable": {
                "research_model": "openai:gpt-4.1",
                "max_researcher_iterations": 3
            }
        }
    }

    try:
        async with httpx.AsyncClient(timeout=600.0) as client:
            print(f"\n📡 Sending request to: {BACKEND_URL}/threads/{thread_id}/runs/stream")
            print(f"📦 Payload: {json.dumps(payload, indent=2)}")

            async with client.stream(
                "POST",
                f"{BACKEND_URL}/threads/{thread_id}/runs/stream",
                json=payload
            ) as response:
                print(f"\n✅ Response status: {response.status_code}")

                if response.status_code != 200:
                    error_text = await response.aread()
                    print(f"❌ Error response: {error_text.decode()}")
                    return False

                print("\n📨 Streaming events:")
                print("-"*60)

                event_count = 0
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        event_count += 1
                        data = line[6:]  # Remove "data: " prefix

                        if data == "[DONE]":
                            print(f"\n✅ Stream completed!")
                            print(f"📊 Total events received: {event_count}")
                            return True

                        try:
                            event = json.loads(data)

                            if event_count <= 5:  # Show first 5 events in detail
                                print(f"\nEvent {event_count}:")
                                # Show the keys of the event
                                if isinstance(event, dict):
                                    data_keys = list(event.keys())
                                    print(f"  Keys: {data_keys}")

                                    # Show specific important fields
                                    if "error" in event:
                                        print(f"  ❌ ERROR: {event['error']}")
                                    if "final_report" in event:
                                        print(f"  ✅ Has final_report")
                                    if "messages" in event:
                                        print(f"  📨 Has {len(event.get('messages', []))} messages")
                                    if "raw_notes" in event:
                                        print(f"  📝 Has {len(event.get('raw_notes', []))} raw notes")
                                else:
                                    print(f"  Data type: {type(event)}")

                            elif event_count % 10 == 0:  # Show progress every 10 events
                                print(f"  ... {event_count} events received ...")

                        except json.JSONDecodeError as e:
                            print(f"  ❌ JSON Error: {e}")
                            print(f"  [Data: {data[:200]}...]")

                print(f"\n✅ Stream ended")
                print(f"📊 Total events received: {event_count}")
                return event_count > 0

    except httpx.TimeoutException:
        print(f"❌ Request timed out after 600 seconds")
        return False
    except Exception as e:
        print(f"❌ Research stream failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 FULL PIPELINE TEST")
    print("="*60)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Query: {TEST_QUERY}")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Test 1: Health check
    if not await test_health_check():
        print("\n❌ Health check failed. Backend may be down.")
        return

    # Test 2: Create thread
    thread_id = await test_create_thread()
    if not thread_id:
        print("\n❌ Thread creation failed. Cannot continue.")
        return

    # Test 3: Stream research
    success = await test_research_stream(thread_id)

    # Summary
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)
    if success:
        print("✅ All tests passed!")
        print("✅ Backend is working correctly")
        print("✅ Research pipeline is functional")
    else:
        print("❌ Research streaming failed")
        print("⚠️  Check backend logs for errors")

    print(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
