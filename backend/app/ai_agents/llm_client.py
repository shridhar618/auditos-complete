"""
Thin wrapper around the OpenAI client used only for generating
human-readable *explanations* of decisions the rule-based logic has
already made - never for the underlying risk scoring or policy
matching itself, which stay deterministic and auditable.

If no OPENAI_API_KEY is configured, `is_available()` returns False and
every agent node falls back to a templated explanation instead of
silently failing or fabricating a call.
"""
from app.core.config import settings


def is_available() -> bool:
    return bool(settings.OPENAI_API_KEY)


def generate_explanation(system_prompt: str, user_prompt: str, max_tokens: int = 300) -> str | None:
    """Returns None if the LLM is unavailable or the call fails - callers must have a fallback."""
    if not is_available():
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content
    except Exception:
        # Network issues, invalid key, rate limits, etc. - degrade gracefully,
        # never let an LLM outage break the (deterministic) audit pipeline.
        return None
