from __future__ import annotations

from dataclasses import dataclass

from rest_framework import status
from rest_framework.response import Response


@dataclass(frozen=True)
class OpenAIErrorPayload:
    http_status: int
    code: str
    message: str


_STATUS_BY_ERROR_NAME: dict[str, int] = {
    "AuthenticationError": status.HTTP_401_UNAUTHORIZED,
    "PermissionDeniedError": status.HTTP_403_FORBIDDEN,
    "RateLimitError": status.HTTP_429_TOO_MANY_REQUESTS,
    "BadRequestError": status.HTTP_400_BAD_REQUEST,
    "UnprocessableEntityError": status.HTTP_400_BAD_REQUEST,
    # Fakes used in tests / potential wrappers.
    "FakeAuthenticationError": status.HTTP_401_UNAUTHORIZED,
    "FakeRateLimitError": status.HTTP_429_TOO_MANY_REQUESTS,
}


def is_openai_exception(exc: Exception) -> bool:
    mod = getattr(exc.__class__, "__module__", "")
    if mod.startswith("openai"):
        return True
    # Fallback: common exception class names when module info is obscured/mocked.
    return exc.__class__.__name__ in _STATUS_BY_ERROR_NAME


def openai_exception_payload(exc: Exception) -> OpenAIErrorPayload:
    name = exc.__class__.__name__
    http_status = _STATUS_BY_ERROR_NAME.get(name)

    # The OpenAI SDK exceptions often expose status_code; use it if sensible.
    status_code = getattr(exc, "status_code", None)
    if http_status is None and isinstance(status_code, int) and 400 <= status_code <= 599:
        http_status = status_code

    if http_status is None:
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE

    msg = str(exc) or name
    msg = msg.strip()
    if len(msg) > 500:
        msg = msg[:500] + "…"

    return OpenAIErrorPayload(http_status=http_status, code=name, message=msg)


def openai_exception_response(exc: Exception) -> Response:
    payload = openai_exception_payload(exc)
    return Response(
        {"error": {"type": "openai_error", "code": payload.code, "message": payload.message}},
        status=payload.http_status,
    )

