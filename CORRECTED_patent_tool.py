# This is the CORRECTED patents_view_api_tool function
# Copy this and replace lines 198-464 in patent_research_agent.py

@function_tool
def patents_view_api_tool(
    keyword: str,
    max_results: int = 25,
    from_date: Optional[str] = None
) -> str:
    """
    Search for pharmaceutical and biotech patents using keywords.
    
    Searches patent titles and abstracts for relevant pharmaceutical innovations,
    drug formulations, therapeutic methods, and biotech inventions.
    Returns patent details including title, abstract, date, inventors, and assignees.
    ***DO NOT PASTE THE EXACT USER'S QUERY IN THE KEYWORD ARGUMENT. MAKE SURE THE KEYWORD
    IS A SHORT PHRASE OR SINGLE WORD THAT SHALL HAVE PATENTS.***
    
    Args:
        keyword: Keywords to search for in patent titles and abstracts 
                (e.g., 'semaglutide', 'GLP-1 receptor agonist', 'diabetes treatment')
        max_results: Maximum number of patents to return (default 25, max 100)
        from_date: Filter patents from this date onwards (YYYY-MM-DD format, e.g., '2020-01-01')
    
    Returns:
        JSON string with patent results and metadata
    """
    
    # Validate inputs
    if not keyword or not keyword.strip():
        return json.dumps({"error": "Keyword is required and cannot be empty"})
    
    max_results = min(max_results or 25, 100)

    # API Key
    api_key = os.getenv("PATENTS_VIEW_API_KEY")
    if not api_key:
        return json.dumps({
            "error": "Missing PATENTS_VIEW_API_KEY environment variable. Please set it in your .env file."
        })

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
    
    # Build query - simple OR search
    query_dict = {"_or": main_search_conditions}
    
    # Add date filter if provided
    if from_date:
        query_dict = {
            "_and": [
                {"_or": main_search_conditions},
                {"_gte": {"patent_date": from_date}}
            ]
        }

    # API endpoint
    url = "https://search.patentsview.org/api/v1/patent"

    # Fields - using cpc_current instead of cpc_group_id
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

    sort = [{"patent_date": "desc"}]

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

    headers = {
        "User-Agent": "pharma-researcher/1.0",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Api-Key": api_key
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        patents = data.get("patents", [])

        if not patents:
            return json.dumps({
                "error": f"No patents found for keyword '{keyword}'",
                "suggestion": "Try different keywords, broader terms, or check if the search is too specific.",
                "query_used": query_dict
            })

        # Format results
        formatted_patents = []
        keyword_lower = keyword_clean.lower()
        keyword_words_lower = [w.lower() for w in keyword_words]
        
        for patent in patents:
            # Get assignees
            assignees = patent.get("assignees", [])
            assignee_names = [a.get("assignee_organization", "Individual") for a in assignees if a.get("assignee_organization")]
            
            # Get inventors
            inventors = patent.get("inventors", [])
            inventor_names = [
                f"{inv.get('inventor_name_first', '')} {inv.get('inventor_name_last', '')}".strip()
                for inv in inventors
            ]
            
            # Get CPC from cpc_current (nested structure)
            cpc_current = patent.get("cpc_current", [])
            cpc_info = []
            for cpc in cpc_current[:3]:
                group_id = cpc.get("cpc_group_id", "")
                subclass_id = cpc.get("cpc_subclass_id", "")
                if group_id:
                    cpc_info.append({"group_id": group_id, "subclass_id": subclass_id})
            
            # Calculate relevance score
            title = patent.get("patent_title", "").lower()
            abstract = patent.get("patent_abstract", "").lower()
            
            relevance_score = 0
            if keyword_lower in title:
                relevance_score += 10
            elif any(word in title for word in keyword_words_lower):
                relevance_score += 5
            
            if keyword_lower in abstract:
                relevance_score += 3
            elif any(word in abstract for word in keyword_words_lower):
                relevance_score += 1
            
            formatted_patents.append({
                "patent_id": patent.get("patent_id"),
                "patent_number": patent.get("patent_number"),
                "title": patent.get("patent_title"),
                "abstract": patent.get("patent_abstract", "")[:500] + "..." if len(patent.get("patent_abstract", "")) > 500 else patent.get("patent_abstract", ""),
                "date": patent.get("patent_date"),
                "type": patent.get("patent_type"),
                "assignees": assignee_names[:3] if assignee_names else ["Individual/Unassigned"],
                "inventors": inventor_names[:3],
                "cpc_classifications": cpc_info,
                "relevance_score": relevance_score
            })
        
        formatted_patents.sort(key=lambda x: (x["relevance_score"], x["date"] or ""), reverse=True)

        result = {
            "patents": formatted_patents,
            "total_found": data.get("total_patent_count", len(patents)),
            "returned": len(formatted_patents),
            "_query_metadata": {
                "keyword": keyword,
                "from_date": from_date,
                "query_structure": query_dict,
                "api_url": url
            }
        }
        
        return json.dumps(result, indent=2)

    except requests.exceptions.HTTPError as e:
        return json.dumps({
            "error": f"HTTP error {e.response.status_code}",
            "details": e.response.text[:500],
            "url": url,
            "suggestion": "Check if API key is valid and has proper permissions"
        })

    except Exception as e:
        return json.dumps({
            "error": f"Exception: {str(e)}",
            "url": url,
            "query": query_dict
        })
