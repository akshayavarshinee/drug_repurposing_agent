# FIXED Patents API Logic
# The issue: PatentsView API v1 is PUBLIC and doesn't use API keys
# Remove the X-Api-Key header and PATENTS_VIEW_API_KEY check

def patents_view_api_logic(keyword: str, max_results: int = 10, from_date: Optional[str] = None):
    """
    Core logic for PatentsView API search, callable directly.
    """
    # Parse keyword
    keyword_clean = keyword.strip()
    keyword_words = keyword_clean.split()
    
    # Determine search strategy
    if len(keyword_words) == 1:
        text_operator = "_text_phrase"
    elif len(keyword_words) <= 3:
        text_operator = "_text_phrase"
    else:
        text_operator = "_text_all"
    
    # Main search conditions - NO CPC FILTERING (causes 400/500 errors)
    main_search_conditions = [
        {text_operator: {"patent_title": keyword_clean}},
        {text_operator: {"patent_abstract": keyword_clean}}
    ]
    
    # Build query structure
    query_parts = []
    
    # Add main search (title OR abstract must contain keywords)
    query_parts.append({"_or": main_search_conditions})
    
    # Add date filter if provided
    if from_date:
        query_parts.append({"_gte": {"patent_date": from_date}})
    
    # Combine all conditions with AND
    if len(query_parts) == 1:
        query_dict = query_parts[0]
    else:
        query_dict = {"_and": query_parts}

    # API endpoint
    url = "https://search.patentsview.org/api/v1/patent"

    # Fields to return - focus on pharmaceutical-relevant info
    fields = [
        "patent_id",
        "patent_number",
        "patent_title",
        "patent_abstract",
        "patent_date",
        "patent_type",
        "patent_kind",
        "assignees",
        "inventors",
        "cpc_current"
    ]

    # Sort by relevance: prioritize patents with keywords in title, then by date
    sort = [{"patent_date": "desc"}]

    # Build request params
    params = {
        "q": json.dumps(query_dict),
        "f": json.dumps(fields),
        "s": json.dumps(sort),
        "o": json.dumps({
            "size": max_results,
            "exclude_withdrawn": True,
            "pad_patent_id": False
        })
    }

    # Headers - NO API KEY! PatentsView v1 is public
    headers = {
        "User-Agent": "pharma-researcher/1.0",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        # Request without CPC filtering
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code != 200:
            return json.dumps({
                "error": f"API Error {response.status_code}",
                "details": response.text
            })
        
        data = response.json()
        
        # Extract patents
        patents = data.get("patents", [])
        
        if not patents:
            return json.dumps({
                "message": "No patents found for this keyword",
                "patents": []
            })
        
        # Simplify patent data
        simplified_patents = []
        for patent in patents:
            # Extract assignee names
            assignee_names = []
            if patent.get("assignees"):
                for assignee in patent["assignees"]:
                    if assignee.get("assignee_organization"):
                        assignee_names.append(assignee["assignee_organization"])
            
            # Extract CPC codes
            cpc_codes = []
            if patent.get("cpc_current"):
                for cpc in patent["cpc_current"]:
                    if cpc.get("cpc_section_id"):
                        cpc_codes.append(cpc["cpc_section_id"])
            
            simplified = {
                "patent_number": patent.get("patent_number"),
                "title": patent.get("patent_title"),
                "abstract": patent.get("patent_abstract", "")[:200] + "..." if patent.get("patent_abstract") else "",
                "date": patent.get("patent_date"),
                "assignees": assignee_names[:3],  # Top 3 assignees
                "cpc_codes": list(set(cpc_codes))[:5]  # Top 5 unique CPC codes
            }
            simplified_patents.append(simplified)
        
        return json.dumps({
            "patents": simplified_patents,
            "total_found": len(patents)
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Patent search failed: {str(e)}"})
