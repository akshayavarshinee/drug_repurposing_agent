"""
Debug script to see what ChEMBL API actually returns for Metformin.
"""

import requests
import json

BASE_URL = "https://www.ebi.ac.uk/chembl/api/data"

def debug_chembl_search(drug_name):
    print(f"Searching ChEMBL for: {drug_name}")
    print("=" * 60)
    
    search_url = f"{BASE_URL}/molecule?format=json"
    params = {"q": drug_name, "limit": 10}
    
    try:
        resp = requests.get(search_url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        
        molecules = data.get("molecules", [])
        print(f"Found {len(molecules)} results\n")
        
        for i, mol in enumerate(molecules, 1):
            print(f"Result {i}:")
            print(f"  ChEMBL ID: {mol.get('molecule_chembl_id')}")
            print(f"  Pref Name: {mol.get('pref_name')}")
            print(f"  Synonyms: {mol.get('molecule_synonyms', [])[:3]}")  # First 3
            print(f"  Type: {mol.get('molecule_type')}")
            print(f"  Max Phase: {mol.get('max_phase')}")
            
            # Check if it has SMILES
            structures = mol.get('molecule_structures', {})
            if structures:
                smiles = structures.get('canonical_smiles', '')
                print(f"  SMILES: {smiles[:50]}...")
            print()
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_chembl_search("Metformin")
