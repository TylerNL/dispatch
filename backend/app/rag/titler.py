import logging

from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)

_client = AsyncOpenAI(api_key=settings.openai_api_key)

_TITLE_PROMPT = (
    "Generate a short, specific title (3-5 words) for this conversation. "
    "Return only the title. No quotes, no trailing punctuation."
)


async def generate_title(question: str, answer: str) -> str:
    resp = await _client.chat.completions.create(
        model=settings.gen_model,
        max_tokens=16,
        messages=[
            {"role": "system", "content": _TITLE_PROMPT},
            {"role": "user", "content": f"User: {question}\n\nAssistant: {answer[:500]}"},
        ],
    )
    title = (resp.choices[0].message.content or "").strip().strip('"').strip()
    return title[:80]