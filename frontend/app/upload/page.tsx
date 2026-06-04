import { FileUpload } from "@/components/FileUpload";
import { WorkspaceShell } from "@/components/WorkspaceShell";

export default function UploadPage() {
  return (
    <WorkspaceShell>
        <div className="mb-6 max-w-2xl">
          <h1 className="text-3xl font-semibold text-ink">Upload study material</h1>
          <p className="mt-2 text-slate-600">
            Files are stored in S3-compatible object storage and registered in Postgres for later ingestion.
          </p>
        </div>
        <FileUpload />
    </WorkspaceShell>
  );
}
