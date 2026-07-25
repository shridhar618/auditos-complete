"""
Thin wrapper around OpenAI's embeddings endpoint. Mirrors
`app/ai_agents/llm_client.py`'s degradation pattern: if no API key is
configured, `embed_text` returns None and callers must fall back to
keyword search - never fabricate a similarity score.
"""
from app.core.config import settings


def is_available() -> bool:
    return bool(settings.OPENAI_API_KEY)


def embed_text(text: str) -> list[float] | None:
    if not is_available():
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.embeddings.create(model=settings.EMBEDDING_MODEL, input=text[:8000])
        return response.data[0].embedding
    except Exception:
        return None
