import requests
import json
import os
import dotenv

dotenv.load_dotenv(override=True)

# --- Tool Logic Copies for Direct Verification ---

def serper_trade_tool_logic(hs_code: str, year: int = 2024, flow: str = None) -> str:
    """
    Search for global EXIM trade trends and data using web search.
    """
    # Construct a targeted search query
    query_parts = [f"{hs_code} trade data {year}"]
    if flow:
        query_parts.append(f"{flow} statistics")
    else:
        query_parts.append("export import trends")
    
    query_parts.append("top countries value")
    
    search_query = " ".join(query_parts)
    
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": search_query})
    
    api_key = os.environ.get("SERPER_API_KEY")
    if not api_key:
        return json.dumps({"error": "Missing SERPER_API_KEY environment variable."})
        
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }

    try:
        print(f"Searching Exim: {search_query}")
        response = requests.post(url, headers=headers, data=payload, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return json.dumps({"error": f"Search failed: {str(e)}"})

def market_insights_tool_logic(query: str) -> str:
    """Search for market insights, sales data, and pharmaceutical trends using web search."""
    # Enhance query for sales data if it looks like a sales request
    search_query = query
    if "sales" in query.lower() or "revenue" in query.lower():
        if "global" not in query.lower():
            search_query += " global sales revenue"
        if "202" not in query:  # If no recent year specified
            search_query += " 2024"
            
    url = "https://google.serper.dev/search"

    payload = json.dumps({
        "q": search_query
    })
    api_key = os.environ.get("SERPER_API_KEY")
    if not api_key:
        return json.dumps({"error": "No API key found."})
        
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }

    try:
        print(f"Searching Market: {search_query}")
        response = requests.post(url, headers=headers, data=payload, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return json.dumps({"error": f"Search failed: {str(e)}"})

# --- Test Execution ---

def test_tools():
    print("--- Testing Exim Tool Logic (Serper Trade) ---")
    # Try to get trade data for HS Code 3004 (Medicaments)
    try:
        exim_result = serper_trade_tool_logic(hs_code="3004", year=2024)
        # Parse JSON to check if we got organic results
        data = json.loads(exim_result)
        if "organic" in data and len(data["organic"]) > 0:
            print(f"✅ Success! Found {len(data['organic'])} organic results.")
            print(f"First result title: {data['organic'][0].get('title')}")
        else:
            print(f"⚠️ No organic results found. Raw output start: {exim_result[:200]}")
    except Exception as e:
        print(f"❌ Exim Tool Failed: {e}")

    print("\n--- Testing Market Tool Logic ---")
    # Try to get sales data for Metformin
    try:
        market_result = market_insights_tool_logic(query="Metformin sales")
        # Parse JSON
        data = json.loads(market_result)
        if "organic" in data and len(data["organic"]) > 0:
            print(f"✅ Success! Found {len(data['organic'])} organic results.")
            print(f"First result title: {data['organic'][0].get('title')}")
        else:
            print(f"⚠️ No organic results found. Raw output start: {market_result[:200]}")
    except Exception as e:
        print(f"❌ Market Tool Failed: {e}")

if __name__ == "__main__":
    test_tools()
