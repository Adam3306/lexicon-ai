from __future__ import annotations

from rest_framework import serializers


class DocumentIngestSerializer(serializers.Serializer):
    file = serializers.FileField()
    title = serializers.CharField(required=False, allow_blank=True, max_length=255)

