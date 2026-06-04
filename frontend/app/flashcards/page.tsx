"use client";

import { useState } from "react";
import { DocumentPicker } from "@/components/DocumentPicker";
import { WorkspaceShell } from "@/components/WorkspaceShell";
import { useDocuments } from "@/components/useDocuments";
import { exportFlashcards, generateFlashcards, type FlashcardSetResponse } from "@/lib/api";

export default function FlashcardsPage() {
  const { documents, token, error } = useDocuments();
  const [documentId, setDocumentId] = useState("");
  const [set, setSet] = useState<FlashcardSetResponse | null>(null);
  const [flipped, setFlipped] = useState<Record<number, boolean>>({});
  const [pageError, setPageError] = useState<string | null>(null);

  async function handleGenerate() {
    if (!token || !documentId) return;
    setPageError(null);
    try {
      setSet(await generateFlashcards(documentId, token));
    } catch (err) {
      setPageError(err instanceof Error ? err.message : "Could not generate flashcards");
    }
  }

  async function handleExport() {
    if (!token || !set) return;
    const blob = await exportFlashcards(set.id, token);
    const url = window.URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "study-flashcards.apkg";
    anchor.click();
    window.URL.revokeObjectURL(url);
  }

  return (
    <WorkspaceShell>
      <h1 className="text-3xl font-semibold text-ink">Flashcards</h1>
      <div className="mt-6 rounded-lg border border-slate-200 bg-white p-5">
        <DocumentPicker documents={documents} value={documentId} onChange={setDocumentId} />
        <button className="mt-4 rounded-md bg-accent px-5 py-2.5 text-sm font-semibold text-white" disabled={!documentId} onClick={handleGenerate}>
          Generate flashcards
        </button>
        {error || pageError ? <p className="mt-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error ?? pageError}</p> : null}
      </div>
      {set ? (
        <>
          <button className="mt-6 inline-block rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-ink" onClick={handleExport}>
            Export Anki deck
          </button>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            {set.cards.map((card, index) => (
              <button className="min-h-40 rounded-lg border border-slate-200 bg-white p-5 text-left shadow-sm" key={`${card.front}-${index}`} onClick={() => setFlipped((current) => ({ ...current, [index]: !current[index] }))}>
                <p className="text-sm font-semibold text-slate-500">{flipped[index] ? "Back" : "Front"}</p>
                <p className="mt-3 text-base leading-7 text-ink">{flipped[index] ? card.back : card.front}</p>
              </button>
            ))}
          </div>
        </>
      ) : null}
    </WorkspaceShell>
  );
}
