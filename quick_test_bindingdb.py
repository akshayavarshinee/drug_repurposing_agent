"""
Quick test to see what's actually being parsed.
"""

from pharma_agents.tools.bindingdb_tool import bindingdb_get_targets

# Test with aspirin - we know from debug this has 37 hits
smiles = "CC(=O)Oc1ccccc1C(=O)O"

print("Testing with Aspirin SMILES:", smiles)
print("=" * 60)

results = bindingdb_get_targets(
    smiles=smiles,
    similarity_cutoff=0.85,
    affinity_cutoff=10000.0  # Very high cutoff to see all results
)

print(f"\nGot {len(results)} results")

if results:
    print("\nFirst 3 results:")
    for i, r in enumerate(results[:3], 1):
        print(f"\n{i}. {r['target_name']}")
        print(f"   Species: {r['target_species']}")
        print(f"   Affinity: {r['affinity_value']} {r['affinity_unit']} ({r['affinity_type']})")
        print(f"   Normalized: {r['affinity_value_uM']:.2f} µM")
        print(f"   Approximate: {r['is_approximate']}")
