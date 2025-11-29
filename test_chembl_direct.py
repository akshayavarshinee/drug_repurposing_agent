"""
Direct test of chembl_search_molecule function.
"""
from pharma_agents.tools.chembl_tools import chembl_search_molecule

def test_metformin_search():
    print("Testing chembl_search_molecule with 'Metformin'...")
    result = chembl_search_molecule("Metformin")
    
    if result:
        print(f"✅ Found drug:")
        print(f"   ChEMBL ID: {result['chembl_id']}")
        print(f"   Name: {result['name']}")
        print(f"   SMILES: {result['smiles'][:50]}...")
        
        # Check if it's the correct Metformin (CHEMBL1431)
        if result['chembl_id'] == 'CHEMBL1431':
            print("✅ CORRECT: Found CHEMBL1431 (Metformin)")
        else:
            print(f"❌ WRONG: Expected CHEMBL1431 but got {result['chembl_id']}")
    else:
        print("❌ No result found")

if __name__ == "__main__":
    test_metformin_search()
