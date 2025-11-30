import requests
import json

def test_phase_param():
    url = "https://clinicaltrials.gov/api/v2/studies"
    
    print("Testing Phase parameters...")
    
    # Test 1: Phase in filter.advanced (Current)
    print("Test 1: Phase in filter.advanced (phase:PHASE_2)")
    params = {
        "format": "json",
        "query.cond": "Diabetes",
        "filter.advanced": "phase:PHASE2",
        "pageSize": 5
    }
    try:
        resp = requests.get(url, params=params, timeout=30)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Found {len(data.get('studies', []))} studies")
        else:
            print(resp.text)
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 50)

    # Test 2: Phase in query.term
    print("Test 2: Phase in query.term (Phase 2)")
    params = {
        "format": "json",
        "query.cond": "Diabetes",
        "query.term": "Phase 2",
        "pageSize": 5
    }
    try:
        resp = requests.get(url, params=params, timeout=30)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Found {len(data.get('studies', []))} studies")
        else:
            print(resp.text)
    except Exception as e:
        print(f"Error: {e}")
        
    # Test 3: filter.phase (Guessing)
    print("Test 3: filter.phase")
    params = {
        "format": "json",
        "query.cond": "Diabetes",
        "filter.phase": ["PHASE2"],
        "pageSize": 5
    }
    try:
        resp = requests.get(url, params=params, timeout=30)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Found {len(data.get('studies', []))} studies")
        else:
            print(resp.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_phase_param()
