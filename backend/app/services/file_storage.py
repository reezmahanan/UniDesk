import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from app.config import settings

class FileStorageService:
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.documents_dir = Path(settings.DOCUMENTS_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.documents_dir.mkdir(parents=True, exist_ok=True)

    def validate_file(self, file: UploadFile, is_document: bool = False):
        # 1. Check file size
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)
        
        if size > settings.MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_BYTES // (1024*1024)}MB"
            )
        
        # 2. Check extension
        ext = Path(file.filename or "").suffix.lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format '{ext}'. Allowed formats: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )

        if is_document and ext not in [".pdf", ".docx", ".txt"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Knowledge source documents must be PDF, DOCX, or TXT."
            )

        return size, ext

    async def save_upload(self, file: UploadFile, is_document: bool = False) -> tuple[str, str, int, str]:
        size, ext = self.validate_file(file, is_document)
        target_dir = self.documents_dir if is_document else self.upload_dir
        
        # Safe server-side generated filename preventing traversal
        stored_filename = f"{uuid.uuid4().hex}{ext}"
        safe_path = target_dir / stored_filename
        
        # Ensure path is strictly inside target directory
        if not safe_path.resolve().is_relative_to(target_dir.resolve()):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file path.")

        content = await file.read()
        with open(safe_path, "wb") as f:
            f.write(content)

        mime = file.content_type or "application/octet-stream"
        return stored_filename, str(safe_path), size, mime

    def get_file_path(self, stored_filename: str, is_document: bool = False) -> Path:
        target_dir = self.documents_dir if is_document else self.upload_dir
        safe_path = (target_dir / stored_filename).resolve()
        
        if not safe_path.is_relative_to(target_dir.resolve()) or not safe_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")
            
        return safe_path

file_storage = FileStorageService()
