import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
import traceback
import json
from pydantic import BaseModel
from agents import Runner

# Import agents
from .web_intelligence_research_agent import web_intelligence_agent
from .patent_research_agent import patent_research_agent
from .clinical_trails_research_agent import clinical_trials_agent
from .market_insights_agent import market_insights_agent
from .exim_trade_agent import exim_trade_agent
from .report_generation_agent import report_generation_agent
from .repurposing_interpretation_agent import repurposing_interpretation_agent

# Import unified pipeline tool directly (logic function, not the tool wrapper)
from .tools.unified_repurposing_pipeline import run_repurposing_pipeline_logic


# Results container
class PharmaResearchContext(BaseModel):
    # New pipeline data
    unified_pipeline_data: Optional[Dict[str, Any]] = None
    interpretation: Optional[str] = None
    
    # Contextual data from other agents
    web_intelligence: Optional[str] = None
    patents: Optional[str] = None
    clinical_trials: Optional[str] = None
    market: Optional[str] = None
    exim: Optional[str] = None
    
    # Final output
    report: Optional[str] = None
    errors: Optional[str] = None


# Runner for a single agent (async compatible using executor)
async def run_agent_local(agent, prompt: str, assign_field: str, context: PharmaResearchContext):
    """Run any agent locally using Runner, assign response to container."""
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] → {assign_field} started")
        
        # Run the agent using Runner.run() - this should be synchronous
        def run_sync():
            import inspect
            # result = Runner.run(agent, input=prompt, max_turns=12)
            result = asyncio.run(Runner.run(agent, input=prompt, max_turns=7))
            
            # The result is a RunResult object
            # We need to extract the actual text content, not the string representation
            if hasattr(result, 'final_output'):
                output = result.final_output
                # Check if output is a coroutine and run it if needed
                if inspect.iscoroutine(output):
                    # Create a new event loop to run the coroutine
                    new_loop = asyncio.new_event_loop()
                    try:
                        output = new_loop.run_until_complete(output)
                    finally:
                        new_loop.close()
                # Return the output directly if it's already a string
                if isinstance(output, str):
                    return output
                return str(output) if output is not None else ""
            elif hasattr(result, 'messages') and result.messages:
                last_msg = result.messages[-1]
                content = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
                # Check if content is a coroutine and run it if needed
                if inspect.iscoroutine(content):
                    new_loop = asyncio.new_event_loop()
                    try:
                        content = new_loop.run_until_complete(content)
                    finally:
                        new_loop.close()
                if isinstance(content, str):
                    return content
                return str(content) if content is not None else ""
            else:
                # Check if result itself is a coroutine
                if inspect.iscoroutine(result):
                    new_loop = asyncio.new_event_loop()
                    try:
                        result = new_loop.run_until_complete(result)
                    finally:
                        new_loop.close()
                # If we still have a RunResult object, try to extract final_output
                if hasattr(result, 'final_output'):
                    output = result.final_output
                    if isinstance(output, str):
                        return output
                    return str(output) if output is not None else ""
                # Last resort: convert to string
                return str(result)
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, run_sync)

        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ {assign_field} completed\n")
        setattr(context, assign_field, response)

    except Exception as e:
        error_msg = str(e)
        
        # Special handling for MaxTurnsExceeded - this is often due to tool issues
        if "Max turns" in error_msg or "MaxTurnsExceeded" in str(type(e)):
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ {assign_field} exceeded max turns (agent got stuck in a loop)\n")
            setattr(context, assign_field, f"⚠️ Agent exceeded maximum conversation turns. This usually indicates a tool error or the task was too complex. Please check the agent's tool implementations.")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ {assign_field} crashed: {error_msg}\n")
            setattr(context, assign_field, f"❌ Agent failed: {error_msg}")
        
        error_trace = str(traceback.format_exc())
        context.errors = error_trace if not context.errors else f"{context.errors}\n\n{error_trace}"


# Phase 1: Run Unified Pipeline (Deterministic)
async def run_unified_pipeline(query: str, context: PharmaResearchContext):
    """Run the deterministic unified pipeline tool directly."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] → unified_pipeline started")
    try:
        # Call the tool function directly (it's a python function)
        # Note: run_repurposing_pipeline_logic is the undecorated function
        
        # We need to run this in a thread pool to avoid blocking the async loop
        # since it makes synchronous HTTP requests
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_repurposing_pipeline_logic, query)
        
        context.unified_pipeline_data = result
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ unified_pipeline completed")
        
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ unified_pipeline failed: {e}")
        context.errors = str(e) if not context.errors else f"{context.errors}\n\n{str(e)}"


# Phase 2: Run Interpretation & Context Agents
async def run_analysis_and_context(query: str, context: PharmaResearchContext):
    """Run interpretation agent and other context agents in parallel."""
    print("\n🧬 Phase 2: Running interpretation and context agents...\n")
    
    tasks = []
    
    # 1. Interpretation Agent (analyzes pipeline data)
    if context.unified_pipeline_data:
        # Convert data to string for the agent
        data_str = json.dumps(context.unified_pipeline_data, indent=2)
        # Truncate if too long (simple safety)
        if len(data_str) > 100000:
            data_str = data_str[:100000] + "... (truncated)"
            
        interpretation_prompt = f"""
        Analyze the following enriched drug repurposing data for '{query}':
        
        {data_str}
        
        Provide a detailed interpretation including:
        1. Primary vs Off-target classification
        2. Mechanism of Action relevance
        3. Repurposing opportunities with confidence scores
        4. Safety assessment
        """
        tasks.append(run_agent_local(repurposing_interpretation_agent, interpretation_prompt, "interpretation", context))
    else:
        context.interpretation = "❌ Unified pipeline failed to produce data."
    
    # 2. Context Agents (Web, Patents, Trials, Market, Exim)
    # These run in parallel with interpretation
    tasks.extend([
        run_agent_local(web_intelligence_agent, query, "web_intelligence", context),
        run_agent_local(patent_research_agent, query, "patents", context),
        run_agent_local(clinical_trials_agent, query, "clinical_trials", context),
        run_agent_local(market_insights_agent, query, "market", context),
        run_agent_local(exim_trade_agent, query, "exim", context)
    ])
    
    await asyncio.gather(*tasks)


# Phase 3: Generate final report
async def generate_final_report(disease: str, context: PharmaResearchContext):
    """Generate final report using all collected data."""
    print("\n📘 Phase 3: Generating final report...\n")
    
    prompt_block = f"""
        Synthesize the following global pharmaceutical research findings into a polished executive report for {disease}:

        # SCIENTIFIC & MECHANISTIC VALIDATION (Core Evidence)
        {context.unified_pipeline_data}
        {context.interpretation}

        # GLOBAL CONTEXT
        
        Web Intelligence Findings:
        {context.web_intelligence}

        Patent Prior-Art Insights:
        {context.patents}

        Global Clinical Trial Intelligence:
        {context.clinical_trials}

        Market, Regulatory Approvals, Pricing, Competitors:
        {context.market}

        Export-Import Global Trade Dependency Summary:
        {context.exim}

        Do NOT speculate. If data was missing, summarize the gap briefly.
        Generate a visually structured report with narrative clarity and concise tables.
        Ensure the "Repurposing Practical Score" from the interpretation is highlighted.
    """

    await run_agent_local(report_generation_agent, prompt_block, "report", context)


# Main pipeline
async def run_pipeline(disease: str, drug: Optional[str]=None) -> PharmaResearchContext:
    """Run the full pharmaceutical research pipeline and return results."""
    context = PharmaResearchContext()
    
    # Construct query based on input
    if drug:
        query = drug  # Pipeline A input
        report_subject = f"{drug} (for {disease})"
    else:
        query = disease  # Pipeline B input
        report_subject = disease
        
    print("\n🚀 Starting Pharmaceutical Research Pipeline")
    print(f"Query: {query}")
    print(f"Target Disease: {disease}")
    print("="*80 + "\n")
    
    start = datetime.now()

    # Phase 1: Run Unified Pipeline (Deterministic Data Collection)
    await run_unified_pipeline(query, context)
    
    # Phase 2: Run Interpretation & Context Agents (Parallel)
    # We pass the full query string to context agents
    context_query = f"Gather global intelligence for repurposing {drug} to treat {disease}" if drug else f"Gather global intelligence for drug repurposing options to treat {disease}"
    await run_analysis_and_context(context_query, context)

    # Phase 3: Generate Report
    await generate_final_report(report_subject, context)

    end = datetime.now()
    duration = (end - start).total_seconds()
    print(f"\n✅ Research completed in {duration:.2f} seconds")
    
    return context


if __name__ == "__main__":
    disease_name = "Type 2 Diabetes"
    asyncio.run(run_pipeline(disease_name))
