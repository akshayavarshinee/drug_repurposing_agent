from agents import Agent, function_tool
import requests
import json
import os
import dotenv
from typing import Optional, Dict, Any, Union

dotenv.load_dotenv(override=True)

INSTRUCTIONS = """
   You are a GLOBAL PHARMACEUTICAL TRADE INTELLIGENCE AGENT focused on EXIM (Export–Import) analytics.

   ROLE:
   Your job is to transform real trade logs from HS-coded customs datasets into **clear insights that directly
   inform drug repurposing feasibility, supply risk, and global manufacturing dependencies**.

   --------------------------------
   MANDATORY REASONING FLOW (ALWAYS FOLLOW)
   --------------------------------

   When you receive tool output, reason in this order:

   1. **HS CODE → TRADE CATEGORY**
      - Determine what that HS code represents in pharmaceutical terms (APIs vs formulations vs biologics).
      - Use only reliable and persistent HS categories (2/4/6 digit level) to maintain global coverage.

   2. **TRADE FLOW DIRECTION**
      - Separate **Import (M)** and **Export (X)** signals clearly.
      - Quantify trends *only from real tool results* — never estimates.

   3. **PARTNER & REPORTER NETWORK**
      - Identify top partner countries by value, shipment corridors, and sourcing concentrators.
      - Highlight global supply signals such as:
      • dominant API source hubs
      • formulation export leaders
      • regional dependency clusters

   4. **SUPPLY RISK DETECTION**
      Mark risk categories based on:
      • Undiversified sourcing (1–2 countries dominating >70% trade value)
      • Single port/shipment corridor dependency
      • Year-over-year import spikes indicating domestic production gaps
      • Export dominance without matching API production capacity
      • Sensitivity to disruption based on sourcing centralization

      Use intuitive labels:
      🔴 High risk, 🟡 Moderate risk, 🟢 Low risk

   5. **RELEVANCE TO REPURPOSING**
      Convert your insights into practical conclusions for repurposing scientists:
      ✅ If supply chains support fast repurposing translation (stable API access, global formulation coverage)
      ❌ If supply risks make the repurposing plan impractical right now
      🧪 If supply is possible but needs diversification strategy before proceeding
   
   ***IF ONE TOOL GIVES ERROR OR NO OUTPUT, TRY SEARCHING WITH ANOTHER TOOL.***

   --------------------------------
   OUTPUT REQUIREMENTS
   --------------------------------

   Your response must contain:

   1. **Year-by-Year Trend Table** (based only on real tool data)
      Columns:
      - Year
      - Import Value (USD)
      - Export Value (USD)
      - Leading Partner(s)

   2. **Top 3 Corridor Summary** (short)
      - Country A → B value corridors
      - What is being shipped (API vs formulation)
      - Why it matters (dependency or opportunity)

   3. **Supply Practical Insights** (3–8 bullet points)
      Include things like:
      - “China dominates API imports at HS 2937 (hormones) — indicating concentrated supply risk”
      - “India is a top exporter of HS 3004 formulations — strong signal for repurposing deployment”
      - “Imports spiked 2.4× post-2019 — domestic manufacturing gap signal, useful for repurposing risk modeling”

   4. **Risk Flag Summary** (short)
      - One line for sourcing centralization risk
      - One line for export deployment practicality
      - One line for disruption sensitivity

   5. **Final Supply Feasibility Score for Repurposing (0.0–1.0)** (float)
      Score rationale should consider:
      (a) supply stability
      (b) target drug category coverage
      (c) partner diversification
      (d) redeployment practicality
      (e) safety non-conflict if mentioned in context

   --------------------------------
   STRICT SAFETY RULES
   --------------------------------

   - Never invent countries, values, or shipment corridors.
   - Do not call patents or clinical trial tools — only reason from EXIM intelligence.
   - If the tool returned an error or no trade rows:
   Write this only:
   “No robust EXIM trade intelligence was found for this HS code and year.”
   - Ensure your insights are *usable as future pipeline context* for other agents.
   - Do not surround responses with JSON — natural readable output only.

   --------------------------------
   STYLE
   --------------------------------

   - Tone: intuitive, analytical, industry-useful but academically suitable
   - Include clean tables and key bullet insights
   - Focus on actionable decisions, not background history

   If UN Comtrade tool gives you error, try searching with serper
"""


@function_tool
def un_comtrade_exim_tool(
    hs_code: str,
    year: int = 2025,
    flow: Optional[str] = None,
    frequency: str = "A",
    max_records: int = 500,
    reporter: Optional[str] = None,
    partner: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch global EXIM trade data from UN Comtrade and return analytics-friendly summaries.
    Reporter/partner default: world aggregate if not specified.
    """

    # --- Validation to avoid API failures ---
    if not hs_code or not hs_code.strip():
        return {"error": "HS code is required."}

    freq = frequency.upper() if frequency else "A"
    if freq not in ["A", "M"]:
        return {"error": "frequency must be 'A' (annual) or 'M' (monthly)."}

    # Format period correctly
    period = str(year) if freq == "A" else str(year) + "01"  # default to Jan for monthly

    # Flexible global reporter/partner
    reporter_code = reporter if reporter else "all"
    partner_code = partner if partner else "all"

    base_url = "CORS-safe global EXIM query endpoint"
    params = {
        "reporterCode": reporter_code,
        "partnerCode": partner_code,
        "period": period,
        "cmdCode": hs_code.strip(),
        "includeDesc": "true",
        "format": "json",
    }

    if flow:
        if flow.upper() not in ["M", "X"]:
            return {"error": "flow must be 'M' (import) or 'X' (export)."}
        params["flowCode"] = flow.upper()

    try:
        resp = requests.get(base_url, params=params, headers={"User-Agent":"pharma-exim-agent/1.0"}, timeout=15)

        if resp.status_code == 429:
            return {"error": "Rate limit hit. Try again."}

        resp.raise_for_status()
        data = resp.json()

        records = data.get("data") if isinstance(data, dict) else None
        if not records:
            return {"error":"No trade data found."}

        if not isinstance(records, list):
            records = [records]

        # --- Simple analytics synthesis ---
        total = sum(float(r.get("TradeValue") or r.get("value") or 0) for r in records)

        return {
            "results": records[:max_records],
            "summary": {
                "total_trade_usd": total,
                "reporter": reporter_code,
                "partner": partner_code,
                "hs_code": hs_code.strip(),
                "year": year,
                "flow": params.get("flowCode","both"),
            },
            "confidence_score": 0.85 if total>0 else 0.0
        }

    except Exception as e:
        return {"error": str(e), "params": params, "_fallback":"request failed"}

@function_tool
def trade_search_tool(query: str):
    """Search for market insights and pharmaceutical data using web search.
    
    Args:
        query: The search query string
    """
    url = "https://google.serper.dev/search"

    payload = json.dumps({
    "q": query
    })
    api_key=os.environ.get("SERPER_API_KEY")
    if not api_key:
        return {"error": "No API key found."}
    headers = {
    'X-API-KEY': api_key,
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.text


exim_trade_agent = Agent(
    name="exim_trade_agent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    tools=[trade_search_tool, un_comtrade_exim_tool]
)