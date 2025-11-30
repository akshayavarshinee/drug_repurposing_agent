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
