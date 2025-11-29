"""
Debug to find where Metformin actually is in ChEMBL.
"""

import requests
import json

BASE_URL = "https://www.ebi.ac.uk/chembl/api/data"

def search_for_metformin():
    print("Searching for Metformin in ChEMBL...")
    print("=" * 60)
    
    # Try drug endpoint
    search_url = f"{BASE_URL}/drug.json"
    params = {"q": "Metformin", "limit": 50}
    
    try:
        resp = requests.get(search_url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        
        drugs = data.get("drugs", [])
        print(f"Found {len(drugs)} drugs\n")
        
        # Look for Metformin in synonyms
        for i, drug in enumerate(drugs, 1):
            chembl_id = drug.get("molecule_chembl_id")
            synonyms = drug.get("molecule_synonyms", [])
            
            # Check if any synonym contains "metformin"
            metformin_syns = [s for s in synonyms if "metformin" in s.get("molecule_synonym", "").lower()]
            
            if metformin_syns:
                print(f"Found in {chembl_id}:")
                print(f"  Pref Name: {drug.get('pref_name')}")
                print(f"  Max Phase: {drug.get('max_phase')}")
                print(f"  Metformin synonyms:")
                for syn in metformin_syns:
                    print(f"    - {syn.get('molecule_synonym')} ({syn.get('syn_type')})")
                print()
                
                if i <= 5:  # Show SMILES for first 5
                    smiles = drug.get('molecule_structures', {}).get('canonical_smiles', '')
                    print(f"  SMILES: {smiles[:60]}...")
                    print()
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    search_for_metformin()
