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
This repository implements a production-shaped Retrieval-Augmented Generation (RAG) system for turning uploaded PDFs into a searchable knowledge base and answering questions grounded in that content.

---

### High-level data flow
1. **Ingest PDF**
   - The frontend uploads a PDF.
   - The backend extracts text from the PDF.
   - The extracted text is split into semantically useful chunks.
   - The system persists the `Document` and its `DocumentChunk`s.

2. **Embed chunks**
   - The frontend requests embeddings for chunks that do not have vectors yet.
   - The backend calls OpenAI embeddings for each chunk.
   - Vectors are stored in PostgreSQL using `pgvector` (`ChunkEmbedding`).

3. **Semantic retrieval (Search)**
   - For a query, the backend embeds the query into the same vector space.
   - PostgreSQL performs a cosine-distance similarity search over stored chunk embeddings.
   - The API returns the top K matching chunks (including chunk text + metadata).

4. **Grounded answer generation (Answer/RAG)**
   - The backend collects the retrieved chunks as context blocks.
   - The backend calls the OpenAI chat model with a strict grounding instruction:
     the answer must use ONLY the provided context.
   - The API returns:
     - the generated answer
     - structured citations pointing back to the exact retrieved chunks
     - (optional) the raw context blocks for debugging/inspection

---

### Document scoping (multi-document workspace)
Most operations support restricting the retrieval scope to user-selected documents:
- `document_id` for a single document
- `document_ids` for multiple documents

If neither is provided, the backend searches/answers across all ingested documents. This enables the UI “library + workspace” flow without duplicating ingestion logic.

---

### Components (by backend responsibility)
1. **Ingestion & chunking**
   - `extract_text_from_pdf_bytes` (PDF -> raw text)
   - `chunk_text` (raw text -> list of chunk strings)

2. **Embeddings**
   - `embed_texts` (list of chunk strings -> list of embedding vectors)
   - Stored as fixed-dimension `VectorField` entries in `ChunkEmbedding`

3. **Retrieval**
   - Query embedding is computed the same way as chunk embeddings.
   - Uses `CosineDistance` annotation and deterministic ordering for stable top-K results.

4. **Generation**
   - `generate_grounded_answer` builds:
     - a system prompt enforcing grounding rules
     - a user message containing the question + verbatim context blocks

5. **Error handling**
   - OpenAI SDK exceptions are caught and mapped to clean JSON API responses (no Django 500 debug pages).
   - The mapping translates common OpenAI error types (auth, rate limits, bad requests) into appropriate HTTP status codes.

---

### Data model (database schema)
The RAG knowledge base is stored in the `documents` Django app:
1. `Document`
   - the uploaded PDF (UUID primary key)
   - a human-readable title
   - the stored PDF file (for traceability)

2. `DocumentChunk`
   - one row per chunk extracted from a `Document`
   - stable `chunk_index` so retrieval and citations can refer to chunk positions

3. `ChunkEmbedding`
   - one-to-one with `DocumentChunk`
   - stores `embedding_model` and the vector itself (`pgvector.VectorField`)

---

### API endpoints (what the frontend calls)
All endpoints are hosted by Django REST Framework:
- `GET  /api/documents`
  - returns the list of uploaded documents for selection
- `POST /api/documents/ingest`
  - uploads a PDF and creates `Document` + `DocumentChunk`s
- `POST /api/embeddings/embed`
  - embeds chunks without vectors yet
  - optionally scoped to `document_id` or `document_ids`
- `POST /api/search`
  - embeds the query and retrieves top matching chunks
  - optionally scoped to `document_id` or `document_ids`
- `POST /api/answer`
  - performs retrieval + grounded answer generation
  - optionally scoped to `document_id` or `document_ids`
  - can include context blocks when `include_context=true`

---

### Why this structure is MVP-friendly
- Ingestion, embedding, retrieval, and generation are separated into clear steps.
- Embeddings are stored separately from chunk text so re-embedding later is possible.
- Scoping is implemented consistently at the API layer, matching the UI’s document selection model.
- Error handling is centralized for OpenAI failures, keeping the user experience predictable.

