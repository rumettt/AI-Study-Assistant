"use client";

import { FormEvent, useState } from "react";
import { askQuestion, type ChatResponse } from "@/lib/api";
import { readAccessToken } from "@/lib/auth-store";
import { WorkspaceShell } from "@/components/WorkspaceShell";

export default function ChatPage() {
  const [question, setQuestion] = useState("");
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [messages, setMessages] = useState<Array<{ question: string; response: ChatResponse }>>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const token = readAccessToken();
    if (!token) {
      setError("Log in before asking questions");
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const response = await askQuestion(question, token, conversationId);
      setConversationId(response.conversation_id);
      setMessages((current) => [...current, { question, response }]);
      setQuestion("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not answer question");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <WorkspaceShell>
      <h1 className="text-3xl font-semibold text-ink">Grounded chat</h1>
      <form className="mt-6 rounded-lg border border-slate-200 bg-white p-5" onSubmit={handleSubmit}>
        <textarea
          className="min-h-28 w-full rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-accent focus:ring-2 focus:ring-teal-100"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask about your uploaded study material"
          required
        />
        {error ? <p className="mt-3 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
        <button className="mt-4 rounded-md bg-accent px-5 py-2.5 text-sm font-semibold text-white" disabled={isLoading}>
          {isLoading ? "Answering..." : "Ask"}
        </button>
      </form>
      <div className="mt-6 space-y-4">
        {messages.map((message, index) => (
          <article className="rounded-lg border border-slate-200 bg-white p-5" key={`${message.response.conversation_id}-${index}`}>
            <p className="text-sm font-semibold text-slate-800">{message.question}</p>
            <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-700">{message.response.answer}</p>
            <div className="mt-4 flex flex-wrap gap-2">
              {message.response.citations.map((citation) => (
                <span className="rounded-md bg-slate-100 px-2 py-1 text-xs text-slate-600" key={`${citation.document_id}-${citation.chunk_index}`}>
                  {citation.document_name}, page {citation.page_number ?? "n/a"}
                </span>
              ))}
            </div>
          </article>
        ))}
      </div>
    </WorkspaceShell>
  );
}
