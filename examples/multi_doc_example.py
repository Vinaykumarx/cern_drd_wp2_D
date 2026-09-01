#!/usr/bin/env python
"""
Example: Multi-document RAG workflow
- Download PDF from CERN URL
- Extract with doc_id tracking
- Ingest into LanceDB
- Search with document filtering

Usage:
    python examples/multi_doc_example.py
"""

import sys
from pathlib import Path
import json

# Add project root to path
BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from core.document_manager import DocumentManager
from core.rag_pipeline import RAGPipeline
from extraction.extract_with_docid import extract_pdf_with_docid


def main():
    print("="*70)
    print("CERN Multi-Document RAG Example")
    print("="*70)
    
    # Initialize components
    doc_mgr = DocumentManager()
    pipeline = RAGPipeline()
    
    # Example documents to add
    documents = [
        # CERN Yellow Report (default, already extracted)
        {
            "type": "default",
            "doc_id": "cern_yellow_report",
            "description": "CERN Yellow Report 357576 (default, may already exist)"
        },
        # You can add more documents by uncommenting the URLs below:
        # CERN Physics Report with specific fields
        # {
        #     "type": "url",
        #     "url": "https://cds.cern.ch/record/205520?ln=en",
        #     "doc_id": "cern_205520",
        #     "description": "CERN Physics data/reports"
        # },
        # Another CERN document
        # {
        #     "type": "url",
        #     "url": "https://cds.cern.ch/record/123456?ln=en",
        #     "doc_id": "cern_123456",
        #     "description": "Another CERN document"
        # },
    ]
    
    print("\n" + "="*70)
    print("Step 1: Register and Extract Documents")
    print("="*70)
    
    extracted_docs = []
    
    for doc_config in documents:
        doc_id = doc_config['doc_id']
        description = doc_config['description']
        
        try:
            if doc_config['type'] == 'default':
                print(f"\n[{doc_id}] Using default CERN Yellow Report")
                print(f"  Description: {description}")
                pdf_file = BASE / "data" / "CERN_Yellow_Report_357576.pdf"
                
                if not pdf_file.exists():
                    print(f"  ! PDF not found at {pdf_file}")
                    print("    Please ensure CERN_Yellow_Report_357576.pdf is in data/ directory")
                    continue
                
                # Register in document manager (returns file path)
                pdf_path = doc_mgr.add_local_pdf(str(pdf_file), doc_id)
                extracted_docs.append((doc_id, pdf_path))
                print(f"  ✓ Registered")
            
            elif doc_config['type'] == 'url':
                url = doc_config['url']
                print(f"\n[{doc_id}] Downloading from URL")
                print(f"  URL: {url}")
                print(f"  Description: {description}")
                
                # Download and register (returns file path)
                pdf_path = doc_mgr.add_remote_pdf(url, doc_id)
                extracted_docs.append((doc_id, pdf_path))
                print(f"  ✓ Downloaded to {pdf_path}")
        
        except Exception as e:
            print(f"  ! Error with {doc_id}: {e}")
            continue
    
    if not extracted_docs:
        print("\n! No documents extracted. Exiting.")
        return
    
    print("\n" + "="*70)
    print("Step 2: Extract Content (Text, Tables, Figures)")
    print("="*70)
    
    ingested_docs = []
    
    for doc_id, pdf_path in extracted_docs:
        try:
            print(f"\n[{doc_id}] Extracting content...")
            
            # Extract (this creates outputs/{doc_id}/ with metadata.json)
            metadata = extract_pdf_with_docid(
                pdf_path=pdf_path,
                doc_id=doc_id,
                force_reprocess=False  # Set to True to re-extract
            )
            
            # Update status in document manager
            doc_mgr.update_status(doc_id, "extracted")
            ingested_docs.append(doc_id)
            
            print(f"\n  ✓ Extraction complete for {doc_id}")
            print(f"    - Pages: {len(metadata.get('pages', []))}")
            print(f"    - Tables: {len(metadata.get('tables', {}))}")
            print(f"    - Figures: {len(metadata.get('figures', {}))}")
        
        except Exception as e:
            print(f"  ! Error extracting {doc_id}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    if not ingested_docs:
        print("\n! No documents extracted. Exiting.")
        return
    
    print("\n" + "="*70)
    print("Step 3: Ingest into LanceDB Vector Store")
    print("="*70)
    
    # Reset LanceDB to ensure clean state with new schema
    print("\n[DB] Resetting LanceDB table...")
    pipeline.store.reset()
    print("✓ Table reset")
    
    # Ingest each document
    for doc_id in ingested_docs:
        try:
            print(f"\n[{doc_id}] Ingesting into LanceDB...")
            pipeline.ingest_from_doc_id_output(doc_id)
            doc_mgr.update_status(doc_id, "ingested")
            print(f"✓ {doc_id} ingested")
        
        except Exception as e:
            print(f"! Error ingesting {doc_id}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print("\n" + "="*70)
    print("Step 4: Search Examples")
    print("="*70)
    
    # Example queries
    queries = [
        ("radiation", None),  # Search all documents
        ("detector", "cern_yellow_report"),  # Search specific document
        ("physics", None),  # Search all
    ]
    
    for query, target_doc_id in queries:
        if target_doc_id and target_doc_id not in ingested_docs:
            print(f"\n! Skipping query for {target_doc_id} (not ingested)")
            continue
        
        print(f"\n[Query] '{query}'" + (f" in {target_doc_id}" if target_doc_id else " (all documents)"))
        print("-" * 50)
        
        try:
            text_hits, figure_hits, table_hits = pipeline.search(
                query,
                top_k=3,
                doc_id=target_doc_id
            )
            
            # Display results
            if text_hits:
                print(f"\n  TEXT HITS ({len(text_hits)}):")
                for i, hit in enumerate(text_hits, 1):
                    print(f"    {i}. [{hit['doc_id']}] p.{hit['page']} (score: {hit['score']:.3f})")
                    print(f"       {hit['text'][:80]}...")
            
            if figure_hits:
                print(f"\n  FIGURE HITS ({len(figure_hits)}):")
                for i, hit in enumerate(figure_hits, 1):
                    print(f"    {i}. [{hit['doc_id']}] p.{hit['page']} (score: {hit['score']:.3f})")
                    print(f"       {hit['text'][:80]}...")
            
            if table_hits:
                print(f"\n  TABLE HITS ({len(table_hits)}):")
                for i, hit in enumerate(table_hits, 1):
                    print(f"    {i}. [{hit['doc_id']}] p.{hit['page']} (score: {hit['score']:.3f})")
                    print(f"       {hit['text'][:80]}...")
            
            if not (text_hits or figure_hits or table_hits):
                print("  (no results)")
        
        except Exception as e:
            print(f"  ! Search error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("Step 5: List Registered Documents")
    print("="*70)
    
    print("\nRegistered documents:")
    docs = doc_mgr.list_documents()
    
    if not docs:
        print("  (none)")
    else:
        for doc in docs:
            print(f"  - {doc['doc_id']}")
            print(f"    Path: {doc['path']}")
            print(f"    Status: {doc.get('status', 'unknown')}")
            print(f"    Size: {doc.get('size', 'unknown')} bytes")
    
    print("\n" + "="*70)
    print("✓ Multi-document RAG workflow complete!")
    print("="*70)
    
    print("\nNext: Start Streamlit app to query documents interactively:")
    print("  $ streamlit run app/streamlit_app_DEPRECATED.py")


if __name__ == '__main__':
    main()
