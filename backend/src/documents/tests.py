from unittest.mock import patch

from django.db import IntegrityError, connection
from django.core.files.base import ContentFile
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from .models import ChunkEmbedding, Document, DocumentChunk


class DocumentsModelsTest(TestCase):
    def test_document_str(self):
        doc = Document.objects.create(title="My Doc")
        self.assertEqual(str(doc), "My Doc")

    def test_chunk_unique_per_document(self):
        doc = Document.objects.create(title="My Doc")
        DocumentChunk.objects.create(document=doc, chunk_index=0, text="a")

        with self.assertRaises(IntegrityError):
            DocumentChunk.objects.create(document=doc, chunk_index=0, text="b")

    def test_embedding_is_one_to_one_with_chunk(self):
        doc = Document.objects.create(title="My Doc")
        chunk = DocumentChunk.objects.create(document=doc, chunk_index=0, text="hello")

        ChunkEmbedding.objects.create(
            chunk=chunk,
            embedding_model="text-embedding-3-small",
            embedding=[0.0] * 1536,
        )

        with self.assertRaises(IntegrityError):
            ChunkEmbedding.objects.create(
                chunk=chunk,
                embedding_model="text-embedding-3-small",
                embedding=[0.0] * 1536,
            )

    def test_vector_extension_is_available(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
            row = cursor.fetchone()
        self.assertIsNotNone(row)


class DocumentsIngestionTest(TestCase):
    def test_chunking_produces_chunks(self):
        from .services.chunking import chunk_text

        chunks = chunk_text("Para1.\n\nPara2.\n\nPara3.", target_chars=10, overlap_chars=0)
        self.assertGreaterEqual(len(chunks), 2)

    def test_ingest_persists_non_empty_source_file(self):
        client = APIClient()
        pdf_bytes = b"%PDF-1.4\n%fake\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF\n"
        uploaded = SimpleUploadedFile("test.pdf", pdf_bytes, content_type="application/pdf")

        from .models import Document  # import here to avoid patch confusion

        def _create_doc_asserting_file(*, title, source_file):
            self.assertIsInstance(source_file, ContentFile)
            self.assertEqual(source_file.size, len(pdf_bytes))
            self.assertGreater(source_file.size, 0)
            doc = Document(title=title)
            doc.save()
            return doc

        with (
            patch("documents.views.extract_text_from_pdf_bytes", return_value="hello world\n\nsecond para"),
            patch("documents.views.Document.objects.create", side_effect=_create_doc_asserting_file),
        ):
            resp = client.post(
                reverse("documents-ingest"),
                data={"file": uploaded, "title": "T"},
                format="multipart",
            )

        self.assertEqual(resp.status_code, 201)
        payload = resp.json()
        self.assertGreaterEqual(payload["chunks_created"], 1)

    def test_embed_scopes_to_document_ids(self):
        client = APIClient()
        doc1 = Document.objects.create(title="D1")
        doc2 = Document.objects.create(title="D2")
        c1 = DocumentChunk.objects.create(document=doc1, chunk_index=0, text="one")
        c2 = DocumentChunk.objects.create(document=doc2, chunk_index=0, text="two")

        vec = [1.0] + [0.0] * 1535

        with (
            patch("documents.views.embed_texts", return_value=[vec]),
        ):
            resp = client.post(
                reverse("embeddings-embed"),
                data={"document_ids": [str(doc1.id)], "limit": 10},
                format="json",
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(ChunkEmbedding.objects.filter(chunk=c1).count(), 1)
        self.assertEqual(ChunkEmbedding.objects.filter(chunk=c2).count(), 0)


class SearchTest(TestCase):
    def test_search_returns_matches(self):
        client = APIClient()
        doc = Document.objects.create(title="D")
        c0 = DocumentChunk.objects.create(document=doc, chunk_index=0, text="hello wise bank")
        c1 = DocumentChunk.objects.create(document=doc, chunk_index=1, text="something else")

        # Precreate embeddings and fake the OpenAI query embedding.
        ChunkEmbedding.objects.create(chunk=c0, embedding_model="text-embedding-3-small", embedding=[1.0] + [0.0] * 1535)
        ChunkEmbedding.objects.create(chunk=c1, embedding_model="text-embedding-3-small", embedding=[0.5] + [0.0] * 1535)

        with patch("documents.views.embed_texts", return_value=[[1.0] + [0.0] * 1535]):
            resp = client.post(reverse("search"), data={"query": "wise"}, format="json")

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertGreaterEqual(len(body["results"]), 1)
        self.assertEqual(body["results"][0]["chunk_id"], str(c0.id))

    def test_search_returns_clean_openai_rate_limit_error(self):
        client = APIClient()

        class FakeRateLimitError(Exception):
            __module__ = "openai"

        with patch("documents.views.embed_texts", side_effect=FakeRateLimitError("quota exceeded")):
            resp = client.post(reverse("search"), data={"query": "x"}, format="json")

        self.assertEqual(resp.status_code, 429)
        body = resp.json()
        self.assertEqual(body["error"]["type"], "openai_error")
        self.assertEqual(body["error"]["code"], "FakeRateLimitError")


class AnswerTest(TestCase):
    def test_answer_returns_answer_and_citations(self):
        client = APIClient()
        doc = Document.objects.create(title="D")
        c0 = DocumentChunk.objects.create(document=doc, chunk_index=0, text="Wise supports downloading an account details document.")
        ChunkEmbedding.objects.create(chunk=c0, embedding_model="text-embedding-3-small", embedding=[1.0] + [0.0] * 1535)

        with (
            patch("documents.views.embed_texts", return_value=[[1.0] + [0.0] * 1535]),
            patch("documents.views.generate_grounded_answer", return_value="You can download an account details document from Wise."),
        ):
            resp = client.post(
                reverse("answer"),
                data={"question": "How do I get account details proof?", "top_k": 1, "document_id": str(doc.id)},
                format="json",
            )

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("answer", body)
        self.assertIn("citations", body)
        self.assertEqual(len(body["citations"]), 1)
        self.assertEqual(body["citations"][0]["chunk_id"], str(c0.id))

    def test_answer_returns_clean_openai_auth_error(self):
        client = APIClient()

        doc = Document.objects.create(title="D")
        c0 = DocumentChunk.objects.create(document=doc, chunk_index=0, text="hello")
        ChunkEmbedding.objects.create(chunk=c0, embedding_model="text-embedding-3-small", embedding=[1.0] + [0.0] * 1535)

        class FakeAuthenticationError(Exception):
            __module__ = "openai"

        with (
            patch("documents.views.embed_texts", return_value=[[1.0] + [0.0] * 1535]),
            patch("documents.views.generate_grounded_answer", side_effect=FakeAuthenticationError("invalid api key")),
        ):
            resp = client.post(reverse("answer"), data={"question": "q", "top_k": 1, "document_id": str(doc.id)}, format="json")

        self.assertEqual(resp.status_code, 401)
        body = resp.json()
        self.assertEqual(body["error"]["type"], "openai_error")
        self.assertEqual(body["error"]["code"], "FakeAuthenticationError")
