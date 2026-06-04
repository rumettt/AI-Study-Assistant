"use client";

import { useState } from "react";
import { DocumentPicker } from "@/components/DocumentPicker";
import { WorkspaceShell } from "@/components/WorkspaceShell";
import { useDocuments } from "@/components/useDocuments";
import { generateQuiz, submitQuiz, type QuizResponse } from "@/lib/api";

export default function QuizPage() {
  const { documents, token, error } = useDocuments();
  const [documentId, setDocumentId] = useState("");
  const [quiz, setQuiz] = useState<QuizResponse | null>(null);
  const [answers, setAnswers] = useState<string[]>([]);
  const [score, setScore] = useState<string | null>(null);
  const [pageError, setPageError] = useState<string | null>(null);

  async function handleGenerate() {
    if (!token || !documentId) return;
    setPageError(null);
    try {
      const nextQuiz = await generateQuiz(documentId, token);
      setQuiz(nextQuiz);
      setAnswers(new Array(nextQuiz.questions.length).fill(""));
      setScore(null);
    } catch (err) {
      setPageError(err instanceof Error ? err.message : "Could not generate quiz");
    }
  }

  async function handleSubmit() {
    if (!token || !quiz) return;
    const result = await submitQuiz(quiz.id, answers, token);
    setScore(`${result.score}/${result.total}`);
  }

  return (
    <WorkspaceShell>
      <h1 className="text-3xl font-semibold text-ink">Quiz</h1>
      <div className="mt-6 rounded-lg border border-slate-200 bg-white p-5">
        <DocumentPicker documents={documents} value={documentId} onChange={setDocumentId} />
        <button className="mt-4 rounded-md bg-accent px-5 py-2.5 text-sm font-semibold text-white" disabled={!documentId} onClick={handleGenerate}>
          Generate quiz
        </button>
        {error || pageError ? <p className="mt-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error ?? pageError}</p> : null}
      </div>
      {quiz ? (
        <div className="mt-6 space-y-4">
          {quiz.questions.map((question, index) => (
            <article className="rounded-lg border border-slate-200 bg-white p-5" key={`${question.question}-${index}`}>
              <p className="font-semibold text-ink">{index + 1}. {question.question}</p>
              {question.options.length ? (
                <div className="mt-3 grid gap-2">
                  {question.options.map((option) => (
                    <label className="flex gap-2 text-sm text-slate-700" key={option}>
                      <input checked={answers[index] === option} name={`q-${index}`} onChange={() => setAnswers((current) => current.map((answer, answerIndex) => answerIndex === index ? option : answer))} type="radio" />
                      {option}
                    </label>
                  ))}
                </div>
              ) : (
                <input className="mt-3 w-full rounded-md border border-slate-300 px-3 py-2 text-sm" value={answers[index] ?? ""} onChange={(event) => setAnswers((current) => current.map((answer, answerIndex) => answerIndex === index ? event.target.value : answer))} />
              )}
              {score ? <p className="mt-3 text-sm text-slate-600">Answer: {question.correct}. {question.explanation}</p> : null}
            </article>
          ))}
          <button className="rounded-md bg-accent px-5 py-2.5 text-sm font-semibold text-white" onClick={handleSubmit}>Submit quiz</button>
          {score ? <p className="text-sm font-semibold text-ink">Score: {score}</p> : null}
        </div>
      ) : null}
    </WorkspaceShell>
  );
}
