from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)  # USER_LOGIN, DOCUMENT_UPLOAD, DOCUMENT_PUBLISHED, DOCUMENT_ARCHIVED, TICKET_STATUS_CHANGED, TICKET_ASSIGNED
    resource_type = Column(String(50), nullable=False)  # USER, TICKET, DOCUMENT, FAQ
    resource_id = Column(String(50), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User")
