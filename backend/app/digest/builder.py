import html as _html
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from app.schemas.item import Digest, DigestSection, Item, Topic
from app.storage.db import SessionLocal
from app.storage.vector import recent_items

# Time zone defaulted to PST
DIGEST_TZ = ZoneInfo("America/Los_Angeles")
def today() -> date:
    return datetime.now(DIGEST_TZ).date()


# Display order + labels for digest sections.
_TOPIC_ORDER: list[Topic] = [
    "labs",
    "research",
    "startups",
    "community",
    "security",
    "signal",
]
_TOPIC_LABELS: dict[str, str] = {
    "labs": "AI Labs",
    "research": "Research",
    "startups": "Startups",
    "community": "Community",
    "security": "Security",
    "signal": "Signal",
}


async def build_for(day: date) -> Digest:
    """Topic-grouped digest of everything ingested on `day` (Pacific time)."""
    # Pacific midnight to next Pacific midnight (per calendar day so DST-change
    # days stay correct). created_at is tz-aware, so this compares fine.
    start = datetime.combine(day, time.min, tzinfo=DIGEST_TZ)
    end = datetime.combine(day + timedelta(days=1), time.min, tzinfo=DIGEST_TZ)

    async with SessionLocal() as session:
        items = await recent_items(session, since=start, until=end)

    by_topic: dict[str, list[Item]] = {}
    for item in items:
        if item.topic:
            by_topic.setdefault(item.topic, []).append(item)

    sections = [
        DigestSection(topic=t, items=by_topic[t]) for t in _TOPIC_ORDER if by_topic.get(t)
    ]
    return Digest(date=day.isoformat(), total_indexed=len(items), sections=sections)


def render_text(digest: Digest) -> str:
    lines = [f"dispatch — {digest.date}", f"{digest.total_indexed} stories", ""]
    for section in digest.sections:
        lines.append(_TOPIC_LABELS.get(section.topic, section.topic).upper())
        for it in section.items:
            lines.append(f"- {it.title} ({it.source})")
            if it.summary:
                lines.append(f"  {it.summary}")
            lines.append(f"  {it.url}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_html(digest: Digest) -> str:
    blocks: list[str] = []
    for section in digest.sections:
        items_html = ""
        for it in section.items:
            summary = (
                f'<p style="margin:4px 0 0;color:#444;font-size:14px;line-height:1.5">'
                f"{_html.escape(it.summary)}</p>"
                if it.summary
                else ""
            )
            items_html += (
                '<div style="margin:0 0 16px">'
                f'<a href="{_html.escape(it.url)}" '
                'style="color:#111;font-size:16px;font-weight:600;text-decoration:none">'
                f"{_html.escape(it.title)}</a>"
                f'<span style="color:#888;font-size:13px"> — {_html.escape(it.source)}</span>'
                f"{summary}</div>"
            )
        label = _html.escape(_TOPIC_LABELS.get(section.topic, section.topic))
        blocks.append(
            '<h2 style="margin:28px 0 12px;font-size:13px;letter-spacing:0.08em;'
            f'text-transform:uppercase;color:#e8a33d">{label}</h2>{items_html}'
        )

    body = "".join(blocks) or '<p style="color:#888">No stories today.</p>'
    return (
        '<!doctype html><html><body style="margin:0;background:#f6f6f7;padding:24px;'
        'font-family:-apple-system,Segoe UI,Roboto,sans-serif">'
        '<div style="max-width:600px;margin:0 auto;background:#fff;border-radius:12px;padding:32px">'
        '<div style="font-size:18px;font-weight:600;color:#111">dispatch</div>'
        f'<div style="color:#888;font-size:13px;margin-top:2px">{digest.date} · '
        f"{digest.total_indexed} stories</div>{body}</div></body></html>"
    )