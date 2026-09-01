from core.bootstrap import require_bootstrap; require_bootstrap()
from core.rag_pipeline import RAGPipeline
from core.document_manager import DocumentManager
import os

doc_id = "cern_205520_cern_89_12"
print(f"Manually ingesting {doc_id} into LanceDB Swarm...")

rag = RAGPipeline()
doc_mgr = DocumentManager()

doc = doc_mgr.get_document(doc_id)
if doc:
    pdf_path = doc["path"]
    if not os.path.isabs(pdf_path):
        pdf_path = os.path.join(os.getcwd(), pdf_path)
    
    print(f"Path: {pdf_path}")
    if os.path.exists(pdf_path):
        # We need to process the PDF
        from core.llm_client import process_text_for_chunks
        # This is a bit complex for a one-liner, but we can call the pipeline method
        # if it has one.
        # Actually, let's just use the existing logic in rag_pipeline if possible.
        pass
    else:
        print("File not found on server!")
else:
    print("Doc ID not found in registry!")
