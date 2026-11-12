from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.notice import Notice
from app.models.user import User, UserRole
from app.schemas.notice import NoticeCreate, NoticeResponse
from app.api.deps import get_current_user, require_admin

router = APIRouter(prefix="/notices", tags=["Notices"])

@router.get("", response_model=List[NoticeResponse])
def list_notices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Notice).filter(Notice.is_published == True)
    if current_user.role == UserRole.STUDENT:
        query = query.filter(Notice.audience.in_(["ALL", "STUDENTS"]))
    return query.order_by(Notice.publish_date.desc()).all()

@router.post("", response_model=NoticeResponse, status_code=status.HTTP_201_CREATED)
def create_notice(
    req: NoticeCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    notice = Notice(
        title=req.title,
        content=req.content,
        tag=req.tag,
        audience=req.audience,
        is_published=req.is_published,
        expiry_date=req.expiry_date,
    )
    db.add(notice)
    db.commit()
    db.refresh(notice)
    return notice

@router.delete("/{notice_id}")
def delete_notice(
    notice_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    notice = db.query(Notice).filter(Notice.id == notice_id).first()
    if not notice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notice not found.")
    db.delete(notice)
    db.commit()
    return {"message": "Notice deleted."}
