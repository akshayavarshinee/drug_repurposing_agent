"""
Direct verification of tool functions.
"""
from pharma_agents.tools.chembl_tools import chembl_search_molecule, chembl_mechanisms
from pharma_agents.tools.bindingdb_tool import bindingdb_get_targets
from pharma_agents.tools.open_targets_tool import open_targets_disease_lookup

def test_chembl():
    print("Testing ChEMBL...")
    res = chembl_search_molecule("Metformin")
    print(f"Search Result: {res}")
    if res:
        mechs = chembl_mechanisms(res["chembl_id"])
        print(f"Mechanisms: {len(mechs)} found")
        if mechs:
            print(f"Sample Mechanism: {mechs[0]}")

def test_bindingdb():
    print("\nTesting BindingDB...")
    # Metformin SMILES
    smiles = "CN(C)C(=N)N=C(N)N" 
    targets = bindingdb_get_targets(smiles)
    print(f"Targets found: {len(targets)}")
    if targets:
        print(f"Sample Target: {targets[0]}")

def test_open_targets():
    print("\nTesting Open Targets...")
    targets = open_targets_disease_lookup("Type 2 Diabetes")
    print(f"Targets found: {len(targets)}")
    if targets:
        print(f"Sample Target: {targets[0]}")

if __name__ == "__main__":
    test_chembl()
    test_bindingdb()
    test_open_targets()
