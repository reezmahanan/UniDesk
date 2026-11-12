from datetime import datetime
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.ticket import Ticket, TicketStatus, TicketPriority, TicketEvent, TicketReply, TicketInternalNote
from app.models.department import Department
from app.models.user import User, UserRole

VALID_TRANSITIONS = {
    TicketStatus.OPEN: [TicketStatus.IN_PROGRESS, TicketStatus.RESOLVED, TicketStatus.CLOSED],
    TicketStatus.IN_PROGRESS: [TicketStatus.WAITING_FOR_STUDENT, TicketStatus.RESOLVED, TicketStatus.CLOSED],
    TicketStatus.WAITING_FOR_STUDENT: [TicketStatus.IN_PROGRESS, TicketStatus.RESOLVED, TicketStatus.CLOSED],
    TicketStatus.RESOLVED: [TicketStatus.IN_PROGRESS, TicketStatus.CLOSED],
    TicketStatus.CLOSED: [TicketStatus.IN_PROGRESS],
}

CATEGORY_TO_DEPT_CODE = {
    "it": "IT",
    "it_support": "IT",
    "lms": "IT",
    "wifi": "IT",
    "admissions": "ADMISSIONS",
    "ugc": "ADMISSIONS",
    "academics": "ACADEMICS",
    "exams": "ACADEMICS",
    "course_registration": "ACADEMICS",
    "welfare": "WELFARE",
    "mahapola": "WELFARE",
    "bursary": "WELFARE",
    "fees": "WELFARE",
    "library": "LIBRARY",
    "general": "GENERAL",
}

class TicketService:
    def generate_ticket_number(self, db: Session) -> str:
        current_year = datetime.utcnow().year
        total_tickets = db.query(Ticket).count() + 1
        return f"APX-{current_year}-{total_tickets:04d}"

    def resolve_department_id(self, db: Session, category: str, requested_dept_id: Optional[int] = None) -> int:
        if requested_dept_id:
            dept = db.query(Department).filter(Department.id == requested_dept_id).first()
            if dept:
                return dept.id

        code = CATEGORY_TO_DEPT_CODE.get(category.lower(), "GENERAL")
        dept = db.query(Department).filter(Department.code == code).first()
        if dept:
            return dept.id

        # Fallback to first department
        first_dept = db.query(Department).first()
        return first_dept.id if first_dept else 1

    def transition_status(
        self,
        db: Session,
        ticket: Ticket,
        new_status: TicketStatus,
        acting_user: User,
        comment: Optional[str] = None
    ) -> Ticket:
        # Check permissions: Student can only close or reopen their own resolved ticket
        if acting_user.role == UserRole.STUDENT:
            if ticket.student_id != acting_user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this ticket.")
            if ticket.status == TicketStatus.RESOLVED and new_status in [TicketStatus.CLOSED, TicketStatus.IN_PROGRESS]:
                pass  # Allowed student confirmation or reopen
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Students may only confirm resolution (Close) or Reopen a resolved ticket."
                )

        # Validate transition matrix
        allowed_next = VALID_TRANSITIONS.get(ticket.status, [])
        if new_status not in allowed_next and new_status != ticket.status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid ticket status transition from {ticket.status.value} to {new_status.value}."
            )

        old_status = ticket.status
        ticket.status = new_status
        ticket.updated_at = datetime.utcnow()

        if new_status == TicketStatus.RESOLVED and not ticket.resolved_at:
            ticket.resolved_at = datetime.utcnow()
        elif new_status == TicketStatus.CLOSED and not ticket.closed_at:
            ticket.closed_at = datetime.utcnow()

        # Audit Event
        event = TicketEvent(
            ticket_id=ticket.id,
            user_id=acting_user.id,
            event_type="STATUS_CHANGE",
            old_value=old_status.value,
            new_value=new_status.value,
            comment=comment or f"Status changed to {new_status.value}",
        )
        db.add(event)
        db.commit()
        db.refresh(ticket)
        return ticket

    def assign_ticket(
        self,
        db: Session,
        ticket: Ticket,
        staff_id: Optional[int],
        acting_user: User,
        department_id: Optional[int] = None,
        comment: Optional[str] = None
    ) -> Ticket:
        old_staff = str(ticket.assigned_staff_id) if ticket.assigned_staff_id else "Unassigned"
        old_dept = str(ticket.department_id)

        if department_id and department_id != ticket.department_id:
            dept = db.query(Department).filter(Department.id == department_id).first()
            if not dept:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found.")
            ticket.department_id = dept.id
            db.add(TicketEvent(
                ticket_id=ticket.id,
                user_id=acting_user.id,
                event_type="REASSIGNED_DEPT",
                old_value=old_dept,
                new_value=str(department_id),
                comment=comment or f"Department reassigned to {dept.name}",
            ))

        if staff_id is not None:
            if staff_id > 0:
                staff_user = db.query(User).filter(User.id == staff_id, User.role.in_([UserRole.STAFF, UserRole.ADMIN])).first()
                if not staff_user:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff user not found.")
                ticket.assigned_staff_id = staff_user.id
                new_val = f"{staff_user.full_name} ({staff_user.email})"
            else:
                ticket.assigned_staff_id = None
                new_val = "Unassigned"

            db.add(TicketEvent(
                ticket_id=ticket.id,
                user_id=acting_user.id,
                event_type="ASSIGNED",
                old_value=old_staff,
                new_value=new_val,
                comment=comment or f"Assignment updated to {new_val}",
            ))

        ticket.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(ticket)
        return ticket

ticket_service = TicketService()
