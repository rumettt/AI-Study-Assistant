"use client";

import { ChangeEvent, FormEvent, useEffect, useState } from "react";
import { getDocumentStatus, uploadDocument, type DocumentResponse, type DocumentStatusResponse } from "@/lib/api";
import { readAccessToken } from "@/lib/auth-store";

const ACCEPTED_TYPES = ".pdf,.pptx,.docx";

export function FileUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [document, setDocument] = useState<DocumentResponse | null>(null);
  const [status, setStatus] = useState<DocumentStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  useEffect(() => {
    if (!document || status?.status === "processed" || status?.status === "failed") {
      return;
    }

    const token = readAccessToken();
    if (!token) {
      return;
    }

    const timer = window.setInterval(async () => {
      try {
        const nextStatus = await getDocumentStatus(document.id, token);
        setStatus(nextStatus);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Could not refresh processing status");
      }
    }, 2500);

    return () => window.clearInterval(timer);
  }, [document, status?.status]);

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    setDocument(null);
    setError(null);
    setFile(event.target.files?.[0] ?? null);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    const token = readAccessToken();
    if (!token) {
      setError("Log in before uploading documents");
      return;
    }
    if (!file) {
      setError("Choose a PDF, PPTX, or DOCX file");
      return;
    }

    setIsUploading(true);
    try {
      const uploaded = await uploadDocument(file, token);
      setDocument(uploaded);
      setStatus({
        id: uploaded.id,
        status: uploaded.status,
        error_message: uploaded.error_message,
        chunk_count: 0
      });
      setFile(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <form className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm" onSubmit={handleSubmit}>
      <label className="block text-sm font-semibold text-slate-800" htmlFor="study-file">
        Study material
      </label>
      <input
        id="study-file"
        className="mt-3 block w-full rounded-md border border-dashed border-slate-300 bg-slate-50 px-4 py-8 text-sm text-slate-700 file:mr-4 file:rounded-md file:border-0 file:bg-accent file:px-4 file:py-2 file:text-sm file:font-semibold file:text-white"
        type="file"
        accept={ACCEPTED_TYPES}
        onChange={handleFileChange}
      />
      <p className="mt-2 text-sm text-slate-500">PDF, PPTX, or DOCX up to 50MB.</p>

      {error ? <p className="mt-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
      {document ? (
        <p className="mt-4 rounded-md bg-emerald-50 px-3 py-2 text-sm text-emerald-800">
          Uploaded {document.original_filename}. Status: {status?.status ?? document.status}
          {status?.chunk_count ? `, ${status.chunk_count} chunks indexed` : ""}.
        </p>
      ) : null}
      {status?.status === "failed" ? (
        <p className="mt-3 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">
          Processing failed: {status.error_message ?? "Unknown error"}
        </p>
      ) : null}

      <button
        className="mt-5 rounded-md bg-accent px-5 py-2.5 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
        type="submit"
        disabled={isUploading}
      >
        {isUploading ? "Uploading..." : "Upload file"}
      </button>
    </form>
  );
}
