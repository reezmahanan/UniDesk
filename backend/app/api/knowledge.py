from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.knowledge import FAQ, ServiceLink, ContentStatus
from app.schemas.knowledge import (
    FAQCreate,
    FAQUpdate,
    FAQResponse,
    ServiceLinkResponse,
    KnowledgeSearchResult,
)
from app.api.deps import get_current_user, require_staff, require_admin
from app.services.rag_service import rag_service

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base & FAQs"])

@router.get("/faqs", response_model=List[FAQResponse])
def list_faqs(
    category: Optional[str] = None,
    language: Optional[str] = "en",
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(FAQ)
    if not current_user or current_user.role == UserRole.STUDENT:
        query = query.filter(FAQ.status == ContentStatus.PUBLISHED)
    if category:
        query = query.filter(FAQ.category == category)
    if language:
        query = query.filter(FAQ.language == language)
    return query.order_by(FAQ.created_at.desc()).all()

@router.post("/faqs", response_model=FAQResponse, status_code=status.HTTP_201_CREATED)
def create_faq(
    req: FAQCreate,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    faq = FAQ(
        category=req.category,
        question=req.question,
        answer=req.answer,
        department_id=req.department_id,
        language=req.language,
        source_reference=req.source_reference,
        status=req.status,
    )
    db.add(faq)
    db.commit()
    db.refresh(faq)
    return faq

@router.patch("/faqs/{faq_id}", response_model=FAQResponse)
def update_faq(
    faq_id: int,
    req: FAQUpdate,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found.")

    for k, v in req.dict(exclude_unset=True).items():
        setattr(faq, k, v)
    db.commit()
    db.refresh(faq)
    return faq

@router.delete("/faqs/{faq_id}")
def delete_faq(
    faq_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found.")
    db.delete(faq)
    db.commit()
    return {"message": "FAQ deleted."}

@router.get("/services", response_model=List[ServiceLinkResponse])
def list_service_links(db: Session = Depends(get_db)):
    links = db.query(ServiceLink).filter(ServiceLink.is_active == True).order_by(ServiceLink.display_order.asc()).all()
    return links

@router.get("/search", response_model=List[KnowledgeSearchResult])
def search_knowledge(
    q: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not q.strip():
        return []
    chunks = rag_service.search_relevant_chunks(db, q, top_k=6)
    results = []
    for item in chunks:
        ch = item["chunk"]
        doc = item["document"]
        results.append(KnowledgeSearchResult(
            chunk_id=ch.id,
            document_id=doc.id,
            document_title=doc.title,
            content=ch.content,
            page_number=ch.page_number,
            section_heading=ch.section_heading,
            score=round(item["score"], 3),
        ))
    return results
