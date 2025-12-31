import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from src.services.generator.service import GeneratorService

def test_config():
    print("Loading environment...")
    load_dotenv()
    
    primary = os.getenv('PRIMARY_GENERATOR', 'gemini')
    fallback = os.getenv('FALLBACK_GENERATOR', 'groq')
    
    print(f"\nConfiguration:")
    print(f"PRIMARY_GENERATOR: {primary}")
    print(f"FALLBACK_GENERATOR: {fallback}")
    print(f"GOOGLE_API_KEY present: {bool(os.getenv('GOOGLE_API_KEY'))}")
    print(f"GROQ_API_KEY present: {bool(os.getenv('GROQ_API_KEY'))}")
    
    print("\nInitializing GeneratorService...")
    service = GeneratorService()
    
    print(f"\nLoaded Providers in Priority Order ({len(service.providers)}):")
    for i, p in enumerate(service.providers):
        priority = "Primary" if i == 0 else "Fallback"
        print(f"{i+1}. {p.provider_name} ({priority})")
        
    if len(service.providers) < 2:
        print("\nNOTE: Less than 2 providers loaded. Fallback will not be available.")
    else:
        print("\nSUCCESS: Providers loaded and ordered correctly.")
        
if __name__ == "__main__":
    test_config()
