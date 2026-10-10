import html as _html
from datetime import date, datetime, time, timedelta
from typing import Mapping, Sequence
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

from app.config import settings
from app.schemas.item import Digest, DigestSection, Item, Topic
from app.schemas.subscriber import SubscriberPreferences
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
    "security",
    "tooling",
]
_TOPIC_LABELS: dict[str, str] = {
    "labs": "AI Labs",
    "research": "Research",
    "startups": "Startups",
    "security": "Security",
    "tooling": "Tooling",
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


def filter_for_topics(
    digest: Digest,
    topics: Sequence[Topic],
    *,
    items_per_topic: int = 3,
) -> Digest:
    """Return the highest-ranked stories for a subscriber's selected topics."""
    selected = set(topics)
    sections_by_topic = {section.topic: section for section in digest.sections}
    sections = [
        DigestSection(
            topic=topic,
            items=sections_by_topic[topic].items[:items_per_topic],
        )
        for topic in _TOPIC_ORDER
        if topic in selected and topic in sections_by_topic
    ]
    return Digest(
        date=digest.date,
        total_indexed=sum(len(section.items) for section in sections),
        sections=sections,
    )


def filter_for_subscriber(
    digest: Digest,
    preferences: SubscriberPreferences,
    *,
    items_per_topic: int = 3,
) -> Digest | None:
    if not preferences.enabled:
        return None
    return filter_for_topics(
        digest,
        preferences.topics,
        items_per_topic=items_per_topic,
    )


def render_text(
    digest: Digest,
    *,
    app_url: str | None = None,
    topic_overviews: Mapping[Topic, str] | None = None,
) -> str:
    chat_url = _app_link("/chat", app_url)
    profile_url = _app_link("/profile", app_url)
    lines = [
        "DISPATCH: DAILY INGEST",
        _display_date(digest.date),
        f"{_story_count(digest.total_indexed)} selected for you",
        "",
    ]
    for section in digest.sections:
        label = _TOPIC_LABELS.get(section.topic, section.topic)
        lines.extend(
            [
                label.upper(),
                _topic_overview(section, topic_overviews),
                "",
            ]
        )
        for it in section.items:
            lines.append(f"- {it.title} ({it.source})")
            if it.summary:
                lines.append(f"  {it.summary}")
            lines.append(f"  {it.url}")
        lines.append("")
    if not digest.sections:
        lines.extend(["No matching stories today.", ""])
    lines.extend(
        [
            "Have questions? Come talk to Dispatch:",
            chat_url,
            "",
            f"Manage your digest preferences: {profile_url}",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_html(
    digest: Digest,
    *,
    app_url: str | None = None,
    topic_overviews: Mapping[Topic, str] | None = None,
) -> str:
    chat_url = _html.escape(_app_link("/chat", app_url), quote=True)
    profile_url = _html.escape(_app_link("/profile", app_url), quote=True)
    sections_html: list[str] = []
    for section in digest.sections:
        items_html: list[str] = []
        for it in section.items:
            summary = (
                '<p style="margin:6px 0 0;color:#5f5e5b;font-size:14px;line-height:1.55">'
                f"{_html.escape(it.summary)}</p>"
                if it.summary
                else ""
            )
            items_html.append(
                '<tr><td style="padding:18px 0;border-top:1px solid #e8e6e1">'
                f'<a href="{_html.escape(_safe_url(it.url), quote=True)}" '
                'style="color:#171716;font-size:16px;font-weight:600;'
                'line-height:1.35;text-decoration:none">'
                f"{_html.escape(it.title)}</a>"
                f'<div style="margin-top:5px;color:#8a8883;font-size:12px">'
                f"{_html.escape(it.source)}</div>{summary}</td></tr>"
            )
        label = _html.escape(_TOPIC_LABELS.get(section.topic, section.topic))
        overview = _html.escape(_topic_overview(section, topic_overviews))
        sections_html.append(
            '<tr><td style="padding:34px 0 0">'
            '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" '
            'style="border-collapse:collapse">'
            '<tr><td>'
            f'<div style="color:#a66510;font-size:12px;font-weight:700;letter-spacing:.12em;'
            f'text-transform:uppercase">{label}</div>'
            f'<p style="margin:8px 0 16px;color:#5f5e5b;font-size:14px;line-height:1.55">'
            f"{overview}</p></td></tr>"
            f"{''.join(items_html)}</table></td></tr>"
        )

    body = "".join(sections_html)
    if not body:
        body = (
            '<tr><td style="padding:36px 0;color:#5f5e5b;font-size:15px">'
            "No matching stories today.</td></tr>"
        )

    preheader = f"{_story_count(digest.total_indexed)} selected for your daily digest."
    return (
        '<!doctype html><html><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1"></head>'
        '<body style="margin:0;padding:0;background:#f3f1ec;'
        'font-family:Arial,Helvetica,sans-serif;color:#171716">'
        f'<div style="display:none;max-height:0;overflow:hidden;opacity:0">{preheader}</div>'
        '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" '
        'style="background:#f3f1ec;border-collapse:collapse">'
        '<tr><td align="center" style="padding:32px 16px">'
        '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" '
        'style="max-width:620px;background:#fffdf9;border:1px solid #e2dfd8;'
        'border-collapse:separate">'
        '<tr><td style="padding:34px 36px">'
        '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" '
        'style="border-collapse:collapse">'
        '<tr><td><span style="display:inline-block;padding:6px 8px;background:#171716;'
        'color:#fffdf9;font-size:12px;font-weight:700;letter-spacing:.08em">D</span>'
        '<span style="margin-left:10px;font-size:17px;font-weight:700">Dispatch</span></td></tr>'
        '<tr><td style="padding-top:30px">'
        '<div style="font-size:28px;font-weight:700;letter-spacing:-.03em;line-height:1.15">'
        'Daily Ingest</div>'
        f'<div style="margin-top:8px;color:#8a8883;font-size:13px">'
        f"{_html.escape(_display_date(digest.date))} &middot; "
        f"{_story_count(digest.total_indexed)} selected for you</div></td></tr>"
        f"{body}"
        '<tr><td style="padding:38px 0 8px;text-align:center">'
        '<p style="margin:0 0 16px;color:#5f5e5b;font-size:15px">'
        "Have questions? Come talk to Dispatch!</p>"
        f'<a href="{chat_url}" style="display:inline-block;background:#171716;color:#fffdf9;'
        'padding:12px 20px;font-size:14px;font-weight:700;text-decoration:none">'
        "Open Dispatch chat</a></td></tr>"
        '<tr><td style="padding-top:30px;border-top:1px solid #e8e6e1;text-align:center;'
        'color:#8a8883;font-size:12px;line-height:1.5">'
        "You chose the topics in this digest. "
        f'<a href="{profile_url}" style="color:#5f5e5b">Manage preferences</a>.'
        "</td></tr></table></td></tr></table></td></tr></table></body></html>"
    )


def _topic_overview(
    section: DigestSection,
    overviews: Mapping[Topic, str] | None,
) -> str:
    if overviews and section.topic in overviews:
        return overviews[section.topic]
    return f"{_story_count(len(section.items))} from today's {_TOPIC_LABELS[section.topic]} coverage."


def _story_count(count: int) -> str:
    return f"{count} {'story' if count == 1 else 'stories'}"


def _display_date(value: str) -> str:
    parsed = date.fromisoformat(value)
    return f"{parsed.strftime('%A, %B')} {parsed.day}, {parsed.year}"


def _app_link(path: str, app_url: str | None) -> str:
    return f"{(app_url or settings.frontend_origin).rstrip('/')}{path}"


def _safe_url(value: str) -> str:
    return value if urlparse(value).scheme in {"http", "https"} else "#"