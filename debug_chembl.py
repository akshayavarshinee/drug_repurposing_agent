"""
Debug script to inspect ChEMBL API response.
"""
import requests
import json

def debug_chembl_search():
    url = "https://www.ebi.ac.uk/chembl/api/data/drug.json"
    params = {"q": "Metformin", "limit": 20}
    
    print(f"Fetching {url} with params {params}...")
    resp = requests.get(url, params=params)
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"Total Count: {data.get('page_meta', {}).get('total_count')}")
        drugs = data.get("drugs", [])
        print(f"Drugs found: {len(drugs)}")
        
        for i, drug in enumerate(drugs):
            print(f"\n--- Result {i+1} ---")
            print(f"Chembl ID: {drug.get('molecule_chembl_id')}")
            print(f"Pref Name: {drug.get('pref_name')}")
            print(f"Synonyms: {drug.get('molecule_synonyms', [])[:3]}") # Print first 3 synonyms
            
            # Check structure
            print(f"Structure keys: {drug.keys()}")
            
    else:
        print(f"Error: {resp.status_code}")

if __name__ == "__main__":
    debug_chembl_search()
