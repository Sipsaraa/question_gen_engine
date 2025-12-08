import subprocess
import time
import requests
import sys
import os

def start_service(command, port, name):
    print(f"Starting {name} on port {port}...")
    # Use python -m uvicorn to ensure path is correct
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", command, "--port", str(port), "--host", "127.0.0.1"],
        cwd=os.getcwd(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return proc

def verify():
    procs = []
    try:
        # Start Services
        procs.append(start_service("src.services.qbank.main:app", 8002, "Science QBank"))
        procs.append(start_service("src.services.qbank.main:app", 8003, "General QBank"))
        procs.append(start_service("src.services.generator.main:app", 8004, "Generation Service"))
        procs.append(start_service("src.services.gateway.main:app", 8000, "Gateway"))
        
        print("Waiting for services to start...")
        time.sleep(10) # Wait a bit longer for all 4 to come up
        
        # Test Health
        try:
            r = requests.get("http://127.0.0.1:8000/health", timeout=5)
            print(f"Gateway Health: {r.status_code} {r.json()}")
        except Exception as e:
            print(f"Gateway Health Check Failed: {e}")

        # Test Routing (Checking if they don't crash)
        try:
            r = requests.get("http://127.0.0.1:8000/questions?subject=Science", timeout=5)
            print(f"Science Query Status: {r.status_code}")
        except Exception as e:
            print(f"Science Query Failed: {e}")

    finally:
        print("Stopping services...")
        for p in procs:
            p.terminate()
            
if __name__ == "__main__":
    verify()
