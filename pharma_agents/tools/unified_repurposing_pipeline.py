from typing import Dict, Any, Tuple, Optional, List
from agents import function_tool

# Import all required tool functions
from .chembl_tools import (
    chembl_search_molecule,
    chembl_get_molecule,
    chembl_mechanisms,
    chembl_drug_indications,
    chembl_drug_warnings,
    chembl_similarity,
    chembl_drugs_for_target
)
from .bindingdb_tool import bindingdb_get_targets
from .lincs_tools import lincs_fetch_molecules, lincs_mechanism_of_action
from .europe_pmc_tool import europe_pmc_count

def detect_input_type(query: str) -> Tuple[str, str]:
    """Detect input type and extract core name."""
    clean = query.strip()
    
    # Remove common instruction phrases at the start
    instruction_prefixes = [
        "provide a review on ",
        "give me information about ",
        "tell me about ",
        "research ",
        "analyze ",
        "find drugs for ",
        "find treatments for "
    ]
    
    for prefix in instruction_prefixes:
        if clean.lower().startswith(prefix):
            clean = clean[len(prefix):].strip()
            break
    
    # Remove everything after separator words
    separators = [" including ", ", and ", " with ", " for "]
    for sep in separators:
        if sep in clean.lower():
            idx = clean.lower().find(sep)
            clean = clean[:idx].strip()
            break
    
    # Get first word for drug detection
    word = clean.split()[0].strip(",.:;!?")
    
    drug_suffixes = ["mab", "nib", "vir", "stat", "pril", "ine", "olol", "azole", "mycin", "cycline", "floxacin", "cillin"]
    
    known_drugs = [
        "metformin", "aspirin", "ibuprofen", "paracetamol", "insulin",
        "warfarin", "heparin", "morphine", "codeine", "penicillin",
        "atorvastatin", "simvastatin", "omeprazole", "amoxicillin",
        "lisinopril", "levothyroxine", "azithromycin", "metoprolol",
        "amlodipine", "hydrochlorothiazide", "gabapentin", "sertraline"
    ]

    if word.lower() in known_drugs or any(word.lower().endswith(s) for s in drug_suffixes):
        return "drug", word

    return "disease", clean


def execute_drug_pipeline(drug: str) -> dict:
    """Drug enrichment pipeline."""
    print(f"\n[Pipeline A] Starting drug enrichment for: {drug}")
    
    result = {
        "input_type": "drug",
        "query": drug,
        "drug_name": drug,
        "chembl_id": None,
        "smiles": None,
        "bindingdb_all_targets": [],
        "chembl_mechanisms": [],
        "chembl_indications": [],
        "chembl_warnings": [],
        "chembl_similar": [],
        "lincs_moa": {},
        "_analysis_ready": True
    }

    print(f"[Pipeline A] Step 1: Looking up '{drug}' in ChEMBL...")
    mol = chembl_search_molecule(drug)
    if not mol:
        print(f"[Pipeline A] ❌ Molecule not found in ChEMBL")
        return result

    # ✅ Preserve real drug name + identifiers
    result["chembl_id"] = mol["chembl_id"]
    result["smiles"] = mol["smiles"]
    result["drug_name"] = mol["name"]
    print(f"[Pipeline A] ✓ Found: {result['chembl_id']} ({result['drug_name']})")
    print(f"[Pipeline A]   SMILES: {result['smiles'][:50] if result['smiles'] else 'N/A'}...")
    
    if result["smiles"]:
        print(f"[Pipeline A] Step 2: Fetching BindingDB targets...")
        result["bindingdb_all_targets"] = bindingdb_get_targets(result["smiles"], cutoff=10.0)
        print(f"[Pipeline A] ✓ Found {len(result['bindingdb_all_targets'])} BindingDB targets")

    if result["chembl_id"]:
        print(f"[Pipeline A] Step 3: Fetching mechanisms...")
        result["chembl_mechanisms"] = chembl_mechanisms(result["chembl_id"])
        print(f"[Pipeline A] ✓ Found {len(result['chembl_mechanisms'])} mechanisms")
        
        print(f"[Pipeline A] Step 4: Fetching indications...")
        result["chembl_indications"] = chembl_drug_indications(result["chembl_id"])
        print(f"[Pipeline A] ✓ Found {len(result['chembl_indications'])} indications")
        
        print(f"[Pipeline A] Step 5: Fetching warnings...")
        result["chembl_warnings"] = chembl_drug_warnings(result["chembl_id"])
        print(f"[Pipeline A] ✓ Found {len(result['chembl_warnings'])} warnings")
        
        print(f"[Pipeline A] Step 6: Finding similar drugs...")
        result["chembl_similar"] = chembl_similarity(result["smiles"], 70)
        print(f"[Pipeline A] ✓ Found {len(result['chembl_similar'])} similar drugs")

    print(f"[Pipeline A] Step 7: Checking LINCS...")
    lincs = lincs_fetch_molecules(drug)
    if lincs.get("found") and lincs.get("LSM"):
        result["lincs_moa"] = lincs_mechanism_of_action(lincs["LSM"])
        print(f"[Pipeline A] ✓ Found LINCS data")
    else:
        print(f"[Pipeline A] ⚠ LINCS data not available")

    print(f"[Pipeline A] ✅ Pipeline complete\n")
    return result

    return result


def execute_disease_pipeline(disease: str) -> dict:
    """Disease enrichment pipeline."""
    result = {
        "input_type": "disease",
        "query": disease,
        "disease_name": disease,
        "disease_targets": [],
        "chembl_drug_candidates": [],
        "bindingdb_all_targets": [],
        "literature_support": {},
        "_analysis_ready": True
    }

    from .open_targets_tool import open_targets_disease_lookup
    targets = open_targets_disease_lookup(disease, limit=10)
    if not targets:
        return result

    # ✅ FIX: Preserve all real Open Targets scores properly
    result["disease_targets"] = [
        {"target_id": t["target_id"], "symbol": t["symbol"], "score": t.get("association_score", 0.0)}
        for t in targets if t.get("target_id")
    ]

    # ✅ FIX: Build enriched drug map with real names, not None
    drug_map = {}
    for t in result["disease_targets"][:5]:
        tid = t["target_id"]
        symbol = t["symbol"]
        drugs = chembl_drugs_for_target(tid) or []
        for d in drugs[:10]:
            cid = d["chembl_id"]
            if cid not in drug_map:
                drug_map[cid] = {"chembl_id": cid, "symbol": None, "smiles": None, "affinity": [], "moa": [], "indications": [], "warnings": [], "targets_hit": [symbol]}
            else:
                drug_map[cid]["targets_hit"].append(symbol)

    for info in drug_map.values():
        mol = chembl_get_molecule(info["chembl_id"])
        if not mol:
            continue

        # ✅ FIX: Assign real drug name and SMILES
        info["drug_name"] = mol["name"]
        info["smiles"] = mol["smiles"]

        if info["smiles"]:
            targets = bindingdb_get_targets(info["smiles"], cutoff=10.0)
            info["affinity"] = targets
            result["bindingdb_all_targets"].extend(targets)

        info["moa"] = chembl_mechanisms(info["chembl_id"])
        info["indications"] = chembl_drug_indications(info["chembl_id"])
        info["warnings"] = chembl_drug_warnings(info["chembl_id"])

        if info.get("drug_name"):
            lincs = lincs_fetch_molecules(info["drug_name"])
            if lincs.get("found") and lincs.get("LSM"):
                info["lincs_moa"] = lincs_mechanism_of_action(lincs["LSM"])

        # ✅ FIX: Proper PMC query using real drug name
        if info.get("drug_name"):
            result["literature_support"][info["drug_name"]] = europe_pmc_count(f"{disease} AND {info['drug_name']}")

    result["chembl_drug_candidates"] = list(drug_map.values())
    return result


def run_repurposing_pipeline_logic(query: str) -> dict:
    """
    Core pipeline logic (undecorated) for direct orchestrator calls.
    """
    input_type, entity = detect_input_type(query)
    if input_type == "drug":
        return execute_drug_pipeline(entity)
    return execute_disease_pipeline(entity)


@function_tool
def run_repurposing_pipeline(query: str) -> dict:
    """
    Decorated tool wrapper for agent usage.
    Execute complete drug repurposing pipeline.
    Automatically detects if input is drug or disease and runs appropriate workflow.
    
    Args:
        query: Drug name or disease name
    
    Returns:
        Complete enriched data dictionary with all findings
    """
    return run_repurposing_pipeline_logic(query)
