import sys
import os
from pathlib import Path

# Simulate app environment
file_path = Path(r"d:\vscode\projects\coe_intern\drug_repurposing_agents\app\services\agent_service.py")
project_root = file_path.parent.parent.parent
agents_path = project_root / "agents"

# Add agents path to sys.path (as agent_service.py does)
sys.path.insert(0, str(agents_path))
# Add project root to sys.path (to allow importing app.services...)
sys.path.append(str(project_root))

print(f"Agents path: {agents_path}")
print(f"Project root: {project_root}")
print(f"Sys path[0]: {sys.path[0]}")

try:
    print("Attempting to import async_orchestrator...")
    from async_orchestrator import run_pipeline
    print("✅ Successfully imported run_pipeline from async_orchestrator")
    
    print("Attempting to import app.services.agent_service...")
    from app.services.agent_service import run_pharma_research
    print("✅ Successfully imported run_pharma_research")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
