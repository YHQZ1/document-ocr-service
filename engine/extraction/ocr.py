import pytesseract
from engine.extraction.preprocess import preprocess_image

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