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

export type Citation = {
  document_id: string;
  document_name: string;
  page_number?: number | null;
  chunk_index: number;
};

export type ChatResponse = {
  conversation_id: string;
  answer: string;
  citations: Citation[];
};

export type SummaryResponse = {
  id: string;
  document_id: string;
  abstract: string;
  key_concepts: string[];
  updated_at: string;
};

export type QuizQuestion = {
  type: "mcq" | "short_answer";
  question: string;
  options: string[];
  correct: string;
  explanation: string;
};

export type QuizResponse = {
  id: string;
  document_id: string;
  questions: QuizQuestion[];
  created_at: string;
};

export type Flashcard = {
  front: string;
  back: string;
};

export type FlashcardSetResponse = {
  id: string;
  document_id: string;
  cards: Flashcard[];
  created_at: string;
};

export type DashboardResponse = {
  documents: Array<{
    id: string;
    original_filename: string;
    status: string;
    created_at: string;
    chunk_count: number;
  }>;
  quiz_attempts: number;
  average_quiz_score?: number | null;
  flashcard_sets: number;
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

export async function listDocuments(accessToken: string): Promise<DocumentResponse[]> {
  const response = await fetch(`${API_BASE_URL}/api/documents`, {
    headers: { Authorization: `Bearer ${accessToken}` }
  });
  return parseResponse<DocumentResponse[]>(response);
}

export async function getDocumentStatus(documentId: string, accessToken: string): Promise<DocumentStatusResponse> {
  const response = await fetch(`${API_BASE_URL}/api/documents/${documentId}/status`, {
    headers: { Authorization: `Bearer ${accessToken}` }
  });
  return parseResponse<DocumentStatusResponse>(response);
}

export async function getDashboard(accessToken: string): Promise<DashboardResponse> {
  const response = await fetch(`${API_BASE_URL}/api/documents/dashboard/overview`, {
    headers: { Authorization: `Bearer ${accessToken}` }
  });
  return parseResponse<DashboardResponse>(response);
}

export async function askQuestion(question: string, accessToken: string, conversationId?: string): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${accessToken}` },
    body: JSON.stringify({ question, conversation_id: conversationId })
  });
  return parseResponse<ChatResponse>(response);
}

export async function generateSummary(documentId: string, accessToken: string): Promise<SummaryResponse> {
  const response = await fetch(`${API_BASE_URL}/api/summaries/${documentId}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${accessToken}` }
  });
  return parseResponse<SummaryResponse>(response);
}

export async function generateQuiz(documentId: string, accessToken: string): Promise<QuizResponse> {
  const response = await fetch(`${API_BASE_URL}/api/quizzes/${documentId}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${accessToken}` }
  });
  return parseResponse<QuizResponse>(response);
}

export async function submitQuiz(quizId: string, answers: string[], accessToken: string): Promise<{ score: number; total: number }> {
  const response = await fetch(`${API_BASE_URL}/api/quizzes/${quizId}/attempts`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${accessToken}` },
    body: JSON.stringify({ answers })
  });
  return parseResponse<{ score: number; total: number }>(response);
}

export async function generateFlashcards(documentId: string, accessToken: string): Promise<FlashcardSetResponse> {
  const response = await fetch(`${API_BASE_URL}/api/flashcards/${documentId}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${accessToken}` }
  });
  return parseResponse<FlashcardSetResponse>(response);
}

export async function exportFlashcards(setId: string, accessToken: string): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/api/flashcards/${setId}/export`, {
    headers: { Authorization: `Bearer ${accessToken}` }
  });
  if (!response.ok) {
    await parseResponse<never>(response);
  }
  return response.blob();
}
