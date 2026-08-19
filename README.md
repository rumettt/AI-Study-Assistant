# AI Study Assistant

Phase 1 establishes the local foundation for the study assistant, and Phase 2 adds the asynchronous document-processing pipeline:

- Next.js 14 frontend with TypeScript and Tailwind
- FastAPI backend with JWT register, login, and refresh endpoints
- PostgreSQL schema for `users`, `documents`, `chunks`, and `sessions`
- S3-compatible file storage through MinIO for local development
- Auth UI and PDF/PPTX/DOCX upload UI
- Celery + Redis background processing for uploaded files
- PDF/PPTX/DOCX parsing, semantic chunking, OpenAI embeddings, and Pinecone indexing
- Hybrid retrieval service using Pinecone vector search + BM25 with Reciprocal Rank Fusion
- GPT-4o powered chat, summaries, quizzes, and flashcards
- Study dashboard, rate limiting, Anki export, and deployment config

## Architecture Decisions

The backend owns authentication, file validation, storage, and document metadata. Files go to object storage immediately, while Postgres stores the stable metadata that later phases will use for ingestion status, chunking, retrieval, and AI features.

The frontend is a thin Next.js App Router client for Phase 1. It stores tokens in `localStorage` for quick local iteration; production hardening should move refresh-token handling to secure HTTP-only cookies.

Docker Compose runs Postgres, MinIO, Redis, FastAPI, and the Celery worker together. The frontend is kept outside Compose for the standard Next.js local workflow.

## Local Development

1. Copy env files:

```bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

2. Start backend dependencies and API:

```bash
docker compose up --build
```

3. Start frontend:

```bash
cd frontend
npm install
npm run dev
```

4. Open:

- Frontend: `http://localhost:3000`
- Backend health: `http://localhost:8000/health`
- MinIO console: `http://localhost:9001`

Document processing requires `OPENAI_API_KEY` and `PINECONE_API_KEY` in `.env`. Uploads are still accepted without those keys, but the worker will mark processing as failed until the keys are configured.

## Phase 1 Checklist

- [x] Initial Next.js 14 project structure with TypeScript and Tailwind
- [x] FastAPI backend folder structure: `app/routers`, `app/services`, `app/models`
- [x] PostgreSQL migration for `users`, `documents`, `chunks`, `sessions`
- [x] JWT register, login, and token refresh endpoints
- [x] File upload endpoint for PDF, PPTX, and DOCX with 50MB max size
- [x] S3-compatible storage service for MinIO/local development
- [x] Docker Compose for Postgres, MinIO, and FastAPI
- [x] Login/signup pages and upload component
- [x] Environment variable examples for root, backend, and frontend

## Phase 2 Checklist

- [x] PDF parsing with PyMuPDF
- [x] PPTX parsing with python-pptx
- [x] DOCX parsing with python-docx
- [x] Paragraph-boundary chunking targeting 400-600 tokens with overlap
- [x] OpenAI `text-embedding-3-small` embedding service
- [x] Pinecone upsert with document/user/page/chunk metadata
- [x] Hybrid retrieval service with dense search, BM25, and RRF fusion
- [x] Celery + Redis worker config for asynchronous upload processing
- [x] Document processing status endpoint
- [x] Frontend upload status polling

## Phase 3 Checklist

- [x] Grounded Q&A endpoint and chat page
- [x] Summary generation endpoint and page
- [x] Quiz generation, attempt scoring, and quiz page
- [x] Flashcard generation, flip UI, and Anki `.apkg` export
- [x] Centralized prompt constants in `backend/app/prompts.py`

## Phase 4 Checklist

- [x] Per-user AI request rate-limit wiring with SlowAPI
- [x] Study dashboard page and dashboard API
- [x] Basic ingestion and retrieval pytest coverage
- [x] RAGAS evaluation harness placeholder with golden dataset sample
- [x] `railway.toml` and `vercel.json` deployment configs
- [x] Production variables documented in `.env.example`

## Verify Before Phase 2

- Create an account from `/signup`
- Log in from `/login`
- Upload a small PDF, PPTX, and DOCX from `/upload`
- Confirm rows are created in `documents`
- Confirm uploaded objects appear in the `study-documents` MinIO bucket
- Configure OpenAI and Pinecone keys, then confirm the worker updates uploaded documents to `processed`
- Confirm rows are created in `chunks`
- Confirm vectors appear in the configured Pinecone index
- Generate a summary, quiz, and flashcard set from a processed document
- Ask a chat question and confirm citations reference uploaded material 
