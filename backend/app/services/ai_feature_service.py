from sqlalchemy import func, select
from sqlalchemy.orm import Session as DbSession

from app.models.chunk import Chunk
from app.models.document import Document


def require_processed_document(db: DbSession, document_id: str, user_id: str) -> Document:
    document = db.get(Document, document_id)
    if document is None or document.user_id != user_id:
        raise ValueError("Document not found")
    if document.status != "processed":
        raise ValueError("Document must be processed before using AI features")
    return document


def document_context(db: DbSession, document_id: str, max_chunks: int = 18) -> str:
    chunks = list(
        db.scalars(
            select(Chunk)
            .where(Chunk.document_id == document_id)
            .order_by(Chunk.chunk_index.asc())
            .limit(max_chunks)
        )
    )
    return "\n\n".join(
        f"[chunk {chunk.chunk_index}, page {chunk.page_number or 'n/a'}]\n{chunk.content}" for chunk in chunks
    )


def document_chunk_count(db: DbSession, document_id: str) -> int:
    return db.scalar(select(func.count()).select_from(Chunk).where(Chunk.document_id == document_id)) or 0
