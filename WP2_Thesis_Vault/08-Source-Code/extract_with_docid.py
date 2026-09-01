"""
Extraction wrapper that processes arbitrary PDFs with doc_id tracking.
Allows ingesting multiple PDFs and maintaining separate document metadata.
"""

import sys
import json
import subprocess
from pathlib import Path
import shutil
import os
from typing import Dict, Any, List

BASE = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE / 'outputs'
DATA_DIR = BASE / 'data'
OUTPUTS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)


def extract_pdf_with_docid(pdf_path: str, doc_id: str, force_reprocess: bool = False):
    """
    Extract text, tables, images, graphs, and captions from a PDF.
    
    Args:
        pdf_path: Full path to PDF file (local or downloaded to data dir)
        doc_id: Unique document identifier (e.g., "cern_205520", "default")
        force_reprocess: If True, reprocess even if outputs already exist
    
    Returns:
        dict: Metadata about the extraction process
    """
    
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF path not found: {pdf_path}")
    
    print(f"\n{'='*60}")
    print(f"Extracting document: {doc_id}")
    print(f"PDF: {pdf_path}")
    print(f"{'='*60}\n")
    
    # Create doc-specific output directory
    doc_outputs_dir = OUTPUTS_DIR / doc_id
    doc_outputs_dir.mkdir(exist_ok=True)
    
    # Check if already processed
    metadata_file = doc_outputs_dir / 'metadata.json'
    if metadata_file.exists() and not force_reprocess:
        print(f"✓ Document {doc_id} already extracted. Use force_reprocess=True to re-run.")
        with open(metadata_file, 'r') as f:
            return json.load(f)
    
    # Copy PDF to data directory for processing (extraction scripts expect it there)
    pdf_copy_path = DATA_DIR / f"{doc_id}.pdf"
    pdf_path_resolved = Path(pdf_path).resolve()
    pdf_copy_resolved = pdf_copy_path.resolve()
    
    # Only copy if source and dest are different
    if pdf_path_resolved != pdf_copy_resolved:
        shutil.copy2(str(pdf_path), str(pdf_copy_path))
        print(f"✓ Copied PDF to {pdf_copy_path}")
    else:
        print(f"✓ PDF already at {pdf_copy_path}")
        pdf_copy_path = pdf_path_resolved
    
    # Extract text using Semantic Markdown Engine
    print(f"\n[1/5] Extracting layouts natively with Multi-Modal Markdown Parsing...")
    _extract_markdown_docid(pdf_copy_path, doc_id, doc_outputs_dir)
    _recover_sparse_text_pages(pdf_copy_path, doc_outputs_dir)
    
    # Extract CSV tables using robust pdfplumber
    print(f"[2/5] Extracting robust CSV tables...")
    _extract_tables_docid(pdf_copy_path, doc_id, doc_outputs_dir)
    
    # Extract images
    print(f"[3/5] Extracting images...")
    _extract_images_docid(pdf_copy_path, doc_id, doc_outputs_dir)
    
    # Detect graphs
    print(f"[4/5] Detecting graphs...")
    _extract_graphs_docid(doc_id, doc_outputs_dir)
    
    # Caption images
    print(f"[5/5] Captioning images...")
    _caption_images_docid(doc_id, doc_outputs_dir)
    
    # Build metadata
    print(f"\n[Final] Building metadata...")
    metadata = _build_metadata_docid(doc_id, doc_outputs_dir)
    
    # Save metadata
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Clean up temporary PDF copy
    pdf_copy_path.unlink()
    print(f"✓ Cleaned up temp PDF copy")
    
    print(f"\n✓ Document {doc_id} extraction complete!")
    print(f"  Outputs: {doc_outputs_dir}")
    print(f"  - pages_text.json")
    print(f"  - tables_index.json")
    print(f"  - figures_index.json")
    print(f"  - metadata.json")
    
    return metadata


def _load_pages(output_dir: Path) -> List[Dict[str, Any]]:
    pages_file = output_dir / "pages_text.json"
    if not pages_file.exists():
        return []
    with open(pages_file, "r") as f:
        return json.load(f)


def _save_pages(output_dir: Path, pages: List[Dict[str, Any]]) -> None:
    pages_file = output_dir / "pages_text.json"
    with open(pages_file, "w") as f:
        json.dump(pages, f, indent=2)


def _recover_sparse_text_pages(pdf_path: Path, output_dir: Path) -> None:
    """
    Recovery hook for scanned PDFs:
    - Detect overly sparse text extraction.
    - Re-run sparse pages with PyMuPDF plain-text extraction.
    - Optionally run OCR if pytesseract is available.
    - If still sparse, use VLM extraction.
    """
    pages = _load_pages(output_dir)
    if not pages:
        return

    lengths = [len((p.get("text") or "").strip()) for p in pages]
    sparse_pages = [i for i, n in enumerate(lengths) if n < 80]
    sparse_ratio = len(sparse_pages) / max(len(pages), 1)

    # Only run recovery when output is clearly bad to avoid unnecessary overhead.
    if sparse_ratio < 0.6:
        return

    print(f"  ! Sparse extraction detected ({len(sparse_pages)}/{len(pages)} pages). Running text recovery...")
    import fitz
    doc = fitz.open(str(pdf_path))
    ocr_available = False
    try:
        import pytesseract  # type: ignore
        from PIL import Image
        import io
        ocr_available = True
    except Exception:
        ocr_available = False

    recovered = 0
    pages_to_vlm = []
    
    for idx in sparse_pages:
        page = doc[idx]
        text = page.get_text("text").strip()

        if len(text) < 80 and ocr_available:
            try:
                pix = page.get_pixmap(dpi=200)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                text = pytesseract.image_to_string(img).strip()
            except Exception:
                pass

        if len(text) >= 80:
            pages[idx]["text"] = text
            recovered += 1
        else:
            pages_to_vlm.append(idx)

    # Save the pages after plain-text/OCR recovery so that VLM skips already recovered pages
    _save_pages(output_dir, pages)
    
    # If still sparse and VLM is likely needed, try Qwen2-VL
    if pages_to_vlm and sparse_ratio > 0.8:
        print(f"  ! Still sparse after basic recovery. Attempting VLM extraction for {len(pages_to_vlm)} pages...")
        try:
            from extraction.extract_vlm_layout import extract_vlm_docid
            extract_vlm_docid(pdf_path, pages[0]['doc_id'], output_dir)
            # Reload pages after VLM
            pages = _load_pages(output_dir)
            recovered = len([p for p in pages if len(p.get('text', '')) > 80])
        except ImportError:
            print("  ! VLM extractor (Qwen2-VL) dependencies not found. Skipping VLM recovery.")
        except Exception as e:
            print(f"  ! VLM recovery failed: {e}")

    _save_pages(output_dir, pages)
    print(f"  ✓ Recovered text for {recovered} pages total")


def _extract_markdown_docid(pdf_path: Path, doc_id: str, output_dir: Path):
    """Extract semantic Markdown from PDF using IBM Docling (with fallback to pymupdf4llm)."""
    
    # 1. Try IBM Docling
    try:
        from docling.document_converter import DocumentConverter
        from docling_core.types.doc.labels import DocItemLabel
        
        print(f"  → Running IBM Docling converter for page-aware extraction...")
        converter = DocumentConverter()
        result = converter.convert(str(pdf_path))
        doc = result.document
        
        pages_content = {}
        for item, level in doc.iterate_items():
            page_num = 1
            if item.prov and len(item.prov) > 0:
                page_num = item.prov[0].page_no
                
            item_text = ""
            if hasattr(item, "export_to_markdown"):
                try:
                    item_text = item.export_to_markdown()
                except Exception:
                    item_text = getattr(item, "text", "")
            else:
                item_text = getattr(item, "text", "")
                
            if not item_text:
                continue
                
            if item.label == DocItemLabel.TITLE:
                item_text = f"# {item_text}\n"
            elif item.label == DocItemLabel.SECTION_HEADER:
                h_prefix = "#" * min(level + 1, 6)
                item_text = f"\n{h_prefix} {item_text}\n"
            elif item.label == DocItemLabel.LIST_ITEM:
                item_text = f"* {item_text}"
                
            pages_content.setdefault(page_num, []).append(item_text)
            
        pages = []
        full_md_with_markers = []
        
        # Docling page numbers are 1-based
        for page_num in sorted(pages_content.keys()):
            page_text = "\n\n".join(pages_content[page_num])
            pages.append({
                'page': page_num,
                'text': page_text.strip(),
                'doc_id': doc_id
            })
            full_md_with_markers.append(f"\n\n=== PAGE {page_num} ===\n\n" + page_text.strip())
            
        # Write pages_text.json
        output_file = output_dir / 'pages_text.json'
        with open(output_file, 'w') as f:
            json.dump(pages, f, indent=2)
            
        # Write the supervisor-expected merged markdown with markers
        merged_md_file = output_dir / f"{doc_id}_with_pages.md"
        with open(merged_md_file, 'w', encoding='utf-8') as f:
            f.write("".join(full_md_with_markers))
            
        print(f"  ✓ IBM Docling extracted {len(pages)} pages successfully")
        return
        
    except Exception as e:
        print(f"  ! IBM Docling extraction failed/not installed: {e}. Falling back to pymupdf4llm...")

    # 2. Fallback to pymupdf4llm
    import pymupdf4llm
    import fitz
    
    doc = fitz.open(str(pdf_path))
    pages = []
    full_md_with_markers = []
    
    for i in range(len(doc)):
        try:
            md_text = pymupdf4llm.to_markdown(str(pdf_path), pages=[i])
            pages.append({
                'page': i + 1,
                'text': md_text.strip(),
                'doc_id': doc_id
            })
            full_md_with_markers.append(f"\n\n=== PAGE {i + 1} ===\n\n" + md_text.strip())
        except Exception as e:
            print(f"  ! Error extracting page {i+1}: {e}")
            pages.append({
                'page': i + 1,
                'text': "",
                'doc_id': doc_id
            })
            
    output_file = output_dir / 'pages_text.json'
    with open(output_file, 'w') as f:
        json.dump(pages, f, indent=2)
        
    # Write the supervisor-expected merged markdown with markers
    merged_md_file = output_dir / f"{doc_id}_with_pages.md"
    with open(merged_md_file, 'w', encoding='utf-8') as f:
        f.write("".join(full_md_with_markers))
    
    print(f"  ✓ Extracted Markdown from {len(pages)} pages with page markers")


def _extract_tables_docid(pdf_path: Path, doc_id: str, output_dir: Path):
    """Extract tables from PDF using pdfplumber with Camelot fallback."""
    import pdfplumber
    
    tables_index = {}
    table_counter = 0
    
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            page_tables = page.extract_tables()
            
            # If pdfplumber doesn't find tables, try Camelot as fallback
            if not page_tables:
                try:
                    import camelot
                    # Try lattice method first (better for tables with lines)
                    camelot_tables = camelot.read_pdf(str(pdf_path), pages=str(page_num), flavor='lattice')
                    if len(camelot_tables) == 0:
                        # Try stream method (better for whitespace-separated tables)
                        camelot_tables = camelot.read_pdf(str(pdf_path), pages=str(page_num), flavor='stream')
                    
                    if len(camelot_tables) > 0:
                        page_tables = []
                        for table in camelot_tables:
                            # Convert Camelot table to list of lists format
                            df = table.df
                            # Handle empty tables
                            if df.empty:
                                continue
                            # Convert DataFrame to list of lists
                            table_data = [df.columns.tolist()] + df.values.tolist()
                            # Clean up empty cells
                            table_data = [[str(cell) if cell is not None else '' for cell in row] for row in table_data]
                            page_tables.append(table_data)
                except Exception as e:
                    # If Camelot fails, continue with pdfplumber results (which may be empty)
                    print(f"    ! Camelot extraction failed for page {page_num}: {e}")
            
            if page_tables:
                for t_idx, table in enumerate(page_tables, 1):
                    table_counter += 1
                    table_id = f"page_{page_num}_table_{t_idx}"
                    
                    # Save as CSV
                    csv_file = output_dir / f"{table_id}.csv"
                    df = _table_to_df(table)
                    df.to_csv(csv_file, index=False)
                    
                    tables_index[table_id] = {
                        'page': page_num,
                        'index': t_idx,
                        'csv_file': str(csv_file),
                        'doc_id': doc_id
                    }
    
    index_file = output_dir / 'tables_index.json'
    with open(index_file, 'w') as f:
        json.dump(tables_index, f, indent=2)
    
    print(f"  ✓ Extracted {table_counter} tables")


def _table_to_df(table):
    """Convert pdfplumber table to pandas DataFrame."""
    import pandas as pd
    
    if not table or len(table) == 0:
        return pd.DataFrame()
    
    headers = table[0] if table else []
    rows = table[1:] if len(table) > 1 else []
    
    df = pd.DataFrame(rows, columns=headers)
    return df


def _extract_images_docid(pdf_path: Path, doc_id: str, output_dir: Path):
    """Extract images from PDF using PyMuPDF."""
    import fitz
    
    doc = fitz.open(str(pdf_path))
    figures_index = {}
    img_counter = 0
    
    for page_num, page in enumerate(doc, 1):
        image_list = page.get_images(full=True)
        
        for img_idx, img_info in enumerate(image_list, 1):
            img_counter += 1
            xref = img_info[0]
            pix = fitz.Pixmap(doc, xref)
            
            # Determine format
            if pix.n - pix.alpha < 4:  # Grayscale or RGB
                fmt = "png"
            else:  # CMYK
                fmt = "jpg"
            
            img_name = f"page_{page_num}_img_{img_idx}"
            img_path = output_dir / f"{img_name}.{fmt}"
            
            pix.save(str(img_path))
            
            figures_index[img_name] = {
                'page': page_num,
                'image_path': str(img_path),
                'doc_id': doc_id,
                'caption': ''  # Will be filled by caption_images
            }
    
    index_file = output_dir / 'figures_index.json'
    with open(index_file, 'w') as f:
        json.dump(figures_index, f, indent=2)
    
    print(f"  ✓ Extracted {img_counter} images")


def _extract_graphs_docid(doc_id: str, output_dir: Path):
    """Detect graphs/shapes in extracted images using OpenCV."""
    import cv2
    import numpy as np
    
    figures_file = output_dir / 'figures_index.json'
    if not figures_file.exists():
        return
    
    with open(figures_file, 'r') as f:
        figures_index = json.load(f)
    
    graph_count = 0
    
    for fig_name, fig_data in figures_index.items():
        img_path = fig_data.get('image_path')
        if not img_path or not Path(img_path).exists():
            continue
        
        img = cv2.imread(img_path)
        if img is None:
            continue
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Simple heuristic: if many contours, likely a complex graph
        if len(contours) > 5:
            fig_data['kind'] = 'graph'
            graph_count += 1
        else:
            fig_data['kind'] = 'image'
    
    # Save updated figures index
    with open(figures_file, 'w') as f:
        json.dump(figures_index, f, indent=2)
    
    print(f"  ✓ Detected {graph_count} graphs")


def _caption_images_docid(doc_id: str, output_dir: Path):
    """Generate captions for extracted images using BLIP."""
    import json
    from PIL import Image
    try:
        from transformers import BlipProcessor, BlipForConditionalGeneration
        
        processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        
        figures_file = output_dir / 'figures_index.json'
        if not figures_file.exists():
            return
        
        with open(figures_file, 'r') as f:
            figures_index = json.load(f)
        
        caption_count = 0
        
        for fig_name, fig_data in figures_index.items():
            img_path = fig_data.get('image_path')
            if not img_path or not Path(img_path).exists():
                continue
            
            try:
                img = Image.open(img_path).convert('RGB')
                inputs = processor(img, return_tensors="pt")
                out = model.generate(**inputs, max_length=50)
                caption = processor.decode(out[0], skip_special_tokens=True)
                
                fig_data['caption'] = caption
                caption_count += 1
            except Exception as e:
                print(f"  ! Could not caption {fig_name}: {e}")
        
        with open(figures_file, 'w') as f:
            json.dump(figures_index, f, indent=2)
        
        print(f"  ✓ Captioned {caption_count} images")
    
    except ImportError:
        print(f"  ! Transformers not available; skipping captions")


def _extract_markdown_tables_from_text(text: str) -> List[Dict[str, Any]]:
    """Extract markdown tables from text and return list of table data.
    Each table data is a dict with 'csv_file' path (to be set later) and the table data in list of lists.
    """
    import re
    import pandas as pd
    from io import StringIO
    
    # Find markdown tables: lines that start with | and have a separator line of ---
    # This regex finds each table block
    # Pattern: 
    #   ^\|.*\|$          (header line)
    #   ^\|?\s*-+\s*\|    (separator line)
    #   ^\|.*\|$          (data lines)
    # We'll do a simple line-by-line state machine.
    
    lines = text.split('\n')
    tables = []
    i = 0
    while i < len(lines):
        # Look for a line that starts with |
        if lines[i].strip().startswith('|'):
            # Potential table start
            start = i
            # Look for the separator line (with ---)
            j = i + 1
            while j < len(lines) and not (lines[j].strip().startswith('|') and re.search(r'-{3,}', lines[j])):
                j += 1
            if j < len(lines) and re.search(r'-{3,}', lines[j]):
                # Found separator line at j
                # Now collect data lines until we hit a line that doesn't start with |
                k = j + 1
                while k < len(lines) and lines[k].strip().startswith('|'):
                    k += 1
                # Lines from start to k-1 form the table
                table_lines = lines[start:k]
                # Convert to CSV-like format
                # Remove leading/trailing | and split by |
                # But keep empty cells
                table_data = []
                for line in table_lines:
                    # Remove leading and trailing |
                    if line.startswith('|') and line.endswith('|'):
                        line = line[1:-1]
                    elif line.startswith('|'):
                        line = line[1:]
                    elif line.endswith('|'):
                        line = line[:-1]
                    # Split by |
                    cells = [cell.strip() for cell in line.split('|')]
                    table_data.append(cells)
                # Now we have table_data as list of lists
                # The first row is header, second is separator (which we ignore), then data
                if len(table_data) >= 3:
                    # Remove the separator row (second row)
                    header = table_data[0]
                    data = table_data[2:]  # skip separator
                    # If header is empty, use first data row as header?
                    # But we'll keep as is
                    tables.append({
                        'header': header,
                        'data': data,
                        'raw_lines': table_lines
                    })
                    # Debug: print what we found
                    # print(f"DEBUG: Found table with {len(header)} columns and {len(data)} rows")
                    # print(f"DEBUG: Header: {header}")
                    # if data:
                    #     print(f"DEBUG: First data row: {data[0]}")
                i = k  # skip past this table
                continue
        i += 1
    return tables


def _build_metadata_docid(doc_id: str, output_dir: Path) -> dict:
    """Aggregate text, tables, figures into unified metadata with doc_id."""
    
    metadata = {
        'doc_id': doc_id,
        'pages': [],
        'tables': {},
        'figures': {}
    }
    
    # Load and merge text
    text_file = output_dir / 'pages_text.json'
    if text_file.exists():
        with open(text_file, 'r') as f:
            pages = json.load(f)
        
        for page_data in pages:
            page_num = page_data.get('page')
            page_text = page_data.get('text', '')
            
            metadata['pages'].append({
                'page': page_num,
                'text': page_text,
                'doc_id': doc_id
            })
            
            # Extract markdown tables from this page's text
            tables = _extract_markdown_tables_from_text(page_text)
            for table_idx, table_info in enumerate(tables):
                table_id = f"page_{page_num}_table_{table_idx}"
                # Save as CSV
                csv_file = output_dir / f"{table_id}.csv"
                # Create DataFrame
                if table_info['data']:
                    # Use first non-empty row as header if header is empty?
                    header = table_info['header']
                    # If header looks empty (all empty strings), use first data row as header
                    if all(h == '' for h in header):
                        if table_info['data']:
                            header = table_info['data'][0]
                            data = table_info['data'][1:]
                        else:
                            data = []
                    else:
                        data = table_info['data']
                    
                    # Create DataFrame
                    import pandas as pd
                    if header and data:
                        # Ensure same length
                        max_len = max(len(header), len(data[0]) if data else 0)
                        header = header + [''] * (max_len - len(header))
                        for row in data:
                            row.extend([''] * (max_len - len(row)))
                        df = pd.DataFrame(data, columns=header)
                    else:
                        df = pd.DataFrame()
                    
                    df.to_csv(csv_file, index=False)
                    
                    metadata['tables'][table_id] = {
                        'page': page_num,
                        'index': table_idx,
                        'csv_file': str(csv_file),
                        'doc_id': doc_id
                    }
                else:
                    # No data, skip
                    pass
    
    # Load and merge tables from tables_index.json (from pdfplumber/Camelot)
    tables_file = output_dir / 'tables_index.json'
    if tables_file.exists():
        with open(tables_file, 'r') as f:
            tables_index = json.load(f)
        
        for table_id, table_info in tables_index.items():
            # Avoid overwriting tables we already added from text
            if table_id not in metadata['tables']:
                metadata['tables'][table_id] = {
                    **table_info,
                    'doc_id': doc_id
                }
    
    # Load and merge figures
    figures_file = output_dir / 'figures_index.json'
    if figures_file.exists():
        with open(figures_file, 'r') as f:
            figures_index = json.load(f)
        
        metadata['figures'] = {
            k: {**v, 'doc_id': doc_id}
            for k, v in figures_index.items()
        }
    
    return metadata


if __name__ == '__main__':
    # Example usage: python extraction/extract_with_docid.py <pdf_path> <doc_id>
    if len(sys.argv) < 3:
        print("Usage: python extraction/extract_with_docid.py <pdf_path> <doc_id> [--force]")
        print("Example: python extraction/extract_with_docid.py /path/to/file.pdf my_document")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    doc_id = sys.argv[2]
    force = '--force' in sys.argv
    
    extract_pdf_with_docid(pdf_path, doc_id, force_reprocess=force)
