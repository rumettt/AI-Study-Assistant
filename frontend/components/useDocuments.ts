"use client";

import { useEffect, useState } from "react";
import { listDocuments, type DocumentResponse } from "@/lib/api";
import { readAccessToken } from "@/lib/auth-store";

export function useDocuments() {
  const [documents, setDocuments] = useState<DocumentResponse[]>([]);
  const [token, setToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const accessToken = readAccessToken();
    setToken(accessToken);
    if (!accessToken) {
      setError("Log in to use this workspace");
      setIsLoading(false);
      return;
    }
    listDocuments(accessToken)
      .then(setDocuments)
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load documents"))
      .finally(() => setIsLoading(false));
  }, []);

  return { documents, token, error, isLoading };
}
