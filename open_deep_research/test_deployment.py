"""
Test script to verify LangGraph backend deployment.
Run this after deploying to Railway to test the API.
"""
import httpx
import json

# Replace with your Railway URL after deployment
BACKEND_URL = "https://your-app.railway.app"

def test_health_check():
    """Test the health check endpoint."""
    print("Testing health check endpoint...")
    try:
        response = httpx.get(f"{BACKEND_URL}/ok", timeout=10.0)
        print(f"✅ Health check passed: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_research_api():
    """Test the research API endpoint."""
    print("\nTesting research API...")
    try:
        payload = {
            "assistant_id": "Deep Researcher",
            "input": {
                "messages": [{"role": "user", "content": "What is machine learning?"}]
            },
            "config": {
                "configurable": {
                    "research_model": "openai:gpt-4.1",
                    "max_researcher_iterations": 3
                }
            }
        }

        response = httpx.post(
            f"{BACKEND_URL}/runs/stream",
            json=payload,
            timeout=60.0
        )

        if response.status_code == 200:
            print("✅ Research API is responding")
            return True
        else:
            print(f"⚠️  Research API returned status: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Research API test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("LangGraph Backend Deployment Test")
    print("=" * 50)

    # Update the URL first
    if "your-app" in BACKEND_URL:
        print("\n⚠️  Please update BACKEND_URL with your Railway deployment URL first!")
        print("Find it in Railway dashboard after deployment.")
        exit(1)

    # Run tests
    health_ok = test_health_check()

    if health_ok:
        test_research_api()
    else:
        print("\n❌ Health check failed - backend may not be running")

    print("\n" + "=" * 50)
