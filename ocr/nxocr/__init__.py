"""nxocr: OCR tooling for scanned Grabar books.

Pipeline: pages -> prep -> engine -> post -> review.
Scored against typed text by evaluate (metrics, align).
Needs Pillow and numpy; the rest is standard library
and the `tesseract` and `pdftoppm` programs.
"""
