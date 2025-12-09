import subprocess
import time
import requests
import sys
import os

def start_service(command, port, name, env=None):
    print(f"Starting {name} on port {port}...")
    
    # Merge current env with passed env
    process_env = os.environ.copy()
    if env:
        process_env.update(env)

    # Use python -m uvicorn to ensure path is correct
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", command, "--port", str(port), "--host", "127.0.0.1"],
        cwd=os.getcwd(),
        env=process_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return proc

def verify():
    procs = []
    try:
        # 1. Start Gateway FIRST 
        procs.append(start_service("src.services.gateway.main:app", 8000, "Gateway", {"SERVICE_PORT": "8000"}))
        print("Waiting 5s for Gateway to initialize...")
        time.sleep(5)

        # 2. Start Services
        procs.append(start_service("src.services.qbank.main:app", 8002, "Science QBank", {"SERVICE_PORT": "8002"}))
        procs.append(start_service("src.services.qbank.main:app", 8003, "General QBank", {"SERVICE_PORT": "8003"}))
        
        # Scale Generation Service
        procs.append(start_service("src.services.generator.main:app", 8004, "Generation Service - 1", {"SERVICE_PORT": "8004"}))
        procs.append(start_service("src.services.generator.main:app", 8005, "Generation Service - 2", {"SERVICE_PORT": "8005"}))
        procs.append(start_service("src.services.generator.main:app", 8006, "Generation Service - 3", {"SERVICE_PORT": "8006"}))
        
        print("Waiting for services to start...")
        time.sleep(10) # Wait a bit longer for all 4 to come up
        
        # Test Health
        try:
            r = requests.get("http://127.0.0.1:8000/health", timeout=5)
            print(f"Gateway Health: {r.status_code} {r.json()}")
        except Exception as e:
            print(f"Gateway Health Check Failed: {e}")

        # Verify Load Balancing (Generation Service)
        print("\nVerifying Generation Service Load Balancing...")
        try:
            # We can't easily trigger generation without a valid payload, 
            # BUT we can hit the actual service instances directly to prove they are up
            for port in [8004, 8005, 8006]:
                try:
                    r = requests.get(f"http://127.0.0.1:{port}/health", timeout=2)
                    print(f"Instance {port} Health: {r.status_code} {r.json()}")
                except Exception as e:
                    print(f"Instance {port} Unreachable: {e}")
        except Exception as e:
            print(f"Load Balancing Verification Error: {e}")

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
