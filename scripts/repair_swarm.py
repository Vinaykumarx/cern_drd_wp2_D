# repair_swarm.py
import os
import json
import requests
from pathlib import Path
import sys

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from core.document_manager import DocumentManager
from core.rag_pipeline import RAGPipeline
from extraction.extract_with_docid import extract_pdf_with_docid

def repair():
    print("=== [Agent Zero] Swarm Repair & Ingestion Restoration ===")
    
    doc_mgr = DocumentManager()
    abs_db_uri = "/home/drd8/Vinay/projects/cern-multimodel-rag-lancedb-migration/lancedb"
    pipeline = RAGPipeline(db_uri=abs_db_uri)
    
    docs = doc_mgr.list_documents()
    print(f"Found {len(docs)} registered documents in registry.")
    
    for doc in docs:
        doc_id = doc['doc_id']
        pdf_path = Path(doc['path'])
        url = doc.get('url')
        
        print(f"\nProcessing: {doc_id}")
        
        # 1. Restore Physical File
        if not pdf_path.exists():
            if url:
                print(f"  ! File missing at {pdf_path}. Attempting re-download from {url}...")
                try:
                    # Leverage doc_mgr logic to restore
                    restored_path = doc_mgr.add_remote_pdf(url, doc_id)
                    print(f"  ✓ Restored to {restored_path}")
                    pdf_path = Path(restored_path)
                except Exception as e:
                    print(f"  ✖ Failed to restore {doc_id}: {e}")
                    continue
            else:
                print(f"  ✖ File missing and no URL available for {doc_id}. Skipping.")
                continue
        else:
            print(f"  ✓ Physical file exists: {pdf_path}")

        # 2. Extract & Re-index
        print(f"  → Triggering semantic extraction for {doc_id}...")
        try:
            # Re-run extraction (force=True to be sure)
            extract_pdf_with_docid(str(pdf_path), doc_id, force_reprocess=True)
            
            # 3. Ingest into LanceDB
            print(f"  → Ingesting semantic chunks into LanceDB...")
            pipeline.ingest_from_doc_id_output(doc_id)
            
            doc_mgr.update_status(doc_id, "indexed")
            print(f"  ✓ Document {doc_id} is now LIVE in the Swarm.")
            
        except Exception as e:
            print(f"  ✖ Ingestion failed for {doc_id}: {e}")

    print("\n=== [Agent Zero] Repair Complete ===")
    print("Check the dashboard at http://localhost:3000 to verify 'Vector Chunks' > 0")

if __name__ == "__main__":
    repair()
