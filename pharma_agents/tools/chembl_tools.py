import requests
import urllib.parse
from typing import Optional, List, Dict, Any

BASE_URL = "https://www.ebi.ac.uk/chembl/api/data"

def chembl_search_molecule(drug_name: str) -> Optional[dict]:
    """
    Look up a molecule by name to retrieve:
    - ChEMBL ID
    - Canonical SMILES
    - Preferred name
    """
    search_url = f"{BASE_URL}/molecule?format=json"
    params = {"q": drug_name, "limit": 5}

    try:
        resp = requests.get(search_url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        molecules = data.get("molecules", [])

        for mol in molecules:
            pref_name = mol.get("pref_name")
            if pref_name and pref_name.lower() == drug_name.lower():
                return {
                    "chembl_id": mol["molecule_chembl_id"],
                    "smiles": mol.get("molecule_structures", {}).get("canonical_smiles"),
                    "name": pref_name
                }

        if molecules:
            mol = molecules[0]
            return {
                "chembl_id": mol["molecule_chembl_id"],
                "smiles": mol.get("molecule_structures", {}).get("canonical_smiles"),
                "name": mol.get("pref_name")
            }

    except Exception as e:
        print(f"ChEMBL search error: {e}")

    return None


def chembl_get_molecule(chembl_id: str) -> Optional[Dict[str, Any]]:
    """Fetch molecule metadata by ID."""
    url = f"{BASE_URL}/molecule/{chembl_id}.json"
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        mol = resp.json()
        return {
            "chembl_id": chembl_id,
            "smiles": mol.get("molecule_structures", {}).get("canonical_smiles"),
            "name": mol.get("pref_name")
        }
    except Exception as e:
        print(f"ChEMBL molecule fetch error: {e}")
        return None


def chembl_mechanisms(chembl_id: str) -> List[Dict[str, Any]]:
    """Fetch mechanism of action data."""
    url = f"{BASE_URL}/mechanism.json"
    params = {"molecule_chembl_id": chembl_id, "limit": 50}
    try:
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        return [
            {
                "action_type": m.get("action_type"),
                "mechanism": m.get("mechanism_of_action"),
                "target_chembl_id": m.get("target_chembl_id"),
                "target_name": m.get("target_name")
            }
            for m in data.get("mechanisms", [])
        ]
    except Exception as e:
        print(f"ChEMBL MoA fetch error: {e}")
        return []


def chembl_drug_indications(chembl_id: str) -> List[str]:
    """Fetch known therapeutic indications."""
    url = f"{BASE_URL}/drug_indication.json"
    params = {"molecule_chembl_id": chembl_id, "limit": 50}

    try:
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        return [
            ind.get("mesh_heading") or ind.get("efo_term")
            for ind in data.get("drug_indications", [])
            if ind.get("mesh_heading") or ind.get("efo_term")
        ]
    except Exception as e:
        print(f"ChEMBL indication fetch error: {e}")
        return []


def chembl_drug_warnings(chembl_id: str) -> List[Dict[str, Any]]:
    """Fetch safety warnings."""
    url = f"{BASE_URL}/drug_warning.json"
    params = {"molecule_chembl_id": chembl_id, "limit": 50}
    try:
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        return [
            {
                "warning_type": w.get("warning_type"),
                "warning_class": w.get("warning_class"),
                "warning_description": w.get("warning_description")
            }
            for w in data.get("drug_warnings", [])
        ]
    except Exception as e:
        print(f"ChEMBL safety warning error: {e}")
        return []


def chembl_similarity(smiles: str, threshold: int = 70) -> List[Dict[str, Any]]:
    """Fetch similar drugs from SMILES."""
    if not smiles:
        return []

    s = urllib.parse.quote(smiles, safe="")
    url = f"{BASE_URL}/similarity/{s}/{threshold}.json"

    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        return [
            {
                "chembl_id": m.get("molecule_chembl_id"),
                "similarity": m.get("similarity"),
                "name": m.get("pref_name"),
            }
            for m in data.get("molecules", [])[:10]
        ]
    except Exception as e:
        print(f"ChEMBL similarity error: {e}")
        return []


def chembl_drugs_for_target(target_chembl_id: str) -> List[Dict[str, Any]]:
    """
    Find drugs that modulate a specific target via mechanism endpoint.
    
    Args:
        target_chembl_id: ChEMBL target ID
        
    Returns:
        List of drugs with their action types
    """
    url = f"{BASE_URL}/mechanism.json"
    params = {"target_chembl_id": target_chembl_id, "limit": 50}
    
    try:
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        
        drugs = []
        seen = set()
        for m in data.get("mechanisms", []):
            chembl_id = m.get("molecule_chembl_id")
            if chembl_id and chembl_id not in seen:
                seen.add(chembl_id)
                drugs.append({
                    "chembl_id": chembl_id,
                    "action_type": m.get("action_type"),
                    "mechanism": m.get("mechanism_of_action")
                })
        return drugs
    except Exception as e:
        print(f"ChEMBL drugs for target error: {e}")
        return []
