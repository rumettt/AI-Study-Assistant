import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-paper">
      <section className="mx-auto flex min-h-screen max-w-5xl flex-col justify-center px-6 py-12">
        <div className="max-w-2xl">
          <p className="text-sm font-semibold uppercase tracking-wide text-accent">AI Study Assistant</p>
          <h1 className="mt-4 text-4xl font-semibold leading-tight text-ink sm:text-5xl">
            Convert class materials into study sessions.
          </h1>
          <p className="mt-5 text-lg leading-8 text-slate-700">
            Upload PDFs, slides, and notes. Phase 1 establishes accounts, secure file intake, and local storage.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link className="rounded-md bg-accent px-5 py-3 text-sm font-semibold text-white" href="/signup">
              Create account
            </Link>
            <Link className="rounded-md border border-slate-300 px-5 py-3 text-sm font-semibold text-ink" href="/login">
              Log in
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
