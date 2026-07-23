import logging
from typing import Optional

from pypdf import PdfReader
from docx import Document

logger = logging.getLogger(__name__)

class ExtractionService:
    """Service for parsing and extracting text from uploaded documents."""
    
    SUPPORTED_MIME_TYPES = {
        "application/pdf": "pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "text/plain": "txt",
        "text/markdown": "markdown",
    }
    
    @staticmethod
    def extract_text(file_path: str, content_type: str) -> Optional[str]:
        """Extract text from the given file based on its content type."""
        try:
            if content_type == "application/pdf":
                return ExtractionService._extract_from_pdf(file_path)
            elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                return ExtractionService._extract_from_docx(file_path)
            elif content_type in {"text/plain", "text/markdown"}:
                return ExtractionService._extract_from_text(file_path)
            else:
                logger.warning(f"Unsupported content_type: {content_type}")
                return None
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return None

    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        """Extract text from a PDF file."""
        text = []
        with open(file_path, "rb") as f:
            reader = PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
        return "\n".join(text)

    @staticmethod
    def _extract_from_docx(file_path: str) -> str:
        """Extract text from a DOCX file."""
        doc = Document(file_path)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)

    @staticmethod
    def _extract_from_text(file_path: str) -> str:
        """Extract text from a plain text or markdown file."""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
