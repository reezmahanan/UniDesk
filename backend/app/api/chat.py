from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.chat import ChatSession, ChatMessage, MessageRole, AnswerFeedback
from app.models.department import Department
from app.schemas.chat import (
    ChatMessageCreate,
    ChatMessageResponse,
    ChatSessionResponse,
    AnswerFeedbackCreate,
    ChatToTicketDraftRequest,
    ChatToTicketDraftResponse,
)
from app.api.deps import get_current_user, require_student
from app.services.rag_service import rag_service
from app.core.rate_limit import rate_limiter
from app.config import settings

router = APIRouter(prefix="/chat", tags=["AI Chatbot"])

@router.get("/sessions", response_model=List[ChatSessionResponse])
def list_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sessions = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).order_by(ChatSession.updated_at.desc()).all()
    return sessions

@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    title: Optional[str] = "New Academic Inquiry",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = ChatSession(
        user_id=current_user.id,
        title=title or "New Academic Inquiry"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
def get_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found.")
    if session.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this conversation.")
    return session

@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found.")
    if session.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    db.delete(session)
    db.commit()
    return {"message": "Chat history deleted successfully."}

@router.post("/message", response_model=ChatMessageResponse)
def send_message(
    req: ChatMessageCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rate_limiter.check_rate_limit(f"chat_{current_user.id}", max_requests=settings.CHAT_RATE_LIMIT_PER_MINUTE, window_seconds=60)

    # 1. Resolve or create session
    if req.session_id:
        session = db.query(ChatSession).filter(ChatSession.id == req.session_id, ChatSession.user_id == current_user.id).first()
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found.")
    else:
        # Create new session with title from first message
        title_snippet = req.content[:35] + ("..." if len(req.content) > 35 else "")
        session = ChatSession(user_id=current_user.id, title=title_snippet)
        db.add(session)
        db.commit()
        db.refresh(session)

    # 2. Save user message
    user_msg = ChatMessage(
        session_id=session.id,
        sender_role=MessageRole.USER,
        content=req.content,
        citations=[],
    )
    db.add(user_msg)
    db.commit()

    # 3. Perform grounded RAG search
    rag_result = rag_service.generate_grounded_response(db, req.content)

    # 4. Save assistant response
    assistant_msg = ChatMessage(
        session_id=session.id,
        sender_role=MessageRole.ASSISTANT,
        content=rag_result["answer"],
        citations=rag_result["citations"],
        confidence_score=rag_result["confidence_score"],
    )
    db.add(assistant_msg)
    session.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(assistant_msg)

    return assistant_msg

@router.post("/feedback")
def submit_feedback(
    req: AnswerFeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    msg = db.query(ChatMessage).filter(ChatMessage.id == req.message_id).first()
    if not msg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found.")

    feedback = AnswerFeedback(
        message_id=msg.id,
        user_id=current_user.id,
        is_helpful=req.is_helpful,
        comment=req.comment,
    )
    db.add(feedback)
    db.commit()
    return {"message": "Thank you for your feedback!"}

@router.post("/hand-off-draft", response_model=ChatToTicketDraftResponse)
def generate_handoff_draft(
    req: ChatToTicketDraftRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(ChatSession).filter(ChatSession.id == req.session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")

    user_msgs = [m.content for m in session.messages if m.sender_role == MessageRole.USER]
    last_query = user_msgs[-1] if user_msgs else "Academic assistance needed"

    # Determine suggested department
    suggested_dept = db.query(Department).filter(Department.code == "IT").first()
    lower_q = last_query.lower()
    if any(k in lower_q for k in ["mahapola", "bursary", "stipend", "welfare", "financial"]):
        suggested_dept = db.query(Department).filter(Department.code == "WELFARE").first()
    elif any(k in lower_q for k in ["admission", "ugc", "z-score", "enroll"]):
        suggested_dept = db.query(Department).filter(Department.code == "ADMISSIONS").first()
    elif any(k in lower_q for k in ["exam", "gpa", "credit", "deferment"]):
        suggested_dept = db.query(Department).filter(Department.code == "ACADEMICS").first()
    elif any(k in lower_q for k in ["library", "book", "fine", "catalog"]):
        suggested_dept = db.query(Department).filter(Department.code == "LIBRARY").first()

    # Create transcript excerpt
    transcript_lines = []
    for m in session.messages[-4:]:
        role_label = "Student" if m.sender_role == MessageRole.USER else "UniDesk Bot"
        clean_text = m.content[:300]
        transcript_lines.append(f"{role_label}: {clean_text}")
    transcript_excerpt = "\n".join(transcript_lines)

    return ChatToTicketDraftResponse(
        suggested_subject=f"Inquiry regarding {last_query[:60]}",
        suggested_description=f"I was inquiring through the AI Help Desk regarding: '{last_query}'. Additional assistance is requested from department officers.",
        suggested_category="general",
        suggested_department_id=suggested_dept.id if suggested_dept else None,
        transcript_excerpt=transcript_excerpt,
    )
