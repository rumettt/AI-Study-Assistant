CHAT_SYSTEM_PROMPT = """
You answer questions only from the provided study material. If the context does not support an answer,
say that the uploaded material does not contain enough information. Cite sources inline as [source N].
""".strip()

SUMMARY_PROMPT = """
Summarize the study material. Return strict JSON with keys:
abstract: one concise paragraph
key_concepts: an array of short bullet-style concept strings
""".strip()

QUIZ_PROMPT = """
Create a study quiz from the material. Return strict JSON:
{"questions":[{"type":"mcq","question":"...","options":["A","B","C","D"],"correct":"B","explanation":"..."},{"type":"short_answer","question":"...","correct":"...","explanation":"..."}]}
Use 5 to 10 questions, mix MCQ and short-answer, and make every answer grounded in the context.
""".strip()

FLASHCARD_PROMPT = """
Create concise active-recall flashcards from the material. Return strict JSON:
[{"front":"...","back":"..."}]
Each front should be a focused prompt; each back should be brief but complete.
""".strip()
