import fitz  # type: ignore # PyMuPDF

def extract_text(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = ""

    for page in doc:
        text += page.get_text()

    return text


if __name__ == "__main__":
    pdf_path = "data/test.pdf"

    text = extract_text(pdf_path)

    print("\n--- Extracted Text ---\n")
    print(text[:1000])
    print("Total length:", len(text))
    print("Preview length:", len(text[:1000]))