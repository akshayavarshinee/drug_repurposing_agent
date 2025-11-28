from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.auth.routes import get_current_user
from app.users.models import User
from app.queries.models import Query
from app.results.models import Report
from app.services.agent_service import validate_query, AgentExecutionError
from app.services.background_tasks import process_query_with_agents
import logging
import random

logger = logging.getLogger(__name__)

router = APIRouter()

class QueryCreate(BaseModel):
    question: str

class QueryResponse(BaseModel):
    report_id: int
    message: str

def generate_dummy_report(question: str) -> tuple[str, str]:
    """
    Generate a dummy pharmaceutical research report.
    This will be replaced with real AI agents in the future.
    """
    title = f"Analysis: {question[:50]}..."
    
    dummy_reports = [
        f"""## Executive Summary

The pharmaceutical research regarding "{question}" has been analyzed using multiple data sources and computational models.

## Key Findings

1. **Molecular Structure Analysis**: The compound structure shows promising binding affinity to target receptors.
   
2. **Clinical Trial Data**: Phase II trials indicate a 67% efficacy rate with minimal adverse effects.
   
3. **Drug Repurposing Potential**: Our analysis suggests potential applications in:
   - Cardiovascular disease management
   - Neurological disorder treatment
   - Inflammatory response modulation

## Market Analysis

The global market for similar therapeutic agents is projected to reach $15.2 billion by 2027.

## Recommendations

1. Proceed with Phase III clinical trials
2. Investigate combination therapies
3. Expand patent protection strategies

## Risk Assessment

- Regulatory approval timeline: 18-24 months
- Competition analysis shows 3 similar compounds in development
- Manufacturing scalability score: 8.5/10

---
*This is a placeholder report. Real pharmaceutical data analysis will be implemented in future updates.*
""",
        f"""## Drug Repurposing Analysis

Based on your query: "{question}"

## Computational Screening Results

Our AI-powered screening has identified several potential drug candidates:

### Candidate 1: Compound Alpha-7
- **Mechanism of Action**: GPCR antagonist
- **Current Use**: Hypertension treatment
- **Proposed New Indication**: Neuroprotection
- **Confidence Score**: 92%

### Candidate 2: Compound Beta-3
- **Mechanism of Action**: Kinase inhibitor
- **Current Use**: Oncology
- **Proposed New Indication**: Anti-inflammatory
- **Confidence Score**: 87%

## Molecular Docking Analysis

Binding affinity scores indicate strong target engagement with IC50 values in the nanomolar range.

## Safety Profile

- Established safety data from existing approvals
- No significant drug-drug interactions predicted
- Favorable pharmacokinetic properties

## Next Steps

1. In vitro validation studies
2. Animal model testing
3. Investigational New Drug (IND) application

---
*Generated report based on computational predictions. Requires experimental validation.*
"""
    ]
    
    report_text = random.choice(dummy_reports)
    
    return title, report_text

@router.post("/submit", response_model=QueryResponse)
async def submit_query(
    query_data: QueryCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a pharmaceutical research query.
    Creates a query record and starts agent processing in the background.
    """
    # Validate query
    if not validate_query(query_data.question):
        raise HTTPException(
            status_code=400,
            detail="Invalid query. Please provide a meaningful research question (10-1000 characters)."
        )
    
    logger.info(f"User {current_user.id} submitted query: {query_data.question[:100]}...")
    
    # Create query record with pending status
    new_query = Query(
        user_id=current_user.id,
        question=query_data.question,
        status="pending"
    )
    
    db.add(new_query)
    db.commit()
    db.refresh(new_query)
    
    # Start async background task to process with agents
    # FastAPI's BackgroundTasks can handle async functions
    background_tasks.add_task(
        process_query_with_agents,
        query_id=new_query.id,
        query_text=query_data.question,
        user_id=current_user.id
    )
    
    logger.info(f"Query {new_query.id} created, background processing started")
    
    return QueryResponse(
        report_id=new_query.id,  # Return query ID for status checking
        message="Query submitted successfully. Processing with AI agents..."
    )

@router.get("/status/{query_id}")
async def get_query_status(
    query_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check the status of a query.
    Returns the current processing status and report if completed.
    """
    query = db.query(Query).filter(
        Query.id == query_id,
        Query.user_id == current_user.id
    ).first()
    
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    
    response = {
        "query_id": query.id,
        "status": query.status,
        "question": query.question,
        "created_at": query.created_at,
        "started_at": query.started_at,
        "completed_at": query.completed_at
    }
    
    # If completed, include report ID
    if query.status == "completed" and query.report:
        response["report_id"] = query.report.id
        response["title"] = query.report.title
    
    # If failed, include error message
    if query.status == "failed":
        response["error_message"] = query.error_message
    
    return response

