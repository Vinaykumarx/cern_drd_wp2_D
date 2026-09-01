"""
Unified Modular CERN Multimodal RAG Pipeline Orchestrator.
Coordinates: Parser -> CanonicalDoc -> Chunker -> Embedder -> LanceDB -> Retrieval -> Rerank -> LLM -> Grounding.
"""

from typing import List, Dict, Optional, Any
import os
import time

from core.schemas.canonical import CanonicalDocument
from core.parsers.base import BaseDocumentParser
from core.parsers.pymupdf_parser import PyMuPDFParser
from core.parsers.docling_parser import DoclingDocumentParser
from core.chunkers.base import BaseChunker, Chunk
from core.chunkers.structure_chunker import StructureAwareChunker
from core.embeddings.base import BaseEmbedder
from core.embeddings.bge_embedder import BGEEmbedder
from core.storage.base import BaseVectorStore, SearchResult
from core.storage.lancedb_store import LanceDBStore
from core.rerankers.base import BaseReranker
from core.rerankers.cross_encoder_reranker import CrossEncoderReranker
from core.models.base import BaseModelProvider, GenerationResponse
from core.models.local_provider import LocalModelProvider
from core.verification.grounding_verifier import GroundingVerifier


class CERNMultimodalRAGPipeline:
    def __init__(
        self,
        parser: Optional[BaseDocumentParser] = None,
        chunker: Optional[BaseChunker] = None,
        embedder: Optional[BaseEmbedder] = None,
        vector_store: Optional[BaseVectorStore] = None,
        reranker: Optional[BaseReranker] = None,
        model_provider: Optional[BaseModelProvider] = None,
        verifier: Optional[GroundingVerifier] = None,
    ):
        self.parser = parser or PyMuPDFParser()
        self.chunker = chunker or StructureAwareChunker()
        self.embedder = embedder or BGEEmbedder(model_name="all-MiniLM-L6-v2")
        self.vector_store = vector_store or LanceDBStore(uri="lancedb", table_name="cern_canonical_chunks")
        self.reranker = reranker or CrossEncoderReranker(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2")
        self.model_provider = model_provider or LocalModelProvider()
        self.verifier = verifier or GroundingVerifier()

    def ingest_document(self, file_path: str, doc_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Full Canonical Ingestion:
        1. Parse document -> CanonicalDocument
        2. Chunk CanonicalDocument -> Structure-Aware Chunks
        3. Embed Chunks -> Dense vectors
        4. Add to Vector Store (LanceDB)
        """
        start_time = time.time()
        print(f"[INGEST] Starting parsing for {file_path} using parser: {self.parser.name}")
        canonical_doc = self.parser.parse(file_path=file_path, doc_id=doc_id)
        
        print(f"[INGEST] CanonicalDoc parsed: {len(canonical_doc.elements)} elements across {canonical_doc.total_pages} pages")
        chunks = self.chunker.chunk(canonical_doc)
        print(f"[INGEST] Generated {len(chunks)} structure-aware chunks")

        texts_to_embed = [c.content for c in chunks]
        embeddings = self.embedder.embed_texts(texts_to_embed)
        print(f"[INGEST] Embedded {len(embeddings)} chunks (dim={embeddings.shape[1]})")

        records_added = self.vector_store.add_chunks(chunks, embeddings)
        elapsed = time.time() - start_time
        print(f"[INGEST] Successfully indexed {records_added} vectors in {elapsed:.2f}s")

        return {
            "doc_id": canonical_doc.doc_id,
            "filename": canonical_doc.filename,
            "total_pages": canonical_doc.total_pages,
            "elements_count": len(canonical_doc.elements),
            "chunks_count": len(chunks),
            "vectors_stored": records_added,
            "elapsed_seconds": elapsed,
        }

    def query(
        self,
        query_text: str,
        top_k: int = 5,
        doc_id: Optional[str] = None,
        enable_reranking: bool = True,
    ) -> Dict[str, Any]:
        """
        Full Grounded Query:
        1. Embed Query -> Query vector
        2. Vector Search -> Initial candidate pool
        3. Rerank -> Top evidence chunks
        4. LLM Generation -> Evidence-grounded response
        5. Verification Gate -> Audit citations and confidence
        """
        start_time = time.time()
        # 1. Embed query
        query_vector = self.embedder.embed_query(query_text)

        # 2. Vector search (fetch 2x top_k for reranker candidate pool)
        candidate_k = top_k * 2 if enable_reranking else top_k
        candidates = self.vector_store.search(
            query_vector=query_vector,
            top_k=candidate_k,
            doc_id=doc_id,
        )

        if not candidates:
            return {
                "query": query_text,
                "answer": "INSUFFICIENT EVIDENCE: No relevant documents found.",
                "citations": [],
                "evidence": [],
                "confidence_score": 0.0,
                "grounding_passed": False,
                "elapsed_seconds": time.time() - start_time,
            }

        # 3. Rerank
        if enable_reranking and self.reranker:
            evidence = self.reranker.rerank(query_text, candidates, top_n=top_k)
        else:
            evidence = candidates[:top_k]

        # 4. Generate grounded answer
        response: GenerationResponse = self.model_provider.generate_grounded_answer(
            query=query_text,
            evidence=evidence,
        )

        # 5. Grounding & Citation Verification
        is_valid, confidence, report = self.verifier.verify(response, evidence)

        elapsed = time.time() - start_time

        return {
            "query": query_text,
            "answer": response.answer,
            "citations": [c.model_dump() for c in response.citations],
            "evidence": [e.model_dump() for e in evidence],
            "is_grounded": is_valid,
            "confidence_score": confidence,
            "verification_report": report,
            "model_name": response.model_name,
            "elapsed_seconds": elapsed,
        }
