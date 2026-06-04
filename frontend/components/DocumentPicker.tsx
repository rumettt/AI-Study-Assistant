"use client";

import type { DocumentResponse } from "@/lib/api";

type DocumentPickerProps = {
  documents: DocumentResponse[];
  value: string;
  onChange: (documentId: string) => void;
};

export function DocumentPicker({ documents, value, onChange }: DocumentPickerProps) {
  return (
    <label className="block text-sm font-medium text-slate-800">
      Document
      <select
        className="mt-2 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-accent focus:ring-2 focus:ring-teal-100"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      >
        <option value="">Choose a processed document</option>
        {documents.map((document) => (
          <option disabled={document.status !== "processed"} key={document.id} value={document.id}>
            {document.original_filename} ({document.status})
          </option>
        ))}
      </select>
    </label>
  );
}
