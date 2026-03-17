from django.db import IntegrityError, connection
from django.test import TestCase

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
