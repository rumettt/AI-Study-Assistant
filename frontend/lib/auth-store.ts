"use client";

import type { AuthResponse } from "@/lib/api";

const STORAGE_KEY = "ai-study-auth";

export function saveAuth(auth: AuthResponse): void {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(auth));
}

export function readAccessToken(): string | null {
  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return null;
  }
  try {
    const parsed = JSON.parse(raw) as AuthResponse;
    return parsed.access_token;
  } catch {
    window.localStorage.removeItem(STORAGE_KEY);
    return null;
  }
}

export function clearAuth(): void {
  window.localStorage.removeItem(STORAGE_KEY);
}
