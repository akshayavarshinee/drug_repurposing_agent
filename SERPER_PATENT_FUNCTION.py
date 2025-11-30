"""
CLEAN SERPER-BASED PATENT SEARCH FUNCTION
Replace the patents_view_api_logic function with this one.
"""

def patents_view_api_logic(
    keyword: str,
    max_results: int = 25,
    from_date: Optional[str] = None
) -> str:
    """
    Core logic for patent search using Serper API (more reliable than PatentsView).
    """
    # Validate inputs
    if not keyword or not keyword.strip():
        return json.dumps({"error": "Keyword is required and cannot be empty"})
    
    max_results = min(max_results or 10, 20)  # Limit to reasonable number

    # Get Serper API key
    serper_api_key = os.getenv("SERPER_API_KEY")
    if not serper_api_key:
        return json.dumps({
            "error": "Missing SERPER_API_KEY environment variable"
        })

    # Construct patent-specific search query
    # Use Google Patents search operators for better results
    search_query = f"{keyword} patent"
    
    # Add date filter if provided (format: YYYY-MM-DD to YYYY)
    if from_date:
        year = from_date.split("-")[0] if "-" in from_date else from_date
        search_query += f" after:{year}"

    # Serper API endpoint
    url = "https://google.serper.dev/search"
    
    # Request payload
    payload = {
        "q": search_query,
        "num": max_results,
        "gl": "us",  # Geographic location
        "hl": "en"   # Language
    }
    
    headers = {
        "X-API-KEY": serper_api_key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Extract patent-related results
        organic_results = data.get("organic", [])
        
        if not organic_results:
            return json.dumps({
                "message": "No patent information found",
                "patents": []
            })
        
        # Filter and structure patent results
        patents = []
        for result in organic_results:
            # Extract patent number from title or link if available
            title = result.get("title", "")
            link = result.get("link", "")
            snippet = result.get("snippet", "")
            
            # Try to extract patent number (e.g., US1234567, EP1234567)
            patent_number = None
            import re
            patent_match = re.search(r'(US|EP|WO|CN|JP)\s*(\d{6,})', title + " " + snippet)
            if patent_match:
                patent_number = patent_match.group(0).replace(" ", "")
            
            # Extract assignee/company from snippet if mentioned
            assignees = []
            # Common patterns: "filed by", "assigned to", "owned by"
            assignee_match = re.search(r'(?:filed by|assigned to|owned by)\s+([A-Z][A-Za-z\s&,\.]+?)(?:\.|,|\s-)', snippet)
            if assignee_match:
                assignees.append(assignee_match.group(1).strip())
            
            patent_info = {
                "title": title,
                "patent_number": patent_number,
                "link": link,
                "snippet": snippet[:200] + "..." if len(snippet) > 200 else snippet,
                "assignees": assignees
            }
            patents.append(patent_info)
        
        return json.dumps({
            "patents": patents,
            "total_found": len(patents),
            "search_query": search_query
        }, indent=2)
        
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"Patent search failed: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"})
