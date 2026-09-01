# DEPRECATED: Use extraction/extract_with_docid.py instead (canonical ingestion path)
import subprocess, sys, os

BASE = os.path.dirname(os.path.dirname(__file__))
print("Base:", BASE)

steps = [
    "extract_vlm_layout.py",
    "extract_images.py",
    "extract_graphs.py",
    "caption_images.py",
    "build_metadata.py"
]

for s in steps:
    p = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), s)])
    if p.returncode != 0:
        print("Step failed:", s)
        break

print("Pipeline completed.")
