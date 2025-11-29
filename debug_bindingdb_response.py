"""
Debug script to inspect the actual BindingDB API response structure.
"""

import requests
import json

def inspect_bindingdb_response():
    """Inspect what the API actually returns."""
    
    url = "https://bindingdb.org/rest/getTargetByCompound"
    
    # Test with a simple, well-known molecule (aspirin)
    test_cases = [
        ("Aspirin", "CC(=O)Oc1ccccc1C(=O)O"),
        ("Ethanol", "CCO"),
        ("Caffeine", "CN1C=NC2=C1C(=O)N(C(=O)N2C)C")
    ]
    
    for name, smiles in test_cases:
        print("=" * 60)
        print(f"Testing: {name} ({smiles})")
        print("=" * 60)
        
        params = {
            "smiles": smiles,
            "cutoff": 0.85,
            "response": "application/json"
        }
        
        try:
            resp = requests.get(url, params=params, timeout=30)
            print(f"Status Code: {resp.status_code}")
            print(f"Response Length: {len(resp.text)} characters")
            print(f"Content-Type: {resp.headers.get('Content-Type', 'N/A')}")
            print()
            
            if resp.status_code == 200:
                if resp.text.strip():
                    try:
                        data = resp.json()
                        print(f"Response Type: {type(data)}")
                        
                        if isinstance(data, dict):
                            print(f"Keys: {list(data.keys())}")
                            print()
                            print("Full Response (formatted):")
                            print(json.dumps(data, indent=2)[:2000])  # First 2000 chars
                        elif isinstance(data, list):
                            print(f"List Length: {len(data)}")
                            if data:
                                print("First Item:")
                                print(json.dumps(data[0], indent=2)[:1000])
                        else:
                            print(f"Unexpected type: {type(data)}")
                            print(str(data)[:500])
                    except json.JSONDecodeError as e:
                        print(f"JSON Decode Error: {e}")
                        print(f"Raw Response (first 500 chars):")
                        print(resp.text[:500])
                else:
                    print("Empty response (no matching compounds)")
            else:
                print(f"Error Response:")
                print(resp.text[:500])
                
        except Exception as e:
            print(f"Exception: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n")

if __name__ == "__main__":
    inspect_bindingdb_response()
