from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.knowledge import ContentStatus, JobStatus
from app.schemas.user import UserResponse

class FAQCreate(BaseModel):
    category: str
    question: str
    answer: str
    department_id: Optional[int] = None
    language: str = "en"
    source_reference: Optional[str] = None
    status: ContentStatus = ContentStatus.PUBLISHED

class FAQUpdate(BaseModel):
    category: Optional[str] = None
    question: Optional[str] = None
    answer: Optional[str] = None
    department_id: Optional[int] = None
    status: Optional[ContentStatus] = None
    language: Optional[str] = None
    source_reference: Optional[str] = None

class FAQResponse(BaseModel):
    id: int
    department_id: Optional[int] = None
    category: str
    question: str
    answer: str
    status: ContentStatus
    language: str
    source_reference: Optional[str] = None
    effective_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    last_reviewed_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentChunkResponse(BaseModel):
    id: int
    document_id: int
    chunk_index: int
    content: str
    page_number: Optional[int] = None
    section_heading: Optional[str] = None
    token_count: Optional[int] = None

    class Config:
        from_attributes = True

class KnowledgeDocumentResponse(BaseModel):
    id: int
    title: str
    original_filename: str
    file_size: int
    mime_type: str
    version: str
    language: str
    department_id: Optional[int] = None
    status: ContentStatus
    effective_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    uploaded_by: int
    uploader: Optional[UserResponse] = None
    created_at: datetime
    updated_at: datetime
    chunks_count: Optional[int] = 0

    class Config:
        from_attributes = True

class IngestionJobResponse(BaseModel):
    id: int
    document_id: int
    status: JobStatus
    error_message: Optional[str] = None
    chunks_created: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ServiceLinkResponse(BaseModel):
    id: int
    title: str
    description: str
    url: str
    icon_name: str
    badge_color: str
    display_order: int
    is_active: bool

    class Config:
        from_attributes = True

class KnowledgeSearchResult(BaseModel):
    chunk_id: int
    document_id: int
    document_title: str
    content: str
    page_number: Optional[int] = None
    section_heading: Optional[str] = None
    score: float
