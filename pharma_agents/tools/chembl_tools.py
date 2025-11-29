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
    
    Uses ChEMBL API filtering and search endpoints for accurate results.
    """
    drug_name_clean = drug_name.strip()
    
    # Strategy 1: Try exact match on pref_name (case-insensitive)
    # https://www.ebi.ac.uk/chembl/api/data/molecule?pref_name__iexact=metformin
    try:
        url = f"{BASE_URL}/molecule.json"
        params = {"pref_name__iexact": drug_name_clean, "limit": 1}
        
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        
        molecules = data.get("molecules", [])
        if molecules:
            mol = molecules[0]
            print(f"[ChEMBL] Found exact pref_name match: {mol.get('pref_name')}")
            return {
                "chembl_id": mol["molecule_chembl_id"],
                "smiles": mol.get("molecule_structures", {}).get("canonical_smiles"),
                "name": mol.get("pref_name")
            }
    except Exception as e:
        print(f"[ChEMBL] Exact name search error: {e}")
    
    # Strategy 2: Use full-text search endpoint
    # https://www.ebi.ac.uk/chembl/api/data/molecule/search.json?q=metformin
    try:
        url = f"{BASE_URL}/molecule/search.json"
        params = {"q": drug_name_clean, "limit": 20}
        
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        
        molecules = data.get("molecules", [])
        if molecules:
            # Look for exact match in pref_name or synonyms
            drug_name_lower = drug_name_clean.lower()
            
            # First pass: exact pref_name match
            for mol in molecules:
                pref_name = mol.get("pref_name", "")
                if pref_name and pref_name.lower() == drug_name_lower:
                    print(f"[ChEMBL] Found in search results: {pref_name}")
                    return {
                        "chembl_id": mol["molecule_chembl_id"],
                        "smiles": mol.get("molecule_structures", {}).get("canonical_smiles"),
                        "name": pref_name
                    }
            
            # Second pass: check synonyms for exact match
            best_match = None
            best_score = 0
            
            for mol in molecules:
                synonyms = mol.get("molecule_synonyms", [])
                max_phase = mol.get("max_phase") or 0
                
                for syn_entry in synonyms:
                    syn_value = syn_entry.get("molecule_synonym", "")
                    syn_type = syn_entry.get("syn_type", "")
                    
                    if syn_value.lower() == drug_name_lower:
                        # Score: prioritize INN/USAN and approved drugs
                        score = max_phase * 10
                        if syn_type in ["INN", "USAN"]:
                            score += 100
                        elif syn_type == "BAN":
                            score += 50
                        elif syn_type in ["TRADE_NAME", "ATC"]:
                            score += 25
                        else:
                            score += 10
                        
                        if score > best_score:
                            best_score = score
                            best_match = (mol, syn_value)
            
            if best_match:
                mol, matched_name = best_match
                print(f"[ChEMBL] Found synonym match: {matched_name}")
                return {
                    "chembl_id": mol["molecule_chembl_id"],
                    "smiles": mol.get("molecule_structures", {}).get("canonical_smiles"),
                    "name": matched_name
                }
            
            # Third pass: return highest max_phase result
            if molecules:
                sorted_mols = sorted(molecules, key=lambda m: (m.get("max_phase") or 0), reverse=True)
                mol = sorted_mols[0]
                
                # Get best name
                name = mol.get("pref_name")
                if not name:
                    synonyms = mol.get("molecule_synonyms", [])
                    for syn in synonyms:
                        if syn.get("syn_type") in ["INN", "USAN", "BAN"]:
                            name = syn.get("molecule_synonym")
                            break
                    if not name and synonyms:
                        name = synonyms[0].get("molecule_synonym")
                
                print(f"[ChEMBL] Using best match from search: {name}")
                return {
                    "chembl_id": mol["molecule_chembl_id"],
                    "smiles": mol.get("molecule_structures", {}).get("canonical_smiles"),
                    "name": name
                }
    
    except Exception as e:
        print(f"[ChEMBL] Full-text search error: {e}")
    
    print(f"[ChEMBL] No results found for '{drug_name_clean}'")
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
    """
    Fetch mechanism of action data.
    
    Args:
        chembl_id: ChEMBL molecule ID (e.g., CHEMBL1431)
        
    Returns:
        List of mechanism dictionaries containing action type, mechanism description, and target info.
    """
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
        print(f"[ChEMBL] MoA fetch error for {chembl_id}: {e}")
        return []


def chembl_drug_indications(chembl_id: str) -> List[str]:
    """
    Fetch known therapeutic indications.
    
    Args:
        chembl_id: ChEMBL molecule ID
        
    Returns:
        List of indication names (Mesh headings or EFO terms).
    """
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
        print(f"[ChEMBL] Indication fetch error for {chembl_id}: {e}")
        return []


def chembl_drug_warnings(chembl_id: str) -> List[Dict[str, Any]]:
    """
    Fetch safety warnings.
    
    Args:
        chembl_id: ChEMBL molecule ID
        
    Returns:
        List of warning dictionaries.
    """
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
        print(f"[ChEMBL] Safety warning fetch error for {chembl_id}: {e}")
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
