import uuid

from django.db import models
from pgvector.django import VectorField


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    source_file = models.FileField(upload_to="documents/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title


class DocumentChunk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="chunks")
    chunk_index = models.PositiveIntegerField()
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["document", "chunk_index"], name="uniq_chunk_per_doc"),
        ]
        indexes = [
            models.Index(fields=["document", "chunk_index"]),
        ]

    def __str__(self) -> str:
        return f"{self.document_id}:{self.chunk_index}"


class ChunkEmbedding(models.Model):
    """
    Keeps embeddings separate from chunk text so we can re-embed with different models later.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chunk = models.OneToOneField(DocumentChunk, on_delete=models.CASCADE, related_name="embedding")
    embedding_model = models.CharField(max_length=128, default="text-embedding-3-small")
    embedding = VectorField(dimensions=1536)
    created_at = models.DateTimeField(auto_now_add=True)
