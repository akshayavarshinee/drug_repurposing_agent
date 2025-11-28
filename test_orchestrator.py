"""
Quick test script to verify the orchestrator handles coroutines correctly.
"""
import sys
import asyncio
from pathlib import Path

# Add agents path to sys.path
project_root = Path(__file__).parent
agents_path = project_root / "agents"
sys.path.insert(0, str(agents_path))

async def test_pipeline():
    """Test the pipeline with a simple query."""
    from async_orchestrator import run_pipeline
    
    print("Testing pipeline with Type 2 Diabetes...")
    context = await run_pipeline("Type 2 Diabetes")
    
    print("\n" + "="*80)
    print("TESTING RESULTS:")
    print("="*80)
    
    # Check if report is a string or a coroutine
    print(f"\nReport type: {type(context.report)}")
    print(f"Report is string: {isinstance(context.report, str)}")
    
    if context.report:
        print(f"\nReport preview (first 200 chars):")
        print(context.report[:200])
        print("...")
    else:
        print("\n⚠️  No report generated!")
    
    if context.errors:
        print(f"\n⚠️  Errors encountered:")
        print(context.errors)
    
    return context

if __name__ == "__main__":
    asyncio.run(test_pipeline())
