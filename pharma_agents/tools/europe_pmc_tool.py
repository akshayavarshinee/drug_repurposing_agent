"""
Europe PMC API integration for literature support counting.
"""
import requests


def europe_pmc_count(query: str) -> int:
    """
    Count literature support for a query.
    
    Args:
        query: Search query string
        
    Returns:
        Number of papers found
    """
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    params = {
        "query": query,
        "format": "json",
        "pageSize": 1  # We only need the count
    }
    
    try:
        resp = requests.get(url, params=params, timeout=20)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("hitCount", 0)
    except Exception as e:
        print(f"Europe PMC error: {e}")
    
    return 0
