"""
Test script for the unified repurposing pipeline.
"""
import asyncio
from agents import Runner
from pharma_agents.unified_pipeline_agent import unified_pipeline_agent
from dotenv import load_dotenv

load_dotenv(override=True)

async def test_drug_pipeline():
    """Test Pipeline A with a drug input."""
    print("\n" + "="*80)
    print("TEST 1: Pipeline A (Drug Input)")
    print("="*80 + "\n")
    
    result = await Runner.run(
        unified_pipeline_agent,
        input="Analyze Imatinib for repurposing opportunities",
        max_turns=3
    )
    
    print("\n" + "="*80)
    print("RESULT:")
    print("="*80)
    print(result.final_output)


async def test_disease_pipeline():
    """Test Pipeline B with a disease input."""
    print("\n" + "="*80)
    print("TEST 2: Pipeline B (Disease Input)")
    print("="*80 + "\n")
    
    result = await Runner.run(
        unified_pipeline_agent,
        input="Find drug repurposing candidates for Type 2 Diabetes",
        max_turns=3
    )
    
    print("\n" + "="*80)
    print("RESULT:")
    print("="*80)
    print(result.final_output)


async def main():
    """Run both tests."""
    await test_drug_pipeline()
    print("\n\n")
    await test_disease_pipeline()


if __name__ == "__main__":
    asyncio.run(main())
