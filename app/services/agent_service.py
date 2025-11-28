"""
Agent service layer for integrating pharmaceutical research agents.
"""
import sys
import os
import logging
import asyncio
import re
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class AgentExecutionError(Exception):
    """Custom exception for agent execution failures."""
    pass

def get_pharma_agents_path():
    """Get the path to the pharma_agents module."""
    # Get the project root (parent of app directory)
    current_dir = Path(__file__).resolve()
    # app/services/agent_service.py -> app/services -> app -> project_root
    project_root = current_dir.parent.parent.parent
    
    # Add project root to Python path if not already there
    # This allows importing from both 'pharma_agents' and 'app' packages
    project_root_str = str(project_root)
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)
    
    pharma_agents_path = project_root / "pharma_agents"
    return pharma_agents_path

def extract_disease_from_query(query: str) -> str:
    """
    Extract the disease name from a natural language query.
    Simple heuristic approach.
    """
    # Common patterns
    patterns = [
        r"treat\s+(.*?)(?:\?|$)",
        r"for\s+(.*?)(?:\?|$)",
        r"repurposing\s+.*?\s+for\s+(.*?)(?:\?|$)",
        r"against\s+(.*?)(?:\?|$)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            candidate = match.group(1).strip()
            # Remove common trailing words if captured
            candidate = re.sub(r"\s+(using|with|by).*$", "", candidate)
            if len(candidate) > 2:
                return candidate
                
    # Fallback: return the whole query if it's short, or a generic placeholder
    if len(query) < 50:
        return query
        
    return query  # Pass full query as fallback, agents might handle it

async def run_pharma_research(query: str, user_id: int) -> tuple[str, str]:
    """
    Execute the pharmaceutical research agents with the given query.
    
    Args:
        query: The research question from the user
        user_id: The ID of the user making the request
        
    Returns:
        tuple: (title, report_text) - The generated report title and content
        
    Raises:
        AgentExecutionError: If agent execution fails
    """
    logger.info(f"Starting pharma research for user {user_id}: {query[:100]}...")
    
    try:
        # Ensure pharma_agents module is in path
        get_pharma_agents_path()
        
        # Import orchestrator
        # Note: We import here to avoid top-level import errors if path isn't set
        from pharma_agents.async_orchestrator import run_pipeline
        
        # Extract disease from query
        disease = extract_disease_from_query(query)
        logger.info(f"Extracted disease target: {disease}")
        
        # Run the pipeline
        # Phase 1 -> Phase 2 -> Phase 3 are handled inside run_pipeline
        context = await run_pipeline(disease=disease)
        
        # Check for errors
        if context.errors:
            logger.warning(f"Some agents encountered errors: {context.errors}")
            
        # Extract report
        report_text = context.report
        if not report_text:
            if context.errors:
                raise AgentExecutionError(f"Report generation failed. Errors: {context.errors}")
            else:
                report_text = "Analysis completed but no report was generated. Please check the individual agent outputs."
        
        # Generate title
        title = generate_title_from_query(query)
        
        logger.info(f"Research completed successfully. Report length: {len(report_text)} characters")
        
        return title, report_text
        
    except ImportError as e:
        logger.error(f"Failed to import pharma_agents module: {e}")
        raise AgentExecutionError(
            f"Agent module not found. Please ensure the pharma_agents package is properly installed. Error: {e}"
        )
    except Exception as e:
        logger.error(f"Agent execution failed: {e}", exc_info=True)
        raise AgentExecutionError(f"Failed to execute research agents: {str(e)}")

def generate_title_from_query(query: str, max_length: int = 100) -> str:
    """
    Generate a report title from the user's query.
    
    Args:
        query: The user's research question
        max_length: Maximum length of the title
        
    Returns:
        str: A formatted title
    """
    # Clean up the query
    title = query.strip()
    
    # Add prefix if not already a question
    if not title.endswith('?'):
        title = f"Research Report: {title}"
    else:
        title = f"Analysis: {title}"
    
    # Truncate if too long
    if len(title) > max_length:
        title = title[:max_length - 3] + "..."
    
    return title

def validate_query(query: str) -> bool:
    """
    Validate that the query is suitable for agent processing.
    
    Args:
        query: The user's research question
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not query or not query.strip():
        return False
    
    # Minimum length check
    if len(query.strip()) < 3:
        return False
    
    # Maximum length check (to prevent abuse)
    if len(query) > 1000:
        return False
    
    return True
