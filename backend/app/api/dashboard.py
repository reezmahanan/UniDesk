from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.user import User, UserRole
from app.models.ticket import Ticket, TicketStatus, TicketPriority
from app.models.department import Department
from app.models.chat import ChatSession, ChatMessage, AnswerFeedback, MessageRole
from app.models.knowledge import KnowledgeDocument, IngestionJob, ContentStatus, JobStatus
from app.models.notice import Notice
from app.schemas.common import (
    StudentDashboardMetrics,
    StaffDashboardMetrics,
    AdminDashboardMetrics,
)
from app.api.deps import get_current_user, require_staff, require_admin

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/student", response_model=StudentDashboardMetrics)
def get_student_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    open_count = db.query(Ticket).filter(
        Ticket.student_id == current_user.id,
        Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS, TicketStatus.WAITING_FOR_STUDENT])
    ).count()

    resolved_count = db.query(Ticket).filter(
        Ticket.student_id == current_user.id,
        Ticket.status.in_([TicketStatus.RESOLVED, TicketStatus.CLOSED])
    ).count()

    awaiting_reply = db.query(Ticket).filter(
        Ticket.student_id == current_user.id,
        Ticket.status == TicketStatus.WAITING_FOR_STUDENT
    ).count()

    # Recent chat inquiries
    recent_sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.updated_at.desc()).limit(4).all()

    recent_inquiries = [
        {"id": s.id, "title": s.title, "date": s.updated_at.strftime("%b %d, %Y")}
        for s in recent_sessions
    ]

    # Latest announcements
    notices = db.query(Notice).filter(
        Notice.is_published == True,
        Notice.audience.in_(["ALL", "STUDENTS"])
    ).order_by(Notice.publish_date.desc()).limit(3).all()

    latest_notices = [
        {"id": n.id, "title": n.title, "tag": n.tag, "date": n.publish_date.strftime("%b %d, %Y"), "content": n.content}
        for n in notices
    ]

    # Configurable Mahapola/Bursary checklist (Sri Lankan context)
    bursary_checklist = [
        {"title": "GCE A/L Z-Score & UGC Enrollment Verified", "completed": True, "badge": "Verified"},
        {"title": "Grama Niladhari Income Certificate Submitted", "completed": True, "badge": "Approved"},
        {"title": "Bank of Ceylon (BOC) Student Account Linked", "completed": True, "badge": "Active"},
        {"title": "June Mahapola Monthly Voucher Collection", "completed": False, "badge": "Pending Payout"},
    ]

    return StudentDashboardMetrics(
        open_tickets_count=open_count,
        resolved_tickets_count=resolved_count,
        awaiting_student_reply_count=awaiting_reply,
        recent_inquiries=recent_inquiries,
        latest_notices=latest_notices,
        bursary_checklist=bursary_checklist,
    )

@router.get("/staff", response_model=StaffDashboardMetrics)
def get_staff_dashboard(
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    dept_id = current_user.department_id

    query = db.query(Ticket)
    if dept_id:
        query = query.filter(Ticket.department_id == dept_id)

    unassigned_count = query.filter(
        Ticket.assigned_staff_id == None,
        Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS])
    ).count()

    assigned_workload = db.query(Ticket).filter(
        Ticket.assigned_staff_id == current_user.id,
        Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS, TicketStatus.WAITING_FOR_STUDENT])
    ).count()

    high_priority = query.filter(
        Ticket.priority.in_([TicketPriority.HIGH, TicketPriority.URGENT]),
        Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS])
    ).count()

    awaiting_staff = query.filter(
        Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS])
    ).count()

    total_resolved = query.filter(
        Ticket.status.in_([TicketStatus.RESOLVED, TicketStatus.CLOSED])
    ).count()

    dept_code = current_user.department.code if current_user.department else "ALL"

    return StaffDashboardMetrics(
        unassigned_department_tickets_count=unassigned_count,
        assigned_workload_count=assigned_workload,
        high_priority_count=high_priority,
        awaiting_staff_response_count=awaiting_staff,
        total_resolved_count=total_resolved,
        department_code=dept_code,
    )

@router.get("/admin", response_model=AdminDashboardMetrics)
def get_admin_dashboard(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    # Tickets by department
    dept_counts = {}
    departments = db.query(Department).all()
    for d in departments:
        dept_counts[d.name] = db.query(Ticket).filter(Ticket.department_id == d.id).count()

    # Tickets by status
    status_counts = {}
    for st in TicketStatus:
        status_counts[st.value] = db.query(Ticket).filter(Ticket.status == st).count()

    # Unanswered / low-confidence chatbot questions
    unanswered_count = db.query(ChatMessage).filter(
        ChatMessage.sender_role == MessageRole.ASSISTANT,
        ChatMessage.confidence_score <= 0.15
    ).count()

    # Feedback counts
    helpful_count = db.query(AnswerFeedback).filter(AnswerFeedback.is_helpful == True).count()
    unhelpful_count = db.query(AnswerFeedback).filter(AnswerFeedback.is_helpful == False).count()

    # Documents metrics
    awaiting_processing = db.query(IngestionJob).filter(
        IngestionJob.status.in_([JobStatus.PENDING, JobStatus.PROCESSING])
    ).count()

    published_docs = db.query(KnowledgeDocument).filter(
        KnowledgeDocument.status == ContentStatus.PUBLISHED
    ).count()

    total_users = db.query(User).count()

    return AdminDashboardMetrics(
        tickets_by_department=dept_counts,
        tickets_by_status=status_counts,
        unanswered_inquiries_count=unanswered_count,
        helpful_feedback_count=helpful_count,
        unhelpful_feedback_count=unhelpful_count,
        documents_awaiting_processing=awaiting_processing,
        total_published_documents=published_docs,
        total_users_count=total_users,
    )
