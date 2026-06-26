#!/usr/bin/env python3
"""RSSからニュースを取得する（単体実行用）."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.config import NEWS_CACHE_PATH
from lib.fetch_news import fetch_news, save_news


def main() -> int:
    articles = fetch_news()
    save_news(articles, NEWS_CACHE_PATH)
    for article in articles:
        print(f"- [{article['source']}] {article['title']}")
    print(f"\n{len(articles)} 件を {NEWS_CACHE_PATH} に保存しました")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
