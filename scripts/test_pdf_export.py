import requests
import time

def main():
    # URL
    url = "http://127.0.0.1:8000/questions/export/pdf"
    
    # We might need to generate some questions first if DB is empty
    # But let's assume there are SOME questions.
    # We will try to fetch ID 1 to 10
    
    params = {
        "start_id": 1,
        "end_id": 100 # Optimistic range
    }
    
    print(f"Requesting PDF from {url} with params {params}...")
    try:
        response = requests.get(url, params=params, stream=True)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            filename = "test_export.pdf"
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"PDF saved to {filename}")
        else:
            print("Error Response:")
            print(response.text)
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    time.sleep(2) # Give services a moment
    main()
