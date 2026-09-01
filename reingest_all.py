
from core.bootstrap import require_bootstrap; require_bootstrap()
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from core.rag_pipeline import RAGPipeline

# Load environment variables (API keys, Base URL)
load_dotenv()

def reingest_all(target_doc_id: str = None):
    base_dir = Path(__file__).resolve().parent
    outputs_dir = base_dir / "outputs"
    
    db_uri = str(base_dir / "lancedb")
    rag = RAGPipeline(db_uri=db_uri)
    
    if not outputs_dir.exists():
        print("No outputs directory found.")
        return

    for doc_dir in outputs_dir.iterdir():
        if doc_dir.is_dir():
            doc_id = doc_dir.name
            if target_doc_id and doc_id != target_doc_id:
                continue
                
            metadata_file = doc_dir / "metadata.json"
            if metadata_file.exists():
                print(f"Ingesting {doc_id}...")
                try:
                    # Cleanup old vectors for this doc_id to prevent duplicates/stale data
                    try:
                        rag.store.delete_by_doc_id(doc_id)
                        print(f"  ✓ Cleaned up old vectors for {doc_id}")
                    except:
                        pass
                        
                    rag.ingest_from_doc_id_output(doc_id)
                    print(f"Successfully ingested {doc_id}")
                except Exception as e:
                    print(f"Failed to ingest {doc_id}: {e}")

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else None
    reingest_all(target)
