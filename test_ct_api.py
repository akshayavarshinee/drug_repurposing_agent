import requests
import json

def test_clinical_trials_tool():
    url = "https://clinicaltrials.gov/api/v2/studies"
    
    # Test case 1: Simple condition search (should work)
    print("Test 1: Simple condition search")
    params = {
        "format": "json",
        "query.cond": "Diabetes",
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

    # Test case 2: Status filter using current implementation logic (filter.advanced)
    print("Test 2: Status filter via filter.advanced (Current Implementation)")
    params = {
        "format": "json",
        "query.cond": "Diabetes",
        "filter.advanced": "overallStatus:RECRUITING",
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

    # Test case 3: Status filter using correct parameter (filter.overallStatus)
    print("Test 3: Status filter via filter.overallStatus (Corrected)")
    params = {
        "format": "json",
        "query.cond": "Diabetes",
        "filter.overallStatus": ["RECRUITING"],
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
    test_clinical_trials_tool()
