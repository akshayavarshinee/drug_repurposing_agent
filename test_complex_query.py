"""
Test script to verify complex query handling in unified pipeline.
"""
from pharma_agents.tools.unified_repurposing_pipeline import detect_input_type

def test_complex_query():
    query = "Metformin including mechanism of action, pharmacology, clinical trials, adverse events, FDA label information, contraindications, and known drug–drug interactions."
    print(f"Testing query: '{query}'")
    
    input_type, cleaned = detect_input_type(query)
    print(f"Detected Type: {input_type}")
    print(f"Cleaned Query: '{cleaned}'")
    
    if input_type == "drug" and cleaned.lower() == "metformin":
        print("✅ SUCCESS: Correctly identified as drug 'Metformin'")
    else:
        print("❌ FAILURE: Failed to identify correctly")

if __name__ == "__main__":
    test_complex_query()
