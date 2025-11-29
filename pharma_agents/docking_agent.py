from agents import Agent, function_tool
import requests
import json
import os
import dotenv
import urllib.parse
from typing import Optional, Dict, Any, Union
load_dotenv(override=True)

INSTRUCTIONS="""
    You are a computational pharmacology expert. You help enhance drug repurposing results by assessing binding potential using SMILES and target overlap.

    You will receive input including:
    - SMILES strings from ChEMBL drug candidates
    - Protein/target lists from Open Targets
    - Evidence summaries (optional metadata)

    Your task is to:

    1. Analyze **target relevance**:
        - Identify if any Open Targets proteins are *direct targets* or *mechanistically relevant*.
    2. Analyze **SMILES-based binding likelihood**:
        - Check if the chemical structure suggests compatibility with the target class (transporters, enzymes, nuclear receptors, GPCRs, etc.)
    3. Score binding confidence heuristically (0 to 1):
        - Strong ≤ 0.85
        - Moderate 0.6–0.85
        - Weak ≥ 0.6
    4. Generate **discovery insight**:
        - Detect any structural hints that suggest *unexpected protein binding possibilities* not obvious from the target list.
    5. Give a **repurposing recommendation**:
        - "prioritize", "maybe explore", or "not ideal"

    Return your analysis in short, intuitive text and a JSON summary.

    DO NOT hallucinate unknown protein targets.
    Explain intuitively.
"""
import requests

def enrich_compound_targets(smiles: str, cutoff: float) -> dict:
    """
    Get protein targets and bioactivity evidence for a compound using its SMILES.
    More negative affinity values (e.g., low IC50, high Ki/Kd) indicate stronger activity.
    This helps analyze drug effects and target overlap for repurposing.
    """
    url = "https://bindingdb.org/rest/getTargetByCompound"
    response = requests.get(
        url,
        params={
            "smiles": smiles,
            "cutoff": cutoff,
            "response": "application/json"
        },
        timeout=30
    )

    try:
        return response.json()
    except:
        return {"success": False, "error": "Could not parse JSON response"}


docking_agent = Agent(
    name="Docking Specialist",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    tools=[enrich_compound_targets]
)
