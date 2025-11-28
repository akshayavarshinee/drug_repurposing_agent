"""
Background task processing for long-running agent executions.
"""
import logging
import asyncio
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.agent_service import run_pharma_research, AgentExecutionError
from app.queries.models import Query
from app.results.models import Report
from datetime import datetime

logger = logging.getLogger(__name__)

async def process_query_with_agents(
    query_id: int,
    query_text: str,
    user_id: int
):
    """
    Async background task to process a query using CrewAI agents.
    This allows multiple queries to be processed concurrently.
    
    Args:
        query_id: Database ID of the query
        query_text: The research question
        user_id: ID of the user who submitted the query
    """
    logger.info(f"Async background task started for query {query_id}")
    
    # Create a new database session for this background task
    db = SessionLocal()
    
    try:
        # Update query status to processing
        query = db.query(Query).filter(Query.id == query_id).first()
        if query:
            query.status = "processing"
            query.started_at = datetime.now()
            db.commit()
        
        # Execute the agents asynchronously
        title, report_text = await run_pharma_research(query_text, user_id)
        
        # Create the report
        new_report = Report(
            query_id=query_id,
            user_id=user_id,
            title=title,
            report_text=report_text
        )
        
        db.add(new_report)
        
        # Update query status to completed
        if query:
            query.status = "completed"
            query.completed_at = datetime.now()
        
        db.commit()
        
        logger.info(f"Background task completed successfully for query {query_id}")
        
    except AgentExecutionError as e:
        logger.error(f"Agent execution failed for query {query_id}: {e}")
        
        # Update query status to failed
        query = db.query(Query).filter(Query.id == query_id).first()
        if query:
            query.status = "failed"
            query.error_message = str(e)
            db.commit()
            
    except Exception as e:
        logger.error(f"Unexpected error in background task for query {query_id}: {e}", exc_info=True)
        
        # Update query status to failed
        query = db.query(Query).filter(Query.id == query_id).first()
        if query:
            query.status = "failed"
            query.error_message = f"Unexpected error: {str(e)}"
            db.commit()
    
    finally:
        # Always close the database session
        db.close()
