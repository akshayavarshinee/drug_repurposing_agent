import math
from typing import List, Dict, Any

def calculate_repurposing_score(
    target_overlap: float,
    potency_confidence: float = None,
    moa_relevance: float = 0.0,
    literature_count: int = 0,
    safety_flags: List[Dict[str, Any]] = None,
    bindingdb_targets: List[dict] = None
) -> float:
    """
    Deterministic weighted scoring for drug repurposing (pure rule-based).
    
    Weights:
    - Target overlap: 30%
    - Binding potency confidence: 30% (auto-computed if bindingdb_targets provided)
    - Mechanism (MoA) relevance: 20%
    - Literature support: 10%
    - Safety feasibility: 10% (inverse risk, capped)
    
    Args:
        target_overlap: 0 to 1 (higher = better disease-target biological overlap)
        potency_confidence: 0 to 1 if supplied externally (optional)
        moa_relevance: 0 to 1 (higher = MoA matches disease biology)
        literature_count: integer count of papers supporting target/disease/drug links
        safety_flags: list of safety warning dicts from ChEMBL
        bindingdb_targets: raw target affinity list from BindingDB for auto potency scoring
    Returns:
        float 0.0 to 1.0
    """

    # Auto-calc potency confidence if BindingDB targets are passed
    if potency_confidence is None and bindingdb_targets:
        potency_confidence = normalize_potency_confidence(bindingdb_targets)

    # Normalize literature using log10 scale
    # ensures 100 papers ≈ 0.66, 1000 ≈ 1.0 (capped)
    if literature_count:
        lit_score = min(1.0, math.log10(literature_count + 1) / 3.0)
    else:
        lit_score = 0.0

    # Compute safety feasibility (inverse), cap safety risk at 1.0 before invert
    if safety_flags:
        safety_risk = min(1.0, accumulate_safety_risk(safety_flags))
        safety_score = 1.0 - safety_risk
    else:
        safety_score = 1.0  # No warnings = safest

    # Weighted scoring
    final_score = (
        0.30 * target_overlap +
        0.30 * (potency_confidence or 0.0) +
        0.20 * moa_relevance +
        0.10 * lit_score +
        0.10 * safety_score
    )

    # Bound & round
    return round(min(1.0, max(0.0, final_score)), 3)


def accumulate_safety_risk(flags: List[Dict[str, Any]]) -> float:
    """Accumulate safety risk from warning entries (deterministic, capped at 1.0)."""
    risk = 0.0
    
    for f in flags:
        warning_type = f.get("warning_type", "").lower()
        warning_class = f.get("warning_class", "").lower()

        if warning_type in ["withdrawn", "black_box"]:
            risk += 0.5
        elif "severe" in warning_class:
            risk += 0.3
        elif warning_type in ["warning", "caution"]:
            risk += 0.1

    return min(1.0, risk)


def normalize_potency_confidence(targets: List[dict]) -> float:
    """
    Determine binding potency confidence.
    Lower IC50/Ki = richer, truer signal.
    """
    if not targets:
        return 0.0

    scores = []
    for t in targets:
        val = t.get("affinity_value")
        unit = (t.get("affinity_unit") or "nm").lower()

        if val is None:
            continue

        # Convert to nM standard internally
        value_nm = val
        if unit == "um" or unit == "µm":
            value_nm = val * 1000
        elif unit == "mm":
            value_nm = val * 1e6

        if value_nm < 10:
            scores.append(1.0)
        elif value_nm < 100:
            scores.append(0.8)
        elif value_nm < 1000:
            scores.append(0.6)
        elif value_nm < 10000:
            scores.append(0.3)
        else:
            scores.append(0.1)

    return round(sum(scores) / len(scores), 3) if scores else 0.0
