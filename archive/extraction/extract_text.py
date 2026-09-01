# DEPRECATED: Use extraction/extract_with_docid.py instead (canonical ingestion path)
"""
Dynamic PDF text extractor.
Usage:
  python extraction/extract_text.py <pdf_path> [output_dir]
  
If no arguments given, scans data/ for all PDFs automatically.
"""
import sys
import fitz
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent


def extract_text_from_pdf(pdf_path: Path, out_dir: Path) -> Path:
    """Extract all page text from a PDF and save to pages_text.json."""
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "pages_text.json"

    doc = fitz.open(str(pdf_path))
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text("text")
        pages.append({"page": i + 1, "text": text})

    with open(out_file, "w") as f:
        json.dump(pages, f, indent=2)

    print(f"[ExtractText] Extracted {len(pages)} pages → {out_file}")
    return out_file


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        # Dynamic mode: user specified a PDF
        pdf_path = Path(sys.argv[1])
        if not pdf_path.is_absolute():
            pdf_path = BASE / pdf_path

        if not pdf_path.exists():
            print(f"[Error] PDF not found: {pdf_path}")
            sys.exit(1)

        # Output dir is named after the PDF stem under outputs/
        out_dir = BASE / "outputs" / pdf_path.stem
        extract_text_from_pdf(pdf_path, out_dir)

    else:
        # Auto mode: scan data/ for all PDFs
        data_dir = BASE / "data"
        pdfs = list(data_dir.glob("*.pdf"))
        if not pdfs:
            print("[ExtractText] No PDFs found in data/ directory.")
            sys.exit(0)

        print(f"[ExtractText] Found {len(pdfs)} PDFs in data/ — processing all...")
        for pdf_path in pdfs:
            out_dir = BASE / "outputs" / pdf_path.stem
            extract_text_from_pdf(pdf_path, out_dir)
        print("[ExtractText] Done.")
