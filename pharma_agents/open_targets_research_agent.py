import requests
from typing import Optional
from agents import Agent, function_tool

@function_tool
def open_targets_graphql_tool(
    endpoint: str,
    entity_id: Optional[str] = None,
    query_type: str = "basic",
    search_query: Optional[str] = None,
    page_size: int = 10,
    page_index: int = 0
) -> str:
    """Send validated queries to Open Targets (GraphQL) and return structured JSON as string."""
    base_url = "https://api.platform.opentargets.org/api/v4/graphql"
    valid_endpoints = ["target", "disease", "drug", "variant", "studies", "credibleSet", "search"]

    if endpoint not in valid_endpoints:
        return f"Error: Invalid endpoint '{endpoint}'. Valid options: {valid_endpoints}"

    # simplified GraphQL query building
    queries = {
        "target": {
            "basic": """query target($ensemblId:String!){target(ensemblId:$ensemblId){id approvedSymbol}}""",
            "tractability": """query target($ensemblId:String!){target(ensemblId:$ensemblId){id tractability{label value}}}""",
            "associated_diseases": """query target($ensemblId:String!,$size:Int!,$index:Int!){target(ensemblId:$ensemblId){associatedDiseases(page:{size:$size,index:$index}){count rows{disease{id name} score}}}}""",
        },
        "disease": {
            "basic": """query disease($efoId:String!){disease(efoId:$efoId){id name}}""",
            "known_drugs": """query disease($efoId:String!,$size:Int!){disease(efoId:$efoId){knownDrugs(size:$size){count rows{drug{id name} mechanismOfAction phase}}}}""",
        },
        "drug": {
            "basic": """query drug($chemblId:String!){drug(chemblId:$chemblId){id name maximumClinicalTrialPhase hasBeenWithdrawn}}""",
            "mechanisms": """query drug($chemblId:String!){drug(chemblId:$chemblId){mechanismsOfAction{rows{mechanismOfAction actionType targets{id approvedSymbol}}}}}""",
        },
        "search": {
            "basic": """query search($queryString:String!,$size:Int!,$index:Int!){search(queryString:$queryString,page:{size:$size,index:$index}){total hits{id entity name score}}}""",
        }
    }

    if endpoint == "search" and search_query:
        query_string = queries["search"]["basic"]
    elif endpoint in queries and query_type in queries[endpoint]:
        query_string = queries[endpoint][query_type]
    elif endpoint == "target" and query_type == "known_drugs":
        query_string = """query target($ensemblId:String!,$size:Int!){target(ensemblId:$ensemblId){knownDrugs(size:$size){count rows{drug{id name} phase}}}}"""
    else:
        query_string = None

    if not query_string:
        return f"Error: Invalid query_type '{query_type}' for endpoint '{endpoint}'."

    # Build variables
    variables = {}
    if endpoint == "target" and entity_id:
        variables["ensemblId"] = entity_id
    elif endpoint == "disease" and entity_id:
        variables["efoId"] = entity_id
    elif endpoint == "drug" and entity_id:
        variables["chemblId"] = entity_id
    elif endpoint == "search" and search_query:
        variables["queryString"] = search_query

    variables["size"] = page_size
    variables["index"] = page_index

    # Execute request
    try:
        headers = {"User-Agent": "pharma-research-agent/1.0", "Content-Type": "application/json"}
        payload = {"query": query_string, "variables": variables}
        resp = requests.post(base_url, json=payload, headers=headers, timeout=20)
        resp.raise_for_status()
        data = resp.json()

        import json
        result = {
            "data": data.get("data", {}),
            "_query_metadata": {
                "endpoint": endpoint,
                "query_type": query_type,
                "entity_id": entity_id,
                "page": page_index
            }
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"

INSTRUCTIONS=(
    """
    You are a GLOBAL TARGET-DRIVEN DRUG REPURPOSING AGENT powered by real insights from the clinicaltrials.gov
    and Open Targets evidence graph.

    MANDATORY TOOL USAGE:
    - You MUST call `open_targets_graphql_tool` to retrieve real data for:
    ✅ target–disease association scores
    ✅ drug → target links with clinical phase or approval evidence
    ✅ genetic evidence (GWAS, somatic, germline)
    ✅ tractability (druggability) scores
    ✅ any mechanistic or disease-link evidence the tool returns
    - If the tool throws an error, returns empty `rows`, or times out after 2 attempts, stop and summarize gaps.
    - Never invent IDs, genes, scores, or phases.

    --------------------------------
    PRACTICAL REASONING CHAIN (ALWAYS FOLLOW)
    --------------------------------
    When data arrives from tools, you must think like this (and reflect it in your output):

    1. **INPUT → QUERY INTENT**
    - Parse what the user actually wants: global repurposing, specific target, or specific drug focus.

    2. **DRUG → TARGET GENETIC EVIDENCE**
    - Extract *human* targets with strong association scores.
    - Include 1-line potency/context hints only if included in the API response fields.

    3. **TARGET TRACTABILITY & DRUGGABILITY**
    - Extract tractability labels like antibody, small molecule, gene therapy, etc.
    - Convert to practical feasibility bullets:
        (e.g., “Small-molecule tractability present + high genetic evidence = fast repurposing path.”)

    4. **TARGET → DISEASE BIOLOGY OVERLAP**
    - Identify *top 3 disease nodes* the target is linked to if they overlap the query condition.
    - Explain overlap intersection concisely.

    5. **CLINICAL PHASE & REGULATORY CONTEXT**
    - Extract and classify clinical phases, approvals, or withdrawal flags *only if present in data*.
    - Convert them into deployment intelligence signals for repurposing.

    6. **REPURPOSING PRACTICAL MINING**
    From the evidence you gather, identify:
    • under-trialed indications
    • high-failure clinical signals worth subgroup mining
    • mechanistically adjacent but clinically distinct white spaces
    • multi-comorbidity angle viability

    --------------------------------
    EXPECTED OUTPUT (INDUSTRY + ACADEMIC PRACTICAL)
    --------------------------------
    Your answer must include **these sections**, filled ONLY from tool-returned evidence (without JSON):

    1. **Target–Disease Association Table (Top 1–5 rows)**  
    Columns: Target, Disease, Evidence Score, Evidence Type Summary (genetic/literature/etc.)

    2. **Drug–Target Mapping Table (Top 1–5 rows)**  
    Columns: Drug (name or ID if API returns it), Target, Most Advanced Clinical Phase, Approval/Withdrawal Notes

    3. **Target Tractability Snapshot** (3–6 bullet points)  
    Example bullets:
    - “Human genetic evidence strong at a metabolic target with small-molecule tractability — high practical repurposing potential.”
    - “Target associated data type is literature only, no genetic signal — weak repurposing reliability.”

    4. **Repurposing Opportunity Statements** (2–4 bullets max)  
    Each bullet should contain:
    - why it qualifies (based on evidence)
    - what clinical or genetic signals support adjacency
    - practical patient cohort or biomarker lever to validate on
    - feasibility score (0.0–1.0) with justification  
    (*score must reflect real biological + clinical adjacency practicality*)

    5. **Conflicts / Safety Flags** (1–3 lines max if present)
    - “Withdrawn in EU for safety action, target overlaps pancreatic pathway — not practical for metabolic repurposing.”

    6. **Final Repurposing Practical Score** (single float 0.0–1.0 line at end)
    - summarizing *regulatory stability + genetic score strength + tractability + disease overlap practicality*.

    --------------------------------
    NO ACTIONABLE SIGNAL FALLBACK
    --------------------------------
    If after tool calls you still cannot derive strong practical insight:
    Return ONLY this line:
    “No target–disease overlap with actionable evidence through tools. Cannot derive robust practical repurposing insights from Open Targets graph for this query.”

    --------------------------------
    STYLE RULES
    --------------------------------
    - Tone: concise, intuitive, evidence-heavy but non-formal
    - Audience: translational researchers, clinical strategy teams, ML feature consumers
    - Avoid long narratives
    - Tables must reflect ONLY what the tool returned
    - Include practical next steps (experiments or cohort mining) only when signals exist
    - No text outside the structured sections
    """

)

# Create a single Open Targets Reasoning Agent
open_targets_agent_sdk = Agent(
    name="Open Targets Pharma Agent",
    instructions=INSTRUCTIONS,
    tools=[open_targets_graphql_tool],
    model="gpt-4o-mini"
)
