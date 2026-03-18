from __future__ import annotations

from django.core.files.base import ContentFile
from django.db import transaction
from pgvector.django import CosineDistance
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ChunkEmbedding, Document, DocumentChunk
from .serializers import (
    AnswerRequestSerializer,
    DocumentEmbedRequestSerializer,
    DocumentIngestSerializer,
    DocumentListItemSerializer,
    SearchRequestSerializer,
)
from .services.chunking import chunk_text
from .services.embeddings import embed_texts, get_embedding_config
from .services.extraction import extract_text_from_pdf_bytes
from .services.generation import generate_grounded_answer, get_chat_config
from .services.openai_errors import is_openai_exception, openai_exception_response


class DocumentListView(APIView):
    """
    List uploaded documents for UI selection.
    """

    def get(self, request):
        qs = Document.objects.all().order_by("-created_at")
        items = [
            {"id": d.id, "title": d.title, "created_at": d.created_at}
            for d in qs
        ]
        ser = DocumentListItemSerializer(items, many=True)
        return Response({"results": ser.data})


class DocumentIngestView(APIView):
    """
    MVP ingestion:
    - accept multipart file upload (PDF)
    - extract text
    - chunk and store chunks
    """

    def post(self, request):
        serializer = DocumentIngestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded = serializer.validated_data["file"]
        title = serializer.validated_data.get("title") or getattr(uploaded, "name", "Untitled")

        # NOTE: read entire file into memory for MVP; later we can stream to temp file.
        pdf_bytes = uploaded.read()
        text = extract_text_from_pdf_bytes(pdf_bytes)
        if not text:
            return Response(
                {"detail": "No extractable text found in PDF."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # uploaded.read() advances the file pointer; persist from bytes to avoid empty files.
        content = ContentFile(pdf_bytes, name=getattr(uploaded, "name", "document.pdf"))
        doc = Document.objects.create(title=title, source_file=content)
        chunks = chunk_text(text)
        DocumentChunk.objects.bulk_create(
            [
                DocumentChunk(document=doc, chunk_index=i, text=chunk)
                for i, chunk in enumerate(chunks)
            ]
        )

        return Response(
            {"document_id": str(doc.id), "chunks_created": len(chunks)},
            status=status.HTTP_201_CREATED,
        )


class EmbedChunksView(APIView):
    """
    Embed chunks that don't have embeddings yet.
    """

    def post(self, request):
        serializer = DocumentEmbedRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        limit = serializer.validated_data["limit"]
        document_id = serializer.validated_data.get("document_id")
        document_ids = serializer.validated_data.get("document_ids")

        qs = DocumentChunk.objects.filter(embedding__isnull=True)
        if document_ids:
            qs = qs.filter(document_id__in=document_ids)
        elif document_id:
            qs = qs.filter(document_id=document_id)
        chunks = list(qs.order_by("created_at")[:limit])
        if not chunks:
            return Response({"embedded": 0})

        cfg = get_embedding_config()
        try:
            vectors = embed_texts([c.text for c in chunks], model=cfg.model)
        except Exception as exc:
            if is_openai_exception(exc):
                return openai_exception_response(exc)
            raise

        with transaction.atomic():
            created = 0
            for chunk, vec in zip(chunks, vectors, strict=True):
                obj, was_created = ChunkEmbedding.objects.get_or_create(
                    chunk=chunk,
                    defaults={"embedding_model": cfg.model, "embedding": vec},
                )
                if was_created:
                    created += 1
                elif obj.embedding_model != cfg.model:
                    # keep MVP simple: don't overwrite; allow later re-embed endpoint
                    pass

        return Response({"embedded": created, "model": cfg.model})


class SearchView(APIView):
    """
    Embed the query, then vector-search chunk embeddings.
    """

    def post(self, request):
        serializer = SearchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        query = serializer.validated_data["query"]
        top_k = serializer.validated_data["top_k"]
        document_id = serializer.validated_data.get("document_id")
        document_ids = serializer.validated_data.get("document_ids")

        cfg = get_embedding_config()
        try:
            qvec = embed_texts([query], model=cfg.model)[0]
        except Exception as exc:
            if is_openai_exception(exc):
                return openai_exception_response(exc)
            raise

        embeddings_qs = ChunkEmbedding.objects.select_related("chunk", "chunk__document")
        if document_ids:
            embeddings_qs = embeddings_qs.filter(chunk__document_id__in=document_ids)
        elif document_id:
            embeddings_qs = embeddings_qs.filter(chunk__document_id=document_id)

        results = (
            embeddings_qs.annotate(distance=CosineDistance("embedding", qvec))
            # Deterministic ordering for tied distances.
            .order_by("distance", "chunk__chunk_index", "chunk_id")[:top_k]
        )

        payload = []
        for r in results:
            payload.append(
                {
                    "document_id": str(r.chunk.document_id),
                    "chunk_id": str(r.chunk_id),
                    "chunk_index": r.chunk.chunk_index,
                    "distance": float(r.distance),
                    "text": r.chunk.text,
                }
            )

        return Response({"model": cfg.model, "results": payload})


class AnswerView(APIView):
    """
    RAG: retrieve relevant chunks and generate a grounded answer.
    """

    def post(self, request):
        serializer = AnswerRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.validated_data["question"]
        top_k = serializer.validated_data["top_k"]
        document_id = serializer.validated_data.get("document_id")
        document_ids = serializer.validated_data.get("document_ids")
        include_context = serializer.validated_data["include_context"]

        emb_cfg = get_embedding_config()
        try:
            qvec = embed_texts([question], model=emb_cfg.model)[0]
        except Exception as exc:
            if is_openai_exception(exc):
                return openai_exception_response(exc)
            raise

        embeddings_qs = ChunkEmbedding.objects.select_related("chunk", "chunk__document")
        if document_ids:
            embeddings_qs = embeddings_qs.filter(chunk__document_id__in=document_ids)
        elif document_id:
            embeddings_qs = embeddings_qs.filter(chunk__document_id=document_id)

        hits = (
            embeddings_qs.annotate(distance=CosineDistance("embedding", qvec))
            .order_by("distance", "chunk__chunk_index", "chunk_id")[:top_k]
        )

        citations = []
        context_blocks: list[str] = []
        for h in hits:
            citations.append(
                {
                    "document_id": str(h.chunk.document_id),
                    "chunk_id": str(h.chunk_id),
                    "chunk_index": h.chunk.chunk_index,
                    "distance": float(h.distance),
                }
            )
            context_blocks.append(f"[chunk {h.chunk.chunk_index}]\n{h.chunk.text}")

        chat_cfg = get_chat_config()
        try:
            answer = generate_grounded_answer(
                question=question,
                context_blocks=context_blocks,
                model=chat_cfg.model,
            )
        except Exception as exc:
            if is_openai_exception(exc):
                return openai_exception_response(exc)
            raise

        resp = {"model": chat_cfg.model, "answer": answer, "citations": citations}
        if include_context:
            resp["context"] = context_blocks
        return Response(resp)
