"""
VLM-based Document Parsing.
Replaces standard PyMuPDF text and pdfplumber table extraction.
Converts PDF pages to images and uses Qwen2-VL to extract structured Markdown.
"""

import os
import sys
import json
import torch
from pathlib import Path
from PIL import Image
import fitz  # PyMuPDF

try:
    from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
    from qwen_vl_utils import process_vision_info
except ImportError:
    print("Error: Missing Qwen2-VL dependencies. Please install with: pip install qwen-vl-utils torchvision accelerate transformers")
    sys.exit(1)

# Initialize Qwen2-VL model and processor
# Using 2B parameter version for fast local inference and excellent layout parsing
MODEL_ID = "Qwen/Qwen2-VL-2B-Instruct"

print(f"Loading {MODEL_ID} on CPU...")
try:
    model = Qwen2VLForConditionalGeneration.from_pretrained(
        MODEL_ID, 
        torch_dtype=torch.float32, 
        device_map={"": "cpu"}
    )
    processor = AutoProcessor.from_pretrained(MODEL_ID)
    print("✓ Model loaded successfully (CPU).")
except Exception as e:
    print(f"Failed to load VLM on CPU: {e}")
    sys.exit(1)


def parse_page_vlm(image: Image.Image) -> str:
    """Prompt the VLM to extract the page into Markdown."""
    prompt_text = (
        "You are an expert document reading assistant. "
        "Your task is to extract all the text and structured data from the provided document image. "
        "Pay special attention to tables. "
        "If there are tables, recreate them precisely using Markdown table syntax (with `|` separators). "
        "Output exactly the text that appears on the page, preserving reading order. "
        "Preserve all logical headers, using standard Markdown heading (#, ##, etc.). "
        "Ignore repetitive page footers or page numbers. "
        "Output only the extracted markdown. Do not include any conversational filler."
    )
    
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": prompt_text},
            ],
        }
    ]
    
    text = processor.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    
    image_inputs, video_inputs = process_vision_info(messages)
    
    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    )
    inputs = inputs.to(model.device)

    # Generate output
    # max_new_tokens set to 2048 to allow full page extraction
    generated_ids = model.generate(**inputs, max_new_tokens=2048)
    
    # Trim prompt from output
    generated_ids_trimmed = [
        out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    
    output_text = processor.batch_decode(
        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )
    
    return output_text[0].strip()


def extract_vlm_docid(pdf_path: Path, doc_id: str, output_dir: Path, start_page: int = 0, end_page: int = None):
    """
    Renders PDF pages to images and parses them with Qwen2-VL.
    Saves the markdown text incrementally to `pages_text.json`.
    """
    print(f"Starting VLM extraction for document: {doc_id}")
    
    doc = fitz.open(str(pdf_path))
    total_pages = len(doc)
    
    if end_page is None:
        end_page = total_pages
    
    output_file = output_dir / 'pages_text.json'
    
    # Load existing progress if any
    pages_data = []
    if output_file.exists():
        try:
            with open(output_file, 'r') as f:
                pages_data = json.load(f)
            print(f"  ✓ Loaded existing progress: {len(pages_data)} pages.")
        except Exception:
            pages_data = []

    # Map existing pages to avoid duplicates
    existing_pages = {p['page'] for p in pages_data}
    
    for i in range(start_page, end_page):
        page_num = i + 1
        if page_num in existing_pages:
            print(f"  -> Skipping Page {page_num} (already extracted)")
            continue
            
        print(f"  -> Processing Page {page_num}/{total_pages}")
        
        page = doc[i]
        # Matrix to increase resolution. scale=2 means 144 DPI
        zoom = 2
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        try:
            md_text = parse_page_vlm(img)
            print(f"     ✓ Extracted {len(md_text)} chars of Markdown.")
        except Exception as e:
            print(f"     ! Error parsing page {page_num}: {e}")
            md_text = ""
            
        pages_data.append({
            'page': page_num,
            'text': md_text,
            'doc_id': doc_id
        })
        
        # Incremental Save
        with open(output_file, 'w') as f:
            json.dump(pages_data, f, indent=2)
        
    print(f"  ✓ VLM Text extraction phase completed. Saved to {output_file}")


if __name__ == '__main__':
    # Test execution: python extraction/extract_vlm_layout.py <pdf_path> <doc_id> [start] [end]
    if len(sys.argv) < 3:
        print("Usage: python extract_vlm_layout.py <pdf_path> <doc_id> [start_idx] [end_idx]")
        sys.exit(1)
        
    pdf_path = Path(sys.argv[1])
    doc_id = sys.argv[2]
    start = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    end = int(sys.argv[4]) if len(sys.argv) > 4 else None
    
    out_dir = Path("outputs") / doc_id
    out_dir.mkdir(parents=True, exist_ok=True)
    
    extract_vlm_docid(pdf_path, doc_id, out_dir, start_page=start, end_page=end)
