# DEPRECATED: Use extraction/extract_with_docid.py instead (canonical ingestion path)
import os
import json
import base64
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import fitz
from PIL import Image
import io

load_dotenv()

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def pil_to_base64(img):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def extract_with_groq_vision(pdf_path: Path, doc_id: str, output_dir: Path, start_page=0, end_page=5):
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    doc = fitz.open(str(pdf_path))
    output_file = output_dir / 'pages_text.json'
    
    pages_data = []
    if output_file.exists():
        try:
            with open(output_file, 'r') as f:
                pages_data = json.load(f)
        except:
            pages_data = []

    existing_pages = {p['page'] for p in pages_data}

    for i in range(start_page, min(end_page, len(doc))):
        page_num = i + 1
        if page_num in existing_pages and pages_data[i]['text']:
            print(f"Skipping page {page_num}")
            continue

        print(f"Processing page {page_num} with Groq Vision...")
        page = doc[i]
        pix = page.get_pixmap(dpi=150)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        base64_image = pil_to_base64(img)

        try:
            response = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extract all text from this document image. Preserve formatting and tables if any. Output ONLY the extracted text."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=2048,
            )
            text = response.choices[0].message.content
            print(f"Extracted {len(text)} chars.")
            
            page_entry = {'page': page_num, 'text': text, 'doc_id': doc_id}
            # Update or append
            found = False
            for p in pages_data:
                if p['page'] == page_num:
                    p['text'] = text
                    found = True
                    break
            if not found:
                pages_data.append(page_entry)
                
            with open(output_file, 'w') as f:
                json.dump(pages_data, f, indent=2)
        except Exception as e:
            print(f"Error on page {page_num}: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python extraction/extract_groq_vision.py <pdf_path> <doc_id> [start] [end]")
    else:
        pdf = Path(sys.argv[1])
        did = sys.argv[2]
        start = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        end = int(sys.argv[4]) if len(sys.argv) > 4 else 5
        out = Path("outputs") / did
        out.mkdir(parents=True, exist_ok=True)
        extract_with_groq_vision(pdf, did, out, start, end)
