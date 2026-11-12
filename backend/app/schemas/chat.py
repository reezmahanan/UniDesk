from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.chat import MessageRole

class CitationItem(BaseModel):
    chunk_id: int
    document_id: int
    document_title: str
    page_number: Optional[int] = None
    section_heading: Optional[str] = None
    snippet: Optional[str] = None

class ChatMessageCreate(BaseModel):
    content: str = Field(..., min_length=1)
    session_id: Optional[int] = None

class ChatMessageResponse(BaseModel):
    id: int
    session_id: int
    sender_role: MessageRole
    content: str
    citations: List[CitationItem] = []
    confidence_score: Optional[float] = None
    created_at: datetime
    feedback: Optional[dict] = None

    class Config:
        from_attributes = True

class ChatSessionResponse(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageResponse] = []

    class Config:
        from_attributes = True

class AnswerFeedbackCreate(BaseModel):
    message_id: int
    is_helpful: bool
    comment: Optional[str] = None

class ChatToTicketDraftRequest(BaseModel):
    session_id: int

class ChatToTicketDraftResponse(BaseModel):
    suggested_subject: str
    suggested_description: str
    suggested_category: str
    suggested_department_id: Optional[int] = None
    transcript_excerpt: str
