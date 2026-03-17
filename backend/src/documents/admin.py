from django.contrib import admin

from .models import ChunkEmbedding, Document, DocumentChunk


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_at")
    search_fields = ("title",)


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ("id", "document_id", "chunk_index", "created_at")
    list_filter = ("created_at",)
    search_fields = ("text",)
    raw_id_fields = ("document",)


@admin.register(ChunkEmbedding)
class ChunkEmbeddingAdmin(admin.ModelAdmin):
    list_display = ("id", "chunk_id", "embedding_model", "created_at")
    list_filter = ("embedding_model", "created_at")
    raw_id_fields = ("chunk",)
