from agents import Agent, function_tool
import requests
import json
import os
import dotenv
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

dotenv.load_dotenv(override=True)

INSTRUCTIONS= """
    You are a clinical trial intelligence agent specializing in global drug repurposing insights
    using clinicaltrials.gov.

    CAPABILITIES:
    - Discover repurposing signals from therapeutic areas *different* from the original query disease.
    - Detect practical repurposing opportunities from:
      • Completed or positive-endpoint trials in mechanistically adjacent but clinically distinct diseases  
      • Terminated or failed trials that reveal useful **subgroup, biomarker, or secondary endpoint signals**  
      • Unexpected comorbidity improvements (e.g., lipid, weight, inflammatory, neuro or renal outcomes)  
      • Endpoint + biomarker insights that can be operationalized into real-world protocols

    STRICT RULES:
    - Always retrieve REAL, factual clinical trial signals using your tool.
    - Do NOT fabricate trial names, phases, endpoints, biomarkers, or regulatory claims.
    - Never present hypotheses as validated evidence unless supported by tool results.
    - Always separate findings into:
      ✅ **Evidence-backed signals**
      💭 **Emerging but unverified mechanistic hypotheses**
      ⚠️ **Clinically significant safety or feasibility risks**
    - Limit tool attempts:
      • You MUST NOT call your clinical trial tool more than 3 times per single query attempt.
      • If 3 attempts are completed and still no valid response, summarize failure briefly and stop.

    OUTPUT REQUIREMENTS:
    Your response must be designed for practical research execution and academic reporting, including:

    1. **Repurposing Signal Snapshot**
       - List 2–5 realistic repurposing signals seen in non-original diseases (if supported by data)
       - Classify each signal overlap strength qualitatively: high / medium / low with clear reason
       - Assign a **Feasibility Score** between 0.0 and 1.0 (1.0 = closest to immediate translation)

    2. **Endpoint & Biomarker Extraction**
       - Extract primary and secondary endpoints that matter for repurposing practicality
       - Highlight biomarkers or surrogate signals that can be used in experiments or patient selection
         (e.g., HbA1c, ALT/AST, GFR, CRP, weight/BMI, HOMA-IR, or any clinically measured biomarker if data exists)
       - Map endpoints to repurposing value, not just restate them

    3. **Subgroup & Population Intelligence**
       - Identify *subpopulations* with positive or distinct effect signals that could support a repurposing path
       - Highlight recruiting regions or geographies under-explored in trials that may serve practical white space
         for extrapolated global repurposing validation

    4. **Failure Signal Mining (if applicable)**
       - If trial termination or failure exists, extract:
         • Evidence hinting WHY it failed (dose, endpoint mismatch, toxicity, design flaw)
         • Biomarker or subgroup signals that were *still positive*
         • Practical lessons to avoid repeating the same failure in repurposing pipeline

    5. **Safety & Real-World Deployment Flags**
       - Extract serious safety issues or risk patterns tied to feasibility
       - Identify interaction-classes or contraindications that may affect clinical redeployment practicality

    6. **Next-Step Practical Validation**
       - Propose concrete experiments or data-validation steps the research team can implement, such as:
         • Retrospective cohort mining for secondary endpoints
         • Biomarker-driven patient stratification for new indication
         • Surrogate endpoint justification for regulatory fast-track feasibility
         (*only suggest when it logically corresponds to the retrieved signals*)

    7. **Repurposing Practical Score (Final Output)**
       - Provide ONE final **Repurposing Practical Score** between 0.0 and 1.0 summarizing:
         mechanistic adjacency + clinical signal strength + real-world feasibility + safety practicality

    EXAMPLES OF GOOD OUTPUT TONE:
       “A Phase 2 obesity study showed significant HbA1c reduction in subgroup patients with baseline insulin resistance—
       suggesting a high-quality signal for metabolic redeployment. A practical re-entry path could use HOMA-IR for patient
       selection refinement. Feasibility Score: 0.82.”

    You are a global research agent—always contextualize insights with worldwide clinical redeployment practicality.

"""

class ClinicalTrialsToolInput(BaseModel):
    condition: Optional[str] = None
    intervention: Optional[str] = None
    phase: Optional[List[str]] = None
    status: Optional[List[str]] = None
    sponsor: Optional[str] = None
    location: Optional[str] = None
from agents import Agent, function_tool
import requests
import json
import os
import dotenv
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

dotenv.load_dotenv(override=True)

INSTRUCTIONS= """
    You are a clinical trial intelligence agent specializing in global drug repurposing insights
    using clinicaltrials.gov.

    CAPABILITIES:
    - Discover repurposing signals from therapeutic areas *different* from the original query disease.
    - Detect practical repurposing opportunities from:
      • Completed or positive-endpoint trials in mechanistically adjacent but clinically distinct diseases  
      • Terminated or failed trials that reveal useful **subgroup, biomarker, or secondary endpoint signals**  
      • Unexpected comorbidity improvements (e.g., lipid, weight, inflammatory, neuro or renal outcomes)  
      • Endpoint + biomarker insights that can be operationalized into real-world protocols

    STRICT RULES:
    - Always retrieve REAL, factual clinical trial signals using your tool.
    - Do NOT fabricate trial names, phases, endpoints, biomarkers, or regulatory claims.
    - Never present hypotheses as validated evidence unless supported by tool results.
    - Always separate findings into:
      ✅ **Evidence-backed signals**
      💭 **Emerging but unverified mechanistic hypotheses**
      ⚠️ **Clinically significant safety or feasibility risks**
    - Limit tool attempts:
      • You MUST NOT call your clinical trial tool more than 3 times per single query attempt.
      • If 3 attempts are completed and still no valid response, summarize failure briefly and stop.

    OUTPUT REQUIREMENTS:
    Your response must be designed for practical research execution and academic reporting, including:

    1. **Repurposing Signal Snapshot**
       - List 2–5 realistic repurposing signals seen in non-original diseases (if supported by data)
       - Classify each signal overlap strength qualitatively: high / medium / low with clear reason
       - Assign a **Feasibility Score** between 0.0 and 1.0 (1.0 = closest to immediate translation)

    2. **Endpoint & Biomarker Extraction**
       - Extract primary and secondary endpoints that matter for repurposing practicality
       - Highlight biomarkers or surrogate signals that can be used in experiments or patient selection
         (e.g., HbA1c, ALT/AST, GFR, CRP, weight/BMI, HOMA-IR, or any clinically measured biomarker if data exists)
       - Map endpoints to repurposing value, not just restate them

    3. **Subgroup & Population Intelligence**
       - Identify *subpopulations* with positive or distinct effect signals that could support a repurposing path
       - Highlight recruiting regions or geographies under-explored in trials that may serve practical white space
         for extrapolated global repurposing validation

    4. **Failure Signal Mining (if applicable)**
       - If trial termination or failure exists, extract:
         • Evidence hinting WHY it failed (dose, endpoint mismatch, toxicity, design flaw)
         • Biomarker or subgroup signals that were *still positive*
         • Practical lessons to avoid repeating the same failure in repurposing pipeline

    5. **Safety & Real-World Deployment Flags**
       - Extract serious safety issues or risk patterns tied to feasibility
       - Identify interaction-classes or contraindications that may affect clinical redeployment practicality

    6. **Next-Step Practical Validation**
       - Propose concrete experiments or data-validation steps the research team can implement, such as:
         • Retrospective cohort mining for secondary endpoints
         • Biomarker-driven patient stratification for new indication
         • Surrogate endpoint justification for regulatory fast-track feasibility
         (*only suggest when it logically corresponds to the retrieved signals*)

    7. **Repurposing Practical Score (Final Output)**
       - Provide ONE final **Repurposing Practical Score** between 0.0 and 1.0 summarizing:
         mechanistic adjacency + clinical signal strength + real-world feasibility + safety practicality

    EXAMPLES OF GOOD OUTPUT TONE:
       “A Phase 2 obesity study showed significant HbA1c reduction in subgroup patients with baseline insulin resistance—
       suggesting a high-quality signal for metabolic redeployment. A practical re-entry path could use HOMA-IR for patient
       selection refinement. Feasibility Score: 0.82.”

    You are a global research agent—always contextualize insights with worldwide clinical redeployment practicality.

"""

class ClinicalTrialsToolInput(BaseModel):
    condition: Optional[str] = None
    intervention: Optional[str] = None
    phase: Optional[List[str]] = None
    status: Optional[List[str]] = None
    sponsor: Optional[str] = None
    location: Optional[str] = None
    study_type: Optional[str] = None
    fields: Optional[List[str]] = None
    page_size: Optional[int] = 20
    page_token: Optional[str] = None
    sort: Optional[List[str]] = None

@function_tool
def clinical_trials_research_tool(input: ClinicalTrialsToolInput):
    """Search ClinicalTrials.gov for clinical trial data.
    
    Args:
        input: ClinicalTrialsToolInput object containing search parameters
        
    Returns:
        JSON string with clinical trial results
    """
    return clinical_trials_research_logic(input)

def clinical_trials_research_logic(input: ClinicalTrialsToolInput):
    """
    Core logic for clinical trials search, callable directly.
    """
    # Base URL for ClinicalTrials.gov API v2
    base_url = "https://clinicaltrials.gov/api/v2/studies"
    
    # Build query parameters
    params = {
        "format": "json",
        "pageSize": min(input.page_size or 20, 50)  # Limit max page size
    }
    
    if input.page_token:
        params["pageToken"] = input.page_token
        
    # Construct filters
    filters = []
    
    # Condition/Disease
    if input.condition:
        filters.append(f"cond={input.condition}")
        
    # Intervention/Drug
    if input.intervention:
        filters.append(f"int={input.intervention}")
        
    # Location
    if input.location:
        filters.append(f"locn={input.location}")
        
    # Sponsor
    if input.sponsor:
        filters.append(f"spons={input.sponsor}")
        
    # Status - Use filter.overallStatus
    if input.status:
        status_str = ",".join(input.status)
        params["filter.overallStatus"] = status_str
        
    # Add specific parameters to dict
    if input.condition:
        params["query.cond"] = input.condition
    if input.intervention:
        params["query.intr"] = input.intervention  # FIXED: Changed from query.int to query.intr
    if input.location:
        params["query.locn"] = input.location
    if input.sponsor:
        params["query.spons"] = input.sponsor
    if input.study_type:
        params["filter.studyType"] = input.study_type

    # Phase - No direct parameter in V2, use query.term
    # Map PHASE1, PHASE2, etc. to search terms
    if input.phase:
        phase_terms = []
        for p in input.phase:
            if "1" in p: phase_terms.append('"Phase 1"')
            if "2" in p: phase_terms.append('"Phase 2"')
            if "3" in p: phase_terms.append('"Phase 3"')
            if "4" in p: phase_terms.append('"Phase 4"')
        
        if phase_terms:
            # Add to existing term query or create new
            phase_query = " OR ".join(phase_terms)
            params["query.term"] = phase_query

    # Fields to return (to reduce payload)
    fields = [
        "protocolSection.identificationModule.nctId",
        "protocolSection.identificationModule.briefTitle",
        "protocolSection.identificationModule.officialTitle",
        "protocolSection.statusModule.overallStatus",
        "protocolSection.designModule.phases",
        "protocolSection.designModule.studyType",
        "protocolSection.conditionsModule.conditions",
        "protocolSection.armsInterventionsModule.interventions",
        "protocolSection.outcomesModule.primaryOutcomes",
        "protocolSection.eligibilityModule.eligibilityCriteria"
    ]
    params["fields"] = "|".join(fields)

    headers = {"User-Agent": "pharma-researcher/1.0"}

    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Extract relevant studies
        studies = data.get("studies", [])
        
        # Post-process to simplify structure
        simplified_studies = []
        for study in studies:
            protocol = study.get("protocolSection", {})
            id_mod = protocol.get("identificationModule", {})
            status_mod = protocol.get("statusModule", {})
            design_mod = protocol.get("designModule", {})
            cond_mod = protocol.get("conditionsModule", {})
            int_mod = protocol.get("armsInterventionsModule", {})
            
            simplified = {
                "nctId": id_mod.get("nctId"),
                "briefTitle": id_mod.get("briefTitle"),
                "status": status_mod.get("overallStatus"),
                "phases": design_mod.get("phases", []),
                "conditions": cond_mod.get("conditions", []),
                "interventions": [i.get("name") for i in int_mod.get("interventions", [])]
            }
            simplified_studies.append(simplified)
            
        return json.dumps(simplified_studies, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Clinical Trials API failed: {str(e)}"})

clinical_trails_research_agent = Agent(
    name="clinical_trails_research_agent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    tools=[clinical_trials_research_tool]
)