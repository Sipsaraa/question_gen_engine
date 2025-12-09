import subprocess
import sys
import os
import signal
import time

def start_service(command, port, name, env=None):
    print(f"Starting {name} on port {port}...")
    
    # Merge current env with passed env
    process_env = os.environ.copy()
    if env:
        process_env.update(env)
        
    # Use python -m uvicorn to ensure path is correct and use reloading for dev
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", command, "--port", str(port), "--host", "127.0.0.1", "--reload"],
        cwd=os.getcwd(),
        env=process_env,
        # We want to see output in the console
        stdout=None, 
        stderr=None
    )
    return proc

def main():
    procs = []
    try:
        # 1. Start Gateway FIRST causing it to be the registry
        # We need it up so services can register
        procs.append(start_service("src.services.gateway.main:app", 8000, "Gateway", {"SERVICE_PORT": "8000"}))
        print("Waiting 5s for Gateway to initialize...")
        time.sleep(5) 
        
        # 2. Start Services (They will auto-register)
        # Dynamic Subject Services
        SUBJECTS = ["general", "science", "maths", "history"]
        BASE_UBANK_PORT = 8010
        
        for i, subject in enumerate(SUBJECTS):
            port = BASE_UBANK_PORT + i
            service_name = f"{subject}_qbank"
            procs.append(start_service(
                "src.services.qbank.main:app", 
                port, 
                f"{subject.title()} QBank", 
                {"SERVICE_PORT": str(port), "SERVICE_NAME": service_name}
            ))
        
        procs.append(start_service("src.services.generator.main:app", 8004, "Generation Service - 1", {"SERVICE_PORT": "8004"}))

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
