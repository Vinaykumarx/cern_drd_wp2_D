from core.bootstrap import require_bootstrap; require_bootstrap()
import os
from dotenv import load_dotenv
from core.rag_pipeline import RAGPipeline

load_dotenv()
doc_id = 'cern_205520_cern_89_12'
print(f"--- Manual Ingestion of {doc_id} ---")
r = RAGPipeline()
r.ingest_from_doc_id_output(doc_id)
print("Ingestion complete.")
