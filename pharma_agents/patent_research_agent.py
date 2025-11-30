from agents import Agent, function_tool
import requests
import json
import os
from typing import Optional, Dict, Any, Union
import dotenv
import re

dotenv.load_dotenv(override=True)

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

    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return json.dumps({"error": f"Serper Patent Search failed: {str(e)}"})


@function_tool
def patents_view_api_tool(
    keyword: str,
    max_results: int = 25,
    from_date: Optional[str] = None
) -> str:
    """
    Search for pharmaceutical and biotech patents using keywords.
    
    Args:
        keyword: Keywords to search for in patent titles and abstracts 
        max_results: Maximum number of patents to return (default 25, max 100)
        from_date: Filter patents from this date onwards (YYYY-MM-DD format)
    
    Returns:
        JSON string with patent results and metadata
    """
    return patents_view_api_logic(keyword, max_results, from_date)


# def patents_view_api_logic(
#     keyword: str,
#     max_results: int = 25,
#     from_date: Optional[str] = None
# ) -> str:
#     """
#     Core logic for patent search, callable directly.
#     """
#     # Validate inputs
#     if not keyword or not keyword.strip():
#         return json.dumps({"error": "Keyword is required and cannot be empty"})
    
#     max_results = min(max_results or 25, 100)

#     # API Key
#     api_key = os.getenv("PATENTS_VIEW_API_KEY")
#     if not api_key:
#         return json.dumps({
#             "error": "Missing PATENTS_VIEW_API_KEY environment variable. Please set it in your .env file."
#         })

#     # Parse keyword
#     keyword_clean = keyword.strip()
#     keyword_words = keyword_clean.split()
    
#     # Determine search strategy
#     if len(keyword_words) == 1:
#         text_operator = "_text_phrase"
#     elif len(keyword_words) <= 3:
#         text_operator = "_text_phrase"
#     else:
#         text_operator = "_text_all"
    
#     # Main search conditions - NO CPC FILTERING (causes 400/500 errors)
#     main_search_conditions = [
#         {text_operator: {"patent_title": keyword_clean}},
#         {text_operator: {"patent_abstract": keyword_clean}}
#     ]
    
#     # Build query structure
#     query_parts = []
    
#     # Add main search (title OR abstract must contain keywords)
#     query_parts.append({"_or": main_search_conditions})
    
#     # Add date filter if provided
#     if from_date:
#         query_parts.append({"_gte": {"patent_date": from_date}})
    
#     # Combine all conditions with AND
#     if len(query_parts) == 1:
#         query_dict = query_parts[0]
#     else:
#         query_dict = {"_and": query_parts}

#     # API endpoint
#     url = "https://search.patentsview.org/api/v1/patent"

#     # Fields to return - focus on pharmaceutical-relevant info
#     # Use cpc_current instead of cpc_group_id/title
#     fields = [
#         "patent_id",
#         "patent_number",
#         "patent_title",
#         "patent_abstract",
#         "patent_date",
#         "patent_type",
#         "patent_kind",
#         "assignees",
#         "inventors",
#         "cpc_current"
#     ]

#     # Sort by relevance: prioritize patents with keywords in title, then by date
#     sort = [{"patent_date": "desc"}]

#     # Build request params
#     params = {
#         "q": json.dumps(query_dict),
#         "f": json.dumps(fields),
#         "s": json.dumps(sort),
#         "o": json.dumps({
#             "size": max_results,
#             "exclude_withdrawn": True,
#             "pad_patent_id": False
#         })
#     }

#     # Headers
#     headers = {
#         "User-Agent": "pharma-researcher/1.0",
#         "Content-Type": "application/json",
#         "Accept": "application/json",
#         "X-Api-Key": api_key
#     }

#     try:
#         # Request without CPC filtering
#         response = requests.get(url, headers=headers, params=params, timeout=30)
        
#         if response.status_code != 200:
#             return json.dumps({
#                 "error": f"API Error {response.status_code}",
#                 "details": response.text
#             })
            
#         data = response.json()
#         patents = data.get("patents", [])
        
#         # Post-process to extract CPC codes from nested structure
#         processed_patents = []
#         for p in patents:
#             # Extract CPC codes from cpc_current list of objects
#             cpc_list = p.get("cpc_current", [])
#             cpc_codes = []
#             if cpc_list:
#                 # Extract group_id from each object
#                 cpc_codes = [item.get("cpc_group_id") for item in cpc_list if item.get("cpc_group_id")]
            
#             # Create clean patent object
#             clean_p = {
#                 "patent_id": p.get("patent_id"),
#                 "patent_number": p.get("patent_number"),
#                 "title": p.get("patent_title"),
#                 "abstract": p.get("patent_abstract"),
#                 "date": p.get("patent_date"),
#                 "assignees": [a.get("assignee_organization") for a in p.get("assignees", []) if a.get("assignee_organization")],
#                 "inventors": [f"{i.get('inventor_first_name')} {i.get('inventor_last_name')}" for i in p.get("inventors", [])],
#                 "cpc_codes": cpc_codes[:5] # Limit to top 5 codes
#             }
#             processed_patents.append(clean_p)
            
#         return json.dumps({"patents": processed_patents, "count": len(processed_patents)}, indent=2)

#     except Exception as e:
#         return json.dumps({"error": f"Unexpected error: {str(e)}"})

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

patent_research_agent = Agent(
    name="patent_landscape_agent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    tools=[serper_patent_tool, patents_view_api_tool]
)