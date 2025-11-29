import requests
import traceback
from typing import List, Optional

def open_targets_disease_lookup(
    disease_name: str, 
    limit: int = 10,
    datasource_ids: Optional[List[str]] = None
) -> List[dict]:
    """
    Look up disease in Open Targets and retrieve associated targets via GraphQL.

    Additional enrichment included:
    - datatypeScores and datasourceScores
    - correct association_score extraction

    Args:
        disease_name: Name of the disease
        limit: Max number of targets
        datasource_ids: Optional datasource filter IDs

    Returns:
        List of enriched target dictionaries
    """

    url = "https://api.platform.opentargets.org/api/v4/graphql"

    # 1️⃣ Find Disease ID via GraphQL
    disease_search_query = """
    query searchDisease($queryString: String!) {
      search(queryString: $queryString, entityNames: ["disease"], page: {index: 0, size: 1}) {
        hits { id name }
      }
    }
    """

    try:
        resp = requests.post(
            url,
            json={"query": disease_search_query, "variables": {"queryString": disease_name}},
            timeout=20
        )
        if resp.status_code != 200:
            print(f"[Open Targets] Search HTTP failed: {resp.status_code}")
            return []

        data = resp.json()

        # GraphQL layer error
        if "errors" in data:
            print(f"[Open Targets] GraphQL returned errors: {data['errors']}")
            return []

        hits = data["data"]["search"]["hits"]
        if not hits:
            print(f"[Open Targets] Disease not found ❌")
            return []

        efo_id = hits[0]["id"]
        print(f"[Open Targets] ✓ Disease ID: {efo_id}")

        # 2️⃣ Fetch associated targets with scores
        disease_targets_query = """
        query getDiseaseTargets($efoId: String!, $size: Int!) {
          disease(efoId: $efoId) {
            associatedTargets(page: {index: 0, size: $size}) {
              rows {
                target { id approvedSymbol approvedName biotype }
                score
                datatypeScores { id score }
                datasourceScores { id score }
              }
            }
          }
        }
        """

        resp = requests.post(
            url,
            json={"query": disease_targets_query, "variables": {"efoId": efo_id, "size": limit}},
            timeout=20
        )

        if resp.status_code != 200:
            print(f"[Open Targets] Target fetch HTTP failed: {resp.status_code}")
            return []

        data = resp.json()
        if "errors" in data:
            print(f"[Open Targets] GraphQL returned errors: {data['errors']}")
            return []

        rows = data["data"]["disease"]["associatedTargets"]["rows"]  # ✅ FIXED PATH

        targets = []
        for row in rows:
            tgt = row["target"]
            ds_scores = {ds["id"]: round(ds["score"],3) for ds in row.get("datasourceScores",[])}
            dt_scores = {dt["id"]: round(dt["score"],3) for dt in row.get("datatypeScores",[])}

            # optional filtering by datasource evidence
            if datasource_ids:
                if not any(ds in ds_scores for ds in datasource_ids):
                    continue

            targets.append({
                "target_id": tgt["id"],
                "symbol": tgt.get("approvedSymbol"),
                "name": tgt.get("approvedName"),
                "biotype": tgt.get("biotype"),
                "association_score": round(row.get("score",0.5),3),  # ✅ FIXED EXTRACTION
                "datasource_scores": ds_scores,
                "datatype_scores": dt_scores
            })

        print(f"[Open Targets] ✓ returning {len(targets)} targets")
        return targets[:limit]

    except Exception as e:
        print("[Open Targets] Unexpected error ❌")
        print(traceback.format_exc())
        return []


open_targets_disease_lookup("Diabetes")