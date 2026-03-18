from __future__ import annotations

from rest_framework import serializers


class DocumentIngestSerializer(serializers.Serializer):
    file = serializers.FileField()
    title = serializers.CharField(required=False, allow_blank=True, max_length=255)


class DocumentEmbedRequestSerializer(serializers.Serializer):
    document_id = serializers.UUIDField(required=False)
    limit = serializers.IntegerField(required=False, min_value=1, max_value=500, default=200)


class SearchRequestSerializer(serializers.Serializer):
    query = serializers.CharField()
    top_k = serializers.IntegerField(required=False, min_value=1, max_value=20, default=5)
    document_id = serializers.UUIDField(required=False)


class AnswerRequestSerializer(serializers.Serializer):
    question = serializers.CharField()
    top_k = serializers.IntegerField(required=False, min_value=1, max_value=20, default=5)
    document_id = serializers.UUIDField(required=False)
    include_context = serializers.BooleanField(required=False, default=True)


