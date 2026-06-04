"use client";

import { useEffect, useState } from "react";
import { getDashboard, type DashboardResponse } from "@/lib/api";
import { readAccessToken } from "@/lib/auth-store";
import { WorkspaceShell } from "@/components/WorkspaceShell";

export default function DashboardPage() {
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = readAccessToken();
    if (!token) {
      setError("Log in to view your dashboard");
      return;
    }
    getDashboard(token)
      .then(setDashboard)
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load dashboard"));
  }, []);

  return (
    <WorkspaceShell>
      <h1 className="text-3xl font-semibold text-ink">Study dashboard</h1>
      {error ? <p className="mt-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
      <div className="mt-6 grid gap-4 sm:grid-cols-3">
        <div className="rounded-lg border border-slate-200 bg-white p-5">
          <p className="text-sm text-slate-500">Documents</p>
          <p className="mt-2 text-3xl font-semibold text-ink">{dashboard?.documents.length ?? 0}</p>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-5">
          <p className="text-sm text-slate-500">Quiz attempts</p>
          <p className="mt-2 text-3xl font-semibold text-ink">{dashboard?.quiz_attempts ?? 0}</p>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-5">
          <p className="text-sm text-slate-500">Flashcard sets</p>
          <p className="mt-2 text-3xl font-semibold text-ink">{dashboard?.flashcard_sets ?? 0}</p>
        </div>
      </div>
      <div className="mt-6 rounded-lg border border-slate-200 bg-white">
        <div className="border-b border-slate-200 px-5 py-3 text-sm font-semibold text-slate-800">Recent documents</div>
        <div className="divide-y divide-slate-100">
          {dashboard?.documents.map((document) => (
            <div className="grid gap-2 px-5 py-4 text-sm sm:grid-cols-[1fr_120px_120px]" key={document.id}>
              <span className="font-medium text-ink">{document.original_filename}</span>
              <span className="text-slate-600">{document.status}</span>
              <span className="text-slate-600">{document.chunk_count} chunks</span>
            </div>
          ))}
        </div>
      </div>
    </WorkspaceShell>
  );
}
