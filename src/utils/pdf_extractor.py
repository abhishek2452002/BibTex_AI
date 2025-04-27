#pdf_extractor.py

import fitz  # PyMuPDF
from pathlib import Path

class PDFExtractor:
    """Extracts text from PDF files using LangChain's PyPDFLoader."""

    @staticmethod
    def extract_text(pdf_path):
        """Extracts text from a PDF using PyMuPDF (fallback for LangChain PDFLoader issues)."""
        doc = fitz.open(pdf_path)
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        return text

# Example usage:
if __name__ == "__main__":
    pdf_path = "sample_paper.pdf"
    extracted_text = PDFExtractor.extract_text(pdf_path)
