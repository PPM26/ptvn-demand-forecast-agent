import requests
import time
import subprocess
import sys

# Since we can't easily start a server and keep it running in the same process, 
# for this script we assume the server is running on localhost:8000.
# However, to be self-contained for the agent, we might want to try to start it or just rely on manual start.
# For now, I will just print the commands to run and then try to ping if it's there.

def test_endpoints():
    base_url = "http://localhost:8000"
    
    # 1. Test Normalize
    print("\n--- Testing Normalize ---")
    try:
        resp = requests.post(f"{base_url}/pipeline/normalize", json={"input_data": "item1, item2"})
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
    except Exception as e:
        print(f"Normalize Test Failed: {e}")

    # 2. Test Match (Mocked if needed, but here we expect real service or error)
    print("\n--- Testing Match ---")
    # Using a dummy item that might not be in RagFlow, just to see if it runs
    try:
        resp = requests.post(f"{base_url}/pipeline/match", params={"item_name": "test_item"})
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
    except Exception as e:
        print(f"Match Test Failed: {e}")
        
    # 3. Test Forecast (now returns formatted string)
    print("\n--- Testing Forecast ---")
    try:
        resp = requests.get(f"{base_url}/pipeline/forecast/test_item")
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}") # Expecting string now
    except Exception as e:
        print(f"Forecast Test Failed: {e}")

    # 5. Test Health
    print("\n--- Testing Health ---")
    try:
        resp = requests.get(f"{base_url}/health")
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
    except Exception as e:
        print(f"Health Test Failed: {e}")

    # 6. Test Full Pipeline
    print("\n--- Testing Full Pipeline ---")
    try:
        resp = requests.post(f"{base_url}/pipeline/run", json={"input_data": "test_item"})
        print(f"Status: {resp.status_code}")
        # Truncate response if too long
        print(f"Response Keys: {resp.json().keys() if resp.status_code == 200 else resp.text}")
    except Exception as e:
        print(f"Pipeline Test Failed: {e}")

if __name__ == "__main__":
    print("Ensure server is running with: uvicorn app.main:app --reload")
    # We can try to wait a bit if we started it in background, but simplest is just to run the tests.
    test_endpoints()
