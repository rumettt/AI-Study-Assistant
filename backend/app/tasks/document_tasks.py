from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.chunk import Chunk
from app.models.document import Document
from app.services.embedding_service import EmbeddingService
from app.services.ingestion_service import IngestionService


@celery_app.task(name="documents.process")
def process_document(document_id: str) -> None:
    db = SessionLocal()
    try:
        _process_document(db, document_id)
    finally:
        db.close()


def _process_document(db: Session, document_id: str) -> None:
    document = db.get(Document, document_id)
    if document is None:
        return

    document.status = "processing"
    document.error_message = None
    db.commit()

    try:
        ingestion = IngestionService()
        parsed_blocks = ingestion.load_blocks(document)
        text_chunks = ingestion.chunk_blocks(parsed_blocks)
        if not text_chunks:
            raise ValueError("No extractable text was found in this document")

        db.query(Chunk).filter(Chunk.document_id == document.id).delete()
        chunks = [
            Chunk(
                document_id=document.id,
                chunk_index=chunk.chunk_index,
                page_number=chunk.page_number,
                source_type=chunk.source_type,
                content=chunk.content,
                token_count=chunk.token_count,
            )
            for chunk in text_chunks
        ]
        db.add_all(chunks)
        db.flush()

        EmbeddingService().upsert_chunks(document, chunks)

        document.status = "processed"
        document.processed_at = datetime.now(UTC)
        db.commit()
    except Exception as exc:
        db.rollback()
        document = db.get(Document, document_id)
        if document is not None:
            document.status = "failed"
            document.error_message = str(exc)
            db.commit()
        raise
