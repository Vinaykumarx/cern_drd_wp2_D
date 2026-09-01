#!/usr/bin/env python3
"""
Comprehensive Test Suite for CERN Multimodal RAG - Agent Zero

This test suite verifies:
1. Document State Manager - lifecycle tracking
2. Health Monitor - system monitoring
3. Async Chunker - non-blocking operations
4. Vector Store - LanceDB operations
5. Agent Swarm - orchestration and research
6. Session Manager - conversation management
7. RAG Pipeline - chunking and indexing
8. Document Manager - document registration
"""

import unittest
import asyncio
import json
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import modules at top level for availability across tests
from core.document_state_manager import DocumentStateManager, DocumentState, StateTransition
from core.health_monitor import HealthMonitor, HealthCheckResult, SystemMetrics

# Test configuration
TEST_DATA_DIR = Path(__file__).parent / "test_data"
TEST_LANCEDB_DIR = Path(__file__).parent / "test_lancedb"


class TestDocumentStateManager(unittest.TestCase):
    """Test DocumentStateManager functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_file = TEST_DATA_DIR / "test_states.json"
        self.test_file.parent.mkdir(parents=True, exist_ok=True)

        # Create a fresh state file for each test
        if self.test_file.exists():
            self.test_file.unlink()

        from core.document_state_manager import DocumentStateManager, DocumentState, StateTransition
        self.state_mgr = DocumentStateManager(str(self.test_file))
        self.DocumentState = DocumentState
        self.StateTransition = StateTransition

    def tearDown(self):
        """Clean up test files"""
        if self.test_file.exists():
            self.test_file.unlink()

    def test_01_register_document(self):
        """Test document registration"""
        entry = self.state_mgr.register("test_doc", "test.pdf", "/data/test.pdf")

        self.assertEqual(entry.doc_id, "test_doc")
        self.assertEqual(entry.state, self.DocumentState.REGISTERED)
        self.assertEqual(entry.filename, "test.pdf")
        self.assertTrue(self.test_file.exists())

    def test_02_valid_transitions(self):
        """Test valid state transitions"""
        self.state_mgr.register("test_doc", "test.pdf", "/data/test.pdf")

        # Test transitioning through valid states
        result = self.state_mgr.transition("test_doc", self.DocumentState.DOWNLOADING)
        self.assertTrue(result)

        result = self.state_mgr.transition("test_doc", self.DocumentState.DOWNLOADED)
        self.assertTrue(result)

        result = self.state_mgr.transition("test_doc", self.DocumentState.EXTRACTING)
        self.assertTrue(result)

        # Verify state is updated
        state = self.state_mgr.get_state("test_doc")
        self.assertEqual(state, self.DocumentState.EXTRACTING)

    def test_03_invalid_transition(self):
        """Test that invalid transitions are rejected"""
        self.state_mgr.register("test_doc", "test.pdf", "/data/test.pdf")

        # Try invalid transition: REGISTERED -> INDEXED (skipping steps)
        result = self.state_mgr.transition("test_doc", self.DocumentState.INDEXED)
        self.assertFalse(result)

    def test_04_metadata_tracking(self):
        """Test metadata storage with transitions"""
        self.state_mgr.register("test_doc", "test.pdf", "/data/test.pdf")

        # Use valid transitions and add metadata
        self.state_mgr.transition("test_doc", self.DocumentState.DOWNLOADING)
        self.state_mgr.transition("test_doc", self.DocumentState.DOWNLOADED, {
            "vector_count": 100,
            "chunk_count": 10
        })

        entry = self.state_mgr.get_entry("test_doc")
        # Metadata is accumulated across transitions
        self.assertIn("vector_count", entry.metadata)
        self.assertIn("chunk_count", entry.metadata)

    def test_05_stuck_document_detection(self):
        """Test detection of stuck documents"""
        self.state_mgr.register("stuck_doc", "stuck.pdf", "/data/stuck.pdf")
        self.state_mgr.transition("stuck_doc", self.DocumentState.EXTRACTING)

        # Manually set old timestamp to simulate stuck document
        entry = self.state_mgr.get_entry("stuck_doc")
        entry.updated_at = (datetime.now().timestamp() - 3600)  # 1 hour ago

        stuck = self.state_mgr.get_stuck_documents(timeout_minutes=30)
        self.assertEqual(len(stuck), 1)
        self.assertEqual(stuck[0].doc_id, "stuck_doc")

    def test_06_state_persistence(self):
        """Test that state persists across instances"""
        self.state_mgr.register("persist_doc", "persist.pdf", "/data/persist.pdf")
        # Go through valid transitions
        self.state_mgr.transition("persist_doc", self.DocumentState.DOWNLOADING)
        self.state_mgr.transition("persist_doc", self.DocumentState.DOWNLOADED)
        self.state_mgr.transition("persist_doc", self.DocumentState.EXTRACTING)
        self.state_mgr.transition("persist_doc", self.DocumentState.EXTRACTED)

        # Create new instance with the same file
        new_mgr = DocumentStateManager(str(self.test_file))
        from core.document_state_manager import DocumentState as DS

        state = new_mgr.get_state("persist_doc")
        self.assertEqual(state, DS.EXTRACTED)


class TestHealthMonitor(unittest.TestCase):
    """Test HealthMonitor functionality"""

    def setUp(self):
        """Set up test fixtures"""
        TEST_LANCEDB_DIR.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """Clean up test files"""
        if TEST_LANCEDB_DIR.exists():
            shutil.rmtree(TEST_LANCEDB_DIR)

    def test_01_health_monitor_creation(self):
        """Test health monitor instantiation"""
        from core.health_monitor import HealthMonitor
        monitor = HealthMonitor(str(Path(__file__).parent.parent))
        self.assertIsNotNone(monitor)

    def test_02_system_metrics(self):
        """Test system metrics collection"""
        from core.health_monitor import HealthMonitor
        monitor = HealthMonitor(str(Path(__file__).parent.parent))

        metrics = monitor.get_metrics()

        self.assertIsInstance(metrics, SystemMetrics)
        self.assertTrue(hasattr(metrics, "cpu_percent"))
        self.assertTrue(hasattr(metrics, "memory_percent"))
        self.assertTrue(hasattr(metrics, "timestamp"))

    def test_03_lancedb_health_check(self):
        """Test LanceDB health check"""
        from core.health_monitor import LanceDBHealthChecker
        checker = LanceDBHealthChecker(str(TEST_LANCEDB_DIR))

        result = asyncio.run(checker.check())
        self.assertIsInstance(result, HealthCheckResult)
        self.assertIn(result.status, ["warning", "healthy", "critical"])

    def test_04_filesystem_health_check(self):
        """Test filesystem health check"""
        from core.health_monitor import FileSystemHealthChecker
        checker = FileSystemHealthChecker(str(Path(__file__).parent.parent))

        result = asyncio.run(checker.check())
        self.assertIsInstance(result, HealthCheckResult)
        self.assertIn(result.status, ["healthy", "warning"])


class TestAsyncChunker(unittest.IsolatedAsyncioTestCase):
    """Test AsyncSemanticChunker functionality"""

    async def asyncSetUp(self):
        """Set up test fixtures"""
        from core.async_chunker import AsyncSemanticChunker
        self.chunker = AsyncSemanticChunker()

    async def test_01_chunk_document(self):
        """Test async chunking"""
        text = """
# Header One

This is some content under header one.

## Header Two

This is content under header two.

### Header Three

More content here.
"""

        chunks = await self.chunker.chunk_document(text, "test_doc", 1)

        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 0)

        # Check first chunk has required fields
        first_chunk = chunks[0]
        self.assertIn("text", first_chunk.__dict__ or dir(first_chunk))

    async def test_02_batch_chunking(self):
        """Test batch chunking"""
        documents = [
            {"text": "# Doc 1\nContent for document 1", "doc_id": "doc1", "page_num": 1},
            {"text": "# Doc 2\nContent for document 2", "doc_id": "doc2", "page_num": 1},
        ]

        results = await self.chunker.chunk_batch(documents)

        self.assertEqual(len(results), 2)
        self.assertIn("doc_id", results[0])
        self.assertIn("chunks", results[0])


class TestVectorStore(unittest.TestCase):
    """Test LanceVectorStore functionality"""

    def setUp(self):
        """Set up test fixtures"""
        TEST_LANCEDB_DIR.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """Clean up test files"""
        if TEST_LANCEDB_DIR.exists():
            shutil.rmtree(TEST_LANCEDB_DIR)

    def test_01_create_store(self):
        """Test vector store creation"""
        from core.vector_store_lance import LanceVectorStore
        store = LanceVectorStore(
            db_uri=str(TEST_LANCEDB_DIR),
            table_name="test_table",
            dim=768
        )
        self.assertIsNotNone(store)

    def test_02_insert_and_search(self):
        """Test basic insert and search operations"""
        import numpy as np
        from core.vector_store_lance import LanceVectorStore

        store = LanceVectorStore(
            db_uri=str(TEST_LANCEDB_DIR),
            table_name="test_table",
            dim=768
        )

        # Insert test data
        test_rows = [
            {
                "id": "test_1",
                "text": "Test content",
                "source": "test.pdf",
                "page": 1,
                "chunk_index": 0,
                "doc_id": "test_doc",
                "section_type": "text",
                "title": "Test Section",
                "topic": "Test",
                "summary": "Test summary",
                "keywords": "test, content",
                "quality_score": 8.0,
                "vector": np.random.randn(768).astype(np.float32).tolist()
            }
        ]

        store.add(test_rows)

        # Search
        query_vector = np.random.randn(768).astype(np.float32).tolist()
        results = store.search(query_vector, top_k=5)

        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)

    def test_03_count_rows(self):
        """Test row counting"""
        import numpy as np
        from core.vector_store_lance import LanceVectorStore

        store = LanceVectorStore(
            db_uri=str(TEST_LANCEDB_DIR),
            table_name="test_table",
            dim=768
        )

        # Add some data
        for i in range(5):
            store.add([{
                "id": f"row_{i}",
                "text": f"Content {i}",
                "source": "test.pdf",
                "page": i,
                "chunk_index": i,
                "doc_id": "test_doc",
                "section_type": "text",
                "title": f"Section {i}",
                "topic": "Test",
                "summary": f"Summary {i}",
                "keywords": "test",
                "quality_score": 8.0,
                "vector": np.random.randn(768).astype(np.float32).tolist()
            }])

        count = store.count_rows()
        self.assertEqual(count, 5)

    def test_04_verify_document_vectors(self):
        """Test document verification"""
        import numpy as np
        from core.vector_store_lance import LanceVectorStore

        store = LanceVectorStore(
            db_uri=str(TEST_LANCEDB_DIR),
            table_name="test_table",
            dim=768
        )

        # Add data with specific doc_id
        store.add([{
            "id": "verify_1",
            "text": "Verify content",
            "source": "test.pdf",
            "page": 1,
            "chunk_index": 0,
            "doc_id": "verify_doc",
            "section_type": "text",
            "title": "Verify Section",
            "topic": "Test",
            "summary": "Verify summary",
            "keywords": "verify",
            "quality_score": 8.0,
            "vector": np.random.randn(768).astype(np.float32).tolist()
        }])

        result = store.verify_document_vectors("verify_doc")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["vector_count"], 1)


class TestAgentSwarm(unittest.IsolatedAsyncioTestCase):
    """Test AI Swarm functionality"""

    async def asyncSetUp(self):
        """Set up test fixtures"""
        from core.agents.swarm_orchestrator import get_swarm_orchestrator
        self.orchestrator = get_swarm_orchestrator()

    async def test_01_orchestrator_creation(self):
        """Test orchestrator instantiation"""
        self.assertIsNotNone(self.orchestrator)

    async def test_02_get_status(self):
        """Test orchestrator status"""
        status = self.orchestrator.get_status()

        self.assertIn("active", status)
        self.assertIn("researcher", status)
        self.assertIn("verifier", status)
        self.assertIn("synthesizer", status)

    async def test_03_process_research_query(self):
        """Test basic research query processing"""
        # This test will use mock data since we don't have real API keys
        result = await self.orchestrator.process_query(
            query="test query for research",
            user_goal="test goal"
        )

        self.assertIn("query", result)
        self.assertIn("processing", result)
        self.assertIn("answer", result)

    async def test_04_reset(self):
        """Test orchestrator reset"""
        self.orchestrator.reset()
        status = self.orchestrator.get_status()

        self.assertFalse(status["active"])


class TestSessionManager(unittest.TestCase):
    """Test SessionManager functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_db_dir = TEST_DATA_DIR / "sessions"
        self.test_db_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """Clean up test files"""
        if self.test_db_dir.exists():
            shutil.rmtree(self.test_db_dir)

    def test_01_create_session(self):
        """Test session creation"""
        from core.session_manager import SessionManager
        mgr = SessionManager(str(self.test_db_dir))

        session_id = mgr.create_new_session_id()
        self.assertIsNotNone(session_id)
        self.assertTrue(session_id.startswith("session_"))

    def test_02_save_and_load(self):
        """Test saving and loading messages"""
        from core.session_manager import SessionManager
        mgr = SessionManager(str(self.test_db_dir))

        session_id = mgr.create_new_session_id()

        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]

        mgr.save_session(session_id, messages)

        loaded = mgr.load_session(session_id)
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0]["role"], "user")

    def test_03_list_sessions(self):
        """Test listing sessions"""
        from core.session_manager import SessionManager
        mgr = SessionManager(str(self.test_db_dir))

        # Create multiple sessions
        sid1 = mgr.create_new_session_id()
        sid2 = mgr.create_new_session_id()

        mgr.save_session(sid1, [{"role": "user", "content": "Test 1"}])
        mgr.save_session(sid2, [{"role": "user", "content": "Test 2"}])

        sessions = mgr.list_sessions()
        self.assertEqual(len(sessions), 2)

    def test_04_delete_session(self):
        """Test deleting a session"""
        from core.session_manager import SessionManager
        mgr = SessionManager(str(self.test_db_dir))

        session_id = mgr.create_new_session_id()
        mgr.save_session(session_id, [{"role": "user", "content": "Test"}])

        # Delete the session
        result = mgr.delete_session(session_id)
        self.assertTrue(result)

        # Verify it's gone
        sessions = mgr.list_sessions()
        self.assertEqual(len(sessions), 0)

    def test_05_clear_sessions(self):
        """Test clearing all sessions"""
        from core.session_manager import SessionManager
        mgr = SessionManager(str(self.test_db_dir))

        # Create multiple sessions
        for i in range(3):
            sid = mgr.create_new_session_id()
            mgr.save_session(sid, [{"role": "user", "content": f"Test {i}"}])

        # Clear all
        result = mgr.clear_sessions()
        self.assertTrue(result)

        sessions = mgr.list_sessions()
        self.assertEqual(len(sessions), 0)


class TestRAGPipeline(unittest.TestCase):
    """Test RAGPipeline functionality"""

    def setUp(self):
        """Set up test fixtures"""
        TEST_LANCEDB_DIR.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """Clean up test files"""
        if TEST_LANCEDB_DIR.exists():
            shutil.rmtree(TEST_LANCEDB_DIR)

    def test_01_pipeline_creation(self):
        """Test pipeline instantiation"""
        from core.rag_pipeline import RAGPipeline

        pipeline = RAGPipeline(
            db_uri=str(TEST_LANCEDB_DIR),
            table_name="test_pipeline"
        )

        self.assertIsNotNone(pipeline)
        self.assertIsNotNone(pipeline.embed_model)
        self.assertIsNotNone(pipeline.reranker)

    def test_02_build_chunks(self):
        """Test chunk building from metadata"""
        from core.rag_pipeline import RAGPipeline

        # Create test metadata with proper structure
        test_metadata = {
            "pages": [
                {"page": 1, "text": "This is a test page with some content. It has multiple sentences to test chunking behavior."}
            ],
            "tables": [],
            "figures": []
        }

        # Write to temp file
        metadata_file = TEST_DATA_DIR / "test_metadata.json"
        metadata_file.parent.mkdir(parents=True, exist_ok=True)

        with open(metadata_file, 'w') as f:
            json.dump(test_metadata, f)

        pipeline = RAGPipeline(
            db_uri=str(TEST_LANCEDB_DIR),
            table_name="test_chunks"
        )

        # Set metadata path AND reload metadata
        pipeline.metadata_path = metadata_file
        pipeline.metadata = pipeline._load_metadata()

        chunks = pipeline.build_chunks_from_metadata(doc_id="test_doc")

        self.assertIsInstance(chunks, list)
        # Should have at least one chunk from the page text
        self.assertGreater(len(chunks), 0)

        # Clean up
        if metadata_file.exists():
            metadata_file.unlink()


class TestDocumentManager(unittest.TestCase):
    """Test DocumentManager functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_data_dir = TEST_DATA_DIR / "documents"
        self.test_data_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """Clean up test files"""
        if self.test_data_dir.exists():
            shutil.rmtree(self.test_data_dir)

    def test_01_create_manager(self):
        """Test document manager instantiation"""
        from core.document_manager import DocumentManager
        mgr = DocumentManager(str(self.test_data_dir))
        self.assertIsNotNone(mgr)

    def test_02_register_document(self):
        """Test document registration"""
        from core.document_manager import DocumentManager
        mgr = DocumentManager(str(self.test_data_dir))

        doc_id = mgr.register_document(
            "test_doc",
            str(self.test_data_dir / "test.pdf"),
            "test.pdf"
        )

        doc = mgr.get_document("test_doc")
        self.assertIsNotNone(doc)
        self.assertEqual(doc["doc_id"], "test_doc")

    def test_03_update_status(self):
        """Test status update"""
        from core.document_manager import DocumentManager
        mgr = DocumentManager(str(self.test_data_dir))

        mgr.register_document("test_doc", str(self.test_data_dir / "test.pdf"), "test.pdf")
        mgr.update_status("test_doc", "indexed")

        doc = mgr.get_document("test_doc")
        self.assertEqual(doc["status"], "indexed")


def run_tests():
    """Run all tests and generate report"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDocumentStateManager))
    suite.addTests(loader.loadTestsFromTestCase(TestHealthMonitor))
    suite.addTests(loader.loadTestsFromTestCase(TestVectorStore))
    suite.addTests(loader.loadTestsFromTestCase(TestSessionManager))
    suite.addTests(loader.loadTestsFromTestCase(TestRAGPipeline))
    suite.addTests(loader.loadTestsFromTestCase(TestDocumentManager))

    # Run tests with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {'YES ✅' if result.wasSuccessful() else 'NO ❌'}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    success = run_tests()
    sys.exit(0 if success else 1)