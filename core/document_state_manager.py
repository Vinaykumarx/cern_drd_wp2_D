# core/document_state_manager.py
"""
Document State Manager - Single Source of Truth for Document Lifecycle

Tracks every document through its lifecycle:
registered → downloading → extracted → chunking → embedding → indexing → verified → failed

This eliminates synchronization issues between extraction, embedding, and LanceDB.
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from enum import Enum


class DocumentState(Enum):
    """Document lifecycle states"""
    UNKNOWN = "unknown"
    REGISTERED = "registered"
    DOWNLOADING = "downloading"
    DOWNLOADED = "downloaded"
    EXTRACTING = "extracting"
    EXTRACTED = "extracted"
    CHUNKING = "chunking"
    CHUNKED = "chunked"
    EMBEDDING = "embedding"
    EMBEDDED = "embedded"
    INDEXING = "indexing"
    INDEXED = "indexed"
    VERIFIED = "verified"
    FAILED = "failed"
    DELETING = "deleting"
    DELETED = "deleted"


class StateTransition:
    """Defines valid state transitions"""
    
    VALID_TRANSITIONS = {
        DocumentState.UNKNOWN: [DocumentState.REGISTERED, DocumentState.DOWNLOADING],
        DocumentState.REGISTERED: [DocumentState.DOWNLOADING, DocumentState.EXTRACTING],
        DocumentState.DOWNLOADING: [DocumentState.DOWNLOADED, DocumentState.FAILED],
        DocumentState.DOWNLOADED: [DocumentState.EXTRACTING, DocumentState.CHUNKING],
        DocumentState.EXTRACTING: [DocumentState.EXTRACTED, DocumentState.INDEXING, DocumentState.FAILED],
        DocumentState.EXTRACTED: [DocumentState.CHUNKING, DocumentState.EMBEDDING, DocumentState.INDEXING],
        DocumentState.CHUNKING: [DocumentState.CHUNKED, DocumentState.FAILED],
        DocumentState.CHUNKED: [DocumentState.EMBEDDING],
        DocumentState.EMBEDDING: [DocumentState.EMBEDDED, DocumentState.INDEXING, DocumentState.FAILED],
        DocumentState.EMBEDDED: [DocumentState.INDEXING],
        DocumentState.INDEXING: [DocumentState.INDEXED, DocumentState.FAILED],
        DocumentState.INDEXED: [DocumentState.VERIFIED, DocumentState.FAILED],
        DocumentState.VERIFIED: [DocumentState.DELETING],
        DocumentState.DELETING: [DocumentState.DELETED, DocumentState.FAILED],
        DocumentState.DELETED: [],
        DocumentState.FAILED: [DocumentState.DOWNLOADING, DocumentState.EXTRACTING, DocumentState.REGISTERED],
    }
    
    @classmethod
    def can_transition(cls, from_state: DocumentState, to_state: DocumentState) -> bool:
        """Check if transition is valid"""
        return to_state in cls.VALID_TRANSITIONS.get(from_state, [])


class DocumentEntry:
    """Single document tracking entry"""
    
    def __init__(self, doc_id: str, filename: str, path: str):
        self.doc_id = doc_id
        self.filename = filename
        self.path = path
        self.state = DocumentState.REGISTERED
        self.previous_state = None
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.metadata: Dict[str, Any] = {}
        self.error_message: Optional[str] = None
        self.retry_count = 0
        self.vector_count = 0
        self.chunk_count = 0
        self.processing_time_ms = 0
        
    def to_dict(self) -> Dict:
        return {
            "doc_id": self.doc_id,
            "filename": self.filename,
            "path": self.path,
            "state": self.state.value,
            "previous_state": self.previous_state.value if self.previous_state else None,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "vector_count": self.vector_count,
            "chunk_count": self.chunk_count,
            "processing_time_ms": self.processing_time_ms,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "DocumentEntry":
        entry = cls(data["doc_id"], data["filename"], data["path"])
        entry.state = DocumentState(data.get("state", "registered"))
        entry.previous_state = DocumentState(data["previous_state"]) if data.get("previous_state") else None
        entry.created_at = data.get("created_at", datetime.now().isoformat())
        entry.updated_at = data.get("updated_at", datetime.now().isoformat())
        entry.metadata = data.get("metadata", {})
        entry.error_message = data.get("error_message")
        entry.retry_count = data.get("retry_count", 0)
        entry.vector_count = data.get("vector_count", 0)
        entry.chunk_count = data.get("chunk_count", 0)
        entry.processing_time_ms = data.get("processing_time_ms", 0)
        return entry


class DocumentStateManager:
    """
    Central authority for document state tracking.
    
    Features:
    - Tracks document lifecycle state
    - Validates state transitions
    - Persists state to disk
    - Provides query methods
    - Auto-healing for stuck documents
    """
    
    def __init__(self, state_file: str = "data/document_states.json"):
        self.state_file = Path(state_file)
        self.documents: Dict[str, DocumentEntry] = {}
        self._load()
        
    def _load(self):
        """Load state from disk"""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    data = json.load(f)
                    for doc_id, entry_data in data.items():
                        self.documents[doc_id] = DocumentEntry.from_dict(entry_data)
                print(f"[StateManager] Loaded {len(self.documents)} document states")
            except Exception as e:
                print(f"[StateManager] Failed to load state: {e}")
                self.documents = {}
    
    def _save(self):
        """Save state to disk"""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            data = {doc_id: entry.to_dict() for doc_id, entry in self.documents.items()}
            # Atomic write - write to temp file then rename
            temp_file = self.state_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)
            os.replace(temp_file, self.state_file)
        except Exception as e:
            print(f"[StateManager] Failed to save state: {e}")
    
    def register(self, doc_id: str, filename: str, path: str) -> DocumentEntry:
        """Register a new document"""
        if doc_id in self.documents:
            return self.documents[doc_id]
        
        entry = DocumentEntry(doc_id, filename, path)
        self.documents[doc_id] = entry
        self._save()
        print(f"[StateManager] Registered: {doc_id}")
        return entry
    
    def transition(self, doc_id: str, new_state: DocumentState, metadata: Dict = None) -> bool:
        """
        Transition document to new state.
        
        Returns True if transition was successful.
        Returns False if transition is invalid (logged as error).
        """
        if doc_id not in self.documents:
            # Auto-register unknown documents
            self.register(doc_id, f"{doc_id}.pdf", f"data/{doc_id}.pdf")
        
        entry = self.documents[doc_id]
        
        if not StateTransition.can_transition(entry.state, new_state):
            if entry.state != new_state:  # Only log if actually different
                print(f"[StateManager] INVALID transition for {doc_id}: {entry.state.value} → {new_state.value}")
            return False
        
        entry.previous_state = entry.state
        entry.state = new_state
        entry.updated_at = datetime.now().isoformat()
        entry.error_message = None  # Clear error on successful transition
        
        if metadata:
            entry.metadata.update(metadata)
            
        if new_state == DocumentState.INDEXED:
            entry.vector_count = metadata.get("vector_count", 0) if metadata else 0
        elif new_state == DocumentState.CHUNKED:
            entry.chunk_count = metadata.get("chunk_count", 0) if metadata else 0
        elif new_state == DocumentState.FAILED:
            entry.error_message = metadata.get("error") if metadata else "Unknown error"
            entry.retry_count += 1
        
        self._save()
        print(f"[StateManager] {doc_id}: {entry.previous_state.value} → {new_state.value}")
        return True
    
    def set_metadata(self, doc_id: str, key: str, value: Any):
        """Set metadata for a document"""
        if doc_id not in self.documents:
            return
        
        entry = self.documents[doc_id]
        entry.metadata[key] = value
        entry.updated_at = datetime.now().isoformat()
        self._save()
    
    def get_state(self, doc_id: str) -> Optional[DocumentState]:
        """Get current state of a document"""
        entry = self.documents.get(doc_id)
        return entry.state if entry else None
    
    def get_entry(self, doc_id: str) -> Optional[DocumentEntry]:
        """Get full entry for a document"""
        return self.documents.get(doc_id)
    
    def get_all_in_state(self, state: DocumentState) -> List[DocumentEntry]:
        """Get all documents in a specific state"""
        return [e for e in self.documents.values() if e.state == state]
    
    def get_stuck_documents(self, timeout_minutes: int = 30) -> List[DocumentEntry]:
        """
        Find documents stuck in processing states too long.
        Used for auto-healing.
        """
        stuck = []
        cutoff = time.time() - (timeout_minutes * 60)
        
        processing_states = [
            DocumentState.DOWNLOADING,
            DocumentState.EXTRACTING,
            DocumentState.CHUNKING,
            DocumentState.EMBEDDING,
            DocumentState.INDEXING,
        ]
        
        for entry in self.documents.values():
            if entry.state in processing_states:
                try:
                    updated = datetime.fromisoformat(entry.updated_at).timestamp()
                    if updated < cutoff:
                        stuck.append(entry)
                except (ValueError, TypeError):
                    stuck.append(entry)
        
        return stuck
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about document states"""
        stats = {
            "total": len(self.documents),
            "by_state": {},
            "failed": [],
            "stuck": [],
        }
        
        for state in DocumentState:
            count = len([e for e in self.documents.values() if e.state == state])
            stats["by_state"][state.value] = count
        
        stats["failed"] = [
            {"doc_id": e.doc_id, "error": e.error_message, "retries": e.retry_count}
            for e in self.documents.values() if e.state == DocumentState.FAILED
        ]
        
        stats["stuck"] = [
            {"doc_id": e.doc_id, "state": e.state.value, "since": e.updated_at}
            for e in self.get_stuck_documents()
        ]
        
        return stats
    
    def get_progress_report(self) -> str:
        """Generate human-readable progress report"""
        stats = self.get_stats()
        
        report = "\n📊 DOCUMENT STATE REPORT\n"
        report += "=" * 50 + "\n\n"
        
        report += "By Status:\n"
        for state, count in stats["by_state"].items():
            if count > 0:
                emoji = {
                    "registered": "📋",
                    "downloading": "⬇️",
                    "extracted": "📄",
                    "chunked": "✂️",
                    "embedded": "🔤",
                    "indexed": "✅",
                    "verified": "✔️",
                    "failed": "❌",
                }.get(state, "❓")
                report += f"  {emoji} {state}: {count}\n"
        
        if stats["failed"]:
            report += "\n❌ Failed Documents:\n"
            for f in stats["failed"][:5]:
                report += f"  - {f['doc_id']}: {f['error']}\n"
        
        if stats["stuck"]:
            report += "\n⏳ Stuck Documents:\n"
            for s in stats["stuck"][:5]:
                report += f"  - {s['doc_id']} (stuck in {s['state']} since {s['since']})\n"
        
        total = stats["by_state"]
        indexed = total.get("indexed", 0) + total.get("verified", 0)
        report += f"\n📈 Overall: {indexed}/{stats['total']} documents fully indexed\n"
        
        return report


# Global instance for easy access
_state_manager: Optional[DocumentStateManager] = None

def get_state_manager() -> DocumentStateManager:
    """Get or create the global state manager instance"""
    global _state_manager
    if _state_manager is None:
        _state_manager = DocumentStateManager()
    return _state_manager