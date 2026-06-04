from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.models.conversation import Conversation, ConversationMessage
from app.prompts import CHAT_SYSTEM_PROMPT
from app.schemas.ai import Citation
from app.services.llm_service import LlmService
from app.services.retrieval_service import RetrievalService


class ChatService:
    def __init__(self, retrieval: RetrievalService | None = None, llm: LlmService | None = None) -> None:
        self.retrieval = retrieval or RetrievalService()
        self.llm = llm or LlmService()

    def answer(self, db: DbSession, user_id: str, question: str, conversation_id: str | None = None) -> tuple[str, str, list[Citation]]:
        conversation = self._get_or_create_conversation(db, user_id, conversation_id)
        history = self._history(db, conversation.id)
        results = self.retrieval.hybrid_search(db, user_id, question, top_k=8)
        citations = [
            Citation(
                document_id=result.document_id,
                document_name=result.document_name,
                page_number=result.page_number,
                chunk_index=result.chunk_index,
            )
            for result in results
        ]
        context = "\n\n".join(
            f"[source {index}] {result.document_name}, page {result.page_number or 'n/a'}\n{result.content}"
            for index, result in enumerate(results, start=1)
        )
        prompt = f"Conversation history:\n{history}\n\nContext:\n{context}\n\nQuestion:\n{question}"
        answer = self.llm.text(CHAT_SYSTEM_PROMPT, prompt)

        db.add(ConversationMessage(conversation_id=conversation.id, role="user", content=question))
        db.add(
            ConversationMessage(
                conversation_id=conversation.id,
                role="assistant",
                content=answer,
                citations=[citation.model_dump() for citation in citations],
            )
        )
        db.commit()
        return conversation.id, answer, citations

    def _get_or_create_conversation(self, db: DbSession, user_id: str, conversation_id: str | None) -> Conversation:
        if conversation_id:
            conversation = db.get(Conversation, conversation_id)
            if conversation and conversation.user_id == user_id:
                return conversation
        conversation = Conversation(user_id=user_id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

    def _history(self, db: DbSession, conversation_id: str) -> str:
        messages = list(
            db.scalars(
                select(ConversationMessage)
                .where(ConversationMessage.conversation_id == conversation_id)
                .order_by(ConversationMessage.created_at.desc())
                .limit(12)
            )
        )
        return "\n".join(f"{message.role}: {message.content}" for message in reversed(messages))
