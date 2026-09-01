import requests
from typing import List, Dict, Any

class CernDbSearch:
    """
    Fallback tool that queries the official CERN Document Server (CDS) API 
    when the local LanceDB context is insufficient or low confidence.
    """
    def __init__(self):
        self.base_url = "https://cds.cern.ch/search"

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Executes a search against the CDS JSON API.
        """
        params = {
            "p": query,
            "of": "recjson",  # Return JSON format
            "rg": top_k       # Number of results
        }
        headers = {
            "User-Agent": "curl/8.2.1"
        }
        
        try:
            print(f"[CernDbSearch] Querying CDS API for: '{query}'")
            response = requests.get(self.base_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # CDS returns a list of records
            for record in data:
                if not isinstance(record, dict):
                    continue
                    
                title_obj = record.get("title", {})
                title = title_obj[0].get("title", "Unknown Title") if isinstance(title_obj, list) else title_obj.get("title", "Unknown Title")
                
                abstract_obj = record.get("abstract", {})
                abstract = abstract_obj[0].get("summary", "No abstract available.") if isinstance(abstract_obj, list) else abstract_obj.get("summary", "No abstract available.")
                
                # Try to get authors
                authors = []
                for author_entry in record.get("authors", []):
                    if isinstance(author_entry, dict) and "name" in author_entry:
                        authors.append(author_entry["name"])
                        
                results.append({
                    "doc_id": str(record.get("recid", "CDS")),
                    "title": title,
                    "authors": ", ".join(authors) if authors else "Unknown",
                    "abstract": abstract,
                    "url": f"https://cds.cern.ch/record/{record.get('recid', '')}"
                })
                
            return results
        except Exception as e:
            print(f"[CernDbSearch] API Error: {e}")
            return []
