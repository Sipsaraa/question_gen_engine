import httpx
import time
import sys

GATEWAY_URL = "http://127.0.0.1:8000"

def test_routing():
    print("Testing Dynamic Routing...")
    
    # 1. Check Registry
    try:
        resp = httpx.get(f"{GATEWAY_URL}/health")
        registry = resp.json().get("registry", {})
        print("\nCurrent Registry:")
        for name, nodes in registry.items():
            print(f"- {name}: {nodes}")
            
        expected_services = ["general_qbank", "science_qbank", "history_qbank", "maths_qbank"]
        for svc in expected_services:
            if svc not in registry or not registry[svc]:
                print(f"FAILED: {svc} not registered!")
                return
        print("SUCCESS: All expected services registered.")
            
    except Exception as e:
        print(f"FAILED: Gateway not reachable. {e}")
        return

    # 2. Test Routing
    # We can't easily check *where* it went without logs, 
    # but we can check if we get a valid response for a new subject.
    
    subjects = ["science", "history", "maths"]
    for sub in subjects:
        try:
            print(f"\nQuerying subject: {sub}...")
            # We expect an empty list (200 OK) since DB is empty, but no 503 error
            resp = httpx.get(f"{GATEWAY_URL}/questions", params={"subject": sub})
            if resp.status_code == 200:
                print(f"SUCCESS: {sub} query returned 200 OK.")
            else:
                print(f"FAILED: {sub} query returned {resp.status_code} - {resp.text}")
        except Exception as e:
             print(f"FAILED: {sub} query error. {e}")

if __name__ == "__main__":
    test_routing()
