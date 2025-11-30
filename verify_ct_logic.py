import requests
import json
from typing import Optional, List, Dict, Any

# Mock input class
class ClinicalTrialsToolInput:
    def __init__(self, condition=None, intervention=None, phase=None, status=None, 
                 sponsor=None, location=None, study_type=None, fields=None, 
                 page_size=20, page_token=None, sort=None):
        self.condition = condition
        self.intervention = intervention
        self.phase = phase
        self.status = status
        self.sponsor = sponsor
        self.location = location
        self.study_type = study_type
        self.fields = fields
        self.page_size = page_size
        self.page_token = page_token
        self.sort = sort

def clinical_trials_research_logic(input):
    print(f"Testing with: Condition={input.condition}, Status={input.status}, Phase={input.phase}")
    
    url = "https://clinicaltrials.gov/api/v2/studies"

    # Extract values from input
    condition = input.condition
    intervention = input.intervention
    phase = input.phase
    status = input.status
    sponsor = input.sponsor
    location = input.location
    study_type = input.study_type
    fields = input.fields
    page_size = input.page_size or 20
    page_token = input.page_token
    sort = input.sort

    params: Dict[str, Any] = {
        "format": "json",
        "pageSize": min(max(page_size, 1), 1000)
    }

    # -----------------------------
    # Query parameters
    # -----------------------------
    if condition:
        params["query.cond"] = condition

    if intervention:
        params["query.intr"] = intervention

    if sponsor:
        params["query.lead"] = sponsor

    if location:
        params["query.locn"] = location

    if study_type:
        params["query.type"] = study_type

    # Handle Phase via query.term (as there is no direct filter)
    if phase:
        # Map standard enum phases to readable search terms
        phase_map = {
            "EARLY_PHASE1": "Early Phase 1",
            "PHASE1": "Phase 1",
            "PHASE2": "Phase 2",
            "PHASE3": "Phase 3",
            "PHASE4": "Phase 4"
        }
        # Convert input phases to search terms, defaulting to original string if not in map
        phase_terms = [f'"{phase_map.get(p.upper(), p)}"' for p in phase]
        if phase_terms:
            # Use OR logic for multiple phases
            phase_query = f"({' OR '.join(phase_terms)})"
            params["query.term"] = phase_query

    # -----------------------------
    # Filters
    # -----------------------------
    if status:
        # Use the dedicated parameter for status
        params["filter.overallStatus"] = status

    # -----------------------------
    # Field selection
    # -----------------------------
    if fields:
        params["fields"] = ",".join(fields)

    # Pagination
    if page_token:
        params["pageToken"] = page_token

    # Sorting
    if sort:
        params["sort"] = ",".join(sort)

    # Must have at least one search parameter
    if not any([condition, intervention, sponsor, location, study_type, phase, status]):
        return {"error": "At least one search parameter must be provided"}

    headers = {"User-Agent": "pharma-researcher/1.0"}

    # -----------------------------
    # Execute request
    # -----------------------------
    try:
        print(f"Request Params: {json.dumps(params, indent=2)}")
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        result = {
            "_query_metadata": {
                "condition": condition,
                "intervention": intervention,
                "phase": phase,
                "status": status,
                "sponsor": sponsor,
                "location": location,
                "study_type": study_type,
                "fields": fields,
                "page_size": page_size,
                "total_count": data.get("totalCount"),
                "returned": len(data.get("studies", [])),
                "next_page_token": data.get("nextPageToken")
            }
        }

        result.update(data)
        return result

    except requests.exceptions.HTTPError as e:
        return {
            "error": f"ClinicalTrials.gov API HTTP {e.response.status_code}",
            "details": e.response.text[:500],
            "params": params
        }

    except Exception as e:
        return {
            "error": f"Unexpected error: {str(e)}",
            "params": params
        }

def verify():
    # Test 1: Status only
    inp1 = ClinicalTrialsToolInput(condition="Diabetes", status=["RECRUITING"], page_size=5)
    res1 = clinical_trials_research_logic(inp1)
    print(f"Result 1 Studies: {res1.get('_query_metadata', {}).get('returned')}")
    print("-" * 50)

    # Test 2: Phase only
    inp2 = ClinicalTrialsToolInput(condition="Diabetes", phase=["PHASE2"], page_size=5)
    res2 = clinical_trials_research_logic(inp2)
    print(f"Result 2 Studies: {res2.get('_query_metadata', {}).get('returned')}")
    print("-" * 50)

    # Test 3: Both
    inp3 = ClinicalTrialsToolInput(condition="Diabetes", status=["RECRUITING"], phase=["PHASE3"], page_size=5)
    res3 = clinical_trials_research_logic(inp3)
    print(f"Result 3 Studies: {res3.get('_query_metadata', {}).get('returned')}")
    print("-" * 50)

if __name__ == "__main__":
    verify()
