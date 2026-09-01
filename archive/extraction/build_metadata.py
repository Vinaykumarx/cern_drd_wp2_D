# DEPRECATED: Use extraction/extract_with_docid.py instead (canonical ingestion path)
import json
import sys
from pathlib import Path

def build_metadata(doc_id: str, doc_output_dir: Path):
    data = {
        'doc_id': doc_id,
        'pages': [],
        'tables': {},
        'figures': {}
    }
    
    # Load pages
    pages_file = doc_output_dir / 'pages_text.json'
    if pages_file.exists():
        with open(pages_file) as f:
            data['pages'] = json.load(f)
            
    # Load tables
    tables_file = doc_output_dir / 'tables_index.json'
    if tables_file.exists():
        with open(tables_file) as f:
            data['tables'] = json.load(f)
            
    # Load figures
    figures_file = doc_output_dir / 'figures_index.json'
    if figures_file.exists():
        with open(figures_file) as f:
            data['figures'] = json.load(f)
            
    metadata_file = doc_output_dir / 'metadata.json'
    with open(metadata_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Saved metadata.json to {metadata_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python build_metadata.py <doc_id> <doc_output_dir>")
        sys.exit(1)
        
    doc_id = sys.argv[1]
    doc_out = Path(sys.argv[2])
    build_metadata(doc_id, doc_out)
