# DEPRECATED: Use extraction/extract_with_docid.py instead (canonical ingestion path)
import os
import sys
import json
import csv
import base64
import io
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import fitz
from PIL import Image
import pdfplumber

load_dotenv()

def pil_to_base64(img):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

class HybridExtractor:
    """
    Unified extractor that uses Groq Vision for layout/text 
    and pdfplumber for exact tabular data extraction.
    """
    def __init__(self, pdf_path: str, doc_id: str, output_dir: str):
        self.pdf_path = Path(pdf_path)
        self.doc_id = doc_id
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.pages_file = self.output_dir / 'pages_text.json'
        
        # Initialize Groq Client
        self.client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY")
        )

    def extract_page_tables(self, page_num: int, plumber_page) -> str:
        """Extract tables via pdfplumber and save to CSV, returning markdown references."""
        try:
            tables = plumber_page.extract_tables()
        except Exception as e:
            print(f"[TABLES] Error extracting tables on page {page_num}: {e}")
            return ""

        if not tables:
            return ""

        table_refs = []
        for t_idx, table in enumerate(tables):
            if not table:
                continue

            csv_filename = f"page_{page_num}_table_{t_idx+1}.csv"
            csv_path = self.output_dir / csv_filename
            
            with open(csv_path, "w", newline="") as cf:
                writer = csv.writer(cf)
                for row in table:
                    clean = ["" if c is None else str(c).replace("\n", " ").strip() for c in row]
                    writer.writerow(clean)
                    
            table_refs.append(f"\n[Extracted Table Data -> {csv_filename}]\n")

        return "\n".join(table_refs)

    def extract_page_vlm(self, fitz_page) -> str:
        """Extract full page text/layout using Groq Vision."""
        pix = fitz_page.get_pixmap(dpi=150)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        base64_image = pil_to_base64(img)

        try:
            response = self.client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extract all text from this document image. Preserve formatting, headers, and structural flow. Output ONLY the extracted markdown text."},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                            },
                        ],
                    }
                ],
                max_tokens=2048,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[VLM] Error: {e}")
            return ""

    def process(self, start_page=0, end_page=None):
        doc = fitz.open(str(self.pdf_path))
        end_page = min(end_page or len(doc), len(doc))
        
        pages_data = []
        if self.pages_file.exists():
            try:
                with open(self.pages_file, 'r') as f:
                    pages_data = json.load(f)
            except:
                pages_data = []

        existing_pages = {p['page'] for p in pages_data}

        with pdfplumber.open(str(self.pdf_path)) as pdf:
            for i in range(start_page, end_page):
                page_num = i + 1
                if page_num in existing_pages:
                    print(f"Skipping page {page_num} (already extracted)")
                    continue

                print(f"Hybrid Extracting Page {page_num}/{len(doc)}...")
                
                # 1. Tabular Extraction (deterministic)
                table_md = self.extract_page_tables(page_num, pdf.pages[i])
                
                # 2. VLM Layout/Text Extraction (semantic)
                vlm_md = self.extract_page_vlm(doc[i])
                
                # 3. Combine
                combined_text = vlm_md
                if table_md:
                    combined_text += f"\n\n### Embedded Tables\n{table_md}"
                
                pages_data.append({
                    'page': page_num,
                    'text': combined_text,
                    'doc_id': self.doc_id
                })
                
                with open(self.pages_file, 'w') as f:
                    json.dump(pages_data, f, indent=2)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python hybrid_extractor.py <pdf_path> <doc_id> [start] [end]")
    else:
        extractor = HybridExtractor(
            pdf_path=sys.argv[1], 
            doc_id=sys.argv[2], 
            output_dir=f"outputs/{sys.argv[2]}"
        )
        s = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        e = int(sys.argv[4]) if len(sys.argv) > 4 else None
        extractor.process(start_page=s, end_page=e)
