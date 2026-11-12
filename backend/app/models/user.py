import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class UserRole(str, enum.Enum):
    STUDENT = "STUDENT"
    STAFF = "STAFF"
    ADMIN = "ADMIN"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT, nullable=False)
    student_index = Column(String(50), nullable=True, index=True)  # e.g. "2026/SE/048"
    faculty = Column(String(100), nullable=True)  # e.g. "Faculty of Computing"
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    department = relationship("Department", back_populates="staff_members", foreign_keys=[department_id])
    department_assignments = relationship("StaffDepartmentAssignment", back_populates="staff_user")
    created_tickets = relationship("Ticket", back_populates="student", foreign_keys="Ticket.student_id")
    assigned_tickets = relationship("Ticket", back_populates="assigned_staff", foreign_keys="Ticket.assigned_staff_id")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
