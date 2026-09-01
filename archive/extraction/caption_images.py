# DEPRECATED: Use extraction/extract_with_docid.py instead (canonical ingestion path)
import json
import base64
import os
from pathlib import Path
import ollama

BASE = Path(__file__).resolve().parent.parent
OUT_DIR = BASE / "outputs"
IMAGES_DIR = OUT_DIR / "images"
GRAPHS_DIR = OUT_DIR / "graphs"
FIGURES_JSON = OUT_DIR / "figures_index.json"

MODEL_NAME = "gemma4:31b-it-q4_K_M"
client = ollama.Client(host='http://localhost:11435')

def infer_page_from_filename(path: Path):
    stem = path.stem
    parts = stem.split("_")
    for i in range(len(parts)):
        if parts[i] == "page" and i + 1 < len(parts):
            try:
                return int(parts[i + 1])
            except ValueError:
                return None
    return None

def generate_caption_gemma(image_path: Path, kind: str) -> str:
    """
    Generate a high-fidelity caption using Gemma 4's native multimodal vision.
    """
    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
    except Exception as e:
        print(f"[Gemma-Vision] Error opening {image_path}: {e}")
        return ""

    if kind == "graph":
        prompt = "This is a scientific plot from a CERN technical report. Describe the axes, the data trends, and any notable physics labels."
    else:
        prompt = "Describe this scientific figure from a CERN report in detail, focusing on Technical components and labels."

    try:
        response = client.generate(
            model=MODEL_NAME,
            prompt=prompt,
            images=[image_bytes],
            stream=False
        )
        return response.get("response", "").strip()
    except Exception as e:
        print(f"[Gemma-Vision] Ollama error: {e}")
        return "Extraction failed."

def main():
    figures = []

    if IMAGES_DIR.exists():
        image_paths = sorted(IMAGES_DIR.glob("*.png"))
        print(f"[Gemma-Vision] Found {len(image_paths)} images")
        for img_path in image_paths:
            print(f"[Gemma-Vision] Processing {img_path.name} ...")
            caption = generate_caption_gemma(img_path, kind="image")
            page = infer_page_from_filename(img_path)
            figures.append({
                "image_path": str(img_path),
                "caption": caption,
                "page": page,
                "kind": "image"
            })

    if GRAPHS_DIR.exists():
        graph_paths = sorted(GRAPHS_DIR.glob("*.png"))
        print(f"[Gemma-Vision] Found {len(graph_paths)} graphs")
        for g_path in graph_paths:
            print(f"[Gemma-Vision] Analyzing graph {g_path.name} ...")
            caption = generate_caption_gemma(g_path, kind="graph")
            page = infer_page_from_filename(g_path)
            figures.append({
                "image_path": str(g_path),
                "caption": caption,
                "page": page,
                "kind": "graph"
            })

    with open(FIGURES_JSON, "w") as f:
        json.dump(figures, f, indent=2)

    print(f"[Gemma-Vision] Saved {len(figures)} detailed captions to {FIGURES_JSON}")

if __name__ == "__main__":
    main()
