"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { login, register } from "@/lib/api";
import { saveAuth } from "@/lib/auth-store";

type AuthFormProps = {
  mode: "login" | "signup";
};

export function AuthForm({ mode }: AuthFormProps) {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const isSignup = mode === "signup";

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const auth = isSignup ? await register(email, password) : await login(email, password);
      saveAuth(auth);
      router.push("/upload");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not complete authentication");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className="w-full max-w-md rounded-lg border border-slate-200 bg-white p-6 shadow-sm" onSubmit={handleSubmit}>
      <h1 className="text-2xl font-semibold text-ink">{isSignup ? "Create account" : "Log in"}</h1>
      <p className="mt-2 text-sm text-slate-600">
        {isSignup ? "Start by creating a secure account." : "Continue to your document workspace."}
      </p>

      <label className="mt-6 block text-sm font-medium text-slate-800" htmlFor="email">
        Email
      </label>
      <input
        id="email"
        className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-accent focus:ring-2 focus:ring-teal-100"
        type="email"
        value={email}
        onChange={(event) => setEmail(event.target.value)}
        required
      />

      <label className="mt-4 block text-sm font-medium text-slate-800" htmlFor="password">
        Password
      </label>
      <input
        id="password"
        className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-accent focus:ring-2 focus:ring-teal-100"
        type="password"
        value={password}
        minLength={isSignup ? 8 : 1}
        onChange={(event) => setPassword(event.target.value)}
        required
      />

      {error ? <p className="mt-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}

      <button
        className="mt-6 w-full rounded-md bg-accent px-4 py-2.5 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
        type="submit"
        disabled={isSubmitting}
      >
        {isSubmitting ? "Working..." : isSignup ? "Sign up" : "Log in"}
      </button>

      <p className="mt-4 text-center text-sm text-slate-600">
        {isSignup ? "Already have an account?" : "Need an account?"}{" "}
        <Link className="font-semibold text-accent" href={isSignup ? "/login" : "/signup"}>
          {isSignup ? "Log in" : "Sign up"}
        </Link>
      </p>
    </form>
  );
}
