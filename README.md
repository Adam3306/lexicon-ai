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