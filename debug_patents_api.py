import sys
sys.path.insert(0, 'd:/vscode/projects/coe_intern/drug_repurposing_agents')

from pharma_agents.patent_research_agent import patents_view_api_logic

# Test Patents API
print("=== Testing Patents API ===")
try:
    result = patents_view_api_logic(keyword="Imatinib", max_results=5)
    print(f"Result: {result[:500]}...")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

# Test with different keyword
print("\n=== Testing with generic keyword ===")
try:
    result = patents_view_api_logic(keyword="cancer treatment", max_results=5)
    print(f"Result: {result[:500]}...")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
