from __future__ import annotations

from django.http import JsonResponse


def healthz(_request) -> JsonResponse:
    # Minimal readiness check for local dev / simple uptime monitors.
    return JsonResponse({"status": "ok"})

