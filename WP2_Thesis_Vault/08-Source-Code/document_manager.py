# core/document_manager.py
"""
Multi-file document manager for PDFs, JSON, and remote documents.
Handles download, listing, and ingestion tracking.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests


class DocumentManager:
    """
    Manages multiple documents (PDFs, JSON, etc.) for RAG ingestion.
    Tracks document metadata and allows per-document or cross-document queries.
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.metadata_file = self.data_dir / "documents.json"
        self.documents = self._load_documents()

    def _load_documents(self) -> Dict[str, Any]:
        """Load document registry from disk."""
        if self.metadata_file.exists():
            with open(self.metadata_file) as f:
                return json.load(f)
        return {}

    def _save_documents(self) -> None:
        """Save document registry to disk."""
        with open(self.metadata_file, "w") as f:
            json.dump(self.documents, f, indent=2)

    def add_local_pdf(self, pdf_path: str, doc_id: Optional[str] = None) -> str:
        """
        Register a local PDF file.
        Returns: Full path to the PDF file.
        """
        pdf_path = Path(pdf_path).resolve()
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        doc_id = doc_id or pdf_path.stem
        dest = (self.data_dir / pdf_path.name).resolve()

        # Only copy if source and destination are different files
        if pdf_path != dest:
            import shutil
            shutil.copy2(str(pdf_path), str(dest))
            print(f"  ✓ Copied to {dest}")
        else:
            print(f"  ✓ Already in data directory: {dest}")

        self.documents[doc_id] = {
            "type": "pdf",
            "filename": pdf_path.name,
            "path": str(dest),
            "doc_id": doc_id,
            "status": "registered",
        }
        self._save_documents()
        return str(dest)

    def add_remote_pdf(self, url: str, doc_id: Optional[str] = None) -> str:
        """
        Download and register a remote PDF from a URL.

        This method is tolerant of "record" pages (e.g. CERN) or other HTML
        landing pages.  It will fetch the URL once and inspect the response.  If
        the content does not look like a PDF (either by content-type header or by
        the first few bytes), it will attempt to parse the HTML body for the
        first link that ends with ``.pdf`` or contains ``/files/`` and re-fetch
        using that link instead.  This means you can hand it either the direct
        PDF link or a record page URL and the correct file will be downloaded.

        Returns: Full path to the downloaded PDF file.
        """
        def _is_pdf_bytes(b: bytes) -> bool:
            # PDF files begin with "%PDF-"
            return b.startswith(b"%PDF")

        def _search_pdf_link(html: str) -> Optional[str]:
            # Look for href="...pdf" or /files/... patterns
            import re

            patterns = [r'href=["\']([^"\']*\.pdf[^"\']*)["\']',
                        r'href=["\']([^"\']*?/files/[^"\']*)["\']']
            for pat in patterns:
                for match in re.findall(pat, html, re.IGNORECASE):
                    # make absolute if necessary
                    if match.startswith("http"):
                        return match
                    else:
                        return f"{requests.utils.urlparse(url).scheme}://{requests.utils.urlparse(url).netloc}{match}"
            return None

        # first attempt
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
        except Exception as e:
            raise RuntimeError(f"Failed to download from {url}: {e}")

        content = resp.content
        # if we got HTML or something that doesn't look like a PDF, try to find
        # the real PDF link
        if not _is_pdf_bytes(content):
            text = resp.text
            pdf_link = _search_pdf_link(text)
            if pdf_link:
                print(f"[DocMgr] resolved PDF link from HTML: {pdf_link}")
                try:
                    resp = requests.get(pdf_link, timeout=30)
                    resp.raise_for_status()
                    content = resp.content
                    url = pdf_link
                except Exception as e:
                    raise RuntimeError(f"Failed to download resolved PDF {pdf_link}: {e}")
            else:
                print(f"[DocMgr] warning: response from {url} is not a PDF and no\n" \
                      "               candidate link was found.  Saving anyway.")

        # Extract filename from URL or use doc_id
        filename = url.split("/")[-1] or f"{doc_id}.pdf"
        if not filename.endswith(".pdf"):
            filename += ".pdf"

        doc_id = doc_id or Path(filename).stem

        dest = self.data_dir / filename
        with open(dest, "wb") as f:
            f.write(content)

        self.documents[doc_id] = {
            "type": "pdf",
            "url": url,
            "filename": filename,
            "path": str(dest),
            "doc_id": doc_id,
            "status": "registered",
        }
        self._save_documents()
        print(f"[DocMgr] Downloaded {filename} as {doc_id}")
        return str(dest.resolve())

    def list_documents(self) -> List[Dict[str, Any]]:
        """Return list of all registered documents."""
        return list(self.documents.values())

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document metadata by ID."""
        return self.documents.get(doc_id)

    def get_pdf_path(self, doc_id: str) -> Optional[Path]:
        """Get the local file path for a PDF's doc_id."""
        doc = self.documents.get(doc_id)
        if doc and doc.get("type") == "pdf":
            path = Path(doc["path"])
            if path.exists():
                return path
        return None

    def delete_document(self, doc_id: str) -> bool:
        """Remove a document from registry and optionally delete file."""
        if doc_id in self.documents:
            del self.documents[doc_id]
            self._save_documents()
            return True
        return False

    def update_status(self, doc_id: str, status: str) -> None:
        """Update document ingestion status (e.g., 'extracted', 'indexed')."""
        if doc_id in self.documents:
            self.documents[doc_id]["status"] = status
            self._save_documents()

    def register_document(self, doc_id: str, pdf_path: str, filename: str) -> None:
        """Register an uploaded/processed document in the registry."""
        self.documents[doc_id] = {
            "type": "pdf",
            "filename": filename,
            "path": pdf_path,
            "doc_id": doc_id,
            "status": "indexed",
        }
        self._save_documents()
        print(f"[DocMgr] Registered {doc_id} → {pdf_path}")

