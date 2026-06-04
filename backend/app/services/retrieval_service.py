from dataclasses import dataclass

from rank_bm25 import BM25Okapi
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.models.chunk import Chunk
from app.models.document import Document
from app.services.embedding_service import EmbeddingService


@dataclass(frozen=True)
class RetrievalResult:
    chunk_id: str
    content: str
    document_id: str
    document_name: str
    page_number: int | None
    chunk_index: int
    score: float


class RetrievalService:
    def __init__(self, embedding_service: EmbeddingService | None = None) -> None:
        self.embedding_service = embedding_service or EmbeddingService()

    def hybrid_search(self, db: DbSession, user_id: str, query: str, top_k: int = 8) -> list[RetrievalResult]:
        chunks = self._load_user_chunks(db, user_id)
        if not chunks:
            return []

        dense_ranked_ids = self._dense_ranked_ids(query, user_id, top_k=max(top_k * 3, 20))
        bm25_ranked_ids = self._bm25_ranked_ids(chunks, query, top_k=max(top_k * 3, 20))
        scores = self._reciprocal_rank_fusion([dense_ranked_ids, bm25_ranked_ids])
        chunk_by_embedding_id = {chunk.embedding_id: chunk for chunk in chunks if chunk.embedding_id}
        ranked_chunks = [
            chunk_by_embedding_id[embedding_id]
            for embedding_id, _score in sorted(scores.items(), key=lambda item: item[1], reverse=True)
            if embedding_id in chunk_by_embedding_id
        ]

        return [
            RetrievalResult(
                chunk_id=chunk.id,
                content=chunk.content,
                document_id=chunk.document_id,
                document_name=chunk.document.original_filename,
                page_number=chunk.page_number,
                chunk_index=chunk.chunk_index,
                score=scores.get(chunk.embedding_id or "", 0.0),
            )
            for chunk in ranked_chunks[:top_k]
        ]

    def _load_user_chunks(self, db: DbSession, user_id: str) -> list[Chunk]:
        statement = select(Chunk).join(Document).where(Document.user_id == user_id, Document.status == "processed")
        return list(db.scalars(statement).unique())

    def _dense_ranked_ids(self, query: str, user_id: str, top_k: int) -> list[str]:
        matches = self.embedding_service.query(query, user_id=user_id, top_k=top_k)
        return [str(match["id"]) for match in matches if match.get("id")]

    def _bm25_ranked_ids(self, chunks: list[Chunk], query: str, top_k: int) -> list[str]:
        tokenized_corpus = [self._tokenize(chunk.content) for chunk in chunks]
        bm25 = BM25Okapi(tokenized_corpus)
        scores = bm25.get_scores(self._tokenize(query))
        ranked = sorted(zip(chunks, scores, strict=True), key=lambda item: item[1], reverse=True)
        return [chunk.embedding_id or chunk.id for chunk, score in ranked[:top_k] if score > 0]

    def _reciprocal_rank_fusion(self, ranked_lists: list[list[str]], k: int = 60) -> dict[str, float]:
        scores: dict[str, float] = {}
        for ranked_list in ranked_lists:
            for rank, item_id in enumerate(ranked_list, start=1):
                scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (k + rank)
        return scores

    def _tokenize(self, text: str) -> list[str]:
        return [token.lower() for token in text.split() if token.strip()]
