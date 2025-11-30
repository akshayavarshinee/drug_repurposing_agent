import sys
sys.path.insert(0, 'd:/vscode/projects/coe_intern/drug_repurposing_agents')

from pharma_agents.patent_research_agent import patents_view_api_tool
import json

# Test the corrected patent tool directly
print("Testing Patent Tool with 'Metformin'...")

# Access the underlying function from the FunctionTool wrapper
result = patents_view_api_tool.func(keyword="Metformin", max_results=5)

data = json.loads(result)
print(f"\nResult Keys: {list(data.keys())}")

if "error" in data:
    print(f"\n❌ Error: {data['error']}")
    if "suggestion" in data:
        print(f"Suggestion: {data['suggestion']}")
else:
    print(f"\n✅ Found {data.get('returned', 0)} patents out of {data.get('total_found', 0)} total")
    if data.get('patents'):
        print(f"\nFirst patent:")
        print(f"  Title: {data['patents'][0]['title']}")
        print(f"  Date: {data['patents'][0]['date']}")
        print(f"  Assignees: {data['patents'][0]['assignees']}")

