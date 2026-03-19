from __future__ import annotations

from rest_framework import serializers


class DocumentIngestSerializer(serializers.Serializer):
    file = serializers.FileField()
    title = serializers.CharField(required=False, allow_blank=True, max_length=255)


class DocumentEmbedRequestSerializer(serializers.Serializer):
    document_id = serializers.UUIDField(required=False)
    document_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        allow_empty=False,
    )
    limit = serializers.IntegerField(required=False, min_value=1, max_value=500, default=200)


class DocumentListItemSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField()
    created_at = serializers.DateTimeField()


class SearchRequestSerializer(serializers.Serializer):
    query = serializers.CharField()
    top_k = serializers.IntegerField(required=False, min_value=1, max_value=20, default=5)
    document_id = serializers.UUIDField(required=False)
    document_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        allow_empty=False,
    )


class AnswerRequestSerializer(serializers.Serializer):
    question = serializers.CharField()
    top_k = serializers.IntegerField(required=False, min_value=1, max_value=20, default=5)
    document_id = serializers.UUIDField(required=False)
    document_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        allow_empty=False,
    )
    include_context = serializers.BooleanField(required=False, default=True)


