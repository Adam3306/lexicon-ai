from __future__ import annotations

import os
from dataclasses import dataclass

from openai import OpenAI


@dataclass(frozen=True)
class ChatConfig:
    model: str


def get_chat_config() -> ChatConfig:
    model = os.environ.get("OPENAI_CHAT_MODEL", "gpt-4o-mini")
    return ChatConfig(model=model)


def generate_grounded_answer(*, question: str, context_blocks: list[str], model: str) -> str:
    """
    Minimal, production-shaped generation:
    - system prompt defines grounding rules
    - context is passed verbatim
    """
    client = OpenAI()
    context = "\n\n---\n\n".join(context_blocks)
    messages = [
        {
            "role": "system",
            "content": (
                "You are a knowledge copilot. Answer the user using ONLY the provided context. "
                "If the context is insufficient, say you don't know and ask for the needed info. "
                "Be concise, factual, and do not invent details."
            ),
        },
        {"role": "user", "content": f"Question:\n{question}\n\nContext:\n{context}"},
    ]
    resp = client.chat.completions.create(model=model, messages=messages)
    return (resp.choices[0].message.content or "").strip()

