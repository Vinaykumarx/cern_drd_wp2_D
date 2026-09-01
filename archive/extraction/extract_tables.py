# DEPRECATED: Use extraction/extract_with_docid.py instead (canonical ingestion path)
import pdfplumber
import json
import csv
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
pdf_path = BASE / "data" / "CERN_Yellow_Report_357576.pdf"
out_dir = BASE / "outputs"
out_dir.mkdir(exist_ok=True)

tables_index = []

with pdfplumber.open(str(pdf_path)) as pdf:
    for i, page in enumerate(pdf.pages):
        page_num = i + 1
        try:
            tables = page.extract_tables()
        except Exception as e:
            print(f"[TABLES] Error extracting tables on page {page_num}: {e}")
            continue

        if not tables:
            continue

        for t_idx, table in enumerate(tables):
            if not table:
                continue

            csv_path = out_dir / f"page_{page_num}_table_{t_idx+1}.csv"
            preview_rows = []
            flat_lines = []

            with open(csv_path, "w", newline="") as cf:
                writer = csv.writer(cf)
                for row in table:
                    clean = [
                        "" if c is None else str(c).replace("\n", " ").strip()
                        for c in row
                    ]
                    writer.writerow(clean)

                    # build preview
                    if len(preview_rows) < 5:
                        preview_rows.append(clean)

                    # build full_text
                    flat_lines.append(" | ".join(clean))

            full_text = "\n".join(flat_lines)

            tables_index.append({
                "page": page_num,
                "table_csv": str(csv_path),
                "preview": preview_rows,
                "full_text": full_text,
            })

with open(out_dir / "tables_index.json", "w") as f:
    json.dump(tables_index, f, indent=2)

print(f"[TABLES] Saved {len(tables_index)} tables to {out_dir}")
