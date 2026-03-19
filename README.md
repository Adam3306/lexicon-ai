<<<<<<< HEAD
# lexicon-ai

Production-shaped MVP for a “knowledge copilot” (RAG) built with:
- Django + Django REST Framework
- PostgreSQL + pgvector
- OpenAI embeddings + grounded chat
- Next.js (React + TypeScript)

## Architecture

```mermaid
flowchart LR
  U[User] --> UI[Next.js UI<br/>Upload PDF → Select docs → Search / Answer]

  subgraph API[Django REST API]
    A1[POST /api/documents/ingest]
    A2[POST /api/embeddings/embed]
    A3[POST /api/search]
    A4[POST /api/answer]
    EH[OpenAI error mapping<br/>→ clean JSON 4xx/429]
  end

  subgraph Services[Services]
    EX[extract_text_from_pdf_bytes<br/> (pypdf)]
    CH[chunk_text<br/> (paragraph-based chunker)]
    EM[embed_texts<br/> (OpenAI embeddings)]
    RET[Vector retrieval<br/> (pgvector cosine distance)]
    GEN[generate_grounded_answer<br/> (LLM w/ context)]
  end

  subgraph DB[(Postgres + pgvector)]
    D[Document]
    C[DocumentChunk]
    V[ChunkEmbedding<br/> VectorField]
  end

  UI --> A1
  A1 --> EX --> CH --> DB
  DB --> C --> V

  UI --> A2
  A2 --> EM --> DB

  UI --> A3
  A3 --> EM
  A3 --> RET --> UI

  UI --> A4
  A4 --> EM
  A4 --> RET --> GEN --> UI

  A1 -.-> EH
  A2 -.-> EH
  A3 -.-> EH
  A4 -.-> EH
```

### Document scoping (important)

Search and Answer accept `document_id` (single) or `document_ids` (multi) to restrict retrieval to the selected documents.

## Quick start (local)

### Backend

1. Install dependencies:
   - `cd backend`
   - `python3 -m venv .venv && source .venv/bin/activate`
   - `pip install -r requirements.txt`

2. Configure environment:
   - `cp .env.example .env`

3. Start Postgres + pgvector:
   - `docker compose -f docker-compose.yml up -d`

4. Apply migrations + start the server:
   - `python src/manage.py migrate`
   - `python src/manage.py runserver 8000`

Notes:
- CORS for the frontend is handled by `CORS_ALLOWED_ORIGINS` (defaults to `http://localhost:3000`).
- Uploaded PDF source files are stored under `backend/src/media/`.

### Frontend

1. Install dependencies:
   - `cd frontend`
   - `npm install`

2. Configure environment:
   - `cp .env.local.example .env.local`

3. Run:
   - `npm run dev`

## How to use the UI

1. `Ingest PDF` (upload a PDF)
2. `Embed` (generates embeddings for the new chunks)
3. `Search` (semantic search via pgvector)
4. `Answer (RAG)` (LLM answer grounded in retrieved chunks, with citations)

=======
# Lexicon AI – Knowledge Copilot

Lexicon AI is an AI-powered knowledge copilot that transforms unstructured documents into actionable insights using Retrieval-Augmented Generation (RAG), semantic search, and LLM-driven analysis.

This project demonstrates a production-oriented approach to building AI systems with Django, PostgreSQL (pgvector), React, and modern LLM tooling.

---

## ✨ Features (MVP)

- 📄 Document ingestion (PDF)
- 🔍 Semantic search with vector embeddings (pgvector)
- 💬 Context-aware chat grounded in document data (RAG)
- 📚 Source attribution (answers linked to document chunks)
- 🧠 Structured outputs (e.g. extracting risks, key points, deadlines)

---

## 🏗️ Tech Stack

### Backend
- Django + Django REST Framework
- PostgreSQL + pgvector
- OpenAI API (embeddings + LLM)

### Frontend (planned)
- Next.js (React + TypeScript)
- Tailwind CSS

### Infrastructure (planned)
- Docker / Docker Compose
- Celery (async processing)

---

## 🧠 Architecture Overview
>>>>>>> 773e416f207ec9b65242a630ba433a86128b3de1
