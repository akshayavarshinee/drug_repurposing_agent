from agents import Agent, function_tool
import requests
import json
import os
from typing import Optional, Dict, Any, Union
import dotenv

dotenv.load_dotenv(override=True)

# INSTRUCTIONS = (
#     """
#         You specialize in patent intelligence for drug repurposing.
#         You analyze Orange Book listed patents, expired claims, secondary medical use
#         claims, formulation patents, and newly filed claims relating to new indications.
#         You use the PatentsView API to retrieve REAL, up-to-date filings, assignees,
#         claims text, expiration timelines, and legal status.You should not just fetch results but also provide
#         interpretation and analysis of the data also provide the ending date of the patent if present.
#         Map patent activity relevant to repurposing: expired patents, secondary claims,
#         formulation IP, new therapeutic claims, and FTO risks for new indications.
#         Extract timelines, unexpired protections, and whitespace opportunities.
#     """
# )

INSTRUCTIONS = """
You are a GLOBAL PATENT INTELLIGENCE AGENT for drug repurposing.

CORE ROLE:
Your job is to analyze patent filings and legal status to determine **if a drug can be safely
repurposed, where the real novelty lives, and what FTO (Freedom-to-Operate) risks exist**.

MANDATORY TOOL BEHAVIOR:
- You MUST call your patent tool (e.g., serper_patents_tool or patents_view_apitool) to get REAL data.
- Maximum 3 tool calls per query. If 3 attempts fail, return a short gap summary and stop.
- Never invent patent IDs, dates, claims, or legal status.
- If expiration or end date is not present in tool data, say so explicitly in the response.

--------------------------------
PRACTICAL ANALYSIS CHAIN (ALWAYS FOLLOW)
--------------------------------

When tool results are returned, analyze in this order and reflect it in output:

1. **PUBLICATION / USER DISEASE OR DRUG CONTEXT**
   - Understand whether the query is for a specific drug or for disease-level repurposing.

2. **PATENT LEGAL STATUS**
   - Extract REAL:
     • Grant status (granted / pending / rejected)
     • Legal state (active / expired / withdrawn)
     • Assignee(s) — organizations or companies holding the patent
     • Expiration or end date if present
   - Produce 2–4 concise bullets on legal risks.

3. **CLAIM TEXT MINING**
   Extract only if visible in tool results:
   • Secondary medical use (treatment of a *new disease* using a known drug/target)
   • Key formulation claims (delivery system, composition, stability improvements)
   • Combination therapy IP (drug blends or co-targeted formulations)
   • Indication whitening signals useful for repurposing ML feasibility
   - Summarize mined claim text into a 2–5 sentence rationale, not raw dumps.

4. **RELEVANCE TO REPURPOSING**
   Label findings as:
   ✅ **Clear white-space novelty**, meaning:
      - Primary patent expired + secondary medical use not claimed yet for disease of interest
      - Unique formulation not explored in a geography (e.g., India-specific delivery)
   🟡 **Possible but constrained practicality**, meaning:
      - Patent active but opportunity may live in unclaimed formulation or population
   ❌ **Not practical**, meaning:
      - Patent active with unexpired protection in the exact indication pathway
   - Contain 2–5 concise bullets max.

5. **TIMELINE EXTRACTION IF APPLICABLE**
   - Provide expiration/end date if available
   - Convert timelines into practical FTO insight
     Example tone: “Protection expires 2027 → strategy must focus on filing after this or
     innovate at formulation level before this.”

--------------------------------
EXPECTED OUTPUT STRUCTURE
--------------------------------

Your response must contain, in natural readable sections (no JSON wrappers):

## 1. Active Patent Snapshot (table only if results exist)
Columns to include:
• Patent ID or number from tool  
• Assignee (organization)  
• Grant Status  
• Legal Status (active / expired)  
• Expiration / End Date (if field present)

## 2. White-Space Opportunity Summary (2–5 bullets max)
Bullets focus on:
• expired primary patents  
• secondary medical use white-space  
• formulation or geography-based novel filing potential  
• combination-therapy gaps

## 3. FTO Practical Risk Notes (1–3 lines max)
What to flag:
• Unexpired patent protections blocking exact indication
• Competitor patents already claiming secondary medical use

## 4. Repurposing Patent Practical Score (single float 0.0–1.0 line at end)
Score rationale:
• 1.0 → exact indication patents expired + clear white-space  
• 0.5 → patents unexpired but formulation/population gap exists  
• 0.0 → active patents block indication, no white-space from tool data

--------------------------------
FAILURE / GAP FALLBACK
--------------------------------
***IF ONE TOOL GIVES ERROR OR NO OUTPUT, TRY SEARCHING WITH ANOTHER TOOL.***
If tool data returns no useful filings or errors after 3 tries:

Return ONLY:
“No actionable patent filings for repurposing derived via tools. Disease or drug lacks visible
secondary medical use or whitespace opportunity in patent data.”

--------------------------------
STYLE & AUDIENCE GUIDE
--------------------------------
- Tone: concise, intelligent, practical, non-formal but precise
- Audience: repurposing scientists, regulatory teams, ML engineers
- Tables only from tool output, never invented
- No filler text or unrelated API commentary
- Avoid infinite reasoning loops; summarize early when stuck
"""

import re

class PharmaKeywordExtractor:
    def __init__(self):
        self.drug_pattern = re.compile(r"\b([A-Za-z][A-Za-z0-9\-\+]{2,}|.+mab|.+nib|.+vir)\b", flags=re.I)
        self.disease_pattern = re.compile(
            r"\b(diabetes|cancer|obesity|arthritis|malaria|tuberculosis|alzheimer\S*|parkinson\S*|anemia|.+emia|.+iasis)\b",
            flags=re.I
        )

    def extract(self, query: str):
        drug = None
        d_match = self.drug_pattern.search(query)
        if d_match:
            drug = d_match.group(0)

        disease = None
        dis_match = self.disease_pattern.search(query)
        if dis_match:
            disease = dis_match.group(0)

        drug = drug.strip() if drug else None
        disease = disease.strip() if disease else None
        return drug, disease


def build_patent_query(raw_query: str) -> str:
    extractor = PharmaKeywordExtractor()
    drug, disease = extractor.extract(raw_query)

    # Practical, search-friendly prompt building
    if drug and disease:
        search_q = f"{drug} \"treatment of {disease}\" secondary medical use patent"
    elif disease:
        search_q = f"\"{disease}\" drug secondary medical use patent filings"
    elif drug:
        search_q = f"{drug} secondary medical use patent filings"
    else:
        # If nothing is detected, fallback to the raw query but trimmed
        cleaned = raw_query[:120].replace("\n", " ").strip()
        search_q = f"{cleaned} patent filings"
    
    return search_q



@function_tool
def serper_patent_tool(query: str):
    """Search for patent information using web search.
    
    Args:
        query: The search query string
    """
    url = "https://google.serper.dev/patents"

    payload = json.dumps({
    "q": build_patent_query(query)
    })
    headers = {
    'X-API-KEY': os.environ.get("SERPER_API_KEY"),
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.text

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

    # Parse keyword to determine if it's a phrase or multiple words
    keyword_clean = keyword.strip()
    keyword_words = keyword_clean.split()
    
    # Determine search strategy based on keyword structure
    # For single words or short phrases, use _text_phrase for exact matching
    # For multiple words, use _text_all to require all words
    if len(keyword_words) == 1:
        # Single word - use phrase search for exact match
        text_operator = "_text_phrase"
    elif len(keyword_words) <= 3:
        # Short phrase - try phrase first, fallback to all words
        text_operator = "_text_phrase"
    else:
        # Multiple words - require all words to be present
        text_operator = "_text_all"
    
    # Build query with pharmaceutical CPC filtering for relevance
    # CPC codes for pharmaceuticals: A61K (preparations for medical/dental/veterinary), 
    # A61P (therapeutic activity), C07K (peptides), C12N (microorganisms/enzymes)
    pharma_cpc_codes = ["A61K", "A61P", "C07K", "C12N"]
    
    # Main search conditions - prioritize title matches (more relevant)
    # Use AND to require keywords in title OR abstract, but prefer title
    main_search_conditions = [
        {text_operator: {"patent_title": keyword_clean}},  # Title match (higher priority)
        {text_operator: {"patent_abstract": keyword_clean}}  # Abstract match (fallback)
    ]
    
    # Build query structure
    query_parts = []
    
    # Add main search (title OR abstract must contain keywords)
    query_parts.append({"_or": main_search_conditions})
    
    # Add pharmaceutical CPC filter to ensure relevance
    # This filters to pharmaceutical/medical/biotech patents only
    # Use cpc_group_id with _begins to match codes starting with these prefixes
    cpc_conditions = [
        {"cpc_group_id": {"_begins": code}} for code in pharma_cpc_codes
    ]
    
    if cpc_conditions:
        # Use OR to match any pharmaceutical CPC code
        query_parts.append({"_or": cpc_conditions})
    
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
        "cpc_group_id",
        "cpc_group_title"
    ]

    # Sort by relevance: prioritize patents with keywords in title, then by date
    # Note: PatentsView doesn't support relevance scoring directly, 
    # but we'll filter and sort by date (newest first)
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

    # Headers
    headers = {
        "User-Agent": "pharma-researcher/1.0",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Api-Key": api_key
    }

    try:
        # First attempt: with CPC filter for pharmaceutical relevance
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Extract results
        patents = data.get("patents", [])
        
        # If no results with CPC filter, try without it (broader search)
        if not patents and len(query_parts) > 1:
            # Remove CPC filter and try again
            query_parts_no_cpc = [query_parts[0]]  # Keep only the main search
            if from_date:
                query_parts_no_cpc.append({"_gte": {"patent_date": from_date}})
            
            if len(query_parts_no_cpc) == 1:
                query_dict_fallback = query_parts_no_cpc[0]
            else:
                query_dict_fallback = {"_and": query_parts_no_cpc}
            
            params_fallback = {
                "q": json.dumps(query_dict_fallback),
                "f": json.dumps(fields),
                "s": json.dumps(sort),
                "o": json.dumps({
                    "size": max_results,
                    "exclude_withdrawn": True,
                    "pad_patent_id": False
                })
            }
            
            try:
                response_fallback = requests.get(url, headers=headers, params=params_fallback, timeout=30)
                response_fallback.raise_for_status()
                data_fallback = response_fallback.json()
                patents = data_fallback.get("patents", [])
                query_dict = query_dict_fallback  # Update for metadata
            except:
                pass  # If fallback also fails, continue with empty results

        if not patents:
            return json.dumps({
                "error": f"No patents found for keyword '{keyword}'",
                "suggestion": "Try different keywords, broader terms, or check if the search is too specific. The CPC filter may have been too restrictive.",
                "query_used": query_dict,
                "note": "Searched with pharmaceutical CPC filter (A61K, A61P, C07K, C12N) and also tried without filter."
            })

        # Format results and calculate relevance scores
        formatted_patents = []
        keyword_lower = keyword_clean.lower()
        keyword_words_lower = [w.lower() for w in keyword_words]
        
        for patent in patents:
            # Get assignee names (companies/organizations)
            assignees = patent.get("assignees", [])
            assignee_names = [a.get("assignee_organization", "Individual") for a in assignees if a.get("assignee_organization")]
            
            # Get inventor names
            inventors = patent.get("inventors", [])
            inventor_names = [
                f"{inv.get('inventor_name_first', '')} {inv.get('inventor_name_last', '')}".strip()
                for inv in inventors
            ]
            
            # Get CPC classifications (technology categories)
            cpc_groups = patent.get("cpc_group_id", [])
            cpc_titles = patent.get("cpc_group_title", [])
            
            # Calculate relevance score
            title = patent.get("patent_title", "").lower()
            abstract = patent.get("patent_abstract", "").lower()
            
            # Score based on keyword matches
            relevance_score = 0
            if keyword_lower in title:
                relevance_score += 10  # High score for title match
            elif any(word in title for word in keyword_words_lower):
                relevance_score += 5  # Medium score for partial title match
            
            if keyword_lower in abstract:
                relevance_score += 3  # Lower score for abstract match
            elif any(word in abstract for word in keyword_words_lower):
                relevance_score += 1  # Minimal score for partial abstract match
            
            formatted_patents.append({
                "patent_id": patent.get("patent_id"),
                "patent_number": patent.get("patent_number"),
                "title": patent.get("patent_title"),
                "abstract": patent.get("patent_abstract", "")[:500] + "..." if len(patent.get("patent_abstract", "")) > 500 else patent.get("patent_abstract", ""),
                "date": patent.get("patent_date"),
                "type": patent.get("patent_type"),
                "assignees": assignee_names[:3] if assignee_names else ["Individual/Unassigned"],
                "inventors": inventor_names[:3],
                "cpc_classifications": list(zip(cpc_groups[:3], cpc_titles[:3])) if cpc_groups and cpc_titles else [],
                "relevance_score": relevance_score
            })
        
        # Sort by relevance score (highest first), then by date
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

patent_research_agent = Agent(
    name="patent_landscape_agent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    tools=[serper_patent_tool, patents_view_api_tool]
)