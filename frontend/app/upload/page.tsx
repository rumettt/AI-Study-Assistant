import Link from "next/link";
import { FileUpload } from "@/components/FileUpload";

export default function UploadPage() {
  return (
    <main className="min-h-screen bg-paper">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <Link className="text-sm font-semibold text-ink" href="/">
            AI Study Assistant
          </Link>
          <span className="text-sm text-slate-500">Phase 1 workspace</span>
        </div>
      </header>
      <section className="mx-auto max-w-5xl px-6 py-10">
        <div className="mb-6 max-w-2xl">
          <h1 className="text-3xl font-semibold text-ink">Upload study material</h1>
          <p className="mt-2 text-slate-600">
            Files are stored in S3-compatible object storage and registered in Postgres for later ingestion.
          </p>
        </div>
        <FileUpload />
      </section>
    </main>
  );
}
