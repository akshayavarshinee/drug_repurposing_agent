"""
Test script for the enhanced Open Targets tool.

This script demonstrates the new features:
1. Datasource and datatype scores
2. Improved error handling
3. Optional datasource filtering
"""

from pharma_agents.tools.open_targets_tool import open_targets_disease_lookup
import json

def test_basic_lookup():
    """Test basic disease lookup without filters."""
    print("=" * 60)
    print("Test 1: Basic lookup for 'Type 2 Diabetes'")
    print("=" * 60)
    
    results = open_targets_disease_lookup("Type 2 Diabetes", limit=3)
    
    if results:
        print(f"\n✓ Found {len(results)} targets\n")
        for i, target in enumerate(results, 1):
            print(f"Target {i}:")
            print(f"  Symbol: {target['symbol']}")
            print(f"  Name: {target['name']}")
            print(f"  Biotype: {target.get('biotype', 'N/A')}")
            print(f"  Association Score: {target['association_score']:.4f}")
            print(f"  Datasource Scores: {list(target['datasource_scores'].keys())[:5]}")
            print(f"  Datatype Scores: {list(target['datatype_scores'].keys())}")
            print()
    else:
        print("✗ No results found")
    
    return results

def test_with_datasource_filter():
    """Test lookup with datasource filtering."""
    print("=" * 60)
    print("Test 2: Lookup with ChEMBL datasource filter")
    print("=" * 60)
    
    results = open_targets_disease_lookup(
        "Type 2 Diabetes", 
        limit=5,
        datasource_ids=["chembl"]
    )
    
    if results:
        print(f"\n✓ Found {len(results)} targets with ChEMBL evidence\n")
        for i, target in enumerate(results, 1):
            chembl_score = target['datasource_scores'].get('chembl', 'N/A')
            print(f"Target {i}: {target['symbol']} - ChEMBL Score: {chembl_score}")
    else:
        print("✗ No results found with ChEMBL evidence")
    
    return results

def test_error_handling():
    """Test error handling with invalid disease name."""
    print("=" * 60)
    print("Test 3: Error handling with invalid disease")
    print("=" * 60)
    
    results = open_targets_disease_lookup("ThisDiseaseDoesNotExist12345", limit=3)
    
    if not results:
        print("✓ Correctly handled non-existent disease")
    else:
        print("✗ Unexpected results for invalid disease")
    
    return results

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("OPEN TARGETS TOOL - ENHANCED VERSION TEST SUITE")
    print("=" * 60 + "\n")
    
    # Run tests
    test_basic_lookup()
    print("\n")
    test_with_datasource_filter()
    print("\n")
    test_error_handling()
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)
