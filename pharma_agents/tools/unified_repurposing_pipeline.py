from typing import Dict, Any, Tuple, Optional, List
from agents import function_tool
import json
import re

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
# from .europe_pmc_tool import europe_pmc_count

# Import missing agents/tools
from ..clinical_trails_research_agent import clinical_trials_research_logic, ClinicalTrialsToolInput
from ..patent_research_agent import patents_view_api_logic
from ..exim_trade_agent import serper_trade_tool_logic
from ..market_insights_agent import market_insights_tool_logic

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
        "find treatments for ",
        "generate a drug repurposing analysis for "
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
    
    drug_suffixes = ["tide", "mide", "mab", "nib", "vir", "stat", "pril", "ine", "olol", "azole", "mycin", "cycline", "floxacin", "cillin"]
    
    known_drugs = [
        "metformin", "aspirin", "ibuprofen", "paracetamol", "insulin",
        "warfarin", "heparin", "morphine", "codeine", "penicillin",
        "atorvastatin", "simvastatin", "omeprazole", "amoxicillin",
        "lisinopril", "levothyroxine", "azithromycin", "metoprolol",
        "amlodipine", "hydrochlorothiazide", "gabapentin", "sertraline",
        "semaglutide", "thiazolidinedione", "thalidomide"
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
        "clinical_trials": [],
        "patents": [],
        "trade_data": None,
        "market_data": None,
        "_analysis_ready": True
    }

    print(f"[Pipeline A] Step 1: Looking up '{drug}' in ChEMBL...")
    mol = chembl_search_molecule(drug)
    if not mol:
        print(f"[Pipeline A] ❌ Molecule not found in ChEMBL")
        # Proceed with other tools even if ChEMBL fails, using the input name
    else:
        # ✅ Preserve real drug name + identifiers
        result["chembl_id"] = mol["chembl_id"]
        result["smiles"] = mol["smiles"]
        result["drug_name"] = mol["name"]
        print(f"[Pipeline A] ✓ Found: {result['chembl_id']} ({result['drug_name']})")
        print(f"[Pipeline A]   SMILES: {result['smiles'][:50] if result['smiles'] else 'N/A'}...")
    
    if result["smiles"]:
        print(f"[Pipeline A] Step 2: Fetching BindingDB targets...")
        try:
            all_targets = bindingdb_get_targets(result["smiles"], similarity_cutoff=0.85, affinity_cutoff=10.0)
            print(f"[Pipeline A] ✓ Found {len(all_targets)} BindingDB targets")
            # Truncate to top 20 to avoid token limits
            result["bindingdb_all_targets"] = sorted(all_targets, key=lambda x: x.get("affinity_value_uM", 999))[:20]
        except Exception as e:
            print(f"[Pipeline A] ⚠️ BindingDB failed: {e}")

    if result["chembl_id"]:
        print(f"[Pipeline A] Step 3: Fetching mechanisms...")
        try:
            mechanisms = chembl_mechanisms(result["chembl_id"])
            print(f"[Pipeline A] ✓ Found {len(mechanisms)} mechanisms")
            result["chembl_mechanisms"] = mechanisms[:20]
        except Exception as e:
            print(f"[Pipeline A] ⚠️ Mechanisms failed: {e}")
        
        print(f"[Pipeline A] Step 4: Fetching indications...")
        try:
            indications = chembl_drug_indications(result["chembl_id"])
            print(f"[Pipeline A] ✓ Found {len(indications)} indications")
            result["chembl_indications"] = indications[:20]
        except Exception as e:
            print(f"[Pipeline A] ⚠️ Indications failed: {e}")
        
        print(f"[Pipeline A] Step 5: Fetching warnings...")
        try:
            result["chembl_warnings"] = chembl_drug_warnings(result["chembl_id"])
            print(f"[Pipeline A] ✓ Found {len(result['chembl_warnings'])} warnings")
        except Exception as e:
            print(f"[Pipeline A] ⚠️ Warnings failed: {e}")
        
        print(f"[Pipeline A] Step 6: Finding similar drugs...")
        try:
            result["chembl_similar"] = chembl_similarity(result["smiles"], 70)
            print(f"[Pipeline A] ✓ Found {len(result['chembl_similar'])} similar drugs")
        except Exception as e:
            print(f"[Pipeline A] ⚠️ Similarity failed: {e}")

    # --- NEW INTEGRATIONS ---
    
    # 7. Clinical Trials
    print(f"[Pipeline A] Step 7: Fetching Clinical Trials...")
    try:
        ct_input = ClinicalTrialsToolInput(
            intervention=drug,
            status=["RECRUITING", "COMPLETED", "TERMINATED"],
            page_size=5
        )
        ct_results_json = clinical_trials_research_logic(ct_input)
        # Parse JSON string result
        ct_data = json.loads(ct_results_json)
        if isinstance(ct_data, list):
             result["clinical_trials"] = ct_data
        elif isinstance(ct_data, dict) and "studies" in ct_data:
             result["clinical_trials"] = ct_data["studies"]
        else:
             result["clinical_trials"] = ct_data # Fallback
        print(f"[Pipeline A] ✓ Clinical Trials fetched")
    except Exception as e:
        print(f"[Pipeline A] ⚠️ Clinical Trials failed: {e}")

    # 8. Patents
    print(f"[Pipeline A] Step 8: Fetching Patents...")
    try:
        patents_json = patents_view_api_logic(keyword=drug, max_results=5)
        result["patents"] = json.loads(patents_json)
        print(f"[Pipeline A] ✓ Patents fetched")
    except Exception as e:
        print(f"[Pipeline A] ⚠️ Patents failed: {e}")

    # 9. EXIM Trade
    print(f"[Pipeline A] Step 9: Fetching Trade Data...")
    try:
        # Use drug name as HS code proxy for search query
        trade_json = serper_trade_tool_logic(hs_code=drug, year=2024) 
        result["trade_data"] = json.loads(trade_json)
        print(f"[Pipeline A] ✓ Trade Data fetched")
    except Exception as e:
        print(f"[Pipeline A] ⚠️ Trade Data failed: {e}")

    # 10. Market Insights
    print(f"[Pipeline A] Step 10: Fetching Market Insights...")
    try:
        market_json = market_insights_tool_logic(query=f"{drug} sales revenue")
        result["market_data"] = json.loads(market_json)
        print(f"[Pipeline A] ✓ Market Insights fetched")
    except Exception as e:
        print(f"[Pipeline A] ⚠️ Market Insights failed: {e}")

    print(f"[Pipeline A] ✅ Pipeline complete\n")
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
    # Limit to top 5 targets to keep runtime reasonable
    for t in result["disease_targets"][:5]:
        tid = t["target_id"]
        symbol = t["symbol"]
        t_score = t.get("score", 0.0)
        
        # Get drugs for this target
        drugs = chembl_drugs_for_target(tid) or []
        
        # OPTIMIZATION: Limit to top 4 drugs per target to avoid API timeouts
        # (5 targets * 4 drugs = 20 drugs max to enrich)
        for d in drugs[:4]:
            cid = d["chembl_id"]
            if cid not in drug_map:
                drug_map[cid] = {
                    "chembl_id": cid, 
                    "drug_name": None,
                    "smiles": None, 
                    "affinity": [], 
                    "moa": [], 
                    "indications": [], 
                    "warnings": [], 
                    "targets_hit": [{"symbol": symbol, "score": t_score}],
                    "repurposing_score": 0.0
                }
            else:
                # Add target if not already present
                if not any(th["symbol"] == symbol for th in drug_map[cid]["targets_hit"]):
                    drug_map[cid]["targets_hit"].append({"symbol": symbol, "score": t_score})

    print(f"[Pipeline B] Enriching {len(drug_map)} unique drug candidates...")
    
    for i, (cid, info) in enumerate(drug_map.values(), 1):
        print(f"[Pipeline B] Processing candidate {i}/{len(drug_map)}: {cid}")
        
        mol = chembl_get_molecule(cid)
        if not mol:
            continue

        # ✅ FIX: Assign real drug name and SMILES
        info["drug_name"] = mol["name"]
        info["smiles"] = mol["smiles"]

        if info["smiles"]:
            # Get affinity data
            targets = bindingdb_get_targets(info["smiles"], similarity_cutoff=0.9, affinity_cutoff=10.0)
            # Keep top 5 affinities
            info["affinity"] = sorted(targets, key=lambda x: x.get("affinity_value_uM", 999))[:5]
            result["bindingdb_all_targets"].extend(info["affinity"])

        info["moa"] = chembl_mechanisms(cid)
        info["indications"] = chembl_drug_indications(cid)
        info["warnings"] = chembl_drug_warnings(cid)

        # Literature support
        lit_count = 0
        if info.get("drug_name"):
            lit_count = europe_pmc_count(f"{disease} AND {info['drug_name']}")
            result["literature_support"][info["drug_name"]] = lit_count
            
        # --- SCORING LOGIC ---
        # 1. Target Score: Sum of association scores of hit targets
        target_score_sum = sum(t["score"] for t in info["targets_hit"])
        
        # 2. Affinity Bonus: +1 for <1uM, +2 for <0.1uM (max 2 points)
        affinity_bonus = 0
        if info["affinity"]:
            best_aff = min(t.get("affinity_value_uM", 999) for t in info["affinity"])
            if best_aff < 0.1: affinity_bonus = 2.0
            elif best_aff < 1.0: affinity_bonus = 1.0
            
        # 3. Literature Bonus: log-like scale (0-3 points)
        # >0: +0.5, >10: +1.0, >50: +2.0, >100: +3.0
        lit_bonus = 0
        if lit_count > 100: lit_bonus = 3.0
        elif lit_count > 50: lit_bonus = 2.0
        elif lit_count > 10: lit_bonus = 1.0
        elif lit_count > 0: lit_bonus = 0.5
        
        # 4. Safety Penalty: -1 per warning type
        safety_penalty = len(info["warnings"]) * 1.0
        
        # Final Score
        final_score = (target_score_sum * 5) + affinity_bonus + lit_bonus - safety_penalty
        info["repurposing_score"] = round(final_score, 2)
        info["literature_count"] = lit_count

    # Sort candidates by score descending
    sorted_candidates = sorted(drug_map.values(), key=lambda x: x.get("repurposing_score", 0), reverse=True)
    result["chembl_drug_candidates"] = sorted_candidates
    
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
