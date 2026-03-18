from django.urls import path

from .views import AnswerView, DocumentIngestView, EmbedChunksView, SearchView


urlpatterns = [
    path("api/documents/ingest", DocumentIngestView.as_view(), name="documents-ingest"),
    path("api/embeddings/embed", EmbedChunksView.as_view(), name="embeddings-embed"),
    path("api/search", SearchView.as_view(), name="search"),
    path("api/answer", AnswerView.as_view(), name="answer"),
]

