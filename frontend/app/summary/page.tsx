"use client";

import { useState } from "react";
import { DocumentPicker } from "@/components/DocumentPicker";
import { WorkspaceShell } from "@/components/WorkspaceShell";
import { useDocuments } from "@/components/useDocuments";
import { generateSummary, type SummaryResponse } from "@/lib/api";

export default function SummaryPage() {
  const { documents, token, error } = useDocuments();
  const [documentId, setDocumentId] = useState("");
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [pageError, setPageError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleGenerate() {
    if (!token || !documentId) return;
    setIsLoading(true);
    setPageError(null);
    try {
      setSummary(await generateSummary(documentId, token));
    } catch (err) {
      setPageError(err instanceof Error ? err.message : "Could not generate summary");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <WorkspaceShell>
      <h1 className="text-3xl font-semibold text-ink">Summary</h1>
      <div className="mt-6 rounded-lg border border-slate-200 bg-white p-5">
        <DocumentPicker documents={documents} value={documentId} onChange={setDocumentId} />
        <button className="mt-4 rounded-md bg-accent px-5 py-2.5 text-sm font-semibold text-white" disabled={!documentId || isLoading} onClick={handleGenerate}>
          {isLoading ? "Generating..." : "Generate summary"}
        </button>
        {error || pageError ? <p className="mt-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error ?? pageError}</p> : null}
      </div>
      {summary ? (
        <article className="mt-6 rounded-lg border border-slate-200 bg-white p-5">
          <p className="text-sm leading-6 text-slate-700">{summary.abstract}</p>
          <ul className="mt-4 list-disc space-y-2 pl-5 text-sm text-slate-700">
            {summary.key_concepts.map((concept) => (
              <li key={concept}>{concept}</li>
            ))}
          </ul>
        </article>
      ) : null}
    </WorkspaceShell>
  );
}
