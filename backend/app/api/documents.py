from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.knowledge import KnowledgeDocument, IngestionJob, ContentStatus, JobStatus
from app.models.audit import AuditLog
from app.schemas.knowledge import (
    KnowledgeDocumentResponse,
    IngestionJobResponse,
)
from app.api.deps import get_current_user, require_admin, require_staff
from app.services.file_storage import file_storage
from app.services.ingestion_worker import process_document_ingestion

router = APIRouter(prefix="/documents", tags=["Knowledge Documents"])

@router.get("", response_model=List[KnowledgeDocumentResponse])
def list_documents(
    status_filter: Optional[ContentStatus] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(KnowledgeDocument)
    # Students can only see published documents
    if current_user.role == UserRole.STUDENT:
        query = query.filter(KnowledgeDocument.status == ContentStatus.PUBLISHED)
    elif status_filter:
        query = query.filter(KnowledgeDocument.status == status_filter)

    docs = query.order_by(KnowledgeDocument.created_at.desc()).all()
    res = []
    for d in docs:
        item = KnowledgeDocumentResponse.from_orm(d)
        item.chunks_count = len(d.chunks)
        res.append(item)
    return res

@router.post("", response_model=KnowledgeDocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    version: str = Form("1.0"),
    language: str = Form("en"),
    department_id: Optional[int] = Form(None),
    status: ContentStatus = Form(ContentStatus.PUBLISHED),
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    stored_name, file_path, size, mime = await file_storage.save_upload(file, is_document=True)

    doc = KnowledgeDocument(
        title=title,
        original_filename=file.filename or "doc",
        stored_filename=stored_name,
        file_path=file_path,
        file_size=size,
        mime_type=mime,
        version=version,
        language=language,
        department_id=department_id,
        status=status,
        uploaded_by=current_user.id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Create background ingestion job
    job = IngestionJob(
        document_id=doc.id,
        status=JobStatus.PENDING,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Queue background task
    background_tasks.add_task(process_document_ingestion, job.id)

    db.add(AuditLog(
        user_id=current_user.id,
        action="DOCUMENT_UPLOAD",
        resource_type="DOCUMENT",
        resource_id=str(doc.id),
        details=f"Uploaded '{doc.title}' ({size} bytes). Job #{job.id} queued.",
    ))
    db.commit()

    resp = KnowledgeDocumentResponse.from_orm(doc)
    resp.chunks_count = 0
    return resp

@router.get("/{document_id}/download")
def download_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    if current_user.role == UserRole.STUDENT and doc.status != ContentStatus.PUBLISHED:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to unpublished documents.")

    path = file_storage.get_file_path(doc.stored_filename, is_document=True)
    return FileResponse(
        path=path,
        media_type=doc.mime_type,
        filename=doc.original_filename,
    )

@router.patch("/{document_id}/status", response_model=KnowledgeDocumentResponse)
def update_document_status(
    document_id: int,
    new_status: ContentStatus,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    old = doc.status
    doc.status = new_status
    doc.updated_at = datetime.utcnow()
    db.commit()

    db.add(AuditLog(
        user_id=current_user.id,
        action=f"DOCUMENT_{new_status.value}",
        resource_type="DOCUMENT",
        resource_id=str(doc.id),
        details=f"Document status changed from {old.value} to {new_status.value}",
    ))
    db.commit()
    db.refresh(doc)
    return doc

@router.get("/{document_id}/jobs", response_model=List[IngestionJobResponse])
def get_document_jobs(
    document_id: int,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    jobs = db.query(IngestionJob).filter(IngestionJob.document_id == document_id).order_by(IngestionJob.created_at.desc()).all()
    return jobs
