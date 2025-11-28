from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union
from datetime import datetime

class ChemblDrugInsight(BaseModel):
    queried_entity: str = Field(..., description="The drug, target, or disease that was queried")
    
    molecule_ids: List[str] = Field(default_factory=list, description="ChEMBL molecule IDs found")
    target_ids: List[str] = Field(default_factory=list, description="ChEMBL target IDs found")
    
    bioactivity: List[Dict[str, Union[str, float, None]]] = Field(
        default_factory=list,
        description="Extracted bioactivity relationships (Ki, IC50, pChEMBL, etc.)"
    )
    
    drug_indications: List[str] = Field(default_factory=list, description="Known indications if returned")
    mechanisms: List[str] = Field(default_factory=list, description="Mechanisms of action if returned")
    
    warning_flags: List[str] = Field(default_factory=list, description="Safety or withdrawn warnings")
    
    rationale_summary: str = Field(..., description="Agent reasoning summary for repurposing relevance")
    repurposing_candidates: List[str] = Field(default_factory=list, description="2–4 proposed repurposing directions")
    confidence_score: float = Field(..., ge=0, le=1, description="Deterministic confidence from evidence overlap")
    
    generated_on: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Timestamp when the insight object was created"
    )


class Target(BaseModel):
    target_id: str = Field(..., description="Stable target identifier (e.g., Open Targets ENSG or protein accession)")
    symbol: str = Field(..., description="Gene/protein symbol")
    name: str = Field(..., description="Full biological name")
    role_in_disease: str = Field(..., description="Biological role in the disease mechanism")
    evidence_score: float = Field(..., ge=0, le=1, description="Confidence based on literature/known associations")
    sources: List[str] = Field(default_factory=list, description="Where the evidence came from (tools/agents)")
    structure_id: Optional[str] = Field(None, description="PDB or AlphaFold ID if available, added by structure agent")

class DockingEvidence(BaseModel):
    target: str = Field(..., description="Target symbol this docking score corresponds to")
    binding_energy: float = Field(..., description="Docking score in kcal/mol (lower is better)")
    method: str = Field(..., description="Docking engine used (e.g., AutoDock Vina, SwissDock)")
    binding_site: Optional[str] = Field(None, description="Pocket or residue region if determined")
    notes: Optional[str] = Field(None, description="Additional interpretability notes")


class ADMetevidence(BaseModel):
    summary: str = Field(..., description="Pass, Borderline, or Fail based on deterministic rules")
    lipinski_violations: int = Field(..., description="Number of Lipinski rule violations (no ML, rule evaluated)")
    veber_violations: Optional[int] = Field(None, description="Number of Veber rule violations if checked")
    flagged_risks: List[str] = Field(default_factory=list, description="Toxicity or PK concerns flagged by rule/API")
    notes: Optional[str] = Field(None, description="Any extra details from SwissADME/pkCSM")


class ClinicalTrialEvidence(BaseModel):
    has_trials: bool = Field(..., description="True if trials exist for this drug–disease pair")
    highest_phase: Optional[int] = Field(None, description="Highest trial phase found (1,2,3,4)")
    number_of_trials: Optional[int] = Field(None, description="Total trials count found")
    outcome_summary: Optional[str] = Field(None, description="Deterministic summary synthesized by agent")

class PatentEvidence(BaseModel):
    has_recent_patents: bool = Field(..., description="True if patents link drug usage for disease/target")
    patent_density: Optional[int] = Field(None, description="Approximate number of patents found")
    patent_summary: Optional[str] = Field(None, description="Short interpretability summary from agent")

class MarketEvidence(BaseModel):
    market_size: Optional[str] = Field(None, description="Estimated market size or value")
    competitors: List[str] = Field(default_factory=list, description="Competing drugs or therapies")
    regulatory_status: Optional[str] = Field(None, description="FDA/EMA approval status summary")
    pricing_info: Optional[str] = Field(None, description="Pricing or reimbursement information")


class DrugCandidate(BaseModel):
    drug_id: str = Field(..., description="ChEMBL or DrugBank stable drug identifier")
    name: str = Field(..., description="Drug name")
    smiles: Optional[str] = Field(None, description="Canonical SMILES (deterministic structure)")
    status: str = Field(..., description="Approved / Investigational / Withdrawn")
    known_indications: List[str] = Field(default_factory=list, description="Existing medical uses")
    
    # Evidence from simulation + feasibility agents
    docking: Optional[DockingEvidence] = Field(None)
    admet: Optional[ADMetevidence] = Field(None)
    clinical: Optional[ClinicalTrialEvidence] = Field(None)
    patent: Optional[PatentEvidence] = Field(None)
    market: Optional[MarketEvidence] = Field(None)

    mechanism_summary: Optional[str] = Field(None, description="MoA justification generated by reasoning agent")
    final_score: Optional[float] = Field(None, ge=0, le=1, description="Calculated deterministically by integration agent")

class RepurposingResult(BaseModel):
    disease: str = Field(..., description="Disease name used for this run")
    targets: List[Target]
    candidates: List[DrugCandidate]
    
    # Report produced by synthesis agent
    ranked_summary: Optional[str] = Field(None, description="Top N ranked drugs with justification")
    generated_on: Optional[str] = Field(None, description="Timestamp added by orchestrator")

