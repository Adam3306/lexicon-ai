from __future__ import annotations

from django.core.files.base import ContentFile
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Document, DocumentChunk
from .serializers import DocumentIngestSerializer
from .services.chunking import chunk_text
from .services.extraction import extract_text_from_pdf_bytes


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
