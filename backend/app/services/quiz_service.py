from sqlalchemy.orm import Session as DbSession

from app.models.quiz import Quiz, QuizAttempt
from app.prompts import QUIZ_PROMPT
from app.services.ai_feature_service import document_context, require_processed_document
from app.services.llm_service import LlmService


class QuizService:
    def __init__(self, llm: LlmService | None = None) -> None:
        self.llm = llm or LlmService()

    def generate(self, db: DbSession, document_id: str, user_id: str) -> Quiz:
        require_processed_document(db, document_id, user_id)
        parsed = self.llm.json_object(QUIZ_PROMPT, f"Material:\n{document_context(db, document_id)}")
        questions = parsed.get("questions", [])
        if not isinstance(questions, list):
            questions = []
        quiz = Quiz(document_id=document_id, questions=questions)
        db.add(quiz)
        db.commit()
        db.refresh(quiz)
        return quiz

    def score(self, db: DbSession, quiz_id: str, user_id: str, answers: list[str]) -> QuizAttempt:
        quiz = db.get(Quiz, quiz_id)
        if quiz is None or quiz.document.user_id != user_id:
            raise ValueError("Quiz not found")
        score = 0
        for answer, question in zip(answers, quiz.questions, strict=False):
            correct = str(question.get("correct", "")).strip().lower()
            if answer.strip().lower() == correct:
                score += 1
        attempt = QuizAttempt(quiz_id=quiz.id, user_id=user_id, score=score, total=len(quiz.questions))
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
        return attempt
