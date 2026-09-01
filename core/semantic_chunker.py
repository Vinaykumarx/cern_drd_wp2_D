# core/semantic_chunker.py
"""
Semantic Chunker
Splits documents by Markdown headers and page boundaries.
"""

import re
from typing import List, Dict, Any
from core.llm_client import SemanticChunk

class SemanticChunker:
    """
    Deterministic semantic chunker that splits Markdown documents by page boundaries
    (=== PAGE X ===) and Markdown headers to maintain structural context.
    """
    def __init__(self):
        # Regex to match Markdown headers (e.g., # Header, ## Header)
        self.header_pattern = re.compile(r'^(#{1,6})\s+(.*)', re.MULTILINE)
        # Regex to match page boundaries
        self.page_pattern = re.compile(r'=== PAGE (\d+) ===')

    def chunk_document(self, text: str, doc_id: str, page_num: int) -> List[SemanticChunk]:
        """
        Splits single-page text by markdown headers and returns a list of SemanticChunks.
        """
        if not text or not text.strip():
            return []

        chunks = []
        
        # Find all headers to split the text
        matches = list(self.header_pattern.finditer(text))
        
        if not matches:
            # No headers found, treat entire page as one chunk
            return [self._create_chunk(text, f"{doc_id} - Page {page_num}", text, page_num)]

        # Process first block before any header
        first_header_start = matches[0].start()
        if first_header_start > 0:
            pre_text = text[:first_header_start].strip()
            if pre_text:
                chunks.append(self._create_chunk(pre_text, f"{doc_id} - Introduction (Page {page_num})", pre_text, page_num))

        # Process each header section
        for i, match in enumerate(matches):
            header_level = len(match.group(1))
            header_text = match.group(2).strip()
            
            start_pos = match.end()
            end_pos = matches[i+1].start() if i + 1 < len(matches) else len(text)
            
            section_text = text[start_pos:end_pos].strip()
            
            # Re-attach the header to the text for context
            full_text = f"{match.group(1)} {header_text}\n\n{section_text}"
            
            if len(section_text) > 20: # Ignore empty/very short sections
                chunks.append(self._create_chunk(full_text, header_text, section_text, page_num))

        return chunks

    def chunk_document_with_page_markers(self, text: str, doc_id: str) -> List[SemanticChunk]:
        """
        Splits full document text by page markers (=== PAGE X ===) first,
        then chunks each page dynamically.
        """
        if not text or not text.strip():
            return []

        parts = self.page_pattern.split(text)
        if len(parts) <= 1:
            # No page markers found, chunk as page 1
            return self.chunk_document(text, doc_id, 1)

        chunks = []
        # parts[0] is header/empty. We loop through matched pairs: (page_num, content)
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                page_num = int(parts[i])
                page_content = parts[i + 1].strip()
                
                if len(page_content) > 50:
                    page_chunks = self.chunk_document(page_content, doc_id, page_num)
                    chunks.extend(page_chunks)
        return chunks

    def _create_chunk(self, full_text: str, title: str, content: str, page_num: int) -> SemanticChunk:
        """
        Heuristically creates a SemanticChunk object.
        """
        # Generate a naive summary (first sentence)
        summary = content.split('.')[0] + '.' if '.' in content else title
        
        # Generate naive keywords
        words = [w.lower() for w in re.findall(r'\b\w+\b', title + " " + content)]
        keywords = list(set([w for w in words if len(w) > 4]))[:8]
        
        # Determine topic from text content
        topic = "General"
        text_lower = (title + " " + content).lower()
        if any(w in text_lower for w in ["safe", "hazard", "warning", "protect"]):
            topic = "Safety"
        elif any(w in text_lower for w in ["rad", "dose", "sievert", "sv/", "gray", "rem"]):
            topic = "Radiation"
        elif any(w in text_lower for w in ["magnet", "sensor", "detector", "cryo", "hardware", "device"]):
            topic = "Equipment"
        elif any(w in text_lower for w in ["atlas", "cms", "alice", "lhcb", "experiment", "collision"]):
            topic = "Experiment"
        elif any(w in text_lower for w in ["step", "procedure", "how-to", "run", "align", "calibrate"]):
            topic = "Procedure"
        elif any(w in text_lower for w in ["code", "software", "daq", "framework", "algorithm"]):
            topic = "Software"

        return SemanticChunk(
            text=full_text,
            title=title[:100],
            topic=topic,
            summary=summary[:200],
            keywords=keywords if keywords else ["document", "section"],
            why_this_chunk_exists=f"Deterministic header split (Page {page_num})",
            quality_score=8.0
        )
