import random
from tempfile import NamedTemporaryFile

import genanki
from sqlalchemy.orm import Session as DbSession

from app.models.flashcard import FlashcardSet
from app.prompts import FLASHCARD_PROMPT
from app.services.ai_feature_service import document_context, require_processed_document
from app.services.llm_service import LlmService


class FlashcardService:
    def __init__(self, llm: LlmService | None = None) -> None:
        self.llm = llm or LlmService()

    def generate(self, db: DbSession, document_id: str, user_id: str) -> FlashcardSet:
        require_processed_document(db, document_id, user_id)
        cards = self.llm.json_array(FLASHCARD_PROMPT, f"Material:\n{document_context(db, document_id)}")
        normalized = [{"front": str(card.get("front", "")), "back": str(card.get("back", ""))} for card in cards]
        flashcard_set = FlashcardSet(document_id=document_id, cards=normalized)
        db.add(flashcard_set)
        db.commit()
        db.refresh(flashcard_set)
        return flashcard_set

    def export_apkg(self, db: DbSession, set_id: str, user_id: str) -> bytes:
        flashcard_set = db.get(FlashcardSet, set_id)
        if flashcard_set is None or flashcard_set.document.user_id != user_id:
            raise ValueError("Flashcard set not found")

        model = genanki.Model(
            random.randrange(1 << 30, 1 << 31),
            "AI Study Assistant Basic",
            fields=[{"name": "Front"}, {"name": "Back"}],
            templates=[{"name": "Card 1", "qfmt": "{{Front}}", "afmt": "{{FrontSide}}<hr id=\"answer\">{{Back}}"}],
        )
        deck = genanki.Deck(random.randrange(1 << 30, 1 << 31), flashcard_set.document.original_filename)
        for card in flashcard_set.cards:
            deck.add_note(genanki.Note(model=model, fields=[card["front"], card["back"]]))
        with NamedTemporaryFile(suffix=".apkg") as temp_file:
            genanki.Package(deck).write_to_file(temp_file.name)
            temp_file.seek(0)
            return temp_file.read()
