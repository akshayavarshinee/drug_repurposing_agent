import requests
import json
import os
import dotenv

dotenv.load_dotenv(override=True)

def test_query(keyword):
    print(f"\n--- Testing keyword: '{keyword}' ---")
    
    api_key = os.getenv("PATENTS_VIEW_API_KEY")
    if not api_key:
        print("❌ No API key found in environment!")
        return

    # Logic from patent_research_agent.py
    keyword_clean = keyword.strip()
    keyword_words = keyword_clean.split()
    
    if len(keyword_words) == 1:
        text_operator = "_text_phrase"
    elif len(keyword_words) <= 3:
        text_operator = "_text_phrase"
    else:
        text_operator = "_text_all"
    
    main_search_conditions = [
        {text_operator: {"patent_title": keyword_clean}},
        {text_operator: {"patent_abstract": keyword_clean}}
    ]
    
    query_dict = {"_or": main_search_conditions}
    
    url = "https://search.patentsview.org/api/v1/patent"
    fields = ["patent_id", "patent_title", "patent_date"]
    
    params = {
        "q": json.dumps(query_dict),
        "f": json.dumps(fields),
        "o": json.dumps({"size": 5})
    }
    
    headers = {
        "User-Agent": "pharma-researcher/1.0",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Api-Key": api_key
    }
    
    print(f"Query: {json.dumps(query_dict)}")
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            total = data.get("total_patent_count")
            patents = data.get("patents", [])
            print(f"Total found: {total}")
            print(f"Returned: {len(patents)}")
            if patents:
                print(f"First title: {patents[0].get('patent_title')}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_query("Metformin")
    test_query("Diabetes") # Try a broader term to verify API works at all
