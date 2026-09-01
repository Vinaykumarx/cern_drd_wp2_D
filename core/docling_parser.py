# core/docling_parser.py
"""
Docling PDF Parser
Converts PDF documents to Markdown with page-level markers using IBM Docling.
"""

import os
import sys
from pathlib import Path

def extract_pdf_with_page_markers(pdf_path: str, output_md_path: str) -> bool:
    """
    Converts a PDF to Markdown, inserting === PAGE X === delimiters.
    Uses IBM Docling's layout and table analysis.
    """
    try:
        from docling.document_converter import DocumentConverter
        from docling_core.types.doc.labels import DocItemLabel
    except ImportError:
        print("[Docling Parser] Error: 'docling' library is not installed.")
        print("Please run: pip install docling")
        return False

    pdf_path = str(Path(pdf_path).resolve())
    output_md_path = str(Path(output_md_path).resolve())
    
    print(f"[Docling Parser] Starting conversion for {pdf_path}...")
    
    try:
        converter = DocumentConverter()
        result = converter.convert(pdf_path)
        doc = result.document
        
        pages_content = {}
        
        # Iterate over all document items and group them by page number
        for item, level in doc.iterate_items():
            # Get 1-based page number
            page_num = 1
            if item.prov and len(item.prov) > 0:
                page_num = item.prov[0].page_no
            
            # Format content based on item type
            item_text = ""
            
            # Use item-specific markdown export if available (like for tables)
            if hasattr(item, "export_to_markdown"):
                try:
                    item_text = item.export_to_markdown()
                except Exception:
                    item_text = getattr(item, "text", "")
            else:
                item_text = getattr(item, "text", "")
                
            if not item_text:
                continue
                
            # Add Markdown header prefix if it's a heading
            if item.label == DocItemLabel.TITLE:
                item_text = f"# {item_text}\n"
            elif item.label == DocItemLabel.SECTION_HEADER:
                h_prefix = "#" * min(level + 1, 6)
                item_text = f"\n{h_prefix} {item_text}\n"
            elif item.label == DocItemLabel.LIST_ITEM:
                item_text = f"* {item_text}"
            
            pages_content.setdefault(page_num, []).append(item_text)
            
        # Write the reconstructed markdown with === PAGE X === headers
        os.makedirs(os.path.dirname(output_md_path), exist_ok=True)
        with open(output_md_path, "w", encoding="utf-8") as f:
            for page_num in sorted(pages_content.keys()):
                f.write(f"\n\n=== PAGE {page_num} ===\n\n")
                # Add spacing between elements
                f.write("\n\n".join(pages_content[page_num]))
                
        print(f"[Docling Parser] Successfully saved markdown to {output_md_path}")
        return True
        
    except Exception as e:
        print(f"[Docling Parser] Error converting document: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python docling_parser.py <input_pdf> <output_markdown>")
        sys.exit(1)
    
    extract_pdf_with_page_markers(sys.argv[1], sys.argv[2])
