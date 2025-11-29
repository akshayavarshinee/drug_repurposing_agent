"""
Debug script to test ChEMBL mechanism, indication, and warning endpoints.
"""

import requests
import json

BASE_URL = "https://www.ebi.ac.uk/chembl/api/data"
CHEMBL_ID = "CHEMBL1431"  # Metformin

def debug_endpoint(name, endpoint, params):
    print(f"Testing {name}...")
    print(f"URL: {BASE_URL}/{endpoint}")
    print(f"Params: {params}")
    
    try:
        resp = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=20)
        print(f"Status: {resp.status_code}")
        resp.raise_for_status()
        data = resp.json()
        
        # Determine list key based on endpoint
        list_key = endpoint.replace(".json", "")
        if list_key == "drug_indication": list_key = "drug_indications"
        if list_key == "drug_warning": list_key = "drug_warnings"
        if list_key == "mechanism": list_key = "mechanisms"
        
        items = data.get(list_key, [])
        print(f"Found {len(items)} items")
        
        if items:
            print("First item sample:")
            print(json.dumps(items[0], indent=2))
        else:
            print("Response keys:", list(data.keys()))
            
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 60)

def main():
    print(f"Debugging details for {CHEMBL_ID} (Metformin)\n")
    
    # Test Mechanisms
    # Try standard param
    debug_endpoint("Mechanisms (standard)", "mechanism.json", {"molecule_chembl_id": CHEMBL_ID})
    # Try exact filter
    debug_endpoint("Mechanisms (exact)", "mechanism.json", {"molecule_chembl_id__exact": CHEMBL_ID})
    # Try parent molecule ID (sometimes mechanisms are linked to parent)
    # Metformin parent is CHEMBL1431 itself, but let's check if there's a salt issue.
    
    # Test Indications
    debug_endpoint("Indications", "drug_indication.json", {"molecule_chembl_id": CHEMBL_ID})
    
    # Test Warnings
    debug_endpoint("Warnings", "drug_warning.json", {"molecule_chembl_id": CHEMBL_ID})

if __name__ == "__main__":
    main()
