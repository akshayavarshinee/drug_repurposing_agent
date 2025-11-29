import requests
from typing import List, Dict, Any
from urllib.parse import quote

def bindingdb_get_targets(
    smiles: str, 
    similarity_cutoff: float = 0.85,
    affinity_cutoff: float = 10.0
) -> List[Dict[str, Any]]:
    """
    Fetch protein targets with binding affinity for a small molecule (by SMILES).
    
    This uses the BindingDB getTargetByCompound service which finds structurally
    similar compounds in the database and returns their binding targets.
    
    Args:
        smiles: Canonical SMILES string for the query compound
        similarity_cutoff: Structural similarity threshold (0.0-1.0). Default 0.85.
                          Higher values = more similar compounds only.
        affinity_cutoff: Optional post-filter for affinity values in µM. 
                        Only targets with affinity <= this value are returned.
    
    Returns:
        List of dicts containing targets and affinity values
        
    Example:
        >>> targets = bindingdb_get_targets("CCO", similarity_cutoff=0.9, affinity_cutoff=5.0)
    """
    
    # Use the REST endpoint with JSON response
    # Note: The documentation shows both /axis2/services/BDBService/ and /rest/ endpoints
    # The /rest/ endpoint is simpler and returns JSON directly
    url = "https://bindingdb.org/rest/getTargetByCompound"
    
    # SMILES needs to be URL-encoded
    params = {
        "smiles": smiles,  # requests will handle URL encoding
        "cutoff": similarity_cutoff,  # This is SIMILARITY cutoff (0-1), not affinity
        "response": "application/json"
    }

    targets = []

    try:
        print(f"[BindingDB] Querying with SMILES: {smiles[:50]}... (similarity cutoff: {similarity_cutoff})")
        
        resp = requests.get(url, params=params, timeout=30)
        
        if resp.status_code != 200:
            print(f"[BindingDB] Request failed: HTTP {resp.status_code}")
            if resp.text:
                print(f"[BindingDB] Response: {resp.text[:200]}")
            return targets

        # Handle empty response (no matching compounds)
        if not resp.text or resp.text.strip() == "":
            print(f"[BindingDB] No matching compounds found for given SMILES")
            return targets

        try:
            data = resp.json()
        except ValueError as e:
            print(f"[BindingDB] Invalid JSON response: {e}")
            print(f"[BindingDB] Response text: {resp.text[:200]}")
            return targets

        # The actual response structure is wrapped in "getTargetByCompoundResponse"
        if isinstance(data, dict) and "getTargetByCompoundResponse" in data:
            response_data = data["getTargetByCompoundResponse"]
            affinities = response_data.get("bdb.affinities", [])  # Note: "bdb." prefix!
        elif isinstance(data, dict):
            # Fallback: try direct "affinities" key
            affinities = data.get("affinities", [])
        elif isinstance(data, list):
            affinities = data
        else:
            print(f"[BindingDB] Unexpected response format: {type(data)}")
            return targets

        if not affinities:
            print(f"[BindingDB] No affinity data found in response")
            return targets

        # Parse each affinity entry
        for affinity_entry in affinities:
            # Field names have "bdb." prefix in the actual API response
            affinity_type = affinity_entry.get("bdb.affinity_type", affinity_entry.get("affinity_type", "Unknown"))
            affinity_value_str = affinity_entry.get("bdb.affinity", affinity_entry.get("affinity", ""))
            target_name = affinity_entry.get("bdb.target", affinity_entry.get("target", "Unknown"))
            target_species = affinity_entry.get("bdb.species", affinity_entry.get("species", ""))
            smiles_matched = affinity_entry.get("bdb.smiles", affinity_entry.get("smiles", ""))
            monomerid = affinity_entry.get("bdb.monomerid", affinity_entry.get("monomerid", ""))
            
            # Parse affinity value (may have >, <, or ~ prefix)
            affinity_value_str = str(affinity_value_str).strip()
            
            # Handle inequality operators
            is_approximate = False
            if affinity_value_str.startswith(">") or affinity_value_str.startswith("<"):
                is_approximate = True
                affinity_value_str = affinity_value_str[1:].strip()
            elif affinity_value_str.startswith("~"):
                is_approximate = True
                affinity_value_str = affinity_value_str[1:].strip()
            
            try:
                affinity_value = float(affinity_value_str) if affinity_value_str else 9999.0
            except (ValueError, TypeError):
                affinity_value = 9999.0
            
            # Assume nM if value is very small, otherwise assume µM
            # BindingDB typically reports in nM
            affinity_unit = "nM"  # Most BindingDB values are in nM
            affinity_in_uM = affinity_value / 1000.0  # Convert nM to µM
            
            # Apply affinity cutoff filter (in µM)
            if affinity_in_uM > affinity_cutoff:
                continue
            
            target_entry = {
                "target_name": target_name,
                "target_species": target_species,
                "affinity_type": affinity_type,  # Ki, IC50, Kd, EC50, etc.
                "affinity_value": affinity_value,  # Original value
                "affinity_value_uM": affinity_in_uM,  # Normalized to µM
                "affinity_unit": affinity_unit,
                "is_approximate": is_approximate,  # True if value had >, <, or ~
                "monomerid": monomerid,
                "smiles": smiles_matched  # SMILES of matched compound
            }
            
            targets.append(target_entry)

        print(f"[BindingDB] ✓ Found {len(targets)} target-affinity pairs (after filtering)")
        return targets

    except requests.exceptions.Timeout:
        print(f"[BindingDB] Request timeout after 30 seconds")
        return targets
    except requests.exceptions.RequestException as e:
        print(f"[BindingDB] Request exception: {e}")
        return targets
    except Exception as e:
        print(f"[BindingDB] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return targets

