from engine.extraction import extract_tokens

from engine.layout.rows import cluster_rows
from engine.layout.columns import infer_column_centers, assign_columns
from engine.layout.table import build_row_column_matrix


if __name__ == "__main__":
    file_path = "data/image.png"

    # -------- Extraction --------
    result = extract_tokens(file_path)
    tokens = result["tokens"]

    print("\n--- Sample Tokens ---\n")
    for t in tokens[:10]:
        print(t)

    print("\nTotal tokens:", len(tokens))

    # -------- Row Clustering --------
    rows = cluster_rows(tokens)

    print("\n--- Sample Rows ---\n")
    for i, row in enumerate(rows[:10]):
        print(f"\nRow {i}:")
        print(" ".join([t["text"] for t in row]))

    # -------- Column Inference --------
    column_centers = infer_column_centers(tokens)
    tokens = assign_columns(tokens, column_centers)

    print("\n--- Column Centers ---\n")
    print(column_centers)

    # -------- Row + Column Matrix --------
    row_matrix = build_row_column_matrix(rows)

    print("\n--- Row + Column View ---\n")
    for i, row in enumerate(row_matrix[:10]):
        print(f"\nRow {i}:")
        for col_id in sorted(row.keys()):
            text = " ".join(t["text"] for t in row[col_id])
            print(f"  Col {col_id}: {text}")