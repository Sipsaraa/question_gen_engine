import subprocess
import sys
import os
import signal
import time

def start_service(command, port, name):
    print(f"Starting {name} on port {port}...")
    # Use python -m uvicorn to ensure path is correct and use reloading for dev
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", command, "--port", str(port), "--host", "127.0.0.1", "--reload"],
        cwd=os.getcwd(),
        # We want to see output in the console
        stdout=None, 
        stderr=None
    )
    return proc

def main():
    procs = []
    try:
        # Start Services
        procs.append(start_service("src.services.qbank.main:app", 8002, "Science QBank"))
        procs.append(start_service("src.services.qbank.main:app", 8003, "General QBank"))
        procs.append(start_service("src.services.generator.main:app", 8004, "Generation Service"))
        procs.append(start_service("src.services.gateway.main:app", 8000, "Gateway"))
        
        print("\nAll Services Started!")
        print("Gateway: http://127.0.0.1:8000")
        print("Press Ctrl+C to stop all services.\n")
        
        # Keep alive
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping services...")
    finally:
        for p in procs:
            p.terminate()
            
if __name__ == "__main__":
    main()
