import requests
import sys

BASE_URL = "http://localhost:8084/api/v2"

def check_resources():
    print("Listing resources...")
    try:
        r = requests.get(f"{BASE_URL}/resources")
        if r.status_code != 200:
            print(f"Error listing resources: {r.status_code} {r.text}")
            return None
        
        data = r.json()
        resources = data.get('resources', [])
        print(f"Found {len(resources)} resources.")
        if not resources:
            print("No resources found to test details.")
            return None
            
        first_id = resources[0]['id']
        print(f"Testing details for Resource ID: {first_id}")
        
        # Test GET Details
        r_det = requests.get(f"{BASE_URL}/resources/{first_id}")
        if r_det.status_code == 200:
            print("GET Details: SUCCESS (JSON received)")
            print(r_det.json().keys())
        else:
            print(f"GET Details FAILED: {r_det.status_code}")
            print(r_det.text[:500]) # First 500 chars
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    check_resources()
