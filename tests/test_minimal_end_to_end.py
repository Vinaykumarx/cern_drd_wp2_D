"""
Task 17 Verification Test: Minimal End-to-End Modular CERN Multimodal RAG Pipeline.
Tests: One Document (CERN-89-12.pdf) -> Canonical Parsing -> Chunking -> LanceDB -> Query -> Rerank -> Grounded Answer -> Verified Citation (#page=N).
"""

import os
import sys
import json

# Ensure project root is on sys.path
project_root = r"C:\Users\vvinayku\cernbox\cern-multimodel-rag-lancedb-migration"
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.pipeline.cern_rag import CERNMultimodalRAGPipeline
from core.parsers.pymupdf_parser import PyMuPDFParser
from core.chunkers.structure_chunker import StructureAwareChunker
from core.embeddings.bge_embedder import BGEEmbedder
from core.storage.lancedb_store import LanceDBStore
from core.rerankers.cross_encoder_reranker import CrossEncoderReranker
from core.models.local_provider import LocalModelProvider
from core.verification.grounding_verifier import GroundingVerifier


def run_minimal_end_to_end_test():
    print("=" * 70)
    print(" CERN MULTIMODAL RAG: MINIMAL END-TO-END PIPELINE VERIFICATION")
    print("=" * 70)

    pdf_path = os.path.join(project_root, "data", "CERN-89-12.pdf")
    if not os.path.exists(pdf_path):
        # Fallback to any available PDF in data/
        data_dir = os.path.join(project_root, "data")
        pdf_files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith(".pdf")]
        if not pdf_files:
            raise FileNotFoundError("No PDF files found in data/ directory.")
        pdf_path = pdf_files[0]

    doc_id = "CERN_89_12"
    print(f"\n[1/3] Target Document: {pdf_path}")
    print(f"      Assigned Doc ID: {doc_id}")

    # Initialize modular components
    pipeline = CERNMultimodalRAGPipeline(
        parser=PyMuPDFParser(),
        chunker=StructureAwareChunker(target_chunk_size=500),
        embedder=BGEEmbedder(model_name="all-MiniLM-L6-v2"),
        vector_store=LanceDBStore(uri=os.path.join(project_root, "lancedb"), table_name="cern_canonical_chunks"),
        reranker=CrossEncoderReranker(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"),
        model_provider=LocalModelProvider(model_name="gemma4"),
        verifier=GroundingVerifier(min_similarity_threshold=0.25),
    )

    # 1. Ingest
    print("\n[2/3] Executing Document Ingestion...")
    ingest_result = pipeline.ingest_document(file_path=pdf_path, doc_id=doc_id)
    print("      Ingestion Output Summary:")
    for k, v in ingest_result.items():
        print(f"        • {k}: {v}")

    # 2. Query
    test_query = "radiation index of thermoplastic and thermosetting materials"
    print(f"\n[3/3] Executing Grounded Query: '{test_query}'...")
    query_result = pipeline.query(query_text=test_query, top_k=3, doc_id=doc_id)

    print("\n" + "=" * 70)
    print(" RESULTS & GROUNDING AUDIT")
    print("=" * 70)
    print(f"\nQUERY: {query_result['query']}")
    print(f"\nGROUNDED ANSWER:\n{query_result['answer']}")
    print(f"\nGROUNDING STATUS: {'PASSED (Grounded)' if query_result['is_grounded'] else 'FAILED'}")
    print(f"CONFIDENCE SCORE: {query_result['confidence_score']:.2f}")

    print("\nVERIFIED CITATIONS (Provenance Links):")
    for cit in query_result["citations"]:
        print(f"  {cit['citation_id']} -> {cit['filename']} Page {cit['page_number']} ({cit['citation_anchor']})")
        print(f"       Snippet: {cit['snippet']}...")

    print(f"\nTOTAL PIPELINE LATENCY: {query_result['elapsed_seconds']:.2f}s")
    print("=" * 70)

    assert query_result["is_grounded"] is True, "Grounding verification failed!"
    assert len(query_result["citations"]) > 0, "No citations generated!"
    print("\n SUCCESS: TASK 17 MINIMAL END-TO-END PIPELINE VALIDATED SUCCESSFULLY!")


if __name__ == "__main__":
    run_minimal_end_to_end_test()
