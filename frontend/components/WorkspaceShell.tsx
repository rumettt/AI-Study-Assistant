import Link from "next/link";
import type { ReactNode } from "react";

const links = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/upload", label: "Upload" },
  { href: "/chat", label: "Chat" },
  { href: "/summary", label: "Summary" },
  { href: "/quiz", label: "Quiz" },
  { href: "/flashcards", label: "Flashcards" }
];

export function WorkspaceShell({ children }: { children: ReactNode }) {
  return (
    <main className="min-h-screen bg-paper">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-col gap-3 px-6 py-4 sm:flex-row sm:items-center sm:justify-between">
          <Link className="text-sm font-semibold text-ink" href="/">
            AI Study Assistant
          </Link>
          <nav className="flex flex-wrap gap-2 text-sm">
            {links.map((link) => (
              <Link className="rounded-md px-3 py-1.5 text-slate-700 hover:bg-slate-100" href={link.href} key={link.href}>
                {link.label}
              </Link>
            ))}
          </nav>
        </div>
      </header>
      <section className="mx-auto max-w-6xl px-6 py-8">{children}</section>
    </main>
  );
}
