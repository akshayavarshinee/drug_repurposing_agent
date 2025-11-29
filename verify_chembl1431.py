"""
Direct lookup of CHEMBL1431 and search alternatives.
"""

import requests
import json

BASE_URL = "https://www.ebi.ac.uk/chembl/api/data"

def lookup_chembl1431():
    """Direct lookup to confirm this is Metformin."""
    print("Looking up CHEMBL1431 directly...")
    print("=" * 60)
    
    url = f"{BASE_URL}/molecule/CHEMBL1431.json"
    
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        
        print(f"ChEMBL ID: {data.get('molecule_chembl_id')}")
        print(f"Pref Name: {data.get('pref_name')}")
        print(f"Max Phase: {data.get('max_phase')}")
        
        synonyms = data.get('molecule_synonyms', [])
        print(f"\nSynonyms ({len(synonyms)} total):")
        for syn in synonyms[:10]:  # First 10
            print(f"  - {syn.get('molecule_synonym')} ({syn.get('syn_type')})")
        
        smiles = data.get('molecule_structures', {}).get('canonical_smiles', '')
        print(f"\nSMILES: {smiles}")
        
    except Exception as e:
        print(f"Error: {e}")

def try_molecule_search():
    """Try the molecule endpoint instead of drug."""
    print("\n" + "=" * 60)
    print("Trying /molecule endpoint...")
    print("=" * 60)
    
    url = f"{BASE_URL}/molecule.json"
    params = {"q": "Metformin", "limit": 20}
    
    try:
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        
        molecules = data.get('molecules', [])
        print(f"Found {len(molecules)} molecules\n")
        
        for i, mol in enumerate(molecules, 1):
            chembl_id = mol.get('molecule_chembl_id')
            pref_name = mol.get('pref_name')
            
            # Check synonyms
            synonyms = mol.get('molecule_synonyms', [])
            metformin_syns = [s for s in synonyms if "metformin" in s.get('molecule_synonym', '').lower()]
            
            if metformin_syns or (pref_name and "metformin" in pref_name.lower()):
                print(f"{i}. {chembl_id}")
                print(f"   Pref Name: {pref_name}")
                print(f"   Max Phase: {mol.get('max_phase')}")
                if metformin_syns:
                    print(f"   Metformin synonyms:")
                    for syn in metformin_syns[:3]:
                        print(f"     - {syn.get('molecule_synonym')} ({syn.get('syn_type')})")
                print()
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    lookup_chembl1431()
    try_molecule_search()
