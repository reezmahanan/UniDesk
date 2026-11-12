from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)  # IT, ADMISSIONS, ACADEMICS, WELFARE, LIBRARY, GENERAL
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    email = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    staff_members = relationship("User", back_populates="department", foreign_keys="User.department_id")
    assignments = relationship("StaffDepartmentAssignment", back_populates="department", cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="department")
    faqs = relationship("FAQ", back_populates="department")
    documents = relationship("KnowledgeDocument", back_populates="department")

class StaffDepartmentAssignment(Base):
    __tablename__ = "staff_department_assignments"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)
    role_title = Column(String(100), default="Support Officer", nullable=False)
    is_primary = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    staff_user = relationship("User", back_populates="department_assignments")
    department = relationship("Department", back_populates="assignments")
