from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from app.database import Base

class Notice(Base):
    __tablename__ = "notices"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    tag = Column(String(50), default="General", nullable=False)  # Urgent, General, Scholarships, Academics
    audience = Column(String(50), default="ALL", nullable=False)  # ALL, STUDENTS, STAFF
    is_published = Column(Boolean, default=True, nullable=False)
    publish_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    expiry_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
