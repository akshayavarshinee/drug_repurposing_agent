import requests
from typing import Dict, Any, List

def lincs_fetch_molecules(drug_name: str) -> Dict[str, Any]:
    """
    Lookup a molecule in LINCS and return its LSM ID if found.
    This is a simple search endpoint.
    """
    url = "https://lincsportal.ccs.miami.edu/dcic-api/fetchmolecules"
    params = {"searchTerm": drug_name, "limit": 1}

    try:
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()

        if isinstance(data, list) and len(data) > 0:
            mol = data[0]
            return {
                "found": True,
                "LSM": mol.get("LSM_ID"),
                "name": mol.get("NAME")
            }

    except Exception as e:
        print(f"LINCS fetch molecules error: {e}")

    return {"found": False, "LSM": None, "name": None}


def lincs_mechanism_of_action(lsm_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get known mechanisms of action for a LINCS small molecule
    (via /mechanismOfAction endpoint) using LINCS ID parameter 'id=LSM-#'
    """
    if not lsm_id:
        return []

    # Ensure correct LINCS syntax
    if not lsm_id.startswith("LSM-"):
        print("Invalid LSM ID format, must start with 'LSM-'")
        return []

    url = "https://lincsportal.ccs.miami.edu/dcic-api/mechanismOfAction"
    params = {
        "id": lsm_id,
        "limit": limit
    }

    try:
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()

        # Data should be a list
        if isinstance(data, list):
            mechanisms = []
            for m in data:
                mechanisms.append({
                    "mechanism": m.get("MECHANISM"),
                    "moa_term": m.get("MOA_TERM"),
                    "perturbation": m.get("PERTURBATION_TYPE")
                })
            return mechanisms

    except Exception as e:
        print(f"LINCS MoA error: {e}")
    
    return []
