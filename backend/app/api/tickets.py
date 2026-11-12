from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.ticket import (
    Ticket,
    TicketStatus,
    TicketPriority,
    TicketReply,
    TicketInternalNote,
    TicketEvent,
    Attachment,
)
from app.models.department import Department
from app.models.audit import AuditLog
from app.schemas.ticket import (
    TicketCreate,
    TicketResponse,
    TicketDetailResponse,
    TicketStatusUpdate,
    TicketAssignUpdate,
    TicketPriorityUpdate,
    TicketReplyCreate,
    TicketReplyResponse,
    TicketInternalNoteCreate,
    TicketInternalNoteResponse,
    AttachmentResponse,
    StaffAiSummaryResponse,
    StaffAiDraftReplyResponse,
)
from app.api.deps import get_current_user, require_staff, require_student
from app.services.ticket_service import ticket_service
from app.services.file_storage import file_storage
from app.services.rag_service import rag_service

router = APIRouter(prefix="/tickets", tags=["Tickets"])

def get_authorized_ticket(ticket_id: int, user: User, db: Session) -> Ticket:
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found.")

    if user.role == UserRole.STUDENT:
        if ticket.student_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this ticket.")
    elif user.role == UserRole.STAFF:
        # Staff can view tickets for their assigned department or if assigned to them
        if user.department_id and ticket.department_id != user.department_id and ticket.assigned_staff_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access restricted to your department tickets.")

    return ticket

@router.get("", response_model=List[TicketResponse])
def list_tickets(
    status_filter: Optional[TicketStatus] = None,
    category_filter: Optional[str] = None,
    department_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Ticket)

    if current_user.role == UserRole.STUDENT:
        query = query.filter(Ticket.student_id == current_user.id)
    elif current_user.role == UserRole.STAFF:
        if current_user.department_id:
            query = query.filter(
                (Ticket.department_id == current_user.department_id) |
                (Ticket.assigned_staff_id == current_user.id)
            )

    if status_filter:
        query = query.filter(Ticket.status == status_filter)
    if category_filter:
        query = query.filter(Ticket.category == category_filter)
    if department_id and current_user.role in [UserRole.STAFF, UserRole.ADMIN]:
        query = query.filter(Ticket.department_id == department_id)

    return query.order_by(Ticket.updated_at.desc()).all()

@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    req: TicketCreate,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    dept_id = ticket_service.resolve_department_id(db, req.category, req.department_id)
    ticket_num = ticket_service.generate_ticket_number(db)

    ticket = Ticket(
        ticket_number=ticket_num,
        student_id=current_user.id,
        department_id=dept_id,
        subject=req.subject,
        description=req.description,
        category=req.category,
        priority=req.priority,
        status=TicketStatus.OPEN,
        transcript_excerpt=req.transcript_excerpt,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    # Log Creation Event
    db.add(TicketEvent(
        ticket_id=ticket.id,
        user_id=current_user.id,
        event_type="CREATED",
        new_value=ticket.status.value,
        comment="Ticket submitted by student",
    ))
    db.commit()
    db.refresh(ticket)
    return ticket

@router.get("/{ticket_id}", response_model=TicketDetailResponse)
def get_ticket_detail(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = get_authorized_ticket(ticket_id, current_user, db)
    
    # Internal notes strictly filtered out for student role
    filtered_internal_notes = []
    if current_user.role in [UserRole.STAFF, UserRole.ADMIN]:
        filtered_internal_notes = ticket.internal_notes

    return TicketDetailResponse(
        id=ticket.id,
        ticket_number=ticket.ticket_number,
        student_id=ticket.student_id,
        student=ticket.student,
        department_id=ticket.department_id,
        assigned_staff_id=ticket.assigned_staff_id,
        assigned_staff=ticket.assigned_staff,
        subject=ticket.subject,
        description=ticket.description,
        category=ticket.category,
        priority=ticket.priority,
        status=ticket.status,
        transcript_excerpt=ticket.transcript_excerpt,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        resolved_at=ticket.resolved_at,
        closed_at=ticket.closed_at,
        replies=ticket.replies,
        internal_notes=filtered_internal_notes,
        events=ticket.events,
        attachments=ticket.attachments,
    )

@router.patch("/{ticket_id}/status", response_model=TicketResponse)
def update_status(
    ticket_id: int,
    req: TicketStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = get_authorized_ticket(ticket_id, current_user, db)
    updated = ticket_service.transition_status(db, ticket, req.status, current_user, req.comment)
    return updated

@router.patch("/{ticket_id}/assign", response_model=TicketResponse)
def assign_ticket(
    ticket_id: int,
    req: TicketAssignUpdate,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    ticket = get_authorized_ticket(ticket_id, current_user, db)
    updated = ticket_service.assign_ticket(
        db, ticket, req.assigned_staff_id, current_user, req.department_id, req.comment
    )
    return updated

@router.post("/{ticket_id}/replies", response_model=TicketReplyResponse)
def add_reply(
    ticket_id: int,
    req: TicketReplyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = get_authorized_ticket(ticket_id, current_user, db)

    reply = TicketReply(
        ticket_id=ticket.id,
        user_id=current_user.id,
        message=req.message,
        is_solution=req.is_solution,
    )
    db.add(reply)

    # Automatic status adjustment based on role
    if current_user.role == UserRole.STUDENT:
        if ticket.status == TicketStatus.WAITING_FOR_STUDENT:
            ticket.status = TicketStatus.IN_PROGRESS
    elif current_user.role in [UserRole.STAFF, UserRole.ADMIN]:
        if req.is_solution:
            ticket.status = TicketStatus.RESOLVED
            ticket.resolved_at = datetime.utcnow()
        elif ticket.status == TicketStatus.OPEN:
            ticket.status = TicketStatus.IN_PROGRESS

    ticket.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(reply)
    return reply

@router.post("/{ticket_id}/internal-notes", response_model=TicketInternalNoteResponse)
def add_internal_note(
    ticket_id: int,
    req: TicketInternalNoteCreate,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    ticket = get_authorized_ticket(ticket_id, current_user, db)

    note = TicketInternalNote(
        ticket_id=ticket.id,
        staff_id=current_user.id,
        note=req.note,
    )
    db.add(note)
    ticket.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(note)
    return note

@router.post("/{ticket_id}/attachments", response_model=AttachmentResponse)
async def upload_attachment(
    ticket_id: int,
    file: UploadFile = File(...),
    reply_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = get_authorized_ticket(ticket_id, current_user, db)
    stored_name, file_path, size, mime = await file_storage.save_upload(file, is_document=False)

    attachment = Attachment(
        ticket_id=ticket.id,
        reply_id=reply_id,
        uploader_id=current_user.id,
        original_filename=file.filename or "attachment",
        stored_filename=stored_name,
        file_path=file_path,
        file_size=size,
        mime_type=mime,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment

@router.get("/{ticket_id}/attachments/{attachment_id}/download")
def download_attachment(
    ticket_id: int,
    attachment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = get_authorized_ticket(ticket_id, current_user, db)
    att = db.query(Attachment).filter(Attachment.id == attachment_id, Attachment.ticket_id == ticket.id).first()
    if not att:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found.")

    path = file_storage.get_file_path(att.stored_filename, is_document=False)
    return FileResponse(
        path=path,
        media_type=att.mime_type,
        filename=att.original_filename,
    )

@router.get("/{ticket_id}/ai-summary", response_model=StaffAiSummaryResponse)
def get_staff_ai_summary(
    ticket_id: int,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    ticket = get_authorized_ticket(ticket_id, current_user, db)
    replies_text = "\n".join([f"- {r.user.full_name}: {r.message}" for r in ticket.replies])

    summary_text = (
        f"Student {ticket.student.full_name} is seeking support regarding {ticket.category.upper()}. "
        f"Issue Description: '{ticket.subject}'. Current status: {ticket.status.value}. "
        f"There are {len(ticket.replies)} prior public responses in the thread."
    )
    facts = [
        f"Student Index / Email: {ticket.student.student_index or 'N/A'} ({ticket.student.email})",
        f"Faculty / Department: {ticket.student.faculty or 'Computing'} / Dept #{ticket.department_id}",
        f"Priority Level: {ticket.priority.value}",
    ]
    missing = [
        "Official verification receipt or payment voucher if inquiring about bursaries",
        "Screenshot of browser error message if reporting LMS login lock",
    ]

    return StaffAiSummaryResponse(
        ticket_id=ticket.id,
        summary=summary_text,
        key_facts=facts,
        missing_information=missing,
    )

@router.get("/{ticket_id}/ai-draft-reply", response_model=StaffAiDraftReplyResponse)
def get_staff_ai_draft_reply(
    ticket_id: int,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    ticket = get_authorized_ticket(ticket_id, current_user, db)
    retrieved = rag_service.search_relevant_chunks(db, f"{ticket.subject} {ticket.description}", top_k=2)

    ref_sources = [f"{item['document'].title} (Page {item['chunk'].page_number or 1})" for item in retrieved]
    guidance = retrieved[0]["chunk"].content if retrieved else "Refer to standard student affairs procedure."

    suggested = (
        f"Dear {ticket.student.full_name},\n\n"
        f"Thank you for contacting the university help desk regarding '{ticket.subject}'.\n\n"
        f"Regarding your inquiry:\n{guidance[:250]}...\n\n"
        f"Please reply to this ticket if you have further questions or if you require additional assistance.\n\n"
        f"Best regards,\n{current_user.full_name}\nUniversity Help Desk Staff"
    )

    return StaffAiDraftReplyResponse(
        ticket_id=ticket.id,
        suggested_reply=suggested,
        relevant_sources=ref_sources,
    )
