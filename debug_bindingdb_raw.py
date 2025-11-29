"""
Debug script to inspect RAW BindingDB response for Metformin.
"""
import requests
import json

METFORMIN_SMILES = "CN(C)C(=N)NC(=N)N"

def debug_raw_response():
    url = "https://bindingdb.org/rest/getTargetByCompound"
    params = {
        "smiles": METFORMIN_SMILES,
        "cutoff": 0.85,
        "response": "application/json"
    }
    
    print(f"Querying BindingDB for Metformin...")
    try:
        resp = requests.get(url, params=params, timeout=30)
        print(f"Status Code: {resp.status_code}")
        
        if resp.status_code == 200:
            print("Response Text Preview (first 500 chars):")
            print(resp.text[:500])
            
            try:
                data = resp.json()
                print("\nParsed JSON Keys:")
                if isinstance(data, dict):
                    print(list(data.keys()))
                    if "getTargetByCompoundResponse" in data:
                        inner = data["getTargetByCompoundResponse"]
                        print("Inner Keys:", list(inner.keys()))
                        affinities = inner.get("bdb.affinities", [])
                        print(f"Affinities count: {len(affinities)}")
                else:
                    print(f"Response is a list of length {len(data)}")
            except json.JSONDecodeError:
                print("Could not parse JSON")
        else:
            print("Request failed")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_raw_response()
