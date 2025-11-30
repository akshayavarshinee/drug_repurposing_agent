import sys
sys.path.insert(0, 'd:/vscode/projects/coe_intern/drug_repurposing_agents')

from pharma_agents.clinical_trails_research_agent import clinical_trials_research_logic, ClinicalTrialsToolInput

# Test Clinical Trials API
print("=== Testing Clinical Trials API ===")
try:
    ct_input = ClinicalTrialsToolInput(
        intervention="Imatinib",
        page_size=5
    )
    result = clinical_trials_research_logic(ct_input)
    print(f"Result: {result[:500]}...")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

# Test with simpler parameters
print("\n=== Testing with minimal parameters ===")
try:
    ct_input = ClinicalTrialsToolInput(
        intervention="Imatinib"
    )
    result = clinical_trials_research_logic(ct_input)
    print(f"Result: {result[:500]}...")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
