"""Extract text from an image using Tesseract OCR (via pytesseract).

Both ``pytesseract`` and ``cv2`` are imported lazily. The Tesseract binary
location can be overridden with the ``TESSERACT_CMD`` environment variable
(needed on Windows where it is not usually on PATH).
"""

import os


def extract_text(image_path):
    """Return the text found in ``image_path`` (empty string on failure)."""
    try:
        import cv2
        import pytesseract
    except ImportError as exc:
        print(f"[text_extractor] OCR backend unavailable: {exc}")
        return ""

    tesseract_cmd = os.environ.get("TESSERACT_CMD")
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    img = cv2.imread(image_path)
    if img is None:
        print(f"[text_extractor] could not read image: {image_path}")
        return ""

    text = pytesseract.image_to_string(img)
    print(text)
    return text


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        extract_text(sys.argv[1])
