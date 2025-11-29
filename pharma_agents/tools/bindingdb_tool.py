import requests
from typing import List, Dict, Any

def bindingdb_get_targets(smiles: str, cutoff: float = 10.0) -> List[Dict[str, Any]]:
    """
    Fetch all human protein targets with binding affinity for a small molecule (by SMILES)
    and return them as raw records with affinity values filtered by cutoff (µM).
    
    Args:
        smiles: Canonical SMILES string
        cutoff: Max affinity value allowed in µM
    
    Returns:
        List of dicts containing targets and affinity values (no classification, raw)
    """
    
    url = "https://bindingdb.org/rest/getTargetByCompound"
    params = {
        "smiles": smiles,
        "cutoff": cutoff,
        "response": "application/json"
    }

    targets = []

    try:
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code != 200:
            print(f"BindingDB request failed with status {resp.status_code}")
            return targets

        data = resp.json()

        # Validate key exists
        affinities = data.get("affinities")
        if not affinities:
            print("No 'affinities' key or no data found in BindingDB")
            return targets

        # Parse each affinity block
        for affinity in affinities:
            target_data_blocks = affinity.get("target_data", [])
            
            for target_block in target_data_blocks:
                # Many entries contain multiple affinity reads for same target,
                # So collect them individually
                target_entry = {
                    "target": target_block.get("target_name"),
                    "uniprot_id": target_block.get("uniprot_id"),
                    "affinity_type": affinity.get("affinity_type"),  # Ki, IC50, Kd, etc
                    "affinity_value": float(affinity.get("affinity", 9999)),  # numeric µM
                    "affinity_unit": affinity.get("affinity_unit"),  # µM, nM, etc
                    "source": affinity.get("source"),  # PubMed or BindingDB source
                    "species": target_block.get("target_species")  # validate human or not
                }

                targets.append(target_entry)

        # Return the full raw target list
        return targets

    except Exception as e:
        print(f"BindingDB error: {e}")
        return targets
