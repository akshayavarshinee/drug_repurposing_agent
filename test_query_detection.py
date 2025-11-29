"""
Test the detect_input_type function with complex queries.
"""
from pharma_agents.tools.unified_repurposing_pipeline import detect_input_type

# Test cases
test_queries = [
    "Metformin including mechanism of action, pharmacology, clinical trials, adverse events, FDA label information, contraindications, and known drug–drug interactions.",
    "Type 2 Diabetes, and what is the current patent whitespace and global API (HS 3004, 2937) import–export landscape for deployment",
    "Type 2 Diabetes",
    "Metformin"
]

print("Testing detect_input_type function:\n")
print("="*80)

for query in test_queries:
    input_type, cleaned = detect_input_type(query)
    print(f"\nOriginal Query:")
    print(f"  {query[:100]}{'...' if len(query) > 100 else ''}")
    print(f"Detected Type: {input_type}")
    print(f"Cleaned Query: {cleaned}")
    print("-"*80)
