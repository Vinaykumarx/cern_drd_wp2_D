"""
Pipeline Sanity Test — End-to-end ingestion → retrieval verification.

Validates the canonical pipeline works correctly:
  1. Create sample data
  2. Chunk via SemanticChunker
  3. Embed via RAGPipeline
  4. Store in LanceVectorStore
  5. Search and retrieve

Uses isolated temp directories — never touches production data.
"""

import os
import sys
import json
import uuid
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.rag_pipeline import RAGPipeline
from core.semantic_chunker import SemanticChunker
from core.vector_store_lance import LanceVectorStore


def make_sample_metadata(temp_dir: Path, doc_id: str) -> Path:
    """Create sample metadata.json with a single page of text."""
    pages = [
        {
            "page": 1,
            "text": (
                "# Introduction\n\n"
                "This is a sample CERN document about particle physics.\n\n"
                "## Detector Overview\n\n"
                "The ATLAS detector is a general-purpose detector at the LHC.\n"
                "It measures particles produced in proton-proton collisions.\n\n"
                "## Radiation Safety\n\n"
                "Radiation protection is critical at CERN facilities.\n"
                "Dosimeters are used to monitor exposure levels.\n"
            ),
        }
    ]
    metadata = {"pages": pages, "tables": {}, "figures": {}}
    meta_path = temp_dir / "metadata.json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f)
    return meta_path


def test_pipeline_sanity():
    """
    Full canonical pipeline test:
    chunk → embed → store → search
    """
    print("=" * 60)
    print("PIPELINE SANITY TEST")
    print("=" * 60)

    test_dir = Path(tempfile.mkdtemp(prefix="pipeline_sanity_"))
    db_dir = test_dir / "lancedb"
    outputs_dir = test_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    doc_id = f"sanity_test_{uuid.uuid4().hex[:8]}"

    try:
        # ── Step 1: Create sample data ──
        print(f"\n[Step 1] Creating sample data for doc_id={doc_id}")
        doc_output_dir = outputs_dir / doc_id
        doc_output_dir.mkdir(parents=True, exist_ok=True)
        meta_path = make_sample_metadata(doc_output_dir, doc_id)

        # ── Step 2: Semantic Chunking ──
        print("[Step 2] Testing SemanticChunker...")
        chunker = SemanticChunker()
        text = "# Test\n\nThis is a test chunk about CERN physics."
        chunks = chunker.chunk_document(text, doc_id, 1)
        assert len(chunks) > 0, "SemanticChunker returned no chunks"
        print(f"  ✓ Chunked into {len(chunks)} chunks")

        # ── Step 3: RAGPipeline ──
        print("[Step 3] Initializing RAGPipeline...")
        pipeline = RAGPipeline(
            db_uri=str(db_dir),
            table_name="sanity_test",
            metadata_path=str(meta_path),
        )
        print("  ✓ RAGPipeline initialized")

        # ── Step 4: Embed ──
        print("[Step 4] Testing embedding...")
        test_texts = ["particle physics at CERN", "radiation safety", "detector systems"]
        vecs = pipeline.embed(test_texts)
        assert vecs.shape[0] == 3, f"Expected 3 vectors, got {vecs.shape[0]}"
        assert vecs.shape[1] == 768, f"Expected 768-dim, got {vecs.shape[1]}"
        print(f"  ✓ Generated {vecs.shape[0]} vectors ({vecs.shape[1]}-dim)")

        # ── Step 5: Ingest via RAGPipeline ──
        print("[Step 5] Testing ingestion via RAGPipeline...")
        pipeline.doc_id = doc_id
        pipeline.ingest_from_metadata(doc_id=doc_id)
        count = pipeline.store.count_rows()
        assert count > 0, f"Ingestion produced 0 rows, expected > 0"
        print(f"  ✓ Ingested {count} rows into vector store")

        # ── Step 6: Search ──
        print("[Step 6] Testing search...")
        text_hits, figure_hits, table_hits = pipeline.search("radiation safety at CERN", top_k=3)
        assert len(text_hits) > 0, "Search returned no text hits"
        print(f"  ✓ Search returned {len(text_hits)} text hits, {len(figure_hits)} figure hits, {len(table_hits)} table hits")

        # ── Step 7: VectorStore wrapper methods ──
        print("[Step 7] Testing VectorStore wrapper methods...")
        all_doc_ids = pipeline.store.get_all_doc_ids()
        assert doc_id in all_doc_ids, f"get_all_doc_ids missing {doc_id}"
        print(f"  ✓ get_all_doc_ids() — found {len(all_doc_ids)} doc(s)")

        all_vecs = pipeline.store.get_all_vectors(doc_ids=[doc_id], limit=10, page=0)
        assert len(all_vecs) > 0, "get_all_vectors returned empty"
        print(f"  ✓ get_all_vectors() — retrieved {len(all_vecs)} rows")

        verify = pipeline.store.verify_document_vectors(doc_id)
        assert verify.get("status") == "ok", f"verify_document_vectors failed: {verify}"
        print(f"  ✓ verify_document_vectors() — status: {verify['status']} ({verify['vector_count']} vectors)")

        # ── Step 8: Search via VectorStore ──
        print("[Step 8] Testing direct VectorStore search...")
        query_vec = pipeline.embed(["CERN detector"])[0].tolist()
        results = pipeline.store.search(query_vec, doc_ids=[doc_id], top_k=2)
        assert len(results) > 0, "VectorStore.search returned empty"
        print(f"  ✓ VectorStore.search() — {len(results)} results")

        print("\n" + "=" * 60)
        print("ALL PIPELINE SANITY CHECKS PASSED")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n❌ PIPELINE SANITY TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        shutil.rmtree(str(test_dir))
        print(f"\n[Cleanup] Removed temp directory: {test_dir}")


if __name__ == "__main__":
    success = test_pipeline_sanity()
    sys.exit(0 if success else 1)
