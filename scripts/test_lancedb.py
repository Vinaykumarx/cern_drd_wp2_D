# scripts/test_lancedb.py

import numpy as np
import lancedb


def main():
    db = lancedb.connect("lancedb")
    print("Tables:", db.table_names())

    if "cern_demo" not in db.table_names():
        print("Table 'cern_demo' does NOT exist.")
        return

    table = db.open_table("cern_demo")
    print("Schema:")
    print(table.schema)

    if table.count_rows() == 0:
        print("Table is empty.")
        return

    vec = np.zeros(768, dtype="float32")  # matches BGE base dim in RAG pipeline
    res = (
        table.search(vec.tolist(), vector_column_name="vector")
        .metric("cosine")
        .limit(3)
        .to_list()
    )
    print("Search result:")
    for r in res:
        print(r)


if __name__ == "__main__":
    main()
