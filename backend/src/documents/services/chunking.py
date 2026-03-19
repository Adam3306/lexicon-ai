from __future__ import annotations

import re


def chunk_text(text: str, *, target_chars: int = 1200, overlap_chars: int = 150) -> list[str]:
    """
    MVP chunker:
    - split on paragraph boundaries
    - merge paragraphs into ~target_chars chunks
    - add small character overlap for retrieval continuity
    """

    cleaned = _normalize_whitespace(text)
    if not cleaned:
        return []

    paragraphs = [p.strip() for p in cleaned.split("\n\n") if p.strip()]
    chunks: list[str] = []
    buf: list[str] = []
    buf_len = 0

    def flush():
        nonlocal buf, buf_len
        if not buf:
            return
        chunk = "\n\n".join(buf).strip()
        if chunk:
            chunks.append(chunk)
        buf = []
        buf_len = 0

    for p in paragraphs:
        p_len = len(p)
        if buf_len and buf_len + 2 + p_len > target_chars:
            flush()
        buf.append(p)
        buf_len += (2 if buf_len else 0) + p_len

    flush()

    if overlap_chars <= 0 or len(chunks) <= 1:
        return chunks

    overlapped: list[str] = []
    for i, c in enumerate(chunks):
        if i == 0:
            overlapped.append(c)
            continue
        prev = overlapped[-1]
        prefix = prev[-overlap_chars:]
        overlapped.append((prefix + "\n\n" + c).strip())
    return overlapped


_ws_re = re.compile(r"[ \t]+")


def _normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [_ws_re.sub(" ", ln).rstrip() for ln in text.split("\n")]
    normalized = "\n".join(lines)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()

