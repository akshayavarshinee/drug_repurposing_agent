import requests
import json
import os
import dotenv

dotenv.load_dotenv(override=True)

def run_test(name, query_dict, fields, description):
    print(f"--- Test: {name} ---")
    print(f"Description: {description}")
    
    api_key = os.getenv("PATENTS_VIEW_API_KEY")
    url = "https://search.patentsview.org/api/v1/patent"
    
    params = {
        "q": json.dumps(query_dict),
        "f": json.dumps(fields),
        "o": json.dumps({"size": 1})
    }
    
    headers = {
        "User-Agent": "pharma-researcher/1.0",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Api-Key": api_key
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Success!")
            data = response.json()
            print(f"Returned {data.get('total_patent_count')} patents")
            if data.get('patents'):
                print(f"Sample keys: {list(data['patents'][0].keys())}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    print("\n")

def verify_patent_tool():
    # Test 1: Minimal valid query and fields
    q1 = {"_text_phrase": {"patent_title": "Metformin"}}
    f1 = ["patent_id", "patent_title"]
    run_test("Minimal", q1, f1, "Basic title search with minimal fields")

    # Test 2: Add Abstract to Query
    q2 = {"_or": [
        {"_text_phrase": {"patent_title": "Metformin"}},
        {"_text_phrase": {"patent_abstract": "Metformin"}}
    ]}
    run_test("Abstract Query", q2, f1, "Search in title OR abstract")

    # Test 3: Add CPC Filter to Query
    q3 = {"_and": [
        q2,
        {"_or": [{"cpc_group_id": {"_begins": "A61K"}}]}
    ]}
    run_test("CPC Query", q3, f1, "Add CPC filter (A61K)")

    # Test 4: Request Extra Fields (Assignees, Inventors)
    f4 = ["patent_id", "patent_title", "assignees", "inventors"]
    run_test("Extra Fields", q1, f4, "Request assignees and inventors")

    # Test 6: CPC Query with Nested Field
    q6 = {"_and": [
        q2,
        {"_or": [{"cpc_current.cpc_group_id": {"_begins": "A61K"}}]}
    ]}
    run_test("CPC Nested Query", q6, f1, "Filter by cpc_current.cpc_group_id")

    # Test 7: Request cpc_current Field
    f7 = ["patent_id", "patent_title", "cpc_current"]
    print(f"--- Test: CPC Current Field ---")
    print(f"Description: Request cpc_current field and inspect structure")
    
    params = {
        "q": json.dumps(q1),
        "f": json.dumps(f7),
        "o": json.dumps({"size": 1})
    }
    
    headers = {
        "User-Agent": "pharma-researcher/1.0",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Api-Key": os.getenv("PATENTS_VIEW_API_KEY")
    }
    
    try:
        response = requests.get("https://search.patentsview.org/api/v1/patent", headers=headers, params=params, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            patents = data.get("patents", [])
            if patents:
                cpc_data = patents[0].get("cpc_current", [])
                print(f"cpc_current data (first item): {json.dumps(cpc_data[:1], indent=2)}")
            else:
                print("No patents found to inspect.")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    verify_patent_tool()
