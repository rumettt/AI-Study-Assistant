export type AuthUser = {
  id: string;
  email: string;
};

export type AuthResponse = {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
  user: AuthUser;
};

export type DocumentResponse = {
  id: string;
  original_filename: string;
  content_type: string;
  size_bytes: number;
  status: string;
  error_message?: string | null;
  created_at: string;
};

export type DocumentStatusResponse = {
  id: string;
  status: string;
  error_message?: string | null;
  chunk_count: number;
  processed_at?: string | null;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function parseResponse<T>(response: Response): Promise<T> {
  if (response.ok) {
    return response.json() as Promise<T>;
  }

  let detail = "Request failed";
  try {
    const body = (await response.json()) as { detail?: string };
    detail = body.detail ?? detail;
  } catch {
    detail = response.statusText || detail;
  }
  throw new Error(detail);
}

export async function register(email: string, password: string): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });
  return parseResponse<AuthResponse>(response);
}

export async function login(email: string, password: string): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });
  return parseResponse<AuthResponse>(response);
}

export async function uploadDocument(file: File, accessToken: string): Promise<DocumentResponse> {
  const data = new FormData();
  data.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/uploads`, {
    method: "POST",
    headers: { Authorization: `Bearer ${accessToken}` },
    body: data
  });
  return parseResponse<DocumentResponse>(response);
}

export async function getDocumentStatus(documentId: string, accessToken: string): Promise<DocumentStatusResponse> {
  const response = await fetch(`${API_BASE_URL}/api/documents/${documentId}/status`, {
    headers: { Authorization: `Bearer ${accessToken}` }
  });
  return parseResponse<DocumentStatusResponse>(response);
}
