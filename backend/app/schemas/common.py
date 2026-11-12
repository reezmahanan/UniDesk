from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    link_url: Optional[str] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class StudentDashboardMetrics(BaseModel):
    open_tickets_count: int
    resolved_tickets_count: int
    awaiting_student_reply_count: int
    recent_inquiries: List[dict] = []
    latest_notices: List[dict] = []
    bursary_checklist: List[dict] = []

class StaffDashboardMetrics(BaseModel):
    unassigned_department_tickets_count: int
    assigned_workload_count: int
    high_priority_count: int
    awaiting_staff_response_count: int
    total_resolved_count: int
    department_code: Optional[str] = None

class AdminDashboardMetrics(BaseModel):
    tickets_by_department: dict
    tickets_by_status: dict
    unanswered_inquiries_count: int
    helpful_feedback_count: int
    unhelpful_feedback_count: int
    documents_awaiting_processing: int
    total_published_documents: int
    total_users_count: int
