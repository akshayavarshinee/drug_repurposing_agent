"""
Debug script to check parent molecule ID for Metformin and see if mechanisms are linked there.
"""

import requests
import json

BASE_URL = "https://www.ebi.ac.uk/chembl/api/data"
CHEMBL_ID = "CHEMBL1431"  # Metformin

def check_parent_and_mechanisms():
    print(f"Checking parent molecule for {CHEMBL_ID}...")
    
    # Get molecule details to find parent
    url = f"{BASE_URL}/molecule/{CHEMBL_ID}.json"
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        mol_data = resp.json()
        
        parent_id = mol_data.get("molecule_hierarchy", {}).get("parent_chembl_id")
        print(f"Parent ChEMBL ID: {parent_id}")
        
        if parent_id and parent_id != CHEMBL_ID:
            print(f"Checking mechanisms for parent {parent_id}...")
            mech_url = f"{BASE_URL}/mechanism.json"
            params = {"molecule_chembl_id": parent_id}
            
            resp = requests.get(mech_url, params=params, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            mechanisms = data.get("mechanisms", [])
            print(f"Found {len(mechanisms)} mechanisms for parent")
            if mechanisms:
                print(json.dumps(mechanisms[0], indent=2))
        else:
            print("Molecule is its own parent or no parent info found.")
            
            # Try searching mechanism by action_type or other fields just to see if ANY mechanism exists for Metformin
            # Maybe it's under a different ID?
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_parent_and_mechanisms()
