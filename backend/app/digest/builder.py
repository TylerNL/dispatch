from datetime import date

from app.schemas.item import Digest


async def build_for(day: date) -> Digest:
    raise NotImplementedError


def render_html(digest: Digest) -> str:
    raise NotImplementedError


def render_text(digest: Digest) -> str:
    raise NotImplementedError
