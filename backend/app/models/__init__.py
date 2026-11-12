from app.database import Base
from app.models.user import User, UserRole
from app.models.department import Department, StaffDepartmentAssignment
from app.models.ticket import (
    Ticket,
    TicketStatus,
    TicketPriority,
    TicketReply,
    TicketInternalNote,
    TicketEvent,
    Attachment,
)
from app.models.knowledge import (
    FAQ,
    KnowledgeDocument,
    DocumentChunk,
    IngestionJob,
    ServiceLink,
    ContentStatus,
    JobStatus,
)
from app.models.chat import (
    ChatSession,
    ChatMessage,
    MessageRole,
    AnswerFeedback,
)
from app.models.notice import Notice
from app.models.notification import Notification
from app.models.audit import AuditLog

__all__ = [
    "Base",
    "User",
    "UserRole",
    "Department",
    "StaffDepartmentAssignment",
    "Ticket",
    "TicketStatus",
    "TicketPriority",
    "TicketReply",
    "TicketInternalNote",
    "TicketEvent",
    "Attachment",
    "FAQ",
    "KnowledgeDocument",
    "DocumentChunk",
    "IngestionJob",
    "ServiceLink",
    "ContentStatus",
    "JobStatus",
    "ChatSession",
    "ChatMessage",
    "MessageRole",
    "AnswerFeedback",
    "Notice",
    "Notification",
    "AuditLog",
]
