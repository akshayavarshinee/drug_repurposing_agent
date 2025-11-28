import asyncio
from typing import Optional
from datetime import datetime
import traceback
from pydantic import BaseModel
from agents import Runner

# Import agents
from .web_intelligence_research_agent import web_intelligence_agent
from .patent_research_agent import patent_research_agent
from .clinical_trails_research_agent import clinical_trials_agent
from .chembl_research_agent import chembl_insights_agent
from .open_targets_research_agent import open_targets_agent_sdk
from .market_insights_agent import market_insights_agent
from .exim_trade_agent import exim_trade_agent
from .disease_pathway_agent import disease_pathway_agent
from .repurposing_strategy_agent import repurposing_strategy_agent
from .report_generation_agent import report_generation_agent


# Results container
class PharmaResearchContext(BaseModel):
    web_intelligence: Optional[str] = None
    patents: Optional[str] = None
    clinical_trials: Optional[str] = None
    chembl: Optional[str] = None
    open_targets: Optional[str] = None
    market: Optional[str] = None
    exim: Optional[str] = None
    pathway: Optional[str] = None
    strategy: Optional[str] = None
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


# Phase 1: Run data collectors in parallel
async def run_parallel_collectors(disease: str, context: PharmaResearchContext, drug: Optional[str]=None):
    """Launch all data collectors concurrently."""
    if drug:
        query = f"Gather global intelligence for repurposing {drug} to treat {disease}"
    else:
        query = f"Gather global intelligence for drug repurposing options to treat {disease}"

    print("📊 Phase 1: Running data collectors in parallel...\n")
    
    tasks = [
        run_agent_local(web_intelligence_agent, query, "web_intelligence", context),
        run_agent_local(patent_research_agent, query, "patents", context),
        run_agent_local(clinical_trials_agent, query, "clinical_trials", context),
        run_agent_local(chembl_insights_agent, query, "chembl", context),
        run_agent_local(open_targets_agent_sdk, query, "open_targets", context),
        run_agent_local(market_insights_agent, query, "market", context),
        run_agent_local(exim_trade_agent, query, "exim", context)
    ]

    await asyncio.gather(*tasks)


# Phase 2: Run pathway and strategy agents sequentially
async def run_analysis_agents(disease: str, context: PharmaResearchContext):
    """Run pathway and strategy agents sequentially using data from phase 1."""
    print("\n🧬 Phase 2: Running analysis agents sequentially...\n")
    
    # Pathway agent analyzes the collected data
    pathway_prompt = f"""
            Analyze the following research data for {disease} and identify mechanistic pathways:

            Web Intelligence: {context.web_intelligence}
            Patents: {context.patents}
            Clinical Trials: {context.clinical_trials}
            ChEMBL Data: {context.chembl}
            Open Targets: {context.open_targets}
            Market Data: {context.market}
            EXIM Data: {context.exim}

            Provide mechanistic validation for drug repurposing opportunities.
        """
    
    await run_agent_local(disease_pathway_agent, pathway_prompt, "pathway", context)
    
    # Strategy agent ranks candidates using pathway analysis
    strategy_prompt = f"""
        Based on the following research and pathway analysis for {disease}, rank drug repurposing candidates:

        Pathway Analysis: {context.pathway}
        Clinical Trials: {context.clinical_trials}
        Patents: {context.patents}
        Market Data: {context.market}

        Provide a ranked list of repurposing candidates with feasibility scores.
    """
    
    await run_agent_local(repurposing_strategy_agent, strategy_prompt, "strategy", context)


# Phase 3: Generate final report
async def generate_final_report(disease: str, context: PharmaResearchContext):
    """Generate final report using all collected data."""
    print("\n📘 Phase 3: Generating final report...\n")
    
    prompt_block = f"""
        Synthesize the following global pharmaceutical research findings into a polished executive report for {disease}:

        Web Intelligence Findings:
        {context.web_intelligence}

        Patent Prior-Art Insights:
        {context.patents}

        Global Clinical Trial Intelligence:
        {context.clinical_trials}

        Compound-level Mechanisms and Bioactivity:
        {context.chembl}

        Validated Targets and Genetic Associations:
        {context.open_targets}

        Market, Regulatory Approvals, Pricing, Competitors:
        {context.market}

        Export-Import Global Trade Dependency Summary:
        {context.exim}

        Target-Disease Mechanistic Validation:
        {context.pathway}

        Repurposing Strategy and Ranking Insights:
        {context.strategy}

        Do NOT speculate. If data was missing, summarize the gap briefly.
        Generate a visually structured report with narrative clarity and concise tables.
    """

    await run_agent_local(report_generation_agent, prompt_block, "report", context)


# Main pipeline
async def run_pipeline(disease: str, drug: Optional[str]=None) -> PharmaResearchContext:
    """Run the full pharmaceutical research pipeline and return results."""
    context = PharmaResearchContext()
    
    print("\n🚀 Starting Pharmaceutical Research Pipeline")
    print(f"Disease: {disease}")
    if drug:
        print(f"Drug: {drug}")
    print("="*80 + "\n")
    
    start = datetime.now()

    # Phase 1: Data collection (parallel)
    await run_parallel_collectors(disease, context, drug)
    
    # Phase 2: Analysis (sequential)
    await run_analysis_agents(disease, context)
    
    # Phase 3: Report generation
    await generate_final_report(disease, context)
    
    end = datetime.now()

    print(f"\n{'='*80}")
    print(f"🎯 Total pipeline time: {(end-start).total_seconds():.2f} seconds")
    print(f"{'='*80}\n")
    print("\n---------- FINAL REPORT OUTPUT ----------\n")
    print(context.report)
    
    return context


if __name__ == "__main__":
    disease_name = "Type 2 Diabetes"
    asyncio.run(run_pipeline(disease_name))
