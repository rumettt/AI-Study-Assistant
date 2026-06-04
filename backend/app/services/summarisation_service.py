from sqlalchemy.orm import Session as DbSession

from app.models.summary import Summary
from app.prompts import SUMMARY_PROMPT
from app.services.ai_feature_service import document_context, require_processed_document
from app.services.llm_service import LlmService


class SummarisationService:
    def __init__(self, llm: LlmService | None = None) -> None:
        self.llm = llm or LlmService()

    def generate(self, db: DbSession, document_id: str, user_id: str) -> Summary:
        require_processed_document(db, document_id, user_id)
        context = document_context(db, document_id)
        parsed = self.llm.json_object(SUMMARY_PROMPT, f"Material:\n{context}")
        abstract = str(parsed.get("abstract", "")).strip()
        concepts = parsed.get("key_concepts", [])
        if not isinstance(concepts, list):
            concepts = []

        summary = db.query(Summary).filter(Summary.document_id == document_id).one_or_none()
        if summary is None:
            summary = Summary(document_id=document_id, abstract=abstract, key_concepts=concepts)
            db.add(summary)
        else:
            summary.abstract = abstract
            summary.key_concepts = [str(concept) for concept in concepts]
        db.commit()
        db.refresh(summary)
        return summary
