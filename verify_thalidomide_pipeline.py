import sys
import os
import json
# Add project root to path
sys.path.insert(0, 'd:/vscode/projects/coe_intern/drug_repurposing_agents')

from pharma_agents.tools.unified_repurposing_pipeline import run_repurposing_pipeline_logic

def verify_pipeline():
    print("--- Verifying Thalidomide Pipeline ---")
    try:
        result = run_repurposing_pipeline_logic("Thalidomide")
        
        print("\n--- Pipeline Result Summary ---")
        print(f"Drug Name: {result.get('drug_name')}")
        print(f"ChEMBL ID: {result.get('chembl_id')}")
        
        # Check Clinical Trials
        ct = result.get("clinical_trials", [])
        print(f"\nClinical Trials Data Type: {type(ct)}")
        if isinstance(ct, list) and ct:
            print(f"Clinical Trials Found: {len(ct)}")
            print(f"First Trial: {ct[0].get('nctId', 'N/A')} - {ct[0].get('briefTitle', 'N/A')[:50]}...")
        elif isinstance(ct, dict):
            print(f"Clinical Trials Raw: {str(ct)[:100]}...")
        else:
            print(f"Clinical Trials: {ct}")
            
        # Check Patents
        patents = result.get("patents", {})
        print(f"\nPatents Data Type: {type(patents)}")
        if isinstance(patents, dict) and "patents" in patents:
             print(f"Patents Found: {len(patents['patents'])}")
             if patents['patents']:
                 print(f"First Patent: {patents['patents'][0].get('title', 'N/A')[:50]}...")
        elif isinstance(patents, list):
             print(f"Patents Found: {len(patents)}")
        else:
             print(f"Patents Raw: {str(patents)[:100]}...")

        # Check Trade Data
        trade = result.get("trade_data", {})
        print(f"\nTrade Data Type: {type(trade)}")
        if isinstance(trade, dict) and "organic" in trade:
            print(f"Trade Results: {len(trade['organic'])}")
            print(f"First Trade Result: {trade['organic'][0].get('title')}")
        else:
            print(f"Trade Raw: {str(trade)[:100]}...")

        # Check Market Data
        market = result.get("market_data", {})
        print(f"\nMarket Data Type: {type(market)}")
        if isinstance(market, dict) and "organic" in market:
            print(f"Market Results: {len(market['organic'])}")
            print(f"First Market Result: {market['organic'][0].get('title')}")
        else:
            print(f"Market Raw: {str(market)[:100]}...")

        print("\n✅ Verification Complete!")

    except Exception as e:
        print(f"❌ Pipeline Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_pipeline()
