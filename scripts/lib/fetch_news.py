"""RSSフィードからニュースを取得する."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Any

import feedparser

from .config import MAX_NEWS_ITEMS, RSS_SOURCES_PATH


def _strip_html(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r"<[^>]+>", "", text)
    return unescape(cleaned).strip()


def _load_sources() -> list[dict[str, str]]:
    with RSS_SOURCES_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    return data["sources"]


def fetch_news(max_items: int = MAX_NEWS_ITEMS) -> list[dict[str, Any]]:
    """複数RSSから最新記事を取得し、重複を除いて返す."""
    articles: list[dict[str, Any]] = []
    seen_links: set[str] = set()

    for source in _load_sources():
        feed = feedparser.parse(source["url"])
        for entry in feed.entries:
            link = getattr(entry, "link", "")
            if not link or link in seen_links:
                continue

            summary = _strip_html(
                getattr(entry, "summary", "") or getattr(entry, "description", "")
            )
            if len(summary) > 300:
                summary = summary[:300] + "…"

            published = getattr(entry, "published", "") or getattr(entry, "updated", "")

            articles.append(
                {
                    "title": getattr(entry, "title", "").strip(),
                    "summary": summary,
                    "url": link,
                    "source": source["name"],
                    "published": published,
                }
            )
            seen_links.add(link)

            if len(articles) >= max_items:
                return articles

    if not articles:
        raise RuntimeError("ニュース記事を取得できませんでした。RSSソースを確認してください。")

    return articles


def save_news(articles: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "articles": articles,
    }
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
