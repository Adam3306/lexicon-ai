from django.urls import path

from .views import DocumentIngestView


urlpatterns = [
    path("api/documents/ingest", DocumentIngestView.as_view(), name="documents-ingest"),
]

