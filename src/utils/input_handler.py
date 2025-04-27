#input_handler.py

import os
import logging
from langchain.schema import Document
import fitz  # PyMuPDF

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InputHandler:
    """Handles user input by validating and processing research papers and format PDFs."""

    def __init__(self, research_papers, format_pdf):
        """
        Initialize InputHandler.
        :param research_papers: List of research paper file paths.
        :param format_pdf: File path of the required format PDF.
        """
        self.research_papers = research_papers
        self.format_pdf = format_pdf

    def validate_files(self):
        """Check if all input files exist."""
        all_files = self.research_papers + [self.format_pdf]
        return all(os.path.exists(file) for file in all_files)

    def extract_text_from_pdf(self, file_path):
        """Extracts text from a PDF file using PyMuPDF."""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text() + "\n"
                if len(text) > 1000000:  # Stop after 100,000 characters to avoid memory issues
                    break
            doc.close()
            return text
        except Exception as e:
            logger.error(f"Failed to extract text from {file_path}: {e}")
            return ""

    def _extract_title(self, text):
        """Extracts the title from the research paper text."""
        return text.split("\n")[0].strip()

    def _extract_author(self, text):
        """Extracts the author(s) from the research paper text."""
        lines = text.split("\n")
        if len(lines) > 1:
            return lines[1].strip()
        return "Unknown"

    def _extract_sections(self, text):
        """Extracts sections from the research paper text."""
        sections = {}
        current_section = None
        for line in text.split("\n"):
            if line.strip().startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "0.")):
                current_section = line.strip()
                sections[current_section] = ""
            elif current_section:
                sections[current_section] += line + "\n"
        return sections

    def process_inputs(self):
        """
        Process research papers and format PDF into LangChain Document objects.
        :return: Dictionary containing processed LangChain Documents.
        """
        if not self.validate_files():
            raise FileNotFoundError("One or more input files are missing.")

        logger.info("Processing research papers and format PDF...")

        # Convert research papers into LangChain Documents
        research_paper_docs = []
        for paper in self.research_papers:
            logger.info(f"Extracting text from: {paper}")
            text = self.extract_text_from_pdf(paper)
            title = self._extract_title(text)
            author = self._extract_author(text)
            sections = self._extract_sections(text)
            logger.info(f"Extracted metadata - Title: {title}, Author: {author}, Sections: {list(sections.keys())}")
            research_paper_docs.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": paper,
                        "title": title,
                        "author": author,
                        "sections": sections
                    }
                )
            )

        # Convert format PDF into a LangChain Document
        logger.info(f"Extracting text from format PDF: {self.format_pdf}")
        format_text = self.extract_text_from_pdf(self.format_pdf)
        format_doc = Document(
            page_content=format_text,
            metadata={"source": self.format_pdf}
        )
        # format_requirements = "This document provides layout guidelines. DO NOT use its content. Only follow its structure."
        format_requirements = format_doc
        logger.info("Input processing completed.")
        return {
            "research_papers": research_paper_docs,
            "format_requirements": format_requirements
        }
