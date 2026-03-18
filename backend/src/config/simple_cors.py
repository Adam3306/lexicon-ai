from __future__ import annotations

import os
from typing import Iterable

from django.http import HttpRequest, HttpResponse


def _split_origins(value: str) -> list[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


class SimpleCORSMiddleware:
    """
    Tiny CORS middleware for local dev (no extra dependency).

    Adds `Access-Control-Allow-*` headers when the request `Origin` is allowed.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        allowed = os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:3000")
        self.allowed_origins = set(_split_origins(allowed))

    def __call__(self, request: HttpRequest):
        origin = request.headers.get("Origin")
        is_allowed = bool(origin) and origin in self.allowed_origins

        # Handle CORS preflight.
        if request.method == "OPTIONS" and is_allowed:
            resp = HttpResponse(status=204)
            self._apply_headers(resp, origin)
            return resp

        resp = self.get_response(request)
        if is_allowed:
            self._apply_headers(resp, origin)
        return resp

    def _apply_headers(self, resp: HttpResponse, origin: str) -> None:
        resp["Access-Control-Allow-Origin"] = origin
        resp["Access-Control-Allow-Credentials"] = "true"
        resp["Vary"] = "Origin"
        resp["Access-Control-Allow-Methods"] = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
        resp["Access-Control-Allow-Headers"] = "Content-Type,Authorization"

