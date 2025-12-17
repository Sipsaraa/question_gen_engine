import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from src.services.generator.service import GeneratorService

def test_config():
    print("Loading environment...")
    load_dotenv()
    
    print(f"GOOGLE_API_KEY present: {bool(os.getenv('GOOGLE_API_KEY'))}")
    print(f"GROQ_API_KEY present: {bool(os.getenv('GROQ_API_KEY'))}")
    
    print("\nInitializing GeneratorService...")
    service = GeneratorService()
    
    print(f"\nLoaded Providers ({len(service.providers)}):")
    for p in service.providers:
        print(f"- {p.provider_name}")
        
    if len(service.providers) < 2:
        print("\nWARNING: Less than 2 providers loaded. Fallback might not work if keys are missing from .env")
    else:
        print("\nSUCCESS: Both providers loaded correctly.")
        
if __name__ == "__main__":
    test_config()
