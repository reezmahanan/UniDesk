import os
from pathlib import Path
from typing import List, Dict, Any
from pypdf import PdfReader
from docx import Document as DocxDocument

class DocumentExtractionResult:
    def __init__(self, sections: List[Dict[str, Any]], has_extractable_text: bool, warning_message: str = ""):
        self.sections = sections  # list of {content, page_number, section_heading}
        self.has_extractable_text = has_extractable_text
        self.warning_message = warning_message

class DocumentExtractorService:
    def extract(self, file_path: str, mime_type: str) -> DocumentExtractionResult:
        path = Path(file_path)
        ext = path.suffix.lower()

        if ext == ".pdf":
            return self._extract_pdf(file_path)
        elif ext == ".docx":
            return self._extract_docx(file_path)
        elif ext == ".txt":
            return self._extract_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type for extraction: {ext}")

    def _extract_pdf(self, file_path: str) -> DocumentExtractionResult:
        sections = []
        total_text_length = 0

        try:
            reader = PdfReader(file_path)
            for page_idx, page in enumerate(reader.pages):
                page_num = page_idx + 1
                text = page.extract_text() or ""
                clean_text = text.strip()
                if clean_text:
                    total_text_length += len(clean_text)
                    sections.append({
                        "content": clean_text,
                        "page_number": page_num,
                        "section_heading": f"Page {page_num}",
                    })

            if total_text_length < 30:
                return DocumentExtractionResult(
                    sections=[],
                    has_extractable_text=False,
                    warning_message="This PDF appears to be a scanned document or image with no extractable text. (OCR capability is a planned future feature)."
                )

            return DocumentExtractionResult(sections=sections, has_extractable_text=True)

        except Exception as e:
            return DocumentExtractionResult(
                sections=[],
                has_extractable_text=False,
                warning_message=f"Failed to extract PDF text: {str(e)}"
            )

    def _extract_docx(self, file_path: str) -> DocumentExtractionResult:
        sections = []
        current_heading = "General"
        current_paras = []

        try:
            doc = DocxDocument(file_path)
            for para in doc.paragraphs:
                text = para.text.strip()
                if not text:
                    continue

                if para.style.name.startswith("Heading"):
                    if current_paras:
                        sections.append({
                            "content": "\n".join(current_paras),
                            "page_number": 1,
                            "section_heading": current_heading,
                        })
                        current_paras = []
                    current_heading = text
                else:
                    current_paras.append(text)

            if current_paras:
                sections.append({
                    "content": "\n".join(current_paras),
                    "page_number": 1,
                    "section_heading": current_heading,
                })

            if not sections:
                return DocumentExtractionResult(
                    sections=[],
                    has_extractable_text=False,
                    warning_message="DOCX document contains no text."
                )

            return DocumentExtractionResult(sections=sections, has_extractable_text=True)

        except Exception as e:
            return DocumentExtractionResult(
                sections=[],
                has_extractable_text=False,
                warning_message=f"Failed to extract DOCX text: {str(e)}"
            )

    def _extract_txt(self, file_path: str) -> DocumentExtractionResult:
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read().strip()

            if not content:
                return DocumentExtractionResult(
                    sections=[],
                    has_extractable_text=False,
                    warning_message="Text document is empty."
                )

            return DocumentExtractionResult(
                sections=[{
                    "content": content,
                    "page_number": 1,
                    "section_heading": "Document Content",
                }],
                has_extractable_text=True
            )
        except Exception as e:
            return DocumentExtractionResult(
                sections=[],
                has_extractable_text=False,
                warning_message=f"Failed to read text file: {str(e)}"
            )

document_extractor = DocumentExtractorService()
