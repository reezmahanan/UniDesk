from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.knowledge import KnowledgeDocument, DocumentChunk, IngestionJob, JobStatus
from app.services.document_extractor import document_extractor
from app.services.chunker import chunker
from app.services.embedding_service import embedding_service

def process_document_ingestion(job_id: int):
    """
    Background worker function to extract text, chunk, generate embeddings,
    and persist document chunks safely.
    """
    db: Session = SessionLocal()
    job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
    if not job:
        db.close()
        return

    doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == job.document_id).first()
    if not doc:
        job.status = JobStatus.FAILED
        job.error_message = "Target document not found."
        db.commit()
        db.close()
        return

    job.status = JobStatus.PROCESSING
    job.started_at = datetime.utcnow()
    db.commit()

    try:
        # 1. Extract
        extraction = document_extractor.extract(doc.file_path, doc.mime_type)
        if not extraction.has_extractable_text:
            job.status = JobStatus.FAILED
            job.error_message = extraction.warning_message or "No extractable text found in document."
            job.completed_at = datetime.utcnow()
            db.commit()
            db.close()
            return

        # 2. Chunk
        chunks_data = chunker.chunk_sections(extraction.sections)
        if not chunks_data:
            job.status = JobStatus.FAILED
            job.error_message = "No valid text chunks generated from document."
            job.completed_at = datetime.utcnow()
            db.commit()
            db.close()
            return

        # 3. Clear existing chunks if re-processing
        db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).delete()

        # 4. Generate embeddings and save chunks
        created_count = 0
        for item in chunks_data:
            emb = embedding_service.generate_embedding(item["content"])
            chunk_obj = DocumentChunk(
                document_id=doc.id,
                chunk_index=item["chunk_index"],
                content=item["content"],
                page_number=item.get("page_number"),
                section_heading=item.get("section_heading"),
                token_count=item.get("token_count"),
                embedding=emb,
            )
            db.add(chunk_obj)
            created_count += 1

        job.status = JobStatus.COMPLETED
        job.chunks_created = created_count
        job.completed_at = datetime.utcnow()
        doc.updated_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        db.rollback()
        job.status = JobStatus.FAILED
        job.error_message = f"Ingestion error: {str(e)}"
        job.completed_at = datetime.utcnow()
        db.commit()

    finally:
        db.close()
