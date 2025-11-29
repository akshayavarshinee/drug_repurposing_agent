"""
Debug BindingDB for Metformin specifically.
"""
from pharma_agents.tools.bindingdb_tool import bindingdb_get_targets
import json

METFORMIN_SMILES = "CN(C)C(=N)NC(=N)N"

def test_bindingdb():
    print(f"Testing BindingDB for Metformin SMILES: {METFORMIN_SMILES}")
    
    # Test 1: Standard call as in pipeline
    print("\nTest 1: Pipeline settings (sim=0.85, aff=10)")
    targets = bindingdb_get_targets(METFORMIN_SMILES, similarity_cutoff=0.85, affinity_cutoff=10.0)
    print(f"Found {len(targets)} targets")
    
    # Test 2: Lower similarity
    print("\nTest 2: Lower similarity (sim=0.7, aff=10)")
    targets = bindingdb_get_targets(METFORMIN_SMILES, similarity_cutoff=0.7, affinity_cutoff=10.0)
    print(f"Found {len(targets)} targets")
    
    # Test 3: Exact match only (sim=1.0)
    print("\nTest 3: Exact match (sim=1.0, aff=10)")
    targets = bindingdb_get_targets(METFORMIN_SMILES, similarity_cutoff=1.0, affinity_cutoff=10.0)
    print(f"Found {len(targets)} targets")

    # Test 4: No affinity cutoff
    print("\nTest 4: No affinity cutoff (sim=0.85, aff=None)")
    targets = bindingdb_get_targets(METFORMIN_SMILES, similarity_cutoff=0.85, affinity_cutoff=None)
    print(f"Found {len(targets)} targets")

if __name__ == "__main__":
    test_bindingdb()
