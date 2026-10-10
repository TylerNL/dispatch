from datetime import datetime, timezone

from app.digest.builder import (
    filter_for_subscriber,
    filter_for_topics,
    render_html,
    render_text,
)
from app.schemas.item import Digest, DigestSection, Item, Topic
from app.schemas.subscriber import SubscriberPreferences


def _item(
    item_id: str,
    topic: Topic,
    *,
    title: str | None = None,
    url: str | None = None,
    summary: str | None = None,
) -> Item:
    return Item(
        id=item_id,
        source="Example & Co.",
        url=url or f"https://example.com/{item_id}",
        title=title or f"Story {item_id}",
        published_at=datetime(2026, 10, 6, tzinfo=timezone.utc),
        summary=summary or f"Summary for {item_id}.",
        topic=topic,
    )


def _digest() -> Digest:
    return Digest(
        date="2026-10-06",
        total_indexed=8,
        sections=[
            DigestSection(
                topic="tooling",
                items=[_item(f"tool-{index}", "tooling") for index in range(4)],
            ),
            DigestSection(
                topic="labs",
                items=[_item("lab-1", "labs"), _item("lab-2", "labs")],
            ),
            DigestSection(
                topic="security",
                items=[_item("security-1", "security")],
            ),
        ],
    )


def test_filter_for_topics_uses_digest_order_and_caps_articles() -> None:
    filtered = filter_for_topics(
        _digest(),
        ["tooling", "labs"],
        items_per_topic=3,
    )

    assert [section.topic for section in filtered.sections] == ["labs", "tooling"]
    assert [len(section.items) for section in filtered.sections] == [2, 3]
    assert filtered.total_indexed == 5


def test_filter_for_subscriber_skips_disabled_digest() -> None:
    preferences = SubscriberPreferences(enabled=False, topics=["labs"])

    assert filter_for_subscriber(_digest(), preferences) is None


def test_render_text_includes_overview_articles_and_dispatch_links() -> None:
    digest = filter_for_topics(_digest(), ["labs"])

    text = render_text(
        digest,
        app_url="https://dispatch.example/",
        topic_overviews={"labs": "Two major model releases lead today's lab news."},
    )

    assert "DISPATCH: DAILY INGEST" in text
    assert "Tuesday, October 6, 2026" in text
    assert "Two major model releases lead today's lab news." in text
    assert "Story lab-1 (Example & Co.)" in text
    assert "https://dispatch.example/chat" in text
    assert "https://dispatch.example/profile" in text


def test_render_html_escapes_content_and_rejects_unsafe_links() -> None:
    digest = Digest(
        date="2026-10-06",
        total_indexed=2,
        sections=[
            DigestSection(
                topic="security",
                items=[
                    _item(
                        "safe",
                        "security",
                        title="<Critical> launch",
                        url="https://example.com/read?a=1&b=2",
                        summary="Research & response.",
                    ),
                    _item("unsafe", "security", url="javascript:alert(1)"),
                ],
            )
        ],
    )

    html = render_html(
        digest,
        app_url="https://dispatch.example",
        topic_overviews={"security": "Safety <and> security updates."},
    )

    assert "Dispatch" in html
    assert "Daily Ingest" in html
    assert "&lt;Critical&gt; launch" in html
    assert "Research &amp; response." in html
    assert "Safety &lt;and&gt; security updates." in html
    assert 'href="https://example.com/read?a=1&amp;b=2"' in html
    assert 'href="#"' in html
    assert 'href="https://dispatch.example/chat"' in html


def test_empty_digest_has_fallback_in_both_formats() -> None:
    digest = Digest(date="2026-10-06", total_indexed=0, sections=[])

    assert "No matching stories today." in render_text(digest)
    html = render_html(digest)
    assert "No matching stories today." in html
    assert "0 stories selected for your daily digest." in html
    assert "0 topics" not in html
