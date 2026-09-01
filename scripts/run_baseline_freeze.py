"""
Baseline Freeze — captures current extraction + chunking output for all PDFs in data/.

Usage:
    python scripts/run_baseline_freeze.py

Output:
    baseline/
    ├── manifest.json
    ├── system_snapshot.json
    └── docs/{doc_id}/
        ├── metadata.json
        ├── chunks.json
        └── ingestion.log

This script:
  - Backs up data/*.pdf to .baseline_pdf_backup/
  - Runs current extraction pipeline on each PDF (force-reprocess)
  - Runs current RAG chunking on each PDF's metadata
  - Saves all artifacts to baseline/
  - Restores data/*.pdf from backup
"""

import sys
import json
import shutil
import time
import logging
import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

DATA_DIR = BASE / "data"
OUTPUTS_DIR = BASE / "outputs"
BASELINE_DIR = BASE / "baseline"
BASELINE_DOCS = BASELINE_DIR / "docs"
BACKUP_DIR = BASE / ".baseline_pdf_backup"

LOG = logging.getLogger("baseline_freeze")
LOG.setLevel(logging.INFO)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
LOG.addHandler(console)


def backup_pdfs() -> list[Path]:
    pdf_files = sorted(DATA_DIR.glob("*.pdf"))
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    for p in pdf_files:
        shutil.copy2(p, BACKUP_DIR / p.name)
    LOG.info("Backed up %d PDFs to %s", len(pdf_files), BACKUP_DIR)
    return pdf_files


def restore_pdfs() -> None:
    restored = 0
    for backup_pdf in BACKUP_DIR.glob("*.pdf"):
        target = DATA_DIR / backup_pdf.name
        shutil.copy2(backup_pdf, target)
        restored += 1
    shutil.rmtree(BACKUP_DIR, ignore_errors=True)
    LOG.info("Restored %d PDFs to data/ and removed backup", restored)


def extract_pdf(pdf_path: Path, doc_id: str) -> dict:
    LOG.info("  extraction...")
    from extraction.extract_with_docid import extract_pdf_with_docid
    metadata = extract_pdf_with_docid(str(pdf_path), doc_id, force_reprocess=True)
    return metadata


def chunk_metadata(doc_id: str, baseline_md_path: Path) -> list[dict]:
    LOG.info("  chunking...")
    from core.rag_pipeline import RAGPipeline
    rag = RAGPipeline(
        db_uri="lancedb",
        table_name="cern_demo",
        embed_model_name="BAAI/bge-base-en-v1.5",
    )
    with open(baseline_md_path) as f:
        rag.metadata = json.load(f)
    for k in ("pages", "tables", "figures"):
        if k not in rag.metadata:
            rag.metadata[k] = []
    chunks = rag.build_chunks_from_metadata(doc_id=doc_id)
    return [c.__dict__ for c in chunks]


def save_chunks(doc_id: str, chunks: list[dict], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "chunks.json"
    with open(path, "w") as f:
        json.dump(chunks, f, indent=2, default=str)
    LOG.info("  saved %d chunks to %s", len(chunks), path)


def save_baseline_metadata(src: Path, doc_id: str, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    dst = out_dir / "metadata.json"
    shutil.copy2(src, dst)
    LOG.info("  saved metadata to %s", dst)


def write_ingestion_log(doc_id: str, status: str, elapsed: float, error: str | None, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "ingestion.log"
    with open(path, "w") as f:
        f.write(f"doc_id={doc_id}\n")
        f.write(f"timestamp={datetime.datetime.now(datetime.timezone.utc).isoformat()}\n")
        f.write(f"status={status}\n")
        f.write(f"elapsed_seconds={elapsed:.3f}\n")
        if error:
            f.write(f"error={error}\n")


def write_manifest(entries: list[dict]) -> None:
    manifest = {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_docs": len(entries),
        "docs": entries,
    }
    path = BASELINE_DIR / "manifest.json"
    with open(path, "w") as f:
        json.dump(manifest, f, indent=2)
    LOG.info("Wrote manifest to %s (%d docs)", path, len(entries))


def write_system_snapshot() -> None:
    snapshot = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "note": "baseline freeze of current RAG behavior",
    }
    try:
        import torch
        snapshot["torch_version"] = torch.__version__
        snapshot["cuda_available"] = torch.cuda.is_available()
        if torch.cuda.is_available():
            snapshot["cuda_device"] = torch.cuda.get_device_name(0)
    except Exception:
        pass
    try:
        import sentence_transformers
        snapshot["sentence_transformers_version"] = sentence_transformers.__version__
    except Exception:
        pass
    try:
        import lancedb
        snapshot["lancedb_version"] = lancedb.__version__
    except Exception:
        pass
    path = BASELINE_DIR / "system_snapshot.json"
    with open(path, "w") as f:
        json.dump(snapshot, f, indent=2)
    LOG.info("Wrote system snapshot to %s", path)


def main() -> None:
    LOG.info("=" * 60)
    LOG.info("BASELINE FREEZE — capturing current extraction + chunking")
    LOG.info("=" * 60)

    pdf_files = backup_pdfs()
    if not pdf_files:
        LOG.warning("No PDF files found in data/. Nothing to freeze.")
        restore_pdfs()
        return

    pdf_sizes = {p.name: p.stat().st_size for p in pdf_files}
    manifest_entries = []

    try:
        for pdf_path in pdf_files:
            doc_id = pdf_path.stem
            LOG.info("[%s] Processing %s", doc_id, pdf_path.name)
            start = time.time()
            error = None
            status = "success"

            try:
                metadata = extract_pdf(pdf_path, doc_id)

                src_metadata = OUTPUTS_DIR / doc_id / "metadata.json"
                if not src_metadata.exists():
                    raise FileNotFoundError(f"metadata.json not produced at {src_metadata}")

                doc_baseline_dir = BASELINE_DOCS / doc_id

                save_baseline_metadata(src_metadata, doc_id, doc_baseline_dir)

                try:
                    baseline_md = doc_baseline_dir / "metadata.json"
                    chunks = chunk_metadata(doc_id, baseline_md)
                    save_chunks(doc_id, chunks, doc_baseline_dir)
                except Exception as e:
                    LOG.error("  chunking failed: %s", e)
                    error = f"chunking_error: {e}"
                    status = "partial"
                    chunks = []

            except Exception as e:
                LOG.error("  extraction failed: %s", e)
                error = f"extraction_error: {e}"
                status = "failed"
                chunks = []

            elapsed = time.time() - start

            doc_baseline_dir = BASELINE_DOCS / doc_id
            doc_baseline_dir.mkdir(parents=True, exist_ok=True)
            write_ingestion_log(doc_id, status, elapsed, error, doc_baseline_dir)

            manifest_entries.append({
                "doc_id": doc_id,
                "filename": pdf_path.name,
                "pdf_size_bytes": pdf_sizes.get(pdf_path.name, 0),
                "status": status,
                "elapsed_seconds": round(elapsed, 3),
                "chunk_count": len(chunks),
                "error": error,
                "processed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            })

            LOG.info("  done (%s, %.1fs)", status, elapsed)

    finally:
        restore_pdfs()

    write_manifest(manifest_entries)
    write_system_snapshot()

    failed = [e for e in manifest_entries if e["status"] == "failed"]
    partial = [e for e in manifest_entries if e["status"] == "partial"]

    LOG.info("=" * 60)
    LOG.info("Baseline freeze complete.")
    LOG.info("  Total:  %d", len(manifest_entries))
    LOG.info("  OK:     %d", len(manifest_entries) - len(failed) - len(partial))
    LOG.info("  Partial:%d", len(partial))
    LOG.info("  Failed: %d", len(failed))
    LOG.info("  Output: %s", BASELINE_DIR)
    LOG.info("=" * 60)

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
