import os
import fitz
import cv2
import numpy as np
import pytesseract

from pdf2image import convert_from_path
from PIL import Image

# -----------------------------
# Preprocessing
# -----------------------------

def preprocess_image(pil_image):
    img = np.array(pil_image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 3)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return thresh

# -----------------------------
# PDF → Tokens
# -----------------------------

def extract_pdf_tokens(pdf_path):
    doc = fitz.open(pdf_path)
    tokens = []

    for page_num, page in enumerate(doc):
        page_dict = page.get_text("dict")

        page_width = page.rect.width
        page_height = page.rect.height

        for block in page_dict.get("blocks", []):
            if "lines" not in block:
                continue

            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if not text:
                        continue

                    x0, y0, x1, y1 = span["bbox"]

                    tokens.append(
                        {
                            "text": text,
                            "x": x0 / page_width,
                            "y": y0 / page_height,
                            "w": (x1 - x0) / page_width,
                            "h": (y1 - y0) / page_height,
                            "page": page_num,
                            "conf": 100.0,
                            "source": "pdf",
                        }
                    )

    page_count = len(doc)
    doc.close()
    return tokens, page_count

# -----------------------------
# OCR → Tokens
# -----------------------------

def extract_ocr_tokens(images):
    tokens = []

    for page_num, img in enumerate(images):
        processed = preprocess_image(img)

        data = pytesseract.image_to_data(
            processed, output_type=pytesseract.Output.DICT, config="--oem 3 --psm 6"
        )

        img_width, img_height = img.size

        for i in range(len(data["text"])):
            text = data["text"][i].strip()
            conf = float(data["conf"][i])

            if conf <= 0 or not text:
                continue

            tokens.append(
                {
                    "text": text,
                    "x": data["left"][i] / img_width,
                    "y": data["top"][i] / img_height,
                    "w": data["width"][i] / img_width,
                    "h": data["height"][i] / img_height,
                    "page": page_num,
                    "conf": conf,
                    "source": "ocr",
                }
            )

    return tokens

# -----------------------------
# Unified Extraction
# -----------------------------

def extract_tokens(file_path: str):
    ext = os.path.splitext(file_path)[1].lower()
    tokens = []

    if ext == ".pdf":
        pdf_tokens, page_count = extract_pdf_tokens(file_path)
        tokens.extend(pdf_tokens)

        images = convert_from_path(file_path)
        ocr_tokens = extract_ocr_tokens(images)
        tokens.extend(ocr_tokens)

    elif ext in [".png", ".jpg", ".jpeg"]:
        img = Image.open(file_path)
        tokens.extend(extract_ocr_tokens([img]))
        page_count = 1

    else:
        raise ValueError(f"Unsupported file type: {ext}")

    return {"tokens": tokens, "meta": {"pages": page_count, "extraction_version": "v1"}}

# -----------------------------
# Row Clustering (NEW)
# -----------------------------

def cluster_rows(tokens, y_threshold=0.01):
    tokens_sorted = sorted(tokens, key=lambda t: t["y"])

    rows = []
    current_row = []
    current_y = None

    for token in tokens_sorted:
        if current_y is None:
            current_row.append(token)
            current_y = token["y"]
            continue

        if abs(token["y"] - current_y) <= y_threshold:
            current_row.append(token)
        else:
            rows.append(current_row)
            current_row = [token]
            current_y = token["y"]

    if current_row:
        rows.append(current_row)

    # sort each row left → right
    for row in rows:
        row.sort(key=lambda t: t["x"])

    return rows

def infer_column_centers(tokens, x_threshold=0.03):
    """
    Cluster x positions into column centers
    """

    xs = sorted([t["x"] for t in tokens])

    clusters = []
    current_cluster = [xs[0]]

    for x in xs[1:]:
        if abs(x - np.mean(current_cluster)) <= x_threshold:
            current_cluster.append(x)
        else:
            clusters.append(current_cluster)
            current_cluster = [x]

    clusters.append(current_cluster)

    # compute centers
    centers = [float(np.mean(cluster)) for cluster in clusters]

    return centers

def assign_columns(tokens, column_centers):
    """
    Assign each token to nearest column center
    """

    for token in tokens:
        distances = [abs(token["x"] - c) for c in column_centers]
        token["col_id"] = int(np.argmin(distances))

    return tokens

def build_row_column_matrix(rows):
    """
    Convert rows into column-aligned structure
    """

    matrix = []

    for row in rows:
        row_dict = {}

        for token in row:
            col = token["col_id"]

            if col not in row_dict:
                row_dict[col] = []

            row_dict[col].append(token)

        matrix.append(row_dict)

    return matrix

# -----------------------------
# Debug Run
# -----------------------------

if __name__ == "__main__":
    file_path = "data/invoice_Gene McClure_9383.pdf"

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

    row_matrix = build_row_column_matrix(rows)

    print("\n--- Column Centers ---\n")
    print(column_centers)

    print("\n--- Row + Column View ---\n")

    for i, row in enumerate(row_matrix[:10]):
        print(f"\nRow {i}:")
        for col_id in sorted(row.keys()):
            text = " ".join(t["text"] for t in row[col_id])
            print(f"  Col {col_id}: {text}")