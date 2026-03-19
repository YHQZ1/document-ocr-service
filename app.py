import os
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import pytesseract
from PIL import Image


def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    final_text = []

    # Preload images once (for OCR fallback)
    images = convert_from_path(pdf_path)

    for i, page in enumerate(doc):
        text = page.get_text()

        if text.strip():
            final_text.append(text)
            print(f"[Page {i+1}] PyMuPDF")
        else:
            print(f"[Page {i+1}] OCR fallback")
            if i < len(images):
                ocr_text = pytesseract.image_to_string(images[i])
            else:
                ocr_text = ""
            final_text.append(ocr_text)

    doc.close()
    return "\n".join(final_text)


def extract_text_from_image(image_path: str) -> str:
    print("[Image] OCR")
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text


def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)

    elif ext in [".png", ".jpg", ".jpeg"]:
        return extract_text_from_image(file_path)

    else:
        raise ValueError(f"Unsupported file type: {ext}")


if __name__ == "__main__":
    file_path = "data/image.png"

    text = extract_text(file_path)

    print("\n--- Extracted Text ---\n")
    print(text[:1000])
    print("Total length:", len(text))
    print("Preview length:", len(text[:1000]))