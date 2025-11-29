"""
Test script for the fixed BindingDB tool.

This script tests the corrected implementation with proper similarity cutoff.
"""

from pharma_agents.tools.bindingdb_tool import bindingdb_get_targets

def test_simple_molecule():
    """Test with aspirin - a well-known drug."""
    print("=" * 60)
    print("Test 1: Aspirin (CC(=O)Oc1ccccc1C(=O)O)")
    print("=" * 60)
    
    smiles = "CC(=O)Oc1ccccc1C(=O)O"  # Aspirin
    results = bindingdb_get_targets(
        smiles=smiles,
        similarity_cutoff=0.85,
        affinity_cutoff=50.0    # 50 µM cutoff to get some results
    )
    
    if results:
        print(f"\n✓ Found {len(results)} target-affinity pairs\n")
        
        # Show first 5 with best (lowest) affinity
        sorted_results = sorted(results, key=lambda x: x['affinity_value_uM'])
        
        for i, target in enumerate(sorted_results[:5], 1):
            print(f"Target {i}:")
            print(f"  Name: {target['target_name']}")
            print(f"  Species: {target['target_species']}")
            print(f"  Affinity: {target['affinity_value']} {target['affinity_unit']} ({target['affinity_type']})")
            print(f"  Normalized: {target['affinity_value_uM']:.3f} µM")
            print(f"  Approximate: {'Yes' if target['is_approximate'] else 'No'}")
            print()
    else:
        print("✗ No results found")
    
    return results

def test_complex_molecule():
    """Test with caffeine - another well-known compound."""
    print("=" * 60)
    print("Test 2: Caffeine (CN1C=NC2=C1C(=O)N(C(=O)N2C)C)")
    print("=" * 60)
    
    smiles = "CN1C=NC2=C1C(=O)N(C(=O)N2C)C"  # Caffeine
    
    results = bindingdb_get_targets(
        smiles=smiles,
        similarity_cutoff=0.85,
        affinity_cutoff=100.0     # 100 µM cutoff
    )
    
    if results:
        print(f"\n✓ Found {len(results)} target-affinity pairs\n")
        
        # Group by target
        targets_dict = {}
        for entry in results:
            target_name = entry['target_name']
            if target_name not in targets_dict:
                targets_dict[target_name] = []
            targets_dict[target_name].append(entry)
        
        print(f"Unique targets: {len(targets_dict)}\n")
        
        # Show first 3 targets with best affinity
        sorted_targets = sorted(targets_dict.items(), 
                               key=lambda x: min(e['affinity_value_uM'] for e in x[1]))
        
        for target_name, entries in sorted_targets[:3]:
            best_affinity = min(entries, key=lambda x: x['affinity_value_uM'])
            print(f"Target: {target_name}")
            print(f"  Species: {entries[0]['target_species']}")
            print(f"  Affinity measurements: {len(entries)}")
            print(f"  Best affinity: {best_affinity['affinity_value_uM']:.3f} µM ({best_affinity['affinity_type']})")
            print()
    else:
        print("✗ No results found")
    
    return results

def test_no_match():
    """Test with invalid SMILES to check error handling."""
    print("=" * 60)
    print("Test 3: Invalid SMILES (error handling)")
    print("=" * 60)
    
    smiles = "INVALID_SMILES_STRING"
    
    results = bindingdb_get_targets(
        smiles=smiles,
        similarity_cutoff=0.85,
        affinity_cutoff=10.0
    )
    
    if not results:
        print("✓ Correctly handled invalid SMILES")
    else:
        print(f"⚠ Unexpected: Got {len(results)} results for invalid SMILES")
    
    return results

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("BINDINGDB TOOL - FIXED VERSION TEST SUITE")
    print("=" * 60 + "\n")
    
    # Run tests
    test_simple_molecule()
    print("\n")
    test_complex_molecule()
    print("\n")
    test_no_match()
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)
    print("\nNote: BindingDB API may be slow or return empty results")
    print("if no structurally similar compounds exist in the database.")
