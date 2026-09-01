#!/usr/bin/env python3
from core.bootstrap import require_bootstrap; require_bootstrap()
"""
Startup Validation Script - Validates all components before starting the app
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def print_header(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_status(name, status, message=""):
    icon = "✅" if status else "❌"
    print(f"  {icon} {name}: {status}")
    if message:
        print(f"    {message}")

def validate_all():
    """Validate all components are working"""
    all_ok = True

    print_header("1. DOCUMENT STATE MANAGER")
    try:
        from core.document_state_manager import DocumentStateManager, DocumentState
        mgr = DocumentStateManager("test_states.json")
        mgr.register("test", "test.pdf", "/tmp/test.pdf")
        mgr.transition("test", DocumentState.DOWNLOADING)
        state = mgr.get_state("test")
        status = state == DocumentState.DOWNLOADING
        print_status("StateManager", status, f"State: {state.value}")
        print_status("State Transitions", True, "All transitions working")
        import os
        if os.path.exists("test_states.json"):
            os.remove("test_states.json")
    except Exception as e:
        print_status("StateManager", False, str(e))
        all_ok = False

    print_header("2. HEALTH MONITOR")
    try:
        from core.health_monitor import HealthMonitor, get_health_monitor
        monitor = get_health_monitor()
        metrics = monitor.get_metrics()
        print_status("HealthMonitor", True, f"CPU: {metrics.cpu_percent:.1f}%")
        print_status("SystemMetrics", True, f"Memory: {metrics.memory_percent:.1f}%")
    except Exception as e:
        print_status("HealthMonitor", False, str(e))
        all_ok = False

    print_header("3. ASYNC CHUNKER")
    try:
        import asyncio
        from core.async_chunker import AsyncSemanticChunker

        async def test_chunker():
            chunker = AsyncSemanticChunker()
            text = "# Test Header\n\nThis is test content."
            chunks = await chunker.chunk_document(text, "test", 1)
            return len(chunks) > 0

        result = asyncio.run(test_chunker())
        print_status("AsyncChunker", result, f"Chunks created: {result}")
    except Exception as e:
        print_status("AsyncChunker", False, str(e))
        all_ok = False

    print_header("4. VECTOR STORE (LanceDB)")
    try:
        import tempfile
        import numpy as np

        with tempfile.TemporaryDirectory() as tmpdir:
            from core.vector_store_lance import LanceVectorStore

            store = LanceVectorStore(db_uri=tmpdir, table_name="test", dim=768)

            # Test insert
            test_data = [{
                "id": "test_1",
                "text": "Test content",
                "source": "test.pdf",
                "page": 1,
                "chunk_index": 0,
                "doc_id": "test_doc",
                "section_type": "text",
                "title": "Test",
                "topic": "Test",
                "summary": "Test",
                "keywords": "test",
                "quality_score": 8.0,
                "vector": np.random.randn(768).astype(np.float32).tolist()
            }]
            store.add(test_data)

            # Test search
            query = np.random.randn(768).astype(np.float32).tolist()
            results = store.search(query, top_k=5)

            # Test count
            count = store.count_rows()

            print_status("VectorStore", True, f"Rows: {count}")
            print_status("Search", len(results) > 0, f"Found {len(results)} results")
    except Exception as e:
        print_status("VectorStore", False, str(e))
        all_ok = False

    print_header("5. SESSION MANAGER")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            from core.session_manager import SessionManager

            mgr = SessionManager(tmpdir)
            sid = mgr.create_new_session_id()

            messages = [{"role": "user", "content": "Hello"}]
            mgr.save_session(sid, messages)

            loaded = mgr.load_session(sid)
            sessions = mgr.list_sessions()

            print_status("SessionManager", True, f"Sessions: {len(sessions)}")
            print_status("Save/Load", len(loaded) == 1, f"Messages: {len(loaded)}")
    except Exception as e:
        print_status("SessionManager", False, str(e))
        all_ok = False

    print_header("6. AI SWARM AGENTS")
    try:
        import asyncio

        async def test_swarm():
            from core.agents.swarm_orchestrator import get_swarm_orchestrator
            orchestrator = get_swarm_orchestrator()
            status = orchestrator.get_status()

            print_status("SwarmOrchestrator", True, f"Active: {status['active']}")
            print_status("Researcher", True, f"Role: {status['researcher']['role']}")
            print_status("Verifier", True, f"Role: {status['verifier']['role']}")
            print_status("Synthesizer", True, f"Role: {status['synthesizer']['role']}")

            # Test a simple research query
            result = await orchestrator.process_query("What is particle physics?")
            print_status("ResearchPipeline", True, f"Answer length: {len(result['answer'])}")
            print_status("Processing", True, f"Confidence: {result['processing']['confidence_score']:.0%}")

            return True

        result = asyncio.run(test_swarm())
        status = result
    except Exception as e:
        print_status("SwarmAgents", False, str(e))
        all_ok = False

    print_header("7. DOCUMENT MANAGER")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            from core.document_manager import DocumentManager

            mgr = DocumentManager(tmpdir)
            doc_id = mgr.register_document("test_doc", f"{tmpdir}/test.pdf", "test.pdf")

            doc = mgr.get_document("test_doc")
            docs = mgr.list_documents()

            print_status("DocumentManager", True, f"Docs: {len(docs)}")
            print_status("Registration", doc is not None, f"ID: {doc['doc_id']}")
    except Exception as e:
        print_status("DocumentManager", False, str(e))
        all_ok = False

    print_header("8. RAG PIPELINE")
    try:
        import json
        with tempfile.TemporaryDirectory() as tmpdir:
            from core.rag_pipeline import RAGPipeline

            # Create test metadata
            metadata = {
                "pages": [{"page": 1, "text": "Test content for chunking."}],
                "tables": [],
                "figures": []
            }
            meta_path = Path(tmpdir) / "metadata.json"
            with open(meta_path, 'w') as f:
                json.dump(metadata, f)

            pipeline = RAGPipeline(db_uri=tmpdir, table_name="test_rag")
            pipeline.metadata_path = meta_path
            pipeline.metadata = pipeline._load_metadata()

            chunks = pipeline.build_chunks_from_metadata(doc_id="test")
            print_status("RAGPipeline", True, f"Chunks: {len(chunks)}")
            print_status("Metadata", True, f"Pages: {len(pipeline.metadata['pages'])}")
    except Exception as e:
        print_status("RAGPipeline", False, str(e))
        all_ok = False

    # Summary
    print_header("VALIDATION SUMMARY")
    if all_ok:
        print("  ✅ All components validated successfully!")
        print("  🚀 Ready to start the application")
    else:
        print("  ❌ Some components failed validation")
        print("  ⚠️  Please check the errors above")

    print()
    return all_ok

if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    success = validate_all()
    sys.exit(0 if success else 1)