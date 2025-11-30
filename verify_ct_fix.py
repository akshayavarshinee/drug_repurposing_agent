from pharma_agents.clinical_trails_research_agent import clinical_trials_research_tool, ClinicalTrialsToolInput
import json

def verify_fix():
    print("Verifying Clinical Trials Tool Fix...\n")
    
    # Test 1: Status only
    print("Test 1: Status = RECRUITING")
    inp1 = ClinicalTrialsToolInput(
        condition="Diabetes",
        status=["RECRUITING"],
        page_size=5
    )
    res1 = clinical_trials_research_tool(inp1)
    if "error" in res1:
        print(f"Error: {res1['error']}")
    else:
        print(f"Success! Found {res1['_query_metadata']['returned']} studies.")
        print(f"Total Count: {res1['_query_metadata']['total_count']}")
    print("-" * 50)

    # Test 2: Phase only
    print("Test 2: Phase = PHASE2")
    inp2 = ClinicalTrialsToolInput(
        condition="Diabetes",
        phase=["PHASE2"],
        page_size=5
    )
    res2 = clinical_trials_research_tool(inp2)
    if "error" in res2:
        print(f"Error: {res2['error']}")
    else:
        print(f"Success! Found {res2['_query_metadata']['returned']} studies.")
        print(f"Query Term Used: {res2.get('params', {}).get('query.term')}") # Need to check if params are returned in success? No, they are not in success path of tool but I can infer from results.
    print("-" * 50)

    # Test 3: Both
    print("Test 3: Status = RECRUITING + Phase = PHASE3")
    inp3 = ClinicalTrialsToolInput(
        condition="Diabetes",
        status=["RECRUITING"],
        phase=["PHASE3"],
        page_size=5
    )
    res3 = clinical_trials_research_tool(inp3)
    if "error" in res3:
        print(f"Error: {res3['error']}")
    else:
        print(f"Success! Found {res3['_query_metadata']['returned']} studies.")
    print("-" * 50)

if __name__ == "__main__":
    verify_fix()
