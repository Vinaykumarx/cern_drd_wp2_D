# core/async_chunker.py
"""
Async Semantic Chunker - Non-blocking chunking for FastAPI

Wraps the synchronous SemanticChunker in async operations
to prevent blocking the event loop.
"""

import asyncio
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor

from core.semantic_chunker import SemanticChunker


class AsyncSemanticChunker:
    """
    Async wrapper for SemanticChunker that runs chunking
    in a thread pool to avoid blocking the event loop.
    """
    
    def __init__(self, max_workers: int = 4):
        self.chunker = SemanticChunker()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._chunking_lock = asyncio.Lock()
    
    async def chunk_document(self, text: str, doc_id: str, page_num: int) -> List:
        """
        Async chunking - runs in thread pool.
        """
        loop = asyncio.get_event_loop()
        
        def _chunk():
            return self.chunker.chunk_document(text, doc_id, page_num)
        
        async with self._chunking_lock:
            chunks = await loop.run_in_executor(self.executor, _chunk)
        
        return chunks
    
    async def chunk_batch(self, documents: List[dict]) -> List[dict]:
        """
        Chunk multiple documents concurrently.
        
        Args:
            documents: List of dicts with keys: text, doc_id, page_num
        
        Returns:
            List of dicts with keys: doc_id, page_num, chunks
        """
        loop = asyncio.get_event_loop()
        
        def _chunk_single(doc):
            return {
                "doc_id": doc["doc_id"],
                "page_num": doc["page_num"],
                "chunks": self.chunker.chunk_document(
                    doc["text"], doc["doc_id"], doc["page_num"]
                )
            }
        
        # Process documents in parallel using thread pool
        tasks = [loop.run_in_executor(self.executor, _chunk_single, doc) 
                 for doc in documents]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out any exceptions and return successful results
        successful = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"[AsyncChunker] Error chunking doc {i}: {result}")
            else:
                successful.append(result)
        
        return successful
    
    async def shutdown(self):
        """Shutdown the executor"""
        self.executor.shutdown(wait=True)


# Global async chunker instance
_chunker_instance: Optional[AsyncSemanticChunker] = None

def get_async_chunker() -> AsyncSemanticChunker:
    """Get or create the global async chunker instance"""
    global _chunker_instance
    if _chunker_instance is None:
        _chunker_instance = AsyncSemanticChunker()
    return _chunker_instance


async def chunk_text_async(text: str, doc_id: str = "default", page_num: int = 0) -> List:
    """
    Convenience function for async chunking.
    """
    chunker = get_async_chunker()
    return await chunker.chunk_document(text, doc_id, page_num)