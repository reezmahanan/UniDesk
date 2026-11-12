from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.ticket import TicketStatus, TicketPriority
from app.schemas.user import UserResponse

class AttachmentResponse(BaseModel):
    id: int
    original_filename: str
    file_size: int
    mime_type: str
    created_at: datetime

    class Config:
        from_attributes = True

class TicketReplyCreate(BaseModel):
    message: str = Field(..., min_length=1)
    is_solution: bool = False

class TicketReplyResponse(BaseModel):
    id: int
    ticket_id: int
    user_id: int
    user: UserResponse
    message: str
    is_solution: bool
    created_at: datetime
    attachments: List[AttachmentResponse] = []

    class Config:
        from_attributes = True

class TicketInternalNoteCreate(BaseModel):
    note: str = Field(..., min_length=1)

class TicketInternalNoteResponse(BaseModel):
    id: int
    ticket_id: int
    staff_id: int
    staff: UserResponse
    note: str
    created_at: datetime

    class Config:
        from_attributes = True

class TicketEventResponse(BaseModel):
    id: int
    ticket_id: int
    user_id: Optional[int] = None
    event_type: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TicketCreate(BaseModel):
    subject: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10)
    category: str
    department_id: Optional[int] = None
    priority: TicketPriority = TicketPriority.MEDIUM
    transcript_excerpt: Optional[str] = None

class TicketStatusUpdate(BaseModel):
    status: TicketStatus
    comment: Optional[str] = None

class TicketAssignUpdate(BaseModel):
    assigned_staff_id: Optional[int] = None
    department_id: Optional[int] = None
    comment: Optional[str] = None

class TicketPriorityUpdate(BaseModel):
    priority: TicketPriority

class TicketResponse(BaseModel):
    id: int
    ticket_number: str
    student_id: int
    student: UserResponse
    department_id: int
    assigned_staff_id: Optional[int] = None
    assigned_staff: Optional[UserResponse] = None
    subject: str
    description: str
    category: str
    priority: TicketPriority
    status: TicketStatus
    transcript_excerpt: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TicketDetailResponse(TicketResponse):
    replies: List[TicketReplyResponse] = []
    internal_notes: List[TicketInternalNoteResponse] = []  # Strictly filtered in API for non-staff
    events: List[TicketEventResponse] = []
    attachments: List[AttachmentResponse] = []

class StaffAiSummaryResponse(BaseModel):
    ticket_id: int
    summary: str
    key_facts: List[str]
    missing_information: List[str]

class StaffAiDraftReplyResponse(BaseModel):
    ticket_id: int
    suggested_reply: str
    relevant_sources: List[str]
